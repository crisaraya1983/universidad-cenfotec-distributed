"""
Configuración de conexiones para el sistema distribuido Cenfotec
Este archivo centraliza todas las configuraciones de conexión a las bases de datos
y servicios del sistema distribuido, incluyendo usuarios especializados.
"""

import os
from typing import Dict, Any

# Configuración de bases de datos MySQL para Docker interno
# Usando IPs internas de la red Docker
DB_CONFIG = {
    'central': {
        'host': '172.20.0.10',  # IP interna del contenedor MySQL Central
        'port': 3306,
        'user': 'root',
        'password': 'admin123',
        'database': 'cenfotec_central',
        'name': '🏛️ Sede Central',
        'description': 'Base de datos administrativa - Planillas y Pagarés',
        'color': '#1f77b4'  # Azul
    },
    'sancarlos': {
        'host': '172.20.0.11',  # IP interna del contenedor MySQL San Carlos
        'port': 3306,
        'user': 'root',
        'password': 'admin123',
        'database': 'cenfotec_sancarlos',
        'name': '🏢 Sede San Carlos',
        'description': 'Base de datos académica - Estudiantes San Carlos',
        'color': '#ff7f0e'  # Naranja
    },
    'heredia': {
        'host': '172.20.0.12',  # IP interna del contenedor MySQL Heredia
        'port': 3306,
        'user': 'root',
        'password': 'admin123',
        'database': 'cenfotec_heredia',
        'name': '🏫 Sede Heredia',
        'description': 'Base de datos académica - Estudiantes Heredia',
        'color': '#2ca02c'  # Verde
    }
}

# ========================================
# CONFIGURACIÓN DE USUARIO DE REPLICACIÓN
# ========================================

# Usuario especializado para operaciones de replicación y verificación
REPLICATION_USER_CONFIG = {
    'central_read_only': {
        'host': '172.20.0.10',
        'port': 3306,
        'user': 'replicacion',        # Usuario con permisos específicos
        'password': 'repl123',
        'database': 'cenfotec_central',
        'name': '🔍 Central (Solo Lectura)',
        'description': 'Conexión de replicación para verificación de datos maestros',
        'color': '#17a2b8'  # Info blue
    }
}

# Configuración de Redis Cache usando IP interna
REDIS_CONFIG = {
    'host': '172.20.0.13',  # IP interna del contenedor Redis
    'port': 6379,
    'decode_responses': True,
    'db': 0,
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'retry_on_timeout': True
}

# Flag para habilitar Redis
REDIS_ENABLED = True 

# Configuración de la aplicación Streamlit
APP_CONFIG = {
    'title': '🎓 Sistema Distribuido Universidad Cenfotec',
    'page_icon': '🎓',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
    'menu_items': {
        'Get Help': 'https://github.com/tu-usuario/universidad-cenfotec-distributed',
        'Report a bug': 'https://github.com/tu-usuario/universidad-cenfotec-distributed/issues',
        'About': 'Sistema de Base de Datos Distribuida para demostración académica'
    }
}

# Colores para visualizaciones
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#2ca02c',
    'danger': '#d62728',
    'warning': '#ff9800',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Configuración de gráficos
CHART_CONFIG = {
    'height': 400,
    'width': None,  # Se ajusta automáticamente al contenedor
    'theme': 'streamlit'
}

# Mensajes de estado del sistema
MESSAGES = {
    'connection_success': '✅ Conexión exitosa a {sede}',
    'connection_error': '❌ Error al conectar con {sede}: {error}',
    'query_success': '✅ Consulta ejecutada exitosamente',
    'query_error': '❌ Error en la consulta: {error}',
    'replication_success': '✅ Replicación completada',
    'replication_error': '❌ Error en la replicación: {error}',
    'cache_hit': '🎯 Datos obtenidos desde cache',
    'cache_miss': '📊 Datos obtenidos desde base de datos',
    'replication_user_info': '🔐 Usando usuario de replicación (solo lectura)',
    'admin_user_info': '🔧 Usando usuario administrador (lectura/escritura)'
}

# Configuración de tiempos de espera y reintentos
TIMEOUT_CONFIG = {
    'connection_timeout': 10,  # segundos
    'query_timeout': 30,       # segundos
    'retry_attempts': 3,
    'retry_delay': 1           # segundos entre reintentos
}

# ========================================
# CONFIGURACIÓN DE ROLES Y PERMISOS
# ========================================

