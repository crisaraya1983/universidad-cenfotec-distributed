# 🏛️ Sistema de Base de Datos Distribuida - Universidad Cenfotec

## 📋 Descripción del Proyecto

Sistema distribuido que demuestra fragmentación horizontal, vertical y mixta para la Universidad Cenfotec con tres sedes: Central (San José), San Carlos y Heredia.

### 🎯 Objetivos Académicos
- ✅ Fragmentación horizontal (estudiantes por sede)
- ✅ Fragmentación vertical (datos administrativos vs académicos)
- ✅ Fragmentación mixta (combinación de ambas)
- ✅ Replicación de datos maestros
- ✅ Autonomía operacional por sede

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SEDE CENTRAL  │    │  SEDE SAN CARLOS│    │   SEDE HEREDIA  │
│  (Nodo Maestro) │    │ (Nodo Regional) │    │ (Nodo Regional) │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Planillas     │    │ • Estudiantes   │    │ • Estudiantes   │
│ • Pagarés       │    │ • Matrículas    │    │ • Matrículas    │
│ • Empleados     │    │ • Calificaciones│    │ • Calificaciones│
│                 │    │ • Pagos         │    │ • Pagos         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ NGINX BALANCER  │
                    │ Redis Cache     │
                    └─────────────────┘
```

## 🛠️ Tecnologías Utilizadas

- **Docker & Docker Compose**: Containerización
- **MySQL 8.0**: Base de datos relacional
- **NGINX**: Load balancer y proxy reverso
- **Redis**: Cache distribuido
- **phpMyAdmin**: Interfaz web de administración

## 📋 Prerrequisitos

### Software Requerido:
- ✅ **Docker Desktop** (Windows/Mac/Linux)
- ✅ **Git** para clonar el repositorio
- ✅ **8GB RAM mínimo** asignados a Docker
- ✅ **Puertos libres:** 80, 3306, 3307, 3308, 6379, 8080

### Verificar Prerrequisitos:
```bash
# Verificar Docker
docker --version
docker-compose --version

# Verificar puertos libres (Windows)
netstat -ano | findstr :3306
netstat -ano | findstr :3307
netstat -ano | findstr :3308
netstat -ano | findstr :80
netstat -ano | findstr :8080
netstat -ano | findstr :6379
```

## 🚀 Instalación y Configuración

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/crisaraya1983/universidad-cenfotec-distributed.git
cd universidad-cenfotec-distributed
```

### Paso 2: Verificar Estructura de Archivos
```
universidad-cenfotec-distributed/
├── docker-compose.yml          ✅
├── nginx/
│   └── nginx.conf              ✅
├── redis/
│   └── redis.conf              ✅
├── mysql/
│   ├── central/
│   │   ├── init.sql            ✅
│   │   └── my.cnf              ✅
│   ├── sancarlos/
│   │   ├── init.sql            ✅
│   │   └── my.cnf              ✅
│   └── heredia/
│       ├── init.sql            ✅
│       └── my.cnf              ✅
├── README.md                   ✅
└── .gitignore                  ✅
```

### Paso 3: Levantar el Sistema
```bash
# Construir y levantar todos los contenedores
docker-compose up -d

# Verificar que todos los servicios estén corriendo
docker-compose ps
```

### Paso 4: Verificar el Estado
```bash
# Debería mostrar 6 contenedores running:
# ✅ mysql-central-cenfotec
# ✅ mysql-sancarlos-cenfotec  
# ✅ mysql-heredia-cenfotec
# ✅ nginx-cenfotec
# ✅ redis-cenfotec
# ✅ phpmyadmin-cenfotec
```

## 🌐 Acceso al Sistema

### URLs de Acceso:
- 🏠 **Sistema Principal**: http://localhost
- 🛠️ **phpMyAdmin**: http://localhost:8080
- ⚡ **Redis**: localhost:6379

### Conexiones MySQL Directas:
- 🏛️ **Central**: localhost:3306
- 🏢 **San Carlos**: localhost:3307  
- 🏫 **Heredia**: localhost:3308

### Credenciales:
- 👤 **Usuario**: `root`
- 🔐 **Contraseña**: `admin123`

## 🧪 Verificación de la Fragmentación

### Método 1: Comandos Docker (Rápido)
```bash
# Verificar Central
docker exec -it mysql-central-cenfotec mysql -u root -padmin123 -e "USE cenfotec_central; SHOW TABLES;"

# Verificar San Carlos
docker exec -it mysql-sancarlos-cenfotec mysql -u root -padmin123 -e "USE cenfotec_sancarlos; SHOW TABLES;"

# Verificar Heredia  
docker exec -it mysql-heredia-cenfotec mysql -u root -padmin123 -e "USE cenfotec_heredia; SHOW TABLES;"
```

