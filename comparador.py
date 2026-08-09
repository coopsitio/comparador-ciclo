"""
comparador.py - Comparador de Ciclo V7 vs V8

Compara el mismo dato calculado en dos versiones (V7 vs V8) en dos niveles:
  1. Totales : suma por (empresa, concepto).           -> la foto grande: que NO cuadra
  2. Detalle : monto por (empresa, cuenta, concepto).  -> el porque: que fila cambio

Uso:
    python comparador.py datos_ejemplo/v7.csv datos_ejemplo/v8.csv
    python comparador.py datos_ejemplo/v7.csv datos_ejemplo/v8.csv --excel reportes/comparacion.xlsx

Las fuentes pueden ser archivos .csv (locales) o .sql (se ejecutan en Oracle,
leyendo las credenciales desde un archivo .env local; ver .env.example):

    python comparador.py consulta_v7.sql consulta_v8.sql
"""

import argparse
import csv
import os
import sys
from collections import defaultdict


def cargar_filas(ruta):
    """Lee un CSV y devuelve la lista de filas (cada fila es un dict)."""
    with open(ruta, newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


_cliente_oracle_iniciado = False


def _asegurar_cliente_oracle():
    """Inicia el modo 'thick' (Instant Client) si ORACLE_CLIENT_LIB esta definido.

    Es necesario para conectarse a V7 (Oracle 11.2), que el modo 'thin' NO soporta
    (da DPY-3010). El Instant Client 19 sirve para ambos: V7 (11.2) y V8 (19c).
    Se llama antes de cualquier conexion y solo se inicia una vez por proceso.
    """
    global _cliente_oracle_iniciado
    if _cliente_oracle_iniciado:
        return
    import oracledb

    lib = os.environ.get("ORACLE_CLIENT_LIB")
    if lib:
        oracledb.init_oracle_client(lib_dir=lib)
    _cliente_oracle_iniciado = True


def cargar_desde_oracle(sql, lado):
    """Ejecuta un SELECT en la base del ambiente indicado ('v7' o 'v8').

    El SELECT debe devolver las columnas: empresa, cuenta, concepto, monto.
    Las credenciales se leen del .env, con prefijo segun el ambiente:
      ORACLE_V7_USER / ORACLE_V7_PASSWORD / ORACLE_V7_DSN   (produccion)
      ORACLE_V8_USER / ORACLE_V8_PASSWORD / ORACLE_V8_DSN   (pruebas)
    (NUNCA en el codigo ni en el repo; el .env esta en .gitignore.)
    """
    # Imports perezosos: estas librerias solo hacen falta si se usa una fuente .sql.
    import oracledb
    from dotenv import load_dotenv

    load_dotenv()               # carga las variables del .env al entorno
    _asegurar_cliente_oracle()  # modo thick si hace falta (para V7 11.2)

    prefijo = f"ORACLE_{lado.upper()}_"
    usuario = os.environ[prefijo + "USER"]
    clave = os.environ[prefijo + "PASSWORD"]
    dsn = os.environ[prefijo + "DSN"]

    with oracledb.connect(user=usuario, password=clave, dsn=dsn) as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(sql)
            columnas = [descripcion[0].lower() for descripcion in cursor.description]
            return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]


def cargar_fuente(ruta, lado):
    """Carga una fuente de datos decidiendo por su extension:
      - .sql -> ejecuta el SELECT en Oracle del ambiente 'lado' ('v7' o 'v8')
      - cualquier otra (.csv) -> lee el archivo local
    """
    if ruta.lower().endswith(".sql"):
        with open(ruta, encoding="utf-8") as archivo:
            return cargar_desde_oracle(archivo.read(), lado)
    return cargar_filas(ruta)


def agrupar(filas, columnas_clave):
    """Suma el monto agrupando por las columnas indicadas.

    Devuelve un dict {clave: suma_del_monto}. La misma funcion sirve para ambos niveles:
      - totales: columnas_clave = ("empresa", "concepto")
      - detalle: columnas_clave = ("empresa", "cuenta", "concepto")
    """
    acumulado = defaultdict(float)
    for fila in filas:
        clave = tuple(str(fila[col]) for col in columnas_clave)
        acumulado[clave] += float(fila["monto"])
    return acumulado


def comparar(datos_v7, datos_v8):
    """Compara dos dicts {clave: monto} y devuelve las diferencias.

    Cada diferencia es (clave, monto_v7, monto_v8); None si falta en un lado.
    """
    diferencias = []
    for clave in sorted(set(datos_v7) | set(datos_v8)):
        monto_v7 = datos_v7.get(clave)
        monto_v8 = datos_v8.get(clave)
        if monto_v7 != monto_v8:
            diferencias.append((clave, monto_v7, monto_v8))
    return diferencias


