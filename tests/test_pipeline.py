"""Pipeline smoke tests — verifica che i mart esistano e abbiano dati."""

import pathlib
import json
import pytest

MART_DIR = pathlib.Path(__file__).parent.parent / "out" / "data" / "mart"
REGISTRY_PATH = pathlib.Path(__file__).parent.parent / "registry" / "registry.json"


def _load_registry():
    """Carica il registry e restituisce la mappa slug -> anno più recente."""
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        data = json.load(f)
    year_map = {}
    for ds in data.get("datasets", []):
        slug = ds.get("slug")
        period = ds.get("period", {})
        end = period.get("end")
        if slug and end:
            year_map[slug] = int(end)
    return year_map


YEAR_MAP = _load_registry()

EXPECTED_MARTS = [
    ("ecb_cbd2", "mart_bank_kpi.parquet"),
    ("ecb_cbd2", "mart_bank_snapshot.parquet"),
    ("ecb_bsi", "mart_bsi_balance.parquet"),
    ("ecb_bsi", "mart_bsi_deposits.parquet"),
    ("ecb_bsi", "mart_bsi_snapshot.parquet"),
    ("ecb_mir", "mart_mir_rates.parquet"),
    ("ecb_mir", "mart_mir_snapshot.parquet"),
    ("wb_financial", "mart_wd_indicators.parquet"),
    ("wb_financial", "mart_wd_snapshot.parquet"),
    ("ecb_bls", "mart_bls_credit.parquet"),
    ("ecb_bls", "mart_bls_snapshot.parquet"),
    ("eba_panel", "mart_banche_kpi.parquet"),
    ("eba_panel", "mart_banche_snapshot.parquet"),
    ("banche_unified", "mart_panorama.parquet"),
]


@pytest.mark.contract
@pytest.mark.parametrize("slug,table", EXPECTED_MARTS)
def test_mart_exists(slug, table):
    """Ogni mart deve esistere nella directory out/data/mart/{slug}/{year}/."""
    year = YEAR_MAP.get(slug, 2026)
    mart_file = MART_DIR / slug / str(year) / table
    assert mart_file.exists(), f"Mart mancante: {mart_file}"


@pytest.mark.contract
@pytest.mark.parametrize("slug,table", EXPECTED_MARTS)
def test_mart_non_empty(slug, table):
    """Ogni mart deve avere almeno 1 riga."""
    year = YEAR_MAP.get(slug, 2026)
    mart_file = MART_DIR / slug / str(year) / table
    if not mart_file.exists():
        pytest.skip(f"Mart non trovato: {mart_file}")
    import duckdb
    con = duckdb.connect()
    count = con.execute(
        f"SELECT COUNT(*) FROM read_parquet('{mart_file}')"
    ).fetchone()[0]
    assert count > 0, f"Mart vuoto: {mart_file}"
    print(f"  {slug}/{table}: {count} righe")
