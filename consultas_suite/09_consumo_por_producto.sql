-- DIMENSION 9: Consumo MEDIDO (kWh activa, tipo 103) por PRODUCTO (utility).
-- Comparacion a nivel de producto/servicio (CARGNUSE = SERVSUSC.SESUNUSE): detecta
-- QUE productos tienen consumo distinto entre V7 y V8, incluso cuando el total por
-- tarifa cuadra (diferencias individuales que se compensan). Puede devolver muchas
-- filas; el reporte consolidado muestra las de mayor diferencia.
SELECT '{ESQUEMA}'         AS empresa,
       cs.COSSSESU         AS cuenta,          -- producto / servicio (cargnuse)
       'KWH_103'           AS concepto,
       SUM(cs.COSSCOCA)    AS monto
FROM   {ESQUEMA}.CONSSESU cs
JOIN   {ESQUEMA}.SERVSUSC s  ON s.SESUNUSE = cs.COSSSESU
WHERE  cs.COSSPEFA = {PEFA} AND cs.COSSMECC = 4 AND cs.COSSTCON = 103
  AND  s.SESUSERV = {SUBSERVE}
GROUP BY cs.COSSSESU
