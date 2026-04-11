#!/usr/bin/env python3
"""
Notification module — sends scrape summaries via Telegram or ServerChan (WeChat).
Both are optional; configure whichever you prefer.
"""

import re
from collections import Counter
from datetime import datetime

import requests

from config import LOCAL_TZ, SERVERCHAN_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def _send_telegram(title: str, body: str) -> bool:
    """Send a message via Telegram Bot API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False

    text = f"*{title}*\n\n{body}"
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "Markdown",
            },
            timeout=10,
        )
        if resp.ok:
            print("📨  Telegram notification sent.")
            return True
        else:
            print(f"⚠️  Telegram error: {resp.status_code} {resp.text[:100]}")
            return False
    except Exception as e:
        print(f"⚠️  Telegram send failed: {e}")
        return False


def _send_serverchan(title: str, body: str) -> bool:
    """Send a message via ServerChan (pushes to WeChat)."""
    if not SERVERCHAN_KEY:
        return False

    try:
        resp = requests.post(
            f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send",
            data={"title": title, "desp": body},
            timeout=10,
        )
        if resp.ok:
            print("📨  ServerChan (WeChat) notification sent.")
            return True
        else:
            print(f"⚠️  ServerChan error: {resp.status_code} {resp.text[:100]}")
            return False
    except Exception as e:
        print(f"⚠️  ServerChan send failed: {e}")
        return False


def _classify_role(title: str) -> str:
    """Classify a job title into a broad category."""
    t = title.lower()
    if any(kw in t for kw in ("machine learning", " ml ", " ml,", "mle", "ai ", "deep learning", "nlp", "computer vision", "cv ")):
        return "MLE/AI"
    if any(kw in t for kw in ("data scien", "data analy", "business intel", "bi ", "analytics")):
        return "Data/Analytics"
    if any(kw in t for kw in ("data eng", "etl", "pipeline", "airflow", "spark")):
        return "Data Eng"
    if any(kw in t for kw in ("product manag", " pm", "program manag", "project manag", "tpm")):
        return "PM/TPM"
    if any(kw in t for kw in ("software", "swe", "backend", "frontend", "full stack", "fullstack", "developer", "engineer")):
        return "SWE"
    if any(kw in t for kw in ("devops", "sre", "infra", "platform", "cloud")):
        return "Infra/DevOps"
    return "Other"


def _classify_seniority(seniority: str) -> str:
    """Normalize seniority level."""
    s = seniority.lower().strip()
    if any(kw in s for kw in ("intern",)):
        return "Intern"
    if any(kw in s for kw in ("new grad", "entry", "junior", "associate")):
        return "NG/Entry"
    if any(kw in s for kw in ("mid", "ii", "2")):
        return "Mid"
    if any(kw in s for kw in ("senior", "sr", "iii", "3", "staff", "principal", "lead", "director")):
        return "Senior+"
    if s:
        return s.title()
    return "Unknown"


def _build_job_detail(jobs: list[dict]) -> str:
    """Build a markdown table + category summary for new jobs."""
    if not jobs:
        return ""

    role_counter = Counter()
    seniority_counter = Counter()
    lines = []

    # Table header
    lines.append("| # | Title | Company | Seniority | Salary |")
    lines.append("|---|-------|---------|-----------|--------|")

    for i, j in enumerate(jobs, 1):
        title = j.get("job_title", "?")
        company = j.get("company_name", "?")
        seniority = j.get("job_seniority", "")
        salary = j.get("salary_desc", "")

        role = _classify_role(title)
        sen = _classify_seniority(seniority)
        role_counter[role] += 1
        seniority_counter[sen] += 1

        # Truncate long titles
        title_short = title[:40] + "…" if len(title) > 40 else title
        company_short = company[:20] + "…" if len(company) > 20 else company
        lines.append(f"| {i} | {title_short} | {company_short} | {seniority} | {salary} |")

    # Aggregation summary
    lines.append("")
    lines.append("**Role Breakdown:**")
    for role, count in role_counter.most_common():
        lines.append(f"- {role}: {count}")

    lines.append("")
    lines.append("**Seniority Breakdown:**")
    for sen, count in seniority_counter.most_common():
        lines.append(f"- {sen}: {count}")

    return "\n".join(lines)


def notify_success(stats: dict, job_count: int, lookback_label: str,
                   new_jobs: list[dict] | None = None):
    """Send a success summary after scraping."""
    now = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M CST")
    new_count = stats.get("new", 0)
    title = f"✅ Job Tracker: +{new_count} new | {now}"

    parts = [
        f"**Scrape Summary ({now})**\n",
        f"- Lookback: {lookback_label}",
        f"- Jobs scraped: {job_count}",
        f"- New to Sheet: {new_count}",
        f"- Skipped (dup): {stats.get('skipped', 0)}",
        f"- Errors: {stats.get('errors', 0)}",
    ]

    if new_jobs:
        parts.append("")
        parts.append("---")
        parts.append("")
        parts.append(_build_job_detail(new_jobs))

    body = "\n".join(parts)
    _send_telegram(title, body) or _send_serverchan(title, body)


def notify_error(error_msg: str):
    """Send an error alert (e.g., session expired)."""
    now = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M CST")
    title = f"❌ Job Tracker Error | {now}"
    body = (
        f"**Error at {now}**\n\n"
        f"{error_msg}\n\n"
        f"Action required: check logs and update secrets if needed."
    )
    _send_telegram(title, body) or _send_serverchan(title, body)
