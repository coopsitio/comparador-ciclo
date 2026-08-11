-- DIMENSION 10: Consumo MEDIDO NORMALIZADO por dia (kWh/dia) por tarifa (utility).
-- Divide el consumo por los DIAS de consumo (COSSDICO). Sirve para comparar V7 vs V8
-- sin el efecto de la VENTANA TEMPORAL: aunque V8 acumule mas dias, la TASA diaria
-- deberia coincidir con V7 si el dato es el mismo. Es la comparacion "justa".
SELECT '{ESQUEMA}'                                        AS empresa,
       g.NAME                                             AS cuenta,      -- tarifa / plan
       'KWH_DIA'                                          AS concepto,
       ROUND(SUM(cs.COSSCOCA) / NULLIF(SUM(cs.COSSDICO), 0), 2) AS monto  -- kWh por dia
FROM   {ESQUEMA}.CONSSESU cs
JOIN   {ESQUEMA}.SERVSUSC s            ON s.SESUNUSE = cs.COSSSESU
JOIN   {ESQUEMA}.PR_PRODUCT p          ON p.PRODUCT_ID = cs.COSSSESU
JOIN   {ESQUEMA}.CC_COMMERCIAL_PLAN g  ON g.COMMERCIAL_PLAN_ID = p.COMMERCIAL_PLAN_ID
WHERE  cs.COSSPEFA = {PEFA} AND cs.COSSMECC = 4 AND cs.COSSTCON = 103
  AND  s.SESUSERV = {SUBSERVE}
GROUP BY g.NAME
