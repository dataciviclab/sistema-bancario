"""Tassi di Interesse — deep dive."""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from sources import load_tassi_all, load_tassi_snapshot, load_volumi

st.title("📈 Tassi di Interesse Bancari")

EXCLUDE = ["U2", "GB", "U5"]

df_rates = load_tassi_all()
df_snap = load_tassi_snapshot()
df_vol = load_volumi()

if df_rates.empty:
    st.warning("Nessun dato disponibile.")
    st.stop()

countries = sorted(df_rates[~df_rates["paese"].isin(EXCLUDE)]["paese"].unique())
country = st.selectbox("Paese", countries, index=countries.index("IT") if "IT" in countries else 0)

df_c = df_rates[df_rates["paese"] == country].copy()
if not df_c.empty and "anno" in df_c.columns and "trimestre" in df_c.columns:
    df_c["periodo_label"] = df_c["anno"].astype(str) + " " + df_c["trimestre"]

# --- Trend ---
st.subheader(f"Trend Tassi — {country}")

if not df_c.empty:
    df_q = df_c[df_c["trimestre"].notna()].copy()
    if not df_q.empty:
        fig = make_subplots(rows=2, cols=1, subplot_titles=("Prestiti (mutui e imprese)", "Depositi"), vertical_spacing=0.15)

        if "tasso_mutuo_pct" in df_q.columns:
            fig.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_mutuo_pct"], name="Mutuo", line=dict(color="#6366f1", width=2)), row=1, col=1)
        if "tasso_mutuo_variabile_pct" in df_q.columns:
            fig.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_mutuo_variabile_pct"], name="Variabile", line=dict(color="#a78bfa", width=2, dash="dash")), row=1, col=1)
        if "tasso_mutuo_fisso_1_5a_pct" in df_q.columns:
            fig.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_mutuo_fisso_1_5a_pct"], name="Fisso 1-5a", line=dict(color="#818cf8", width=2, dash="dot")), row=1, col=1)
        if "tasso_imprese_pct" in df_q.columns:
            fig.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_imprese_pct"], name="Imprese", line=dict(color="#e74c3c", width=2)), row=1, col=1)

        if "tasso_depositi_overnight_pct" in df_q.columns:
            fig.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_depositi_overnight_pct"], name="Overnight", line=dict(color="#22c55e", width=2)), row=2, col=1)
        if "tasso_depositi_scadenza_pct" in df_q.columns:
            fig.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_depositi_scadenza_pct"], name="Scadenza", line=dict(color="#16a34a", width=2)), row=2, col=1)

        fig.update_layout(height=550, margin={"t": 40})
        fig.update_yaxes(title_text="Tasso (%)")
        st.plotly_chart(fig, width="stretch")

# --- Spread ---
st.subheader("Spread Mutuo/Deposito")

if not df_c.empty and "spread_mutuo_deposito_pp" in df_c.columns:
    df_q = df_c[df_c["trimestre"].notna()].copy()
    if not df_q.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["spread_mutuo_deposito_pp"], fill="tozeroy", line=dict(color="#6366f1", width=2), fillcolor="rgba(99,102,241,0.2)", name="Spread"))
        fig2.add_hline(y=0, line_dash="dash", line_color="gray")
        fig2.update_layout(yaxis_title="Spread (pp)", height=250, margin={"t": 30})
        st.plotly_chart(fig2, width="stretch")

# --- Confronto ---
st.subheader("Confronto Tassi Mutuo (latest)")

if not df_snap.empty:
    df_f = df_snap[~df_snap["paese"].isin(EXCLUDE) & df_snap["tasso_mutuo_pct"].notna()].sort_values("tasso_mutuo_pct")
    if not df_f.empty:
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=df_f["tasso_mutuo_pct"], y=df_f["paese"], orientation="h", marker_color=["#6366f1" if c == country else "#94a3b8" for c in df_f["paese"]]))
        fig3.update_layout(xaxis_title="Tasso Mutuo (%)", height=400, margin={"t": 30, "l": 60})
        st.plotly_chart(fig3, width="stretch")

