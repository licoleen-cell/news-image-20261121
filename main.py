#!/usr/bin/env python3
"""Entry point: copy the rendered front page into /output/entry.png.

stdlib only (os/shutil/sys) by design; the PNG is rendered ahead of time by
gen_image.py, so this step is a pure, deterministic file copy.
"""
import os
import shutil
import sys

OUT_DIR = "/output"
OUT_NAME = "entry.png"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "image.png")
    if not os.path.isfile(src):
        sys.stderr.write("missing source image: %s\n" % src)
        return 1
    if not os.path.isdir(OUT_DIR):
        os.makedirs(OUT_DIR, exist_ok=True)
    dst = os.path.join(OUT_DIR, OUT_NAME)
    shutil.copyfile(src, dst)
    sys.stdout.write("wrote %s (%d bytes)\n" % (dst, os.path.getsize(dst)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
