#!/usr/bin/env python3
"""Build a vertical Reels MP4 from a folder of images."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except Exception as exc:  # pragma: no cover
    raise SystemExit("Pillow is required: pip install pillow") from exc


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def list_images(images_dir: Path) -> list[Path]:
    images = [p for p in images_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS]
    return sorted(images, key=lambda p: p.name.lower())


def subject_center(im: Image.Image, crop_mode: str) -> int:
    w, h = im.size
    if crop_mode == "center":
        return w // 2

    px = im.convert("RGB").load()
    xs: list[int] = []
    start_x = int(w * 0.18) if crop_mode == "subject-right" else 0

    for y in range(0, h, 2):
        for x in range(start_x, w, 2):
            r, g, b = px[x, y]
            mx = max(r, g, b)
            mn = min(r, g, b)
            if (mx - mn > 35 and mx < 245) or mx < 205:
                xs.append(x)

    if not xs:
        return int(w * 0.70) if crop_mode == "subject-right" else w // 2

    detected = int(sum(xs) / len(xs))
    if crop_mode == "subject-right":
        return int(detected * 0.75 + (w * 0.74) * 0.25)
    return detected


def make_vertical_crops(
    images: list[Path],
    crop_dir: Path,
    width: int,
    height: int,
    crop_mode: str,
) -> list[Path]:
    crop_dir.mkdir(parents=True, exist_ok=True)
    out_paths: list[Path] = []

    for image_path in images:
        im = Image.open(image_path).convert("RGB")
        w, h = im.size
        target_ratio = width / height
        source_ratio = w / h

        if source_ratio > target_ratio:
            crop_w = round(h * target_ratio)
            center = subject_center(im, crop_mode)
            left = max(0, min(w - crop_w, center - crop_w // 2))
            crop = im.crop((left, 0, left + crop_w, h))
        else:
            crop_h = round(w / target_ratio)
            top = max(0, min(h - crop_h, (h - crop_h) // 2))
            crop = im.crop((0, top, w, top + crop_h))

        out_path = crop_dir / image_path.name
        crop.resize((width, height), Image.Resampling.LANCZOS).save(out_path, quality=95)
        out_paths.append(out_path)

    return out_paths


def write_concat_file(images: list[Path], concat_path: Path, per_image: float) -> None:
    lines: list[str] = []
    for image in images:
        safe = str(image).replace("'", "'\\''")
        lines.append(f"file '{safe}'")
        lines.append(f"duration {per_image:.6f}")
    lines.append(f"file '{str(images[-1]).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'")
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_video(crops: list[Path], out: Path, duration: float, fps: int) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    per_image = duration / len(crops)

    with tempfile.TemporaryDirectory(prefix="reels-build-") as td:
        tmp = Path(td)
        concat_path = tmp / "images.txt"
        video_only = tmp / "video_only.mp4"
        write_concat_file(crops, concat_path, per_image)

        run([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_path),
            "-vf", f"fps={fps},format=yuv420p",
            "-t", f"{duration:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p",
            str(video_only),
        ])

        run([
            "ffmpeg", "-y",
            "-i", str(video_only),
            "-f", "lavfi", "-t", f"{duration:.3f}",
            "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-shortest", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
            str(out),
        ])


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a vertical 1080x1920 Reels video from images.")
    parser.add_argument("--images-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--size", default="1080x1920")
    parser.add_argument("--crop-mode", choices=["center", "subject", "subject-right"], default="subject-right")
    parser.add_argument("--keep-crops", type=Path, default=None)
    args = parser.parse_args()

    images = list_images(args.images_dir)
    if not images:
        print(f"No images found in {args.images_dir}", file=sys.stderr)
        return 1

    width, height = (int(part) for part in args.size.lower().split("x", 1))

    if args.keep_crops:
        crop_dir = args.keep_crops
        crops = make_vertical_crops(images, crop_dir, width, height, args.crop_mode)
        build_video(crops, args.out, args.duration, args.fps)
    else:
        with tempfile.TemporaryDirectory(prefix="reels-crops-") as td:
            crops = make_vertical_crops(images, Path(td), width, height, args.crop_mode)
            build_video(crops, args.out, args.duration, args.fps)

    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
