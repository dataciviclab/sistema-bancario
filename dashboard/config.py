"""Costanti condivise dalla dashboard.

Un solo posto per i codici che non sono paesi: prima erano copiati in sette
pagine, con il Regno Unito che restava nell'elenco anche dopo l'uscita dal
panel EBA.
"""

# U2 = area euro, B0 = Unione europea, U5 = altri paesi dell'area, 4F = BCE.
# GB: serie EBA che si ferma al 2019, fuori dai confronti sull'ultimo periodo.
PAESI_ESCLUSI = frozenset({"U2", "B0", "U5", "4F", "GB"})
