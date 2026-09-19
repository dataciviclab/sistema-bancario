"""Benchmarks e soglie per interpretare i dati bancari.

Ogni KPI ha:
- soglie: (ottimo, buono, accettabile, preoccupante)
- verso: "higher_is_better" o "lower_is_better"
- spiegazione: cosa misura in parole semplici
"""

KPI_CONTEXT = {
    "roe_pct": {
        "label": "Redditività sul capitale (ROE)",
        "spiegazione": "Quanto guadagna la banca sul capitale investito. Più è alto, meglio è.",
        "verso": "higher_is_better",
        "soglie": {"ottimo": 10, "buono": 6, "accettabile": 3, "preoccupante": 0},
        "unita": "%",
        "fonte": "CBD2 (BCE)",
    },
    "roa_pct": {
        "label": "Redditività sugli attivi (ROA)",
        "spiegazione": "Quanto guadagna la banca su ogni euro di attivi. Misura l'efficienza nell'uso delle risorse.",
        "verso": "higher_is_better",
        "soglie": {"ottimo": 0.8, "buono": 0.5, "accettabile": 0.2, "preoccupante": 0},
        "unita": "%",
        "fonte": "CBD2 (BCE)",
    },
    "cet1_pct": {
        "label": "Capitale di base (CET1)",
        "spiegazione": "Quanto capitale di alta qualità ha la banca a copertura dei rischi. Il minimo regolamentare è 4.5% + buffer.",
        "verso": "higher_is_better",
        "soglie": {"ottimo": 20, "buono": 15, "accettabile": 10, "preoccupante": 6},
        "unita": "%",
        "fonte": "CBD2 (BCE)",
    },
    "npl_ratio_pct": {
        "label": "Crediti in sofferenza (NPL)",
        "spiegazione": "Percentuale di prestiti che le banche non si aspettano di rientrare. Più è basso, meglio è.",
        "verso": "lower_is_better",
        "soglie": {"ottimo": 2, "buono": 4, "accettabile": 8, "preoccupante": 15},
        "unita": "%",
        "fonte": "CBD2 (BCE)",
    },
    "costo_reddito_pct": {
        "label": "Rapporto costo/ricavi (C/I)",
        "spiegazione": "Quanto costa ogni euro di ricavi. Più è basso, più la banca è efficiente.",
        "verso": "lower_is_better",
        "soglie": {"ottimo": 40, "buono": 55, "accettabile": 70, "preoccupante": 85},
        "unita": "%",
        "fonte": "CBD2 (BCE)",
    },
    "lcr_pct": {
        "label": "Copertura liquidità (LCR)",
        "spiegazione": "Quanta liquidità di alta qualità ha la banca per resistere a 30 giorni di stress. Il minimo è 100%.",
        "verso": "higher_is_better",
        "soglie": {"ottimo": 200, "buono": 150, "accettabile": 100, "preoccupante": 80},
        "unita": "%",
        "fonte": "CBD2 (BCE)",
    },
    "tasso_mutuo_pct": {
        "label": "Tasso mutuo first-home",
        "spiegazione": "Costo medio del mutuo per acquisto prima casa. Non ha un valore 'bene/male' — dipende dal contesto.",
        "verso": "neutral",
        "soglie": {},
        "unita": "%",
        "fonte": "MIR (BCE)",
    },
    "tasso_depositi_scadenza_pct": {
        "label": "Tasso depositi a scadenza",
        "spiegazione": "Rendimento dei depositi vincolati. Più è alto, meglio per i risparmiatori.",
        "verso": "higher_is_better",
        "soglie": {"ottimo": 4, "buono": 2.5, "accettabile": 1, "preoccupante": 0},
        "unita": "%",
        "fonte": "MIR (BCE)",
    },
    "spread_mutuo_deposito_pp": {
        "label": "Spread mutuo/deposito",
        "spiegazione": "Differenza tra tasso mutuo e tasso deposito. Misura il margine della banca sul credito ipotecario.",
        "verso": "neutral",
        "soglie": {},
        "unita": "pp",
        "fonte": "MIR (BCE)",
    },
    "prestiti_mld": {
        "label": "Prestiti bancari",
        "spiegazione": "Totale prestiti erogati dalle banche. Indica la dimensione del mercato creditizio.",
        "verso": "neutral",
        "soglie": {},
        "unita": "mld EUR",
        "fonte": "BSI (BCE)",
    },
    "deposits_mld": {
        "label": "Depositi bancari",
        "spiegazione": "Totale depositi raccolti dalle banche. Indica la base di risorse a disposizione.",
        "verso": "neutral",
        "soglie": {},
        "unita": "mld EUR",
        "fonte": "BSI (BCE)",
    },
    "rapporto_prestiti_deposits_pct": {
        "label": "Rapporto prestiti/depositi",
        "spiegazione": "Quanto dei depositi viene prestato. Se è basso, la banca ha margine per crescere.",
        "verso": "neutral",
        "soglie": {},
        "unita": "%",
        "fonte": "BSI (BCE)",
    },
    "cs_imprese": {
        "label": "Condizioni credito imprese",
        "spiegazione": "Indice di diffusione: positivo = le banche stringono i criteri, negativo = le allentano.",
        "verso": "lower_is_better",
        "soglie": {"ottimo": -10, "buono": -3, "accettabile": 0, "preoccupante": 10},
        "unita": "indice",
        "fonte": "BLS (BCE)",
    },
    "domanda_credito_imprese": {
        "label": "Domanda di credito imprese",
        "spiegazione": "Indice di diffusione: positivo = cresce la domanda, negativo = cala. Indicatore anticipatore.",
        "verso": "higher_is_better",
        "soglie": {"ottimo": 10, "buono": 3, "accettabile": -3, "preoccupante": -10},
        "unita": "indice",
        "fonte": "BLS (BCE)",
    },
    "npl_ratio_pct_wb": {
        "label": "NPL ratio (World Bank)",
        "spiegazione": "Stessa metrica dei NPL CBD2 ma con serie storica più lunga (dal 1990).",
        "verso": "lower_is_better",
        "soglie": {"ottimo": 2, "buono": 4, "accettabile": 8, "preoccupante": 15},
        "unita": "%",
        "fonte": "World Bank WDI",
    },
}


