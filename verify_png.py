#!/usr/bin/env python3
"""
Verify entry.png: whole valid PNG, 1024x1024, <= 1,048,576 bytes;
prints sha256 + bytes.
"""

import os
import sys
import hashlib
from PIL import Image

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_SIZE = 1048576

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "entry.png")

    if not os.path.exists(path):
        print(f"ERROR: {path} not found", file=sys.stderr)
        sys.exit(1)

    size = os.path.getsize(path)
    if size > MAX_SIZE:
        print(f"ERROR: size {size} exceeds 1 MiB", file=sys.stderr)
        sys.exit(1)

    with open(path, "rb") as f:
        header = f.read(8)
        f.seek(0)
        data = f.read()

    if header != PNG_MAGIC:
        print(f"ERROR: invalid PNG magic: {header!r}", file=sys.stderr)
        sys.exit(1)

    try:
        img = Image.open(path)
        img.verify()
        width, height = img.size
    except Exception as e:
        print(f"ERROR: invalid image: {e}", file=sys.stderr)
        sys.exit(1)

    if width != 1024 or height != 1024:
        print(f"ERROR: dimensions are {width}x{height}, expected 1024x1024", file=sys.stderr)
        sys.exit(1)

    sha256 = hashlib.sha256(data).hexdigest()
    print(f"sha256: {sha256}")
    print(f"bytes: {size}")

if __name__ == "__main__":
    main()
