#!/usr/bin/env python3
"""
build_resumes.py — Batch MD→PDF resume compiler.

Orchestrates: resumes/*.md → output/tex/*.tex → output/pdf/*.pdf
Auto-detects PDFs exceeding 2 pages and progressively compresses.

Compression levels:
  0 = Default (two-line header, two-line job, normal spacing)
  1 = Single-line header (name | contact)
  2 = Level 1 + single-line job titles
  3 = Level 2 + compact spacing

Usage:
    python3 build_resumes.py                         # compile all
    python3 build_resumes.py --single resumes/03*.md # compile one
    python3 build_resumes.py --parallel              # parallel compilation
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# Import the converter
sys.path.insert(0, os.path.dirname(__file__))
from md_to_tex import convert_file


ROOT = Path(__file__).parent
RESUME_DIR = ROOT / "resumes"
TEX_DIR = ROOT / "output" / "tex"
PDF_DIR = ROOT / "output" / "pdf"
JUNK_EXTS = [".aux", ".log", ".out", ".fls", ".fdb_latexmk", ".synctex.gz"]
MAX_PAGES = 2
MAX_LEVEL = 3
REQUIRED_SECTIONS = (
    "Professional Summary",
    "Skills",
    "Work Experience",
    "Education",
)


def get_pdf_pages_from_log(compile_stdout: str) -> int:
    """从 xelatex 编译输出中提取页数。
    xelatex 输出: 'Output written on file.pdf (N pages, ...)'
    """
    import re
    m = re.search(r'Output written on .+?\((\d+) pages?', compile_stdout, re.DOTALL)
    if m:
        return int(m.group(1))
    return -1


def compile_tex(tex_path: str, pdf_dir: Path = None) -> tuple[str, bool, str, int]:
    """Compile a single .tex → .pdf. Returns (filename, success, message, pages)."""
    if pdf_dir is None:
        pdf_dir = PDF_DIR
    tex_path = Path(tex_path)
    tex_name = tex_path.name
    pdf_name = tex_path.with_suffix(".pdf").name

    cmd = [
        "xelatex",
        "-interaction=nonstopmode",
        "-output-directory", str(pdf_dir),
        str(tex_path),
    ]

    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=60
        )

        pdf_path = pdf_dir / pdf_name
        if pdf_path.exists():
            # Clean junk files from pdf_dir
            for ext in JUNK_EXTS:
                junk = pdf_dir / tex_path.with_suffix(ext).name
                if junk.exists():
                    junk.unlink()
            pages = get_pdf_pages_from_log(result.stdout)
            return (tex_name, True, f"→ {pdf_name}", pages)
        else:
            log_tail = result.stdout[-800:] if result.stdout else "No output"
            return (tex_name, False, f"Compilation failed. Log tail:\n{log_tail}", -1)

    except subprocess.TimeoutExpired:
        return (tex_name, False, "Compilation timed out (>60s)", -1)
    except Exception as e:
        return (tex_name, False, f"System error: {e}", -1)


def validate_tex_sections(tex_path: Path, required_sections: tuple[str, ...] = REQUIRED_SECTIONS) -> list[str]:
    text = tex_path.read_text(encoding="utf-8")
    missing: list[str] = []
    for section in required_sections:
        if f"\\section{{{section}}}" not in text:
            missing.append(section)
    return missing


def resolve_output_dirs(md_path: Path) -> tuple[Path, Path]:
    """根据源文件路径决定输出目录。
    如果源文件在 output/{profile_id}/resumes/ 下，输出到同 profile 的 tex/ 和 pdf/。
    否则使用默认 output/tex/ 和 output/pdf/。
    """
    try:
        rel = md_path.resolve().relative_to(ROOT / "output")
        parts = rel.parts  # e.g., ('vinnie_illinois_447', 'resumes', 'xxx.md')
        if len(parts) >= 3 and parts[1] == "resumes":
            profile_id = parts[0]
            profile_tex = ROOT / "output" / profile_id / "tex"
            profile_pdf = ROOT / "output" / profile_id / "pdf"
            return profile_tex, profile_pdf
    except (ValueError, IndexError):
        pass
    return TEX_DIR, PDF_DIR


def build_one(md_path: Path, level: int = 0, tex_dir: Path = None, pdf_dir: Path = None) -> tuple[str, bool, int, int]:
    """Build one resume: MD→TEX→PDF at given compression level.
    Returns (filename, success, pages, level).
    """
    if tex_dir is None or pdf_dir is None:
        tex_dir, pdf_dir = resolve_output_dirs(md_path)
    tex_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    try:
        tex_path = convert_file(str(md_path), str(tex_dir), level=level)
        missing_sections = validate_tex_sections(Path(tex_path))
        if missing_sections:
            return (
                md_path.name,
                False,
                -1,
                level,
            )
        name, ok, msg, pages = compile_tex(tex_path, pdf_dir=pdf_dir)
        if ok:
            return (md_path.name, True, pages, level)
        else:
            return (md_path.name, False, -1, level)
    except Exception as e:
        return (md_path.name, False, -1, level)


def build_progressive(md_path: Path, tex_dir: Path = None, pdf_dir: Path = None) -> tuple[str, bool, int, int]:
    """渐进式构建：从 level 0 开始，如果超过 2 页则逐级压缩。"""
    for level in range(MAX_LEVEL + 1):
        name, ok, pages, lvl = build_one(md_path, level=level, tex_dir=tex_dir, pdf_dir=pdf_dir)
        if not ok:
            return (name, False, pages, lvl)
        if pages <= MAX_PAGES:
            return (name, ok, pages, lvl)
        # 超页，尝试下一个压缩级别
    # 所有级别都试过了，返回最后一次结果
    return (name, ok, pages, MAX_LEVEL)


def main():
    ap = argparse.ArgumentParser(description="Batch compile MD resumes to PDF")
    ap.add_argument("--single", nargs="+", help="Specific .md file(s) to compile")
    ap.add_argument("--parallel", action="store_true", help="Compile in parallel")
    ap.add_argument("--tex-only", action="store_true", help="Only generate .tex, skip PDF compilation")
    ap.add_argument("--level", type=int, default=None, choices=[0, 1, 2, 3],
                    help="Force specific compression level (skip progressive)")
    args = ap.parse_args()

    # Determine input files
    if args.single:
        md_files = [Path(f) for f in args.single]
    else:
        md_files = sorted(RESUME_DIR.glob("*.md"))

    if not md_files:
        print("❌ No .md files found.")
        sys.exit(1)

    # Ensure output dirs exist
    TEX_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    if args.tex_only:
        # 仅生成 TEX
        print(f"📝 Converting {len(md_files)} Markdown file(s) to LaTeX...\n")
        level = args.level if args.level is not None else 0
        for md in md_files:
            try:
                out = convert_file(str(md), str(TEX_DIR), level=level)
                print(f"  ✅ {md.name} → {Path(out).name}")
            except Exception as e:
                print(f"  ❌ {md.name}: {e}", file=sys.stderr)
        print(f"\n🎉 Generated .tex file(s) in {TEX_DIR}")
        return

    # ── 全量构建 ──
    print(f"📝 Building {len(md_files)} resume(s)...\n")
    t0 = time.time()
    success_count = 0
    fail_count = 0
    level_stats = {0: 0, 1: 0, 2: 0, 3: 0}

    for md in md_files:
        tex_out, pdf_out = resolve_output_dirs(md)
        tex_out.mkdir(parents=True, exist_ok=True)
        pdf_out.mkdir(parents=True, exist_ok=True)
        if args.level is not None:
            name, ok, pages, lvl = build_one(md, level=args.level, tex_dir=tex_out, pdf_dir=pdf_out)
        else:
            name, ok, pages, lvl = build_progressive(md, tex_dir=tex_out, pdf_dir=pdf_out)

        if ok:
            level_label = f"L{lvl}" if lvl > 0 else "  "
            page_warn = " ⚠️ >2pp" if pages > MAX_PAGES else ""
            print(f"  ✅ [{level_label}] {name} → {pages}p{page_warn}")
            success_count += 1
            level_stats[lvl] = level_stats.get(lvl, 0) + 1
        else:
            print(f"  ❌ {name}: build failed")
            fail_count += 1

    elapsed = time.time() - t0
    print(f"\n🎉 Done in {elapsed:.1f}s — {success_count}/{len(md_files)} succeeded, {fail_count} failed.")

    # 显示压缩统计
    compressed = sum(v for k, v in level_stats.items() if k > 0)
    if compressed > 0:
        print(f"   Compression: {level_stats[0]} default, ", end="")
        for lvl in range(1, MAX_LEVEL + 1):
            if level_stats.get(lvl, 0) > 0:
                print(f"{level_stats[lvl]} at L{lvl}, ", end="")
        print()

    if fail_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
