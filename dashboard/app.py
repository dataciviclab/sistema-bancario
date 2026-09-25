"""
Sistema Bancario Intelligence - Dashboard Streamlit
"""

import streamlit as st
from lab_connectors.branding import apply_branding

st.set_page_config(
    page_title="Sistema Bancario - Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_branding(
    repo_name="sistema-bancario", repo_url="https://github.com/dataciviclab/sistema-bancario"
)

pages = {
    "": [
        st.Page("pages/01_Panoramica.py", title="Panoramica", icon="📊", default=True),
    ],
    "Analisi": [
        st.Page("pages/02_Italia.py", title="Italia", icon="🇮🇹"),
        st.Page("pages/03_Confronti.py", title="Confronti", icon="⚖️"),
        st.Page("pages/04_Tassi.py", title="Tassi di Interesse", icon="📈"),
        st.Page("pages/05_Bilanci.py", title="Bilanci MFI", icon="🏦"),
        st.Page("pages/07_Storageico.py", title="Tendenze Storiche", icon="📊"),
        st.Page("pages/08_BancheSingole.py", title="Banche Singole", icon="🏛️"),
    ],
    "Strumenti": [
        st.Page("pages/06_SQL.py", title="Query SQL", icon="🧪"),
    ],
}

pg = st.navigation(pages, position="sidebar")
pg.run()
