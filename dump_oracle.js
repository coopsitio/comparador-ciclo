// Ejecuta una query en UN ambiente (v7/v8) y vuelca el resultado a CSV, con Node.
// Se usa cuando el antivirus mata a python.exe (node.exe no lo caza). Modo thin
// (sirve para V8 = 19c; V7 = 11.2 no soporta thin -> usar dump_oracle.py para V7).
//
// oracledb se resuelve desde ORACLE_NODE_ORACLEDB (.env) si esta definido; si no,
// se intenta require('oracledb').  Si se pasan --esquema/--pefa, reemplaza
// {ESQUEMA} y {PEFA} en la plantilla.
//
// Uso:  node dump_oracle.js <v7|v8> <query.sql> <salida.csv> [--esquema CHILQUIN] [--pefa 15492]
const fs = require("fs");

function loadEnv() {
  const env = {};
  for (const line of fs.readFileSync(".env", "utf8").split(/\r?\n/)) {
    const s = line.trim();
    if (!s || s.startsWith("#")) continue;
    const i = s.indexOf("=");
    if (i > 0) env[s.slice(0, i).trim()] = s.slice(i + 1).trim();
  }
  return env;
}

function arg(name) {
  const i = process.argv.indexOf(name);
  return i > -1 ? process.argv[i + 1] : null;
}

function csvCell(v) {
  if (v === null || v === undefined) return "";
  const s = String(v);
  return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
}

(async () => {
  const env = loadEnv();
  // Normaliza backslashes -> '/' para que require resuelva la ruta exacta en Windows.
  const oraPath = (env.ORACLE_NODE_ORACLEDB || "oracledb").replace(/\\/g, "/");
  const oracledb = require(oraPath);
  // Modo thick (Instant Client): necesario para V7 (Oracle 11.2). Sirve tambien
  // para V8 (19c). node.exe no lo caza el antivirus (a diferencia de python.exe).
  if (env.ORACLE_CLIENT_LIB) {
    try {
      oracledb.initOracleClient({ libDir: env.ORACLE_CLIENT_LIB.replace(/\\/g, "/") });
    } catch (e) {
      if (!/already been initialized/i.test(e.message)) throw e;
    }
  }
  const [lado, sqlPath, csvPath] = process.argv.slice(2);
  const pref = "ORACLE_" + lado.toUpperCase() + "_";
  let sql = fs.readFileSync(sqlPath, "utf8");
  const esq = arg("--esquema"), pefa = arg("--pefa");
  if (esq) sql = sql.split("{ESQUEMA}").join(esq);
  if (pefa) sql = sql.split("{PEFA}").join(pefa);
  // Parametros POR AMBIENTE: cualquier {NOMBRE} se reemplaza por ORACLE_<lado>_<NOMBRE>
  // del .env. Ej.: {SUBSERVE} -> ORACLE_V7_SUBSERVE (=2) / ORACLE_V8_SUBSERVE (=47).
  sql = sql.replace(/\{([A-Z_][A-Z0-9_]*)\}/g, (m, name) => {
    const v = env[pref + name];
    return v !== undefined ? v : m;
  });
  sql = sql.replace(/;\s*$/, "");

  let con;
  try {
    con = await oracledb.getConnection({
      user: env[pref + "USER"],
      password: env[pref + "PASSWORD"],
      connectString: env[pref + "DSN"],
    });
    con.callTimeout = 120000;
    const r = await con.execute(sql, [], { outFormat: oracledb.OUT_FORMAT_ARRAY });
    const cols = r.metaData.map((m) => m.name.toLowerCase());
    const lines = [cols.join(",")];
    for (const row of r.rows) lines.push(row.map(csvCell).join(","));
    fs.writeFileSync(csvPath, lines.join("\n") + "\n", "utf8");
    console.log(`${lado} (node): ${r.rows.length} filas -> ${csvPath}`);
  } catch (e) {
    console.error(`ERROR ${lado} (node):`, e.message);
    process.exit(1);
  } finally {
    if (con) await con.close();
  }
})();
