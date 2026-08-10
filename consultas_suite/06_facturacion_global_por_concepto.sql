-- DIMENSION 6: Facturacion GLOBAL por concepto (utility), sin abrir por tarifa.
-- Es el "cuadre grande" del ciclo: total facturado de cada concepto en V7 vs V8.
SELECT '{ESQUEMA}'                                    AS empresa,
       'GLOBAL'                                       AS cuenta,
       c.CARGCONC                                     AS concepto,
       SUM(DECODE(c.CARGSIGN,'CR',-1,1) * c.CARGVALO) AS monto
FROM   {ESQUEMA}.CARGOS c
JOIN   {ESQUEMA}.SERVSUSC s  ON s.SESUNUSE = c.CARGNUSE
WHERE  c.CARGPEFA = {PEFA} AND c.CARGTIPR = 'A' AND c.CARGSIGN IN ('CR','DB')
  AND  s.SESUSERV = {SUBSERVE}
GROUP BY c.CARGCONC