# ============================================================
# DETTAGLIO: Mutui per tipo di tasso
# ============================================================
st.subheader(f"Mutui per tipo di tasso — {country}")

if not df_c.empty:
    df_q = df_c[df_c["trimestre"].notna()].copy()
    if not df_q.empty:
        figm = go.Figure()
        if "tasso_mutuo_variabile_pct" in df_q.columns:
            figm.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_mutuo_variabile_pct"], name="Variabile (fino a 1 anno)", line=dict(color="#6366f1", width=2)))
        if "tasso_mutuo_fisso_1_5a_pct" in df_q.columns:
            figm.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_mutuo_fisso_1_5a_pct"], name="Fisso 1-5 anni", line=dict(color="#a78bfa", width=2)))
        if "tasso_mutuo_fisso_5_10a_pct" in df_q.columns:
            figm.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_mutuo_fisso_5_10a_pct"], name="Fisso 5-10 anni", line=dict(color="#c4b5fd", width=2)))
        figm.update_layout(yaxis_title="Tasso (%)", height=350, margin={"t": 30})
        st.plotly_chart(figm, width="stretch")
        st.caption("Serie MIR dichiarate in datasets/ecb-mir/series_catalog.csv: nuovi contratti, tutte le classi di importo.")

# ============================================================
# DETTAGLIO: Quanto costa il credito alle piccole imprese
# ============================================================
st.subheader(f"Imprese: piccolo vs medio-grande — {country}")

if not df_c.empty:
    df_q = df_c[df_c["trimestre"].notna()].copy()
    if not df_q.empty and "tasso_imprese_piccole_pct" in df_q.columns:
        figp = go.Figure()
        figp.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_imprese_pct"], name="Tutti gli importi", line=dict(color="#e74c3c", width=2)))
        figp.add_trace(go.Scatter(x=df_q["periodo_label"], y=df_q["tasso_imprese_piccole_pct"], name="Fino a 0,25 mln", line=dict(color="#f59e0b", width=2, dash="dash")))
        figp.update_layout(yaxis_title="Tasso (%)", height=350, margin={"t": 30})
        st.plotly_chart(figp, width="stretch")
        st.caption("Le imprese piu' piccole pagano un premio: e' il costo del credito che non vedi nei titoli.")

# ============================================================
# QUANTO CREDITO NUOVO
# ============================================================
st.subheader(f"Nuovo credito per trimestre — {country}")

if not df_vol.empty:
    df_v = df_vol[df_vol["paese"] == country].copy()
    if not df_v.empty:
        df_v["periodo_label"] = df_v["anno"].astype(str) + " " + df_v["trimestre"]
        df_v = df_v.sort_values(["anno", "trimestre"])

        figv = go.Figure()
        if "volume_mutui_mld" in df_v.columns:
            figv.add_trace(go.Bar(x=df_v["periodo_label"], y=df_v["volume_mutui_mld"],
                                  name="Mutui casa", marker_color="#6366f1"))
        if "volume_prestiti_imprese_mld" in df_v.columns:
            figv.add_trace(go.Bar(x=df_v["periodo_label"], y=df_v["volume_prestiti_imprese_mld"],
                                  name="Prestiti alle imprese", marker_color="#f59e0b"))
        figv.update_layout(barmode="group", yaxis_title="Miliardi € nel trimestre",
                           height=350, margin={"t": 30})
        st.plotly_chart(figv, width="stretch")

        if "quota_piccole_imprese_pct" in df_v.columns:
            quota = df_v["quota_piccole_imprese_pct"].dropna()
            if not quota.empty:
                st.caption(
                    f"Flussi trimestrali (somma dei tre mesi). Alle imprese fino a 1 mln "
                    f"va il {quota.iloc[-1]:.0f}% del nuovo credito alle imprese."
                )
