"""Italia — Deep dive sul sistema bancario italiano."""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from sources import load_kpi_all, load_bilanci_all, load_deposits_all, load_tassi_all

st.title("🇮🇹 Italia — Sistema Bancario")

EXCLUDE = ["U2", "GB", "U5"]

# --- Load all data ---
df_kpi = load_kpi_all()
df_bsi = load_bilanci_all()
df_dep = load_deposits_all()
df_mir = load_tassi_all()

# Filter Italy and add label
df_kpi_it = df_kpi[df_kpi["paese"] == "IT"].copy() if not df_kpi.empty else pd.DataFrame()
df_bsi_it = df_bsi[df_bsi["paese"] == "IT"].copy() if not df_bsi.empty else pd.DataFrame()
df_dep_it = df_dep[df_dep["paese"] == "IT"].copy() if not df_dep.empty else pd.DataFrame()
df_mir_it = df_mir[df_mir["paese"] == "IT"].copy() if not df_mir.empty else pd.DataFrame()

for df in [df_kpi_it, df_bsi_it, df_dep_it, df_mir_it]:
    if not df.empty and "anno" in df.columns and "trimestre" in df.columns:
        df["periodo_label"] = df["anno"].astype(str) + " " + df["trimestre"]

if df_kpi_it.empty:
    st.warning("Nessun dato Italia disponibile.")
    st.stop()

# --- KPI cards ---
st.subheader("Indicatori Chiave")
c1, c2, c3, c4 = st.columns(4)

latest = df_kpi_it[df_kpi_it["anno"] == df_kpi_it["anno"].max()]
if not latest.empty:
    row = latest.iloc[-1]
    c1.metric("Redditività (ROE)", f"{row.get('roe_pct', 0):.1f}%")
    c2.metric("Capitale (CET1)", f"{row.get('cet1_pct', 0):.1f}%")
    c3.metric("Crediti in sofferenza", f"{row.get('npl_ratio_pct', 0):.1f}%")
    c4.metric("Efficienza (C/I)", f"{row.get('costo_reddito_pct', 0):.0f}%")

# --- Trend ---
st.subheader("Trend 2024–2026")

if len(df_kpi_it) > 1:
    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=("Redditività ROE (%)", "Capitale CET1 (%)",
                                        "Crediti in sofferenza (%)", "Efficienza C/I (%)"),
                        vertical_spacing=0.18, horizontal_spacing=0.08,
                        specs=[[{"type": "scatter"}, {"type": "scatter"}],
                               [{"type": "scatter"}, {"type": "scatter"}]])

    x = df_kpi_it["periodo_label"]
    fig.add_trace(go.Scatter(x=x, y=df_kpi_it["roe_pct"], mode="lines+markers", name="ROE", line=dict(color="#6366f1", width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=x, y=df_kpi_it["cet1_pct"], mode="lines+markers", name="CET1", line=dict(color="#22c55e", width=2)), row=1, col=2)
    fig.add_trace(go.Scatter(x=x, y=df_kpi_it["npl_ratio_pct"], mode="lines+markers", name="NPL", line=dict(color="#e74c3c", width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=x, y=df_kpi_it["costo_reddito_pct"], mode="lines+markers", name="C/I", line=dict(color="#f59e0b", width=2)), row=2, col=2)

    fig.update_layout(height=600, margin={"t": 50, "b": 40}, showlegend=False)
    st.plotly_chart(fig, width="stretch")

# --- Bilanci MFI ---
st.subheader("Bilanci MFI — Prestiti e Depositi")

if not df_bsi_it.empty:
    df_q = df_bsi_it[df_bsi_it["trimestre"].notna()].copy()
    if not df_q.empty:
        fig2 = go.Figure()
        if "prestiti_mld" in df_q.columns:
            fig2.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["prestiti_mld"], name="Prestiti", line=dict(color="#6366f1", width=2), fill="tozeroy", fillcolor="rgba(99,102,241,0.1)"))
        if "deposits_mld" in df_q.columns:
            fig2.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["deposits_mld"], name="Depositi", line=dict(color="#22c55e", width=2), fill="tozeroy", fillcolor="rgba(34,197,94,0.1)"))
        fig2.update_layout(yaxis_title="Miliardi EUR", height=350, margin={"t": 30})
        st.plotly_chart(fig2, width="stretch")

# --- Tassi ---
st.subheader("Tassi di Interesse")

if not df_mir_it.empty:
    df_q = df_mir_it[df_mir_it["trimestre"].notna()].copy()
    if not df_q.empty:
        fig3 = go.Figure()
        if "tasso_mutuo_pct" in df_q.columns:
            fig3.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_mutuo_pct"], name="Mutuo", line=dict(color="#6366f1", width=2)))
        if "tasso_imprese_pct" in df_q.columns:
            fig3.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_imprese_pct"], name="Imprese", line=dict(color="#e74c3c", width=2)))
        if "tasso_depositi_scadenza_pct" in df_q.columns:
            fig3.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_depositi_scadenza_pct"], name="Deposit", line=dict(color="#22c55e", width=2)))
        fig3.update_layout(yaxis_title="Tasso (%)", height=300, margin={"t": 30})
        st.plotly_chart(fig3, width="stretch")
