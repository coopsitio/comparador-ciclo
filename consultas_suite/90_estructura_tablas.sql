-- DIMENSION ESTRUCTURAL A: TABLAS del esquema y su tamano estimado (num_rows del
-- diccionario). Detecta tablas que existen en un ambiente y no en el otro, y
-- diferencias gruesas de volumen. No usa pefa (es metadata; consulta instantanea).
-- 'monto' = filas estimadas (segun estadisticas); tipo "solo en V7/V8" = tabla que
-- falta en el otro ambiente.
SELECT '{ESQUEMA}'      AS empresa,
       'TABLA'          AS cuenta,
       table_name       AS concepto,
       NVL(num_rows, 0) AS monto
FROM   all_tables
WHERE  owner = '{ESQUEMA}'
