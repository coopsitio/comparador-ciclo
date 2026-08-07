"""
comparador.py - Comparador de Ciclo V7 vs V8 (nivel totales)

Lee dos archivos CSV con columnas: empresa, cuenta, concepto, monto.
Suma el monto por (empresa, concepto) en cada version y reporta las diferencias.

Uso:
    python comparador.py datos_ejemplo/v7.csv datos_ejemplo/v8.csv
"""

import argparse
import csv
import sys
from collections import defaultdict


def cargar_totales(ruta):
    """Lee un CSV y devuelve un dict {(empresa, concepto): suma_del_monto}."""
    totales = defaultdict(float)
    with open(ruta, newline="", encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            clave = (fila["empresa"], fila["concepto"])
            totales[clave] += float(fila["monto"])
    return totales


def comparar(totales_v7, totales_v8):
    """Compara dos dicts de totales y devuelve las diferencias.

    Cada diferencia es una tupla: (clave, monto_v7, monto_v8).
    Si una clave existe en una sola version, el monto de la otra es None.
    """
    todas_las_claves = sorted(set(totales_v7) | set(totales_v8))
    diferencias = []
    for clave in todas_las_claves:
        monto_v7 = totales_v7.get(clave)
        monto_v8 = totales_v8.get(clave)
        if monto_v7 != monto_v8:
            diferencias.append((clave, monto_v7, monto_v8))
    return diferencias


def formatear_monto(valor):
    """Formatea un monto; None se muestra como '(no existe)'."""
    if valor is None:
        return "(no existe)"
    return f"{valor:,.0f}"


def imprimir_reporte(diferencias):
    """Imprime el resultado en formato Markdown (legible en consola y en un PR)."""
    if not diferencias:
        print("OK: V7 y V8 cuadran en todos los totales por empresa/concepto.")
        return

    print(f"Se encontraron {len(diferencias)} diferencia(s):\n")
    print("| empresa | concepto | total V7 | total V8 | tipo |")
    print("|---|---|---|---|---|")
    for (empresa, concepto), monto_v7, monto_v8 in diferencias:
        if monto_v7 is None:
            tipo = "solo en V8"
        elif monto_v8 is None:
            tipo = "solo en V7"
        else:
            tipo = "monto distinto"
        print(
            f"| {empresa} | {concepto} | "
            f"{formatear_monto(monto_v7)} | {formatear_monto(monto_v8)} | {tipo} |"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Compara totales por empresa/concepto entre V7 y V8."
    )
    parser.add_argument("archivo_v7", help="CSV con los datos de V7")
    parser.add_argument("archivo_v8", help="CSV con los datos de V8")
    args = parser.parse_args()

    totales_v7 = cargar_totales(args.archivo_v7)
    totales_v8 = cargar_totales(args.archivo_v8)
    diferencias = comparar(totales_v7, totales_v8)
    imprimir_reporte(diferencias)

    # Codigo de salida: 0 si todo cuadra, 1 si hay diferencias.
    # Mas adelante esto permite que una GitHub Action marque el PR verde/rojo solo.
    sys.exit(0 if not diferencias else 1)


if __name__ == "__main__":
    main()
