@echo off
echo ========================================
echo RECUPERANDO SISTEMA ORIGINAL
echo ========================================
echo.

echo [1/3] Levantando solo las bases de datos y servicios originales...
docker-compose up -d mysql-central mysql-sancarlos mysql-heredia redis-cache nginx-loadbalancer phpmyadmin

echo.
echo [2/3] Esperando que los servicios estén listos...
timeout /t 20 /nobreak >nul

echo.
echo [3/3] Verificando estado...
docker-compose ps

echo.
echo ========================================
echo ✅ SISTEMA ORIGINAL RECUPERADO
echo ========================================
echo.
echo 🌐 URLs disponibles:
echo   • phpMyAdmin:         http://localhost:8080
echo   • Load Balancer:      http://localhost
echo.
echo 🗄️  Conexiones MySQL:
echo   • Central:            localhost:3306
echo   • San Carlos:         localhost:3307
echo   • Heredia:            localhost:3308
echo.
echo ⚠️  Streamlit todavía no está disponible
echo    Ejecuta fix-requirements.bat para solucionarlo
echo.
echo ========================================
pause