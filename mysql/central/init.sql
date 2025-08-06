-- ========================================
-- INICIALIZACIÓN BASE DE DATOS - SEDE CENTRAL
-- Universidad Cenfotec - Nodo Maestro
-- ========================================

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS cenfotec_central 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE cenfotec_central;

-- ========================================
-- TABLAS MAESTRAS (SE REPLICAN A REGIONALES)
-- ========================================

-- Tabla de Sedes
CREATE TABLE sede (
    id_sede INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    direccion TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nombre (nombre)
) ENGINE=InnoDB;

-- Tabla de Carreras (Fragmentación Vertical - Se replica a regionales)
CREATE TABLE carrera (
    id_carrera INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    id_sede INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sede (id_sede),
    FOREIGN KEY (id_sede) REFERENCES sede(id_sede) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Profesores (Fragmentación Vertical - Se replica a regionales)
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
-- TABLAS ESPECÍFICAS DE SEDE CENTRAL
-- (Fragmentación Vertical - Solo en Central)
-- ========================================

-- Tabla de Planillas (SOLO CENTRAL)
CREATE TABLE planilla (
    id_planilla INT PRIMARY KEY AUTO_INCREMENT,
    id_profesor INT NOT NULL,
    salario DECIMAL(10,2) NOT NULL,
    mes VARCHAR(20) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_profesor (id_profesor),
    INDEX idx_mes (mes),
    FOREIGN KEY (id_profesor) REFERENCES profesor(id_profesor) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Pagarés (SOLO CENTRAL)
CREATE TABLE pagare (
    id_pagare INT PRIMARY KEY AUTO_INCREMENT,
    id_estudiante INT NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    vencimiento DATE NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_estudiante (id_estudiante),
    INDEX idx_vencimiento (vencimiento)
) ENGINE=InnoDB;

-- ========================================
-- TABLAS ACADÉMICAS DE SEDE CENTRAL
-- (Fragmentación Mixta - Central también tiene estudiantes)
-- ========================================

-- Tabla de Estudiantes (SEDE CENTRAL)
CREATE TABLE estudiante (
    id_estudiante INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    id_sede INT NOT NULL DEFAULT 1, -- Central
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('activo', 'transferido', 'inactivo'),
    sede_actual INT DEFAULT 1,
    fecha_transferencia TIMESTAMP,
    INDEX idx_sede (id_sede),
    INDEX idx_email (email),
    FOREIGN KEY (id_sede) REFERENCES sede(id_sede) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Cursos (SEDE CENTRAL)
CREATE TABLE curso (
    id_curso INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    id_carrera INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_carrera (id_carrera),
    FOREIGN KEY (id_carrera) REFERENCES carrera(id_carrera) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Matrículas (SEDE CENTRAL)
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

-- Tabla de Notas (SEDE CENTRAL)
CREATE TABLE nota (
    id_nota INT PRIMARY KEY AUTO_INCREMENT,
    id_matricula INT NOT NULL,
    nota DECIMAL(4,2) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_matricula (id_matricula),
    FOREIGN KEY (id_matricula) REFERENCES matricula(id_matricula) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Asistencias (SEDE CENTRAL)
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

-- Tabla de Pagos (SEDE CENTRAL)
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
-- TABLAS DE CONTROL Y SINCRONIZACIÓN
-- ========================================

-- Tabla de log de replicación
CREATE TABLE replication_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    tabla_afectada VARCHAR(100) NOT NULL,
    operacion ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    registro_id INT NOT NULL,
    datos_anteriores JSON,
    datos_nuevos JSON,
    usuario VARCHAR(100),
    timestamp_operacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sede_destino VARCHAR(50),
    estado_replicacion ENUM('pendiente', 'procesado', 'error') DEFAULT 'pendiente',
    INDEX idx_tabla_operacion (tabla_afectada, operacion),
    INDEX idx_timestamp (timestamp_operacion),
    INDEX idx_estado (estado_replicacion)
) ENGINE=InnoDB;


-- Crear tabla de auditoría
CREATE TABLE IF NOT EXISTS transferencia_estudiante (
    id_transferencia INT PRIMARY KEY AUTO_INCREMENT,
    id_estudiante INT,
    sede_origen INT,
    sede_destino INT,
    fecha_transferencia TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('completada', 'revertida'),
    motivo TEXT,
    FOREIGN KEY (id_estudiante) REFERENCES estudiante(id_estudiante)
);

-- ========================================
-- DATOS INICIALES DE PRUEBA
-- ========================================

-- Insertar sedes
INSERT INTO sede (id_sede, nombre, direccion) VALUES
(1, 'Central', 'San José, Costa Rica'),
(2, 'San Carlos', 'Ciudad Quesada, Alajuela'),
(3, 'Heredia', 'Heredia Centro, Heredia');

-- Insertar carreras
INSERT INTO carrera (nombre, id_sede) VALUES
('Ingeniería en Software', 1),
('Ingeniería en Software', 2),
('Ingeniería en Software', 3),
('Diseño Gráfico Digital', 1),
('Diseño Gráfico Digital', 3),
('Mercadeo Digital', 1),
('Mercadeo Digital', 2),
('Mercadeo Digital', 3);

-- Insertar profesores
INSERT INTO profesor (nombre, email, id_sede) VALUES
('Carlos Rodríguez Mora', 'carlos.rodriguez@cenfotec.ac.cr', 1),
('María González Vargas', 'maria.gonzalez@cenfotec.ac.cr', 1),
('Luis Hernández Castro', 'luis.hernandez@cenfotec.ac.cr', 2),
('Ana Jiménez Solano', 'ana.jimenez@cenfotec.ac.cr', 2),
('Roberto Chaves Alpízar', 'roberto.chaves@cenfotec.ac.cr', 3),
('Silvia Morales Pérez', 'silvia.morales@cenfotec.ac.cr', 3);

-- Insertar planillas de ejemplo
INSERT INTO planilla (id_profesor, salario, mes) VALUES
(1, 1200000.00, '2024-01'),
(2, 1200000.00, '2024-01'),
(1, 1200000.00, '2024-02'),
(2, 1200000.00, '2024-02');

-- Insertar pagarés de ejemplo (con id_estudiante de referencia)
INSERT INTO pagare (id_estudiante, monto, vencimiento) VALUES
(1, 500000.00, '2024-06-30'),
(2, 750000.00, '2024-07-31'),
(3, 600000.00, '2024-08-15');

-- Insertar estudiantes de Central
INSERT INTO estudiante (nombre, email, id_sede, estado, sede_actual, fecha_transferencia) VALUES
('Andrea López Vargas', 'andrea.lopez@estudiante.cenfotec.ac.cr', 1, 'activo', 1, NULL),
('Miguel Rojas Hernández', 'miguel.rojas@estudiante.cenfotec.ac.cr', 1, 'activo', 1, NULL),
('Patricia Méndez Castro', 'patricia.mendez@estudiante.cenfotec.ac.cr', 1, 'activo', 1, NULL),
('Fernando Gutiérrez Mora', 'fernando.gutierrez@estudiante.cenfotec.ac.cr', 1, 'activo', 1, NULL),
('Isabella Vargas Solís', 'isabella.vargas@estudiante.cenfotec.ac.cr', 1, 'activo', 1, NULL);

-- Insertar cursos para Central
INSERT INTO curso (nombre, id_carrera) VALUES
('Matemáticas Avanzadas', 1),
('Algoritmos y Estructuras de Datos', 1),
('Gestión de Proyectos', 6),
('Análisis de Mercados', 6),
('Diseño de Interfaces', 4);

-- Insertar matrículas
INSERT INTO matricula (id_estudiante, id_curso) VALUES
(1, 1), (1, 2),
(2, 1), (2, 3),
(3, 3), (3, 4),
(4, 4), (4, 5),
(5, 2), (5, 5);

-- Insertar notas
INSERT INTO nota (id_matricula, nota) VALUES
(1, 95.0),
(2, 89.5),
(3, 92.0),
(4, 87.5),
(5, 93.5);

-- Insertar asistencias
INSERT INTO asistencia (id_matricula, fecha, presente) VALUES
(1, '2024-01-15', TRUE),
(1, '2024-01-16', TRUE),
(2, '2024-01-15', TRUE),
(3, '2024-01-15', FALSE),
(4, '2024-01-15', TRUE);

-- Insertar pagos
INSERT INTO pago (id_estudiante, monto, fecha) VALUES
(1, 200000.00, '2024-01-10'),
(2, 200000.00, '2024-01-12'),
(3, 200000.00, '2024-01-14'),
(4, 200000.00, '2024-01-16'),
(5, 200000.00, '2024-01-18');

-- Crear usuario de replicación
CREATE USER 'replicacion'@'%' IDENTIFIED BY 'repl123';
GRANT REPLICATION SLAVE ON *.* TO 'replicacion'@'%';
GRANT SELECT ON cenfotec_central.sede TO 'replicacion'@'%';
GRANT SELECT ON cenfotec_central.carrera TO 'replicacion'@'%';
GRANT SELECT ON cenfotec_central.profesor TO 'replicacion'@'%';
FLUSH PRIVILEGES;

----------------------------------Vistas

-- Mensaje de confirmación
SELECT 'Base de datos SEDE CENTRAL inicializada correctamente' AS mensaje;

-- ========================================
-- VISTAS PARA ROL ADMINISTRATIVO (CENTRAL)
-- ========================================

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

-- ========================================
-- VISTAS PARA ROL DIRECTIVO (CENTRAL)
-- ========================================

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
    (SELECT SUM(salario) FROM planilla WHERE YEAR(mes) = YEAR(CURDATE())) as gastos_planilla_año,
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
WHERE e.id_sede = 1 -- Solo estudiantes de Central
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
