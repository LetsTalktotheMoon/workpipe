#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
RUNTIME_ROOT = ROOT / "runtime"
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

from automation.portfolio import rebuild_portfolio_indexes
from automation.resume_repair import audit_resume_markdown, normalize_resume_markdown
from automation.seed_registry import load_seed_registry
from core.anthropic_client import LLMUnavailableError, configure_llm_client
from core.provider_settings import PROVIDER_CHOICES, resolve_provider_settings
from core.prompt_builder import build_upgrade_revision_prompt
from models.jd import JDProfile
from pipeline.revision_acceptance import should_adopt_revision
from reviewers.unified_reviewer import ReviewSummary, UnifiedReviewer
from writers.master_writer import MasterWriter


DEFAULT_PORTFOLIO_ROOT = ROOT / "data" / "deliverables" / "resume_portfolio"
PASS_THRESHOLD = 93.0
MAX_REVISIONS = 2
REREVIEW_VERSION = "historical_rereview_v1"
UNIFIED_REWRITE_VERSION = "unified_followup_v1"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def verdict_for_review(review: ReviewSummary) -> str:
    if review.passed:
        return "pass"
    return "pending"


def _normalized_review_state(raw_status: str) -> str:
    status = str(raw_status or "").strip().lower()
    if status == "pass":
        return "pass"
    if status == "reject":
        return "reject"
    if status in {"pending", "conditional_pass", "fail"}:
        return "pending"
    return status


def _manifest_source_kind(manifest: dict[str, Any]) -> str:
    return str(manifest.get("source_kind", "") or "").strip()


def _manifest_review_status(manifest: dict[str, Any]) -> str:
    review_payload = manifest.get("review", {}) if isinstance(manifest.get("review"), dict) else {}
    review_verdict = str(manifest.get("review_verdict", "") or "").strip()
    if review_verdict:
        return review_verdict
    nested_verdict = str(review_payload.get("verdict", "") or review_payload.get("overall_verdict", "") or "").strip()
    if nested_verdict:
        return nested_verdict
    return ""


def _matches_source_scope(manifest: dict[str, Any], source_scope: str) -> bool:
    source_kind = _manifest_source_kind(manifest)
    if source_scope == "legacy_only":
        return source_kind != "local_unified_pipeline"
    if source_scope == "unified_only":
        return source_kind == "local_unified_pipeline"
    return True


def _matches_status_scope(manifest: dict[str, Any], status_scope: str) -> bool:
    status = _normalized_review_state(_manifest_review_status(manifest))
    if status_scope == "non_pass_only":
        return status == "pending"
    if status_scope == "pass_only":
        return status == "pass"
    return True


def _matches_route_mode(manifest: dict[str, Any], route_mode: str) -> bool:
    if route_mode == "all":
        return True
    return str(manifest.get("route_mode", "") or "").strip() == route_mode


def _review_score(review: dict[str, Any]) -> float:
    try:
        return float(review.get("final_score", review.get("weighted_score", 0.0)) or 0.0)
    except Exception:
        return 0.0


def _review_state(review: dict[str, Any]) -> str:
    verdict = str(review.get("verdict", "") or review.get("overall_verdict", "") or "").strip().lower()
    if verdict == "pass":
        return "pass"
    return "pending"


def _has_review_signal(review: dict[str, Any]) -> bool:
    if not isinstance(review, dict):
        return False
    for key in ("final_score", "weighted_score", "verdict", "overall_verdict", "passed"):
        value = review.get(key)
        if value not in (None, "", []):
            return True
    return False


