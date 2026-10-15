#!/usr/bin/env python3
"""Cue hit-counts for verification tables. Usage:
  python3 scripts/hits.py <ep.srt> keyword [keyword ...]
Prints per-keyword hit count + first 4 matches (timestamp | text).
Case-insensitive. Stdlib only.
"""
import re
import sys


def load(srt_path):
    txt = open(srt_path).read()
    cues = []
    for b in re.split(r"\n\s*\n", txt.strip()):
        lines = b.strip().splitlines()
        if len(lines) >= 3 and "-->" in lines[1]:
            cues.append((lines[1][:12], " ".join(lines[2:])))
    return cues


def main():
    srt_path, keywords = sys.argv[1], sys.argv[2:]
    cues = load(srt_path)
    print(f"cues: {len(cues)}")
    for kw in keywords:
        hits = [(t, x[:75]) for t, x in cues if kw.lower() in x.lower()]
        print(f"---{kw}: {len(hits)}")
        for t, x in hits[:4]:
            print(f"  {t} | {x}")


if __name__ == "__main__":
    main()
