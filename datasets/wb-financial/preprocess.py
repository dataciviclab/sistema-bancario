#!/usr/bin/env python3
"""Download World Bank WDI Financial Sector data.

Output: raw_input.csv nella directory raw del toolkit.
"""

import csv
import io
import sys
import zipfile
from pathlib import Path

from lab_connectors.http import HttpClient

URL = "https://api.worldbank.org/v2/en/topic/7?downloadformat=csv"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def main(output_path: str) -> None:
    print(f"Downloading World Bank WDI Financial Sector...")
    client = HttpClient(timeout=120)
    result = client.get(URL, headers={"User-Agent": UA})
    if result.is_error:
        print(f"Error: {result.err}", file=sys.stderr)
        sys.exit(1)

    print(f"Extracting main data file from ZIP ({len(result.response.content)} bytes)...")
    with zipfile.ZipFile(io.BytesIO(result.response.content)) as z:
        data_files = [n for n in z.namelist()
                      if n.endswith(".csv") and not n.startswith("Metadata_")]
        if not data_files:
            print("Error: no data CSV found in ZIP", file=sys.stderr)
            sys.exit(1)

        with z.open(data_files[0]) as src:
            content = src.read()
            with open(output_path, "wb") as dst:
                dst.write(content)

    print(f"Written to {output_path} ({len(content)} bytes)")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "raw_input.csv"
    main(output)