def _normalize_seed_label(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").strip().lower()).strip()


def _seed_id_aliases(seed_id: str) -> list[str]:
    normalized = str(seed_id or "").strip()
    aliases = [normalized] if normalized else []
    if normalized.startswith("candidate_"):
        aliases.append("seed_" + normalized[len("candidate_") :])
    return aliases


def _index_portfolio_records(
    records: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    by_job_id: dict[str, dict[str, Any]] = {}
    by_seed_id: dict[str, list[dict[str, Any]]] = {}
    by_seed_label: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        job_id = str(record.get("job_id", "") or "").strip()
        if job_id:
            by_job_id[job_id] = record
        seed_id = str(record.get("parent_seed_id", "") or record.get("seed_id", "") or "").strip()
        if seed_id:
            by_seed_id.setdefault(seed_id, []).append(record)
        seed_label = _normalize_seed_label(str(record.get("seed_label", "") or ""))
        if seed_label:
            by_seed_label.setdefault(seed_label, []).append(record)
    for items in list(by_seed_id.values()) + list(by_seed_label.values()):
        items.sort(
            key=lambda item: (
                1 if _review_state(item.get("review", {}) if isinstance(item.get("review"), dict) else {}) == "pass" else 0,
                _review_score(item.get("review", {}) if isinstance(item.get("review"), dict) else {}),
                str(item.get("generated_at", "") or ""),
            ),
            reverse=True,
        )
    return by_job_id, by_seed_id, by_seed_label


def _resolve_existing_resume_path(raw_path: str) -> Path | None:
    path_text = str(raw_path or "").strip()
    if not path_text:
        return None
    path = Path(path_text).expanduser()
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    if not path.exists():
        return None
    return path


def _resolve_reuse_resume_path(
    manifest: dict[str, Any],
    *,
    seeds_by_id: dict[str, Any],
    portfolio_by_job_id: dict[str, dict[str, Any]],
    portfolio_by_seed_id: dict[str, list[dict[str, Any]]],
    portfolio_by_seed_label: dict[str, list[dict[str, Any]]],
) -> tuple[Path | None, dict[str, Any]]:
    seed_id = str(manifest.get("parent_seed_id", "") or manifest.get("seed_id", "") or "").strip()
    seed_label = _normalize_seed_label(str(manifest.get("seed_label", "") or ""))

    for candidate_seed_id in _seed_id_aliases(seed_id):
        seed = seeds_by_id.get(candidate_seed_id)
        source_job_id = str(getattr(seed, "source_job_id", "") or "").strip()
        if source_job_id:
            source_record = portfolio_by_job_id.get(source_job_id)
            if isinstance(source_record, dict):
                resolved = _resolve_existing_resume_path(str(source_record.get("resume_md", "") or ""))
                if resolved is not None:
                    review_payload = source_record.get("review", {}) if isinstance(source_record.get("review"), dict) else {}
                    return resolved, (review_payload if isinstance(review_payload, dict) else {})

        for record in portfolio_by_seed_id.get(candidate_seed_id, []):
            resolved = _resolve_existing_resume_path(str(record.get("resume_md", "") or ""))
            if resolved is not None:
                review_payload = record.get("review", {}) if isinstance(record.get("review"), dict) else {}
                return resolved, (review_payload if isinstance(review_payload, dict) else {})

        source_md = getattr(seed, "source_md", None)
        if source_md is not None:
            path = Path(str(source_md)).expanduser()
            if path.exists():
                validated_score = float(getattr(seed, "validated_score", 0.0) or 0.0)
                verdict = "pass" if validated_score >= PASS_THRESHOLD else "pending"
                return path, {
                    "final_score": round(validated_score, 1),
                    "weighted_score": round(validated_score, 1),
                    "verdict": verdict,
                    "passed": verdict == "pass",
                }

    if seed_label:
        for record in portfolio_by_seed_label.get(seed_label, []):
            resolved = _resolve_existing_resume_path(str(record.get("resume_md", "") or ""))
            if resolved is not None:
                review_payload = record.get("review", {}) if isinstance(record.get("review"), dict) else {}
                return resolved, (review_payload if isinstance(review_payload, dict) else {})
    return None, {}


def serialize_review(result: dict[str, Any], *, route_mode: str, seed_label: str) -> dict[str, Any]:
    review_obj = result.get("review")
    if review_obj is not None and hasattr(review_obj, "to_dict"):
        payload = review_obj.to_dict()
    else:
        payload = {}
    payload.update(
        {
            "final_score": round(float(result.get("final_score", 0.0) or 0.0), 1),
            "verdict": str(result.get("verdict", "") or ""),
            "seed_label": seed_label,
            "route_mode": route_mode,
            "revised": bool(result.get("revised", False)),
            "rewrite_adopted": bool(result.get("rewrite_adopted", result.get("revised", False))),
            "content_changed": bool(result.get("content_changed", False)),
        }
    )
    review_obj = result.get("review")
    if isinstance(review_obj, ReviewSummary):
        payload["revision_instructions"] = review_obj.revision_instructions
        payload["revision_priority"] = review_obj.revision_priority
    return payload


def review_once(
    *,
    reviewer: UnifiedReviewer,
    resume_md: str,
    jd: JDProfile,
    review_mode: str,
) -> ReviewSummary:
    return reviewer.review(resume_md, jd, mode=review_mode)


_COMPANY_SIZE_RANK: dict[str, int] = {
    "10001+ employees": 8,
    "5001-10000 employees": 7,
    "1001-5000 employees": 6,
    "501-1000 employees": 5,
    "201-500 employees": 4,
    "51-200 employees": 3,
    "11-50 employees": 2,
    "2-10 employees": 1,
}

_COMPANY_SIZE_TO_TIER: dict[str, str] = {
    "10001+ employees": "large",
    "5001-10000 employees": "large",
    "1001-5000 employees": "mid_large",
    "501-1000 employees": "mid_small",
    "201-500 employees": "small",
    "51-200 employees": "small",
    "11-50 employees": "small",
    "2-10 employees": "small",
}

_COMPANY_TIER_ALIASES: dict[str, tuple[str, ...]] = {
    "large": ("large",),
    "big": ("large",),
    "major": ("large",),
    "大厂": ("large",),
    "10000+": ("large",),
    "10001+": ("large",),
    "5001-10000": ("large",),
    "5001-10000 employees": ("large",),
    "10001+ employees": ("large",),
    "mid": ("mid_large", "mid_small"),
    "medium": ("mid_large", "mid_small"),
    "中厂": ("mid_large", "mid_small"),
    "mid_large": ("mid_large",),
    "mid-1001-5000": ("mid_large",),
    "1001-5000": ("mid_large",),
    "1001-5000 employees": ("mid_large",),
    "mid_small": ("mid_small",),
    "mid-501-1000": ("mid_small",),
    "501-1000": ("mid_small",),
    "501-1000 employees": ("mid_small",),
    "small": ("small",),
    "小厂": ("small",),
    "<=500": ("small",),
    "201-500": ("small",),
    "201-500 employees": ("small",),
    "51-200": ("small",),
    "51-200 employees": ("small",),
    "11-50": ("small",),
    "11-50 employees": ("small",),
    "2-10": ("small",),
    "2-10 employees": ("small",),
    "all": (),
    "*": (),
}


def _parse_cli_date(value: str | None) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    return datetime.strptime(text, "%Y-%m-%d").date()


def _normalize_company_tiers(raw_values: list[str] | None) -> set[str] | None:
    if not raw_values:
        return {"large"}

    normalized: set[str] = set()
    for raw_value in raw_values:
        for part in str(raw_value or "").split(","):
            token = part.strip().lower()
            if not token:
                continue
            mapped = _COMPANY_TIER_ALIASES.get(token)
            if mapped == ():
                return None
            if mapped is not None:
                normalized.update(mapped)
                continue
            raise ValueError(f"Unsupported company tier: {part.strip()}")
    return normalized or {"large"}


def _resolve_publish_date_filters(args: argparse.Namespace) -> tuple[date | None, date | None, date | None]:
    publish_date = _parse_cli_date(args.publish_date)
    publish_date_from = _parse_cli_date(args.publish_date_from)
    publish_date_to = _parse_cli_date(args.publish_date_to)
    if publish_date is not None and (publish_date_from is not None or publish_date_to is not None):
        raise ValueError("--publish-date cannot be combined with --publish-date-from/--publish-date-to")
    if publish_date_from is not None and publish_date_to is not None and publish_date_from > publish_date_to:
        raise ValueError("--publish-date-from cannot be later than --publish-date-to")
    return publish_date, publish_date_from, publish_date_to


def _manifest_publish_date(manifest: dict[str, Any]) -> date | None:
    for key in ("publish_time", "publish_date", "rereviewed_at"):
        raw = str(manifest.get(key, "") or "").strip()
        if not raw:
            continue
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
    return None


def _manifest_matches_filters(
    manifest_path: Path,
    *,
    allowed_company_tiers: set[str] | None,
    publish_date: date | None,
    publish_date_from: date | None,
    publish_date_to: date | None,
) -> bool:
    try:
        manifest = load_json(manifest_path)
    except Exception:
        return False

    if allowed_company_tiers is not None:
        sheet_row_path = manifest_path.parent / "sheet_row.json"
        company_size = ""
        if sheet_row_path.exists():
            try:
                sheet_row = load_json(sheet_row_path)
                company_size = str(sheet_row.get("company_size", "") or "").strip()
            except Exception:
                company_size = ""
        company_tier = _COMPANY_SIZE_TO_TIER.get(company_size)
        if company_tier not in allowed_company_tiers:
            return False

    manifest_publish_date = _manifest_publish_date(manifest)
    if publish_date is not None and manifest_publish_date != publish_date:
        return False
    if publish_date_from is not None and (manifest_publish_date is None or manifest_publish_date < publish_date_from):
        return False
    if publish_date_to is not None and (manifest_publish_date is None or manifest_publish_date > publish_date_to):
        return False
    return True


def _manifest_sort_key(manifest_path: Path) -> tuple[int, float, str, str, str]:
    try:
        manifest = load_json(manifest_path)
    except Exception:
        return (0, 0.0, "", "", str(manifest_path))

    # 从 sheet_row.json 读取薪资和公司规模
    sheet_row_path = manifest_path.parent / "sheet_row.json"
    min_salary = 0.0
    company_size_rank = 0
    try:
        sheet_row = load_json(sheet_row_path)
        min_salary = float(sheet_row.get("min_salary", 0) or 0)
        company_size_rank = _COMPANY_SIZE_RANK.get(
            str(sheet_row.get("company_size", "") or ""), 0
        )
    except Exception:
        pass

    publish_date = str(manifest.get("publish_date", "") or "")
    publish_time = str(manifest.get("publish_time", "") or "")
    job_id = str(manifest.get("job_id", "") or manifest_path.parent.name)
    return (company_size_rank, min_salary, publish_date, publish_time, job_id)


def process_manifest(
    manifest_path: Path,
    *,
    writer: MasterWriter,
    reviewer: UnifiedReviewer,
    write_changes: bool,
    review_mode: str,
    review_version: str,
    score_only: bool,
    seeds_by_id: dict[str, Any],
    portfolio_by_job_id: dict[str, dict[str, Any]],
    portfolio_by_seed_id: dict[str, list[dict[str, Any]]],
    portfolio_by_seed_label: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    resume_path = _resolve_existing_resume_path(str(manifest.get("resume_md", "") or ""))
    source_prior_review: dict[str, Any] = {}
    if resume_path is None and str(manifest.get("route_mode", "") or "").strip() == "reuse":
        resume_path, source_prior_review = _resolve_reuse_resume_path(
            manifest,
            seeds_by_id=seeds_by_id,
            portfolio_by_job_id=portfolio_by_job_id,
            portfolio_by_seed_id=portfolio_by_seed_id,
            portfolio_by_seed_label=portfolio_by_seed_label,
        )
    job_md_path = Path(str(manifest.get("job_md", "") or "")).expanduser()
    review_path = manifest_path.parent / "review.json"
    prior_review = load_json(review_path) if review_path.exists() else {}
    effective_prior_review = prior_review if _has_review_signal(prior_review) else source_prior_review
    previous_final_score = float(
        effective_prior_review.get("final_score", effective_prior_review.get("weighted_score", 0.0)) or 0.0
    )
    previous_verdict = str(effective_prior_review.get("verdict", effective_prior_review.get("overall_verdict", "")) or "")

    if not job_md_path.is_absolute():
        job_md_path = (ROOT / job_md_path).resolve()

    if resume_path is None or not job_md_path.exists():
        return {
            "artifact": str(manifest_path.parent),
            "status": "missing_input",
            "revised": False,
            "score_before": previous_final_score,
            "score_after": previous_final_score,
        }

    jd_text = job_md_path.read_text(encoding="utf-8")
    jd = JDProfile.from_text(
        jd_text,
        jd_id=str(manifest.get("job_id", "") or ""),
        company=str(manifest.get("company_name", "") or ""),
    )

    original_resume_md = resume_path.read_text(encoding="utf-8")
    normalized_resume_md, normalize_changes = normalize_resume_markdown(original_resume_md)
    current_resume_md = normalized_resume_md
    normalized_before_review = current_resume_md != original_resume_md

    review = review_once(reviewer=reviewer, resume_md=current_resume_md, jd=jd, review_mode=review_mode)
    review_rounds = 0
    revised = False

    while not score_only and not review.passed and review.needs_revision and review_rounds < MAX_REVISIONS:
        review_rounds += 1
        rewrite_review = review_once(reviewer=reviewer, resume_md=current_resume_md, jd=jd, review_mode="rewrite")
        prompt = build_upgrade_revision_prompt(
            current_resume_md,
            rewrite_review.__dict__ | {
                "scores": {
                    key: {
                        "score": dim.score,
                        "weight": dim.weight,
                        "verdict": dim.verdict,
                        "findings": dim.findings,
                    }
                    for key, dim in rewrite_review.dimensions.items()
                },
                "weighted_score": rewrite_review.weighted_score,
                "revision_instructions": rewrite_review.revision_instructions,
                "revision_priority": rewrite_review.revision_priority,
            },
            tech_required=jd.tech_required,
            jd_title=jd.title,
            route_mode=str(manifest.get("route_mode", "") or ""),
            seed_label=str(manifest.get("seed_label", "") or ""),
        )
        revised_md = writer.revise(
            current_resume_md,
            prompt,
            jd,
            rewrite_mode="upgrade",
        )
        revised_md, revision_normalize_changes = normalize_resume_markdown(revised_md)
        revised_review = review_once(reviewer=reviewer, resume_md=revised_md, jd=jd, review_mode=review_mode)
        adopted = should_adopt_revision(
            score_before=review.weighted_score,
            critical_before=review.critical_count,
            high_before=review.high_count,
            score_after=revised_review.weighted_score,
            critical_after=revised_review.critical_count,
            high_after=revised_review.high_count,
            passed_after=revised_review.passed,
        )
        if adopted:
            current_resume_md = revised_md
            review = revised_review
            revised = True
            normalize_changes = list(dict.fromkeys(normalize_changes + revision_normalize_changes))
            if review.passed:
                break
        else:
            break

    issues_after = audit_resume_markdown(current_resume_md)
    rereviewed_at = datetime.now().isoformat(timespec="seconds")
    content_changed = (current_resume_md != original_resume_md) if not score_only else False
    result = {
        "resume_markdown": current_resume_md,
        "review": review,
        "final_score": review.weighted_score,
        "verdict": verdict_for_review(review),
        "revised": revised,
        "rewrite_adopted": revised,
        "content_changed": content_changed,
    }
    review_payload = serialize_review(
        result,
        route_mode=str(manifest.get("route_mode", "") or ""),
        seed_label=str(manifest.get("seed_label", "") or ""),
    )
    review_payload.update(
        {
            "rereview_version": review_version,
            "rereviewed_at": rereviewed_at,
            "rereview_rounds": review_rounds,
            "rereview_revised": revised,
            "rewrite_adopted": revised,
            "content_changed": content_changed,
            "normalized_before_review": normalized_before_review,
            "normalize_changes": normalize_changes,
            "deterministic_issue_codes_after": [issue.code for issue in issues_after],
            "previous_final_score": previous_final_score,
            "previous_verdict": previous_verdict,
        }
    )

    manifest["review"] = review_payload
    manifest["rereview_version"] = review_version
    manifest["rereviewed_at"] = rereviewed_at
    manifest["rereview_rounds"] = review_rounds
    manifest["rereview_revised"] = revised
    manifest["rewrite_adopted"] = revised
    manifest["content_changed"] = content_changed
    manifest["review_final_score"] = round(float(review_payload.get("final_score", 0.0) or 0.0), 1)
    manifest["review_verdict"] = str(review_payload.get("verdict", "") or "")

    if write_changes:
        if not score_only and current_resume_md != original_resume_md:
            resume_path.write_text(current_resume_md, encoding="utf-8")
        write_json(review_path, review_payload)
        write_json(manifest_path, manifest)

    return {
        "artifact": str(manifest_path.parent),
        "status": "ok",
        "revised": revised,
        "rewrite_adopted": revised,
        "content_changed": content_changed,
        "normalized_before_review": normalized_before_review,
        "score_before": review_payload["previous_final_score"],
        "score_after": float(review_payload.get("final_score", 0.0) or 0.0),
        "verdict_after": str(review_payload.get("verdict", "") or ""),
        "passed_after": bool(review_payload.get("passed", False)),
    }


def main() -> None:
    if os.environ.get("MANAGED_RUN_ACTIVE", "").strip() != "1" and len(sys.argv) > 1:
        os.execv(
            sys.executable,
            [
                sys.executable,
                str(ROOT / "managed_run.py"),
                "--label",
                "rereview",
                "--display-name",
                "Rereview",
                "--cwd",
                str(ROOT),
                "--preset-id",
                "rereview",
                "--",
                sys.executable,
                str(ROOT / "rereview_resume_portfolio.py"),
                *sys.argv[1:],
            ],
        )
    parser = argparse.ArgumentParser(description="JD-aware historical re-review for the resume portfolio.")
    parser.add_argument("--portfolio-root", default=str(DEFAULT_PORTFOLIO_ROOT))
    parser.add_argument("--company", default="", help="Only process one company_slug.")
    parser.add_argument("--job-id", default="", help="Only process one job_id.")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--company-tier",
        dest="company_tiers",
        action="append",
        default=["large"],
        help="Filter by company tier. Default is large only. Repeatable or comma-separated.",
    )
    parser.add_argument("--publish-date", default="", help="Only process jobs published on YYYY-MM-DD.")
    parser.add_argument("--publish-date-from", default="", help="Only process jobs published on/after YYYY-MM-DD.")
    parser.add_argument("--publish-date-to", default="", help="Only process jobs published on/before YYYY-MM-DD.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-rebuild", action="store_true")
    parser.add_argument(
        "--rebuild-every",
        type=int,
        default=10,
        help="Rebuild portfolio indexes every N processed resumes during long runs (0 disables periodic rebuilds).",
    )
    parser.add_argument("--skip-rereviewed", action="store_true")
    parser.add_argument("--oldest-first", action="store_true")
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--provider", choices=PROVIDER_CHOICES, default="codex")
    parser.add_argument("--write-model", default=None)
    parser.add_argument("--review-model", default=None)
    parser.add_argument("--llm-transport", default=None)
    parser.add_argument("--review-mode", default="full", choices=["compact", "full"])
    parser.add_argument(
        "--route-mode",
        default="all",
        choices=["all", "reuse", "retarget", "new_seed"],
        help="Filter manifests by route_mode. Default is all.",
    )
    parser.add_argument(
        "--score-only",
        action="store_true",
        help="Only re-score resumes and write back review payloads; do not attempt rewrite or modify resume.md.",
    )
    parser.add_argument(
        "--source-scope",
        default="legacy_only",
        choices=["legacy_only", "unified_only", "all"],
        help="Which portfolio source pool to rereview. Default is legacy_only.",
    )
    parser.add_argument(
        "--status-scope",
        default="all",
        choices=["all", "non_pass_only", "pass_only"],
        help="Filter manifests by current review status before rereview. non_pass_only means rewriteable pending items only.",
    )
    parser.add_argument(
        "--review-version",
        default=REREVIEW_VERSION,
        help="Version tag written into rereview payloads.",
    )
    args = parser.parse_args()
    provider_settings = resolve_provider_settings(
        args.provider,
        args.write_model,
        args.review_model,
        args.llm_transport,
    )

    configure_llm_client(
        enabled=True,
        write_model=provider_settings["write_model"],
        review_model=provider_settings["review_model"],
        transport=provider_settings["llm_transport"],
    )

    portfolio_root = Path(args.portfolio_root).expanduser().resolve()
    portfolio_index_path = portfolio_root / "portfolio_index.json"
    portfolio_records = load_json(portfolio_index_path) if portfolio_index_path.exists() else []
    portfolio_by_job_id, portfolio_by_seed_id, portfolio_by_seed_label = _index_portfolio_records(
        portfolio_records if isinstance(portfolio_records, list) else []
    )
    seeds_by_id = {seed.seed_id: seed for seed in load_seed_registry(include_promoted=True)}
    company_tiers = _normalize_company_tiers(args.company_tiers)
    publish_date, publish_date_from, publish_date_to = _resolve_publish_date_filters(args)
    manifests = sorted(
        (portfolio_root / "by_company").glob("*/*/*/manifest.json"),
        key=_manifest_sort_key,
        reverse=not args.oldest_first,
    )
    manifests = [
        path
        for path in manifests
        if _manifest_matches_filters(
            path,
            allowed_company_tiers=company_tiers,
            publish_date=publish_date,
            publish_date_from=publish_date_from,
            publish_date_to=publish_date_to,
        )
    ]
    manifests = [
        path
        for path in manifests
        if (
            (
                lambda manifest: _matches_source_scope(manifest, args.source_scope)
                and _matches_status_scope(manifest, args.status_scope)
                and _matches_route_mode(manifest, args.route_mode)
            )(
                load_json(path)
            )
        )
    ]
    if args.company:
        manifests = [path for path in manifests if path.parts[-4] == args.company]
    if args.job_id:
        manifests = [path for path in manifests if path.parts[-2] == args.job_id]
    if args.skip_rereviewed:
        filtered = []
        for path in manifests:
            review_path = path.parent / "review.json"
            if review_path.exists():
                review_payload = load_json(review_path)
                if str(review_payload.get("rereview_version", "") or "") == str(args.review_version or ""):
                    continue
            filtered.append(path)
        manifests = filtered
    if args.limit > 0:
        manifests = manifests[: args.limit]
    if args.shard_count > 1:
        manifests = [
            path
            for index, path in enumerate(manifests)
            if index % args.shard_count == args.shard_index
        ]

    writer = MasterWriter()
    reviewer = UnifiedReviewer()
    summary = {
        "total": len(manifests),
        "processed": 0,
        "revised": 0,
        "normalized_before_review": 0,
        "passed_after": 0,
        "pending_after": 0,
        "failed_after": 0,
        "score_improved": 0,
    }
    portfolio_changed = False
    interrupted = False

    try:
        for index, manifest_path in enumerate(manifests, start=1):
            result = process_manifest(
                manifest_path,
                writer=writer,
                reviewer=reviewer,
                write_changes=not args.dry_run,
                review_mode=args.review_mode,
                review_version=str(args.review_version or REREVIEW_VERSION),
                score_only=bool(args.score_only),
                seeds_by_id=seeds_by_id,
                portfolio_by_job_id=portfolio_by_job_id,
                portfolio_by_seed_id=portfolio_by_seed_id,
                portfolio_by_seed_label=portfolio_by_seed_label,
            )
            summary["processed"] += 1
            summary["revised"] += int(bool(result.get("revised")))
            summary["normalized_before_review"] += int(bool(result.get("normalized_before_review")))
            summary["passed_after"] += int(bool(result.get("passed_after")))
            summary["pending_after"] += int(not bool(result.get("passed_after")))
            summary["failed_after"] = summary["pending_after"]
            summary["score_improved"] += int(
                float(result.get("score_after", 0.0) or 0.0) > float(result.get("score_before", 0.0) or 0.0)
            )
            portfolio_changed = portfolio_changed or (not args.dry_run and result.get("status") == "ok")
            if (
                portfolio_changed
                and not args.dry_run
                and not args.skip_rebuild
                and args.rebuild_every > 0
                and summary["processed"] % args.rebuild_every == 0
            ):
                rebuild_portfolio_indexes(portfolio_root)
            print(
                json.dumps(
                    {
                        "index": index,
                        "total": len(manifests),
                        "job_dir": result.get("artifact"),
                        "score_before": result.get("score_before"),
                        "score_after": result.get("score_after"),
                        "verdict_after": result.get("verdict_after"),
                        "revised": result.get("revised"),
                        "rewrite_adopted": result.get("rewrite_adopted"),
                        "content_changed": result.get("content_changed"),
                        "rescored_only": (
                            float(result.get("score_after", 0.0) or 0.0)
                            != float(result.get("score_before", 0.0) or 0.0)
                            and not bool(result.get("content_changed"))
                        ),
                    },
                    ensure_ascii=False,
                )
            )
    except KeyboardInterrupt:
        interrupted = True
    finally:
        if portfolio_changed and not args.dry_run and not args.skip_rebuild:
            rebuild_portfolio_indexes(portfolio_root)
        payload = {"summary": summary}
        if interrupted:
            payload["interrupted"] = True
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    if interrupted:
        raise SystemExit(130)


if __name__ == "__main__":
    try:
        main()
    except LLMUnavailableError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        raise SystemExit(2)
