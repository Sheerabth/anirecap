#!/usr/bin/env python3
"""Cut video-only clips matched to per-beat VO durations. Usage:
  python3 scripts/cut.py <input.mkv> beats.json vo_durations.json work/
Each beat VO duration is split evenly across its clips (unless clip has explicit "dur").
Output: work/c_<beat>_<k>.mp4 (720p, -an). Stdlib + ffmpeg only.
"""
import json
import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        raise SystemExit(2)
    src = sys.argv[1]
    beats = json.loads(Path(sys.argv[2]).read_text())["beats"]
    durations = json.loads(Path(sys.argv[3]).read_text())
    work = Path(sys.argv[4])
    work.mkdir(parents=True, exist_ok=True)
    vlist = []
    for bi, (b, total) in enumerate(zip(beats, durations), 1):
        clips = b["clips"]
        auto = [c for c in clips if "dur" not in c]
        fixed = sum(c["dur"] for c in clips if "dur" in c)
        each = (total - fixed) / max(len(auto), 1)
        for ki, c in enumerate(clips, 1):
            dur = c.get("dur", each)
            out = work / f"c_{bi}_{ki}.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-v", "error",
                 "-ss", c["start"], "-t", str(dur),
                 "-i", src, "-map", "0:v:0",
                 "-vf", "scale=1280:720",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                 "-an", str(out)],
                check=True,
            )
            vlist.append(out)
            print(f"beat {bi} clip {ki}: {c['start']} +{dur:.2f}s")
    (work / "vlist.txt").write_text("".join(f"file '{p.resolve()}'\n" for p in vlist))
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(work / "vlist.txt"), "-c", "copy", str(work / "montage.mp4")],
        check=True,
    )
    print(f"montage: {work / 'montage.mp4'} ({len(vlist)} cuts)")


if __name__ == "__main__":
    main()
