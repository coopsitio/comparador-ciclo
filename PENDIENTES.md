# Estado y pendientes — comparador-ciclo

Checkpoint para retomar el proyecto en una sesion nueva.

## Que hace hoy la herramienta

Motor de **conciliacion de migracion V7 (produccion) vs V8 (pruebas)** de OSF.

- `COMPARAR_CICLO.bat <pefa> [empresa]` — compara un ciclo por tarifa x concepto.
- `COMPARAR_SUITE.bat <pefa> [empresa]` — **revision integral**: corre las 12 plantillas
  de `consultas_suite/` (facturacion, productos, cargos fijos, cuentas, consumo por
  tarifa/tipo/producto, **consumo diario normalizado kWh/dia**, estados de corte, y
  estructura de **tablas** y **columnas**), y deja en `local/suite_<pefa>/`:
  - `resumen_<pefa>.xlsx` — para analizar (una hoja por dimension, con Delta y %).
  - `hallazgos_<pefa>.html` — para **reportar** (panel de control con semaforo +
    resumen ejecutivo por severidad + veredictos verificados). Imprimir a PDF.

### Como corre (importante)
- Los volcados usan **Node en modo thick** (`node.exe` esquiva el antivirus que mata
  a python.exe; conecta a V7=11.2 y V8=19c). El compare y los reportes, Python.
- Credenciales y parametros por-ambiente en `.env` (gitignored). Ver `.env.example`.
  Clave: `{SUBSERVE}` = servicio utility (V7=2, V8=47); Instant Client 19; ruta al
  `oracledb` de Node. Queries reales, CSV y salidas viven en `local/` (gitignored).

## Hallazgos vigentes (ciclo 15281)
- Universo cuadra (~±1-2%): productos, cargos fijos, cuentas de cobro.
- Consumo/facturacion divergen: crudo +390% / +971%, **pero normalizado por dia baja
  a -19%** => la causa es la **ventana temporal** (V8 acumula ~222 dias por producto
  vs ~33 en V7; lo carga SFINTERFAZ/COSSFUNC=751). Verificado con investigacion
  multiagente. Residual ~19% por revisar.
- Estructura: V8 tiene ~817 tablas nuevas (modulos AB_*) y 10 columnas core nuevas.

## Pendientes / roadmap (prioridad)
1. Investigar el **residual ~19%** del consumo diario normalizado (composicion de
   productos por plan, dias atipicos).
2. **Tendencia entre ciclos**: guardar el resumen de cada corrida y graficar el
   "% que cuadra" ciclo a ciclo (mostrar convergencia de la migracion).
3. **Las 5 empresas en una corrida** (loop CHILQUIN/LITORAL/ENERQUIN/... + consolidado).
4. **Bitacora de hallazgos con estado** (abierto/explicado/aceptado) que se arrastre
   entre ciclos, para no re-explicar lo mismo cada mes.
5. Mas dimensiones: descuentos, medido-vs-facturado por producto, potencia/demanda,
   morosidad.
6. **Verificacion multiagente** como paso estandar (hoy es a pedido, via workflow).
7. Operacion remota (disparar desde el celular con el patron whatsapp-bridge/cloudflared).

## Como retomar
Abrir Claude Code en `D:\Code\comparador-ciclo` y decir, por ejemplo:
"retomamos el comparador, sigamos con la tendencia entre ciclos" o
"compara el ciclo <pefa>". El estado detallado esta en la memoria del proyecto.
