# Beat picker: input: fandom summary + full .srt + coverage map. Output: beats.json only.

Fandom is canonical. Season context is for your understanding only: never put future-episode knowledge in VO. Skip OP/recaps/EDs/previews entirely. Fluent complete English sentences only.

## Rules
- One row of the coverage map per beat: wiki beat → cue timestamps + quotes with hit counts → KEEP / REPHRASE / DROP.
- 0 hits = not in this episode's footage. Do not describe it. Rephrase to what the cues prove, or drop.
- Flash-forward cold opens: DROP by default.
- Every cue range assigned to a beat or SKIP-with-reason. Unassigned = 0.
- Each beat carries `weight` 1–3 (3 = irreversible plot, 2 = stakes with setup, 1 = bridge; two-yes test: later episode depends on it? thumbnail reason? 2 yes = 3, 1 = 2, 0 = 1).
- Sentences = weight (w3 → 3, w2 → 2, w1 → 1); clips = `round(weight × 4 / 2)`. Each beat: `vo_text` (fluent third-person narration paraphrasing anchor quotes ONLY: never character dialogue) + `weight` + `quote` (≤12 words, real cue text) + `"time"`.
- Beats in STORY-chronological order, not air order.
- Every clip `start` is an exact cue start `HH:MM:SS.mmm`. Silent action → nearest cue, `"approx": true`.
- No fragments. No staccato. Full sentences.

## Output schema (only this, no markdown)
{"beats": [{"id": "b1", "vo_text": "...", "weight": 2, "quote": "...", "time": "present", "clips": [{"start": "00:04:01.783"}]}]}
