"""Data sources for the Sistema Bancario dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from pathlib import Path

from lab_connectors.duckdb.queries import years_from_registry
from lab_connectors.duckdb.queries import load_mart_flat, load_mart_table
from lab_connectors.registry import load_registry

_REPO_ROOT = Path(__file__).parent.parent
_LOCAL_DATA = _REPO_ROOT / "out" / "data"
LOCAL_ROOT = str(_LOCAL_DATA) if _LOCAL_DATA.is_dir() else None
PREFIX = "sistema_bancario/"
_registry = load_registry(_REPO_ROOT / "registry" / "registry.json")


def _latest_year(slug: str) -> int:
    """Restituisce l'anno più recente disponibile per uno slug dal registry."""
    years = years_from_registry(_registry, slug=slug)
    if not years:
        raise ValueError(f"Dataset {slug} non trovato nel registry")
    return max(years)


def _years(slug: str) -> list[int]:
    """Anni disponibili per uno slug dal registry."""
    return years_from_registry(_registry, slug=slug)


def _mart(slug: str, table: str, year: int | None = None) -> pd.DataFrame:
    if year is None:
        return load_mart_flat(slug, table, prefix=PREFIX, local_root=LOCAL_ROOT)
    return load_mart_table(slug, table, year, prefix=PREFIX, local_root=LOCAL_ROOT)


def get_last_updated() -> str:
    return "N/A"


# --- CBD2: KPI bancari ---

@st.cache_data(ttl=3600, show_spinner=False)
def load_kpi(year: int = 2026) -> pd.DataFrame:
    return _mart("ecb_cbd2", "mart_bank_kpi", year)


@st.cache_data(ttl=3600, show_spinner=False)
def load_snapshot(year: int = 2026) -> pd.DataFrame:
    return _mart("ecb_cbd2", "mart_bank_snapshot", year)


@st.cache_data(ttl=3600, show_spinner=False)
def load_kpi_all() -> pd.DataFrame:
    frames = []
    for y in _years("ecb_cbd2"):
        try:
            df = _mart("ecb_cbd2", "mart_bank_kpi", y)
            if not df.empty:
                frames.append(df)
        except Exception:
            pass
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# --- BSI: Bilanci MFI ---

@st.cache_data(ttl=3600, show_spinner=False)
def load_bilanci(year: int = 2026) -> pd.DataFrame:
    return _mart("ecb_bsi", "mart_bsi_balance", year)


@st.cache_data(ttl=3600, show_spinner=False)
def load_deposits(year: int = 2026) -> pd.DataFrame:
    return _mart("ecb_bsi", "mart_bsi_deposits", year)


@st.cache_data(ttl=3600, show_spinner=False)
def load_bsi_snapshot(year: int = 2026) -> pd.DataFrame:
    return _mart("ecb_bsi", "mart_bsi_snapshot", year)


@st.cache_data(ttl=3600, show_spinner=False)
def load_bilanci_all() -> pd.DataFrame:
    frames = []
    for y in _years("ecb_bsi"):
        try:
            df = _mart("ecb_bsi", "mart_bsi_balance", y)
            if not df.empty:
                frames.append(df)
        except Exception:
            pass
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def load_deposits_all() -> pd.DataFrame:
    frames = []
    for y in _years("ecb_bsi"):
        try:
            df = _mart("ecb_bsi", "mart_bsi_deposits", y)
            if not df.empty:
                frames.append(df)
        except Exception:
            pass
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# --- MIR: Tassi di interesse ---

@st.cache_data(ttl=3600, show_spinner=False)
def load_tassi(year: int = 2026) -> pd.DataFrame:
    return _mart("ecb_mir", "mart_mir_rates", year)


@st.cache_data(ttl=3600, show_spinner=False)
def load_tassi_snapshot(year: int = 2026) -> pd.DataFrame:
    return _mart("ecb_mir", "mart_mir_snapshot", year)


@st.cache_data(ttl=3600, show_spinner=False)
def load_tassi_all() -> pd.DataFrame:
    frames = []
    for y in _years("ecb_mir"):
        try:
            df = _mart("ecb_mir", "mart_mir_rates", y)
            if not df.empty:
                frames.append(df)
        except Exception:
            pass
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def load_tassi_granular() -> pd.DataFrame:
    """Carica dati MIR granulari (tutte le scadenze) dal clean layer."""
    frames = []
    for y in _years("ecb_mir"):
        try:
            df = pd.read_parquet(f"{LOCAL_ROOT}/clean/ecb_mir/{y}/ecb_mir_{y}_clean.parquet")
            if not df.empty:
                frames.append(df)
        except Exception:
            pass
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# --- World Bank: Indicatori storici ---

@st.cache_data(ttl=3600, show_spinner=False)
def load_wb_snapshot() -> pd.DataFrame:
    return _mart("wb_financial", "mart_wd_snapshot", _latest_year("wb_financial"))


@st.cache_data(ttl=3600, show_spinner=False)
def load_wb_indicators() -> pd.DataFrame:
    return _mart("wb_financial", "mart_wd_indicators", _latest_year("wb_financial"))


# --- BLS: Condizioni di credito ---

@st.cache_data(ttl=3600, show_spinner=False)
def load_bls_snapshot() -> pd.DataFrame:
    return _mart("ecb_bls", "mart_bls_snapshot", 2026)


@st.cache_data(ttl=3600, show_spinner=False)
def load_bls_credit() -> pd.DataFrame:
    return _mart("ecb_bls", "mart_bls_credit", 2026)


# --- Compose: Vista unificata ---

@st.cache_data(ttl=3600, show_spinner=False)
def load_panorama() -> pd.DataFrame:
    return _mart("banche_unified", "mart_panorama", 2026)


# --- EBA Panel: Dati per singola banca ---

@st.cache_data(ttl=3600, show_spinner=False)
def load_banche_kpi() -> pd.DataFrame:
    return _mart("eba_panel", "mart_banche_kpi", _latest_year("eba_panel"))


@st.cache_data(ttl=3600, show_spinner=False)
def load_banche_snapshot() -> pd.DataFrame:
    return _mart("eba_panel", "mart_banche_snapshot", _latest_year("eba_panel"))
