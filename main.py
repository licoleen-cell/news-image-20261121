#!/usr/bin/env python3
"""Copy the rendered front page to /output/entry.png.

Standard library only. The output is a byte-for-byte copy of image.png,
so repeated runs are identical.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "image.png")
OUTPUT_DIR = "/output"
TARGET = os.path.join(OUTPUT_DIR, "entry.png")


def main():
    if not os.path.isfile(SOURCE):
        sys.stderr.write("missing %s; run gen_image.py first\n" % SOURCE)
        return 1
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    shutil.copyfile(SOURCE, TARGET)
    sys.stdout.write("wrote %s (%d bytes)\n"
                     % (TARGET, os.path.getsize(TARGET)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
