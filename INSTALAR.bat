@echo off
echo ========================================
echo    OptiSolarAI - Instalacion
echo ========================================
echo.

echo [1/3] Creando entorno virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

echo [2/3] Activando entorno virtual...
call venv\Scripts\activate.bat

echo [3/3] Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ========================================
echo    INSTALACION COMPLETADA!
echo ========================================
echo.
echo Para ejecutar la aplicacion, usa: EJECUTAR.bat
echo O ejecuta manualmente: streamlit run app.py
echo.

pause
