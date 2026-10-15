#!/usr/bin/env python3
"""Per-beat TTS via free edge-tts. Usage:
  python3 scripts/tts.py beats.json work/ [--voice en-US-GuyNeural]
Writes work/v1.mp3..vN.mp3, work/vo_full.mp3, work/vo_durations.json
Stdlib only + uvx edge-tts + ffmpeg.
"""
import json
import subprocess
import sys
from pathlib import Path


def probe_dur(p):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    beats_p, work = Path(sys.argv[1]), Path(sys.argv[2])
    voice = "en-US-GuyNeural"
    for a in sys.argv[3:]:
        if not a.startswith("-"):
            voice = a
        elif a.startswith("--voice"):
            voice = a.split("=", 1)[1] if "=" in a else sys.argv[sys.argv.index(a) + 1]
    work.mkdir(parents=True, exist_ok=True)
    beats = json.loads(beats_p.read_text())["beats"]
    durations = []
    mp3s = []
    for i, b in enumerate(beats, 1):
        txt = work / f"s{i}.txt"
        mp3 = work / f"v{i}.mp3"
        txt.write_text(b["vo_text"].strip() + "\n")
        subprocess.run(
            ["uvx", "edge-tts", "--file", str(txt),
             "--write-media", str(mp3), "--voice", voice],
            check=True,
        )
        d = probe_dur(mp3)
        durations.append(d)
        mp3s.append(mp3)
        print(f"beat {b.get('id', i)}: {d:.2f}s -> {mp3.name}")
    # concat VO
    lst = work / "alist.txt"
    lst.write_text("".join(f"file '{m.resolve()}'\n" for m in mp3s))
    vo_full = work / "vo_full.mp3"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(lst), "-c", "copy", str(vo_full)],
        check=True,
    )
    (work / "vo_durations.json").write_text(json.dumps(durations, indent=2))
    print(f"total VO: {sum(durations):.2f}s -> {vo_full}")


if __name__ == "__main__":
    main()
