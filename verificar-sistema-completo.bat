@echo off
echo ====================================================
echo  Verificando Estado del Sistema
echo ====================================================
echo.

echo [1] Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Docker instalado
) else (
    echo ❌ Docker no encontrado
)

echo.
echo [2] Verificando contenedores...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo [3] Verificando MySQL Central...
docker exec mysql-central-cenfotec mysql -uroot -padmin123 -e "SELECT 'OK' as status;" 2>nul
if %errorlevel% equ 0 (
    echo ✅ MySQL Central funcionando
) else (
    echo ❌ MySQL Central no responde
)

echo.
echo [4] Verificando MySQL San Carlos...
docker exec mysql-sancarlos-cenfotec mysql -uroot -padmin123 -e "SELECT 'OK' as status;" 2>nul
if %errorlevel% equ 0 (
    echo ✅ MySQL San Carlos funcionando
) else (
    echo ❌ MySQL San Carlos no responde
)

echo.
echo [5] Verificando MySQL Heredia...
docker exec mysql-heredia-cenfotec mysql -uroot -padmin123 -e "SELECT 'OK' as status;" 2>nul
if %errorlevel% equ 0 (
    echo ✅ MySQL Heredia funcionando
) else (
    echo ❌ MySQL Heredia no responde
)

echo.
echo [6] Verificando Redis Cache...
docker exec redis-cenfotec redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis funcionando
) else (
    echo ❌ Redis no responde
)

echo.
echo [7] Verificando Python/Streamlit...
python --version
pip show streamlit >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Streamlit instalado
) else (
    echo ⚠️  Streamlit no instalado - ejecuta: pip install -r streamlit/requirements.txt
)

echo.
echo ====================================================
pause