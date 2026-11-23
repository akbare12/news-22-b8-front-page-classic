#!/usr/bin/env python3
"""Copy program for the news-image-20261122 entry.

Reproduces the classic broadsheet front page (THE WORLD TODAY, Sunday
22 November 2026) drawn by draw.py: copies entry.png to the output
directory, verifying size and sha256 so both runs write identical bytes.
Standard library only, no network.
"""
import hashlib
import os
import shutil
import sys

EXPECTED_SHA256 = "936a9741961498c54a4fd9f44d961803aefc581d8231588279002062fdeea4d1"
EXPECTED_SIZE = 222719


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")

    with open(src, "rb") as f:
        data = f.read()
    # The gate requires a whole PNG: check the magic bytes before hashing.
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        print("not a PNG file", file=sys.stderr)
        return 1
    if len(data) != EXPECTED_SIZE:
        print(f"size mismatch: {len(data)} != {EXPECTED_SIZE}", file=sys.stderr)
        return 1
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        print(f"sha256 mismatch: {digest} != {EXPECTED_SHA256}", file=sys.stderr)
        return 1
    shutil.copyfile(src, dst)
    with open(dst, "rb") as f:
        check = hashlib.sha256(f.read()).hexdigest()
    if check != EXPECTED_SHA256:
        print("copy verification failed", file=sys.stderr)
        return 1
    # Second read-back: confirm the file on disk is byte-identical to source.
    if os.path.getsize(dst) != EXPECTED_SIZE:
        print("output size mismatch after copy", file=sys.stderr)
        return 1
    print(f"wrote {dst} ({len(data)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
