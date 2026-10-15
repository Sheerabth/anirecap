#!/usr/bin/env python3
"""Assemble VO-only recap. Usage:
  python3 scripts/assemble.py work/ out.mp4
Muxes work/montage.mp4 (video-only) + work/vo_full.mp3. No anime audio, ever.
"""
import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    work, out = Path(sys.argv[1]), sys.argv[2]
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error",
         "-i", str(work / "montage.mp4"), "-i", str(work / "vo_full.mp3"),
         "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-shortest", out],
        check=True,
    )
    # verify: exactly 1 video + 1 audio
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type",
         "-of", "default=noprint_wrappers=1:nokey=1", out],
        capture_output=True, text=True, check=True,
    )
    kinds = r.stdout.strip().split()
    assert kinds.count("video") == 1 and kinds.count("audio") == 1, kinds
    print(f"OK VO-only: {out} {kinds}")


if __name__ == "__main__":
    main()
