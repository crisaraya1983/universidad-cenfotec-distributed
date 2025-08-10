"""
Configuración de conexiones
Este archivo centraliza todas las configuraciones de conexión a las bases de datos
y servicios del sistema distribuido.
"""

import os
from typing import Dict, Any

# Configuración de bases de datos MySQL para Docker
DB_CONFIG = {
    'central': {
        'host': '172.20.0.10',
        'port': 3306,
        'user': 'root',
        'password': 'admin123',
        'database': 'cenfotec_central',
        'name': 'Sede Central',
        'description': 'Base de datos administrativa - Planillas y Pagarés',
        'color': '#1f77b4'
    },
    'sancarlos': {
        'host': '172.20.0.11',
        'port': 3306,
        'user': 'root',
        'password': 'admin123',
        'database': 'cenfotec_sancarlos',
        'name': 'Sede San Carlos',
        'description': 'Base de datos académica - Estudiantes San Carlos',
        'color': '#ff7f0e' 
    },
    'heredia': {
        'host': '172.20.0.12',
        'port': 3306,
        'user': 'root',
        'password': 'admin123',
        'database': 'cenfotec_heredia',
        'name': 'Sede Heredia',
        'description': 'Base de datos académica - Estudiantes Heredia',
        'color': '#2ca02c'
    }
}

# ========================================
# CONFIGURACIÓN DE USUARIO DE REPLICACIÓN
# ========================================

# Usuario para operaciones de replicación y verificación
REPLICATION_USER_CONFIG = {
    'central_read_only': {
        'host': '172.20.0.10',
        'port': 3306,
        'user': 'replicacion',
        'password': 'repl123',
        'database': 'cenfotec_central',
        'name': 'Central',
        'description': 'Conexión de replicación para verificación de datos maestros',
        'color': '#17a2b8' 
    }
}

# Configuración de Redis Cache
REDIS_CONFIG = {
    'host': '172.20.0.13',
    'port': 6379,
    'decode_responses': True,
    'db': 0,
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'retry_on_timeout': True
}

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

CHART_CONFIG = {
    'height': 400,
    'width': None,
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
    'cache_hit': 'Datos obtenidos desde cache',
    'cache_miss': 'Datos obtenidos desde base de datos',
    'replication_user_info': 'Usando usuario de replicación (solo lectura)',
    'admin_user_info': 'Usando usuario administrador (lectura/escritura)'
}

# Configuración de tiempos de espera y reintentos
TIMEOUT_CONFIG = {
    'connection_timeout': 10,
    'query_timeout': 30,
    'retry_attempts': 3,
    'retry_delay': 1
}

# ========================================
# CONFIGURACIÓN DE ROLES Y PERMISOS
# ========================================

OPERATION_USERS = {
    'read_master_data': 'replication', 
    'write_master_data': 'admin', 
    'verify_replication': 'replication',
    'audit_operations': 'admin',
    'student_operations': 'admin',
    'monitoring': 'replication'
}

REPLICATION_READABLE_TABLES = [
    'sede',
    'carrera', 
    'profesor',
    'replication_log'
]

def get_db_config(sede: str) -> Dict[str, Any]:
    if sede not in DB_CONFIG:
        raise ValueError(f"Sede '{sede}' no válida. Sedes disponibles: {list(DB_CONFIG.keys())}")
    return DB_CONFIG[sede].copy()

def get_replication_config() -> Dict[str, Any]:
    return REPLICATION_USER_CONFIG['central_read_only'].copy()

def get_connection_for_operation(operation: str, sede: str = 'central') -> Dict[str, Any]:
    user_type = OPERATION_USERS.get(operation, 'admin')
    
    if user_type == 'replication' and sede == 'central':
        return get_replication_config()
    else:
        return get_db_config(sede)

def get_all_sedes() -> list:
    return list(DB_CONFIG.keys())

def get_sede_info(sede: str) -> Dict[str, str]:
    config = get_db_config(sede)
    return {
        'name': config['name'],
        'description': config['description'],
        'color': config['color']
    }

def is_replication_table_readable(table_name: str) -> bool:
    return table_name.lower() in [t.lower() for t in REPLICATION_READABLE_TABLES]

def get_user_info_for_operation(operation: str) -> Dict[str, str]:
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

REPLICATION_CONFIG = {
    'master_sede': 'central',
    'slave_sedes': ['sancarlos', 'heredia'],
    'replicated_tables': ['sede', 'carrera', 'profesor'],
    'replication_user': 'replicacion',
    'replication_log_table': 'replication_log',
    'verification_interval': 30,
    'max_replication_lag': 5 
}