"""Standalone JD skill extraction entrypoint."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_jd_only


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--jd-scraped-path",
        default="data/job_tracker/jobs_catalog.json",
        help="Structured full JD catalog path. Flag name is kept for compatibility.",
    )
    parser.add_argument(
        "--portfolio-index-path",
        default="data/deliverables/resume_portfolio/portfolio_index.json",
        help="Portfolio index used by the job webapp catalog.",
    )
    parser.add_argument("--out", default="build_skills/output", help="Directory to write outputs into.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_jd_only(Path(args.jd_scraped_path), Path(args.portfolio_index_path), Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
