"""Test di contratto sui mart — proteggono i numeri, non solo l'esistenza dei file.

Il repo prima aveva solo smoke test ("il parquet esiste e ha righe"), quindi
poteva pubblicare 138 mld di prestiti dove ce ne sono 1.706. Questi test
fissano:

1. ogni serie dichiarata in series_catalog.csv esiste davvero nel dato;
2. i valori golden (verificati a mano sui titoli ufficiali BCE) tornano;
3. nessuna colonna mescola unita' diverse;
4. nessun aggregato sopranazionale entra nel campo `paese`;
5. la copertura minima delle metriche chiave e' rispettata.
"""

from __future__ import annotations

import pathlib

import duckdb
import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
MART = REPO / "out" / "data" / "mart"
CLEAN = REPO / "out" / "data" / "clean"
DATASETS = REPO / "datasets"

# Anni di output correnti (allineati a dataset.yml -> years).
YEAR = 2026

pytestmark = pytest.mark.contract


def _read(path: pathlib.Path):
    if not path.exists():
        pytest.skip(f"output non presente in locale: {path}")
    con = duckdb.connect()
    try:
        return con.execute(f"SELECT * FROM read_parquet('{path}')").df()
    finally:
        con.close()


def _mart(slug: str, table: str):
    return _read(MART / slug / str(YEAR) / f"{table}.parquet")


def _clean(slug: str, year: int = YEAR):
    return _read(CLEAN / slug / str(year) / f"{slug}_{year}_clean.parquet")


def _catalog(dataset: str):
    con = duckdb.connect()
    try:
        return con.execute(
            f"SELECT * FROM read_csv('{DATASETS / dataset / 'series_catalog.csv'}', header=true)"
        ).df()
    finally:
        con.close()


# --------------------------------------------------------------------------
# 1. Le serie dichiarate esistono
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "dataset,slug",
    [
        ("ecb-bsi", "ecb_bsi"),
        ("ecb-mir", "ecb_mir"),
        ("ecb-cbd2", "ecb_cbd2"),
    ],
)
def test_serie_dichiarate_esistono(dataset: str, slug: str):
    """Ogni serie del catalogo deve avere almeno un'osservazione nel clean.

    Se la BCE rinomina o ritira una serie (e' successo con A20T), la pipeline
    deve fermarsi qui invece di produrre una colonna vuota o una media.
    """
    catalogo = _catalog(dataset)
    clean = _clean(slug)
    presenti = set(clean["serie_id"].dropna().unique())
    mancanti = sorted(set(catalogo["serie_id"]) - presenti)
    assert not mancanti, f"serie dichiarate ma assenti nel clean: {mancanti}"


# --------------------------------------------------------------------------
# 2. Valori golden — Italia 2024 Q4, verificati sulle serie ufficiali BCE
# --------------------------------------------------------------------------


def test_golden_bsi_italia_2024q4():
    df = _mart("ecb_bsi", "mart_bsi_balance")
    row = df[(df.paese == "IT") & (df.anno == 2024) & (df.trimestre == "T4")]
    assert len(row) == 1
    r = row.iloc[0]
    # T00 B Z5 0000: attivo delle deposit-taking corporations escl. banche centrali
    assert r["attivo_totale_mld"] == pytest.approx(3849.0, rel=0.01)
    # A20 B U2 0000: prestiti a residenti dell'area euro
    assert r["prestiti_mld"] == pytest.approx(2223.8, rel=0.01)
    # A20 A U2 2000: prestiti a famiglie e imprese
    assert r["prestiti_famiglie_imprese_mld"] == pytest.approx(1705.7, rel=0.01)
    # L20 B U2 0000: depositi da residenti dell'area euro
    assert r["depositi_mld"] == pytest.approx(2662.9, rel=0.01)


def test_golden_cbd2_italia_2024q4():
    df = _mart("ecb_cbd2", "mart_bank_kpi")
    row = df[(df.paese == "IT") & (df.anno == 2024) & (df.trimestre == "T4")]
    assert len(row) == 1
    r = row.iloc[0]
    assert r["roe_pct"] == pytest.approx(13.73, abs=0.05)
    assert r["roa_pct"] == pytest.approx(1.18, abs=0.05)
    assert r["cet1_pct"] == pytest.approx(16.11, abs=0.05)
    assert r["npl_ratio_pct"] == pytest.approx(2.67, abs=0.05)
    assert r["prestiti_deposits_pct"] == pytest.approx(81.56, abs=0.1)


