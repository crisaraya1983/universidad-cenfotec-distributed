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

-- Crear usuario de replicación
CREATE USER 'replicacion'@'%' IDENTIFIED BY 'repl123';
GRANT REPLICATION SLAVE ON *.* TO 'replicacion'@'%';
GRANT SELECT ON cenfotec_central.sede TO 'replicacion'@'%';
GRANT SELECT ON cenfotec_central.carrera TO 'replicacion'@'%';
GRANT SELECT ON cenfotec_central.profesor TO 'replicacion'@'%';
FLUSH PRIVILEGES;

-- Mensaje de confirmación
SELECT 'Base de datos SEDE CENTRAL inicializada correctamente' AS mensaje;