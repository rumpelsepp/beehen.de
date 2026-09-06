#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""Preprocess raw video clips inside Hugo page bundles for web delivery.

Konvention: In jedem Page-Bundle liegt die Rohdatei als `<name>.raw.<ext>`
(z.B. `schwarmfang.raw.mov`). Das Skript erzeugt daneben:

    <name>.mp4          H.264/AAC, faststart, für breite Kompatibilitaet
    <name>.webm         AV1/Opus, optional, kleinere Dateigroesse
    <name>-poster.jpg   Posterframe fuer <video poster="...">

Idempotent: Ueberspringt Dateien, deren Output juenger ist als die Rohdatei.
Gedacht als Pre-Build-Schritt vor `hugo build` (siehe justfile).
"""

from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
from pathlib import Path

RAW_SUFFIX = ".raw"
RAW_EXTENSIONS = {".mov", ".mp4", ".mkv", ".avi", ".m4v"}

log = logging.getLogger("preprocess_video")


def find_raw_videos(root: Path) -> list[Path]:
    return sorted(
        p
        for p in root.rglob(f"*{RAW_SUFFIX}*")
        if p.is_file() and p.suffix.lower() in RAW_EXTENSIONS
    )


def output_stem(raw_path: Path) -> Path:
    # "schwarmfang.raw.mov" -> "schwarmfang"
    name = raw_path.name
    idx = name.rfind(RAW_SUFFIX + ".")
    stem = name[:idx] if idx != -1 else raw_path.stem
    return raw_path.with_name(stem)


def needs_rebuild(raw_path: Path, out_path: Path) -> bool:
    if not out_path.exists():
        return True
    return raw_path.stat().st_mtime > out_path.stat().st_mtime


def run_ffmpeg(args: list[str], out_path: Path) -> None:
    log.info("ffmpeg -> %s", out_path.name)
    result = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", *args, str(out_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed for {out_path}:\n{result.stderr}")


def encode_mp4(raw_path: Path, out_path: Path, crf: int, max_width: int) -> None:
    run_ffmpeg(
        [
            "-i", str(raw_path),
            "-vf", f"scale='min({max_width},iw)':-2",
            "-c:v", "libx264",
            "-crf", str(crf),
            "-preset", "medium",
            "-movflags", "+faststart",
            "-c:a", "aac",
            "-b:a", "128k",
        ],
        out_path,
    )


def encode_webm(raw_path: Path, out_path: Path, crf: int, max_width: int) -> None:
    run_ffmpeg(
        [
            "-i", str(raw_path),
            "-vf", f"scale='min({max_width},iw)':-2",
            "-c:v", "libsvtav1",
            "-crf", str(crf),
            "-b:v", "0",
            "-c:a", "libopus",
            "-b:a", "96k",
        ],
        out_path,
    )


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
    )
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0


def extract_poster(raw_path: Path, out_path: Path) -> None:
    # Seek past a possible fade-in / black intro (~20 % in, clamped to 2–10 s),
    # then let ffmpeg's thumbnail filter pick the most representative frame there.
    duration = probe_duration(raw_path)
    seek = min(max(duration * 0.2, 2.0), 10.0) if duration else 3.0
    run_ffmpeg(
        [
            "-ss", f"{seek:.2f}",
            "-i", str(raw_path),
            "-vf", "thumbnail=n=200,scale=1280:-2",
            "-frames:v", "1",
        ],
        out_path,
    )


def process(
    raw_path: Path, crf: int, webm_crf: int, max_width: int, make_webm: bool
) -> None:
    stem = output_stem(raw_path)
    mp4_out = stem.with_suffix(".mp4")
    poster_out = stem.with_name(stem.name + "-poster.jpg")

    if needs_rebuild(raw_path, mp4_out):
        encode_mp4(raw_path, mp4_out, crf, max_width)
    else:
        log.info("skip (aktuell): %s", mp4_out.name)

    if needs_rebuild(raw_path, poster_out):
        extract_poster(raw_path, poster_out)

    if make_webm:
        webm_out = stem.with_suffix(".webm")
        if needs_rebuild(raw_path, webm_out):
            encode_webm(raw_path, webm_out, webm_crf, max_width)
        else:
            log.info("skip (aktuell): %s", webm_out.name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root", type=Path, help="Wurzelverzeichnis, z.B. content/"
    )
    parser.add_argument("--crf", type=int, default=23, help="x264 CRF (Default: 23)")
    parser.add_argument(
        "--webm-crf", type=int, default=32, help="AV1 CRF fuer WebM (Default: 32)"
    )
    parser.add_argument(
        "--max-width", type=int, default=1280, help="Max. Breite in Pixel"
    )
    parser.add_argument(
        "--webm", action="store_true", help="Zusaetzlich AV1/WebM-Variante erzeugen"
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg nicht gefunden. `sudo dnf install ffmpeg` o.ae.")

    raw_videos = find_raw_videos(args.root)
    if not raw_videos:
        log.info("Keine Rohvideos (*.raw.*) unter %s gefunden.", args.root)
        return

    for raw_path in raw_videos:
        try:
            process(raw_path, args.crf, args.webm_crf, args.max_width, args.webm)
        except RuntimeError as exc:
            log.error(str(exc))
            raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
