#!/usr/bin/env python3
"""
Phase 3 — Core Scraper
Paginates the Jobright recommend/list API, respects rate limits,
deduplicates by apply URL, and filters to recent-14-day postings.
"""

import json
import random
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

from config import (
    API_BASE,
    HEADERS,
    LOCAL_TZ,
    LOOKBACK_DAYS,
    PAGE_SIZE,
    SESSION_ID,
    SLEEP_MAX,
    SLEEP_MIN,
)

# Default lookback in hours (14 days = 336 hours)
DEFAULT_LOOKBACK_HOURS = LOOKBACK_DAYS * 24


class AuthError(Exception):
    """Raised on 401/403 — session expired or IP blocked."""


def _build_cookies(session_id: str) -> dict:
    """Build the minimal cookie jar needed for auth."""
    return {"SESSION_ID": session_id}


def _parse_publish_time(raw: str | None) -> datetime | None:
    """Parse the API's publishTime string into a timezone-aware datetime."""
    if not raw:
        return None
    try:
        # Format: "2026-04-02 22:53:22"
        return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return None


def _utc_to_local(raw: str) -> str:
    """Convert API’s UTC publishTime string to Chicago local time string."""
    if not raw:
        return ""
    dt = _parse_publish_time(raw)
    if not dt:
        return raw
    return dt.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")


def fetch_page(position: int, session_id: str) -> dict:
    """
    Fetch one page from the Jobright API.
    Raises AuthError on 401/403.
    Returns the parsed JSON body.
    """
    params = {
        "refresh": "false",  # only first page should be true
        "sortCondition": "0",
        "position": str(position),
        "count": str(PAGE_SIZE),
        "syncRerank": "false",
    }
    # First page uses refresh=true to get a fresh recommendation set
    if position == 0:
        params["refresh"] = "true"

    resp = requests.get(
        API_BASE,
        params=params,
        headers=HEADERS,
        cookies=_build_cookies(session_id),
        timeout=30,
    )

    if resp.status_code in (401, 403):
        raise AuthError(
            f"❌  HTTP {resp.status_code} — "
            f"{'Session expired. Re-export SESSION_ID from browser.' if resp.status_code == 401 else 'Forbidden. Possible IP/rate-limit block.'}"
        )
    resp.raise_for_status()
    return resp.json()


def flatten_job(raw_job: dict) -> dict:
    """
    Convert a raw API job object into a flat dict matching ALL_COLUMNS.
    Also returns the raw JSON for full-field preservation.
    """
    jr = raw_job.get("jobResult", {})
    cr = raw_job.get("companyResult", {})
    gr = cr.get("grating", {})

    # ── helper: safely join list-of-dicts by a key ──
    def join_skills(arr, key="skill", limit=5):
        if not arr:
            return ""
        return ", ".join(str(item.get(key, "")) for item in arr[:limit])

    def join_scores(arr, limit=5):
        if not arr:
            return ""
        return ", ".join(
            f"{item.get('displayName', '')}:{item.get('score', '')}"
            for item in arr[:limit]
        )

    def join_list(arr, limit=10):
        if not arr:
            return ""
        if isinstance(arr[0], str):
            return ", ".join(arr[:limit])
        return ", ".join(str(x) for x in arr[:limit])

    quals = jr.get("qualifications", {})

    return {
        # Tracking (defaults — will be overridden by Sheets logic)
        "application_status": "1_Discovered",
        "discovered_date": datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M"),
        # Job core
        "job_id": jr.get("jobId", ""),
        "job_title": jr.get("jobTitle", ""),
        "job_nlp_title": jr.get("jobNlpTitle", ""),
        "job_seniority": jr.get("jobSeniority", ""),
        "job_location": jr.get("jobLocation", ""),
        "is_remote": str(jr.get("isRemote", "")),
        "work_model": jr.get("workModel", ""),
        "employment_type": jr.get("employmentType", ""),
        # Compensation
        "salary_desc": jr.get("salaryDesc", ""),
        "min_salary": str(jr.get("minSalary", "")),
        "max_salary": str(jr.get("maxSalary", "")),
        # Dates — convert API’s UTC publishTime to Chicago local
        "publish_time": _utc_to_local(jr.get("publishTime", "")),
        # Links
        "apply_link": jr.get("applyLink", ""),
        "original_url": jr.get("originalUrl", ""),
        # Match scores
        "display_score": str(raw_job.get("displayScore", "")),
        "recommendation_tags": join_list(jr.get("recommendationTags", [])),
        "first_taxonomy": jr.get("firstTaxonomy", ""),
        "taxonomy_v3": join_list(jr.get("jobTaxonomyV3", [])),
        # Company
        "company_name": cr.get("companyName", ""),
        "company_size": cr.get("companySize", ""),
        "company_location": cr.get("companyLocation", ""),
        "glassdoor_rating": str(gr.get("rating", "")),
        "glassdoor_url": gr.get("url", ""),
        "company_url": cr.get("companyURL", ""),
        # Visa
        "is_h1b_sponsor": str(jr.get("isH1bSponsor", "")),
        "is_citizen_only": str(jr.get("isCitizenOnly", "")),
        "is_clearance_required": str(jr.get("isClearanceRequired", "")),
        "is_work_auth_required": str(jr.get("isWorkAuthRequired", "")),
        # Skills & qualifications
        "applicants_count": str(jr.get("applicantsCount", "")),
        "min_years_experience": str(jr.get("minYearsOfExperience", "")),
        "core_skills": join_skills(jr.get("jdCoreSkills", []), "skill", 5),
        "skill_match_scores": join_scores(jr.get("skillMatchingScores", []), 5),
        "must_have_quals": join_list(quals.get("mustHave", []), 10),
        "preferred_quals": join_list(quals.get("preferredHave", []), 10),
        "core_responsibilities": join_list(jr.get("coreResponsibilities", []), 10),
        "job_summary": (jr.get("jobSummary", "") or "")[:500],
        # Raw JSON blob
        "full_job_json": json.dumps(raw_job, ensure_ascii=False),
    }


