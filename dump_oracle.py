"""Ejecuta una query en UN ambiente (v7/v8) y vuelca el resultado a CSV.

Motor Python (thick si hay ORACLE_CLIENT_LIB, necesario para V7 = Oracle 11.2).
Se lanza como PROCESO HOJA desde un .bat (no desde otro python): asi el antivirus
no mata al padre por la espera. Correr cada ambiente por separado tambien evita
la espera acumulada.

Si se pasan --esquema y --pefa, reemplaza {ESQUEMA} y {PEFA} en la plantilla.

Uso:  python dump_oracle.py <v7|v8> <query.sql> <salida.csv> [--esquema CHILQUIN] [--pefa 15492]
"""
import argparse
import os
import csv
import oracledb
from dotenv import load_dotenv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lado", choices=["v7", "v8"])
    ap.add_argument("query")
    ap.add_argument("csv_out")
    ap.add_argument("--esquema")
    ap.add_argument("--pefa")
    args = ap.parse_args()

    load_dotenv()
    lib = os.environ.get("ORACLE_CLIENT_LIB")
    if lib:
        oracledb.init_oracle_client(lib_dir=lib)  # modo thick (para V7 11.2)

    with open(args.query, encoding="utf-8") as f:
        sql = f.read()
    if args.esquema:
        sql = sql.replace("{ESQUEMA}", args.esquema)
    if args.pefa:
        sql = sql.replace("{PEFA}", str(args.pefa))
    sql = sql.rstrip().rstrip(";")

    pref = f"ORACLE_{args.lado.upper()}_"
    con = oracledb.connect(user=os.environ[pref + "USER"],
                           password=os.environ[pref + "PASSWORD"],
                           dsn=os.environ[pref + "DSN"])
    con.call_timeout = 120000
    cur = con.cursor()
    cur.execute(sql)
    cols = [d[0].lower() for d in cur.description]
    rows = cur.fetchall()
    with open(args.csv_out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    print(f"{args.lado} (python): {len(rows)} filas -> {args.csv_out}")
    cur.close()
    con.close()


if __name__ == "__main__":
    main()
