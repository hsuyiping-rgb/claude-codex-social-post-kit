#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pack.py — 建立「貼文包」資料夾骨架並產出發布清單範本。

只用 Python 標準庫，跨平台。技能會呼叫這支腳本先把資料夾與空白檔案建好，
接著再把文案寫進各 .txt、把圖與影片放進去，最後補完發布清單。

用法：
    python pack.py --topic "閱讀闖關" --platforms fb ig reels --outdir .

參數：
    --topic       主題（會出現在資料夾名與發布清單標題）
    --platforms   要產出的平台，可多選：fb ig reels（預設三者都要）
    --outdir      在哪個目錄下建立貼文包資料夾（預設當前目錄）
    --date        指定日期 YYYYMMDD（預設今天）
"""
import argparse
import datetime as _dt
import sys
from pathlib import Path

PLATFORM_FILES = {
    "fb": ["FB.txt"],
    "ig": ["IG.txt"],
    "reels": ["Reels說明.txt", "Reels腳本.txt"],
}

CHECKLIST_TEMPLATE = """# 發布清單 — {topic}（{date}）

> 這份清單是「手動發布」的操作依據。技能只負責產出素材，實際上傳與送出請由本人完成，
> 以便最後一次確認學生肖像與內容無誤。

## 一、發布前檢查（每次都要過一遍）
- [ ] 肖像已處理：三擇一 →（a）原照已授權 /（b）未授權者已打碼或改用背影 /（c）已重繪為插畫
- [ ] 若用重繪插圖，未讓它被誤認為紀實照片（必要時另附授權真照或文字說明）
- [ ] 文案中的人名、數字、名次皆為真實資訊（無 AI 填空）
- [ ] hashtag 中的 `○○國小` 已替換為真實校名
- [ ] 錯字、標點檢查一遍

## 二、素材對應（哪張圖配哪段文）
| 平台 | 文案檔 | 搭配圖／影片 | 建議發布時間 |
|------|--------|--------------|--------------|
{rows}

## 三、逐平台發布步驟
{steps}

## 四、發布後
- [ ] 隔天看一次觸及與留言，記錄哪種內容反應好（供下次調整）
"""

TIME_HINT = {
    "fb": "晚上 20:00–22:00",
    "ig": "晚上 20:00–22:00",
    "reels": "週末白天",
}

STEP_BLOCKS = {
    "fb": "### Facebook\n1. 開啟粉專 → 建立貼文\n2. 貼上 `FB.txt` 內容\n3. 上傳搭配照片\n4. 確認預覽 → 發布\n",
    "ig": "### Instagram\n1. 新貼文 → 選 4:5 直式\n2. 上傳照片（多圖依發布清單順序）\n3. 貼上 `IG.txt` 內容\n4. hashtag 可放說明或首則留言 → 分享\n",
    "reels": "### Reels（IG／FB）\n1. 上傳 `reels_直式_有字幕.mp4`\n2. 貼上 `Reels說明.txt`\n3. 選封面（可用 1080×1920 字卡）\n4. 確認字幕未被底部 UI 遮住 → 分享\n",
}


def build(topic: str, platforms: list[str], outdir: Path, date: str) -> Path:
    folder = outdir / f"貼文包_{topic}_{date}"
    folder.mkdir(parents=True, exist_ok=True)

    # 建立各平台空白文案檔
    for p in platforms:
        for fname in PLATFORM_FILES.get(p, []):
            f = folder / fname
            if not f.exists():
                f.write_text("", encoding="utf-8")

    # 組發布清單
    rows, steps = [], []
    for p in platforms:
        label = {"fb": "Facebook", "ig": "Instagram", "reels": "Reels"}[p]
        first_file = PLATFORM_FILES[p][0]
        rows.append(f"| {label} | `{first_file}` | （填入檔名） | {TIME_HINT[p]} |")
        steps.append(STEP_BLOCKS[p])

    checklist = CHECKLIST_TEMPLATE.format(
        topic=topic,
        date=date,
        rows="\n".join(rows),
        steps="\n".join(steps),
    )
    (folder / "發布清單.md").write_text(checklist, encoding="utf-8")
    return folder


def main() -> int:
    ap = argparse.ArgumentParser(description="建立貼文包資料夾骨架")
    ap.add_argument("--topic", required=True, help="主題")
    ap.add_argument("--platforms", nargs="+", default=["fb", "ig", "reels"],
                    choices=["fb", "ig", "reels"], help="要產出的平台")
    ap.add_argument("--outdir", default=".", help="輸出目錄")
    ap.add_argument("--date", default=_dt.date.today().strftime("%Y%m%d"),
                    help="日期 YYYYMMDD")
    args = ap.parse_args()

    folder = build(args.topic, args.platforms, Path(args.outdir), args.date)
    print(f"[social-post-kit] 貼文包已建立：{folder}")
    for child in sorted(folder.iterdir()):
        print(f"  - {child.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
