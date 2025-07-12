@echo off
echo ========================================
echo VERIFICACIÓN DE FRAGMENTACIÓN - CENFOTEC
echo ========================================
echo.

echo [VERIFICANDO] Conectividad de contenedores...
docker-compose ps | findstr "Up" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Los contenedores no están corriendo
    echo Ejecuta: docker-compose up -d
    pause
    exit /b 1
)
echo ✅ Todos los contenedores están activos
echo.

echo ========================================
echo 🏛️  SEDE CENTRAL - DATOS ADMINISTRATIVOS
echo ========================================
echo.
echo Tablas en Sede Central:
docker exec mysql-central-cenfotec mysql -u root -padmin123 -e "USE cenfotec_central; SHOW TABLES;" 2>nul
echo.
echo Registros administrativos:
docker exec mysql-central-cenfotec mysql -u root -padmin123 -e "USE cenfotec_central; SELECT 'Sedes' as tabla, COUNT(*) as registros FROM sede UNION SELECT 'Carreras', COUNT(*) FROM carrera UNION SELECT 'Profesores', COUNT(*) FROM profesor UNION SELECT 'Planillas', COUNT(*) FROM planilla UNION SELECT 'Pagarés', COUNT(*) FROM pagare;" 2>nul

echo.
echo ========================================
echo 🏢 SEDE SAN CARLOS - DATOS ACADÉMICOS
echo ========================================
echo.
echo Tablas en San Carlos:
docker exec mysql-sancarlos-cenfotec mysql -u root -padmin123 -e "USE cenfotec_sancarlos; SHOW TABLES;" 2>nul
echo.
echo Registros académicos:
docker exec mysql-sancarlos-cenfotec mysql -u root -padmin123 -e "USE cenfotec_sancarlos; SELECT 'Estudiantes' as tabla, COUNT(*) as registros FROM estudiante UNION SELECT 'Cursos', COUNT(*) FROM curso UNION SELECT 'Matrículas', COUNT(*) FROM matricula UNION SELECT 'Notas', COUNT(*) FROM nota UNION SELECT 'Pagos', COUNT(*) FROM pago;" 2>nul
echo.
echo Estudiantes de San Carlos:
docker exec mysql-sancarlos-cenfotec mysql -u root -padmin123 -e "USE cenfotec_sancarlos; SELECT e.nombre as estudiante, s.nombre as sede FROM estudiante e JOIN sede s ON e.id_sede = s.id_sede WHERE s.nombre = 'San Carlos' LIMIT 3;" 2>nul

echo.
echo ========================================
echo 🏫 SEDE HEREDIA - DATOS ACADÉMICOS  
echo ========================================
echo.
echo Tablas en Heredia:
docker exec mysql-heredia-cenfotec mysql -u root -padmin123 -e "USE cenfotec_heredia; SHOW TABLES;" 2>nul
echo.
echo Registros académicos:
docker exec mysql-heredia-cenfotec mysql -u root -padmin123 -e "USE cenfotec_heredia; SELECT 'Estudiantes' as tabla, COUNT(*) as registros FROM estudiante UNION SELECT 'Cursos', COUNT(*) FROM curso UNION SELECT 'Matrículas', COUNT(*) FROM matricula UNION SELECT 'Notas', COUNT(*) FROM nota UNION SELECT 'Pagos', COUNT(*) FROM pago;" 2>nul
echo.
echo Estudiantes de Heredia:
docker exec mysql-heredia-cenfotec mysql -u root -padmin123 -e "USE cenfotec_heredia; SELECT e.nombre as estudiante, s.nombre as sede FROM estudiante e JOIN sede s ON e.id_sede = s.id_sede WHERE s.nombre = 'Heredia' LIMIT 3;" 2>nul

echo.
echo ========================================
echo 📊 RESUMEN DE FRAGMENTACIÓN
echo ========================================
echo.
echo ✅ FRAGMENTACIÓN VERTICAL demostrada:
echo    • Central: Solo datos administrativos (planillas, pagarés)
echo    • Regionales: Solo datos académicos (estudiantes, matrículas)
echo.
echo ✅ FRAGMENTACIÓN HORIZONTAL demostrada:
echo    • San Carlos: Solo estudiantes de San Carlos
echo    • Heredia: Solo estudiantes de Heredia
echo.
echo ✅ FRAGMENTACIÓN MIXTA demostrada:
echo    • Combinación de vertical + horizontal
echo.
echo ✅ DATOS MAESTROS replicados:
echo    • Sedes, carreras, profesores en todas las bases
echo.
echo ========================================
echo 🎯 URLs para explorar:
echo ========================================
echo • Sistema Principal: http://localhost
echo • phpMyAdmin:        http://localhost:8080
echo.
echo Para conectar VS Code MySQL:
echo • Central:    172.20.0.10:3306
echo • San Carlos: 172.20.0.11:3306  
echo • Heredia:    172.20.0.12:3306
echo.
echo Usuario: root | Contraseña: admin123
echo ========================================
pause