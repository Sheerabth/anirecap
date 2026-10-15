# anirecap

Anime episodes in, narrated recap videos out. Fandom-canonical summaries fused with embedded subtitles: every voiceover line anchored to a real subtitle cue, every clip cut to match its line, zero anime audio in the final mix.

Battle-tested on a full 12-episode season (blind-agent verified: zero unassigned cues, all timestamps cue-exact). Bring your own episode files.

## The protocol (the whole thing)

1. **Single source.** The fandom wiki episode page is canonical. Season context is gathered for *understanding only* — nothing enters the VO unless this episode's footage proves it.
2. **Full-coverage map.** The entire transcript is split into sections; every section maps to a story beat or to SKIP-with-reason (OP/recaps/EDs/previews, flash-forward cold opens). Unassigned cue count must be zero. Saved as `work/map_<ep>.json`.
3. **Beats from the map only.** Fluent third-person English narration (never character dialogue), 4–7 clips per beat at ~2s each, story-chronological order, every timestamp an exact subtitle cue start.
4. **Scripts render.** Per-beat TTS → video-only cuts matched to VO durations → VO-only mux. See `SKILL.md` for the full spec.

## Quickstart

```bash
# 1. subs out (ENG subrip/CC preferred; no Whisper when subs exist)
python3 scripts/extract.py <episode.mkv> work/ep01/ep01.srt

# 2. draft beats.json from wiki summary + full .srt + coverage map
#    (prompt template: references/beat_prompt.md)

# 3. per-beat voiceover (free edge-tts via uvx, default en-US-GuyNeural)
python3 scripts/tts.py work/beats_ep01.json work/ep01

# 4. video-only cuts matched to VO
python3 scripts/cut.py <episode.mkv> work/beats_ep01.json work/ep01/vo_durations.json work/ep01

# 5. VO-only final (1 video + 1 audio stream, no anime audio)
python3 scripts/assemble.py work/ep01 samples/ep01_CLEAN.mp4
```

Requires: `ffmpeg`, `ffprobe`, `python3` (stdlib only), [`uvx`](https://docs.astral.sh/uv/) with `edge-tts`. No API keys.

## Layout

```
SKILL.md                 agent skill: the protocol, gates, tool constraints
scripts/                 extract / tts / cut / assemble / hits / budget (stdlib + ffmpeg)
references/beat_prompt.md  beat-drafting prompt (fandom-canonical, coverage map)
```

Your episode files, transcripts, maps, and renders stay local — never commit footage, subtitles, or clips.

## Note on footage

This builds *transformative* recaps: original commentary VO, <3s clips, no anime audio. It does not re-upload episodes. Review YouTube's copyright and fair-use rules before publishing anything made with it.
