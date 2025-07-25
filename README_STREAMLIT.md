# 🎓 Interfaz Streamlit - Sistema Distribuido Cenfotec

## 📋 Descripción

Esta interfaz web interactiva permite visualizar y demostrar todas las funcionalidades del sistema de base de datos distribuida de la Universidad Cenfotec. Proporciona dashboards, herramientas de monitoreo y simulaciones de transacciones distribuidas.

## 🚀 Instalación Rápida

### Prerrequisitos
- Python 3.8 o superior
- Docker Desktop ejecutándose
- Sistema de base de datos distribuida levantado (`docker-compose up -d`)

### Windows
```bash
# En la carpeta raíz del proyecto
start-streamlit.bat
```

### Linux/Mac
```bash
# En la carpeta raíz del proyecto
chmod +x start-streamlit.sh
./start-streamlit.sh
```

### Instalación Manual
```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r streamlit/requirements.txt

# 4. Iniciar Streamlit
cd streamlit
streamlit run app.py
```

## 📱 Páginas Disponibles

### 1. 🏠 Dashboard Principal (`app.py`)
- **Estado de conexiones**: Verifica todas las conexiones a bases de datos y Redis
- **Métricas generales**: Estudiantes, profesores, matrículas por sede
- **Distribución de datos**: Visualización de la fragmentación
- **Actividad reciente**: Últimas transacciones del sistema

### 2. 📊 Fragmentación (`pages/2_📊_Fragmentacion.py`)
- **Conceptos**: Explicación visual de tipos de fragmentación
- **Fragmentación Horizontal**: Distribución de estudiantes por sede
- **Fragmentación Vertical**: Separación de datos administrativos/académicos
- **Fragmentación Mixta**: Combinación de técnicas

### 3. 🔄 Replicación (`pages/3_🔄_Replicacion.py`)
- **Master-Slave**: Visualización de la replicación desde Central
- **Sincronización**: Simulación de transferencias entre sedes
- **Monitoreo**: Estado en tiempo real de la replicación

### 4. 💼 Transacciones (`pages/4_💼_Transacciones.py`)
- **Consultas Globales**: Queries que involucran múltiples sedes
- **Pago Global**: Simulación de transacción distribuida
- **Reportes Consolidados**: Generación de reportes ejecutivos
- **Vistas de Usuario**: Diferentes vistas según roles

### 5. 📈 Monitoreo (`pages/5_📈_Monitoreo.py`)
- **Dashboard General**: Estado completo del sistema
- **Recursos**: CPU, RAM, Disco por sede
- **Rendimiento**: Análisis de queries y optimización
- **Diagnóstico**: Herramientas para troubleshooting

## 🔧 Configuración

### Variables de Entorno
Crea un archivo `.env` en la carpeta `streamlit/` (opcional):

```env
# Conexiones MySQL
MYSQL_CENTRAL_HOST=localhost
MYSQL_CENTRAL_PORT=3306
MYSQL_SANCARLOS_HOST=localhost
MYSQL_SANCARLOS_PORT=3307
MYSQL_HEREDIA_HOST=localhost
MYSQL_HEREDIA_PORT=3308

# Credenciales
MYSQL_USER=root
MYSQL_PASSWORD=admin123

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Personalización de la UI
Edita `streamlit/.streamlit/config.toml` para cambiar:
- Colores del tema
- Configuración del servidor
- Límites de carga
- Opciones de interfaz

## 🎯 Casos de Uso para Demostración

### Demo 1: Fragmentación Horizontal
1. Ir a la página de Fragmentación
2. Seleccionar la pestaña "Fragmentación Horizontal"
3. Mostrar cómo los estudiantes están distribuidos por sede
4. Ejecutar queries para verificar que cada sede solo tiene sus datos

### Demo 2: Replicación Master-Slave
1. Ir a la página de Replicación
2. En la pestaña "Master-Slave", verificar datos maestros
3. Simular agregar una nueva carrera en Central
4. Ver cómo se propaga a las sedes regionales

### Demo 3: Transacción Distribuida
1. Ir a la página de Transacciones
2. En "Procesamiento de Pago Global", llenar el formulario
3. Observar los pasos de la transacción distribuida
4. Ver el log de auditoría generado

### Demo 4: Monitoreo en Tiempo Real
1. Ir a la página de Monitoreo
2. Activar "Auto-actualizar" para ver cambios en tiempo real
3. Usar herramientas de diagnóstico para verificar el sistema
4. Revisar métricas históricas y tendencias

## 🛠️ Solución de Problemas

### Error: "No se puede conectar a MySQL"
```bash
# Verificar que Docker esté corriendo
docker ps

# Verificar los contenedores específicos
docker-compose ps

# Reiniciar los servicios
docker-compose restart
```

### Error: "ModuleNotFoundError"
```bash
# Asegurarse de estar en el entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Reinstalar dependencias
pip install -r streamlit/requirements.txt
```

### La página no carga o está lenta
- Verificar que todas las bases de datos estén activas
- Limpiar el cache de Redis desde la interfaz
- Reducir el período de datos en consultas históricas

## 📊 Arquitectura de la Aplicación

```
streamlit/
├── app.py                    # Dashboard principal
├── config.py                 # Configuración de conexiones
├── requirements.txt          # Dependencias Python
├── pages/                    # Páginas adicionales
│   ├── 2_📊_Fragmentacion.py
│   ├── 3_🔄_Replicacion.py
│   ├── 4_💼_Transacciones.py
│   └── 5_📈_Monitoreo.py
├── utils/                    # Utilidades compartidas
│   ├── __init__.py
│   ├── db_connections.py     # Gestión de conexiones
│   └── queries.py            # Consultas SQL predefinidas
└── .streamlit/              # Configuración de Streamlit
    └── config.toml
```

## 🔐 Seguridad

- Las credenciales están configuradas en `config.py`
- No se exponen passwords en la interfaz
- Las conexiones son solo dentro de la red Docker
- El acceso es de solo lectura para la mayoría de operaciones

## 🚀 Despliegue en Producción

Para un entorno de producción:

1. **Usar HTTPS**: Configurar un proxy reverso con certificados SSL
2. **Autenticación**: Implementar login con `streamlit-authenticator`
3. **Variables de entorno**: Usar secretos en lugar de hardcodear credenciales
4. **Límites**: Configurar rate limiting y timeouts
5. **Logs**: Implementar logging centralizado

## 📚 Recursos Adicionales

- [Documentación de Streamlit](https://docs.streamlit.io)
- [Guía de MySQL Connector](https://dev.mysql.com/doc/connector-python/en/)
- [Redis Python Client](https://redis-py.readthedocs.io/)
- [Plotly para Python](https://plotly.com/python/)

## 🤝 Contribución

Para agregar nuevas funcionalidades:

1. Crear nueva página en `pages/` siguiendo la nomenclatura
2. Agregar queries necesarias en `utils/queries.py`
3. Actualizar la documentación
4. Probar con todas las sedes activas

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs de Docker: `docker-compose logs`
2. Verifica el estado en el Dashboard principal
3. Usa las herramientas de diagnóstico en la página de Monitoreo
4. Consulta la documentación del proyecto principal

---

**Proyecto Final - Base de Datos Distribuidas**  
Universidad Cenfotec - 2025