def get_kpi_label(kpi: str) -> str:
    """Restituisce il nome leggibile del KPI."""
    return KPI_CONTEXT.get(kpi, {}).get("label", kpi)


def get_kpi_status(kpi: str, value: float) -> str:
    """Restituisce lo stato del KPI: 'ottimo', 'buono', 'accettabile', 'preoccupante', 'neutro'."""
    ctx = KPI_CONTEXT.get(kpi, {})
    verso = ctx.get("verso", "neutral")
    soglie = ctx.get("soglie", {})

    if verso == "neutral" or not soglie:
        return "neutro"

    if verso == "higher_is_better":
        if value >= soglie.get("ottimo", 999):
            return "ottimo"
        elif value >= soglie.get("buono", 999):
            return "buono"
        elif value >= soglie.get("accettabile", 999):
            return "accettabile"
        else:
            return "preoccupante"
    else:  # lower_is_better
        if value <= soglie.get("ottimo", -999):
            return "ottimo"
        elif value <= soglie.get("buono", -999):
            return "buono"
        elif value <= soglie.get("accettabile", -999):
            return "accettabile"
        else:
            return "preoccupante"


def get_status_color(status: str) -> str:
    """Restituisce il colore per lo stato."""
    return {
        "ottimo": "#22c55e",
        "buono": "#84cc16",
        "accettabile": "#f59e0b",
        "preoccupante": "#e74c3c",
        "neutro": "#94a3b8",
    }.get(status, "#94a3b8")


def get_status_emoji(status: str) -> str:
    """Restituisce l'emoji per lo stato."""
    return {
        "ottimo": "🟢",
        "buono": "🟡",
        "accettabile": "🟠",
        "preoccupante": "🔴",
        "neutro": "⚪",
    }.get(status, "⚪")
