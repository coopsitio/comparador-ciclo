# comparador-ciclo

CLI en Python que compara el **mismo dato calculado en dos versiones** (V7 vs V8)
y reporta **donde dejaron de cuadrar**. Pensado para cazar regresiones durante una
migracion de sistema de facturacion.

> Proyecto del curso **Claude Code + Claude Design (UAI)**.
> Publico y reproducible: incluye datos de ejemplo **100% ficticios**.
> No contiene datos ni credenciales reales de ninguna empresa.

## Que compara

En dos niveles:

1. **Cuadre por totales** — suma por `empresa` + `concepto` en V7 vs V8, y marca las
   diferencias. Es la foto grande para detectar el problema rapido.
2. **Detalle fila a fila** *(siguiente etapa)* — para lo que no cuadra, compara
   registro por registro usando una llave e indica: filas solo en V7, solo en V8,
   y filas en ambas con valores distintos.

## Fuentes de datos

La herramienta es **agnostica de la fuente**:

- **Modo ejemplo (CSV):** usa los archivos de `datos_ejemplo/` (ficticios). No
  necesita nada mas. Es el modo con el que se prueba este repo.
- **Modo Oracle** *(uso local):* se conecta a una base real leyendo las credenciales
  desde un archivo `.env` local **que nunca se sube** (esta en `.gitignore`).
  Ver `.env.example` como plantilla.

## Datos de ejemplo

`datos_ejemplo/v7.csv` y `datos_ejemplo/v8.csv` traen diferencias a proposito para
que el comparador tenga algo que encontrar:

- una cuenta que esta **solo en V7** (se perdio en V8),
- una cuenta que esta **solo en V8** (aparecio de mas),
- un concepto con **monto distinto** entre V7 y V8.

## Uso

```bash
# Comparar dos CSV locales (datos de ejemplo)
python comparador.py datos_ejemplo/v7.csv datos_ejemplo/v8.csv

# Ademas, generar un Excel
python comparador.py datos_ejemplo/v7.csv datos_ejemplo/v8.csv --excel reportes/comparacion.xlsx

# Comparar ejecutando consultas en Oracle (uso local, requiere .env)
python comparador.py consulta_v7.sql consulta_v8.sql
```

La fuente se decide por la extension: `.csv` lee un archivo local; `.sql` ejecuta
ese SELECT en Oracle (que debe devolver las columnas empresa, cuenta, concepto, monto).

## Estado

Funcional: comparacion por totales y detalle, reporte Excel opcional, y lectura
desde CSV o desde Oracle (via .env local).
