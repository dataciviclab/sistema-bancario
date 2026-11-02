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
    """Intesa verso governi centrali italiani al 2025H2: 133,3 mld (SA+IRB).

    E' il numero che regge l'analisi "chi finanzia lo Stato". La componente
    standardizzata vale 124,5 e l'IRB 8,7: usare solo SA sottostimerebbe.
    """
    df = _mart("eba_panel", "mart_esposizioni")
    row = df[(df.banca == "INT") & (df.periodo == 202506) & (df.paese_controparte == "Italy")]
    assert len(row) == 1
    assert row.iloc[0]["esposizione_sovrana_mld"] == pytest.approx(133.3, rel=0.01)
    # Il totale include tutte le classi, non solo le sei principali
    assert row.iloc[0]["esposizione_totale_mld"] == pytest.approx(420.2, rel=0.01)
    assert row.iloc[0]["quota_sovrana_pct"] == pytest.approx(31.7, abs=0.5)


def test_eba_metodo_sa_irb_coerenti():
    """SA + IRB deve ricostruire l'aggregato: sono approcci alternativi sulle
    stesse posizioni, quindi la somma per metodo non puo' divergere."""
    df = _mart("eba_panel", "mart_esposizioni")
    m = _mart("eba_panel", "mart_esposizioni_metodo")

    chiavi = ["banca", "periodo", "paese_controparte"]
    agg = df.groupby(chiavi, as_index=False).agg(
        esposizione_totale_mld=("esposizione_totale_mld", "sum"),
        esposizione_sovrana_mld=("esposizione_sovrana_mld", "sum"),
    )
    per_metodo = m.groupby(chiavi, as_index=False).agg(
        esposizione_mld=("esposizione_mld", "sum"),
        sovrana=("esposizione_sovrana_mld", "sum"),
    )
    merged = agg.merge(per_metodo, on=chiavi, how="outer").fillna(0)
    assert (merged["esposizione_totale_mld"] - merged["esposizione_mld"]).abs().max() < 1.0
    assert (merged["esposizione_sovrana_mld"] - merged["sovrana"]).abs().max() < 1.0

    # Golden sul dettaglio: Intesa verso l'Italia
    int_it = m[(m.banca == "INT") & (m.periodo == 202506) & (m.paese_controparte == "Italy")]
    sa = int_it[int_it.metodo == "SA"].iloc[0]
    irb = int_it[int_it.metodo == "IRB"].iloc[0]
    assert sa["esposizione_sovrana_mld"] == pytest.approx(124.5, rel=0.01)
    assert irb["esposizione_sovrana_mld"] == pytest.approx(8.7, rel=0.02)


def test_eba_esposizioni_forma():
    df = _mart("eba_panel", "mart_esposizioni")
    assert df["banca"].nunique() >= 140, "banche attese: ~147"
    assert df["paese_controparte"].nunique() >= 85, "paesi controparte attesi: ~89"
    assert df["periodo"].min() <= 201212
    assert df["periodo"].max() >= 202506
    # Nessun paese controparte nullo o vuoto
    assert df["paese_controparte"].notna().all()
    assert (df["paese_controparte"].str.len() > 1).all()


