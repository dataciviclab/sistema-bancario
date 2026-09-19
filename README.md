# Sistema Bancario

Intelligence sul sistema bancario europeo — dati aperti da BCE, World Bank, Banca d'Italia.

## Fonti dati

| Fonte | Dataset | Contenuto |
|---|---|---|
| BCE SDMX | CBD2 | Consolidated Banking Data: profittabilità, NPL, CET1, liquidità per paese |
| BCE SDMX | BSI | Balance Sheet Items: bilanci MFI, aggregati monetari, prestiti, depositi |
| BCE SDMX | MIR | MFI Interest Rates: tassi attivi/passivi su prestiti e depositi |
| BCE SDMX | BLS | Bank Lending Survey: condizioni di credito |
| World Bank | WDI | NPL storico, credito/PIL, filiali, ATM |
| EBA | Panel | Dati per singola banca: CET1, ROE, leverage |

## Setup

```bash
pip install -e ".[pipeline,dashboard]"
```

## Uso

```bash
# Esegui tutti i dataset
make seeds

# Esegui compose
make run-compose

# Esegui tutto
make run-all

# Dashboard
make dashboard

# Test
make test
```

## Struttura

```
datasets/
  ecb-cbd2/        # Consolidated Banking Data (BCE)
  ecb-bsi/         # Balance Sheet Items (BCE)
  ecb-mir/         # MFI Interest Rates (BCE)
  ecb-bls/         # Bank Lending Survey (BCE)
  wb-financial/    # World Bank Financial Sector
  eba-panel/       # EBA bank-level data
compose/
  banche-unified/  # Vista unificata KPI + bilanci + tassi
dashboard/         # Streamlit dashboard
```

## Licenza

MIT
