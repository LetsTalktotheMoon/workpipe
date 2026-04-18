from __future__ import annotations

import html
import json
import re
import time
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlparse

import requests

from .models import DetectionResult, FetchedPage, JobAvailability, JobRecord
from .rules import GENERIC_CLOSED_MARKERS, GENERIC_OPEN_MARKERS, canonical_host, host_rule

requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]


DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

FALLBACK_HEADERS = {
    "User-Agent": DEFAULT_HEADERS["User-Agent"],
    "Accept": "*/*",
}

TITLE_RE = re.compile(r"(?is)<title[^>]*>(.*?)</title>")
SCRIPT_RE = re.compile(r"(?is)<script[^>]*>(.*?)</script>")
SCRIPT_TAG_RE = re.compile(r"(?is)<script(?P<attrs>[^>]*)>(?P<body>.*?)</script>")
STYLE_RE = re.compile(r"(?is)<style[^>]*>.*?</style>")
TAG_RE = re.compile(r"(?is)<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")
JSON_LD_TYPE_RE = re.compile(r"""type\s*=\s*['"]application/ld\+json['"]""", re.IGNORECASE)
META_RE = re.compile(
    r'(?is)<meta[^>]+(?:property|name)\s*=\s*["\']([^"\']+)["\'][^>]+content\s*=\s*["\']([^"\']+)["\']'
)
JOBPOSTING_RE = re.compile(r'"@type"\s*:\s*"JobPosting"', re.IGNORECASE)
LINKEDIN_JOB_ID_RE = re.compile(r"/jobs/view/(?:[^/?#]+-)?(\d+)")
LINKEDIN_CURRENT_JOB_ID_RE = re.compile(r"[?&]currentJobId=(\d+)")

STRUCTURED_SCRIPT_HINTS = (
    "jobposting",
    "job posting",
    "jobpostinginfo",
    "applicationformdefinition",
    "jobdescription",
    "qualifications",
    "responsibilities",
    "hiringorganization",
    "dateposted",
    "validthrough",
    "jobid",
    "requisition",
    "externalpath",
    "og:title",
    "og:description",
    "questions",
    "candidateexperience",
    "greenhouse",
    "ashby",
    "lever",
    "myworkdayjobs",
    "oraclecloud",
    "icims",
    "jobvite",
    "phenom",
)

STRUCTURED_OPEN_MARKERS = (
    '"@type":"jobposting"',
    '"@type": "jobposting"',
    '"hiringorganization"',
    '"jobpostinginfo"',
    '"applicationformdefinition"',
    '"jobdescription"',
    '"jobtitle"',
    '"jobid"',
    '"externalpath"',
    '"questions"',
    "og:title",
    "og:description",
)

STRUCTURED_CLOSED_MARKERS = (
    '"isacceptingapplications":false',
    '"isacceptingapplications": false',
    '"status":"closed"',
    '"status": "closed"',
    '"jobstatus":"closed"',
    '"jobstatus": "closed"',
    '"postingstatus":"closed"',
    '"postingstatus": "closed"',
    '"errorcode":"404"',
    '"errorcode": "404"',
    "the job listing no longer exists",
)

FINAL_URL_CLOSED_HINTS = (
    "job-not-found",
    "posting-closed",
    "position-closed",
    "no-longer-available",
    "not_found=true",
    "/error/404",
    "/errors/404",
    "/404",
)

DEEP_LINK_OPEN_HINTS = (
    "/candidateexperience/en/job/",
    "/hcmui/candidateexperience/en/job/",
    "/jobs/results/",
    "/jobs/view/",
    "/embed/job_app?token=",
    "/jobs/",
)

ANTI_BOT_TITLE_MARKERS = (
    "security check",
    "just a moment",
    "attention required",
    "verify that you're not a robot",
    "access denied",
)

ANTI_BOT_CHALLENGE_TEXT_MARKERS = (
    "verify that you're not a robot",
    "in order to continue, we need to verify that you're not a robot",
    "enable javascript and then reload the page",
    "javascript is disabled",
    "attention required! | cloudflare",
    "just a moment...",
    "security check - indeed.com",
    "cf-challenge",
    "cf-browser-verification",
    "checking your browser before accessing",
)