def scrape_all(session_id: str, max_pages: int = 50, lookback_hours: int | None = None) -> list[dict]:
    """
    Paginate through the API, collecting all jobs published within
    the last `lookback_hours` hours. Deduplicates by apply_link (URL).

    Args:
        lookback_hours: How far back to look. Defaults to LOOKBACK_DAYS * 24.
                        Use 1 for a quick test, 336 for full 14-day backfill.
    Returns a list of flattened job dicts.
    """
    if not session_id:
        raise AuthError("❌  JOBRIGHT_SESSION_ID is not set. Export it first.")

    hours = lookback_hours if lookback_hours is not None else DEFAULT_LOOKBACK_HOURS
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    seen_urls: set[str] = set()
    all_jobs: list[dict] = []
    position = 0
    empty_pages = 0

    label = f"{hours}h" if hours < 48 else f"{hours // 24}d"
    now_local = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M")
    cutoff_local = cutoff.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M")
    print(f"🚀  Starting scrape — lookback {label} (cutoff: {cutoff_local} Chicago, now: {now_local})")

    for page_num in range(max_pages):
        print(f"\n📄  Page {page_num + 1} (position={position}) …", end=" ")
        try:
            body = fetch_page(position, session_id)
        except AuthError as e:
            print(f"\n{e}")
            print("🛑  Aborting scrape safely.")
            sys.exit(1)

        if not body.get("success"):
            print(f"⚠️  API returned success=false (errorCode={body.get('errorCode')}). Stopping.")
            break

        job_list = body.get("result", {}).get("jobList", [])
        if not job_list:
            empty_pages += 1
            print(f"(empty page — {empty_pages}/3 consecutive)")
            if empty_pages >= 3:
                print("🏁  3 consecutive empty pages. All jobs fetched.")
                break
            position += PAGE_SIZE
            time.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))
            continue

        empty_pages = 0
        page_new = 0
        page_old = 0
        page_dup = 0

        for raw_job in job_list:
            jr = raw_job.get("jobResult", {})
            apply_url = jr.get("applyLink", "")
            pub_time = _parse_publish_time(jr.get("publishTime"))

            # ── Date filter: skip jobs older than lookback ──
            if pub_time and pub_time < cutoff:
                page_old += 1
                continue

            # ── URL dedup ──
            if apply_url in seen_urls:
                page_dup += 1
                continue

            seen_urls.add(apply_url)
            flat = flatten_job(raw_job)
            all_jobs.append(flat)
            page_new += 1

        print(f"+{page_new} new, {page_dup} dup, {page_old} old")

        # If the entire page was old jobs, we've gone past the lookback window
        if page_old == len(job_list):
            print("🏁  Entire page is older than lookback window. Stopping.")
            break

        position += PAGE_SIZE
        sleep_sec = random.uniform(SLEEP_MIN, SLEEP_MAX)
        print(f"   💤 sleeping {sleep_sec:.1f}s …")
        time.sleep(sleep_sec)

    print(f"\n✅  Scrape complete: {len(all_jobs)} jobs collected.")
    return all_jobs


# ── CLI entry point (for local testing) ─────────────────────────────────
if __name__ == "__main__":
    import os
    import argparse as _ap
    from pathlib import Path

    p = _ap.ArgumentParser()
    p.add_argument("--lookback-hours", type=int, default=None,
                   help="Override lookback window in hours (default: 336 = 14 days)")
    p.add_argument("--max-pages", type=int, default=50)
    a = p.parse_args()

    sid = os.environ.get("JOBRIGHT_SESSION_ID", SESSION_ID)
    if not sid:
        print("❌  Set JOBRIGHT_SESSION_ID env var first.")
        sys.exit(1)

    jobs = scrape_all(sid, max_pages=a.max_pages, lookback_hours=a.lookback_hours)
    out = "scraped_jobs.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)
    print(f"💾  Saved {len(jobs)} jobs → {out}")

    runtime_root = Path(__file__).resolve().parents[1]
    if str(runtime_root) not in sys.path:
        sys.path.insert(0, str(runtime_root))
    from automation.jobs_catalog import merge_rows_into_catalog

    catalog_summary = merge_rows_into_catalog(jobs)
    print(
        f"🗂️  Catalog updated → {catalog_summary['catalog_path']} "
        f"({catalog_summary['catalog_count']} rows / {catalog_summary['unique_job_ids']} unique job_id)"
    )
