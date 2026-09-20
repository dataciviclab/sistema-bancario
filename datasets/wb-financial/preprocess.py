#!/usr/bin/env python3
"""Download World Bank WDI data (bulk CSV).

Output: raw_input.csv nella directory raw del toolkit.
Usa il bulk download WDI_CSV.zip — più affidabile del topic API.
"""

import subprocess
import sys
import zipfile
from pathlib import Path

URL = "https://databank.worldbank.org/data/download/WDI_CSV.zip"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def main(output_path: str) -> None:
    print("Downloading World Bank WDI (bulk CSV)...")
    zip_path = Path(output_path).parent / "wdi_bulk.zip"

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

    print("Extracting WDICSV.csv from ZIP...")
    with zipfile.ZipFile(zip_path) as z:
        csv_files = [n for n in z.namelist() if n.endswith(".csv") and "WDICSV" in n.upper()]
        if not csv_files:
            print("Error: WDICSV.csv not found in ZIP", file=sys.stderr)
            sys.exit(1)

        with z.open(csv_files[0]) as src:
            content = src.read()
            with open(output_path, "wb") as dst:
                dst.write(content)

    zip_path.unlink(missing_ok=True)
    print(f"Written to {output_path} ({len(content)} bytes)")


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "raw_input.csv"
    main(output)