def tipo_diferencia(monto_v7, monto_v8):
    """Clasifica una diferencia segun en que version existe."""
    if monto_v7 is None:
        return "solo en V8"
    if monto_v8 is None:
        return "solo en V7"
    return "monto distinto"


def formatear_monto(valor):
    """Formatea un monto; None se muestra como '(no existe)'."""
    return "(no existe)" if valor is None else f"{valor:,.0f}"


def imprimir_seccion(titulo, columnas_clave, diferencias):
    """Imprime una seccion del reporte como tabla Markdown en la consola."""
    print(f"\n## {titulo}")
    if not diferencias:
        print("OK: sin diferencias.")
        return

    print(f"\nSe encontraron {len(diferencias)} diferencia(s):\n")
    print("| " + " | ".join(columnas_clave) + " | V7 | V8 | tipo |")
    print("|" + "---|" * (len(columnas_clave) + 3))
    for clave, monto_v7, monto_v8 in diferencias:
        print(
            "| " + " | ".join(clave) + " | "
            f"{formatear_monto(monto_v7)} | {formatear_monto(monto_v8)} | "
            f"{tipo_diferencia(monto_v7, monto_v8)} |"
        )


def escribir_excel(ruta_salida, secciones):
    """Guarda el reporte en un Excel, con una hoja por seccion.

    'secciones' es la lista de dicts que arma main(): cada uno trae el nombre de
    la hoja, las columnas clave y las diferencias.
    """
    # Import perezoso: openpyxl solo hace falta si el usuario pidio --excel.
    # Asi el modo consola sigue funcionando sin instalar nada.
    from openpyxl import Workbook

    libro = Workbook()
    libro.remove(libro.active)  # quita la hoja vacia que viene por defecto
    for seccion in secciones:
        hoja = libro.create_sheet(title=seccion["hoja"])
        hoja.append(list(seccion["columnas_clave"]) + ["V7", "V8", "tipo"])
        for clave, monto_v7, monto_v8 in seccion["diferencias"]:
            hoja.append(
                list(clave) + [monto_v7, monto_v8, tipo_diferencia(monto_v7, monto_v8)]
            )

    carpeta = os.path.dirname(ruta_salida)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)  # crea la carpeta de salida si no existe
    libro.save(ruta_salida)
    print(f"\nReporte Excel guardado en: {ruta_salida}")


def main():
    parser = argparse.ArgumentParser(
        description="Compara V7 vs V8 por totales y por detalle de fila."
    )
    parser.add_argument("archivo_v7", help="Fuente V7: archivo .csv local o .sql (Oracle)")
    parser.add_argument("archivo_v8", help="Fuente V8: archivo .csv local o .sql (Oracle)")
    parser.add_argument(
        "--excel",
        metavar="RUTA",
        help="Ademas del reporte en consola, guarda un Excel en la ruta indicada",
    )
    args = parser.parse_args()

    filas_v7 = cargar_fuente(args.archivo_v7, "v7")
    filas_v8 = cargar_fuente(args.archivo_v8, "v8")

    # Cada seccion define su nivel de comparacion en un solo lugar.
    secciones = [
        {
            "titulo": "Cuadre por totales (empresa / concepto)",
            "hoja": "Totales",
            "columnas_clave": ["empresa", "concepto"],
            "diferencias": comparar(
                agrupar(filas_v7, ("empresa", "concepto")),
                agrupar(filas_v8, ("empresa", "concepto")),
            ),
        },
        {
            "titulo": "Detalle fila a fila (empresa / cuenta / concepto)",
            "hoja": "Detalle",
            "columnas_clave": ["empresa", "cuenta", "concepto"],
            "diferencias": comparar(
                agrupar(filas_v7, ("empresa", "cuenta", "concepto")),
                agrupar(filas_v8, ("empresa", "cuenta", "concepto")),
            ),
        },
    ]

    for seccion in secciones:
        imprimir_seccion(seccion["titulo"], seccion["columnas_clave"], seccion["diferencias"])

    if args.excel:
        escribir_excel(args.excel, secciones)

    # Sale con 1 si hubo cualquier diferencia (util para automatizar con una GitHub Action).
    hay_diferencias = any(seccion["diferencias"] for seccion in secciones)
    sys.exit(1 if hay_diferencias else 0)


if __name__ == "__main__":
    main()
