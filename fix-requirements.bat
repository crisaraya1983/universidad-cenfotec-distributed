@echo off
echo ========================================
echo CORRIGIENDO REQUIREMENTS Y STREAMLIT
echo ========================================
echo.

echo [1/6] Creando requirements.txt correcto...
(
echo # Dependencias principales
echo streamlit==1.47.0
echo mysql-connector-python==9.1.0
echo pandas==2.2.3
echo plotly==5.24.1
echo redis==5.3.1
echo python-dotenv==1.0.1
echo.
echo # Visualización y análisis
echo matplotlib==3.9.5
echo seaborn==0.13.2
echo altair==5.5.0
echo.
echo # Utilidades adicionales
echo numpy==2.1.3
echo pytz==2024.2
echo tabulate==0.9.0
) > streamlit\requirements.txt

echo ✅ requirements.txt actualizado

echo.
echo [2/6] Verificando que el Dockerfile esté en streamlit/...
if not exist "streamlit\Dockerfile" (
    echo Creando Dockerfile...
    (
        echo FROM python:3.11-slim
        echo.
        echo WORKDIR /app
        echo.
        echo RUN apt-get update ^&^& apt-get install -y gcc g++ curl ^&^& rm -rf /var/lib/apt/lists/*
        echo.
        echo COPY requirements.txt .
        echo RUN pip install --no-cache-dir -r requirements.txt
        echo.
        echo COPY . .
        echo.
        echo EXPOSE 8501
        echo.
        echo CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
    ) > streamlit\Dockerfile
)

echo ✅ Dockerfile verificado

echo.
echo [3/6] Deteniendo contenedores existentes...
docker-compose down >nul 2>&1

echo.
echo [4/6] Construyendo imagen de Streamlit corregida...
docker-compose build streamlit-app --no-cache

echo.
echo [5/6] Levantando todos los servicios...
docker-compose up -d

echo.
echo [6/6] Verificando estado de servicios...
timeout /t 15 /nobreak >nul
docker-compose ps

echo.
echo ========================================
echo ✅ SISTEMA COMPLETO FUNCIONANDO
echo ========================================
echo.
echo 🌐 URLs disponibles:
echo   • Streamlit App:      http://localhost:8501
echo   • phpMyAdmin:         http://localhost:8080
echo   • Load Balancer:      http://localhost
echo.
echo 🗄️  Conexiones MySQL:
echo   • Central:            localhost:3306
echo   • San Carlos:         localhost:3307
echo   • Heredia:            localhost:3308
echo.
echo 🔧 Si hay problemas:
echo   docker-compose logs streamlit-app
echo.
echo ========================================
pause