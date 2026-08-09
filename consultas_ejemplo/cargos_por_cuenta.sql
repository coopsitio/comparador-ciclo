-- ============================================================
--  Ejemplo de query real de facturacion (CARGOS) para el comparador.
--  Devuelve las 4 columnas que el comparador espera:
--      empresa, cuenta, concepto, monto
--
--  Como se usa:
--    - Guarda tu version (con esquema, pefa y filtros reales) en la carpeta
--      local/ (que esta en .gitignore, para NO subir datos ni ids reales).
--    - Ejecuta:  python comparador.py local/v7.sql local/v8.sql
--      El primer archivo se ejecuta en V7 y el segundo en V8.
--
--  IMPORTANTE (rendimiento / antivirus):
--    Acota la query (pocas cuentas, o un solo concepto, o un rango) para que
--    corra en pocos segundos. Contra queries largas (varios segundos) el
--    antivirus puede matar el proceso de Python; para ciclos completos conviene
--    el patron asincrono / Node.
-- ============================================================

SELECT '<EMPRESA>'                                  AS empresa,   -- ej. 'CHILQUIN'
       CARGNUSE                                     AS cuenta,    -- servicio/producto
       CARGCONC                                     AS concepto,  -- codigo de concepto
       SUM(DECODE(CARGSIGN,'CR',-1,1) * CARGVALO)   AS monto      -- valor neto (DB - CR)
FROM   <ESQUEMA>.CARGOS                                           -- ej. CHILQUIN.CARGOS
WHERE  CARGPEFA = <PEFA>              -- periodo de facturacion (ciclo) a comparar
  AND  CARGTIPR = 'A'                 -- 'A' = facturacion recurrente del ciclo
  AND  CARGSIGN IN ('CR','DB')        -- solo signos de facturacion (no pagos/saldos)
  -- AND CARGNUSE IN (111111, 222222) -- acota a pocas cuentas para pruebas rapidas
GROUP BY CARGNUSE, CARGCONC
