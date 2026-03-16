@echo off
echo ========================================
echo    OptiSolarAI - Inicio Rapido
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
) else (
    echo ADVERTENCIA: No se encontro entorno virtual
    echo Ejecuta: python -m venv venv
    echo.
)

echo Iniciando OptiSolarAI...
echo.
streamlit run app.py

pause
