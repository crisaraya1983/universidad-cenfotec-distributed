@echo off
echo ====================================================
echo  Sistema Distribuido Cenfotec - Setup Windows
echo ====================================================
echo.

echo [1/3] Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker no está instalado o no está en el PATH
    echo Por favor instala Docker Desktop
    pause
    exit /b 1
)

echo [2/3] Levantando servicios de base de datos...
docker-compose up -d

echo [3/3] Esperando que las bases de datos estén listas...
echo Esto puede tomar 30-60 segundos...
timeout /t 30 /nobreak

echo.
echo ====================================================
echo  ✅ Bases de datos instaladas!
echo ====================================================
echo.
echo Para iniciar Streamlit, ejecuta:
echo   start-streamlit.bat
echo.
echo O manualmente:
echo   cd streamlit
echo   streamlit run app.py
echo.
echo Accesos disponibles:
echo - MySQL Central: localhost:3306
echo - MySQL San Carlos: localhost:3307
echo - MySQL Heredia: localhost:3308
echo - Redis Cache: localhost:6379
echo - phpMyAdmin: http://localhost:8080
echo.
echo Usuario MySQL: root
echo Password MySQL: admin123
echo.
pause