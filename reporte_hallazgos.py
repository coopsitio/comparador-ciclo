"""
reporte_hallazgos.py - Documento de HALLAZGOS (para reportar) de una revision.

Lee los pares v7_*.csv / v8_*.csv de local/suite_<pefa>/, y arma un HTML presentable:
  - Resumen ejecutivo (una fila por dimension: totales V7/V8, ratio, # diferencias,
    severidad y hallazgo en lenguaje claro).
  - Detalle por dimension (top diferencias).
  - Veredictos del verificador multiagente, si existe local/suite_<pefa>/veredictos_<pefa>.json
    ({ "clave_dimension": {"veredicto": "...", "detalle": "..."} }).

Uso:  python reporte_hallazgos.py --pefa 15281
"""
import argparse
import csv
import glob
import json
import os
import html

UMBRAL_RATIO = 1.05  # >5% de diferencia en el total se marca


def cargar(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def clave(r):
    return (r.get("empresa", ""), r.get("cuenta", ""), r.get("concepto", ""))


def analizar(v7_rows, v8_rows):
    v7 = {clave(r): num(r.get("monto")) for r in v7_rows}
    v8 = {clave(r): num(r.get("monto")) for r in v8_rows}
    tot7 = sum(x for x in v7.values() if x)
    tot8 = sum(x for x in v8.values() if x)
    difs = []
    for k in set(v7) | set(v8):
        a, b = v7.get(k), v8.get(k)
        if a == b:
            continue
        delta = (b or 0) - (a or 0)
        difs.append({"k": k, "v7": a, "v8": b, "delta": delta,
                     "tipo": "solo V8" if a is None else "solo V7" if b is None else "distinto"})
    difs.sort(key=lambda d: abs(d["delta"]), reverse=True)
    solo7 = sum(1 for d in difs if d["tipo"] == "solo V7")
    solo8 = sum(1 for d in difs if d["tipo"] == "solo V8")
    return {"tot7": tot7, "tot8": tot8, "n": len(difs), "solo7": solo7,
            "solo8": solo8, "difs": difs}


def severidad(a):
    ratio = (a["tot8"] / a["tot7"]) if a["tot7"] else None
    if ratio and (ratio > 1.5 or ratio < 0.67):
        return "ALTA", ratio
    if a["n"] == 0:
        return "OK", ratio
    if ratio and abs(ratio - 1) > (UMBRAL_RATIO - 1):
        return "MEDIA", ratio
    return "BAJA", ratio


def fmt(v):
    return "(no existe)" if v is None else f"{v:,.0f}"


def nombre(base):
    p = base.split("_")
    if p and p[0].isdigit():
        p = p[1:]
    return " ".join(p).capitalize()


def hallazgo_texto(a, sev, ratio):
    if a["n"] == 0:
        return "Sin diferencias: V7 y V8 cuadran."
    partes = []
    if a["tot7"] and ratio:
        partes.append(f"Total V7 {a['tot7']:,.0f} vs V8 {a['tot8']:,.0f} (V8 = {ratio:.2f}x V7).")
    if a["solo7"] or a["solo8"]:
        partes.append(f"{a['solo7']} solo en V7, {a['solo8']} solo en V8.")
    top = a["difs"][0]
    et = " / ".join(x for x in top["k"][1:] if x)
    partes.append(f"Mayor brecha: {et} ({fmt(top['v7'])} -> {fmt(top['v8'])}).")
    return " ".join(partes)


CSS = """
body{font-family:Segoe UI,Arial,sans-serif;margin:24px;color:#1a1a1a}
h1{color:#1F4E78;margin-bottom:0} .sub{color:#666;margin-top:4px}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:14px}
th,td{border:1px solid #ccc;padding:6px 8px;text-align:left}
th{background:#1F4E78;color:#fff} tr:nth-child(even){background:#f4f7fb}
.ALTA{color:#b00020;font-weight:bold}.MEDIA{color:#b06f00;font-weight:bold}
.BAJA{color:#555}.OK{color:#2e7d32;font-weight:bold}
.ver{background:#eef6ee;border-left:4px solid #2e7d32;padding:8px 12px;margin:8px 0}
.card{border:1px solid #ddd;border-radius:6px;padding:12px 16px;margin:14px 0}
.num{text-align:right;font-variant-numeric:tabular-nums}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pefa", required=True)
    ap.add_argument("--empresa", default="CHILQUIN")
    args = ap.parse_args()
    raiz = os.path.dirname(os.path.abspath(__file__))
    carpeta = os.path.join(raiz, "local", f"suite_{args.pefa}")

    ver_path = os.path.join(carpeta, f"veredictos_{args.pefa}.json")
    veredictos = json.load(open(ver_path, encoding="utf-8")) if os.path.exists(ver_path) else {}

    dims = []
    for v7f in sorted(glob.glob(os.path.join(carpeta, "v7_*.csv"))):
        base = os.path.basename(v7f)[3:-4]
        v8f = os.path.join(carpeta, "v8_" + base + ".csv")
        if not os.path.exists(v8f):
            continue
        a = analizar(cargar(v7f), cargar(v8f))
        sev, ratio = severidad(a)
        dims.append({"base": base, "nombre": nombre(base), "a": a, "sev": sev,
                     "ratio": ratio, "texto": hallazgo_texto(a, sev, ratio)})

    orden = {"ALTA": 0, "MEDIA": 1, "BAJA": 2, "OK": 3}
    dims.sort(key=lambda d: orden.get(d["sev"], 9))

    h = [f"<style>{CSS}</style>",
         f"<h1>Reporte de hallazgos — Comparacion V7 vs V8</h1>",
         f"<div class='sub'>Empresa {html.escape(args.empresa)} · Ciclo (pefa) {args.pefa} · {len(dims)} dimensiones revisadas</div>",
         "<h2>Resumen ejecutivo</h2>",
         "<table><tr><th>Dimension</th><th>Severidad</th><th># dif.</th><th>Hallazgo</th></tr>"]
    for d in dims:
        h.append(f"<tr><td>{html.escape(d['nombre'])}</td>"
                 f"<td class='{d['sev']}'>{d['sev']}</td>"
                 f"<td class='num'>{d['a']['n']}</td>"
                 f"<td>{html.escape(d['texto'])}</td></tr>")
    h.append("</table>")

    for d in dims:
        if d["a"]["n"] == 0:
            continue
        h.append(f"<div class='card'><h3>{html.escape(d['nombre'])} "
                 f"<span class='{d['sev']}'>[{d['sev']}]</span></h3>")
        h.append(f"<p>{html.escape(d['texto'])}</p>")
        key = d["base"].split("_", 1)[-1] if d["base"][0].isdigit() else d["base"]
        v = veredictos.get(d["base"]) or veredictos.get(key)
        if v:
            h.append(f"<div class='ver'><b>Veredicto verificado ({html.escape(str(v.get('veredicto','')))}):</b> "
                     f"{html.escape(str(v.get('detalle','')))}</div>")
        h.append("<table><tr><th>empresa</th><th>cuenta</th><th>concepto</th>"
                 "<th class='num'>V7</th><th class='num'>V8</th><th class='num'>Delta</th><th>tipo</th></tr>")
        for dd in d["a"]["difs"][:15]:
            e, c, co = dd["k"]
            h.append(f"<tr><td>{html.escape(e)}</td><td>{html.escape(c)}</td><td>{html.escape(co)}</td>"
                     f"<td class='num'>{fmt(dd['v7'])}</td><td class='num'>{fmt(dd['v8'])}</td>"
                     f"<td class='num'>{fmt(dd['delta'])}</td><td>{dd['tipo']}</td></tr>")
        h.append("</table></div>")

    salida = os.path.join(carpeta, f"hallazgos_{args.pefa}.html")
    with open(salida, "w", encoding="utf-8") as f:
        f.write("\n".join(h))
    print(f"Documento de hallazgos: {os.path.relpath(salida, raiz)}")


if __name__ == "__main__":
    main()
