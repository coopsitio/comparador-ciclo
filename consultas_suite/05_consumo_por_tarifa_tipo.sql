-- DIMENSION 5: Energia/potencia MEDIDA por tarifa x tipo de consumo (utility).
-- COSSTCON: 103 energia activa, 104 reactiva, 107 demanda max, 108 demanda HP,
-- 105 potencia contratada, etc. Detecta diferencias V7 vs V8 en cualquier medida,
-- no solo la energia activa. Plan tomado del producto actual (PR_PRODUCT).
SELECT '{ESQUEMA}'         AS empresa,
       g.NAME              AS cuenta,                -- tarifa / plan
       cs.COSSTCON         AS concepto,             -- tipo de consumo
       SUM(cs.COSSCOCA)    AS monto
FROM   {ESQUEMA}.CONSSESU cs
JOIN   {ESQUEMA}.SERVSUSC s            ON s.SESUNUSE = cs.COSSSESU
JOIN   {ESQUEMA}.PR_PRODUCT p          ON p.PRODUCT_ID = cs.COSSSESU
JOIN   {ESQUEMA}.CC_COMMERCIAL_PLAN g  ON g.COMMERCIAL_PLAN_ID = p.COMMERCIAL_PLAN_ID
WHERE  cs.COSSPEFA = {PEFA} AND cs.COSSMECC = 4
  AND  s.SESUSERV = {SUBSERVE}
GROUP BY g.NAME, cs.COSSTCON
