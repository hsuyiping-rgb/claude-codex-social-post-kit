#!/usr/bin/env python3
"""Write Facebook-compatible SRT subtitles with language-code filename and UTF-8 BOM."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def timestamp(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    millis = round(seconds * 1000)
    hh, rem = divmod(millis, 3_600_000)
    mm, rem = divmod(rem, 60_000)
    ss, ms = divmod(rem, 1000)
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def ensure_facebook_name(path: Path, lang: str) -> Path:
    if path.suffix.lower() != ".srt":
        path = path.with_suffix(".srt")
    expected_suffix = f".{lang}.srt"
    if not path.name.endswith(expected_suffix):
        stem = re.sub(r"[^A-Za-z0-9_-]+", "_", path.stem).strip("_") or "captions"
        path = path.with_name(f"{stem}.{lang}.srt")
    return path


def read_lines(args: argparse.Namespace) -> list[str]:
    if args.lines:
        return [line.strip() for line in args.lines if line.strip()]
    if args.lines_file:
        return [line.strip() for line in args.lines_file.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    raise SystemExit("Provide --lines or --lines-file")


def build_srt(lines: list[str], duration: float) -> str:
    per = duration / len(lines)
    blocks: list[str] = []
    for idx, line in enumerate(lines, start=1):
        start = (idx - 1) * per
        end = duration if idx == len(lines) else idx * per
        blocks.append(f"{idx}\r\n{timestamp(start)} --> {timestamp(end)}\r\n{line}\r\n")
    return "\r\n".join(blocks)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Facebook-compatible SRT subtitles.")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--duration", type=float, required=True)
    parser.add_argument("--lang", default="zh_TW")
    parser.add_argument("--lines", nargs="*")
    parser.add_argument("--lines-file", type=Path)
    args = parser.parse_args()

    lines = read_lines(args)
    if not lines:
        print("No subtitle lines provided", file=sys.stderr)
        return 1

    out = ensure_facebook_name(args.out, args.lang)
    out.parent.mkdir(parents=True, exist_ok=True)
    content = build_srt(lines, args.duration)
    out.write_text(content, encoding="utf-8-sig", newline="")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
