"""Confronti — Cross-country comparison."""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from sources import load_snapshot, load_tassi_snapshot, load_bsi_snapshot

st.title("⚖️ Confronti Paesi")

EXCLUDE = ["U2", "GB", "U5"]

df_bank = load_snapshot()
df_mir = load_tassi_snapshot()
df_bsi = load_bsi_snapshot()

if df_bank.empty:
    st.warning("Nessun dato disponibile.")
    st.stop()

countries = sorted(df_bank[~df_bank["paese"].isin(EXCLUDE)]["paese"].unique())
selected = st.multiselect("Seleziona paesi", countries, default=["IT", "DE", "FR", "ES"])

if not selected:
    st.info("Seleziona almeno un paese.")
    st.stop()

# --- Radar chart ---
st.subheader("Profilo Bancario")

radar_kpis = ["roe_pct", "cet1_pct", "npl_ratio_pct", "costo_reddito_pct", "lcr_pct"]
radar_labels = ["Redditività", "Capitale", "Sofferenze", "Efficienza", "Liquidità"]
max_vals = [15, 25, 15, 80, 200]
invert = [False, False, True, True, False]  # NPL e C/I: più alto = peggio

fig = go.Figure()
for country in selected:
    row = df_bank[df_bank["paese"] == country]
    if not row.empty:
        vals = []
        for k, m, inv in zip(radar_kpis, max_vals, invert):
            v = row.iloc[0].get(k, 0) or 0
            v = abs(v)  # C/I è negativo nei dati CBD2
            norm = min(v / m * 100, 100)
            vals.append(100 - norm if inv else norm)
        vals.append(vals[0])
        fig.add_trace(go.Scatterpolar(r=vals, theta=radar_labels + [radar_labels[0]], fill="toself", name=country))

fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), height=450, margin={"t": 40})
st.plotly_chart(fig, width="stretch")

# --- Bar charts ---
st.subheader("Confronto Diretto")

metrics = {
    "roe_pct": ("Redditività ROE (%)", "#6366f1"),
    "cet1_pct": ("Capitale CET1 (%)", "#22c55e"),
    "npl_ratio_pct": ("Sofferenze NPL (%)", "#e74c3c"),
    "costo_reddito_pct": ("Efficienza C/I (%)", "#f59e0b"),
}

cols = st.columns(2)
for i, (col_name, (label, color)) in enumerate(metrics.items()):
    with cols[i % 2]:
        df_f = df_bank[df_bank["paese"].isin(selected) & df_bank[col_name].notna()]
        if not df_f.empty:
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(x=df_f["paese"], y=df_f[col_name], marker_color=color))
            fig_bar.update_layout(title=label, height=250, margin={"t": 40, "b": 30})
            st.plotly_chart(fig_bar, width="stretch")

# --- Interest rates ---
st.subheader("Tassi di Interesse")

if not df_mir.empty:
    df_sel = df_mir[df_mir["paese"].isin(selected)]
    if not df_sel.empty and "tasso_mutuo_pct" in df_sel.columns:
        fig_rates = go.Figure()
        for country in selected:
            dc = df_sel[df_sel["paese"] == country]
            if not dc.empty:
                fig_rates.add_trace(go.Bar(
                    x=["Mutuo", "Imprese", "Deposit"],
                    y=[dc["tasso_mutuo_pct"].values[0],
                       dc.get("tasso_imprese_pct", pd.Series([0])).values[0],
                       dc.get("tasso_depositi_scadenza_pct", pd.Series([0])).values[0]],
                    name=country))
        fig_rates.update_layout(barmode="group", height=350, margin={"t": 30})
        st.plotly_chart(fig_rates, width="stretch")

# --- Table ---
st.subheader("Tabella Riepilogativa")

cols_show = ["paese", "roe_pct", "cet1_pct", "npl_ratio_pct", "costo_reddito_pct", "lcr_pct", "prestiti_deposits_pct"]
cols_avail = [c for c in cols_show if c in df_bank.columns]
df_table = df_bank[df_bank["paese"].isin(selected)][cols_avail].copy()
df_table.columns = [c.replace("_", " ").title() for c in df_table.columns]
st.dataframe(df_table, use_container_width=True, hide_index=True)
