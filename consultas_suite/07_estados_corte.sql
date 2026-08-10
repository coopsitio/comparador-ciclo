-- DIMENSION 7: Distribucion de servicios (utility) por ESTADO DE CORTE.
-- SERVSUSC.SESUESCO -> ESTACORT.ESCOCODI (ESCODESC = descripcion). Detecta si el
-- universo por estado (conexion, suspension, retiro, etc.) difiere entre V7 y V8.
SELECT '{ESQUEMA}'          AS empresa,
       'ESTADO_CORTE'       AS cuenta,
       s.SESUESCO           AS concepto,             -- codigo de estado de corte
       COUNT(*)             AS monto
FROM   {ESQUEMA}.SERVSUSC s
WHERE  s.SESUSERV = {SUBSERVE}
GROUP BY s.SESUESCO
