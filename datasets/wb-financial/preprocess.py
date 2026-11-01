#!/usr/bin/env python3
"""Download World Bank WDI — solo gli indicatori dichiarati nel dataset.

Il bulk WDI_CSV.zip contiene ~1.400 indicatori e pesa ~190 MB per estrarne 7.
Qui si usa la v2 JSON API per indicatore: ~4 MB di JSON ciascuno, di cui si
tengono solo le osservazioni non nulle.

Output: CSV lungo con colonne
    paese,codice_paese,indicatore,codice_indicatore,anno,valore
"""

from __future__ import annotations

import csv
import json
import sys
import urllib.request
from pathlib import Path

INDICATORS = {
    "FB.AST.NPER.ZS": "Bank nonperforming loans to total gross loans (%)",
    "FS.AST.PRVT.GD.ZS": "Domestic credit to private sector (% of GDP)",
    "FB.CBK.BRCH.P5": "Commercial bank branches (per 100,000 adults)",
    "FB.ATM.TOTL.P5": "Automated teller machines (ATMs) (per 100,000 adults)",
    "FB.BNK.CAPA.ZS": "Bank capital to assets ratio (%)",
    "FR.INR.RINR": "Real interest rate (%)",
    "FR.INR.LNDP": "Interest rate spread (lending rate minus deposit rate, %)",
}

BASE = "https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=20000"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
TIMEOUT = 120


def fetch_indicator(code: str) -> list[dict]:
    records: list[dict] = []
    page = 1
    while True:
        url = BASE.format(code=code)
        if page > 1:
            url += f"&page={page}"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        if not isinstance(payload, list) or len(payload) < 2:
            raise RuntimeError(f"risposta World Bank non valida per {code}: {payload}")
        meta, rows = payload[0], payload[1] or []
        records.extend(rows)
        if page >= int(meta.get("pages", 1)):
            break
        page += 1
    return records


def main(output_path: str) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0

    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            ["paese", "codice_paese", "indicatore", "codice_indicatore", "anno", "valore"]
        )
        for code, fallback_name in INDICATORS.items():
            print(f"fetch {code}")
            try:
                rows = fetch_indicator(code)
            except Exception as exc:  # noqa: BLE001 - fail loud with context
                print(f"ERRORE su {code}: {exc}", file=sys.stderr)
                raise

            for row in rows:
                value = row.get("value")
                year = row.get("date")
                if value is None or year is None:
                    continue
                name = (row.get("indicator") or {}).get("value") or fallback_name
                writer.writerow(
                    [
                        (row.get("country") or {}).get("value", ""),
                        row.get("countryiso3code", ""),
                        name,
                        code,
                        year,
                        value,
                    ]
                )
                written += 1

    print(f"Scritte {written} osservazioni in {out}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "raw_input.csv")
