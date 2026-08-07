"""
comparador.py - Comparador de Ciclo V7 vs V8

Compara el mismo dato calculado en dos versiones (V7 vs V8) en dos niveles:
  1. Totales : suma por (empresa, concepto).           -> la foto grande: que NO cuadra
  2. Detalle : monto por (empresa, cuenta, concepto).  -> el porque: que fila cambio

Uso:
    python comparador.py datos_ejemplo/v7.csv datos_ejemplo/v8.csv
"""

import argparse
import csv
import sys
from collections import defaultdict


def cargar_filas(ruta):
    """Lee un CSV y devuelve la lista de filas (cada fila es un dict)."""
    with open(ruta, newline="", encoding="utf-8") as archivo:
        return list(csv.DictReader(archivo))


def agrupar(filas, columnas_clave):
    """Suma el monto agrupando por las columnas indicadas.

    Devuelve un dict {clave: suma_del_monto}, donde la clave es una tupla
    con los valores de 'columnas_clave'. La misma funcion sirve para ambos niveles:
      - totales: columnas_clave = ("empresa", "concepto")
      - detalle: columnas_clave = ("empresa", "cuenta", "concepto")
    """
    acumulado = defaultdict(float)
    for fila in filas:
        clave = tuple(fila[col] for col in columnas_clave)
        acumulado[clave] += float(fila["monto"])
    return acumulado


def comparar(datos_v7, datos_v8):
    """Compara dos dicts {clave: monto} y devuelve las diferencias.

    Cada diferencia es (clave, monto_v7, monto_v8); None si falta en un lado.
    Es generica: no le importa si la clave es de totales o de detalle.
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
    """Imprime una seccion del reporte como tabla Markdown."""
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


def main():
    parser = argparse.ArgumentParser(
        description="Compara V7 vs V8 por totales y por detalle de fila."
    )
    parser.add_argument("archivo_v7", help="CSV con los datos de V7")
    parser.add_argument("archivo_v8", help="CSV con los datos de V8")
    args = parser.parse_args()

    filas_v7 = cargar_filas(args.archivo_v7)
    filas_v8 = cargar_filas(args.archivo_v8)

    # Nivel 1: totales por empresa + concepto (la foto grande).
    dif_totales = comparar(
        agrupar(filas_v7, ("empresa", "concepto")),
        agrupar(filas_v8, ("empresa", "concepto")),
    )
    imprimir_seccion(
        "Cuadre por totales (empresa / concepto)",
        ["empresa", "concepto"],
        dif_totales,
    )

    # Nivel 2: detalle por empresa + cuenta + concepto (el porque de cada diferencia).
    dif_detalle = comparar(
        agrupar(filas_v7, ("empresa", "cuenta", "concepto")),
        agrupar(filas_v8, ("empresa", "cuenta", "concepto")),
    )
    imprimir_seccion(
        "Detalle fila a fila (empresa / cuenta / concepto)",
        ["empresa", "cuenta", "concepto"],
        dif_detalle,
    )

    # Sale con 1 si hubo cualquier diferencia (util para automatizar con una GitHub Action).
    sys.exit(1 if (dif_totales or dif_detalle) else 0)


if __name__ == "__main__":
    main()
