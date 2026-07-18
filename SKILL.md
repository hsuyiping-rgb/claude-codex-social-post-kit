---
name: claude-codex-social-post-kit
description: Claude and Codex shared social media skill for creating Facebook, Instagram, and Reels copy packs, vertical short videos, and Facebook-compatible SRT subtitles from local photos, lesson-analysis notes, classroom screenshots, or generated illustrations. Use when the user asks for FB/IG/Reels copy, social post packages, short-video scripts, SRT subtitles, Facebook-compatible captions, or vertical Reels videos from a folder of images.
---

# Claude / Codex Shared Social Post Kit

## Purpose

Turn a local content folder into publishable social media materials:

- Facebook long or short post copy.
- Instagram caption and carousel text.
- Reels title, description, voiceover script, and subtitle file.
- Reels video assembled from local images.

Prefer concrete artifacts over explanation. Read the source folder first, use the user's existing analysis files as the source of truth, and write outputs into a clearly named package folder beside the source content.

## Source Reading Order

1. Inspect the requested folder and list available images, transcripts, analysis notes, decks, and videos.
2. If a lesson-analysis file exists, use it as the main narrative source.
3. If a slide outline exists, use it to map image order and short-video beats.
4. If only images exist, infer a visual sequence from filenames and create cautious, source-grounded copy.
5. Do not invent names, dates, school details, or claims not present in the source files.

## Copy Package Workflow

Create an output folder named like:

`新媒體文案包_<topic>_<YYYYMMDD>`

Recommended files:

- `FB.txt`
- `IG.txt`
- `Reels_腳本.txt`
- `素材使用建議.md`

For lesson or classroom content, write in Traditional Chinese unless the user asks otherwise. Focus on observable learning facts: what students saw, said, read, revised, or exchanged. Avoid turning the post into generic praise of a teacher or a class.

## Reels Video Workflow

Use `scripts/reels_from_images.py` when the user asks to turn local images into a Reels video.

Default choices:

- Output video: MP4, H.264, 1080 x 1920, 30 fps.
- Duration: 30 seconds unless the user specifies otherwise.
- Image timing: distribute duration evenly across all selected images.
- Audio: include a silent AAC track for platform compatibility.
- If source images are horizontal, do not simply shrink them into the center with large blank areas. Use vertical crop mode so the subject fills the Reels frame.
- For generated classroom illustrations that fade out on the left, use right-biased subject cropping.

Example:

```powershell
python C:\Users\vm\.codex\skills\claude-codex-social-post-kit\scripts\reels_from_images.py `
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
python C:\Users\vm\.codex\skills\claude-codex-social-post-kit\scripts\facebook_srt.py `
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

For every final SRT, verify:

- Filename matches `^[A-Za-z0-9_-]+\.zh_TW\.srt$` for Traditional Chinese Facebook uploads.
- File is UTF-8 with BOM.
- Time cues use `HH:MM:SS,mmm --> HH:MM:SS,mmm`.
- Final cue does not exceed the video duration.