# Define qué usuario usar para cada tipo de operación
OPERATION_USERS = {
    'read_master_data': 'replication',      # Leer datos maestros (carreras, profesores, sedes)
    'write_master_data': 'admin',           # Escribir datos maestros
    'verify_replication': 'replication',    # Verificar estado de replicación
    'audit_operations': 'admin',            # Operaciones de auditoría
    'student_operations': 'admin',          # Operaciones con estudiantes
    'monitoring': 'replication'             # Monitoreo del sistema
}

# Tablas que el usuario de replicación puede leer
REPLICATION_READABLE_TABLES = [
    'sede',
    'carrera', 
    'profesor',
    'replication_log'  # Tu tabla de logs existente
]

def get_db_config(sede: str) -> Dict[str, Any]:
    """
    Obtiene la configuración de conexión para una sede específica.
    
    Args:
        sede: Identificador de la sede ('central', 'sancarlos', 'heredia')
    
    Returns:
        Diccionario con la configuración de conexión
    
    Raises:
        ValueError: Si la sede no es válida
    """
    if sede not in DB_CONFIG:
        raise ValueError(f"Sede '{sede}' no válida. Sedes disponibles: {list(DB_CONFIG.keys())}")
    return DB_CONFIG[sede].copy()

def get_replication_config() -> Dict[str, Any]:
    """
    Obtiene la configuración del usuario de replicación.
    
    Returns:
        Diccionario con la configuración del usuario de replicación
    """
    return REPLICATION_USER_CONFIG['central_read_only'].copy()

def get_connection_for_operation(operation: str, sede: str = 'central') -> Dict[str, Any]:
    """
    Determina qué configuración de conexión usar según el tipo de operación.
    
    Args:
        operation: Tipo de operación (ver OPERATION_USERS)
        sede: Sede donde realizar la operación
    
    Returns:
        Configuración de conexión apropiada
    """
    user_type = OPERATION_USERS.get(operation, 'admin')
    
    if user_type == 'replication' and sede == 'central':
        # Usar usuario de replicación para operaciones de solo lectura en Central
        return get_replication_config()
    else:
        # Usar usuario admin para todo lo demás
        return get_db_config(sede)

def get_all_sedes() -> list:
    """
    Retorna una lista con todos los identificadores de sedes disponibles.
    
    Returns:
        Lista de strings con los identificadores de sedes
    """
    return list(DB_CONFIG.keys())

def get_sede_info(sede: str) -> Dict[str, str]:
    """
    Obtiene información descriptiva de una sede.
    
    Args:
        sede: Identificador de la sede
    
    Returns:
        Diccionario con nombre, descripción y color de la sede
    """
    config = get_db_config(sede)
    return {
        'name': config['name'],
        'description': config['description'],
        'color': config['color']
    }

def is_replication_table_readable(table_name: str) -> bool:
    """
    Verifica si una tabla puede ser leída por el usuario de replicación.
    
    Args:
        table_name: Nombre de la tabla
    
    Returns:
        True si la tabla es accesible para el usuario de replicación
    """
    return table_name.lower() in [t.lower() for t in REPLICATION_READABLE_TABLES]

def get_user_info_for_operation(operation: str) -> Dict[str, str]:
    """
    Obtiene información sobre qué usuario se usará para una operación.
    
    Args:
        operation: Tipo de operación
    
    Returns:
        Información del usuario y tipo de conexión
    """
    user_type = OPERATION_USERS.get(operation, 'admin')
    
    if user_type == 'replication':
        return {
            'user': 'replicacion',
            'type': 'read_only',
            'description': 'Usuario especializado para replicación (solo lectura)',
            'permissions': 'SELECT en tablas maestras',
            'icon': '🔍'
        }
    else:
        return {
            'user': 'root',
            'type': 'admin',
            'description': 'Usuario administrador (lectura/escritura)',
            'permissions': 'Permisos completos',
            'icon': '🔧'
        }

# ========================================
# CONFIGURACIÓN DE REPLICACIÓN AVANZADA
# ========================================

REPLICATION_CONFIG = {
    'master_sede': 'central',
    'slave_sedes': ['sancarlos', 'heredia'],
    'replicated_tables': ['sede', 'carrera', 'profesor'],
    'replication_user': 'replicacion',
    'replication_log_table': 'replication_log',  # Tu tabla existente
    'verification_interval': 30,  # segundos
    'max_replication_lag': 5      # segundos máximos de retraso aceptable
}