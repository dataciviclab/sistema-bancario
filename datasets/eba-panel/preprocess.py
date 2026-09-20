#!/usr/bin/env python3
"""Download EBA panel dataset from Zenodo.

Output: raw_input.parquet nella directory raw del toolkit.
Usa lab_connectors.http.download con fallback completo.
"""

import sys
from pathlib import Path

from lab_connectors.http import download

URL = "https://zenodo.org/api/records/19109425/files/dataset.parquet/content"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MIN_SIZE = 50_000_000  # 50 MB minimum


def main(output_path: str) -> None:
    print("Downloading EBA panel from Zenodo...")
    try:
        content = download(URL, timeout=300, user_agent=UA, max_retries=3)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if len(content) < MIN_SIZE:
        print(f"Error: file troppo piccolo ({len(content)} bytes)", file=sys.stderr)
        sys.exit(1)

    Path(output_path).write_bytes(content)
    print(f"Written to {output_path} ({len(content)} bytes)")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "raw_input.parquet"
    main(output)
