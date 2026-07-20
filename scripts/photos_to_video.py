#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
photos_to_video.py — 把一組照片串成 30–90 秒的相片影片（適合 Reels / 短影音）。

用 ffmpeg 產生直式滿版影片，每張照片緩慢推移（Ken Burns），照片之間交叉淡入淡出轉場，
可選配樂。照片會自動縮放並補滿目標畫布（超出裁切、不足補模糊背景），不變形。

需求：ffmpeg 與 ffprobe 在 PATH。

用法：
    python photos_to_video.py 圖1.jpg 圖2.jpg 圖3.png --out reels.mp4
    python photos_to_video.py photos/*.jpg --out reels.mp4 --total 45 --music bgm.mp3

主要參數：
    images            照片路徑（可多張，依給定順序播放）
    --out             輸出檔名（預設 photos_video.mp4）
    --total           影片總長秒數，30–90，預設 45；每張秒數 = total / 張數
    --per             指定每張秒數（給了就忽略 --total）
    --size            畫布尺寸，預設 1080x1920（Reels 直式）。橫式用 1920x1080，方形 1080x1080
    --fps             幀率，預設 30
    --transition      轉場秒數，預設 0.8
    --music           背景音樂檔（選用），自動裁切到影片長度並結尾淡出
    --no-kenburns     關閉 Ken Burns 緩慢推移（改為靜止）
"""
import argparse
import subprocess
import sys
from pathlib import Path

MIN_TOTAL, MAX_TOTAL = 30, 90


def probe_ok() -> bool:
    for tool in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run([tool, "-version"], capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError):
            print(f"[錯誤] 找不到 {tool}，請確認 ffmpeg 已安裝並在 PATH。", file=sys.stderr)
            return False
    return True


def build_filter(n: int, w: int, h: int, per: float, trans: float,
                 fps: int, kenburns: bool) -> str:
    """組出 filter_complex：每張縮放補滿 + 可選 Ken Burns + xfade 串接。"""
    frames = max(int(per * fps), 1)
    segs = []
    for i in range(n):
        # 縮放到覆蓋畫布 → 裁切置中；補滿避免黑邊
        base = (
            f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},setsar=1,fps={fps}"
        )
        if kenburns:
            # 緩慢放大 1.0 → 1.08，營造呼吸感
            base += (
                f",zoompan=z='min(zoom+0.0009,1.08)':d={frames}:"
                f"s={w}x{h}:fps={fps}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            )
        else:
            base += f",trim=duration={per},setpts=PTS-STARTPTS"
        segs.append(f"{base}[v{i}]")

    if n == 1:
        return ";".join(segs) + f";[v0]format=yuv420p[vout]"

    # xfade 逐段串接；offset = 累積播放時間 - 轉場重疊
    chain = segs[:]
    prev = "v0"
    offset = per - trans
    for i in range(1, n):
        out = f"x{i}" if i < n - 1 else "vpre"
        chain.append(
            f"[{prev}][v{i}]xfade=transition=fade:duration={trans}:offset={offset:.3f}[{out}]"
        )
        prev = out
        offset += per - trans
    chain.append("[vpre]format=yuv420p[vout]")
    return ";".join(chain)


def main() -> int:
    ap = argparse.ArgumentParser(description="照片 → 30–90 秒相片影片")
    ap.add_argument("images", nargs="+", help="照片路徑（依序播放）")
    ap.add_argument("--out", default="photos_video.mp4")
    ap.add_argument("--total", type=float, default=45.0)
    ap.add_argument("--per", type=float, default=None)
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--transition", type=float, default=0.8)
    ap.add_argument("--music", default=None)
    ap.add_argument("--no-kenburns", action="store_true")
    args = ap.parse_args()

    if not probe_ok():
        return 1

    images = [Path(p) for p in args.images]
    missing = [p for p in images if not p.exists()]
    if missing:
        print(f"[錯誤] 找不到照片：{', '.join(str(m) for m in missing)}", file=sys.stderr)
        return 1

    n = len(images)
    w, h = (int(x) for x in args.size.lower().split("x"))
    trans = args.transition

    # 決定每張秒數
    if args.per:
        per = args.per
    else:
        total = min(max(args.total, MIN_TOTAL), MAX_TOTAL)
        per = total / n
    # 轉場需短於每張秒數
    if trans >= per:
        trans = max(per * 0.3, 0.2)

    real_total = per * n - trans * (n - 1)
    print(f"[social-post-kit] {n} 張照片 × 每張 {per:.1f}s，轉場 {trans:.1f}s → 約 {real_total:.1f}s，{w}x{h}")

    filt = build_filter(n, w, h, per, trans, args.fps, not args.no_kenburns)

    cmd = ["ffmpeg", "-y"]
    for p in images:
        # 每張輸入用 loop 撐到 per 秒（zoompan/xfade 需要足夠幀）
        cmd += ["-loop", "1", "-t", f"{per:.3f}", "-i", str(p)]

    if args.music:
        cmd += ["-i", args.music]

    cmd += ["-filter_complex", filt, "-map", "[vout]"]

    if args.music:
        music_idx = n
        # 音樂裁到影片長度、結尾淡出
        afade_start = max(real_total - 2, 0)
        cmd += [
            "-map", f"{music_idx}:a",
            "-af", f"afade=t=out:st={afade_start:.2f}:d=2",
            "-shortest", "-c:a", "aac", "-b:a", "192k",
        ]

    cmd += [
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(args.fps),
        "-t", f"{real_total:.3f}", str(args.out),
    ]

    print("[social-post-kit] 執行 ffmpeg…")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("[錯誤] ffmpeg 失敗。", file=sys.stderr)
        return res.returncode
    print(f"[social-post-kit] 完成：{args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
