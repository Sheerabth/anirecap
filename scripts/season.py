#!/usr/bin/env python3
"""Season assembly: title cards + episode recaps + burned subs + leveled audio."""
import json
import subprocess
import sys
from pathlib import Path


def probe_dur(p):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def to_s(x):
    h, m, rest = x.split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def to_x(t):
    ms = int(round(t * 1000))
    h, r = divmod(ms, 3600000)
    m, r = divmod(r, 60000)
    s, ms = divmod(r, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def shift_srt(srt_path, offset):
    out = []
    n = 1
    for block in Path(srt_path).read_text().split("\n\n"):
        lines = block.strip().splitlines()
        if len(lines) >= 3 and "-->" in lines[1]:
            a, b = lines[1].split(" --> ")
            text = "\n".join(lines[2:])
            out.append(f"{n}\n{to_x(to_s(a) + offset)} --> {to_x(to_s(b) + offset)}\n{text}")
            n += 1
    return "\n\n".join(out) + "\n\n"


def main():
    manifest = Path(sys.argv[1])
    out = sys.argv[2]
    voice = "en-US-GuyNeural"
    burn = True
    args = sys.argv[3:]
    for i, a in enumerate(args):
        if a == "--voice":
            voice = args[i + 1]
        if a == "--no-burn":
            burn = False
    eps = json.loads(manifest.read_text())["episodes"]
    tmp = Path(out).parent / "_season_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    segs = []
    merged_srt = ""
    clock = 0.0
    for idx, ep in enumerate(eps):
        ttxt = tmp / f"title_{idx}.txt"
        tmp3 = tmp / f"title_{idx}.mp3"
        ttxt.write_text(ep["title_vo"].strip() + "\n")
        subprocess.run(["uvx", "edge-tts", "--file", str(ttxt),
                        "--write-media", str(tmp3), "--voice", voice], check=True)
        vd = probe_dur(tmp3)
        card_dur = max(3.0, vd + 0.5)
        card = tmp / f"card_{idx}.mp4"
        safe_title = ep["title"].replace("'", "").replace(":", " -")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error", "-f", "lavfi",
            "-i", f"color=c=black:s=1280x720:d={card_dur:.2f}:r=30",
            "-i", str(tmp3), "-map", "0:v", "-map", "1:a",
            "-vf", "drawtext=fontfile=/usr/share/fonts/TTF/DejaVuSans.ttf:"
                   f"text='{safe_title}':fontcolor=white:fontsize=52:"
                   "x=(w-text_w)/2:y=(h-text_h)/2",
            "-af", f"apad=whole_dur={card_dur:.2f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-c:a", "aac", str(card)], check=True)
        segs.append(card)
        clock += card_dur
        segs.append(Path(ep["video"]))
        ep_dur = probe_dur(ep["video"])
        merged_srt += shift_srt(ep["srt"], clock)
        clock += ep_dur
    # concat FILTER (never the concat demuxer): cards are 30fps/1-15360 timebase,
    # episodes 23.976fps/1-24000: the demuxer mixes timebases and stretches video.
    season_srt = Path(out).with_suffix(".srt")
    season_srt.write_text(merged_srt)
    inputs = []
    for s in segs:
        inputs += ["-i", str(Path(s).resolve())]
    n = len(segs)
    pre = "".join(
        f"[{i}:v]fps=30,scale=1280:720,format=yuv420p,settb=AVTB[v{i}];"
        f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}];"
        for i in range(n))
    joint = "".join(f"[v{i}][a{i}]" for i in range(n))
    if burn:
        ass = season_srt.with_suffix(".ass")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(season_srt),
                        str(ass)], check=True)
        fc = (pre + f"{joint}concat=n={n}:v=1:a=1[vcat][acat];"
              f"[vcat]subtitles={ass.resolve()}:fontsdir=/usr/share/fonts/TTF[v];"
              f"[acat]loudnorm[a]")
        vmap, amap = "[v]", "[a]"
    else:
        fc = (pre + f"{joint}concat=n={n}:v=1:a=1[vcat][acat];"
              f"[acat]loudnorm[a]")
        vmap, amap = "[vcat]", "[a]"
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs,
                    "-filter_complex", fc,
                    "-map", vmap, "-map", amap,
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-c:a", "aac", str(out)], check=True)
    print(f"season: {out} ({clock:.0f}s) + {season_srt.name}")


if __name__ == "__main__":
    main()
