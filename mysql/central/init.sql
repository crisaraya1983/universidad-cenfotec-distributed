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
INSERT INTO estudiante (nombre, email, id_sede) VALUES
('Andrea López Vargas', 'andrea.lopez@estudiante.cenfotec.ac.cr', 1),
('Miguel Rojas Hernández', 'miguel.rojas@estudiante.cenfotec.ac.cr', 1),
('Patricia Méndez Castro', 'patricia.mendez@estudiante.cenfotec.ac.cr', 1),
('Fernando Gutiérrez Mora', 'fernando.gutierrez@estudiante.cenfotec.ac.cr', 1),
('Isabella Vargas Solís', 'isabella.vargas@estudiante.cenfotec.ac.cr', 1);

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

-- Mensaje de confirmación
SELECT 'Base de datos SEDE CENTRAL inicializada correctamente' AS mensaje;