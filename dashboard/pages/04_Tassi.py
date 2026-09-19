"""Tassi di Interesse — deep dive."""

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from sources import load_tassi_all, load_tassi_snapshot, load_tassi_granular

st.title("📈 Tassi di Interesse Bancari")

EXCLUDE = ["U2", "GB", "U5"]

df_rates = load_tassi_all()
df_snap = load_tassi_snapshot()
df_gran = load_tassi_granular()

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
# DETTAGLIO: Tassi per scadenza (dati granulari MIR)
# ============================================================
st.subheader(f"Dettaglio Tassi — {country}")

if not df_gran.empty:
    # Filtra: solo tassi (R), new business (N), paese selezionato
    gr = df_gran[
        (df_gran["paese"] == country) &
        (df_gran["tipo_dato"] == "R") &
        (df_gran["copertura_attivita"] == "N")
    ].copy()

    if not gr.empty:
        # === MUTUI per scadenza ===
        st.markdown("**Mutui first-home: tasso per durata del tasso fisso**")

        mutui = gr[gr["voce"] == "A2C"].copy()
        if not mutui.empty:
            # Aggrega a trimestre (media dei 3 mesi)
            mutui_q = mutui.groupby(["anno", "trimestre", "scadenza"]).agg({"valore": "mean"}).reset_index()
            scadenze_mutui = {
                "F": "Variabile (fino a 1 anno)",
                "I": "Fisso 1-5 anni",
                "K": "Fisso 5-10 anni",
                "O": "Fisso oltre 10 anni",
            }
            fig_m = go.Figure()
            colors_m = ["#6366f1", "#a78bfa", "#818cf8", "#c4b5fd"]
            for (sc, label), color in zip(scadenze_mutui.items(), colors_m):
                d = mutui_q[mutui_q["scadenza"] == sc].sort_values(["anno", "trimestre"])
                if not d.empty:
                    d["periodo_label"] = d["anno"].astype(str) + " " + d["trimestre"]
                    fig_m.add_trace(go.Scatter(
                        x=d["periodo_label"], y=d["valore"],
                        name=label, line=dict(color=color, width=2)))
            fig_m.update_layout(yaxis_title="Tasso (%)", height=350, margin={"t": 30})
            st.plotly_chart(fig_m, width="stretch")
            st.caption("Il tasso fisso più lungo è quasi sempre il più caro — le banche chiedono un premio per bloccare il tasso a lungo.")

        # === IMPRESE per scadenza ===
        st.markdown("**Prestiti imprese: tasso per durata del tasso**")

        imp = gr[gr["voce"] == "A2A"].copy()
        if not imp.empty:
            imp_q = imp.groupby(["anno", "trimestre", "scadenza"]).agg({"valore": "mean"}).reset_index()
            scadenze_imp = {
                "D": "Fino a 1 anno",
                "I": "1-5 anni",
                "K": "5-10 anni",
                "O": "Oltre 10 anni",
            }
            fig_i = go.Figure()
            colors_i = ["#e74c3c", "#f87171", "#fca5a5", "#fecaca"]
            for (sc, label), color in zip(scadenze_imp.items(), colors_i):
                d = imp_q[imp_q["scadenza"] == sc].sort_values(["anno", "trimestre"])
                if not d.empty:
                    d["periodo_label"] = d["anno"].astype(str) + " " + d["trimestre"]
                    fig_i.add_trace(go.Scatter(
                        x=d["periodo_label"], y=d["valore"],
                        name=label, line=dict(color=color, width=2)))
            fig_i.update_layout(yaxis_title="Tasso (%)", height=350, margin={"t": 30})
            st.plotly_chart(fig_i, width="stretch")
            st.caption("Per le imprese il costo cresce con la durata del tasso — il rischio duration si riflette nel prezzo.")

        # === DEPOSITI per scadenza ===
        st.markdown("**Depositi a scadenza: tasso per durata del vincolo**")

        dep = gr[gr["voce"] == "L22"].copy()
        if not dep.empty:
            dep_q = dep.groupby(["anno", "trimestre", "scadenza"]).agg({"valore": "mean"}).reset_index()
            scadenze_dep = {
                "F": "Fino a 1 anno",
                "H": "1-2 anni",
                "K": "2-3 anni",
                "L": "Oltre 3 anni",
            }
            fig_d = go.Figure()
            colors_d = ["#22c55e", "#4ade80", "#86efac", "#bbf7d0"]
            for (sc, label), color in zip(scadenze_dep.items(), colors_d):
                d = dep_q[dep_q["scadenza"] == sc].sort_values(["anno", "trimestre"])
                if not d.empty:
                    d["periodo_label"] = d["anno"].astype(str) + " " + d["trimestre"]
                    fig_d.add_trace(go.Scatter(
                        x=d["periodo_label"], y=d["valore"],
                        name=label, line=dict(color=color, width=2)))
            fig_d.update_layout(yaxis_title="Tasso (%)", height=350, margin={"t": 30})
            st.plotly_chart(fig_d, width="stretch")
            st.caption("I vincoli più lunghi rendono di più — la liquidità ha un prezzo.")
