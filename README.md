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
El primer argumento se ejecuta en V7 y el segundo en V8 (credenciales por ambiente
en el `.env`; ver `.env.example`).

## Comparar V7 vs V8 con queries reales

1. Escribe tu consulta (una por ambiente) tomando como base
   `consultas_ejemplo/cargos_por_cuenta.sql`. Debe devolver
   `empresa, cuenta, concepto, monto`.
2. Guardala en la carpeta `local/` (esta en `.gitignore`: no se suben ids ni datos
   reales, y el repo sigue siendo publico).
3. Ejecuta:

   ```bash
   python comparador.py local/v7.sql local/v8.sql --excel local/comparacion.xlsx
   ```

**Rendimiento / antivirus:** acota la query (pocas cuentas, un concepto, un rango)
para que corra en pocos segundos. Contra queries largas el antivirus puede matar
el proceso de Python; para ciclos completos conviene el patron asincrono / Node.

**Esquema:** V7 y V8 usan un esquema por empresa (ej. `CHILQUIN`). En la query,
prefija la tabla (`CHILQUIN.CARGOS`) o fija `ALTER SESSION SET CURRENT_SCHEMA`.

## Comparar un CICLO COMPLETO con un comando (COMPARAR_CICLO.bat)

Para comparar un ciclo entero (por tarifa x concepto) entre V7 y V8 con **los mismos
criterios**, en un solo paso:

```bat
COMPARAR_CICLO.bat 15492
COMPARAR_CICLO.bat 15281 CHILQUIN
```

Hace: genera la query desde `consultas_ejemplo/cargos_por_tarifa.sql` (reemplaza
esquema y pefa), vuelca cada ambiente a CSV y genera `local/comparacion_<pefa>.xlsx`.

**Por que un `.bat` y Node (esquiva el antivirus):** en este equipo el antivirus mata
`python.exe` cuando queda esperando una query Oracle larga (aunque la espere un
proceso hijo). Solucion: el orquestador es un `.bat` (`cmd.exe` puede esperar sin
morir) y los volcados usan **Node** (`node.exe` no lo caza; en modo thick conecta a
V7=11.2 y a V8=19c). La comparacion de los dos CSV la hace Python (instantanea, sin BD).

Requiere en el `.env`: credenciales `ORACLE_V7_*` / `ORACLE_V8_*`, `ORACLE_CLIENT_LIB`
(Instant Client 19, para el modo thick) y `ORACLE_NODE_ORACLEDB` (ruta al modulo
`oracledb` de Node). Ver `.env.example`.

## Estado

Funcional y probado contra V7 (produccion) y V8 (pruebas) con una query real de
CARGOS: comparacion por totales y detalle, reporte Excel opcional, y lectura desde
CSV o desde Oracle (via `.env` local, credenciales por ambiente).
