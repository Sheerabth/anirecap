#!/usr/bin/env python3
"""Extract best ENG subtitle track to .srt. Usage:
  python3 scripts/extract.py <input.mkv> <out.srt> [--lang eng]
Stdlib only + ffmpeg/ffprobe. Prefers subrip/CC ENG, falls back to first ENG sub.
"""
import json
import subprocess
import sys


def probe_subs(src):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=index,codec_name,codec_type:stream_tags=language,title",
         "-of", "json", src],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout).get("streams", [])


def pick_eng_sub(streams, lang="eng"):
    subs = [s for s in streams if s.get("codec_type") == "subtitle"]
    eng = [s for s in subs
           if s.get("tags", {}).get("language", "").lower() == lang.lower()]
    pool = eng or subs
    if not pool:
        raise SystemExit("no subtitle streams found")
    # prefer subrip (easiest timestamps), then anything eng
    for s in pool:
        if s.get("codec_name") == "subrip":
            return s["index"]
    return pool[0]["index"]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    src, out = sys.argv[1], sys.argv[2]
    lang = sys.argv[3].lstrip("-lang=") if len(sys.argv) > 3 else "eng"
    if lang.startswith("-"):
        lang = "eng"
    # allow --lang eng form
    if len(sys.argv) > 4:
        lang = sys.argv[-1]
    idx = pick_eng_sub(probe_subs(src), lang)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", src, "-map", f"0:{idx}", out],
        check=True,
    )
    print(f"extracted stream 0:{idx} -> {out}")


if __name__ == "__main__":
    main()
