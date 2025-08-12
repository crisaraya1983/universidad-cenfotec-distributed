-- ==================================
-- VISTAS PARA ROL ADMINISTRATIVO
-- ==================================

-- Vista de pagarés activos
CREATE VIEW vista_admin_pagares_activos AS
SELECT 
    pg.id_pagare,
    pg.id_estudiante,
    CONCAT('EST-', LPAD(pg.id_estudiante, 4, '0')) as codigo_estudiante,
    pg.monto,
    pg.vencimiento,
    CASE 
        WHEN pg.vencimiento < CURDATE() THEN 'Vencido'
        WHEN pg.vencimiento <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 'Por vencer'
        ELSE 'Vigente'
    END as estado,
    DATEDIFF(pg.vencimiento, CURDATE()) as dias_vencimiento,
    pg.fecha_creacion
FROM pagare pg
ORDER BY pg.vencimiento ASC;


-- Vista de resumen de planillas por profesor
CREATE VIEW vista_admin_planillas_resumen AS
SELECT 
    pl.id_profesor,
    p.nombre as nombre_profesor,
    p.email as email_profesor,
    s.nombre as sede_profesor,
    COUNT(pl.id_planilla) as total_registros_planilla,
    SUM(pl.salario) as total_pagado,
    AVG(pl.salario) as promedio_salario,
    MAX(pl.mes) as ultimo_mes_pagado,
    MIN(pl.mes) as primer_mes_registrado
FROM planilla pl
JOIN profesor p ON pl.id_profesor = p.id_profesor
JOIN sede s ON p.id_sede = s.id_sede
GROUP BY pl.id_profesor, p.nombre, p.email, s.nombre
ORDER BY p.nombre;

-- ===================================
-- VISTAS PARA ROL DIRECTIVO
-- ===================================

-- Vista ejecutiva con datos administrativos centrales
CREATE VIEW vista_directivo_datos_centrales AS
SELECT 
    (SELECT COUNT(*) FROM profesor) as total_profesores_sistema,
    (SELECT COUNT(*) FROM carrera) as total_carreras_sistema,
    (SELECT COUNT(*) FROM sede) as total_sedes,
    (SELECT COUNT(*) FROM pagare WHERE vencimiento >= CURDATE()) as pagares_vigentes,
    (SELECT COUNT(*) FROM pagare WHERE vencimiento < CURDATE()) as pagares_vencidos,
    (SELECT SUM(monto) FROM pagare WHERE vencimiento >= CURDATE()) as monto_pagares_vigentes,
    (SELECT SUM(monto) FROM pagare WHERE vencimiento < CURDATE()) as monto_pagares_vencidos,
    (SELECT SUM(salario) FROM planilla WHERE LEFT(mes, 4) = YEAR(CURDATE())) as gastos_planilla_año,
    (SELECT SUM(salario) FROM planilla WHERE LEFT(mes, 4) = YEAR(CURDATE()) -1) as gastos_planilla_año_anterior,
    (SELECT COUNT(DISTINCT id_profesor) FROM planilla) as profesores_en_planilla;

-- Vista de distribución de profesores por sede
CREATE VIEW vista_directivo_profesores_por_sede AS
SELECT 
    s.id_sede,
    s.nombre as nombre_sede,
    s.direccion,
    COUNT(DISTINCT p.id_profesor) as total_profesores,
    COUNT(DISTINCT c.id_carrera) as total_carreras
FROM sede s
LEFT JOIN profesor p ON s.id_sede = p.id_sede
LEFT JOIN carrera c ON s.id_sede = c.id_sede
GROUP BY s.id_sede, s.nombre, s.direccion
ORDER BY s.id_sede;


-- Vista de análisis financiero de pagarés
CREATE VIEW vista_directivo_analisis_pagares AS
SELECT 
    YEAR(vencimiento) as año_vencimiento,
    MONTH(vencimiento) as mes_vencimiento,
    COUNT(*) as cantidad_pagares,
    SUM(monto) as monto_total,
    AVG(monto) as monto_promedio,
    MIN(monto) as monto_minimo,
    MAX(monto) as monto_maximo,
    COUNT(CASE WHEN vencimiento < CURDATE() THEN 1 END) as vencidos,
    COUNT(CASE WHEN vencimiento >= CURDATE() THEN 1 END) as vigentes
