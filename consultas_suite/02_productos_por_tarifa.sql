-- DIMENSION 2: Numero de productos (utility) facturados por tarifa.
-- Detecta tarifas donde el UNIVERSO de productos difiere entre V7 y V8
-- (productos que aparecen/desaparecen, o cambian de plan).
SELECT '{ESQUEMA}'               AS empresa,
       g.NAME                    AS cuenta,          -- tarifa / plan
       'NPRODUCTOS'              AS concepto,
       COUNT(DISTINCT c.CARGNUSE) AS monto
FROM   {ESQUEMA}.CARGOS c
JOIN   {ESQUEMA}.CUENCOBR cu           ON cu.CUCOCODI = c.CARGCUCO
JOIN   {ESQUEMA}.CC_COMMERCIAL_PLAN g  ON g.COMMERCIAL_PLAN_ID = cu.CUCOPLSU
JOIN   {ESQUEMA}.SERVSUSC s            ON s.SESUNUSE = c.CARGNUSE
WHERE  c.CARGPEFA = {PEFA} AND c.CARGTIPR = 'A'
  AND  s.SESUSERV = {SUBSERVE}
GROUP BY g.NAME
