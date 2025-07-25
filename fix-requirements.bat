@echo off
echo ========================================
echo CORRIGIENDO REQUIREMENTS Y STREAMLIT
echo ========================================
echo.

echo [1/5] Corrigiendo requirements.txt...
(
echo # Dependencias principales
echo streamlit==1.37.0
echo mysql-connector-python==8.2.0
echo pandas==2.1.4
echo plotly==5.17.0
echo python-dotenv==1.0.1
echo.
echo # Visualización y análisis
echo matplotlib==3.8.2
echo seaborn==0.13.0
echo altair==5.1.2
echo.
echo # Utilidades adicionales
echo numpy==1.25.2
echo pytz==2024.1
echo tabulate==0.9.0
) > streamlit\requirements.txt

echo ✅ requirements.txt corregido

echo.
echo [2/5] Limpiando imágenes Docker anteriores...
docker rmi universidad-cenfotec-distributed_streamlit-app 2>nul

echo.
echo [3/5] Construyendo imagen de Streamlit...
docker-compose build streamlit-app --no-cache

echo.
echo [4/5] Levantando todos los servicios...
docker-compose up -d

echo.
echo [5/5] Verificando estado...
timeout /t 20 /nobreak >nul
docker-compose ps

echo.
echo ========================================
echo ✅ SISTEMA CORREGIDO
echo ========================================
echo.
echo 🌐 URLs disponibles:
echo   • Streamlit App:      http://localhost:8501
echo   • phpMyAdmin:         http://localhost:8080
echo.
pause