---
name: anirecap
description: Turn anime episodes into narrated recap videos. Use when user says anime recap, recap this episode, make recap video. Fandom-canonical, full-coverage transcript mapping, fluent English VO, VO-only mix, fast cuts.
---

# Recap Builder — the only path

## Rules (global)

1. **Fandom wins.** The fandom wiki episode page is the single canonical summary source. It beats Wikipedia, MAL, everything. If the episode page's summary section is blank/thin (happens on small wikis), backfill ONLY from same-wiki character/location pages, and flag each backfilled beat `GAP-FILL` in the map. Never pull a second wiki silently.
2. **Season context is for understanding, never for VO.** Fetch it the same way every time: (a) Wikipedia series premise (1 paragraph: who, skill, goal), (b) fandom character pages for anyone debuting/returning this episode (origin, ability, season role), (c) fandom episode list for position (what came before/after). Extract: premise + episode position + debutants + season drivers (wars, successions). Nothing enters the voiceover unless this episode's footage + cues prove it.
3. **Skipped sections don't exist.** Opening songs, prior-episode recaps, ending songs, post-ED teasers, next-episode previews are excluded from the map, the clips, and the VO. Entirely. Detect OP/ED per episode from the transcript (`opening theme song playing` + title cards, `Next time` / preview) — never hardcode cue numbers, OP position moves between episodes. Boundary rules: mid-episode title cards (eyecatches) STAY inside their surrounding section; the episode ends at the last in-episode cue (ED theme / "Next time" card = SKIP even when story talk plays over them). Names: on-screen stats spelling wins for all spellings (transliteration varies across wiki pages — first stats-screen occurrence is canonical).
4. **Fluent English VO.** Brainrot means fast cuts, never broken English. Full proper sentences only. Staccato fragments are banned.
5. **No length cap, no episode-number bonus.** Cover what the episode needs. Same weight rubric for every episode — EP01 gets no premium for being first. An episode runs longer only if it genuinely earns more KEEP beats. ~60s/episode is typical; genuinely dense episodes run longer.
6. **Weight decides screentime, evenly.** Every beat gets `weight` 1–3 at map time, scored identically in every episode. Each weight point ≈ 4 seconds of VO (≈1 fluent sentence): weight 3 ≈ 12s / 3 sentences, 2 ≈ 8s / 2 sentences, 1 ≈ 4s / 1 sentence. Episode length = `sum(weights) × 4s`. Clips = `round(beat_seconds / 2)` so pace holds ~2s everywhere.
   - **3 — irreversible plot.** Recruitments, oaths, power reveals, abductions, duel outcomes, episode-title moments. Cutting it breaks the season.
   - **2 — stakes with setup.** Talent demos, motivating backstory, arranged confrontations, night-before reckonings.
   - **1 — bridges.** Travel, meals, market filler, lessons. Compress into montages.
   - Score it without vibes: (a) does a later episode depend on this? (b) is it why someone clicks this episode? Two yeses = 3, one = 2, none = 1.
7. **Creative calls serve retention.** Approx windows, emphasis, hooks — choose whatever sells the recap, within the gates below.

## Workflow

### Step 1 — Detailed summary (single source) + series context
1. Pull the fandom wiki episode page. Read all of it before touching video. Note `flash-forward / flashback / cold open / X years later` labels.
2. Pull Season 1 context (premise, episode position, key characters) for YOUR understanding only.
3. Output: episode beats in wiki order + time labels (past/present/future).

### Step 2 — Full transcript + coverage map (mandatory artifact)
1. Extract subs: `python3 scripts/extract.py <input.mkv> <work/ep.srt>` (ENG subrip/CC preferred; never Whisper when subs exist).
2. Parse ALL cues (`python3 scripts/hits.py <ep.srt> <keyword>...` gives hit counts + first matches for the table — never eyeball). Note in-world time cards (calendar-year captions, `X YEARS LATER`, `CHARACTER, AGE N`), OP/recap/ED/preview ranges (marked SKIP, never clipped).
3. Build the verification table — one row per wiki beat:

| Wiki beat | Transcript evidence (cue timestamps + quotes, with hit counts) | Verdict |
|---|---|---|
| ... | `05:27` "awakening line" (keyword: 5 hits) | KEEP |
| ... | `keyword: 0 hits` (novel-only backstory, skipped scene) | NEVER ANIMATED → rephrase or DROP |
| ... | `00:34` gathering, adult cast contradicts child-protagonist timeline | FUTURE flash-forward → DROP |

4. Verdicts: KEEP (cue-backed) / REPHRASE (event true, wiki wording unshowable) / DROP (0 hits, future/past cold open, OP/ED/preview).
5. Assign EVERY cue range to a beat or to SKIP-with-reason. Unassigned count must be zero. Save as `work/map_<ep>.json`.

