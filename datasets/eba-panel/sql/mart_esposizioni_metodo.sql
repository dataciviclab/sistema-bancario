-- mart_esposizioni_metodo: la stessa esposizione vista per approccio regolamentare
--
-- Una riga = banca x paese controparte x periodo x metodo (SA / IRB).
--
-- Serve a rispondere a due domande che il mart aggregato non puo' dare:
--   1. quanto pesa il modello interno di una banca (IRB) rispetto allo
--      standardizzato: e' la ragione per cui le quote SA-only erano incomparabili;
--   2. quanto capitale assorbe ciascun approccio (RWA / esposizione).

WITH serie AS (
    SELECT
        banca,
        nome_banca,
        paese,
        periodo,
        paese_controparte,
        codice_paese_controparte,
        metodo,
        SUM(CASE WHEN metrica LIKE 'esposizione_%' THEN valore END) AS esposizione_mld,
        SUM(CASE WHEN metrica = 'esposizione_sovrana' THEN valore END) AS esposizione_sovrana_mld,
        SUM(CASE WHEN metrica LIKE 'rwa_%' THEN valore END) AS rwa_mld
    FROM clean_input
    WHERE paese_controparte IS NOT NULL
      AND metodo IS NOT NULL
      AND metodo <> ''
    GROUP BY banca, nome_banca, paese, periodo, paese_controparte,
             codice_paese_controparte, metodo
)

SELECT
    banca,
    nome_banca,
    paese,
    periodo,
    paese_controparte,
    codice_paese_controparte,
    metodo,
    ROUND(esposizione_mld, 1) AS esposizione_mld,
    ROUND(esposizione_sovrana_mld, 1) AS esposizione_sovrana_mld,
    ROUND(rwa_mld, 1) AS rwa_mld,
    ROUND(rwa_mld / NULLIF(esposizione_mld, 0) * 100, 2) AS densita_rwa_pct
FROM serie
WHERE ROUND(esposizione_mld, 1) > 0
ORDER BY banca, periodo, paese_controparte, metodo
