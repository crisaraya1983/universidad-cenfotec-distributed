-- ========================================
-- INICIALIZACIÓN BASE DE DATOS - SEDE SAN CARLOS
-- Universidad Cenfotec - Nodo Regional
-- ========================================

-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS cenfotec_sancarlos 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE cenfotec_sancarlos;

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
-- TABLAS ESPECÍFICAS DE SAN CARLOS
-- (Fragmentación Horizontal - Solo estudiantes de San Carlos)
-- ========================================

-- Tabla de Estudiantes (SOLO SAN CARLOS)
CREATE TABLE estudiante (
    id_estudiante INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    id_sede INT NOT NULL DEFAULT 2, -- San Carlos
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sede (id_sede),
    INDEX idx_email (email),
    FOREIGN KEY (id_sede) REFERENCES sede(id_sede) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Cursos (SOLO SAN CARLOS)
CREATE TABLE curso (
    id_curso INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(255) NOT NULL,
    id_carrera INT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_carrera (id_carrera),
    FOREIGN KEY (id_carrera) REFERENCES carrera(id_carrera) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Matrículas (SOLO SAN CARLOS)
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

-- Tabla de Asistencias (SOLO SAN CARLOS)
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

-- Tabla de Notas (SOLO SAN CARLOS)
CREATE TABLE nota (
    id_nota INT PRIMARY KEY AUTO_INCREMENT,
    id_matricula INT NOT NULL,
    nota DECIMAL(4,2) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_matricula (id_matricula),
    FOREIGN KEY (id_matricula) REFERENCES matricula(id_matricula) ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Tabla de Pagos (SOLO SAN CARLOS)
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
(2, 'Ingeniería en Software', 2),
(7, 'Mercadeo Digital', 2);

INSERT INTO profesor (id_profesor, nombre, email, id_sede) VALUES
(3, 'Luis Hernández Castro', 'luis.hernandez@cenfotec.ac.cr', 2),
(4, 'Ana Jiménez Solano', 'ana.jimenez@cenfotec.ac.cr', 2);

-- Insertar estudiantes de San Carlos (Fragmentación Horizontal)
INSERT INTO estudiante (nombre, email, id_sede) VALUES
('Juan Pérez López', 'juan.perez@estudiante.cenfotec.ac.cr', 2),
('María Rodríguez Vargas', 'maria.rodriguez@estudiante.cenfotec.ac.cr', 2),
('Carlos González Mora', 'carlos.gonzalez@estudiante.cenfotec.ac.cr', 2),
('Ana Jiménez Castro', 'ana.jimenez@estudiante.cenfotec.ac.cr', 2),
('Luis Hernández Solano', 'luis.hernandez@estudiante.cenfotec.ac.cr', 2);

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

-- Insertar asistencias de ejemplo
INSERT INTO asistencia (id_matricula, fecha, presente) VALUES
(1, '2024-01-15', TRUE),
(1, '2024-01-16', TRUE),
(1, '2024-01-17', FALSE),
(2, '2024-01-15', TRUE),
(3, '2024-01-15', TRUE);

-- Insertar notas de ejemplo
INSERT INTO nota (id_matricula, nota) VALUES
(1, 85.5),
(2, 92.0),
(3, 78.5),
(4, 88.0),
(5, 91.5);

-- Insertar pagos de ejemplo
INSERT INTO pago (id_estudiante, monto, fecha) VALUES
(1, 150000.00, '2024-01-15'),
(2, 150000.00, '2024-01-20'),
(3, 150000.00, '2024-01-18'),
(4, 150000.00, '2024-01-22'),
(5, 150000.00, '2024-01-25');

-- Mensaje de confirmación
SELECT 'Base de datos SEDE SAN CARLOS inicializada correctamente' AS mensaje;