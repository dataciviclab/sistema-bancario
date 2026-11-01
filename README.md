# Sistema Bancario Intelligence

**I bilanci delle banche europee, interrogabili — dati EBA, BCE e World Bank in un'unica dashboard.**

Sistema di intelligence sul sistema bancario europeo: raccoglie dati regolatori EBA, aggregati BCE (bilanci, tassi, condizioni di credito) e indicatori World Bank, li trasforma in mart analitici e li rende interrogabili via dashboard Streamlit.

- **Fonti**: [EBA Transparency Exercise](https://www.eba.europa.eu/risk-and-data-analysis/risk-data/eu-wide-regulatory-reporting) · [ECB SDMX](https://data.ecb.europa.eu/) · [World Bank WDI](https://datacatalog.worldbank.org/search/dataset/0037712)
- **Copertura**: 2007-2025 (a seconda del dataset)
- **Livello**: Paesi EU/EEA — aggregato e per singola banca (EBA)
- **Output pubblico**: Dashboard Streamlit

## Cosa risponde

1. **Come varia la solidità delle banche europee?** → CET1, leverage ratio, ROE per paese e banca (EBA panel)
2. **Come cresce il credito in Europa?** → Bank Lending Survey: standard e domanda per paese (BCE BLS)
3. **Qual è la struttura dei bilanci MFI?** → depositi, prestiti, titoli per paese (BCE BSI)
4. **Come variano i tassi di interesse?** → tassi attivi/passivi su prestiti e depositi (BCE MIR)
5. **Come si confrontano i sistemi bancari?** → NPL, credito/PIL, filiali, ATM (World Bank)
6. **Come sta cambiando il sistema?** → snapshot multi-anno con KPI chiave (compose)

## Dataset

| Dataset | Fonte | Anni (reali) | Mart | Descrizione |
|---|---|---|---|---|
| ecb_cbd2 | BCE SDMX | 2015-2026 | 2 | Consolidated Banking Data: redditività, capitale, NPL per settore, liquidità |
| ecb_bsi | BCE SDMX | 2003-2026 | 3 | Balance Sheet Items: attivo, prestiti, depositi per detentore |
| ecb_mir | BCE SDMX | 2003-2026 | 2 | Tassi attivi/passivi su mutui, imprese, consumo, depositi |
| ecb_bls | BCE SDMX | 2003-2026 | 2 | Bank Lending Survey: condizioni e domanda di credito (indici di diffusione) |
| wb_financial | World Bank | 1960-2025 | 2 | NPL, credito/PIL, filiali, ATM per 100k abitanti |
| eba_panel | EBA | 2012-2025 | 4 | Dati per singola banca: CET1, ROE, leverage, esposizioni per paese controparte e RWA |

### Contratto delle serie

Ogni colonna di un mart corrisponde a **una serie dichiarata** in
`datasets/<dataset>/series_catalog.csv`: nome metrica, serie SDMX, descrizione,
unità e moltiplicatore. Niente medie tra serie diverse.

- Il raw è scaricato con una **key SDMX mirata** (pochi MB invece del dataflow
  intero da 1-2 GB).
- Il clean tiene solo le serie del catalogo e fallisce in modo rumoroso se una
  serie sparisce (è già successo: la voce `A20T` non esiste più).
- I test in `tests/test_mart_contract.py` fissano i valori golden e la copertura
  minima: un numero sbagliato rompe la CI, non arriva in dashboard.

### EBA: banche singole ed esposizioni

Il panel EBA (`eba_panel`) ha 4 mart:

| Mart | Cosa risponde |
|---|---|
| `mart_banche_kpi` | CET1, ROE, leverage, attivo per banca e periodo |
| `mart_banche_snapshot` | ultimo valore per banca, con il periodo di riferimento per colonna |
| `mart_esposizioni` | dove è esposta ogni banca: 6 classi (sovrana, imprese, retail, istituzioni, equity, altro) × 95 paesi controparte × 39 periodi, con i relativi RWA |
| `mart_banche_anagrafica` | nome, paese, LEI, stato SSM, copertura temporale |

Note di lettura:

- `mart_esposizioni` è la base di "chi finanzia lo Stato": al 2025H2 Intesa ha
  124,5 mld di esposizione sovrana italiana, il 77% della sua esposizione verso
  l'Italia.
- `country_long_rank`, presente nel dataset di origine, è una colonna spuria
  (contiene un'altra lista di paesi): viene scartata nel clean.
- il campo `gruppo` non esiste: il panel identifica la banca (LEI), non il
  gruppo di appartenenza. Per i gruppi serve l'albo Banca d'Italia.
- i ratio sono in punti percentuali, gli importi in miliardi di euro.
- CET1 e ROE partono dal 2015H2 e non sono ancora pubblicati per il 2025.

### Compose

| Compose | Contenuto |
|---|---|
| banche_unified | Vista unificata: KPI + bilanci + tassi per banca/paese |

## Dashboard

```bash
cd dashboard && streamlit run app.py
```

Pagine: Panoramica · Italia · Confronti · Tassi · Bilanci · SQL · Storico · Banche Singole

## Setup

```bash
pip install -e ".[pipeline,dashboard]"
```

## Uso

```bash
make run-all     # Tutti i dataset + compose
make seeds       # Solo dataset
make run-compose # Solo compose
make dashboard   # Avvia dashboard
make test        # Test di contratto sui mart
```

> I `clean.sql` leggono il catalogo con path relativo alla root del repo
> (`datasets/ecb-bsi/series_catalog.csv`): esegui i comandi dalla root del repo,
> come fanno `make` e la CI.

## Struttura

```
datasets/
  ecb-cbd2/        Consolidated Banking Data (BCE)
  ecb-bsi/         Balance Sheet Items (BCE)
  ecb-mir/         MFI Interest Rates (BCE)
  ecb-bls/         Bank Lending Survey (BCE)
  wb-financial/    World Bank Financial Sector
  eba-panel/       EBA bank-level data
compose/
  banche-unified/  Vista unificata KPI + bilanci + tassi
dashboard/         Streamlit dashboard
```

## Licenza

MIT
