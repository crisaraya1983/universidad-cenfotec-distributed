"""
Configuración de conexiones para el sistema distribuido Cenfotec
Este archivo centraliza todas las configuraciones de conexión a las bases de datos
y servicios del sistema distribuido.
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

# Configuración de Redis Cache usando IP interna
REDIS_CONFIG = {
    'host': '172.20.0.13',  # IP interna del contenedor Redis
    'port': 6379,
    'decode_responses': True,
    'db': 0
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
    'cache_miss': '📊 Datos obtenidos desde base de datos'
}

# Configuración de tiempos de espera y reintentos
TIMEOUT_CONFIG = {
    'connection_timeout': 10,  # segundos
    'query_timeout': 30,       # segundos
    'retry_attempts': 3,
    'retry_delay': 1           # segundos entre reintentos
}

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