@echo off
REM ============================================================
REM  Compara un ciclo (pefa) entre V7 y V8, de punta a punta.
REM  Uso:  COMPARAR_CICLO.bat <pefa> [esquema]
REM        COMPARAR_CICLO.bat 15492
REM        COMPARAR_CICLO.bat 15281 CHILQUIN
REM
REM  El orquestador es un .bat (NO python) a proposito: cmd.exe puede ESPERAR a
REM  los procesos hoja sin que el antivirus lo mate. Los volcados usan NODE
REM  (node.exe NO lo caza el antivirus; en modo thick conecta a V7=11.2 y a
REM  V8=19c). Luego se comparan los dos CSV con python (instantaneo, sin BD).
REM ============================================================
setlocal
pushd "%~dp0"

set "PEFA=%~1"
if "%PEFA%"=="" (
  echo Uso: COMPARAR_CICLO.bat ^<pefa^> [esquema]
  popd & exit /b 1
)
set "ESQ=%~2"
if "%ESQ%"=="" set "ESQ=CHILQUIN"

set "PY=%~dp0.venv\Scripts\python.exe"
set "TPL=consultas_ejemplo\cargos_por_tarifa.sql"
if not exist local mkdir local

echo == Volcando V7 (node thick) - pefa %PEFA% esquema %ESQ% ==
node "%~dp0dump_oracle.js" v7 "%TPL%" "local\v7_%PEFA%.csv" --esquema %ESQ% --pefa %PEFA%
if errorlevel 1 goto :err

echo == Volcando V8 (node) - pefa %PEFA% esquema %ESQ% ==
node "%~dp0dump_oracle.js" v8 "%TPL%" "local\v8_%PEFA%.csv" --esquema %ESQ% --pefa %PEFA%
if errorlevel 1 goto :err

echo == Comparando y generando Excel ==
"%PY%" "%~dp0comparador.py" "local\v7_%PEFA%.csv" "local\v8_%PEFA%.csv" --excel "local\comparacion_%PEFA%.xlsx"

echo.
echo LISTO: local\comparacion_%PEFA%.xlsx
popd & endlocal & exit /b 0

:err
echo ERROR en el volcado (ver mensajes arriba).
popd & endlocal & exit /b 1
