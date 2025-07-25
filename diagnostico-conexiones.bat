@echo off
echo ========================================
echo DIAGNÓSTICO DE CONEXIONES - CENFOTEC
echo ========================================
echo.

echo [1] Verificando contenedores Docker...
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

echo [2] Verificando red Docker...
docker network inspect universidad-cenfotec-distributed_cenfotec --format "{{.Name}}: {{.IPAM.Config}}" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Red Docker no encontrada, verificando con nombre alternativo...
    docker network ls | findstr cenfotec
)
echo.

echo [3] Verificando conectividad MySQL desde contenedores...
echo.
echo 🏛️  MYSQL CENTRAL:
docker exec mysql-central-cenfotec mysql -u root -padmin123 -e "SELECT 'Central OK' as status, NOW() as timestamp;" 2>nul
if %errorlevel% equ 0 (
    echo ✅ MySQL Central: Conectado y funcionando
) else (
    echo ❌ MySQL Central: Error de conexión
)

echo.
echo 🏢 MYSQL SAN CARLOS:
docker exec mysql-sancarlos-cenfotec mysql -u root -padmin123 -e "SELECT 'San Carlos OK' as status, NOW() as timestamp;" 2>nul
if %errorlevel% equ 0 (
    echo ✅ MySQL San Carlos: Conectado y funcionando
) else (
    echo ❌ MySQL San Carlos: Error de conexión
)

echo.
echo 🏫 MYSQL HEREDIA:
docker exec mysql-heredia-cenfotec mysql -u root -padmin123 -e "SELECT 'Heredia OK' as status, NOW() as timestamp;" 2>nul
if %errorlevel% equ 0 (
    echo ✅ MySQL Heredia: Conectado y funcionando
) else (
    echo ❌ MySQL Heredia: Error de conexión
)

echo.
echo [4] Verificando Redis...
docker exec redis-cenfotec redis-cli ping 2>nul
if %errorlevel% equ 0 (
    echo ✅ Redis: Funcionando correctamente
    docker exec redis-cenfotec redis-cli info server | findstr redis_version 2>nul
) else (
    echo ❌ Redis: Error de conexión
)

echo.
echo [5] Verificando Streamlit...
docker exec streamlit-cenfotec ps aux | findstr streamlit 2>nul
if %errorlevel% equ 0 (
    echo ✅ Streamlit: Proceso ejecutándose
) else (
    echo ❌ Streamlit: Proceso no encontrado
)

echo.
echo [6] Verificando conectividad interna...
echo Probando conectividad desde Streamlit a MySQL Central:
docker exec streamlit-cenfotec nc -zv 172.20.0.10 3306 2>nul
if %errorlevel% equ 0 (
    echo ✅ Streamlit puede conectar a MySQL Central
) else (
    echo ❌ Streamlit NO puede conectar a MySQL Central
)

echo.
echo Probando conectividad desde Streamlit a Redis:
docker exec streamlit-cenfotec nc -zv 172.20.0.13 6379 2>nul
if %errorlevel% equ 0 (
    echo ✅ Streamlit puede conectar a Redis
) else (
    echo ❌ Streamlit NO puede conectar a Redis
)

echo.
echo [7] Logs de Streamlit (últimas 10 líneas):
docker logs streamlit-cenfotec --tail 10 2>nul

echo.
echo [8] Puertos expuestos:
netstat -ano | findstr ":8501" 2>nul
netstat -ano | findstr ":3306" 2>nul | findstr "LISTENING"
netstat -ano | findstr ":3307" 2>nul | findstr "LISTENING"  
netstat -ano | findstr ":3308" 2>nul | findstr "LISTENING"

echo.
echo ========================================
echo RECOMENDACIONES DE SOLUCIÓN
echo ========================================
echo.
echo Si hay problemas de conexión:
echo 1. Ejecutar: docker-compose down ^&^& docker-compose up -d
echo 2. Verificar que Docker Desktop tenga suficiente memoria
echo 3. Reiniciar Docker Desktop si persisten los problemas
echo 4. Verificar firewall/antivirus no esté bloqueando puertos
echo.
echo Para ver logs detallados:
echo   docker-compose logs streamlit-app
echo   docker-compose logs mysql-central
echo   docker-compose logs redis-cache
echo.
echo ========================================
pause