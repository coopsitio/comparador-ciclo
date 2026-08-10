-- DIMENSION 1: Facturacion por tarifa x concepto (solo utility electrico).
-- Detecta diferencias de MONTO facturado por plan y concepto entre V7 y V8.
-- {SUBSERVE} = servicio utility: 2 en V7, 47 en V8 (ORACLE_<lado>_SUBSERVE).
SELECT '{ESQUEMA}'                                    AS empresa,
       g.NAME                                         AS cuenta,     -- tarifa / plan
       c.CARGCONC                                     AS concepto,
       SUM(DECODE(c.CARGSIGN,'CR',-1,1) * c.CARGVALO) AS monto
FROM   {ESQUEMA}.CARGOS c
JOIN   {ESQUEMA}.CUENCOBR cu           ON cu.CUCOCODI = c.CARGCUCO
JOIN   {ESQUEMA}.CC_COMMERCIAL_PLAN g  ON g.COMMERCIAL_PLAN_ID = cu.CUCOPLSU
JOIN   {ESQUEMA}.SERVSUSC s            ON s.SESUNUSE = c.CARGNUSE
WHERE  c.CARGPEFA = {PEFA} AND c.CARGTIPR = 'A' AND c.CARGSIGN IN ('CR','DB')
  AND  s.SESUSERV = {SUBSERVE}
GROUP BY g.NAME, c.CARGCONC
