#!/usr/bin/env python3
"""Entry point for the news-image-20261120 make.fun bounty.

Copies the pre-rendered front page (entry.png) to /output/entry.png.
No network access. The image itself is produced by build_image.py
(Pillow + DejaVu fonts, all committed in this repo).
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST = "/output/entry.png"


def main():
    os.makedirs(os.path.dirname(DST), exist_ok=True)
    shutil.copyfile(SRC, DST)
    print(f"Copied {SRC} -> {DST} ({os.path.getsize(DST)} bytes)")


if __name__ == "__main__":
    main()
