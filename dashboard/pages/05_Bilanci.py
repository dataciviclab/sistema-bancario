"""Bilanci MFI — deep dive."""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from sources import load_bilanci_all, load_deposits_all, load_bsi_snapshot

st.title("🏦 Bilanci MFI")

EXCLUDE = ["U2", "GB", "U5"]

df_bal = load_bilanci_all()
df_dep = load_deposits_all()
df_snap = load_bsi_snapshot()

if df_bal.empty:
    st.warning("Nessun dato disponibile.")
    st.stop()

countries = sorted(df_bal[~df_bal["paese"].isin(EXCLUDE)]["paese"].unique())
country = st.selectbox("Paese", countries, index=countries.index("IT") if "IT" in countries else 0)

df_c = df_bal[df_bal["paese"] == country].copy()
if not df_c.empty and "anno" in df_c.columns and "trimestre" in df_c.columns:
    df_c["periodo_label"] = df_c["anno"].astype(str) + " " + df_c["trimestre"]

df_dep_c = df_dep[df_dep["paese"] == country].copy() if not df_dep.empty else df_dep
if not df_dep_c.empty and "anno" in df_dep_c.columns and "trimestre" in df_dep_c.columns:
    df_dep_c["periodo_label"] = df_dep_c["anno"].astype(str) + " " + df_dep_c["trimestre"]

# --- Trend ---
st.subheader(f"Bilanci MFI — {country}")

if not df_c.empty:
    df_q = df_c[df_c["trimestre"].notna()].copy()
    if not df_q.empty:
        fig = make_subplots(rows=2, cols=1, subplot_titles=("Prestiti e Depositi", "Composizione Bilancio"), vertical_spacing=0.15)

        if "prestiti_mld" in df_q.columns:
            fig.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["prestiti_mld"], name="Prestiti", line=dict(color="#6366f1", width=2)), row=1, col=1)
        if "deposits_mld" in df_q.columns:
            fig.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["deposits_mld"], name="Depositi", line=dict(color="#22c55e", width=2)), row=1, col=1)

        if "attivo_totale_mld" in df_q.columns:
            fig.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["attivo_totale_mld"], name="Attivo", line=dict(color="#94a3b8", width=1, dash="dot")), row=2, col=1)
        if "obbligazioni_mld" in df_q.columns:
            fig.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["obbligazioni_mld"], name="Obbligazioni", line=dict(color="#f59e0b", width=2)), row=2, col=1)
        if "capitale_mld" in df_q.columns:
            fig.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["capitale_mld"], name="Capitale", line=dict(color="#e74c3c", width=2)), row=2, col=1)

        fig.update_layout(height=550, margin={"t": 40})
        fig.update_yaxes(title_text="Miliardi EUR")
        st.plotly_chart(fig, width="stretch")

# --- Ratio ---
st.subheader("Rapporti Finanziari")

if not df_c.empty:
    df_q = df_c[df_c["trimestre"].notna()].copy()
    if not df_q.empty:
        fig2 = make_subplots(rows=1, cols=2, subplot_titles=("Prestiti/Depositi (%)", "Prestiti/Attivo (%)"))
        if "rapporto_prestiti_deposits_pct" in df_q.columns:
            fig2.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["rapporto_prestiti_deposits_pct"], name="P/D", line=dict(color="#6366f1", width=2)), row=1, col=1)
        if "prestiti_pct_attivo" in df_q.columns:
            fig2.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["prestiti_pct_attivo"], name="P/A", line=dict(color="#22c55e", width=2)), row=1, col=2)
        fig2.update_layout(height=300, margin={"t": 40})
        st.plotly_chart(fig2, width="stretch")

# --- Depositi ---
st.subheader("Composizione Depositi")

if not df_dep_c.empty:
    df_q = df_dep_c[df_dep_c["trimestre"].notna()].copy()
    if not df_q.empty and "pct_overnight" in df_q.columns:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["pct_overnight"], name="Conti correnti", line=dict(color="#6366f1", width=2)))
        if "pct_scadenza" in df_q.columns:
            fig3.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["pct_scadenza"], name="A scadenza", line=dict(color="#22c55e", width=2)))
        if "pct_preavviso" in df_q.columns:
            fig3.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["pct_preavviso"], name="Preavviso", line=dict(color="#f59e0b", width=2)))
        fig3.update_layout(yaxis_title="%", height=300, margin={"t": 30})
        st.plotly_chart(fig3, width="stretch")

# --- Confronto ---
st.subheader("Confronto Prestiti/Depositi (latest)")

if not df_snap.empty:
    df_f = df_snap[~df_snap["paese"].isin(EXCLUDE) & df_snap["rapporto_prestiti_deposits_pct"].notna()].sort_values("rapporto_prestiti_deposits_pct")
    if not df_f.empty:
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=df_f["rapporto_prestiti_deposits_pct"], y=df_f["paese"], orientation="h", marker_color=["#6366f1" if c == country else "#94a3b8" for c in df_f["paese"]]))
        fig4.update_layout(xaxis_title="Prestiti/Depositi (%)", height=400, margin={"t": 30, "l": 60})
        st.plotly_chart(fig4, width="stretch")