### Método 2: VS Code MySQL Extension
1. Instalar extensión "MySQL" en VS Code
2. Configurar 3 conexiones:
   - Central: `172.20.0.10:3306`
   - San Carlos: `172.20.0.11:3306`
   - Heredia: `172.20.0.12:3306`

### Método 3: phpMyAdmin
1. Ir a http://localhost:8080
2. Cambiar servidor manualmente para otras sedes

## 📊 Consultas de Demostración

### Fragmentación Vertical (Central vs Regionales)
```sql
-- En Central: Solo datos administrativos
USE cenfotec_central;
SELECT 'Central-Planillas' as tipo, COUNT(*) as registros FROM planilla
UNION SELECT 'Central-Pagares', COUNT(*) FROM pagare;

-- En San Carlos: Solo datos académicos  
USE cenfotec_sancarlos;
SELECT 'SanCarlos-Estudiantes' as tipo, COUNT(*) as registros FROM estudiante
UNION SELECT 'SanCarlos-Matriculas', COUNT(*) FROM matricula;
```

### Fragmentación Horizontal (Estudiantes por sede)
```sql
-- Verificar estudiantes por sede
-- San Carlos
SELECT e.nombre, 'San Carlos' as sede FROM estudiante e LIMIT 3;

-- Heredia  
SELECT e.nombre, 'Heredia' as sede FROM estudiante e LIMIT 3;
```

## 🔧 Comandos Útiles

### Gestión de Contenedores:
```bash
# Ver logs de un servicio específico
docker-compose logs mysql-central
docker-compose logs nginx-loadbalancer

# Reiniciar un servicio
docker-compose restart mysql-sancarlos

# Parar todo el sistema
docker-compose down

# Parar y eliminar volúmenes (⚠️ Borra datos)
docker-compose down -v

# Ver estado de recursos
docker stats
```

### Backup de Datos:
```bash
# Backup de cada sede
docker exec mysql-central-cenfotec mysqldump -u root -padmin123 cenfotec_central > backup_central.sql
docker exec mysql-sancarlos-cenfotec mysqldump -u root -padmin123 cenfotec_sancarlos > backup_sancarlos.sql
docker exec mysql-heredia-cenfotec mysqldump -u root -padmin123 cenfotec_heredia > backup_heredia.sql
```

## 🚨 Solución de Problemas

### Error: "Port already in use"
```bash
# Ver qué proceso usa el puerto
netstat -ano | findstr :3306

# Parar Docker y reiniciar
docker-compose down
docker-compose up -d
```

### Error: "No space left on device"
```bash
# Limpiar Docker
docker system prune -a
docker volume prune
```

### Contenedor no inicia:
```bash
# Ver logs detallados
docker-compose logs [nombre-contenedor]
```

### Reset completo del sistema:
```bash
# ⚠️ CUIDADO: Esto borra TODO
docker-compose down -v
docker system prune -a
docker-compose up -d
```

## 📁 Estructura de Datos

### Sede Central (Datos Administrativos):
- `sede` - Información de sedes
- `carrera` - Carreras por sede  
- `profesor` - Profesores por sede
- `planilla` - Nóminas (SOLO CENTRAL)
- `pagare` - Pagarés estudiantiles (SOLO CENTRAL)

### Sedes Regionales (Datos Académicos):
- `estudiante` - Estudiantes por sede
- `curso` - Cursos por carrera
- `matricula` - Matrículas de estudiantes
- `asistencia` - Registro de asistencias
- `nota` - Calificaciones
- `pago` - Pagos estudiantiles

## 🎯 Resultados Esperados

Al completar la instalación deberías tener:
- ✅ 6 contenedores corriendo
- ✅ 3 bases de datos independientes
- ✅ Fragmentación horizontal demostrada
- ✅ Fragmentación vertical implementada
- ✅ Load balancer funcional
- ✅ Cache Redis operativo
- ✅ Datos de prueba poblados

## 👥 Colaboradores

- [Tu Nombre]
- [Compañero 1]
- [Compañero 2]

## 📚 Referencias Académicas

- Silberschatz, A., Korth, H. F., & Sudarshan, S. (2020). Database System Concepts
- Özsu, M. T., & Valduriez, P. (2020). Principles of Distributed Database Systems

---

## 🆘 Soporte

Si tienes problemas:
1. Revisar la sección "Solución de Problemas"
2. Verificar que Docker Desktop esté corriendo
3. Contactar al equipo de desarrollo

**¡El sistema está listo para demostración académica!** 🎉