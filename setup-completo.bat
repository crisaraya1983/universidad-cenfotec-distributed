@echo off
echo ====================================================
echo  Sistema Distribuido Cenfotec - Setup Completo Docker
echo ====================================================
echo.

echo [1/6] Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker no está instalado o no está en el PATH
    echo Por favor instala Docker Desktop
    pause
    exit /b 1
) else (
    echo ✅ Docker instalado correctamente
)

echo.
echo [2/6] Verificando estructura de archivos...
if not exist "streamlit\Dockerfile" (
    echo ⚠️  Creando Dockerfile para Streamlit...
    mkdir streamlit >nul 2>&1
    echo FROM python:3.11-slim > streamlit\Dockerfile
    echo. >> streamlit\Dockerfile
    echo WORKDIR /app >> streamlit\Dockerfile
    echo. >> streamlit\Dockerfile
    echo RUN apt-get update ^&^& apt-get install -y gcc g++ ^&^& rm -rf /var/lib/apt/lists/* >> streamlit\Dockerfile
    echo. >> streamlit\Dockerfile
    echo COPY requirements.txt . >> streamlit\Dockerfile
    echo RUN pip install --no-cache-dir -r requirements.txt >> streamlit\Dockerfile
    echo. >> streamlit\Dockerfile
    echo COPY . . >> streamlit\Dockerfile
    echo. >> streamlit\Dockerfile
    echo EXPOSE 8501 >> streamlit\Dockerfile
    echo. >> streamlit\Dockerfile
    echo CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"] >> streamlit\Dockerfile
)

echo ✅ Estructura de archivos verificada

echo.
echo [3/6] Deteniendo servicios anteriores...
docker-compose down >nul 2>&1

echo.
echo [4/6] Construyendo imágenes Docker...
echo Esto puede tomar varios minutos en la primera ejecución...
docker-compose build --no-cache

if %errorlevel% neq 0 (
    echo ❌ Error al construir las imágenes
    echo Revisa los logs arriba para más detalles
    pause
    exit /b 1
)

echo.
echo [5/6] Levantando todos los servicios...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Error al levantar los servicios
    echo Revisa los logs con: docker-compose logs
    pause
    exit /b 1
)

echo.
echo [6/6] Verificando servicios...
timeout /t 15 /nobreak >nul

docker-compose ps

echo.
echo ====================================================
echo ✅ INSTALACIÓN COMPLETADA EXITOSAMENTE
echo ====================================================
echo.
echo 🌐 URLs de acceso:
echo   • Streamlit App:      http://localhost:8501
echo   • phpMyAdmin:         http://localhost:8080
echo   • Load Balancer:      http://localhost
echo.
echo 🗄️  Conexiones MySQL (desde fuera de Docker):
echo   • Central:            localhost:3306
echo   • San Carlos:         localhost:3307
echo   • Heredia:            localhost:3308
echo.
echo 🔐 Credenciales:
echo   • Usuario: root
echo   • Contraseña: admin123
echo.
echo 📊 Para verificar la fragmentación:
echo   docker exec -it mysql-central-cenfotec mysql -u root -padmin123 -e "SHOW DATABASES;"
echo.
echo 🔧 Comandos útiles:
echo   • Ver logs: docker-compose logs streamlit-app
echo   • Reiniciar: docker-compose restart
echo   • Parar todo: docker-compose down
echo.
echo ====================================================
pause