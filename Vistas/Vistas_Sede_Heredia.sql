-- ========================================
-- VISTAS PARA ROL ESTUDIANTE
-- ========================================

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
WHERE e.id_sede = 3 
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
WHERE e.id_sede = 3
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
WHERE e.id_sede = 3
GROUP BY e.id_estudiante, e.nombre, e.email, e.estado, e.fecha_creacion
ORDER BY e.nombre;

-- ========================================
-- VISTAS PARA ROL PROFESOR
-- ========================================

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
WHERE p.id_sede = 3 AND e.id_sede = 3
ORDER BY p.nombre, c.nombre, e.nombre;

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
WHERE p.id_sede = 3 AND e.id_sede = 3
GROUP BY p.id_profesor, c.id_curso
ORDER BY p.nombre, c.nombre;
