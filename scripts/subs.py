#!/usr/bin/env python3
"""VO subtitles from beats (no transcription needed). Usage:
  python3 scripts/subs.py beats.json vo_durations.json work/
Writes work/voiceover.srt + work/voiceover.ass (brainrot style:
bold white, black outline, bottom-center). One entry per beat;
beats over 10s split at sentence boundaries, time shared by characters.
Stdlib only.
"""
import json
import re
import sys
from pathlib import Path


def split_sentences(text):
    parts = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    return parts or [text.strip()]


def fmt_srt(t):
    ms = int(round(t * 1000))
    h, r = divmod(ms, 3600000)
    m, r = divmod(r, 60000)
    s, ms = divmod(r, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def fmt_ass(t):
    ms = int(round(t * 1000))
    h, r = divmod(ms, 3600000)
    m, r = divmod(r, 60000)
    s, ms = divmod(r, 1000)
    return f"{h}:{m:02d}:{s:02d}.{ms // 10:02d}"


ASS_HEAD = """[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Recap,DejaVu Sans,64,&H00FFFFFF,&H000019FF,&H80000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,40,40,60,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def main():
    beats = json.loads(Path(sys.argv[1]).read_text())["beats"]
    durations = json.loads(Path(sys.argv[2]).read_text())
    work = Path(sys.argv[3])
    work.mkdir(parents=True, exist_ok=True)
    entries = []  # (start, end, text)
    t = 0.0
    for b, dur in zip(beats, durations):
        sents = split_sentences(b["vo_text"])
        if dur > 10.0 and len(sents) > 1:
            total_chars = sum(len(s) for s in sents)
            for s in sents:
                share = dur * len(s) / total_chars
                entries.append((t, t + share, s))
                t += share
        else:
            entries.append((t, t + dur, " ".join(sents)))
            t += dur
    srt = "".join(
        f"{i}\n{fmt_srt(s)} --> {fmt_srt(e)}\n{txt}\n\n"
        for i, (s, e, txt) in enumerate(entries, 1)
    )
    (work / "voiceover.srt").write_text(srt)
    ass = ASS_HEAD + "".join(
        f"Dialogue: 0,{fmt_ass(s)},{fmt_ass(e)},Recap,,0,0,0,,{txt}\n"
        for s, e, txt in entries
    )
    (work / "voiceover.ass").write_text(ass)
    print(f"{len(entries)} entries, {t:.1f}s -> voiceover.srt + voiceover.ass")


if __name__ == "__main__":
    main()
