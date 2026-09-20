#!/usr/bin/env python3
"""Download World Bank WDI Financial Sector data.

Output: raw_input.csv nella directory raw del toolkit.
Usa curl per il download — più robusto di requests su CI.
"""

import csv
import subprocess
import sys
import zipfile
from pathlib import Path

URL = "https://api.worldbank.org/v2/en/topic/7?downloadformat=csv"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def main(output_path: str) -> None:
    print("Downloading World Bank WDI Financial Sector...")
    zip_path = Path(output_path).parent / "wb_financial_raw.zip"

    result = subprocess.run(
        [
            "curl", "-sL",
            "-H", f"User-Agent: {UA}",
            "--retry", "3",
            "--retry-delay", "5",
            "--connect-timeout", "30",
            "--max-time", "600",
            "-o", str(zip_path),
            URL,
        ],
        capture_output=True, text=True, timeout=900,
    )
    if result.returncode != 0:
        print(f"Error: curl failed (exit {result.returncode}): {result.stderr}", file=sys.stderr)
        sys.exit(1)

    zip_size = zip_path.stat().st_size
    print(f"Downloaded ZIP ({zip_size} bytes)")

    print("Extracting main data file from ZIP...")
    with zipfile.ZipFile(zip_path) as z:
        data_files = [n for n in z.namelist()
                      if n.endswith(".csv") and not n.startswith("Metadata_")]
        if not data_files:
            print("Error: no data CSV found in ZIP", file=sys.stderr)
            sys.exit(1)

        with z.open(data_files[0]) as src:
            content = src.read()
            with open(output_path, "wb") as dst:
                dst.write(content)

    zip_path.unlink(missing_ok=True)
    print(f"Written to {output_path} ({len(content)} bytes)")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "raw_input.csv"
    main(output)