ANTI_BOT_WEAK_TEXT_MARKERS = (
    "captcha",
    "recaptcha",
    "hcaptcha",
    "cloudflare",
)

STOPWORDS = {
    "and",
    "for",
    "with",
    "the",
    "job",
    "role",
}


@dataclass(frozen=True)
class MatchSummary:
    markers: tuple[str, ...]
    score: int


@dataclass(frozen=True)
class AntiBotSummary:
    strong_hits: tuple[str, ...]
    weak_hits: tuple[str, ...]

    @property
    def hits(self) -> tuple[str, ...]:
        return self.strong_hits + tuple(hit for hit in self.weak_hits if hit not in self.strong_hits)

    @property
    def is_strong(self) -> bool:
        return bool(self.strong_hits)


def _extract_title(raw_html: str) -> str:
    match = TITLE_RE.search(raw_html)
    if not match:
        return ""
    return html.unescape(WHITESPACE_RE.sub(" ", match.group(1))).strip()


def _clean_script_blob(blob: str) -> str:
    cleaned = html.unescape(blob or "")
    cleaned = cleaned.replace("\\/", "/")
    cleaned = cleaned.replace("\\u002f", "/").replace("\\u002F", "/")
    cleaned = cleaned.replace("\\u003a", ":").replace("\\u003A", ":")
    cleaned = cleaned.replace("\\u003d", "=").replace("\\u003D", "=")
    cleaned = cleaned.replace("\\u0026", "&").replace("\\u002B", "+")
    cleaned = cleaned.replace('\\"', '"')
    return WHITESPACE_RE.sub(" ", cleaned).strip()


def _json_root_candidates(snippet: str) -> tuple[str, ...]:
    compact = snippet.strip().rstrip(";")
    candidates: list[str] = [compact]
    if "=" in compact[:200]:
        rhs = compact.split("=", 1)[1].strip().rstrip(";")
        candidates.append(rhs)
    for opener, closer in (("{", "}"), ("[", "]")):
        start = compact.find(opener)
        end = compact.rfind(closer)
        if start >= 0 and end > start:
            candidates.append(compact[start : end + 1])
    deduped: list[str] = []
    for item in candidates:
        if item and item not in deduped and item[:1] in {"{", "["}:
            deduped.append(item)
    return tuple(deduped)


def _flatten_json_strings(value: object, out: list[str], *, budget: int = 1400) -> None:
    if len(out) >= budget:
        return
    if isinstance(value, dict):
        for key, nested in value.items():
            if len(out) >= budget:
                return
            out.append(str(key))
            _flatten_json_strings(nested, out, budget=budget)
        return
    if isinstance(value, list):
        for nested in value:
            if len(out) >= budget:
                return
            _flatten_json_strings(nested, out, budget=budget)
        return
    if isinstance(value, str):
        text = value.strip()
        if text:
            out.append(text)
        return
    if isinstance(value, (int, float, bool)):
        out.append(str(value))


def _extract_meta_fragments(raw_html: str) -> list[str]:
    fragments: list[str] = []
    for key, value in META_RE.findall(raw_html):
        key_norm = str(key or "").strip().lower()
        val_norm = html.unescape(WHITESPACE_RE.sub(" ", str(value or "")).strip())
        if not val_norm:
            continue
        if key_norm in {"og:title", "og:description", "twitter:title", "twitter:description", "description"}:
            fragments.append(f"{key_norm}: {val_norm}")
    return fragments


def _extract_structured_fragments(raw_html: str) -> list[str]:
    fragments: list[str] = []
    for match in SCRIPT_TAG_RE.finditer(raw_html):
        attrs = str(match.group("attrs") or "")
        body = str(match.group("body") or "")
        body_lower = body.lower()
        is_json_ld = bool(JSON_LD_TYPE_RE.search(attrs))
        has_hint = any(token in body_lower for token in STRUCTURED_SCRIPT_HINTS)
        if not is_json_ld and not has_hint:
            continue
        cleaned = _clean_script_blob(body)
        if cleaned:
            fragments.append(cleaned[:12000])
        if is_json_ld or cleaned[:1] in {"{", "["}:
            for candidate in _json_root_candidates(cleaned):
                try:
                    parsed = json.loads(candidate)
                except Exception:
                    continue
                flattened: list[str] = []
                _flatten_json_strings(parsed, flattened)
                if flattened:
                    fragments.append(" ".join(flattened))
                    break
        if len(fragments) >= 24:
            break
    return fragments


