"""Panoramica — Visione d'insieme del sistema bancario europeo."""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from sources import (
    load_snapshot, load_wb_indicators, load_bls_credit,
    load_panorama, get_last_updated,
)
from context import get_kpi_status, get_status_color, get_status_emoji, KPI_CONTEXT

st.title("🏦 Sistema Bancario Europeo")
st.sidebar.caption(f"Aggiornato: {get_last_updated()}")

# --- Glossario sidebar ---
with st.sidebar.expander("📋 Glossario KPI", expanded=False):
    for kpi, ctx in KPI_CONTEXT.items():
        st.markdown(f"**{ctx['label']}**")
        st.caption(ctx['spiegazione'])

EXCLUDE = ["U2", "GB", "U5"]

# --- Load data ---
df_bank = load_snapshot()
df_wb = load_wb_indicators()
df_bls = load_bls_credit()
df_pano = load_panorama()

if df_bank.empty:
    st.warning("Nessun dato disponibile. Esegui `make run` prima.")
    st.stop()

# ============================================================
# KPI ITALIA con status
# ============================================================
st.subheader("Indicatori Chiave — Italia")

df_it = df_bank[df_bank["paese"] == "IT"]
df_ea = df_bank[df_bank["paese"] == "U2"]

kpis = [
    ("roe_pct", "ROE"),
    ("cet1_pct", "CET1"),
    ("npl_ratio_pct", "NPL"),
    ("costo_reddito_pct", "C/I"),
]

cols = st.columns(4)
for i, (kpi, short) in enumerate(kpis):
    val_it = df_it[kpi].values[0] if not df_it.empty and kpi in df_it.columns else None
    val_ea = df_ea[kpi].values[0] if not df_ea.empty and kpi in df_ea.columns else None

    if val_it is not None:
        status = get_kpi_status(kpi, val_it)
        emoji = get_status_emoji(status)
        ctx = KPI_CONTEXT[kpi]
        delta = f"{val_it - val_ea:+.1f} vs U2" if val_ea is not None else None
        cols[i].metric(
            f"{emoji} {short}",
            f"{val_it:.1f}{ctx['unita']}",
            delta=delta,
            help=ctx["spiegazione"],
        )

# ============================================================
# ANDAMENTO ITALIA (Compose)
# ============================================================
st.subheader("Andamento Italia — Tutti i KPI")

if not df_pano.empty:
    pano_it = df_pano[df_pano["paese"] == "IT"].copy()
    if not pano_it.empty:
        pano_it["periodo"] = pano_it["anno"].astype(str) + " " + pano_it["trimestre"]
        pano_it = pano_it.sort_values("periodo")

        fig = go.Figure()

        if "roe_pct" in pano_it.columns:
            fig.add_trace(go.Scatter(
                x=pano_it["periodo"], y=pano_it["roe_pct"],
                name="ROE (%)", line=dict(color="#6366f1", width=2), yaxis="y"))

        if "npl_ratio_pct" in pano_it.columns:
            fig.add_trace(go.Scatter(
                x=pano_it["periodo"], y=pano_it["npl_ratio_pct"],
                name="NPL (%)", line=dict(color="#e74c3c", width=2), yaxis="y2"))

        if "tasso_mutuo_pct" in pano_it.columns:
            fig.add_trace(go.Scatter(
                x=pano_it["periodo"], y=pano_it["tasso_mutuo_pct"],
                name="Tasso Mutuo (%)", line=dict(color="#22c55e", width=2), yaxis="y3"))

        fig.update_layout(
            height=400, margin={"t": 30},
            yaxis=dict(title="ROE (%)", side="left"),
            yaxis2=dict(title="NPL (%)", overlaying="y", side="right"),
            yaxis3=dict(title="Mutuo (%)", overlaying="y", side="right", position=0.95),
            legend=dict(x=0, y=1.15, orientation="h"),
        )
        st.plotly_chart(fig, width="stretch")

# ============================================================
# CONFRONTO EU — ROE
# ============================================================
st.subheader("Confronto EU — Redditività (ROE)")

