-- mart_bls_snapshot: ultimo trimestre disponibile per paese
--
-- Stesse serie dichiarate di mart_bls_credit, stesso perimetro.

WITH serie AS (
    SELECT
        paese,
        anno,
        trimestre,
        MAX(CASE WHEN metrica = 'cs_imprese' THEN valore END) AS cs_imprese,
        MAX(CASE WHEN metrica = 'cs_pmi' THEN valore END) AS cs_pmi,
        MAX(CASE WHEN metrica = 'cs_grandi' THEN valore END) AS cs_grandi,
        MAX(CASE WHEN metrica = 'cs_mutui' THEN valore END) AS cs_mutui,
        MAX(CASE WHEN metrica = 'domanda_imprese' THEN valore END) AS domanda_credito_imprese,
        MAX(CASE WHEN metrica = 'domanda_mutui' THEN valore END) AS domanda_credito_famiglie,
        MAX(CASE WHEN metrica = 'margins_prestiti' THEN valore END) AS margins_prestiti,
        MAX(CASE WHEN metrica = 'spese_non_interesse' THEN valore END) AS spese_non_interesse
    FROM clean_input
    WHERE trimestre IS NOT NULL
      AND LENGTH(paese) = 2
      AND paese NOT IN ('U2', 'U5', '4F')
    GROUP BY paese, anno, trimestre
),

ultimo AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY paese ORDER BY anno DESC, trimestre DESC) AS rn
    FROM serie
    WHERE cs_imprese IS NOT NULL
)

SELECT
    paese,
    anno,
    trimestre,
    ROUND(cs_imprese, 2) AS cs_imprese,
    ROUND(cs_pmi, 2) AS cs_pmi,
    ROUND(cs_grandi, 2) AS cs_grandi,
    ROUND(cs_mutui, 2) AS cs_mutui,
    ROUND(domanda_credito_imprese, 2) AS domanda_credito_imprese,
    ROUND(domanda_credito_famiglie, 2) AS domanda_credito_famiglie,
    ROUND(margins_prestiti, 2) AS margins_prestiti,
    ROUND(spese_non_interesse, 2) AS spese_non_interesse
FROM ultimo
WHERE rn = 1
ORDER BY paese