def _extract_text(raw_html: str) -> str:
    without_style = STYLE_RE.sub(" ", raw_html)
    structured_scripts = _extract_structured_fragments(without_style)
    meta_fragments = _extract_meta_fragments(without_style)
    without_scripts = SCRIPT_RE.sub(" ", without_style)
    visible_text = TAG_RE.sub(" ", without_scripts)
    text = " ".join([visible_text, *meta_fragments, *structured_scripts])
    return html.unescape(WHITESPACE_RE.sub(" ", text)).strip()


def _build_fetched_page(url: str, response: requests.Response) -> FetchedPage:
    raw_html = response.text or ""
    return FetchedPage(
        requested_url=url,
        final_url=str(response.url or url),
        status_code=int(response.status_code or 0),
        title=_extract_title(raw_html),
        raw_html=raw_html,
        text=_extract_text(raw_html),
        content_type=str(response.headers.get("content-type", "") or ""),
    )


def _is_jometer(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return host.endswith("jometer.com") or ".jometer.com" in host


def _extract_linkedin_job_id(url: str) -> str:
    text = str(url or "")
    match = LINKEDIN_JOB_ID_RE.search(text)
    if match:
        return str(match.group(1))
    query_match = LINKEDIN_CURRENT_JOB_ID_RE.search(text)
    if query_match:
        return str(query_match.group(1))
    return ""


def fetch_linkedin_guest_page(job: JobRecord, session: requests.Session | None = None, timeout: int = 20) -> FetchedPage | None:
    job_id = _extract_linkedin_job_id(job.apply_url)
    if not job_id:
        return None
    client = session or requests.Session()
    guest_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
    last_page: FetchedPage | None = None
    for attempt in range(3):
        try:
            response = client.get(
                guest_url,
                headers={
                    **DEFAULT_HEADERS,
                    "Accept": "text/html,*/*",
                    "Referer": "https://www.linkedin.com/",
                },
                timeout=timeout,
                allow_redirects=True,
                verify=False,
            )
        except requests.RequestException:
            if attempt >= 2:
                return last_page
            time.sleep(0.8 * (attempt + 1))
            continue
        page = _build_fetched_page(job.apply_url, response)
        if response.status_code not in {429, 999, 500, 502, 503, 504}:
            return page
        last_page = page
        time.sleep(0.8 * (attempt + 1))
    return last_page


def fetch_page(url: str, session: requests.Session | None = None, timeout: int = 20) -> FetchedPage:
    client = session or requests.Session()
    last_page: FetchedPage | None = None
    for attempt in range(3):
        headers = DEFAULT_HEADERS
        if _is_jometer(url) and attempt >= 1:
            headers = FALLBACK_HEADERS
        response = client.get(
            url,
            headers=headers,
            timeout=timeout,
            allow_redirects=True,
            verify=False,
        )
        page = _build_fetched_page(url, response)
        busy_title = page.title.strip().lower() == "server busy"
        if response.status_code not in {406, 429, 500, 502, 503, 504, 999} and not busy_title:
            return page
        last_page = page
        time.sleep(1.2 * (attempt + 1))
    if last_page is not None:
        return last_page
    raise RuntimeError(f"failed to fetch page: {url}")


def _normalize_text(*parts: str) -> str:
    return WHITESPACE_RE.sub(" ", " ".join(part for part in parts if part)).strip().lower()


def _find_markers(text: str, markers: Iterable[str]) -> MatchSummary:
    matched = tuple(sorted(marker for marker in markers if marker and marker in text))
    return MatchSummary(markers=matched, score=len(matched))


def _title_tokens(title: str) -> tuple[str, ...]:
    tokens = []
    for token in re.findall(r"[a-z0-9]{3,}", title.lower()):
        if token in STOPWORDS:
            continue
        tokens.append(token)
    deduped: list[str] = []
    for token in tokens:
        if token not in deduped:
            deduped.append(token)
    return tuple(deduped[:6])


def _title_overlap(job: JobRecord, text: str, page_title: str) -> tuple[str, ...]:
    searchable = _normalize_text(text[:9000], page_title)
    matched = tuple(token for token in _title_tokens(job.title) if token in searchable)
    return matched


def _job_specific_path(url: str) -> bool:
    path = urlparse(str(url or "")).path.lower()
    return (
        any(token in path for token in ("/job/", "/jobs/", "/positions/", "/opportunitydetail"))
        or "am9icg9zd" in path
    )


def _dedupe_hits(*collections: Iterable[str]) -> tuple[str, ...]:
    deduped: list[str] = []
    for collection in collections:
        for item in collection:
            if item and item not in deduped:
                deduped.append(item)
    return tuple(deduped)


def _anti_bot_summary(page: FetchedPage, normalized: str) -> AntiBotSummary:
    title_lower = (page.title or "").strip().lower()
    final_url_lower = str(page.final_url or "").lower()
    strong_hits: list[str] = []
    weak_hits: list[str] = []
    for marker in ANTI_BOT_TITLE_MARKERS:
        if marker in title_lower:
            strong_hits.append(f"title:{marker}")
    for marker in ANTI_BOT_CHALLENGE_TEXT_MARKERS:
        if marker in normalized or marker in final_url_lower:
            strong_hits.append(marker)
    for marker in ANTI_BOT_WEAK_TEXT_MARKERS:
        if marker in normalized or marker in final_url_lower:
            weak_hits.append(marker)
    if page.status_code in {202, 403, 429, 999}:
        if "robot" in normalized or "challenge" in normalized or "captcha" in normalized:
            strong_hits.append(f"http:{page.status_code}:robot_challenge")
        elif page.status_code in {403, 429, 999} and (strong_hits or weak_hits):
            strong_hits.append(f"http:{page.status_code}:anti_bot_status")
    return AntiBotSummary(
        strong_hits=_dedupe_hits(strong_hits),
        weak_hits=_dedupe_hits(weak_hits),
    )


def _anti_bot_hits(page: FetchedPage, normalized: str) -> tuple[str, ...]:
    return _anti_bot_summary(page, normalized).hits


def _count_terms(text: str, terms: tuple[str, ...]) -> int:
    return sum(1 for term in terms if term in text)


def evaluate_fetched_page(job: JobRecord, page: FetchedPage) -> DetectionResult:
    canonical = canonical_host(job.host)
    normalized = _normalize_text(page.raw_html[:70000], page.text[:70000], page.title)
    page_host = urlparse(page.final_url).netloc.lower()
    page_canonical = canonical_host(page_host or job.host)
    effective_host = page_host or job.host
    effective_canonical = page_canonical if host_rule(effective_host) else canonical
    rule = host_rule(effective_host if effective_canonical == page_canonical else job.host)
    overlap = _title_overlap(job, page.text, page.title)
    normalized_job_title = WHITESPACE_RE.sub(" ", job.title).strip().lower()
    normalized_page_title = WHITESPACE_RE.sub(" ", page.title).strip().lower()
    final_url_lower = str(page.final_url or "").lower()

    if page.status_code in {404, 410}:
        return DetectionResult(
            job_id=job.job_id,
            status=JobAvailability.CLOSED,
            detector="http_status",
            confidence=0.99,
            reason=f"HTTP {page.status_code}",
            requested_url=job.apply_url,
            final_url=page.final_url,
            host=job.host,
            http_status=page.status_code,
            title=page.title,
            signals={"title_overlap": list(overlap)},
        )

    if any(hint in final_url_lower for hint in FINAL_URL_CLOSED_HINTS):
        return DetectionResult(
            job_id=job.job_id,
            status=JobAvailability.CLOSED,
            detector=f"{effective_canonical}:final_url",
            confidence=0.95,
            reason="Final URL indicates missing or closed posting",
            requested_url=job.apply_url,
            final_url=page.final_url,
            host=job.host,
            http_status=page.status_code,
            title=page.title,
            signals={"title_overlap": list(overlap), "page_host": page_host},
        )

    anti_bot = _anti_bot_summary(page, normalized)
    generic_closed = _find_markers(normalized, GENERIC_CLOSED_MARKERS)
    generic_open = _find_markers(normalized, GENERIC_OPEN_MARKERS)
    structured_closed = _find_markers(normalized, STRUCTURED_CLOSED_MARKERS)
    structured_open = _find_markers(normalized, STRUCTURED_OPEN_MARKERS)
    rule_closed = _find_markers(normalized, rule.closed_markers if rule else ())
    rule_open = _find_markers(normalized, rule.open_markers if rule else ())
    strong_closed = _find_markers(normalized, rule.strong_closed_markers if rule else ())
    strong_open = _find_markers(normalized, rule.strong_open_markers if rule else ())

    if effective_canonical == "workday":
        posting_false_markers = (
            "postingavailable: false",
            '"postingavailable":false',
            '"postingavailable": false',
            "postingavailable false",
        )
        if any(marker in normalized for marker in posting_false_markers):
            return DetectionResult(
                job_id=job.job_id,
                status=JobAvailability.CLOSED,
                detector="workday:posting_unavailable",
                confidence=0.99,
                reason="Workday payload indicates postingAvailable=false.",
                requested_url=job.apply_url,
                final_url=page.final_url,
                host=job.host,
                http_status=page.status_code,
                title=page.title,
                matched_markers=posting_false_markers,
                signals={"title_overlap": list(overlap), "page_host": page_host},
            )

    ashby_null_markers = ('"organization":null', '"posting":null', '"jobboard":null')
    if effective_canonical == "ashby" and all(marker in normalized for marker in ashby_null_markers):
        if page.title.strip().lower() == "jobs" or "window.__appdata" in normalized:
            return DetectionResult(
                job_id=job.job_id,
                status=JobAvailability.CLOSED,
                detector="ashby:null_payload",
                confidence=0.99,
                reason="Ashby payload has null organization/posting/jobBoard.",
                requested_url=job.apply_url,
                final_url=page.final_url,
                host=job.host,
                http_status=page.status_code,
                title=page.title,
                matched_markers=ashby_null_markers,
                signals={"title_overlap": list(overlap), "page_host": page_host},
            )

    if anti_bot.is_strong:
        return DetectionResult(
            job_id=job.job_id,
            status=JobAvailability.UNKNOWN,
            detector=f"{effective_canonical}:anti_bot",
            confidence=0.0,
            reason="Anti-bot or browser challenge page.",
            requested_url=job.apply_url,
            final_url=page.final_url,
            host=job.host,
            http_status=page.status_code,
            title=page.title,
            matched_markers=anti_bot.hits,
            signals={
                "title_overlap": list(overlap),
                "page_host": page_host,
                "anti_bot_weak_hits": list(anti_bot.weak_hits),
            },
        )

    closed_score = strong_closed.score * 4 + structured_closed.score * 3 + rule_closed.score + generic_closed.score
    if (
        strong_closed.score
        or (structured_closed.score and strong_open.score == 0)
        or closed_score >= 3
        or (
            closed_score >= 1
            and strong_open.score == 0
            and structured_open.score == 0
            and rule_open.score == 0
            and generic_open.score == 0
        )
    ):
        matched = strong_closed.markers or structured_closed.markers or rule_closed.markers or generic_closed.markers
        return DetectionResult(
            job_id=job.job_id,
            status=JobAvailability.CLOSED,
            detector=f"{effective_canonical}:markers",
            confidence=0.98 if strong_closed.score else 0.94,
            reason="Closed markers found",
            requested_url=job.apply_url,
            final_url=page.final_url,
            host=job.host,
            http_status=page.status_code,
            title=page.title,
            matched_markers=matched,
            signals={"title_overlap": list(overlap), "page_host": page_host},
        )

    redirect_score = 0
    if page_canonical != canonical and page_host:
        redirect_score -= 1
    if page.status_code in {301, 302, 303, 307, 308}:
        redirect_score -= 1
    if page.final_url.rstrip("/") == f"https://{page_host}/".rstrip("/"):
        redirect_score -= 1

    open_score = 0
    open_markers: list[str] = []
    if strong_open.score:
        open_score += 3
        open_markers.extend(strong_open.markers)
    if structured_open.score:
        open_score += min(structured_open.score, 3)
        open_markers.extend(structured_open.markers[:3])
    if rule_open.score:
        open_score += min(rule_open.score, 3)
        open_markers.extend(rule_open.markers[:3])
    if generic_open.score:
        open_score += 1
        open_markers.extend(generic_open.markers[:2])
    if JOBPOSTING_RE.search(page.raw_html):
        open_score += 2
        open_markers.append("schema.org/jobposting")
    if any(hint in final_url_lower for hint in DEEP_LINK_OPEN_HINTS):
        open_score += 1
    if len(overlap) >= 2:
        open_score += 2
    elif len(overlap) == 1:
        open_score += 1
    open_score += redirect_score

    if generic_closed.score == 1:
        open_score -= 1
    if structured_closed.score:
        open_score -= 2
    if normalized_job_title and normalized_job_title in normalized_page_title:
        open_score += 2
    if effective_canonical == "workday" and "/job/" in final_url_lower:
        if "og:title:" in normalized or "og:description:" in normalized:
            open_score += 2
        if overlap or rule_open.score or structured_open.score:
            open_score += 1
    if effective_canonical == "linkedin" and page.status_code == 200 and "d_jobs_guest_details" in normalized:
        open_score += 2
        open_markers.append("d_jobs_guest_details")
    if "apply.workable.com" in effective_host:
        if "not_found=true" in final_url_lower:
            return DetectionResult(
                job_id=job.job_id,
                status=JobAvailability.CLOSED,
                detector="workable:not_found",
                confidence=0.98,
                reason="Workable returned not_found page",
                requested_url=job.apply_url,
                final_url=page.final_url,
                host=job.host,
                http_status=page.status_code,
                title=page.title,
                signals={"page_host": page_host},
            )
        if " - " in page.title and "current openings" not in normalized_page_title:
            open_score += 3
    if effective_host.endswith(".breezy.hr") and " at " in normalized_page_title:
        open_score += 3
    if page.status_code == 200 and page_canonical == canonical and canonical in {
        "greenhouse",
        "ashby",
        "lever",
        "amazon",
        "microsoft",
        "google",
        "workday",
        "oracle",
        "icims",
        "phenom",
    } and (rule_open.score >= 1 or structured_open.score >= 1):
        open_score += 1

    if effective_canonical == "linkedin" and page.status_code == 200 and closed_score == 0:
        linkedin_top_card = _count_terms(
            normalized,
            ("top-card-layout", "jobs-unified-top-card", "topcard", "jobs-search__job-details"),
        )
        linkedin_content = _count_terms(
            normalized,
            (
                "description__text",
                "show more",
                "about the job",
                "responsibilities",
                "qualifications",
                "apply",
                "company",
            ),
        )
        if linkedin_top_card >= 1 and (linkedin_content >= 2 or len(overlap) >= 1):
            return DetectionResult(
                job_id=job.job_id,
                status=JobAvailability.OPEN,
                detector="linkedin:guest_top_card",
                confidence=0.9,
                reason="LinkedIn guest top-card posting signals detected.",
                requested_url=job.apply_url,
                final_url=page.final_url,
                host=job.host,
                http_status=page.status_code,
                title=page.title,
                matched_markers=tuple(dict.fromkeys(rule_open.markers + generic_open.markers[:2])),
                signals={"title_overlap": list(overlap), "page_host": page_host},
            )

    if effective_canonical == "gem" and page.status_code == 200 and _job_specific_path(page.final_url or job.apply_url):
        org_only_terms = _count_terms(normalized, ("careers", "open positions", "we're hiring", "we are hiring"))
        if "og:url" in normalized and org_only_terms >= 1 and open_score <= 1 and closed_score == 0:
            return DetectionResult(
                job_id=job.job_id,
                status=JobAvailability.CLOSED,
                detector="gem:org_landing_for_job_path",
                confidence=0.9,
                reason="Gem job-specific path resolves to org-level careers metadata.",
                requested_url=job.apply_url,
                final_url=page.final_url,
                host=job.host,
                http_status=page.status_code,
                title=page.title,
                signals={"title_overlap": list(overlap), "page_host": page_host},
            )

    if effective_canonical == "ultipro" and page.status_code == 200 and "opportunitydetail" in final_url_lower and closed_score == 0:
        ultipro_content = _count_terms(
            normalized,
            ("qualifications", "description", "benefits", "responsibilities", "essential duties"),
        )
        if ultipro_content >= 2:
            return DetectionResult(
                job_id=job.job_id,
                status=JobAvailability.OPEN,
                detector="ultipro:opportunitydetail_content",
                confidence=0.86,
                reason="Ultipro OpportunityDetail page contains rich posting content.",
                requested_url=job.apply_url,
                final_url=page.final_url,
                host=job.host,
                http_status=page.status_code,
                title=page.title,
                matched_markers=tuple(dict.fromkeys(rule_open.markers + generic_open.markers[:2])),
                signals={"title_overlap": list(overlap), "page_host": page_host},
            )

    if open_score >= 4 and page.status_code < 400 and open_score >= closed_score + 1:
        return DetectionResult(
            job_id=job.job_id,
            status=JobAvailability.OPEN,
            detector=f"{effective_canonical}:markers",
            confidence=0.88 if strong_open.score else 0.8,
            reason="Open markers and structured/title evidence found",
            requested_url=job.apply_url,
            final_url=page.final_url,
            host=job.host,
            http_status=page.status_code,
            title=page.title,
            matched_markers=tuple(dict.fromkeys(open_markers)),
            signals={"title_overlap": list(overlap), "page_host": page_host, "open_score": open_score},
        )

    if page.status_code == 200 and len(overlap) >= 3 and len(page.text) > 600 and closed_score == 0:
        return DetectionResult(
            job_id=job.job_id,
            status=JobAvailability.OPEN,
            detector=f"{effective_canonical}:title_overlap",
            confidence=0.72,
            reason="Page contains strong title overlap",
            requested_url=job.apply_url,
            final_url=page.final_url,
            host=job.host,
            http_status=page.status_code,
            title=page.title,
            matched_markers=overlap,
            signals={"page_host": page_host},
        )

    return DetectionResult(
        job_id=job.job_id,
        status=JobAvailability.UNKNOWN,
        detector=f"{effective_canonical}:fallback",
        confidence=0.0,
        reason="Insufficient evidence",
        requested_url=job.apply_url,
        final_url=page.final_url,
        host=job.host,
        http_status=page.status_code,
        title=page.title,
        matched_markers=tuple(
            dict.fromkeys(
                strong_closed.markers
                + rule_closed.markers
                + generic_closed.markers
                + structured_closed.markers
                + rule_open.markers[:1]
            )
        ),
        signals={
            "title_overlap": list(overlap),
            "page_host": page_host,
            "closed_score": closed_score,
            "open_score": open_score,
        },
    )


def detect_job_status(job: JobRecord, session: requests.Session | None = None) -> DetectionResult:
    try:
        if canonical_host(job.host) == "linkedin":
            guest_page = fetch_linkedin_guest_page(job, session=session)
            if guest_page and guest_page.status_code < 400:
                guest_result = evaluate_fetched_page(job, guest_page)
                if guest_result.status != JobAvailability.UNKNOWN:
                    return guest_result
        page = fetch_page(job.apply_url, session=session)
        return evaluate_fetched_page(job, page)
    except requests.RequestException as exc:
        return DetectionResult(
            job_id=job.job_id,
            status=JobAvailability.UNKNOWN,
            detector="request_error",
            confidence=0.0,
            reason=str(exc),
            requested_url=job.apply_url,
            final_url=job.apply_url,
            host=job.host,
            signals={"error_type": type(exc).__name__},
        )
    except Exception as exc:  # pragma: no cover - defensive
        return DetectionResult(
            job_id=job.job_id,
            status=JobAvailability.UNKNOWN,
            detector="unexpected_error",
            confidence=0.0,
            reason=str(exc),
            requested_url=job.apply_url,
            final_url=job.apply_url,
            host=job.host,
            signals={"error_type": type(exc).__name__},
        )