def test_eba_esposizioni_non_negative():
    df = _mart("eba_panel", "mart_esposizioni")
    for col in (
        "esposizione_sovrana_mld", "esposizione_imprese_mld", "esposizione_totale_mld",
        "esposizione_altre_classi_mld", "rwa_totale_mld",
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


def test_mir_volumi_sono_flussi():
    """I volumi sono flussi mensili: nel trimestre si sommano, non si mediano.

    Se qualcuno cambia SUM in AVG, il trimestre diventa un terzo del vero.
    """
    vol = _mart("ecb_mir", "mart_mir_volumi")
    clean = _clean("ecb_mir")

    riga = vol[(vol.paese == "IT") & (vol.anno == 2025) & (vol.trimestre == "T4")]
    assert len(riga) == 1
    assert riga.iloc[0]["volume_mutui_mld"] == pytest.approx(18.9, rel=0.02)
    assert riga.iloc[0]["mesi_mutui"] == 3

    mensile = clean[
        (clean.paese == "IT")
        & (clean.metrica == "volume_mutui")
        & (clean.anno == 2025)
        & (clean.trimestre == "T4")
    ]["valore"].sum()
    assert mensile == pytest.approx(riga.iloc[0]["volume_mutui_mld"], rel=0.01)


def test_mir_volumi_coerenti():
    vol = _mart("ecb_mir", "mart_mir_volumi").dropna(subset=["volume_prestiti_imprese_mld"])
    # Il totale imprese e' la somma delle due classi dimensionali
    somma = vol["volume_prestiti_piccole_mld"].fillna(0) + vol["volume_prestiti_grandi_mld"].fillna(0)
    assert (somma - vol["volume_prestiti_imprese_mld"]).abs().max() < 0.2
    assert (vol["volume_prestiti_imprese_mld"] >= 0).all()
    assert vol["quota_piccole_imprese_pct"].dropna().between(0, 100).all()


def test_eba_conto_economico_ytd():
    """Utile e margine operativo sono cumulati dall'inizio dell'anno (YTD).

    Il test fissa il comportamento: Q1 < Q2 < Q3 < Q4 nello stesso anno. Se
    qualcuno li trattasse come flussi trimestrali (o li sommasse), i valori
    cambierebbero e questo test cadrebbe.
    """
    df = _mart("eba_panel", "mart_banche_kpi")
    intesa = (
        df[(df.banca == "INT") & (df.periodo.between(202403, 202412))]
        .sort_values("periodo")["utile_netto_ytd_mld"]
        .tolist()
    )
    assert len(intesa) == 4
    assert intesa == sorted(intesa), f"YTD non cumulato: {intesa}"
    assert intesa[0] == pytest.approx(2.3, abs=0.15)
    assert intesa[-1] == pytest.approx(8.7, abs=0.15)

    q4 = df[(df.banca == "INT") & (df.periodo == 202412)].iloc[0]
    assert q4["margine_operativo_ytd_mld"] == pytest.approx(26.6, rel=0.02)
    assert q4["cost_of_risk_pct"] == pytest.approx(0.61, abs=0.05)
    assert q4["return_on_rwa_pct"] == pytest.approx(2.93, abs=0.1)


def test_eba_conto_economico_range():
    """Le mediane distinguono punti percentuali da frazioni: un errore di scala
    (x100 di troppo o mancante) sposta la mediana di due ordini di grandezza."""
    df = _mart("eba_panel", "mart_banche_kpi")
    cor = df["cost_of_risk_pct"].dropna()
    rorwa = df["return_on_rwa_pct"].dropna()
    # valori attesi: cost of risk ~0,5%, return on RWA ~2%
    assert 0 < cor.median() < 2
    assert 0.5 < rorwa.median() < 4
    # outlier legittimi esistono (Kommuninvest, Hamburg Commercial Bank):
    # si guardano i percentili estremi, non il minimo assoluto
    assert -10 < cor.quantile(0.01) and cor.quantile(0.99) < 5
    assert -30 < rorwa.quantile(0.01) and rorwa.quantile(0.99) < 40
    utile = df["utile_netto_ytd_mld"].dropna()
    assert utile.notna().mean() > 0.9


def test_eba_bilancio_golden_intesa():
    """Composizione di Intesa al 2024-12, verificata sul dato di origine."""
    df = _mart("eba_panel", "mart_banche_bilancio")
    row = df[(df.banca == "INT") & (df.periodo == 202412)]
    assert len(row) == 1
    r = row.iloc[0]
    assert r["rwa_totale_mld"] == pytest.approx(296.4, rel=0.01)
    assert r["quota_rwa_credito_pct"] == pytest.approx(79.8, abs=0.2)
    assert r["quota_fair_value_pct"] == pytest.approx(19.6, abs=0.2)
    assert r["prestiti_stage2_pct"] == pytest.approx(8.0, abs=0.1)
    assert r["prestiti_stage3_pct"] == pytest.approx(2.11, abs=0.05)
    assert r["copertura_stage3_pct"] == pytest.approx(49.5, abs=0.5)


def test_eba_bilancio_non_supera_l_attivo():
    """L'attivo finanziario non puo' superare l'attivo totale.

    E' il guardrail contro la tentazione di sommare le righe duplicate del
    dataset di origine: con SUM il rapporto sfonda il 100% su quasi tutte le
    banche, con MAX resta sotto.
    """
    bil = _mart("eba_panel", "mart_banche_bilancio")
    kpi = _mart("eba_panel", "mart_banche_kpi")
    merged = bil.merge(kpi[["banca", "periodo", "attivo_totale_mld"]], on=["banca", "periodo"])
    merged = merged.dropna(subset=["attivo_totale_mld", "attivo_finanziario_mld"])
    violazioni = (merged["attivo_finanziario_mld"] > merged["attivo_totale_mld"] * 1.001).sum()
    assert violazioni <= 2, f"{violazioni} banche con attivo finanziario sopra l'attivo totale"


def test_eba_bilancio_range():
    df = _mart("eba_panel", "mart_banche_bilancio")
    fv = df["quota_fair_value_pct"].dropna()
    assert fv.between(0, 100).all()
    for col in ("prestiti_stage2_pct", "prestiti_stage3_pct", "copertura_stage3_pct"):
        serie = df[col].dropna()
        assert serie.between(0, 100).all(), f"{col} fuori range"
    # stage 2 e' tipicamente piu' grande di stage 3: se si invertono, c'e' un errore di mappa
    both = df.dropna(subset=["prestiti_stage2_pct", "prestiti_stage3_pct"])
    assert (both["prestiti_stage2_pct"] >= both["prestiti_stage3_pct"]).mean() > 0.9


def test_eba_duplicati_hanno_struttura_di_totale():
    """Il dataset EBA riporta piu' righe per la stessa banca/periodo/serie.

    Per le attivita' finanziarie la struttura e' verificata: il valore maggiore
    e' il totale (le altre righe sono le sue componenti). E' la ragione per cui
    i mart usano MAX e non SUM: sommare darebbe il doppio.
    """
    clean = _clean("eba_panel")
    for metrica in ("attivo_hft", "attivo_oci"):
        g = (
            clean[clean.metrica == metrica]
            .groupby(["banca", "periodo"])["valore"]
            .agg(["max", "sum", "count"])
        )
        multi = g[g["count"] > 1]
        assert len(multi) > 100, f"{metrica}: attese molte celle con piu' righe"
        # max == somma delle altre righe (tolleranza 1%) su quasi tutte le celle
        resto = multi["sum"] - multi["max"]
        conferma = (resto - multi["max"]).abs() <= multi["max"].abs() * 0.01
        assert conferma.mean() > 0.95, f"{metrica}: struttura totale+componenti non confermata"


def test_eba_serie_senza_ambiguita():
    """Alcune serie sono pulite: una sola riga per banca/periodo.

    Se un giorno comparissero duplicati anche qui, il mart sceglierebbe un
    valore a caso e il test cade.
    """
    clean = _clean("eba_panel")
    for metrica in ("prestiti_stage1", "prestiti_stage2", "prestiti_stage3",
                    "attivo_totale", "attivo_costo_ammortizzato"):
        duplicati = (clean[clean.metrica == metrica].groupby(["banca", "periodo"]).size() > 1).sum()
        assert duplicati == 0, f"{metrica}: {duplicati} celle con piu' righe"


def test_bls_determinanti():
    """Le determinanti della stretta devono esserci e raccontare la stessa storia.

    Italia 2022Q4: stretta di +18,18 sulle imprese, guidata da prospettive
    economiche (+22,73) e settore specifico, non dal capitale (+9,09).
    """
    df = _mart("ecb_bls", "mart_bls_credit")
    row = df[(df.paese == "IT") & (df.anno == 2022) & (df.trimestre == "T4")]
    assert len(row) == 1
    r = row.iloc[0]
    assert r["cs_imprese"] == pytest.approx(18.18, abs=0.1)
    assert r["det_attivita_economica"] == pytest.approx(22.73, abs=0.1)
    assert r["det_posizione_capitale"] == pytest.approx(9.09, abs=0.1)

    # copertura: la determinante "attivita' economica" c'e' sempre;
    # "tolleranza al rischio" e' una domanda introdotta piu' tardi (~2018)
    assert df["det_attivita_economica"].notna().mean() > 0.95
    assert 0.4 < df["det_tolleranza_rischio"].notna().mean() < 0.7


def test_bsi_crediti_settore_fine_periodo():
    """I prestiti sono stock: il trimestre vale l'ULTIMO mese, non media ne' somma.

    Italia 2025Q4: famiglie 684,9 mld, imprese 620,2 mld (dati di dicembre).
    """
    df = _mart("ecb_bsi", "mart_bsi_crediti")
    row = df[(df.paese == "IT") & (df.anno == 2025) & (df.trimestre == "T4")]
    assert len(row) == 1
    r = row.iloc[0]
    assert r["mese_riferimento"] == "2025-12"
    assert r["prestiti_famiglie_mld"] == pytest.approx(684.9, rel=0.01)
    assert r["prestiti_imprese_mld"] == pytest.approx(620.2, rel=0.01)
    assert r["quota_famiglie_pct"] == pytest.approx(52.5, abs=0.2)

    # Coerenza con il clean: il valore del mart e' quello del mese di riferimento
    clean = _clean("ecb_bsi")
    mensile = clean[
        (clean.paese == "IT")
        & (clean.metrica == "prestiti_famiglie")
        & (clean.periodo == "2025-12")
    ]["valore"].max()
    assert r["prestiti_famiglie_mld"] == pytest.approx(mensile, rel=0.01)

    somma = df["prestiti_famiglie_mld"].fillna(0) + df["prestiti_imprese_mld"].fillna(0)
    assert (somma - df["prestiti_famiglie_imprese_mld"]).abs().max() < 0.2


def test_cbd2_benchmark_separato():
    """Gli aggregati stanno in un mart dedicato, non nel mart per paese.

    Se finissero in `mart_bank_kpi`, ogni media o join li conterebbe come se
    fossero un paese.
    """
    bench = _mart("ecb_cbd2", "mart_benchmark")
    assert set(bench["area"]) == {"U2", "B0"}
    riga = bench[(bench.area == "U2") & (bench.anno == 2024) & (bench.trimestre == "T4")]
    assert len(riga) == 1
    assert riga.iloc[0]["roe_pct"] == pytest.approx(13.7, abs=6)  # area euro, non Italia
    assert riga.iloc[0]["area_nome"] == "Area euro"

    kpi = _mart("ecb_cbd2", "mart_bank_kpi")
    assert not set(kpi["paese"].unique()) & {"U2", "B0"}


def test_cbd2_snapshot_solo_esercizio():
    """ROE/ROA/margine sono cumulati sull'anno: lo snapshot usa solo i T4.

    Prendere un primo trimestre mostrerebbe 3,4% invece del 13,5% dell'anno.
    """
    snap = _mart("ecb_cbd2", "mart_bank_snapshot")
    assert (snap["trimestre"] == "T4").all()
    it = snap[snap.paese == "IT"]
    assert len(it) == 1
    assert it.iloc[0]["anno"] == 2025
    assert it.iloc[0]["roe_pct"] == pytest.approx(13.52, abs=0.05)
