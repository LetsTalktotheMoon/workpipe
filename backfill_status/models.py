from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from urllib.parse import urlparse


class JobAvailability(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class JobRecord:
    job_id: str
    company_name: str
    title: str
    apply_url: str
    host: str
    source_scope: str = ""
    publish_at: str = ""
    discovered_at: str = ""
    resume_dir: str = ""
    has_generated_resume: bool = False

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "JobRecord":
        apply_url = str(payload.get("apply_url", "") or "").strip()
        host = urlparse(apply_url).netloc.lower()
        return cls(
            job_id=str(payload.get("job_id", "") or "").strip(),
            company_name=str(payload.get("company_name", "") or "").strip(),
            title=str(payload.get("title", "") or "").strip(),
            apply_url=apply_url,
            host=host,
            source_scope=str(payload.get("source_scope", "") or "").strip(),
            publish_at=str(payload.get("publish_at", "") or "").strip(),
            discovered_at=str(payload.get("discovered_at", "") or "").strip(),
            resume_dir=str(payload.get("resume_dir", "") or "").strip(),
            has_generated_resume=bool(payload.get("has_generated_resume", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FetchedPage:
    requested_url: str
    final_url: str
    status_code: int
    title: str
    raw_html: str
    text: str
    content_type: str = ""
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["raw_html"] = self.raw_html[:4000]
        payload["text"] = self.text[:4000]
        return payload


@dataclass(frozen=True)
class DetectionResult:
    job_id: str
    status: JobAvailability
    detector: str
    confidence: float
    reason: str
    requested_url: str
    final_url: str
    host: str
    http_status: int = 0
    title: str = ""
    matched_markers: tuple[str, ...] = ()
    checked_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    signals: dict[str, Any] = field(default_factory=dict)

    @property
    def is_terminal(self) -> bool:
        return self.status in {JobAvailability.OPEN, JobAvailability.CLOSED}

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["matched_markers"] = list(self.matched_markers)
        return payload