FROM pagare
GROUP BY YEAR(vencimiento), MONTH(vencimiento)
ORDER BY año_vencimiento DESC, mes_vencimiento DESC;

-- ---------------------VISTAS ESTUDIANTES----------------------------------
CREATE VIEW vista_estudiante_mis_materias AS
SELECT 
    e.id_estudiante,
    e.nombre as nombre_estudiante,
    e.email as email_estudiante,
    c.nombre as nombre_curso,
    car.nombre as carrera,
    COALESCE(n.nota, 0) as nota_obtenida,
    CASE 
        WHEN n.nota IS NULL THEN 'En curso'
        WHEN n.nota >= 70 THEN 'Aprobado'
        ELSE 'Reprobado'
    END as estado_materia,
    m.id_matricula,
    m.fecha_creacion AS fecha_matricula,
    COALESCE(
        (SELECT COUNT(*) FROM asistencia a WHERE a.id_matricula = m.id_matricula), 0
    ) as total_clases_registradas,
    COALESCE(
        (SELECT COUNT(*) FROM asistencia a WHERE a.id_matricula = m.id_matricula AND a.presente = 1), 0
    ) as clases_asistidas,
    CASE 
        WHEN (SELECT COUNT(*) FROM asistencia a WHERE a.id_matricula = m.id_matricula) > 0 THEN
            ROUND(
                ((SELECT COUNT(*) FROM asistencia a WHERE a.id_matricula = m.id_matricula AND a.presente = 1) / 
                 (SELECT COUNT(*) FROM asistencia a WHERE a.id_matricula = m.id_matricula)) * 100, 2
            )
        ELSE 0
    END as porcentaje_asistencia
FROM estudiante e
JOIN matricula m ON e.id_estudiante = m.id_estudiante
JOIN curso c ON m.id_curso = c.id_curso
JOIN carrera car ON c.id_carrera = car.id_carrera
LEFT JOIN nota n ON m.id_matricula = n.id_matricula
WHERE e.id_sede = 1
ORDER BY e.nombre, c.nombre;


CREATE VIEW vista_estudiante_mis_pagos AS
SELECT 
    e.id_estudiante,
    e.nombre as nombre_estudiante,
    e.email as email_estudiante,
    p.id_pago,
    p.monto,
    p.fecha,
    'Pago de matrícula/mensualidad' as concepto,
    MONTH(p.fecha) as mes_pago,
    YEAR(p.fecha) as año_pago,
    MONTHNAME(p.fecha) as nombre_mes
FROM estudiante e
JOIN pago p ON e.id_estudiante = p.id_estudiante
WHERE e.id_sede = 1
ORDER BY p.fecha DESC;



CREATE VIEW vista_estudiante_expediente_completo AS
SELECT 
    e.id_estudiante,
    e.nombre as nombre_estudiante,
    e.email,
    e.estado as estado_estudiante,
    e.fecha_creacion,
    COUNT(DISTINCT m.id_curso) as total_materias_matriculadas,
    COUNT(DISTINCT CASE WHEN n.nota >= 70 THEN m.id_curso END) as materias_aprobadas,
    COUNT(DISTINCT CASE WHEN n.nota < 70 AND n.nota IS NOT NULL THEN m.id_curso END) as materias_reprobadas,
    COUNT(DISTINCT CASE WHEN n.nota IS NULL THEN m.id_curso END) as materias_en_curso,
    COALESCE(AVG(n.nota), 0) as promedio_general,
    COALESCE(SUM(pag.monto), 0) as total_pagado,
    COUNT(pag.id_pago) as total_pagos_realizados
