from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path
import re
from typing import Iterable

from .loader import document_from_row
from .matcher import MatchEngine, TEACHER_CONFIGS, _norm_title
from .models import JobDocument, StructuredJob
from .taxonomy import DEFAULT_TAXONOMY
from .units import build_structured_job


def _job_fingerprint(job: StructuredJob) -> str:
    payload = "|".join(
        [
            job.company_name.strip().lower(),
            _norm_title(job.title),
            job.pattern_signature,
            ",".join(sorted(job.canonical_elements)),
        ]
    )
    return hashlib.md5(payload.encode("utf-8")).hexdigest()


def _surface_token_candidates(text: str) -> list[str]:
    return sorted(
        {
            token
            for token in re.findall(r"[A-Za-z][A-Za-z0-9+#./-]{2,}", text)
            if token.lower() not in {"experience", "years", "team", "work", "using", "with", "build", "develop"}
        }
    )


@dataclass
class AliasCandidate:
    token: str
    source_job_id: str
    source_text: str
    suggested_content_type: str
    status: str = "pending"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class IngestResult:
    job_id: str
    action: str
    fingerprint: str
    duplicate_of: str = ""
    quarantine_reason: str = ""
    alias_candidates: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class IncrementalMatchStore:
    def __init__(
        self,
        jobs: Iterable[StructuredJob],
        *,
        snapshot_path: str | Path | None = None,
    ):
        self.engine = MatchEngine(jobs, taxonomy=DEFAULT_TAXONOMY, feature_config=TEACHER_CONFIGS["teacher_b_pure_semantic"])
        self.snapshot_path = Path(snapshot_path).expanduser().resolve() if snapshot_path else None
        self.fingerprint_to_job_id = {_job_fingerprint(job): job.job_id for job in self.engine.index.jobs}
        self.alias_candidates: list[AliasCandidate] = []
        self.quarantined_jobs: dict[str, str] = {}

    @classmethod
    def from_project_data(cls, *, snapshot_path: str | Path | None = None) -> "IncrementalMatchStore":
        engine = MatchEngine.from_project_data(
            include_scraped=True,
            include_portfolio=True,
            feature_config=TEACHER_CONFIGS["teacher_b_pure_semantic"],
        )
        return cls(engine.index.jobs, snapshot_path=snapshot_path)

    def ingest_row(self, row: dict, *, source_kind: str = "incremental_scraped") -> IngestResult:
        document = document_from_row(row, source_kind=source_kind)
        if document is None:
            return IngestResult(job_id="", action="skipped_invalid", fingerprint="")
        return self.ingest_document(document)

    def ingest_document(self, document: JobDocument) -> IngestResult:
        structured = build_structured_job(document, taxonomy=DEFAULT_TAXONOMY)
        return self.ingest_structured_job(structured)

    def ingest_structured_job(self, job: StructuredJob) -> IngestResult:
        fingerprint = _job_fingerprint(job)
        duplicate_of = self.fingerprint_to_job_id.get(fingerprint, "")
        if duplicate_of:
            return IngestResult(job_id=job.job_id, action="merged_duplicate", fingerprint=fingerprint, duplicate_of=duplicate_of)
        if len(job.canonical_elements) <= 1 and len(job.pending_surface_texts) >= 3:
            reason = "low_semantic_signal_high_pending_surface"
            self.quarantined_jobs[job.job_id] = reason
            return IngestResult(job_id=job.job_id, action="quarantined", fingerprint=fingerprint, quarantine_reason=reason)
        self.engine.add_structured_job(job)
        self.fingerprint_to_job_id[fingerprint] = job.job_id
        alias_candidates = self._discover_alias_candidates(job)
        if self.snapshot_path:
            self.save()
        return IngestResult(
            job_id=job.job_id,
            action="indexed",
            fingerprint=fingerprint,
            alias_candidates=[item.to_dict() for item in alias_candidates],
        )

    def _discover_alias_candidates(self, job: StructuredJob) -> list[AliasCandidate]:
        discovered: list[AliasCandidate] = []
        for unit in job.surface_elements:
            if unit.canonical_ids:
                continue
            for token in _surface_token_candidates(unit.text)[:4]:
                candidate = AliasCandidate(
                    token=token,
                    source_job_id=job.job_id,
                    source_text=unit.text,
                    suggested_content_type=unit.type_hint,
                )
                self.alias_candidates.append(candidate)
                discovered.append(candidate)
        return discovered

    def save(self) -> None:
        if self.snapshot_path is None:
            return
        self.snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "job_count": len(self.engine.index.jobs),
            "jobs": [job.to_dict() for job in self.engine.index.jobs],
            "alias_candidates": [item.to_dict() for item in self.alias_candidates],
            "quarantined_jobs": self.quarantined_jobs,
        }
        self.snapshot_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
