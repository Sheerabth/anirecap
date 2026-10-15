#!/usr/bin/env python3
"""Check VO actuals vs weight budget. Usage:
  python3 scripts/budget.py beats.json vo_durations.json
Target = weight * 4s per beat, ±35% tolerance (TTS floor ~5s/sentence). Exits 0 always; prints PASS/ADJUST per beat.
Stdlib only.
"""
import json
import sys


def main():
    beats = json.loads(open(sys.argv[1]).read())["beats"]
    durations = json.loads(open(sys.argv[2]).read())
    total_target = 0.0
    total_actual = 0.0
    ok = True
    for b, actual in zip(beats, durations):
        w = b.get("weight", 2)
        target = w * 4.0
        total_target += target
        total_actual += actual
        lo, hi = target * 0.65, target * 1.35
        flag = "PASS" if lo <= actual <= hi else "ADJUST"
        if flag == "ADJUST":
            ok = False
        print(f"{b.get('id')}: w{w} target {target:.1f}s actual {actual:.1f}s [{flag}]")
    print(f"total target ~{total_target:.1f}s actual {total_actual:.1f}s")
    if not ok:
        print("note: rewrite flagged VO to sentence budget (w3=3, w2=2, w1=1 sentences)")


if __name__ == "__main__":
    main()
