from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from html import unescape
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from runtime.job_webapp.main import (
    PORTFOLIO_INDEX_PATH,
    SCRAPED_JOBS_PATH,
    YOE_CACHE_PATH,
    _infer_yoe_value,
    _load_json,
    _normalize_yoe_value,
    _read_sheet_row,
    _write_json,
)


WORD_NUMBERS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

YEAR_PATTERNS = (
    re.compile(r"\b(\d{1,2})\s*(?:\+|plus)?\s*(?:years?|yrs?)\b", re.I),
    re.compile(r"\b(?:at\s+least|minimum\s+of|minimum|over)\s+(\d{1,2})\s+(?:years?|yrs?)\b", re.I),
    re.compile(r"\b(" + "|".join(WORD_NUMBERS) + r")\s*(?:\+|plus)?\s*(?:years?|yrs?)\b", re.I),
)


def _fetch_text(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
            )
        },
    )
    with urlopen(req, timeout=15) as response:
        raw = response.read().decode("utf-8", errors="ignore")
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", raw)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def _extract_year_candidates(text: str) -> list[int]:
    candidates: list[int] = []
    lowered = text.lower()
    for pattern in YEAR_PATTERNS:
        for match in pattern.findall(lowered):
            if isinstance(match, tuple):
                match = next((item for item in match if item), "")
            if not match:
                continue
            if match.isdigit():
                value = int(match)
            else:
                value = WORD_NUMBERS.get(match.lower(), 0)
            if 0 < value <= 20:
                candidates.append(value)
    return sorted(candidates)


def _estimate_from_seniority_and_title(title: str, seniority: str) -> tuple[int | None, str, float]:
    text = f"{title} {seniority}".lower()
    if any(marker in text for marker in ("intern",)):
        return None, "", 0.0
    if any(marker in text for marker in ("staff", "principal", "lead ", " lead", "architect", "manager", "director")):
        return 5, "title_seniority", 0.62
    if "senior associate" in text:
        return 3, "title_seniority", 0.7
    if re.search(r"\b(engineer|developer|scientist|analyst|sre|mle)\s+iii\b", text) or re.search(r"\biii\b", text):
        return 3, "title_seniority", 0.74
    if any(marker in text for marker in ("senior", "sr.", " sr ")):
        return 4, "title_seniority", 0.72
    if re.search(r"\b(engineer|developer|scientist|analyst|sre|mle)\s+ii\b", text) or re.search(r"\bii\b", text):
        return 2, "title_seniority", 0.78
    if re.search(r"\b(engineer|developer|scientist|analyst|sre|mle)\s+i\b", text) or re.search(r"\bi\b", text):
        return 1, "title_seniority", 0.75
    if "entry" in text or "junior" in text or "new grad" in text or "graduate" in text:
        return 0, "title_seniority", 0.85
    if "mid, senior" in text or "mid senior" in text:
        return 4, "title_seniority", 0.6
    if "senior level" in text:
        return 4, "title_seniority", 0.58
    if "mid level" in text:
        return 2, "title_seniority", 0.55
    return None, "", 0.0


def _estimate_yoe(job_id: str, title: str, row: dict[str, Any], fetch_html: bool) -> dict[str, Any] | None:
    raw_yoe = _infer_yoe_value(row)
    if raw_yoe is not None:
        return {
            "job_id": job_id,
            "yoe_value": raw_yoe,
            "source": "original",
            "confidence": 1.0,
            "signals": ["min_years_experience"],
        }

    text_fields = " ".join(
        str(row.get(key, "") or "")
        for key in ("must_have_quals", "preferred_quals", "job_summary", "core_responsibilities")
    )
    year_candidates = _extract_year_candidates(text_fields)
    if year_candidates:
        return {
            "job_id": job_id,
            "yoe_value": min(year_candidates),
            "source": "local_text",
            "confidence": 0.95,
            "signals": [f"years:{value}" for value in year_candidates[:5]],
        }

    estimated, source, confidence = _estimate_from_seniority_and_title(
        title,
        str(row.get("job_seniority", "") or ""),
    )
    signals = [str(row.get("job_seniority", "") or "").strip(), title]
    if estimated is not None:
        return {
            "job_id": job_id,
            "yoe_value": estimated,
            "source": source,
            "confidence": confidence,
            "signals": [signal for signal in signals if signal],
        }

    if fetch_html:
        url = str(row.get("apply_link", "") or row.get("original_url", "") or "").strip()
        if url:
            try:
                fetched_text = _fetch_text(url)
            except (HTTPError, URLError, TimeoutError, ValueError, OSError):
                fetched_text = ""
            if fetched_text:
                fetched_candidates = _extract_year_candidates(fetched_text)
                if fetched_candidates:
                    return {
                        "job_id": job_id,
                        "yoe_value": min(fetched_candidates),
                        "source": "fetched_html",
                        "confidence": 0.82,
                        "signals": [f"years:{value}" for value in fetched_candidates[:5]],
                    }
                estimated, source, confidence = _estimate_from_seniority_and_title(title, fetched_text[:600])
                if estimated is not None:
                    return {
                        "job_id": job_id,
                        "yoe_value": estimated,
                        "source": "fetched_html_keywords",
                        "confidence": min(confidence, 0.55),
                        "signals": [title, "html_keyword_match"],
                    }
    return None


