"""
Google Sheets read/write helpers for the jobs tracker workbook.
"""
from __future__ import annotations

import csv
import io
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, Sequence
from urllib.request import urlopen


DEFAULT_SHEET_ID = "11A-MDEn96wrGAvfPzd5ZNwvvb_UvlcdeqcdSOSILBkw"
DEFAULT_WORKSHEET = "Jobs"

APPLICATION_STATUS_COLUMN = "application_status"
JOB_ID_COLUMN = "job_id"
DISCOVERED_STATUSES = ("1_Discovered", "已发现")
GENERATED_STATUS = "已生成简历"
PUBLISH_TIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
)

_STATUS_ALIASES = {
    "discovered": DISCOVERED_STATUSES,
    "generated": (GENERATED_STATUS,),
}


@dataclass
class SheetConfig:
    sheet_id: str = DEFAULT_SHEET_ID
    worksheet: str = DEFAULT_WORKSHEET
    credentials_file: Optional[str] = None


def canonicalize_status(status: str) -> str:
    raw = str(status or "").strip()
    compact = raw.casefold().replace("_", "").replace("-", "").replace(" ", "")
    if compact in {"1discovered", "discovered", "已发现"}:
        return "discovered"
    if compact in {"generated", "resumegenerated", "已生成简历"}:
        return "generated"
    return raw


def expand_status_filters(statuses: Sequence[str] | None) -> set[str]:
    expanded: set[str] = set()
    for status in statuses or ():
        for part in str(status or "").split(","):
            candidate = part.strip()
            if not candidate:
                continue
            if candidate.upper() == "ALL":
                return {"ALL"}
            canonical = canonicalize_status(candidate)
            expanded.add(candidate)
            if canonical in _STATUS_ALIASES:
                expanded.add(canonical)
                expanded.update(_STATUS_ALIASES[canonical])
    return expanded


def filter_rows_by_status(rows: Iterable[dict], statuses: Sequence[str] | None) -> list[dict]:
    expanded = expand_status_filters(statuses)
    if not expanded or "ALL" in expanded:
        return list(rows)

    filtered = []
    for row in rows:
        raw_status = str(row.get(APPLICATION_STATUS_COLUMN, "") or "").strip()
        if raw_status in expanded or canonicalize_status(raw_status) in expanded:
            filtered.append(row)
    return filtered


def parse_publish_time(value: object) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    for time_format in PUBLISH_TIME_FORMATS:
        try:
            return datetime.strptime(text, time_format)
        except ValueError:
            continue
    return None


def sort_sheet_rows_by_publish_time(rows: Iterable[dict]) -> list[dict]:
    # Python's sort is stable, so equal timestamps preserve their incoming order.
    return sorted(list(rows), key=lambda row: _publish_time_sort_key(row.get("publish_time", "")), reverse=True)


def _publish_time_sort_key(value: object) -> tuple[int, datetime, str]:
    raw = str(value or "").strip()
    parsed = parse_publish_time(raw)
    if parsed is not None:
        return (1, parsed, raw)
    return (0, datetime.min, raw)


