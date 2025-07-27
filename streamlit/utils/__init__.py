"""
Módulo de utilidades para el Sistema Distribuido Cenfotec
Este paquete contiene todas las utilidades compartidas por la aplicación Streamlit.
"""

# Importar las funciones principales de cada módulo
from .db_connections import (
    DatabaseConnection,
    RedisConnection,
    get_db_connection,
    get_redis_connection,
    test_all_connections,
    execute_distributed_query
)

from .queries import (
    FRAGMENTATION_QUERIES,
    REPLICATION_QUERIES,
    TRANSACTION_QUERIES,
    MONITORING_QUERIES,
    ANALYSIS_QUERIES,
    USER_VIEW_QUERIES,
    ReportQueries,
    build_date_filter,
    build_pagination
)

from .replication import (
    MasterSlaveReplication,
    execute_master_slave_replication,
    ReplicationConnection
)

# Definir qué se exporta cuando se hace "from utils import *"
__all__ = [
    # Conexiones
    'DatabaseConnection',
    'RedisConnection',
    'get_db_connection',
    'get_redis_connection',
    'test_all_connections',
    'execute_distributed_query',
    
    # Queries
    'FRAGMENTATION_QUERIES',
    'REPLICATION_QUERIES',
    'TRANSACTION_QUERIES',
    'MONITORING_QUERIES',
    'ANALYSIS_QUERIES',
    'USER_VIEW_QUERIES',
    'ReportQueries',
    'build_date_filter',
    'build_pagination',
    'MasterSlaveReplication',
    'execute_master_slave_replication',
    'ReplicationConnection'
]

# Versión del módulo
__version__ = '1.0.0'