### Step 3 — beats.json (from the map only)
- Input: wiki summary + full .srt + coverage map. Nothing else.
- Each beat: `vo_text` (sentences = weight: w3 → 3, w2 → 2, w1 → 1; third-person narration paraphrasing its anchor quotes ONLY) + `clips` (count = `round(expected_seconds / 2)`, 2 minimum) + `weight` + `quote` (≤12 words, copied from a real cue) + `"time"`.
- VO never speaks character dialogue. No first/second-person quotes ("State your name", "I swear", "We shall"). Narrate speech acts instead: "the lord demands his name", "the recruit swears lifelong service".
- Beats sorted STORY-chronological (time cards rule), not air order. Flash-forward cold opens dropped by default.
- Every clip `start` is an exact subtitle cue start `HH:MM:SS.mmm`. No invented timestamps. Silent action anchored to nearest cue, `"approx": true`.
- Prefer, in order: stat/ability screens, name declarations, impact reaction lines (gasps, "grazed him"), weapon draws/clashes, oath kneels, food/bribe gags. Talking-head filler only to bridge.
- **VO / subs / clip lock (unbreakable).** Every clip must visually show what its beat's `vo_text` narrates, proven in the coverage map (wiki beat → cue timestamps + quotes → KEEP). Content-unchecked clips are banned — never evenly space clips across a range, never auto-grab nearby cue text as a quote, never illustrate a line with unrelated footage. If no cue-backed visual exists, rephrase the VO to what the footage proves or DROP the beat.
- Pace: 4-7 clips per beat, each ~2s (allow up to 2.6s; dense text overlays ≤4s) after auto-split. No static shot breathes.

```json
{"beats": [{"id": "b1", "vo_text": "...", "quote": "...", "time": "present", "clips": [{"start": "00:04:01.783"}]}]}
```

### Step 4 — Render (scripts only, no hand-cutting)
```
python3 scripts/tts.py beats.json work/
python3 scripts/budget.py beats.json work/vo_durations.json   # actuals vs weight targets, ±35% tolerance
python3 scripts/cut.py <input.mkv> beats.json work/vo_durations.json work/
python3 scripts/assemble.py work/ out.mp4
python3 scripts/subs.py beats.json work/vo_durations.json work/   # voiceover.srt + .ass per episode (timing exact, no transcription)
```
- TTS: one mp3 per beat (default `en-US-GuyNeural` via `uvx edge-tts`), concat to `vo_full.mp3`. Blob VO banned. Sizing: this voice floors at ~5s per sentence — write short sentences (w1 ≈ 10-14 words, w2 ≈ 20-26, w3 ≈ 30-38) or budget check fails and you re-trim.
- Cut: video-only `-an`, 720p `libx264 veryfast crf23`, per-beat duration split evenly across clips.
- Assemble: `montage.mp4` + `vo_full.mp3` → `-map 0:v -map 1:a -c:v copy -c:a aac -shortest`. Exactly 1 video + 1 audio stream. No anime audio ever.
- Frame check: thumbnail every clip's first frame; reject black/fade-in opens (shift +2s) and OP/ED cards.

- Subs stay sidecar at episode stage (mp4s keep clean); burn-in happens once at season assembly (single re-encode). Long beats split at sentence boundaries.

### Step 5 — Season assembly (optional sew step)
Episode level owns everything (clips, VO, subs); season level only assembles.
```
python3 scripts/season.py work/season_manifest.json season_S01.mp4
```
- `season.py` manifest: list of `{video, srt, title, title_vo}` per episode in order. Per episode: generated title card (VO line via same TTS voice, card padded to match) + recap with subs burned in. Output: season mp4 + merged season `.srt` (offsets automatic) + `loudnorm` audio across episodes.
- Concat uses the concat *filter* with normalized timebases (cards 30fps vs episodes 23.976fps) — never the concat demuxer with `-c copy`, which stretches video past audio.

## Quality gates (all must pass)

- [ ] Coverage: map exists, every cue assigned, unassigned = 0
- [ ] Sourcing: every beat traceable to a fandom beat + cue quotes; 0-hit content absent from VO
- [ ] Lock: VO, subs, and video all agree per beat — each clip shows its VO line; no mismatched illustration
- [ ] Chronology: story order; cold opens dropped unless hook style requested
- [ ] Language: fluent complete sentences; no fragments
- [ ] Audio: VO-only, 1 audio track
- [ ] Sync: |video − VO| < 0.3s; each clip ~2s (allow up to 2.6s; dense text overlays ≤4s)
- [ ] Budget: every beat's VO within ±35% of `weight × 4s` (TTS floor ≈ 5s/sentence); total ≈ `sum(weights) × 4s`

## Tools

Allowed: `ffmpeg`, `ffprobe`, `python3` stdlib, `uvx edge-tts`. No pip installs, no Whisper when subs exist, no API keys for v0.
