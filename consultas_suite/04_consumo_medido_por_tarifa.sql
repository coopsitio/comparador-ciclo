-- DIMENSION 4: Energia MEDIDA (kWh activa, tipo consumo 103) por tarifa (utility).
-- Compara el consumo leido (CONSSESU) entre V7 y V8. La tarifa se toma del plan
-- ACTUAL del producto (PR_PRODUCT); sirve para contrastar volumen medido por plan.
SELECT '{ESQUEMA}'         AS empresa,
       g.NAME              AS cuenta,                -- tarifa / plan (actual)
       'KWH_MEDIDO_103'    AS concepto,
       SUM(cs.COSSCOCA)    AS monto
FROM   {ESQUEMA}.CONSSESU cs
JOIN   {ESQUEMA}.SERVSUSC s            ON s.SESUNUSE = cs.COSSSESU
JOIN   {ESQUEMA}.PR_PRODUCT p          ON p.PRODUCT_ID = cs.COSSSESU
JOIN   {ESQUEMA}.CC_COMMERCIAL_PLAN g  ON g.COMMERCIAL_PLAN_ID = p.COMMERCIAL_PLAN_ID
WHERE  cs.COSSPEFA = {PEFA} AND cs.COSSMECC = 4 AND cs.COSSTCON = 103
  AND  s.SESUSERV = {SUBSERVE}
GROUP BY g.NAME
