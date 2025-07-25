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

REM Iniciar Streamlit
echo.
echo Iniciando Streamlit en http://localhost:8501
echo Presiona Ctrl+C para detener el servidor
echo.
streamlit run app.py