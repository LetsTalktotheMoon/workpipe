# ── project config ───────────────────────────────────────────────────────
"""
Central configuration for the job-tracker project.
Sensitive values (SESSION_ID, Google credentials) are loaded from
environment variables so they work in both local dev and GitHub Actions.
"""
import os
from zoneinfo import ZoneInfo

# ── Timezone ─────────────────────────────────────────────────────────────
LOCAL_TZ = ZoneInfo("America/Chicago")

# ── Jobright API ─────────────────────────────────────────────────────────
API_BASE = "https://jobright.ai/swan/recommend/list/jobs"
PAGE_SIZE = 10                       # API max per request
SLEEP_MIN = 3                        # seconds between pages
SLEEP_MAX = 6
LOOKBACK_DAYS = 14                   # only keep jobs published within N days

# Cookie-based auth — the only credential the API needs
SESSION_ID = os.environ.get("JOBRIGHT_SESSION_ID", "")

# Static headers (non-sensitive)
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9",
    "referer": "https://jobright.ai/jobs/recommend",
    "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
    "x-client-type": "web",
}

# ── Google Sheets ────────────────────────────────────────────────────────
# The Sheet must be shared with the service-account email.
GOOGLE_SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "")

# Path to the service-account JSON key.
# In GitHub Actions this will be written from a secret to a temp file.
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON", "")

# Worksheet name inside the Google Sheet
WORKSHEET_NAME = "Jobs"

# ── Column layout (order matters — this defines the Sheet columns) ──────
# Tracking columns (user-managed)
TRACKING_COLUMNS = [
    "application_status",
    "discovered_date",
]

# Core job fields (auto-populated)
JOB_CORE_COLUMNS = [
    "job_id",
    "job_title",
    "job_nlp_title",
    "job_seniority",
    "job_location",
    "is_remote",
    "work_model",
    "employment_type",
]

COMPENSATION_COLUMNS = [
    "salary_desc",
    "min_salary",
    "max_salary",
]

DATE_COLUMNS = [
    "publish_time",
]

LINK_COLUMNS = [
    "apply_link",
    "original_url",
]

MATCH_COLUMNS = [
    "display_score",
    "recommendation_tags",
    "first_taxonomy",
    "taxonomy_v3",
]

COMPANY_COLUMNS = [
    "company_name",
    "company_size",
    "company_location",
    "glassdoor_rating",
    "glassdoor_url",
    "company_url",
]

VISA_COLUMNS = [
    "is_h1b_sponsor",
    "is_citizen_only",
    "is_clearance_required",
    "is_work_auth_required",
]

SKILLS_COLUMNS = [
    "applicants_count",
    "min_years_experience",
    "core_skills",          # top-5 jdCoreSkills, comma-joined
    "skill_match_scores",   # top-5 skill matching, comma-joined
    "must_have_quals",      # comma-joined
    "preferred_quals",      # comma-joined
    "core_responsibilities",
    "job_summary",
]

RAW_COLUMNS = [
    "full_job_json",
]

ALL_COLUMNS = (
    TRACKING_COLUMNS
    + JOB_CORE_COLUMNS
    + COMPENSATION_COLUMNS
    + DATE_COLUMNS
    + LINK_COLUMNS
    + MATCH_COLUMNS
    + COMPANY_COLUMNS
    + VISA_COLUMNS
    + SKILLS_COLUMNS
    + RAW_COLUMNS
)

# ── Notifications ────────────────────────────────────────────────────────
# Telegram Bot (recommended — easy setup)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Server酱 / ServerChan (pushes to WeChat)
# Get your SendKey at https://sct.ftqq.com/
SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY", "")
