---
name: claude-codex-social-post-kit
description: >-
  Claude and Codex shared social media skill for creating Facebook, Instagram, and Reels copy packs,
  vertical short videos, and Facebook-compatible SRT subtitles from local photos, lesson-analysis notes,
  classroom screenshots, or generated illustrations. Use when the user asks for FB/IG/Reels copy,
  social post packages, short-video scripts, SRT subtitles, Facebook-compatible captions,
  or vertical Reels videos from a folder of images.
  中文情境同樣適用：當使用者說「幫我做這次活動的貼文」「把這段影片做成 Reels」「這批照片做成 IG 貼文」
  「寫個 FB 貼文文案」「班級活動要發社群」「短影音腳本」「做張字卡」「幫我上 Facebook 字幕」
  「照片串成直式短影音」，或丟一批照片／影片／課例分析檔並要求做成社群貼文時，務必使用此技能。
  即使使用者只說「發個文」「做成 IG」而沒明講平台規格，只要目的是產出社群貼文素材，也應觸發。
  發布動作留給使用者手動，不自動貼文。
---

# Claude / Codex Shared Social Post Kit

## Purpose

Turn a local content folder into publishable social media materials:

- Facebook long or short post copy.
- Instagram caption and carousel text.
- Reels title, description, voiceover script, and subtitle file.
- Reels video assembled from local images.

Prefer concrete artifacts over explanation. Read the source folder first, use the user's existing analysis files as the source of truth, and write outputs into a clearly named package folder beside the source content.

## Skill Directory

`$SKILL_DIR` in the examples below is this skill's own folder:

- Claude Code: `C:\Users\vm\.claude\skills\claude-codex-social-post-kit`
- Codex: `C:\Users\vm\.codex\skills\claude-codex-social-post-kit`

## Bundled References and Scripts

| File | Use it when |
|------|-------------|
| `references/copywriting.md` | 撰寫 FB／IG／Reels 文案前先讀：各平台語氣、長度、hashtag 數量與範本 |
| `references/platform-specs.md` | 決定圖片尺寸、字數上限、影片規格前先讀 |
| `scripts/pack.py` | 建立 `貼文包_<主題>_<YYYYMMDD>/` 資料夾骨架與發布清單範本（純標準庫） |
| `scripts/photos_to_video.py` | 只有照片沒有影片時，把 4–10 張照片串成 30–90 秒直式相片影片（Ken Burns + 轉場 + 選用配樂，需 ffmpeg） |
| `scripts/reels_from_images.py` | 從一個圖片資料夾產 1080x1920 Reels，含裁切模式（需 ffmpeg） |
| `scripts/facebook_srt.py` | 產 Facebook 相容的 `.zh_TW.srt`（UTF-8 BOM + CRLF） |

```bash
python $SKILL_DIR/scripts/pack.py --topic "閱讀闖關" --platforms fb ig reels --outdir .
python $SKILL_DIR/scripts/photos_to_video.py 圖1.jpg 圖2.jpg 圖3.jpg --out reels_相片影片.mp4 --total 45 --music bgm.mp3
```

## Guardrails for School Content

學校場景不可省略的三條護欄：

1. **肖像權優先**：產出任何含學生照片的內容前，先問使用者「這些照片是否已取得家長／學校授權？」並提供三條路徑：(a) 已授權直接用原照；(b) 打碼或改用背影、局部特寫；(c) 用 `draw` 技能重繪為插畫（對外公開最安全）。不確定時傾向保守。
2. **不捏造事實**：不自動生成參加人數、得獎名次、師生評語等未提供的資訊。需要具體數字或引言時向使用者索取。
3. **發布留給使用者**：終點是「產出貼文包 + 發布清單」。不要用瀏覽器或平台 API 代為登入、貼文、送出。

## Source Reading Order

1. Inspect the requested folder and list available images, transcripts, analysis notes, decks, and videos.
2. If a lesson-analysis file exists, use it as the main narrative source.
3. If a slide outline exists, use it to map image order and short-video beats.
4. If only images exist, infer a visual sequence from filenames and create cautious, source-grounded copy.
5. Do not invent names, dates, school details, or claims not present in the source files.

## Final Asset Selection

Before rendering a Reels video, identify the exact final visual sequence. Do not pass a directory containing drafts, source screenshots, crops, or multiple variants directly to the video script.