class GoogleSheetJobStore:
    def __init__(self, config: SheetConfig):
        self.config = config
        self._client = None
        self._worksheet = None

    def fetch_jobs(
        self,
        *,
        statuses: Sequence[str] | None = None,
        sort_by_publish_time: bool = False,
    ) -> list[dict]:
        rows = self._fetch_rows()
        if statuses:
            rows = filter_rows_by_status(rows, statuses)
        if sort_by_publish_time:
            rows = sort_sheet_rows_by_publish_time(rows)
        return rows

    def update_job_status(self, job_id: str, status: str) -> int:
        applied = self.batch_update_job_statuses({job_id: status})
        return applied[str(job_id)]

    def batch_update_job_statuses(self, updates: dict[str, str]) -> dict[str, int]:
        if not updates:
            return {}

        worksheet = self._get_worksheet(require_credentials=True)
        headers = worksheet.row_values(1)
        row_index = self._build_row_index(worksheet, headers=headers)
        try:
            status_col_number = headers.index(APPLICATION_STATUS_COLUMN) + 1
        except ValueError as exc:
            raise RuntimeError(f"Missing column in sheet: {APPLICATION_STATUS_COLUMN}") from exc

        normalized_updates = {str(job_id): status for job_id, status in updates.items()}
        missing = [job_id for job_id in normalized_updates if job_id not in row_index]
        if missing:
            raise LookupError(f"job_id not found in sheet: {', '.join(missing[:5])}")

        from gspread.utils import rowcol_to_a1

        batch_payload = []
        for job_id, status in normalized_updates.items():
            row_number = row_index[job_id]
            batch_payload.append(
                {
                    "range": rowcol_to_a1(row_number, status_col_number),
                    "values": [[status]],
                }
            )

        worksheet.batch_update(batch_payload, value_input_option="USER_ENTERED")
        return {job_id: row_index[job_id] for job_id in normalized_updates}

    def _fetch_rows(self) -> list[dict]:
        if self.config.credentials_file:
            try:
                return self._fetch_with_gspread()
            except Exception:
                # Viewer/public CSV remains a viable fallback for read-only mode.
                pass
        return self._fetch_with_csv_export()

    def _fetch_with_gspread(self) -> list[dict]:
        worksheet = self._get_worksheet(require_credentials=True)
        return worksheet.get_all_records()

    def _fetch_with_csv_export(self) -> list[dict]:
        gid = self._worksheet_gid()
        url = (
            f"https://docs.google.com/spreadsheets/d/{self.config.sheet_id}/export"
            f"?format=csv&gid={gid}"
        )
        try:
            with urlopen(url) as response:
                payload = response.read().decode("utf-8")
        except Exception:
            completed = subprocess.run(
                ["curl", "-sS", "-L", url],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                raise
            payload = completed.stdout
        reader = csv.DictReader(io.StringIO(payload))
        return list(reader)

    def _get_worksheet(self, *, require_credentials: bool) -> object:
        if self._worksheet is not None:
            return self._worksheet

        client = self._get_client(require_credentials=require_credentials)
        self._worksheet = client.open_by_key(self.config.sheet_id).worksheet(self.config.worksheet)
        return self._worksheet

    def _get_client(self, *, require_credentials: bool) -> object:
        if self._client is not None:
            return self._client
        if not self.config.credentials_file:
            if require_credentials:
                raise RuntimeError("Google credentials are required for authenticated Sheet access.")
            raise RuntimeError("Google credentials are not configured.")

        import gspread
        from google.oauth2.service_account import Credentials

        creds = Credentials.from_service_account_file(
            self.config.credentials_file,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ],
        )
        self._client = gspread.authorize(creds)
        return self._client

    def _build_row_index(
        self,
        worksheet: object,
        *,
        headers: Sequence[str] | None = None,
    ) -> dict[str, int]:
        all_values = worksheet.get_all_values()
        if len(all_values) <= 1:
            return {}

        resolved_headers = list(headers or all_values[0])
        try:
            job_id_col = resolved_headers.index(JOB_ID_COLUMN)
        except ValueError as exc:
            raise RuntimeError(f"Missing column in sheet: {JOB_ID_COLUMN}") from exc

        row_index: dict[str, int] = {}
        for row_number, row in enumerate(all_values[1:], start=2):
            job_id = str(row[job_id_col]).strip() if job_id_col < len(row) else ""
            if job_id and job_id not in row_index:
                row_index[job_id] = row_number
        return row_index

    def _worksheet_gid(self) -> str:
        # Current sheet only needs Jobs; keep this explicit instead of adding sheet discovery.
        if self.config.worksheet == "Jobs":
            return "242092932"
        return os.environ.get("GOOGLE_WORKSHEET_GID", "0")


def default_sheet_config() -> SheetConfig:
    credentials = (
        os.environ.get("GOOGLE_CREDENTIALS_FILE")
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    )
    if credentials and not Path(credentials).exists():
        credentials = None
    return SheetConfig(credentials_file=credentials)
