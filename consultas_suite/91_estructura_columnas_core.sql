-- DIMENSION ESTRUCTURAL B: COLUMNAS de las tablas CORE (posicion column_id).
-- Detecta columnas que se AGREGARON o QUITARON entre V7 y V8 ("solo en V7/V8")
-- y columnas que CAMBIARON de posicion ("monto distinto"). Metadata (instantaneo).
-- 'cuenta' = tabla ; 'concepto' = columna ; 'monto' = column_id (posicion).
SELECT '{ESQUEMA}'   AS empresa,
       table_name    AS cuenta,
       column_name   AS concepto,
       column_id     AS monto
FROM   all_tab_columns
WHERE  owner = '{ESQUEMA}'
  AND  table_name IN ('CARGOS','CONSSESU','SERVSUSC','CUENCOBR','FACTURA',
                      'PR_PRODUCT','CC_COMMERCIAL_PLAN','CONCEPTO','PERIFACT','ESTACORT')
