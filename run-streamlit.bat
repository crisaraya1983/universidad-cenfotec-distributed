@echo off
echo ====================================
echo  Sistema Distribuido Cenfotec
echo  Iniciando interfaz Streamlit...
echo ====================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.8 o superior
    pause
    exit /b 1
)

REM Navegar a la carpeta streamlit
cd streamlit

REM Verificar si Streamlit está instalado
pip show streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando Streamlit y dependencias...
    pip install -r requirements.txt
)

REM Abrir navegador automáticamente después de 3 segundos
echo.
echo Abriendo navegador en 3 segundos...
timeout /t 3 /nobreak >nul
start http://localhost:8501

REM Iniciar Streamlit
echo.
echo Streamlit corriendo en http://localhost:8501
echo.
echo IMPORTANTE: NO CIERRES ESTA VENTANA
echo Presiona Ctrl+C para detener Streamlit
echo.
python -m streamlit run app.py