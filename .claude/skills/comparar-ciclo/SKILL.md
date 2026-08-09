---
name: comparar-ciclo
description: >-
  Compara dos fuentes de datos de facturacion (V7 vs V8, o cualquier par de
  archivos CSV / consultas Oracle) por totales y por detalle de fila, y reporta
  las diferencias. Usar cuando el usuario quiera comparar dos versiones o fuentes
  de datos y encontrar que NO cuadra: cazar regresiones de una migracion,
  reconciliar un ciclo, o generar un reporte de diferencias (opcionalmente en Excel).
---

# Comparar ciclo (V7 vs V8)

Esta habilidad usa el CLI `comparador.py` de este repositorio para comparar dos
fuentes de datos y reportar las diferencias en dos niveles:

1. **Totales** por `empresa` + `concepto` (la foto grande: que no cuadra).
2. **Detalle** por `empresa` + `cuenta` + `concepto` (el porque: que fila cambio).

## Cuando usarla

- "Compara el ciclo de V7 con el de V8."
- "Que diferencias hay entre estos dos archivos / estas dos consultas?"
- "Genera un reporte de diferencias en Excel."
- Cualquier reconciliacion entre dos conjuntos que tengan las columnas
  `empresa, cuenta, concepto, monto`.

## Como ejecutarla

Las fuentes pueden ser archivos `.csv` locales o `.sql` (se ejecutan en Oracle).
Se decide por la extension.

1. Asegurar el entorno (una sola vez):

   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Comparar dos CSV:

   ```bash
   python comparador.py <fuente_v7.csv> <fuente_v8.csv>
   ```

3. Comparar generando ademas un Excel:

   ```bash
   python comparador.py <fuente_v7.csv> <fuente_v8.csv> --excel reportes/comparacion.xlsx
   ```

4. Comparar ejecutando consultas en Oracle. Requiere un `.env` local con las
   credenciales por ambiente (`ORACLE_V7_*` y `ORACLE_V8_*`) y, para V7 (Oracle 11.2),
   `ORACLE_CLIENT_LIB` apuntando a un Instant Client 19; ver `.env.example`. La
   posicion decide el ambiente: el primer argumento va a V7, el segundo a V8. Cada
   `.sql` debe devolver las columnas `empresa, cuenta, concepto, monto`:

   ```bash
   python comparador.py <consulta_v7.sql> <consulta_v8.sql>
   ```

## Como interpretar el resultado

La salida es una tabla Markdown por seccion. La columna `tipo` indica:

- **monto distinto** — la clave existe en ambas versiones pero el monto cambio.
- **solo en V7** — la fila esta en V7 y desaparecio en V8.
- **solo en V8** — la fila aparecio en V8 y no estaba en V7.

El programa termina con codigo de salida `1` si encontro diferencias y `0` si todo
cuadra (util para automatizar en CI).

## Reglas

- No exponer credenciales: las consultas Oracle leen del `.env` local (ignorado por git).
- Los datos de ejemplo (`datos_ejemplo/`) son ficticios; para uso real, apuntar a
  las fuentes correspondientes sin commitear datos sensibles.
