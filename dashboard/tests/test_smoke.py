"""Smoke test — verifica che tutte le pagine siano importabili."""

import py_compile
import pathlib

DASHBOARD_DIR = pathlib.Path(__file__).parent.parent
PAGES = DASHBOARD_DIR / "pages"

def test_all_pages_importable():
    """Every page .py file should compile without errors."""
    errors = []
    for page_file in sorted(PAGES.glob("*.py")):
        try:
            py_compile.compile(str(page_file), doraise=True)
        except py_compile.PyCompileError as e:
            errors.append(str(e))
    assert not errors, f"Pages with compilation errors:\n" + "\n".join(errors)
