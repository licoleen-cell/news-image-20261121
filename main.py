#!/usr/bin/env python3
"""Entry for the news-image-20261121 bounty.

Writes the finished front page (image.png, 1024x1024) to /output/entry.png.

Standard library only, no network, no randomness, no clock reads: the same
bytes are written on every run.
"""

import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "image.png"
OUTPUT_DIR = Path("/output")
OUTPUT = OUTPUT_DIR / "entry.png"


def main() -> int:
    if not SOURCE.is_file():
        print(f"missing {SOURCE}", file=sys.stderr)
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # copyfile, not copy2: timestamps must not leak into the result
    shutil.copyfile(SOURCE, OUTPUT)

    size = OUTPUT.stat().st_size
    print(f"wrote {OUTPUT} ({size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
