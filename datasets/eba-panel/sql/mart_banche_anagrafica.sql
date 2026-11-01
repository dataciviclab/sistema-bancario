-- mart_banche_anagrafica: chi sono le banche del panel
--
-- Una riga per banca. Serve a leggere i mart senza conoscere il codice EBA:
-- nome leggibile, paese, LEI, stato SSM, copertura temporale.
--
-- Il campo `gruppo` non c'e' di proposito: il panel EBA identifica la banca
-- (LEI), non il gruppo di appartenenza, e ricostruirlo dai nomi sarebbe un
-- dato inventato. Per i gruppi serve l'albo Banca d'Italia (fonte separata).

WITH base AS (
    SELECT
        banca,
        nome_banca,
        nome_legale,
        paese,
        nome_paese,
        tipo_ssm,
        finrep,
        lei,
        periodo
    FROM clean_input
)

SELECT
    banca,
    MAX(nome_banca) AS nome_banca,
    MAX(nome_legale) AS nome_legale,
    MAX(paese) AS paese,
    MAX(nome_paese) AS nome_paese,
    MAX(tipo_ssm) AS tipo_ssm,
    MAX(finrep) AS finrep,
    MAX(lei) AS lei,
    MIN(periodo) AS periodo_min,
    MAX(periodo) AS periodo_max,
    COUNT(DISTINCT periodo) AS n_periodi
FROM base
GROUP BY banca
ORDER BY paese, nome_banca