- For lesson-analysis decks, read the final deck or HTML outline and use one visual per slide/beat in that order.
- Prefer an explicit vertical final set such as `drawings_vertical/slide_1.png` through `slide_N.png`.
- Exclude files or folders named `_source`, `screenshot`, `preview`, `draft`, `v2`, `clean`, or other non-final variants unless the user explicitly selects them.
- When a source folder contains mixed variants, prepare a dedicated `selected_final_images/` folder inside the new social package containing only the chosen images. Count its images before rendering; the count must equal the planned Reels beats and subtitle cues.
- Keep original sources untouched. The selected-image folder is a reproducible build input and may be removed only when the user asks for final cleanup.

## Copy Package Workflow

Create an output folder named like:

`新媒體文案包_<topic>_<YYYYMMDD>`

Recommended files:

- `FB.txt`
- `IG.txt`
- `Reels_腳本.txt`
- `素材使用建議.md`

For a Reels request, also include the final `.mp4`, the final ASCII-named `.zh_TW.srt`, and a plain-text list of the selected subtitle lines in the same package.

For lesson or classroom content, write in Traditional Chinese unless the user asks otherwise. Focus on observable learning facts: what students saw, said, read, revised, or exchanged. Avoid turning the post into generic praise of a teacher or a class.

## Reels Video Workflow

Use `scripts/reels_from_images.py` when the user asks to turn local images into a Reels video.

Default choices:

- Output video: MP4, H.264, 1080 x 1920, 30 fps.
- Duration: 30 seconds unless the user specifies otherwise.
- Image timing: distribute duration evenly across all selected images.
- Select exactly one final image per planned beat before running the script. For a 30-second, 12-beat lesson Reels, use 12 images at about 2.5 seconds each.
- Audio: include a silent AAC track for platform compatibility.
- If source images are horizontal, do not simply shrink them into the center with large blank areas. Use vertical crop mode so the subject fills the Reels frame.
- For generated classroom illustrations that fade out on the left, use right-biased subject cropping.

Example:

```powershell
python $SKILL_DIR\scripts\reels_from_images.py `
  --images-dir "G:\...\圖片\GPT插圖" `
  --out "G:\...\新媒體文案包_主題_20260718\reels_topic_30s.mp4" `
  --duration 30 `
  --crop-mode subject-right
```

If the user reports large blank areas or small centered images, regenerate the video with vertical crop mode instead of a blurred-background layout.

## Facebook SRT Workflow

Use `scripts/facebook_srt.py` when creating subtitles for Facebook or Instagram uploads.

Rules learned from Facebook Reels upload behavior:

- Filename must include a language code, for example `filename.zh_TW.srt`.
- For Traditional Chinese, use `.zh_TW.srt`.
- Write the file as UTF-8 with BOM. UTF-8 without BOM may open as mojibake in some Windows or Facebook upload contexts.
- Use CRLF line endings.
- Keep each subtitle cue short. Facebook's bottom caption area may overflow with long Chinese lines.
- For a 30-second, 12-image Reels, prefer 12 cues of about 2.5 seconds each.
- Avoid two or three full subtitle lines unless the user explicitly wants voiceover-style subtitles.

Example:

```powershell
python $SKILL_DIR\scripts\facebook_srt.py `
  --lines "寫作，從看見開始" "共同看見，才有共同語言" `
  --out "G:\...\utsugi_taiwanese_writing_reels_30s.zh_TW.srt" `
  --duration 30.021
```

If the user reports a Facebook error saying the SRT filename is wrong, rename or regenerate the file as `ascii_slug.zh_TW.srt`.

If the user reports mojibake, regenerate with UTF-8 BOM and verify the first bytes are `EF BB BF`.

If the user reports subtitles exceed the page or screen, rewrite subtitles into shorter cues. Prefer a single compact sentence per cue.

## Final Cleanup

When the project is complete and the user asks to clean up:

- Keep only the final video and final subtitle if that is what the user requests.
- Remove preview images, old SRT files, old video versions, crop folders, build folders, and draft copy files from the output package.
- Do not delete original source images, transcripts, lesson-analysis files, decks, or videos.
- Before deleting recursively, verify the target path is the intended output package folder.

## Quality Checks

For every final Reels video, verify:

- `ffprobe` reports 1080 x 1920.
- Duration matches the subtitle end time.
- Video has an AAC audio stream, even if silent.
- A sampled preview frame shows subject-filled composition, not a small image floating in a large blank layout.
- Selected image count, visual-beat count, and subtitle-cue count agree.

For every final SRT, verify:

- Filename matches `^[A-Za-z0-9_-]+\.zh_TW\.srt$` for Traditional Chinese Facebook uploads.
- File is UTF-8 with BOM.
- Time cues use `HH:MM:SS,mmm --> HH:MM:SS,mmm`.
- Final cue does not exceed the video duration.
