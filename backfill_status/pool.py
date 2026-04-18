from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from runtime.job_webapp.main import JOBS_CATALOG_PATH, JobAppStore

from .models import JobRecord


@dataclass(frozen=True)
class JobPoolSnapshot:
    jobs: list[JobRecord]
    total_jobs: int
    jobs_with_apply_url: int
    unique_hosts: int
    host_counts: dict[str, int]
    source_scope_counts: dict[str, int] = field(default_factory=dict)
    generated_at: str = ""
    canonical_source: str = "runtime.job_webapp.main.JobAppStore.build_jobs_payload"
    canonical_source_path: str = str(JOBS_CATALOG_PATH)


def load_full_job_pool() -> JobPoolSnapshot:
    store = JobAppStore()
    payload = store.build_jobs_payload()
    raw_jobs = payload.get("jobs", [])
    jobs: list[JobRecord] = []
    host_counts: Counter[str] = Counter()
    source_scope_counts: Counter[str] = Counter()

    for raw_job in raw_jobs:
        if not isinstance(raw_job, dict):
            continue
        apply_url = str(raw_job.get("apply_url", "") or "").strip()
        if not apply_url:
            continue
        job = JobRecord.from_payload(raw_job)
        if not job.job_id or not job.host:
            continue
        jobs.append(job)
        host_counts[job.host] += 1
        source_scope_counts[job.source_scope or "unspecified"] += 1

    jobs.sort(key=lambda item: (item.publish_at, item.discovered_at, item.job_id), reverse=True)
    return JobPoolSnapshot(
        jobs=jobs,
        total_jobs=len(raw_jobs),
        jobs_with_apply_url=len(jobs),
        unique_hosts=len(host_counts),
        host_counts=dict(host_counts.most_common()),
        source_scope_counts=dict(source_scope_counts.most_common()),
        generated_at=str(payload.get("generated_at", "") or "").strip(),
    )
