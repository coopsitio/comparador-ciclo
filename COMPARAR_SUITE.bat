@echo off
REM ============================================================
REM  Corre TODAS las comparaciones de consultas_suite\ entre V7 y V8,
REM  para un mismo ciclo (pefa), y deja un Excel por dimension.
REM  Uso:  COMPARAR_SUITE.bat <pefa> [esquema]
REM
REM  Cada .sql de consultas_suite\ es una dimension de analisis (facturacion,
REM  productos, cargo fijo, consumo medido, ...). Se puede agregar mas .sql.
REM  Los volcados usan Node (esquiva el antivirus); el compare, python.
REM  Parametros por-ambiente (ej. {SUBSERVE}=2 en V7 / 47 en V8) salen del .env.
REM ============================================================
setlocal enabledelayedexpansion
pushd "%~dp0"

set "PEFA=%~1"
if "%PEFA%"=="" (
  echo Uso: COMPARAR_SUITE.bat ^<pefa^> [esquema]
  popd & exit /b 1
)
set "ESQ=%~2"
if "%ESQ%"=="" set "ESQ=CHILQUIN"
set "PY=%~dp0.venv\Scripts\python.exe"
set "OUT=local\suite_%PEFA%"
if not exist "%OUT%" mkdir "%OUT%"

for %%F in ("%~dp0consultas_suite\*.sql") do (
  set "NOM=%%~nF"
  echo === Dimension: !NOM! ===
  node "%~dp0dump_oracle.js" v7 "%%F" "%OUT%\v7_!NOM!.csv" --esquema %ESQ% --pefa %PEFA%
  if errorlevel 1 goto :err
  node "%~dp0dump_oracle.js" v8 "%%F" "%OUT%\v8_!NOM!.csv" --esquema %ESQ% --pefa %PEFA%
  if errorlevel 1 goto :err
  "%PY%" "%~dp0comparador.py" "%OUT%\v7_!NOM!.csv" "%OUT%\v8_!NOM!.csv" --excel "%OUT%\comp_!NOM!.xlsx" > "%OUT%\salida_!NOM!.txt"
)

echo.
echo LISTO: resultados en %OUT%\
popd & endlocal & exit /b 0

:err
echo ERROR en el volcado de la dimension !NOM! (ver mensajes arriba).
popd & endlocal & exit /b 1
