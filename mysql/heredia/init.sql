-- ========================================
-- INICIALIZACIÓN BASE DE DATOS - SEDE HEREDIA
-- Universidad Cenfotec - Nodo Regional
-- ========================================

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS cenfotec_heredia 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE cenfotec_heredia;

-- ========================================
-- TABLAS REPLICADAS DESDE CENTRAL
-- (Estas se poblarán automáticamente vía replicación)
-- ========================================

-- Tabla de Sedes (REPLICADA desde Central)
CREATE TABLE sede (
    id_sede INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    direccion TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_nombre (nombre)
) ENGINE=InnoDB;

-- Tabla de Carreras (REPLICADA desde Central)
CREATE TABLE carrera (
    id_carrera INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    id_sede INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sede (id_sede),
    FOREIGN KEY (id_sede) REFERENCES sede(id_sede) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Profesores (REPLICADA desde Central)
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
-- TABLAS ESPECÍFICAS DE HEREDIA
-- (Fragmentación Horizontal - Solo estudiantes de Heredia)
-- ========================================

-- Tabla de Estudiantes (SOLO HEREDIA)
CREATE TABLE estudiante (
    id_estudiante INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    id_sede INT NOT NULL DEFAULT 3, -- Heredia
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sede (id_sede),
    INDEX idx_email (email),
    FOREIGN KEY (id_sede) REFERENCES sede(id_sede) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Cursos (SOLO HEREDIA)
CREATE TABLE curso (
    id_curso INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    id_carrera INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_carrera (id_carrera),
    FOREIGN KEY (id_carrera) REFERENCES carrera(id_carrera) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Matrículas (SOLO HEREDIA)
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

-- Tabla de Asistencias (SOLO HEREDIA)
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

-- Tabla de Notas (SOLO HEREDIA)
CREATE TABLE nota (
    id_nota INT PRIMARY KEY AUTO_INCREMENT,
    id_matricula INT NOT NULL,
    nota DECIMAL(4,2) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_matricula (id_matricula),
    FOREIGN KEY (id_matricula) REFERENCES matricula(id_matricula) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Pagos (SOLO HEREDIA)
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

-- Insertar datos temporales (estos vendrán de replicación en realidad)
INSERT INTO sede (id_sede, nombre, direccion) VALUES
(1, 'Central', 'San José, Costa Rica'),
(2, 'San Carlos', 'Ciudad Quesada, Alajuela'),
(3, 'Heredia', 'Heredia Centro, Heredia');

INSERT INTO carrera (id_carrera, nombre, id_sede) VALUES
(3, 'Ingeniería en Software', 3),
(5, 'Diseño Gráfico Digital', 3),
(8, 'Mercadeo Digital', 3);

INSERT INTO profesor (id_profesor, nombre, email, id_sede) VALUES
(5, 'Roberto Chaves Alpízar', 'roberto.chaves@cenfotec.ac.cr', 3),
(6, 'Silvia Morales Pérez', 'silvia.morales@cenfotec.ac.cr', 3);

-- Insertar estudiantes de Heredia (Fragmentación Horizontal)
INSERT INTO estudiante (nombre, email, id_sede) VALUES
('Sofía Chaves Morales', 'sofia.chaves@estudiante.cenfotec.ac.cr', 3),
('Diego Mata Rojas', 'diego.mata@estudiante.cenfotec.ac.cr', 3),
('Camila Vargas Solís', 'camila.vargas@estudiante.cenfotec.ac.cr', 3),
('Andrés Quesada Herrera', 'andres.quesada@estudiante.cenfotec.ac.cr', 3),
('Valeria Rojas Camacho', 'valeria.rojas@estudiante.cenfotec.ac.cr', 3);

-- Insertar cursos
INSERT INTO curso (nombre, id_carrera) VALUES
('Introducción a la Programación', 3),
('Desarrollo Web Frontend', 3),
('Fundamentos de Diseño', 5),
('Diseño Digital Avanzado', 5),
('Estrategias de Marketing', 8);

-- Insertar matrículas
INSERT INTO matricula (id_estudiante, id_curso) VALUES
(1, 1), (1, 2),
(2, 1), (2, 2),
(3, 3), (3, 4),
(4, 5), (4, 1),
(5, 3), (5, 5);

-- Insertar asistencias de ejemplo
INSERT INTO asistencia (id_matricula, fecha, presente) VALUES
(1, '2024-01-15', TRUE),
(1, '2024-01-16', TRUE),
(1, '2024-01-17', FALSE),
(2, '2024-01-15', TRUE),
(3, '2024-01-15', TRUE);

-- Insertar notas de ejemplo
INSERT INTO nota (id_matricula, nota) VALUES
(1, 90.0),
(2, 87.5),
(3, 94.0),
(4, 82.5),
(5, 89.0);

-- Insertar pagos de ejemplo
INSERT INTO pago (id_estudiante, monto, fecha) VALUES
(1, 150000.00, '2024-01-10'),
(2, 150000.00, '2024-01-12'),
(3, 150000.00, '2024-01-14'),
(4, 150000.00, '2024-01-16'),
(5, 150000.00, '2024-01-18');

-- Mensaje de confirmación
SELECT 'Base de datos SEDE HEREDIA inicializada correctamente' AS mensaje;