df_roe = df_bank[~df_bank["paese"].isin(EXCLUDE) & df_bank["roe_pct"].notna()].sort_values("roe_pct")
if not df_roe.empty:
    fig2 = go.Figure()
    colors = []
    for c in df_roe["paese"]:
        status = get_kpi_status("roe_pct", df_roe[df_roe["paese"] == c]["roe_pct"].values[0])
        colors.append(get_status_color(status))
    fig2.add_trace(go.Bar(x=df_roe["roe_pct"], y=df_roe["paese"], orientation="h", marker_color=colors))
    fig2.update_layout(xaxis_title="ROE (%)", height=400, margin={"t": 30, "l": 60})
    st.plotly_chart(fig2, width="stretch")
    st.caption("🟢 Ottimo (>10%) · 🟡 Buono (>6%) · 🟠 Accettabile (>3%) · 🔴 Preoccupante (≤3%)")

# ============================================================
# TASSI
# ============================================================
st.subheader("Confronto Tassi di Interesse")

df_rates = df_pano[~df_pano["paese"].isin(EXCLUDE)].copy() if not df_pano.empty else pd.DataFrame()
if not df_rates.empty and "tasso_mutuo_pct" in df_rates.columns:
    df_rates = df_rates.dropna(subset=["tasso_mutuo_pct"]).drop_duplicates(subset=["paese"]).sort_values("tasso_mutuo_pct")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=df_rates["tasso_mutuo_pct"], y=df_rates["paese"], orientation="h", name="Mutuo", marker_color="#6366f1"))
    if "tasso_depositi_scadenza_pct" in df_rates.columns:
        fig3.add_trace(go.Bar(x=df_rates["tasso_depositi_scadenza_pct"], y=df_rates["paese"], orientation="h", name="Deposit", marker_color="#22c55e"))
    fig3.update_layout(barmode="group", xaxis_title="Tasso (%)", height=400, margin={"t": 30, "l": 60})
    st.plotly_chart(fig3, width="stretch")
    st.caption("Il mutuo è il costo per chi compra casa. Il deposito è il rendimento per chi risparmia.")

# ============================================================
# WORLD BANK: NPL storico
# ============================================================
st.subheader("NPL Ratio — Tendenza Storica")

if not df_wb.empty:
    wb_it = df_wb[df_wb["paese"] == "Italy"]
    if not wb_it.empty and "npl_ratio_pct" in wb_it.columns:
        wb_it = wb_it.sort_values("anno")
        fig_wb = go.Figure()
        fig_wb.add_trace(go.Scatter(
            x=wb_it["anno"], y=wb_it["npl_ratio_pct"],
            mode="lines+markers", line=dict(color="#e74c3c", width=2), fill="tozeroy",
            fillcolor="rgba(231,76,60,0.1)",
        ))
        fig_wb.update_layout(xaxis_title="Anno", yaxis_title="NPL (%)", height=300, margin={"t": 30})
        st.plotly_chart(fig_wb, width="stretch")
        st.caption("I NPL sono scesi dal 18% (2015) al 2.5% (2025) — un miglioramento enorme.")

# ============================================================
# BLS: Condizioni di credito
# ============================================================
st.subheader("Condizioni di Credito (BLS)")

if not df_bls.empty:
    bls_it = df_bls[df_bls["paese"] == "IT"].copy()
    if not bls_it.empty:
        bls_it["periodo"] = bls_it["anno"].astype(str) + " " + bls_it["trimestre"]
        bls_it = bls_it.sort_values("periodo")

        fig_bls = go.Figure()
        if "cs_imprese" in bls_it.columns:
            fig_bls.add_trace(go.Scatter(
                x=bls_it["periodo"], y=bls_it["cs_imprese"], name="Credit standards imprese",
                line=dict(color="#6366f1", width=2),
            ))
        if "domanda_credito_imprese" in bls_it.columns:
            fig_bls.add_trace(go.Scatter(
                x=bls_it["periodo"], y=bls_it["domanda_credito_imprese"], name="Domanda credito",
                line=dict(color="#22c55e", width=2),
            ))
        fig_bls.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_bls.update_layout(yaxis_title="Indice diffusione", height=300, margin={"t": 30})
        st.plotly_chart(fig_bls, width="stretch")
        st.caption("Positivo = le banche stringono i criteri / cresce la domanda. Negativo = allentano / cala.")
