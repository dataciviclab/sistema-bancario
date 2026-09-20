#!/usr/bin/env python3
"""Download EBA panel dataset from Zenodo.

Output: raw_input.parquet nella directory raw del toolkit.
Usa curl direttamente — più robusto di requests per file grandi su CI.
Supporta proxy via BLOCKED_SOURCE_PROXY (se configurato).
"""

import os
import subprocess
import sys
from pathlib import Path

URL = "https://zenodo.org/records/19109425/files/dataset.parquet?download=1"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MIN_SIZE = 50_000_000  # 50 MB minimum


def main(output_path: str) -> None:
    print("Downloading EBA panel from Zenodo...")
    proxy = os.environ.get("BLOCKED_SOURCE_PROXY", "")
    if proxy:
        print(f"  con proxy {proxy[:50]}...")

    cmd = [
        "curl", "-sL",
        "-H", f"User-Agent: {UA}",
        "--retry", "3",
        "--retry-delay", "5",
        "--connect-timeout", "30",
        "--max-time", "600",
        "-o", output_path,
    ]
    if proxy:
        cmd.extend(["-x", proxy])
    cmd.append(URL)

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if result.returncode != 0:
        print(f"Error: curl failed (exit {result.returncode}): {result.stderr}", file=sys.stderr)
        sys.exit(1)

    size = Path(output_path).stat().st_size
    if size < MIN_SIZE:
        print(f"Error: file troppo piccolo ({size} bytes, min {MIN_SIZE})", file=sys.stderr)
        sys.exit(1)

    print(f"Written to {output_path} ({size} bytes)")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "raw_input.parquet"
    main(output)
