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


def _year_for(slug: str, base: pathlib.Path) -> int:
    """Anno di output del dataset: lo legge dalle directory presenti.

    Non tutti i dataset usano lo stesso anno (eba_panel pubblica il 2025, gli
    SDMX il 2026), quindi l'anno non puo' essere una costante.
    """
    dirs = [d for d in (base / slug).glob("*") if d.is_dir() and d.name.isdigit()]
    if not dirs:
        pytest.skip(f"output non presente in locale per {slug}")
    return max(int(d.name) for d in dirs)


def _mart(slug: str, table: str):
    year = _year_for(slug, MART)
    return _read(MART / slug / str(year) / f"{table}.parquet")


def _clean(slug: str, year: int | None = None):
    year = year or _year_for(slug, CLEAN)
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


# --------------------------------------------------------------------------
# 7. EBA panel — dati per singola banca ed esposizioni per paese
# --------------------------------------------------------------------------


def test_eba_serie_dichiarate_esistono():
    """Ogni metrica del catalogo EBA deve avere osservazioni nel clean."""
    catalogo = _catalog("eba-panel")
    clean = _clean("eba_panel", year=2025)
    presenti = set(clean["metrica"].dropna().unique())
    mancanti = sorted(set(catalogo["metrica"]) - presenti)
    assert not mancanti, f"serie EBA dichiarate ma assenti: {mancanti}"


def test_eba_golden_esposizione_sovrana_intesa():
    """Intesa verso governi centrali italiani: 124,5 mld al 2025H2.

    E' il numero che regge l'analisi "chi finanzia lo Stato": se cambia la
    definizione della serie, deve rompersi qui.
    """
    df = _mart("eba_panel", "mart_esposizioni")
    row = df[(df.banca == "INT") & (df.periodo == 202506) & (df.paese_controparte == "Italy")]
    assert len(row) == 1
    assert row.iloc[0]["esposizione_sovrana_mld"] == pytest.approx(124.5, rel=0.01)


def test_eba_esposizioni_forma():
    df = _mart("eba_panel", "mart_esposizioni")
    assert df["banca"].nunique() >= 140, "banche attese: ~148"
    assert df["paese_controparte"].nunique() >= 80, "paesi controparte attesi: ~95"
    assert df["periodo"].min() <= 201212
    assert df["periodo"].max() >= 202506
    # Nessun paese controparte nullo o vuoto
    assert df["paese_controparte"].notna().all()
    assert (df["paese_controparte"].str.len() > 1).all()


def test_eba_esposizioni_non_negative():
    df = _mart("eba_panel", "mart_esposizioni")
    for col in (
        "esposizione_sovrana_mld", "esposizione_imprese_mld", "esposizione_totale_mld",
        "rwa_totale_mld",
    ):
        assert (df[col].dropna() >= 0).all(), f"{col} ha valori negativi"
    assert df["esposizione_totale_mld"].gt(0).all()
    assert df["quota_sovrana_pct"].dropna().between(0, 100).all()


def test_eba_kpi_in_punti_percentuali():
    """I ratio EBA nel dato di origine sono frazioni (0.1611): il clean li porta
    a punti percentuali. Se qualcuno reintroduce le frazioni, questo test cade."""
    df = _mart("eba_panel", "mart_banche_kpi").dropna(subset=["cet1_pct"])
    # La mediana distingue punti percentuali (15,5) da frazioni (0,155).
    assert 8 < df["cet1_pct"].median() < 25
    # Outlier legittimi esistono (Kommuninvest: RWA quasi nulli -> CET1 ~530%),
    # quindi si guarda il 99esimo percentile, non il massimo.
    assert df["cet1_pct"].quantile(0.99) < 200
    roe = _mart("eba_panel", "mart_banche_kpi")["roe_pct"].dropna()
    assert -5 < roe.median() < 25
    assert roe.quantile(0.99) < 100


def test_eba_anagrafica():
    df = _mart("eba_panel", "mart_banche_anagrafica")
    assert df["banca"].is_unique
    assert len(df) >= 150
    assert df["lei"].notna().mean() >= 0.95
    assert df["paese"].str.len().max() == 2
    # Nessun residuo della colonna spuria del dataset di origine
    assert "country_long_rank" not in df.columns


def test_eba_copertura_kpi():
    df = _mart("eba_panel", "mart_banche_kpi")
    # CET1 e ROE partono dal 2015H2 e mancano nel 2025: copertura attesa ~85%
    assert df["cet1_pct"].notna().mean() >= 0.80
    assert df["attivo_totale_mld"].notna().mean() >= 0.60


def test_eba_join_paesi_controparte():
    """`paese` e' ISO2, `paese_controparte` e' un nome inglese: il mart espone
    `codice_paese_controparte` perche' nessun consumatore debba rifare la mappa."""
    df = _mart("eba_panel", "mart_esposizioni")
    copertura = df["codice_paese_controparte"].notna().mean()
    assert copertura >= 0.95, f"copertura ISO2 {copertura:.1%} < 95%"
    codici = df["codice_paese_controparte"].dropna()
    assert (codici.str.len() == 2).all()
    # Le voci non-paese sono marcate, non silenziose
    aggregati = df[df["controparte_aggregata"]]
    assert aggregati["codice_paese_controparte"].isna().all()
