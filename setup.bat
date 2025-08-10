@echo off
echo ========================================
echo SETUP SISTEMA DISTRIBUIDO CENFOTEC
echo ========================================
echo.

echo [1/6] Verificando prerequisitos...

REM Verificar Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker no está instalado
    echo Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
) else (
    echo Docker instalado y funcionando
)

REM Verificar Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker Compose no está disponible
    pause
    exit /b 1
) else (
    echo Docker Compose disponible
)

echo.
echo [2/6] Verificando estructura de archivos...

if not exist "docker-compose.yml" (
    echo Error: docker-compose.yml no encontrado
    echo Asegúrate de estar en el directorio correcto del proyecto
    pause
    exit /b 1
) else (
    echo docker-compose.yml encontrado
)

if not exist "nginx\nginx.conf" (
    echo Error: nginx/nginx.conf no encontrado
    pause
    exit /b 1
) else (
    echo Configuración NGINX encontrada
)

if not exist "mysql\central\init.sql" (
    echo Error: Scripts MySQL no encontrados
    pause
    exit /b 1
) else (
    echo Scripts de inicialización MySQL encontrados
)

if not exist "streamlit\app.py" (
    echo Error: Aplicación Streamlit no encontrada
    echo Asegúrate de que la carpeta streamlit/ esté presente
    pause
    exit /b 1
) else (
    echo Aplicación Streamlit encontrada
)

if not exist "streamlit\Dockerfile" (
    echo Error: Dockerfile de Streamlit no encontrado
    pause
    exit /b 1
) else (
    echo Dockerfile de Streamlit encontrado
)

echo.
echo [3/6] Verificando puertos disponibles...

REM Verificar puerto 80 (NGINX)
netstat -ano | findstr :80 >nul 2>&1
if %errorlevel% equ 0 (
    echo Advertencia: Puerto 80 puede estar en uso (NGINX)
)

REM Verificar puerto 3306 (MySQL Central)
netstat -ano | findstr :3306 >nul 2>&1
if %errorlevel% equ 0 (
    echo Advertencia: Puerto 3306 puede estar en uso (MySQL Central)
)

REM Verificar puerto 3307 (MySQL San Carlos)
netstat -ano | findstr :3307 >nul 2>&1
if %errorlevel% equ 0 (
    echo Advertencia: Puerto 3307 puede estar en uso (MySQL San Carlos)
)

REM Verificar puerto 3308 (MySQL Heredia)
netstat -ano | findstr :3308 >nul 2>&1
if %errorlevel% equ 0 (
    echo Advertencia: Puerto 3308 puede estar en uso (MySQL Heredia)
)

REM Verificar puerto 6379 (Redis)
netstat -ano | findstr :6379 >nul 2>&1
if %errorlevel% equ 0 (
    echo Advertencia: Puerto 6379 puede estar en uso (Redis)
)

REM Verificar puerto 8080 (phpMyAdmin)
netstat -ano | findstr :8080 >nul 2>&1
if %errorlevel% equ 0 (
    echo Advertencia: Puerto 8080 puede estar en uso (phpMyAdmin)
)

REM Verificar puerto 8501 (Streamlit) - NUEVO
netstat -ano | findstr :8501 >nul 2>&1
if %errorlevel% equ 0 (
    echo Advertencia: Puerto 8501 puede estar en uso (Streamlit)
)

echo.
echo [4/6] Limpiando instalación anterior...
echo Parando contenedores existentes...

docker-compose down >nul 2>&1

echo.
echo [5/6] Construyendo y levantando servicios...
echo Esto puede tomar varios minutos en la primera ejecución...
echo Construyendo imágenes y descargando dependencias...

docker-compose up -d --build

if %errorlevel% neq 0 (
    echo Error al levantar los servicios
    echo Revisa los logs con: docker-compose logs
    pause
    exit /b 1
)

echo.
echo [6/6] Verificando servicios...
echo Esperando que todos los servicios estén listos...

timeout /t 15 /nobreak >nul

REM Verificar que todos los contenedores estén corriendo
docker-compose ps | findstr "Up" >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Algunos servicios no están corriendo
    echo.
    echo Estado actual de los contenedores:
    docker-compose ps
    echo.
    echo Ver logs con: docker-compose logs [nombre-servicio]
    pause
    exit /b 1
)

echo Verificando contenedores individuales...

REM Verificar MySQL Central
docker exec mysql-central-cenfotec mysql -u root -padmin123 -e "SELECT 'Central OK' as status;" >nul 2>&1
if %errorlevel% equ 0 (
    echo MySQL Central: Funcionando
) else (
    echo MySQL Central: Aún inicializando...
)

REM Verificar MySQL San Carlos
docker exec mysql-sancarlos-cenfotec mysql -u root -padmin123 -e "SELECT 'San Carlos OK' as status;" >nul 2>&1
if %errorlevel% equ 0 (
    echo MySQL San Carlos: Funcionando
) else (
    echo MySQL San Carlos: Aún inicializando...
)

REM Verificar MySQL Heredia
docker exec mysql-heredia-cenfotec mysql -u root -padmin123 -e "SELECT 'Heredia OK' as status;" >nul 2>&1
if %errorlevel% equ 0 (
    echo MySQL Heredia: Funcionando
) else (
    echo MySQL Heredia: Aún inicializando...
)

REM Verificar Redis
docker exec redis-cenfotec redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo Redis Cache: Funcionando
) else (
    echo Redis Cache: Aún inicializando...
)

REM Verificar Streamlit
timeout /t 5 /nobreak >nul
curl -s http://localhost:8501 >nul 2>&1
if %errorlevel% equ 0 (
    echo Streamlit: Funcionando
) else (
    echo Streamlit: Aún inicializando... (puede tomar 1-2 minutos más)
)

echo.
echo =======================
echo INSTALACIÓN COMPLETADA
echo =======================
echo.
echo URLs de acceso:
echo   • Streamlit (Interfaz): http://localhost:8501
echo   • phpMyAdmin (Admin BD):          http://localhost:8080
echo   • Sistema Principal (NGINX):      http://localhost
echo.
echo Conexiones MySQL:
echo   • Central:       localhost:3306
echo   • San Carlos:     localhost:3307
echo   • Heredia:        localhost:3308
echo.
echo Credenciales:
echo   • Usuario: root
echo   • Contraseña: admin123
echo.
echo Servicios instalados:
echo   • 3 Bases de datos MySQL
echo   • Redis Cache distribuido
echo   • NGINX Load Balancer
echo   • Streamlit Web Interface
echo   • phpMyAdmin para administración
echo.
echo ========================================
pause