def build_cache(fetch_html: bool, limit: int | None) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    scraped_rows = _load_json(SCRAPED_JOBS_PATH, [])
    portfolio_rows = _load_json(PORTFOLIO_INDEX_PATH, [])

    scraped_by_job_id = {
        str(row.get("job_id", "") or "").strip(): row
        for row in scraped_rows
        if isinstance(row, dict) and str(row.get("job_id", "") or "").strip()
    }

    cache: dict[str, dict[str, Any]] = {}
    stats = {"estimated": 0, "skipped_known": 0, "unresolved": 0}

    seen_job_ids: set[str] = set()

    for index, record in enumerate(portfolio_rows, start=1):
        if limit is not None and index > limit:
            break
        if not isinstance(record, dict):
            continue
        job_id = str(record.get("job_id", "") or "").strip()
        if not job_id:
            continue
        seen_job_ids.add(job_id)
        row = _read_sheet_row(record)
        row.update(scraped_by_job_id.get(job_id, {}))
        title = str(
            row.get("job_title")
            or row.get("job_nlp_title")
            or record.get("title")
            or ""
        ).strip()

        direct_yoe = _normalize_yoe_value(_infer_yoe_value(row))
        if direct_yoe is not None:
            stats["skipped_known"] += 1
            continue

        estimate = _estimate_yoe(job_id, title, row, fetch_html=fetch_html)
        if estimate is None:
            stats["unresolved"] += 1
            continue

        cache[job_id] = {
            "yoe_value": int(estimate["yoe_value"]),
            "source": str(estimate["source"]),
            "confidence": float(estimate["confidence"]),
            "signals": list(estimate.get("signals", [])),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
        stats["estimated"] += 1

    if limit is None:
        for job_id, row in scraped_by_job_id.items():
            if job_id in seen_job_ids:
                continue
            title = str(row.get("job_title") or row.get("job_nlp_title") or "").strip()
            direct_yoe = _normalize_yoe_value(_infer_yoe_value(row))
            if direct_yoe is not None:
                stats["skipped_known"] += 1
                continue
            estimate = _estimate_yoe(job_id, title, row, fetch_html=fetch_html)
            if estimate is None:
                stats["unresolved"] += 1
                continue
            cache[job_id] = {
                "yoe_value": int(estimate["yoe_value"]),
                "source": str(estimate["source"]),
                "confidence": float(estimate["confidence"]),
                "signals": list(estimate.get("signals", [])),
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            }
            stats["estimated"] += 1

    return cache, stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill estimated YOE values for the local job app.")
    parser.add_argument("--fetch-html", action="store_true", help="Try fetching job pages for unresolved jobs.")
    parser.add_argument("--limit", type=int, default=None, help="Only inspect the first N portfolio records.")
    args = parser.parse_args()

    existing_cache = _load_json(YOE_CACHE_PATH, {})
    if not isinstance(existing_cache, dict):
        existing_cache = {}

    generated_cache, stats = build_cache(fetch_html=args.fetch_html, limit=args.limit)
    merged_cache = dict(existing_cache)
    merged_cache.update(generated_cache)
    _write_json(YOE_CACHE_PATH, merged_cache)

    print(
        json.dumps(
            {
                "cache_path": str(YOE_CACHE_PATH),
                "new_estimates": stats["estimated"],
                "skipped_known": stats["skipped_known"],
                "unresolved": stats["unresolved"],
                "cache_size": len(merged_cache),
                "fetch_html": args.fetch_html,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
