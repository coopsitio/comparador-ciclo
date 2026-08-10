-- DIMENSION 3: Cantidad de cargos fijos (concepto 1001) por tarifa (utility).
-- Deberia haber 1 cargo fijo por producto: si el total por tarifa no coincide
-- con el numero de productos, hay productos con multiples (o cero) cargo fijo.
-- Detecta el problema clasico de "multi cargo fijo" y diferencias V7 vs V8.
SELECT '{ESQUEMA}'          AS empresa,
       g.NAME               AS cuenta,               -- tarifa / plan
       'N_CARGO_FIJO_1001'  AS concepto,
       COUNT(*)             AS monto
FROM   {ESQUEMA}.CARGOS c
JOIN   {ESQUEMA}.CUENCOBR cu           ON cu.CUCOCODI = c.CARGCUCO
JOIN   {ESQUEMA}.CC_COMMERCIAL_PLAN g  ON g.COMMERCIAL_PLAN_ID = cu.CUCOPLSU
JOIN   {ESQUEMA}.SERVSUSC s            ON s.SESUNUSE = c.CARGNUSE
WHERE  c.CARGPEFA = {PEFA} AND c.CARGTIPR = 'A' AND c.CARGCONC = 1001
  AND  s.SESUSERV = {SUBSERVE}
GROUP BY g.NAME
