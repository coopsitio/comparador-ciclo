-- DIMENSION 7: Distribucion de servicios (utility) por ESTADO DE CORTE, con nombre.
-- SERVSUSC.SESUESCO -> ESTACORT.ESCOCODI (ESCODESC = descripcion). Detecta si el
-- universo por estado (conexion, suspension, retiro, etc.) difiere entre V7 y V8.
SELECT '{ESQUEMA}'                                        AS empresa,
       'ESTADO_CORTE'                                     AS cuenta,
       LPAD(s.SESUESCO, 3, '0') || ' - ' || e.ESCODESC    AS concepto,   -- codigo - nombre
       COUNT(*)                                            AS monto
FROM   {ESQUEMA}.SERVSUSC s
JOIN   {ESQUEMA}.ESTACORT e  ON e.ESCOCODI = s.SESUESCO
WHERE  s.SESUSERV = {SUBSERVE}
GROUP BY s.SESUESCO, e.ESCODESC
