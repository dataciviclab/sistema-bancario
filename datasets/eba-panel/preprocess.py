#!/usr/bin/env python3
"""Download EBA panel dataset from author's GitHub repo.

Output: raw_input.parquet nella directory raw del toolkit.
GitHub non blocca i download come Zenodo.
"""

import subprocess
import sys
from pathlib import Path

URL = "https://github.com/ericc001/european-bank-regulatory-data/raw/main/dataset.parquet"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MIN_SIZE = 50_000_000  # 50 MB minimum


def main(output_path: str) -> None:
    print("Downloading EBA panel from GitHub...")
    result = subprocess.run(
        [
            "curl", "-sL",
            "-H", f"User-Agent: {UA}",
            "--retry", "3",
            "--retry-delay", "5",
            "--connect-timeout", "30",
            "--max-time", "600",
            "-o", output_path,
            URL,
        ],
        capture_output=True, text=True, timeout=900,
    )
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
