"""Standalone resume skill extraction entrypoint."""

from __future__ import annotations

import argparse
from pathlib import Path

from .pipeline import run_resume_only


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume-root", default="data/deliverables", help="Root directory containing resume.md files.")
    parser.add_argument("--out", default="build_skills/output", help="Directory to write outputs into.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_resume_only(Path(args.resume_root), Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
