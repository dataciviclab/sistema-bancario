"""Banche Singole — Dati per singola banca (EBA Panel)."""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from sources import load_banche_snapshot, load_banche_kpi
from context import get_kpi_status, get_status_emoji

st.title("🏦 Banche Singole")
st.caption("Dati EBA Transparency Exercise — singole banche EU/EEA (2012–2025)")

EXCLUDE = ["U2", "GB", "U5"]

df_snap = load_banche_snapshot()
df_kpi = load_banche_kpi()

if df_snap.empty:
    st.warning("Nessun dato EBA disponibile.")
    st.stop()

# --- Filtro paese ---
countries = sorted(df_snap[~df_snap["paese"].isin(EXCLUDE)]["paese"].unique())
country = st.selectbox("Paese", countries, index=countries.index("IT") if "IT" in countries else 0)

df_country = df_snap[df_snap["paese"] == country].copy()

# --- Tabella banche ---
st.subheader(f"Banche {country}")

cols_show = ["banca", "nome_banca", "periodo_cet1", "periodo_roe", "cet1_ratio", "roe", "leverage_ratio", "total_assets"]
cols_avail = [c for c in cols_show if c in df_country.columns]

df_table = df_country[cols_avail].copy()
if "cet1_ratio" in df_table.columns:
    df_table["cet1_ratio"] = (df_table["cet1_ratio"] * 100).round(1)
if "roe" in df_table.columns:
    df_table["roe"] = (df_table["roe"] * 100).round(1)
if "leverage_ratio" in df_table.columns:
    df_table["leverage_ratio"] = (df_table["leverage_ratio"] * 100).round(1)
if "total_assets" in df_table.columns:
    df_table["total_assets"] = (df_table["total_assets"] / 1000).round(0)

df_table.columns = [c.replace("_", " ").title() for c in df_table.columns]
st.dataframe(df_table, use_container_width=True, hide_index=True)
st.caption("Periodo = ultimo anno disponibile per quella variabile (dati EBA con 6-12 mesi di ritardo)")

# --- Trend per banca selezionata ---
if not df_kpi.empty:
    banks = sorted(df_country["banca"].unique())
    sel_bank = st.selectbox("Seleziona banca per trend", banks)

    df_bank = df_kpi[(df_kpi["banca"] == sel_bank)].copy()
    if not df_bank.empty:
        df_bank = df_bank.sort_values("periodo")
        # Convert period (e.g. 201809) to readable date
        df_bank["data"] = df_bank["periodo"].astype(str).apply(
            lambda x: f"{x[:4]}-{x[4:6]}" if len(x) == 6 else x
        )

        fig = go.Figure()

        if "cet1_ratio" in df_bank.columns:
            fig.add_trace(go.Scatter(
                x=df_bank["data"], y=df_bank["cet1_ratio"] * 100,
                name="CET1 (%)", line=dict(color="#22c55e", width=2)))

        if "roe" in df_bank.columns:
            fig.add_trace(go.Scatter(
                x=df_bank["data"], y=df_bank["roe"] * 100,
                name="ROE (%)", line=dict(color="#6366f1", width=2)))

        if "leverage_ratio" in df_bank.columns:
            fig.add_trace(go.Scatter(
                x=df_bank["data"], y=df_bank["leverage_ratio"] * 100,
                name="Leverage (%)", line=dict(color="#f59e0b", width=2)))

        fig.update_layout(yaxis_title="%", height=400, margin={"t": 30})
        st.plotly_chart(fig, width="stretch")
