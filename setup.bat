@echo off
echo ========================================
echo SETUP SISTEMA DISTRIBUIDO CENFOTEC
echo ========================================
echo.

echo [1/5] Verificando prerequisitos...

REM Verificar Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Docker no está instalado
    echo Por favor instala Docker Desktop desde: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
) else (
    echo ✅ Docker instalado y funcionando
)

REM Verificar Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Docker Compose no está disponible
    pause
    exit /b 1
) else (
    echo ✅ Docker Compose disponible
)

echo.
echo [2/5] Verificando estructura de archivos...

if not exist "docker-compose.yml" (
    echo ❌ Error: docker-compose.yml no encontrado
    echo Asegúrate de estar en el directorio correcto del proyecto
    pause
    exit /b 1
) else (
    echo ✅ docker-compose.yml encontrado
)

if not exist "nginx\nginx.conf" (
    echo ❌ Error: nginx/nginx.conf no encontrado
    pause
    exit /b 1
) else (
    echo ✅ Configuración NGINX encontrada
)

if not exist "mysql\central\init.sql" (
    echo ❌ Error: Scripts MySQL no encontrados
    pause
    exit /b 1
) else (
    echo ✅ Scripts de inicialización MySQL encontrados
)

echo.
echo [3/5] Verificando puertos disponibles...

REM Verificar puerto 80
netstat -ano | findstr :80 >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Advertencia: Puerto 80 puede estar en uso
)

REM Verificar puerto 3306
netstat -ano | findstr :3306 >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Advertencia: Puerto 3306 puede estar en uso
)

echo.
echo [4/5] Construyendo y levantando servicios...
echo Esto puede tomar varios minutos en la primera ejecución...

docker-compose down >nul 2>&1
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Error al levantar los servicios
    echo Revisa los logs con: docker-compose logs
    pause
    exit /b 1
)

echo.
echo [5/5] Verificando servicios...

timeout /t 10 /nobreak >nul

docker-compose ps | findstr "Up" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Algunos servicios no están corriendo
    docker-compose ps
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ INSTALACIÓN COMPLETADA EXITOSAMENTE
echo ========================================
echo.
echo 🌐 URLs de acceso:
echo   • Sistema Principal: http://localhost
echo   • phpMyAdmin:        http://localhost:8080
echo.
echo 🗄️  Conexiones MySQL:
echo   • Central:           localhost:3306
echo   • San Carlos:        localhost:3307
echo   • Heredia:           localhost:3308
echo.
echo 🔐 Credenciales:
echo   • Usuario: root
echo   • Contraseña: admin123
echo.
echo 📊 Para verificar la fragmentación, ejecuta:
echo   verify-fragmentation.bat
echo.
echo ========================================
pause