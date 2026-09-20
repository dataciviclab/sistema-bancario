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

| Dataset | Fonte | Anni | Mart | Descrizione |
|---|---|---|---|---|
| ecb_cbd2 | BCE SDMX | 2015-2025 | 2 | Consolidated Banking Data: profittabilità, NPL, CET1, liquidità |
| ecb_bsi | BCE SDMX | 2020-2025 | 3 | Balance Sheet Items: bilanci MFI, aggregati monetari |
| ecb_mir | BCE SDMX | 2020-2025 | 2 | MFI Interest Rates: tassi attivi/passivi |
| ecb_bls | BCE SDMX | 2007-2025 | 2 | Bank Lending Survey: condizioni di credito |
| wb_financial | World Bank | 1960-2025 | 2 | NPL, credito/PIL, filiali, ATM |
| eba_panel | EBA | 2012-2025 | 2 | Dati per singola banca: CET1, ROE, leverage |

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
make test        # Test
```

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
