-- ========================================
-- INICIALIZACIÓN BASE DE DATOS - SEDE SAN CARLOS
-- ========================================

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS cenfotec_sancarlos 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE cenfotec_sancarlos;

-- ========================================
-- TABLAS REPLICADAS DESDE CENTRAL
-- ========================================

-- Tabla de Sedes
CREATE TABLE sede (
    id_sede INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    direccion TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nombre (nombre)
) ENGINE=InnoDB;

-- Tabla de Carreras
CREATE TABLE carrera (
    id_carrera INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    id_sede INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sede (id_sede),
    FOREIGN KEY (id_sede) REFERENCES sede(id_sede) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Profesores
CREATE TABLE profesor (
    id_profesor INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    id_sede INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sede (id_sede),
    INDEX idx_email (email),
    FOREIGN KEY (id_sede) REFERENCES sede(id_sede) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- TABLAS ESPECÍFICAS DE SAN CARLOS
-- ========================================

-- Tabla de Estudiantes
CREATE TABLE estudiante (
    id_estudiante INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    id_sede INT NOT NULL DEFAULT 2,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('activo', 'transferido', 'inactivo'),
    sede_actual INT DEFAULT 1,
    fecha_transferencia TIMESTAMP,
    INDEX idx_sede (id_sede),
    INDEX idx_email (email),
    FOREIGN KEY (id_sede) REFERENCES sede(id_sede) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Cursos
CREATE TABLE curso (
    id_curso INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    id_carrera INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_carrera (id_carrera),
    FOREIGN KEY (id_carrera) REFERENCES carrera(id_carrera) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Matrículas
CREATE TABLE matricula (
    id_matricula INT PRIMARY KEY AUTO_INCREMENT,
    id_estudiante INT NOT NULL,
    id_curso INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_estudiante (id_estudiante),
    INDEX idx_curso (id_curso),
    UNIQUE KEY unique_matricula (id_estudiante, id_curso),
    FOREIGN KEY (id_estudiante) REFERENCES estudiante(id_estudiante) ON UPDATE CASCADE,
    FOREIGN KEY (id_curso) REFERENCES curso(id_curso) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Asistencias
CREATE TABLE asistencia (
    id_asistencia INT PRIMARY KEY AUTO_INCREMENT,
    id_matricula INT NOT NULL,
    fecha DATE NOT NULL,
    presente BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_matricula (id_matricula),
    INDEX idx_fecha (fecha),
    FOREIGN KEY (id_matricula) REFERENCES matricula(id_matricula) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Notas
CREATE TABLE nota (
    id_nota INT PRIMARY KEY AUTO_INCREMENT,
    id_matricula INT NOT NULL,
    nota DECIMAL(4,2) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_matricula (id_matricula),
    FOREIGN KEY (id_matricula) REFERENCES matricula(id_matricula) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Pagos
CREATE TABLE pago (
    id_pago INT PRIMARY KEY AUTO_INCREMENT,
    id_estudiante INT NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    fecha DATE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_estudiante (id_estudiante),
    INDEX idx_fecha (fecha),
    FOREIGN KEY (id_estudiante) REFERENCES estudiante(id_estudiante) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- ========================================
-- TABLA DE SINCRONIZACIÓN
-- ========================================

-- Tabla para cola de sincronización con otras sedes
CREATE TABLE sync_queue (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tabla_origen VARCHAR(100) NOT NULL,
    operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    registro_id INT NOT NULL,
    datos JSON NOT NULL,
    sede_destino VARCHAR(20),
    procesado BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_procesamiento TIMESTAMP NULL,
    intentos INT DEFAULT 0,
    ultimo_error TEXT,
    INDEX idx_procesado (procesado),
    INDEX idx_sede_destino (sede_destino),
    INDEX idx_fecha_creacion (fecha_creacion)
) ENGINE=InnoDB;

-- ========================================
-- DATOS INICIALES DE PRUEBA
-- ========================================

-- Insertar datos temporales
INSERT INTO sede (id_sede, nombre, direccion) VALUES
(1, 'Central', 'San José, Costa Rica'),
(2, 'San Carlos', 'Ciudad Quesada, Alajuela'),
(3, 'Heredia', 'Heredia Centro, Heredia');

INSERT INTO carrera (id_carrera, nombre, id_sede) VALUES
(2, 'Ingeniería en Software', 2),
(7, 'Mercadeo Digital', 2);

INSERT INTO profesor (id_profesor, nombre, email, id_sede) VALUES
(3, 'Luis Hernández Castro', 'luis.hernandez@cenfotec.ac.cr', 2),
(4, 'Ana Jiménez Solano', 'ana.jimenez@cenfotec.ac.cr', 2);

-- Insertar estudiantes
INSERT INTO estudiante (nombre, email, id_sede, estado, sede_actual, fecha_transferencia) VALUES
('Juan Pérez López', 'juan.perez@estudiante.cenfotec.ac.cr', 2, 'activo', 2, NULL),
('María Rodríguez Vargas', 'maria.rodriguez@estudiante.cenfotec.ac.cr', 2, 'activo', 2, NULL),
('Carlos González Mora', 'carlos.gonzalez@estudiante.cenfotec.ac.cr', 2, 'activo', 2, NULL),
('Ana Jiménez Castro', 'ana.jimenez@estudiante.cenfotec.ac.cr', 2, 'activo', 2, NULL),
('Luis Hernández Solano', 'luis.hernandez@estudiante.cenfotec.ac.cr', 2, 'activo', 2, NULL);

-- Insertar cursos
INSERT INTO curso (nombre, id_carrera) VALUES
('Introducción a la Programación', 2),
('Programación Orientada a Objetos', 2),
('Bases de Datos', 2),
('Fundamentos de Marketing', 7),
('Marketing Digital Avanzado', 7);

-- Insertar matrículas
INSERT INTO matricula (id_estudiante, id_curso) VALUES
(1, 1), (1, 2),
(2, 1), (2, 3),
(3, 2), (3, 3),
(4, 4), (4, 5),
(5, 1), (5, 4);

-- Insertar asistencias
INSERT INTO asistencia (id_matricula, fecha, presente) VALUES
(1, '2024-01-15', TRUE),
(1, '2024-01-16', TRUE),
(1, '2024-01-17', FALSE),
(2, '2024-01-15', TRUE),
(3, '2024-01-15', TRUE);

-- Insertar notas
INSERT INTO nota (id_matricula, nota) VALUES
(1, 85.5),
(2, 92.0),
(3, 78.5),
(4, 88.0),
(5, 91.5);

-- Insertar pagos
INSERT INTO pago (id_estudiante, monto, fecha) VALUES
(1, 150000.00, '2024-01-15'),
(2, 150000.00, '2024-01-20'),
(3, 150000.00, '2024-01-18'),
(4, 150000.00, '2024-01-22'),
(5, 150000.00, '2024-01-25');

-- ============================
-- VISTAS PARA ROL ESTUDIANTE 
-- ============================

-- Vista de materias y notas por estudiante
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
WHERE e.id_sede = 2
ORDER BY e.nombre, c.nombre;

-- Vista de historial de pagos del estudiante
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
WHERE e.id_sede = 2
ORDER BY p.fecha DESC;

-- Vista consolidada del expediente estudiantil
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
WHERE e.id_sede = 2
GROUP BY e.id_estudiante, e.nombre, e.email, e.estado, e.fecha_creacion
ORDER BY e.nombre;

-- ===========================
-- VISTAS PARA ROL PROFESOR
-- ===========================

-- Vista de estudiantes por curso del profesor
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
WHERE p.id_sede = 2 AND e.id_sede = 2
ORDER BY p.nombre, c.nombre, e.nombre;

-- Vista resumen de cursos del profesor
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
WHERE p.id_sede = 2 AND e.id_sede = 2
GROUP BY p.id_profesor, c.id_curso
ORDER BY p.nombre, c.nombre;


-- Mensaje de confirmación
SELECT 'Base de datos SEDE SAN CARLOS inicializada correctamente' AS mensaje;