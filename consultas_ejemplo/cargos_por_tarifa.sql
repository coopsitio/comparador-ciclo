-- ============================================================
--  Plantilla: facturacion por TARIFA (plan comercial) x CONCEPTO de un ciclo.
--  La usa comparar_ciclo.py: reemplaza {ESQUEMA} y {PEFA} y la ejecuta en cada
--  ambiente (V7 y V8). Devuelve las 4 columnas del comparador:
--      empresa, cuenta (= tarifa), concepto, monto (valor neto DB-CR).
--
--  Criterios (los mismos de las queries de Analisis Conceptos por Tarifa):
--    CARGTIPR = 'A'  (facturacion recurrente del ciclo)
--    CARGSIGN IN ('CR','DB')  (solo signos de facturacion)
--  En V7 (Oracle 11.2) hay que prefijar TODAS las tablas con el esquema.
-- ============================================================
SELECT '{ESQUEMA}'                                    AS empresa,
       g.NAME                                         AS cuenta,     -- tarifa / plan
       c.CARGCONC                                     AS concepto,
       SUM(DECODE(c.CARGSIGN,'CR',-1,1) * c.CARGVALO) AS monto
FROM   {ESQUEMA}.CARGOS c
JOIN   {ESQUEMA}.CUENCOBR cu           ON cu.CUCOCODI = c.CARGCUCO
JOIN   {ESQUEMA}.CC_COMMERCIAL_PLAN g  ON g.COMMERCIAL_PLAN_ID = cu.CUCOPLSU
WHERE  c.CARGPEFA = {PEFA} AND c.CARGTIPR = 'A' AND c.CARGSIGN IN ('CR','DB')
GROUP BY g.NAME, c.CARGCONC
