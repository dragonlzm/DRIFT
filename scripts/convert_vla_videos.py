#!/usr/bin/env python3
"""Convert VLA rollout MP4s into browser-friendly HTML video assets."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


DEFAULT_SOURCE = Path(
    "/Users/zhuomingliu/Desktop/paper/OUR/2026_NEURIPS/figures/"
    "supplementary/supplementary_material"
)
DEFAULT_OUTPUT = Path("assets/videos/vla")


def run(command: list[str]) -> None:
    print(" ".join(command), flush=True)
    subprocess.run(command, check=True)


def has_audio(source: Path) -> bool:
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            str(source),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return bool(probe.stdout.strip())


def convert_video(source: Path, output_dir: Path, overwrite: bool) -> Path:
    output = output_dir / source.name
    command = [
        "ffmpeg",
        "-hide_banner",
        "-y" if overwrite else "-n",
        "-i",
        str(source),
        "-map",
        "0:v:0",
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-vf",
        "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-movflags",
        "+faststart",
    ]
    if has_audio(source):
        command.extend(["-map", "0:a?", "-c:a", "aac", "-b:a", "128k"])
    else:
        command.append("-an")
    command.append(str(output))
    run(command)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Transcode VLA MP4 videos to H.264/AAC MP4 files that play reliably "
            "in HTML5 video elements."
        )
    )
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    videos = sorted(args.source_dir.glob("*.mp4"))
    if not videos:
        raise SystemExit(f"No .mp4 files found in {args.source_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    converted = [convert_video(video, args.output_dir, args.overwrite) for video in videos]

    print("\nConverted videos:")
    for path in converted:
        print(f"  {path}")


if __name__ == "__main__":
    main()
