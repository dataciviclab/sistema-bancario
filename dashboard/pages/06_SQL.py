"""Query SQL — Interroga direttamente i dati."""

from lab_connectors.duckdb.sql_page import render_sql_query
from lab_connectors.registry import load_registry_github

render_sql_query(
    registry=load_registry_github("sistema-bancario"),
    prefix="sistema-bancario/",
    default_slug="ecb_cbd2",
    title="🧪 Query SQL",
    description="Interroga direttamente i dati bancari europei.",
)
