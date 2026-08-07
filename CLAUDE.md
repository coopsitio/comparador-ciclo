# CLAUDE.md

Instrucciones para Claude Code al trabajar en este repositorio.

## Qué es este proyecto

`comparador-ciclo` es un CLI en Python que compara el mismo dato calculado en dos
versiones de un sistema de facturacion (V7 vs V8) y reporta las diferencias, en dos
niveles: **totales** (empresa/concepto) y **detalle** fila a fila
(empresa/cuenta/concepto). Nacio como proyecto de laboratorio del curso
Claude Code + Claude Design (UAI).

## Reglas importantes

- **Sin datos ni credenciales reales.** Este repo es publico. Los datos de ejemplo
  (`datos_ejemplo/`) son 100% ficticios. Nunca commitear datos de produccion.
- **Credenciales solo en `.env` local**, que esta en `.gitignore` y NO se sube.
  Ver `.env.example` como plantilla.
- **Lo generado no se versiona**: entorno virtual (`.venv/`), reportes (`reportes/`,
  `*.xlsx`) estan ignorados. Se versiona el codigo y la "receta" (`requirements.txt`).
- **Idioma:** codigo, comentarios y mensajes en espanol.

## Como correr

```bash
# 1. Crear e iniciar el entorno virtual (una sola vez)
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar: solo consola
python comparador.py datos_ejemplo/v7.csv datos_ejemplo/v8.csv

# 3b. Ejecutar: ademas generar Excel
python comparador.py datos_ejemplo/v7.csv datos_ejemplo/v8.csv --excel reportes/comparacion.xlsx
```

El programa termina con codigo de salida `1` si encontro diferencias, `0` si todo
cuadra (util para automatizar con una GitHub Action).

## Estructura

- `comparador.py` — el CLI. Funciones clave:
  - `cargar_filas(ruta)` — lee un CSV a lista de dicts.
  - `agrupar(filas, columnas_clave)` — suma monto agrupando por columnas configurables
    (equivale a un GROUP BY parametrizable). Sirve para totales y para detalle.
  - `comparar(v7, v8)` — diffs generico entre dos dicts {clave: monto}.
  - `escribir_excel(ruta, secciones)` — genera el .xlsx (import perezoso de openpyxl).
- `datos_ejemplo/` — CSV ficticios (v7.csv, v8.csv) con diferencias sembradas a proposito.
- `requirements.txt` — dependencias (openpyxl).
- `.env.example` — plantilla de conexion (para el modo Oracle, aun no implementado).

## Convenciones de codigo

- Python estandar, funciones pequenas y con docstring.
- Preferir reutilizar funciones existentes antes que duplicar (principio DRY):
  `agrupar` y `comparar` son genericas a proposito.
- Mantener el modo consola sin dependencias externas (imports de librerias pesadas
  como openpyxl van "perezosos", dentro de la funcion que los usa).

## Flujo de trabajo (Git)

- No trabajar directo sobre `main`. Crear una rama `feature/...` por cada cambio.
- Un commit = un cambio con sentido, con mensaje en imperativo.
- Integrar a `main` via Pull Request.

## Pendiente / roadmap

- Modo Oracle: leer de la base via `.env` en vez de CSV (python-oracledb).
- Empaquetar el comparador como Skill reutilizable.
- GitHub Action que corra el comparador en cada PR.
