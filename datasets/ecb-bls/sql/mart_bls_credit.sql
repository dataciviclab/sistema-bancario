-- mart_bls_credit: condizioni e domanda di credito per paese/trimestre
--
-- Una colonna = una serie dichiarata in series_catalog.csv.
-- Indice di diffusione: positivo = stretta sulle condizioni / domanda in
-- aumento a seconda della metrica (vedi `descrizione` nel catalogo).

WITH serie AS (
    SELECT
        paese,
        anno,
        trimestre,
        MAX(CASE WHEN metrica = 'cs_imprese' THEN valore END) AS cs_imprese,
        MAX(CASE WHEN metrica = 'cs_pmi' THEN valore END) AS cs_pmi,
        MAX(CASE WHEN metrica = 'cs_grandi' THEN valore END) AS cs_grandi,
        MAX(CASE WHEN metrica = 'cs_mutui' THEN valore END) AS cs_mutui,
        MAX(CASE WHEN metrica = 'cs_consumo' THEN valore END) AS cs_consumo,
        MAX(CASE WHEN metrica = 'domanda_imprese' THEN valore END) AS domanda_credito_imprese,
        MAX(CASE WHEN metrica = 'domanda_mutui' THEN valore END) AS domanda_credito_famiglie,
        MAX(CASE WHEN metrica = 'margins_prestiti' THEN valore END) AS margins_prestiti,
        MAX(CASE WHEN metrica = 'margini_rischiosi' THEN valore END) AS margini_rischiosi,
        MAX(CASE WHEN metrica = 'spese_non_interesse' THEN valore END) AS spese_non_interesse,
        MAX(CASE WHEN metrica = 'rifiutate_imprese' THEN valore END) AS rifiutate_imprese_pct
    FROM clean_input
    WHERE trimestre IS NOT NULL
      AND LENGTH(paese) = 2
      AND paese NOT IN ('U2', 'U5', '4F')
    GROUP BY paese, anno, trimestre
)

SELECT
    paese,
    anno,
    trimestre,
    ROUND(cs_imprese, 2) AS cs_imprese,
    ROUND(cs_pmi, 2) AS cs_pmi,
    ROUND(cs_grandi, 2) AS cs_grandi,
    ROUND(cs_mutui, 2) AS cs_mutui,
    ROUND(cs_consumo, 2) AS cs_consumo,
    ROUND(domanda_credito_imprese, 2) AS domanda_credito_imprese,
    ROUND(domanda_credito_famiglie, 2) AS domanda_credito_famiglie,
    ROUND(margins_prestiti, 2) AS margins_prestiti,
    ROUND(margini_rischiosi, 2) AS margini_rischiosi,
    ROUND(spese_non_interesse, 2) AS spese_non_interesse,
    ROUND(rifiutate_imprese_pct, 2) AS rifiutate_imprese_pct,
    -- Divario PMI vs grandi imprese: chi paga la stretta
    ROUND(cs_pmi - cs_grandi, 2) AS divario_pmi_grandi
FROM serie
WHERE cs_imprese IS NOT NULL
ORDER BY paese, anno, trimestre
