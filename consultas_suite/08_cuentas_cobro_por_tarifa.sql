-- DIMENSION 8: Numero de CUENTAS DE COBRO (utility) por tarifa.
-- Cuenta de cobro = CARGOS.CARGCUCO (CUENCOBR). Detecta diferencias en cuantas
-- cuentas se generaron por plan entre V7 y V8.
SELECT '{ESQUEMA}'                 AS empresa,
       g.NAME                      AS cuenta,        -- tarifa / plan
       'NCUENTAS_COBRO'            AS concepto,
       COUNT(DISTINCT c.CARGCUCO)  AS monto
FROM   {ESQUEMA}.CARGOS c
JOIN   {ESQUEMA}.CUENCOBR cu           ON cu.CUCOCODI = c.CARGCUCO
JOIN   {ESQUEMA}.CC_COMMERCIAL_PLAN g  ON g.COMMERCIAL_PLAN_ID = cu.CUCOPLSU
JOIN   {ESQUEMA}.SERVSUSC s            ON s.SESUNUSE = c.CARGNUSE
WHERE  c.CARGPEFA = {PEFA} AND c.CARGTIPR = 'A'
  AND  s.SESUSERV = {SUBSERVE}
GROUP BY g.NAME
