#!/usr/bin/env python3
"""
Deploy entry.png to $MAKEFUN_OUTPUT_DIR (default /output).
Standard library only; deploys via a staged temp file in the output dir,
chmod 0644 BEFORE an atomic rename; verifies PNG magic + size <= 1 MiB
before and after; non-zero exit + clear message on failure.
"""

import os
import sys
import tempfile
import shutil

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_SIZE = 1048576  # 1 MiB

def verify_png_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    size = os.path.getsize(path)
    if size > MAX_SIZE:
        raise ValueError(f"File size {size} bytes exceeds 1 MiB ({MAX_SIZE} bytes)")
    with open(path, "rb") as f:
        header = f.read(8)
    if header != PNG_MAGIC:
        raise ValueError(f"Invalid PNG magic bytes: {header!r}")
    return size

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src_png = os.path.join(here, "entry.png")

    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

    try:
        verify_png_file(src_png)

        os.makedirs(output_dir, exist_ok=True)

        fd, tmp_path = tempfile.mkstemp(dir=output_dir, prefix="entry_", suffix=".tmp")
        os.close(fd)

        try:
            shutil.copyfile(src_png, tmp_path)
            verify_png_file(tmp_path)

            # chmod 0644 BEFORE atomic rename
            os.chmod(tmp_path, 0o644)

            dest_path = os.path.join(output_dir, "entry.png")
            os.replace(tmp_path, dest_path)

            verify_png_file(dest_path)
            print(f"Successfully deployed entry.png to {dest_path}")
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise
    except Exception as e:
        print(f"ERROR: deployment failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
