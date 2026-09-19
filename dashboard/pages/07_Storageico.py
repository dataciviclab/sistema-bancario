"""Tendenze Storiche — World Bank e BLS (leading indicators)."""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from sources import load_wb_indicators, load_bls_credit

st.title("📊 Tendenze Storiche")

EXCLUDE = ["U2", "GB", "U5"]

df_wb = load_wb_indicators()
df_bls = load_bls_credit()

# ============================================================
# WORLD BANK: Indicatori per paese
# ============================================================
st.subheader("NPL Ratio — Confronto Storico")

countries_wb = sorted(df_wb[~df_wb["paese"].isin(EXCLUDE)]["paese"].unique())
sel_wb = st.multiselect("Paesi (World Bank)", countries_wb,
                         default=["Italy", "Germany", "France", "Spain"])

if sel_wb and not df_wb.empty:
    fig = go.Figure()
    for paese in sel_wb:
        d = df_wb[df_wb["paese"] == paese].sort_values("anno")
        if "npl_ratio_pct" in d.columns:
            fig.add_trace(go.Scatter(
                x=d["anno"], y=d["npl_ratio_pct"],
                name=paese, mode="lines+markers", line=dict(width=2),
            ))
    fig.update_layout(yaxis_title="NPL (%)", height=350, margin={"t": 30})
    st.plotly_chart(fig, width="stretch")

# ============================================================
# WORLD BANK: Credito/PIL
# ============================================================
st.subheader("Credito al Settore Privato / PIL")

if sel_wb and not df_wb.empty:
    fig2 = go.Figure()
    for paese in sel_wb:
        d = df_wb[df_wb["paese"] == paese].sort_values("anno")
        if "credito_pil_pct" in d.columns:
            fig2.add_trace(go.Scatter(
                x=d["anno"], y=d["credito_pil_pct"],
                name=paese, mode="lines+markers", line=dict(width=2),
            ))
    fig2.update_layout(yaxis_title="% PIL", height=350, margin={"t": 30})
    st.plotly_chart(fig2, width="stretch")

# ============================================================
# BLS: Credit standards Italia
# ============================================================
st.subheader("Condizioni di Credito — Italia (BLS)")

bls_it = df_bls[df_bls["paese"] == "IT"].copy() if not df_bls.empty else df_bls
if not bls_it.empty:
    bls_it["periodo"] = bls_it["anno"].astype(str) + " " + bls_it["trimestre"]
    bls_it = bls_it.sort_values("periodo")

    fig3 = go.Figure()
    if "cs_imprese" in bls_it.columns:
        fig3.add_trace(go.Scatter(x=bls_it["periodo"], y=bls_it["cs_imprese"],
                                  name="Credit standards imprese", line=dict(color="#6366f1", width=2)))
    if "cs_pmi" in bls_it.columns:
        fig3.add_trace(go.Scatter(x=bls_it["periodo"], y=bls_it["cs_pmi"],
                                  name="Credit standards PMI", line=dict(color="#a78bfa", width=2, dash="dash")))
    if "domanda_credito_imprese" in bls_it.columns:
        fig3.add_trace(go.Scatter(x=bls_it["periodo"], y=bls_it["domanda_credito_imprese"],
                                  name="Domanda credito imprese", line=dict(color="#22c55e", width=2)))
    fig3.add_hline(y=0, line_dash="dash", line_color="gray")
    fig3.update_layout(yaxis_title="Indice diffusione", height=350, margin={"t": 30})
    st.plotly_chart(fig3, width="stretch")

    st.caption("Valori positivi = peggioramento condizioni / maggiore domanda. Negativi = miglioramento / minore domanda.")
