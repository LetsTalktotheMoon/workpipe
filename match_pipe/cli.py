#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .matcher import MatchEngine


ROOT = Path(__file__).resolve().parents[1]


def _default_query_job_id(engine: MatchEngine) -> str:
    scraped_jobs = [job for job in engine.index.jobs if job.source_kind == "scraped"]
    if not scraped_jobs:
        return engine.index.jobs[0].job_id
    return scraped_jobs[0].job_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Requirement-unit-based JD matcher.")
    parser.add_argument("--job-id", default="", help="Query a job_id from the indexed pool.")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--scraped-only", action="store_true")
    parser.add_argument("--portfolio-only", action="store_true")
    parser.add_argument("--dump-job", action="store_true", help="Print the structured query job before matching.")
    parser.add_argument("--output", default="", help="Optional JSON output path.")
    args = parser.parse_args()

    include_scraped = not args.portfolio_only
    include_portfolio = not args.scraped_only
    if not include_scraped and not include_portfolio:
        raise SystemExit("At least one of scraped or portfolio inputs must be enabled.")

    engine = MatchEngine.from_project_data(
        include_scraped=include_scraped,
        include_portfolio=include_portfolio,
    )
    if not engine.index.jobs:
        raise SystemExit("No jobs indexed.")

    job_id = str(args.job_id or "").strip() or _default_query_job_id(engine)
    response = engine.match_by_job_id(job_id, top_k=args.top_k)
    payload = response.to_dict()
    if args.dump_job:
        payload["query_structured"] = response.query.to_dict()

    output_path = Path(args.output).expanduser().resolve() if str(args.output or "").strip() else None
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