FROM estudiante e
LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
LEFT JOIN nota n ON m.id_matricula = n.id_matricula
LEFT JOIN pago pag ON e.id_estudiante = pag.id_estudiante
WHERE e.id_sede = 1
GROUP BY e.id_estudiante, e.nombre, e.email, e.estado, e.fecha_creacion
ORDER BY e.nombre;

-- -------------------------------------Profesor Sede Central---------------------------------------------
CREATE VIEW vista_profesor_resumen_cursos AS
SELECT 
    p.id_profesor,
    p.nombre as nombre_profesor,
    c.id_curso,
    c.nombre as nombre_curso,
    car.nombre as carrera,
    COUNT(DISTINCT m.id_estudiante) as total_estudiantes,
    COUNT(DISTINCT CASE WHEN n.nota >= 70 THEN m.id_estudiante END) as estudiantes_aprobados,
    COUNT(DISTINCT CASE WHEN n.nota < 70 AND n.nota IS NOT NULL THEN m.id_estudiante END) as estudiantes_reprobados,
    COUNT(DISTINCT CASE WHEN n.nota IS NULL THEN m.id_estudiante END) as estudiantes_pendientes,
    COALESCE(ROUND(AVG(n.nota), 2), 0) as promedio_curso,
    COALESCE(MAX(n.nota), 0) as nota_maxima,
    COALESCE(MIN(n.nota), 0) as nota_minima,
    COUNT(DISTINCT m.fecha_creacion) as periodos_activos
FROM profesor p
JOIN sede s ON s.id_sede = p.id_sede
JOIN carrera car ON car.id_sede = s.id_sede
JOIN curso c ON car.id_carrera = c.id_carrera
JOIN matricula m ON c.id_curso = m.id_curso
JOIN estudiante e ON m.id_estudiante = e.id_estudiante
LEFT JOIN nota n ON m.id_matricula = n.id_matricula
WHERE p.id_sede = 1 AND e.id_sede = 1
GROUP BY p.id_profesor, c.id_curso
ORDER BY p.nombre, c.nombre;

CREATE VIEW vista_profesor_mis_estudiantes AS
SELECT 
    p.id_profesor,
    p.nombre as nombre_profesor,
    c.id_curso,
    c.nombre as nombre_curso,
    car.nombre as carrera,
    e.id_estudiante,
    e.nombre as nombre_estudiante,
    e.email as email_estudiante,
    COALESCE(n.nota, 0) as nota_actual,
    CASE 
        WHEN n.nota IS NULL THEN 'Pendiente'
        WHEN n.nota >= 70 THEN 'Aprobado'
        ELSE 'Reprobado'
    END as estado,
    m.id_matricula,
    m.fecha_creacion AS fecha_matricula,
    COALESCE(
        (SELECT COUNT(*) FROM asistencia a WHERE a.id_matricula = m.id_matricula), 0
    ) as total_clases_registradas,
    COALESCE(
        (SELECT COUNT(*) FROM asistencia a WHERE a.id_matricula = m.id_matricula AND a.presente = 1), 0
    ) as clases_asistidas,
    CASE 
        WHEN (SELECT COUNT(*) FROM asistencia a WHERE a.id_matricula = m.id_matricula) > 0 THEN
            ROUND(
                ((SELECT COUNT(*) FROM asistencia a WHERE a.id_matricula = m.id_matricula AND a.presente = 1) / 
                 (SELECT COUNT(*) FROM asistencia a WHERE a.id_matricula = m.id_matricula)) * 100, 2
            )
        ELSE 0
    END as porcentaje_asistencia
FROM profesor p
JOIN sede s ON s.id_sede = p.id_sede
JOIN carrera car ON car.id_sede = s.id_sede
JOIN curso c ON c.id_carrera = car.id_carrera
JOIN matricula m ON c.id_curso = m.id_curso
JOIN estudiante e ON m.id_estudiante = e.id_estudiante
LEFT JOIN nota n ON m.id_matricula = n.id_matricula
WHERE p.id_sede = 1 AND e.id_sede = 1
ORDER BY p.nombre, c.nombre, e.nombre;
