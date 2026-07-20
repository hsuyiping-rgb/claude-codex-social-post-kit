# Claude / Codex 共用新媒體技能

這是一個可供 Claude Code 與 Codex 共用的新媒體技能，用來把本機資料夾中的照片、課堂分析、文字稿、簡報大綱或 AI 插圖，整理成 Facebook、Instagram 與 Reels 可直接使用的文案、短影音與字幕素材。

## 主要功能

- 產生 Facebook 長文或短版貼文文案。
- 產生 Instagram Caption 與輪播頁文案。
- 產生 Reels 標題、旁白腳本、貼文說明與短句字幕。
- 從圖片資料夾建立 1080 x 1920 直式 Reels 影片。
- 對橫式圖片做直式主體裁切，避免手機畫面中出現過大的留白。
- 可從混有草稿、截圖與不同版本的資料夾中，明確挑選每個段落唯一的最終圖片。
- 產生 Facebook 可上傳的 `.zh_TW.srt` 字幕檔。
- 自動使用 UTF-8 with BOM 與 CRLF 換行，降低中文字幕亂碼風險。

## 適用情境

- 活動照片要轉成 FB / IG / Reels 發布素材。
- 課堂觀察、公開課、學習共同體資料要做成社群貼文。
- 已有 GPT 插圖或簡報圖片，要快速生成 Reels 影片。
- Facebook 上傳 SRT 時遇到檔名格式或中文字亂碼問題。
- Reels 字幕太長、超出畫面，需要改成短句字幕。

## 技能內容

```text
claude-codex-social-post-kit/
  SKILL.md
  README.md
  scripts/
    reels_from_images.py
    facebook_srt.py
```

## 產生直式 Reels 影片

```powershell
python scripts/reels_from_images.py `
  --images-dir "G:\path\to\images" `
  --out "G:\path\to\output\reels_topic_30s.mp4" `
  --duration 30 `
  --crop-mode subject-right
```

輸出規格：

- MP4 / H.264
- 1080 x 1920
- 30 fps
- 靜音 AAC 音軌

`--crop-mode subject-right` 適合左側有留白、右側有主要人物或內容的橫式 AI 插圖。

## 課例簡報的最終圖片選取

製作課例 Reels 時，先依最終 PPTX 或 HTML 的頁面順序選擇圖片，再把選定檔案放到發布包內的 `selected_final_images/`，最後才交給影片工具。這可避免把 `_source`、`screenshot`、`preview`、`draft`、`v2` 或其他中間版本混進成品。

若專案已有 `drawings_vertical/slide_1.png` 至 `slide_N.png`，優先使用這一組；圖片數量、影片段落與字幕 cue 數必須一致。例如 12 張圖片製作 30 秒 Reels，每張約 2.5 秒，字幕也使用 12 則短句。

## 產生 Facebook 字幕

```powershell
python scripts/facebook_srt.py `
  --out "G:\path\to\output\reels_topic.zh_TW.srt" `
  --duration 30.021 `
  --lines "寫作，從看見開始" "共同看見，才有共同語言"
```

字幕輸出會自動處理：

- 檔名結尾為 `.zh_TW.srt`
- UTF-8 with BOM
- CRLF 換行
- 標準 SRT 時間格式

## 使用原則

- 先讀本機來源資料，不憑空編造活動名稱、日期、學校資訊或學習成效。
- 課堂類素材以學生學習事實為主，不寫成泛泛的教師稱讚。
- Reels 字幕保持短句，避免 Facebook 底部字幕區超出畫面。
- 社群發布包要保留最終 MP4、ASCII 檔名的 `.zh_TW.srt`、文案檔與字幕短句來源；中間版圖片不可當作成片輸入。
- 專案完成後，只保留最後影片與最後字幕；中間裁切圖、預覽圖、舊版影片與舊版字幕可清理。

## 驗證

建議每次更新後執行：

```powershell
$env:PYTHONUTF8='1'
python C:\Users\vm\.codex\skills\.system\skill-creator\scripts\quick_validate.py .
python -m py_compile scripts\reels_from_images.py scripts\facebook_srt.py
```
