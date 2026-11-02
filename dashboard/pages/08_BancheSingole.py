"""Banche Singole — Dati per singola banca (EBA Panel)."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from context import get_kpi_status, get_status_emoji
from sources import (
    load_banche_kpi,
    load_banche_snapshot,
    load_bilancio_composizione,
    load_esposizioni,
)

st.title("🏦 Banche Singole")
st.caption("Dati EBA Transparency Exercise — singole banche EU/EEA (2012–2025)")

EXCLUDE = ["U2", "GB", "U5"]

df_snap = load_banche_snapshot()
df_kpi = load_banche_kpi()
sel_bank = None

if df_snap.empty:
    st.warning("Nessun dato EBA disponibile.")
    st.stop()

# --- Filtro paese ---
countries = sorted(df_snap[~df_snap["paese"].isin(EXCLUDE)]["paese"].unique())
country = st.selectbox("Paese", countries, index=countries.index("IT") if "IT" in countries else 0)

df_country = df_snap[df_snap["paese"] == country].copy()

# --- Tabella banche ---
st.subheader(f"Banche {country}")

cols_show = [
    "nome_banca", "periodo_attivo", "periodo_utile", "attivo_totale_mld",
    "utile_netto_ytd_mld", "cet1_pct", "roe_pct", "leverage_pct",
]
cols_avail = [c for c in cols_show if c in df_country.columns]
df_table = df_country[cols_avail].copy()
df_table.columns = [c.replace("_", " ").title() for c in df_table.columns]
st.dataframe(df_table, width="stretch", hide_index=True)
st.caption(
    "Ogni colonna porta il periodo a cui si riferisce: EBA pubblica con 6-12 mesi "
    "di ritardo e alcune variabili (CET1, ROE) non sono ancora disponibili per il 2025. "
    "L'utile e' cumulato dall'inizio dell'anno (YTD): a meta' anno e' un semestre, a dicembre l'esercizio."
)

# --- Trend per banca selezionata ---
if not df_kpi.empty:
    banks = sorted(df_country["banca"].unique())
    sel_bank = st.selectbox("Seleziona banca per il trend", banks)

    df_bank = df_kpi[df_kpi["banca"] == sel_bank].sort_values("periodo").copy()
    if not df_bank.empty:
        df_bank["data"] = df_bank["periodo"].astype(str).apply(
            lambda x: f"{x[:4]}-{x[4:6]}" if len(x) == 6 else x
        )

        fig = go.Figure()
        if "cet1_pct" in df_bank.columns:
            fig.add_trace(go.Scatter(x=df_bank["data"], y=df_bank["cet1_pct"],
                                     name="CET1 (%)", line=dict(color="#22c55e", width=2)))
        if "roe_pct" in df_bank.columns:
            fig.add_trace(go.Scatter(x=df_bank["data"], y=df_bank["roe_pct"],
                                     name="ROE (%)", line=dict(color="#6366f1", width=2)))
        if "leverage_pct" in df_bank.columns:
            fig.add_trace(go.Scatter(x=df_bank["data"], y=df_bank["leverage_pct"],
                                     name="Leverage (%)", line=dict(color="#f59e0b", width=2)))
        fig.update_layout(yaxis_title="%", height=380, margin={"t": 30})
        st.plotly_chart(fig, width="stretch")

        st.caption(
            "Serie dichiarate in datasets/eba-panel/series_catalog.csv. "
            "Il ROE trimestrale e' volatile: confronta periodi omogenei (annuale fino al 2017, trimestrale dal 2018)."
        )

    # --- Esposizioni per paese controparte ---
    st.subheader("Dove è esposta")
    df_esp = load_esposizioni()

    if df_esp.empty:
        st.info("Dati di esposizione non disponibili.")
    else:
        df_b = df_esp[df_esp["banca"] == sel_bank].copy()
        if df_b.empty:
            st.info("Questa banca non ha una scomposizione geografica delle esposizioni nel panel EBA.")
        else:
            ultimo = int(df_b["periodo"].max())
            # "Other Countries", "International organisations" e simili non sono
            # paesi: restano nel mart ma fuori da questo grafico.
            df_l = df_b[
                (df_b["periodo"] == ultimo) & (~df_b["controparte_aggregata"])
            ].sort_values("esposizione_totale_mld", ascending=False).head(12)

            classi = {
                "esposizione_sovrana_mld": "Sovrana",
                "esposizione_imprese_mld": "Imprese",
                "esposizione_retail_mld": "Retail",
                "esposizione_istituzioni_mld": "Istituzioni",
                "esposizione_equity_mld": "Equity",
                "esposizione_altro_mld": "Altro",
            }
            colori = {
                "esposizione_sovrana_mld": "#6366f1",
                "esposizione_imprese_mld": "#f59e0b",
                "esposizione_retail_mld": "#22c55e",
                "esposizione_istituzioni_mld": "#94a3b8",
                "esposizione_equity_mld": "#a78bfa",
                "esposizione_altro_mld": "#e2e8f0",
            }

            fig_e = go.Figure()
            for col, label in classi.items():
                if col in df_l.columns:
                    fig_e.add_trace(go.Bar(
                        y=df_l["paese_controparte"],
                        x=df_l[col].fillna(0),
                        name=label,
                        orientation="h",
                        marker_color=colori[col],
                    ))
            fig_e.update_layout(
                barmode="stack",
                xaxis_title="Esposizione (mld €)",
                height=420,
                margin={"t": 30, "l": 120},
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig_e, width="stretch")

            periodo_label = f"{str(ultimo)[:4]}H{1 if str(ultimo)[4:6] == '06' else 2}"
            st.caption(
                f"Esposizioni al {periodo_label}, somma dei metodi SA e IRB "
                "(classi dichiarate in series_catalog.csv). "
                "La quota sovrana e' il peso dei titoli di Stato sul totale dell'esposizione "
                "verso quel paese."
            )

            df_show = df_l[[
                "paese_controparte", "esposizione_sovrana_mld", "esposizione_totale_mld",
                "quota_sovrana_pct", "rwa_totale_mld", "densita_rwa_pct",
            ]].copy()
            df_show.columns = [
                "Paese controparte", "Sovrana (mld)", "Totale (mld)",
                "Quota sovrana (%)", "RWA (mld)", "Densità RWA (%)",
            ]
            st.dataframe(df_show, width="stretch", hide_index=True)

# ============================================================
# COMPOSIZIONE: da dove viene il rischio
# ============================================================
if sel_bank is not None:
    st.subheader("Da dove viene il rischio")
    df_comp = load_bilancio_composizione()

    if not df_comp.empty:
        df_c = df_comp[df_comp["banca"] == sel_bank].sort_values("periodo")
        if df_c.empty:
            st.info("Composizione non disponibile per questa banca.")
        else:
            ultimo_c = int(df_c["periodo"].max())
            r = df_c[df_c["periodo"] == ultimo_c].iloc[0]
            etichetta = f"{str(ultimo_c)[:4]}H{1 if str(ultimo_c)[4:6] == '06' else 2}"

            c1, c2, c3 = st.columns(3)
            if r.get("quota_rwa_credito_pct") == r.get("quota_rwa_credito_pct"):
                c1.metric(
                    "RWA da credito",
                    f"{r['quota_rwa_credito_pct']:.0f}%",
                    help="Quota del capitale assorbito che viene dal rischio di credito",
                )
            if r.get("quota_fair_value_pct") == r.get("quota_fair_value_pct"):
                c2.metric(
                    "Attivo a fair value",
                    f"{r['quota_fair_value_pct']:.0f}%",
                    help="Quota di attivita' finanziarie valutate a prezzi di mercato",
                )
            if r.get("prestiti_stage2_pct") == r.get("prestiti_stage2_pct"):
                c3.metric(
                    "Prestiti in stage 2",
                    f"{r['prestiti_stage2_pct']:.1f}%",
                    help="Credito con aumento significativo del rischio: il segnale prima delle sofferenze",
                )

            st.caption(
                f"Al {etichetta}. Stage 3 (deteriorati): {r.get('prestiti_stage3_pct', float('nan')):.1f}%, "
                f"copertura {r.get('copertura_stage3_pct', float('nan')):.0f}%. "
                "RWA: credito, mercato, operativo. Fonte EBA (COREP/FINREP)."
            )