def test_golden_mir_italia_2024q4():
    df = _mart("ecb_mir", "mart_mir_rates")
    row = df[(df.paese == "IT") & (df.anno == 2024) & (df.trimestre == "T4")]
    assert len(row) == 1
    r = row.iloc[0]
    # medie dei mesi ott-dic 2024 delle serie dichiarate
    assert r["tasso_mutuo_pct"] == pytest.approx(3.20, abs=0.1)
    assert r["tasso_imprese_pct"] == pytest.approx(4.54, abs=0.1)
    assert r["tasso_depositi_overnight_pct"] == pytest.approx(0.31, abs=0.05)
    assert r["mesi_osservati"] == 3


# --------------------------------------------------------------------------
# 3. Nessuna colonna mescola unita' diverse
# --------------------------------------------------------------------------


@pytest.mark.parametrize("slug", ["ecb_bsi", "ecb_mir", "ecb_cbd2"])
def test_unita_unica_per_metrica(slug: str):
    """Una metrica = una unita'. Mescolare EUR e variazioni % e' l'errore che
    ha prodotto i numeri sbagliati precedenti."""
    clean = _clean(slug)
    per_metrica = clean.groupby("metrica")["unita"].nunique()
    rotte = per_metrica[per_metrica > 1]
    assert rotte.empty, f"metriche con piu' unita': {rotte.to_dict()}"


# --------------------------------------------------------------------------
# 4. Nessun aggregato sopranazionale nel campo paese
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "slug,table",
    [
        ("ecb_bsi", "mart_bsi_balance"),
        ("ecb_bsi", "mart_bsi_deposits"),
        ("ecb_mir", "mart_mir_rates"),
        ("ecb_cbd2", "mart_bank_kpi"),
    ],
)
def test_nessun_aggregato_in_paese(slug: str, table: str):
    df = _mart(slug, table)
    sporchi = set(df["paese"].unique()) & {"B0", "U2", "U5", "4F", "W0"}
    assert not sporchi, f"aggregati BCE nel campo paese: {sorted(sporchi)}"
    assert df["paese"].str.len().max() == 2


# --------------------------------------------------------------------------
# 5. Copertura minima
# --------------------------------------------------------------------------


def test_copertura_cbd2():
    df = _mart("ecb_cbd2", "mart_bank_kpi")
    for col in ("roe_pct", "cet1_pct", "npl_ratio_pct", "copertura_npl_pct"):
        copertura = df[col].notna().mean()
        assert copertura >= 0.95, f"{col}: copertura {copertura:.1%} < 95%"


def test_copertura_bsi():
    df = _mart("ecb_bsi", "mart_bsi_balance")
    for col in ("attivo_totale_mld", "prestiti_mld", "depositi_mld"):
        assert df[col].notna().all(), f"{col} contiene NULL"


# --------------------------------------------------------------------------
# 6. Coerenza contabile
# --------------------------------------------------------------------------


def test_bsi_coerenza_bilancio():
    df = _mart("ecb_bsi", "mart_bsi_balance")
    # I prestiti non possono superare l'attivo, i depositi non possono essere negativi
    assert (df["prestiti_mld"] <= df["attivo_totale_mld"] * 1.05).all()
    assert (df["depositi_mld"] > 0).all()
    assert df["prestiti_pct_attivo"].between(0, 100).all()


def test_cbd2_range_plausibili():
    df = _mart("ecb_cbd2", "mart_bank_kpi").dropna(subset=["roe_pct", "cet1_pct"])
    assert df["cet1_pct"].between(0, 60).all()
    assert df["roe_pct"].between(-50, 80).all()
    assert (df["npl_ratio_pct"].dropna() >= 0).all()
    assert (df["costo_reddito_pct"].dropna() >= 0).all()  # segno normalizzato
