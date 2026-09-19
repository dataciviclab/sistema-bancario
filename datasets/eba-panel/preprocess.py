#!/usr/bin/env python3
"""Download EBA panel dataset from Zenodo.

Output: raw_input.csv nella directory raw del toolkit.
"""

import csv
import io
import subprocess
import sys
from pathlib import Path

URL = "https://zenodo.org/api/records/19109425/files/dataset.parquet/content"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def main(output_path: str) -> None:
    print(f"Downloading EBA panel dataset from Zenodo...")
    result = subprocess.run(
        ["curl", "-sL", "-H", f"User-Agent: {UA}", "-o", output_path, URL],
        capture_output=True, text=True, timeout=600,
    )
    if result.returncode != 0:
        print(f"Error: curl failed with return code {result.returncode}", file=sys.stderr)
        sys.exit(1)

    size = Path(output_path).stat().st_size
    print(f"Written to {output_path} ({size} bytes)")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "raw_input.csv"
    main(output)
