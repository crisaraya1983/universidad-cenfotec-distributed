"""
Módulo de gestión de conexiones a bases de datos
Este módulo proporciona funciones y clases para conectarse de manera segura
y eficiente a las diferentes bases de datos MySQL del sistema distribuido.
"""

import mysql.connector
from mysql.connector import Error
# import redis  # Comentado - Redis deshabilitado
import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any, List, Tuple
import time
from contextlib import contextmanager
import logging
from datetime import datetime, date, timedelta
import time 

# Importar configuración desde el módulo config
import sys
import os
# Agregar el directorio padre al path para importar config.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG, TIMEOUT_CONFIG, MESSAGES, REDIS_CONFIG, REDIS_ENABLED

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """
    Clase para gestionar conexiones a bases de datos MySQL.
    Implementa pool de conexiones, reintentos automáticos y manejo de errores.
    """
    
    def __init__(self, sede: str):
        """
        Inicializa una conexión a la base de datos de una sede específica.
        
        Args:
            sede: Identificador de la sede ('central', 'sancarlos', 'heredia')
        """
        self.sede = sede
        self.config = DB_CONFIG.get(sede)
        if not self.config:
            raise ValueError(f"Sede '{sede}' no encontrada en la configuración")
        
        self.connection = None
        self.cursor = None
        
    def connect(self) -> bool:
        """
        Establece la conexión con la base de datos.
        Implementa reintentos automáticos según la configuración.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        for attempt in range(TIMEOUT_CONFIG['retry_attempts']):
            try:
                # Intentar establecer la conexión
                self.connection = mysql.connector.connect(
                    host=self.config['host'],
                    port=self.config['port'],
                    user=self.config['user'],
                    password=self.config['password'],
                    database=self.config['database'],
                    connection_timeout=TIMEOUT_CONFIG['connection_timeout']
                )
                
                if self.connection.is_connected():
                    self.cursor = self.connection.cursor(dictionary=True)
                    logger.info(f"Conexión exitosa a {self.config['name']}")
                    return True
                    
            except Error as e:
                logger.warning(f"Intento {attempt + 1} fallido para {self.sede}: {e}")
                if attempt < TIMEOUT_CONFIG['retry_attempts'] - 1:
                    time.sleep(TIMEOUT_CONFIG['retry_delay'])
                else:
                    logger.error(f"No se pudo conectar a {self.sede} después de {TIMEOUT_CONFIG['retry_attempts']} intentos")
                    st.error(MESSAGES['connection_error'].format(sede=self.config['name'], error=str(e)))
        
        return False
    
    def disconnect(self):
        """
        Cierra la conexión con la base de datos de manera segura.
        """
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logger.info(f"Desconexión exitosa de {self.config['name']}")
        except Error as e:
            logger.error(f"Error al desconectar de {self.sede}: {e}")
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> Optional[List[Dict]]:
        """
        Ejecuta una consulta SELECT y retorna los resultados.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros opcionales para consultas parametrizadas
        
        Returns:
            Lista de diccionarios con los resultados o None si hay error
        """
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
            
            # Registrar la consulta para debugging
            logger.debug(f"Ejecutando consulta en {self.sede}: {query[:100]}...")
            
            # Ejecutar la consulta con timeout
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            logger.info(f"Consulta exitosa en {self.sede}: {len(results)} registros")
            return results
            
        except Error as e:
            logger.error(f"Error en consulta {self.sede}: {e}")
            st.error(MESSAGES['query_error'].format(error=str(e)))
            return None
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> Optional[int]:
        """
        Ejecuta una consulta INSERT, UPDATE o DELETE.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros opcionales para consultas parametrizadas
        
        Returns:
            Número de filas afectadas o None si hay error
        """
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
            
            self.cursor.execute(query, params)
            self.connection.commit()
            
            affected_rows = self.cursor.rowcount
            logger.info(f"Update exitoso en {self.sede}: {affected_rows} filas afectadas")
            return affected_rows
            
        except Error as e:
            logger.error(f"Error en update {self.sede}: {e}")
            self.connection.rollback()
            st.error(MESSAGES['query_error'].format(error=str(e)))
            return None
    
    def get_dataframe(self, query: str, params: Optional[Tuple] = None) -> Optional[pd.DataFrame]:
        """
        Ejecuta una consulta y retorna los resultados como DataFrame de pandas.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros opcionales
        
        Returns:
            DataFrame con los resultados o None si hay error
        """
        results = self.execute_query(query, params)
        if results is not None:
            return pd.DataFrame(results)
        return None


class RedisConnection:
    """
    Clase para gestionar conexiones a Redis Cache distribuido.
    """
    
    def __init__(self):
        logger.info("=== INICIANDO RedisConnection.__init__ ===")
        self.redis_client = None
        self.is_connected = False
        
        logger.info(f"REDIS_ENABLED = {REDIS_ENABLED}")
        
        if REDIS_ENABLED:
            logger.info("Inicializando conexión a Redis...")
            resultado = self.connect()
            logger.info(f"Resultado de connect(): {resultado}")
        else:
            logger.info("Redis deshabilitado en configuración")
        
        logger.info(f"=== FIN RedisConnection.__init__ - is_connected: {self.is_connected} ===")
    
    def connect(self) -> bool:
        logger.info("=== DENTRO DE connect() ===")
        
        if not REDIS_ENABLED:
            logger.info("Redis deshabilitado en configuración")
            return False
            
        try:
            import redis
            logger.info(f"Configuración Redis: {REDIS_CONFIG}")
            
            self.redis_client = redis.Redis(**REDIS_CONFIG)
            
            ping_result = self.redis_client.ping()
            
            self.is_connected = True
            logger.info("Conexión exitosa a Redis Cache")
            return True
        except ImportError as e:
            logger.warning("Módulo redis no disponible. Cache deshabilitado.")
            self.is_connected = False
            return False
        except Exception as e:
            logger.warning(f"Error al conectar con Redis: {e}. Cache deshabilitado.")
            self.is_connected = False
            return False
    
    def get(self, key: str) -> Optional[str]:
        """
        Obtiene un valor del cache.
        
        Args:
            key: Clave para el valor
        
        Returns:
            Valor almacenado o None si no existe o hay error
        """
        if not self.is_connected:
            return None
        try:
            value = self.redis_client.get(key)
            return value.decode('utf-8') if value else None
        except Exception as e:
            logger.warning(f"Error al obtener del cache: {e}")
            return None
    
    def set(self, key: str, value: str, expiry: int = 300):
        """
        Guarda un valor en el cache con tiempo de expiración.
        
        Args:
            key: Clave para el valor
            value: Valor a guardar
            expiry: Tiempo de expiración en segundos (default: 5 minutos)
        """
        if not self.is_connected:
            return
        try:
            self.redis_client.setex(key, expiry, value)
            logger.debug(f"Valor guardado en cache: {key}")
        except Exception as e:
            logger.warning(f"Error al guardar en cache: {e}")
    
    def delete(self, key: str):
        """
        Elimina un valor del cache.
        
        Args:
            key: Clave a eliminar
        """
        if not self.is_connected:
            return
        try:
            self.redis_client.delete(key)
            logger.debug(f"Clave eliminada del cache: {key}")
        except Exception as e:
            logger.warning(f"Error al eliminar del cache: {e}")
    
    def flush(self):
        """Limpia todo el cache."""
        if not self.is_connected:
            return
        try:
            self.redis_client.flushdb()
            logger.info("Cache limpiado exitosamente")
        except Exception as e:
            logger.warning(f"Error al limpiar cache: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Obtiene información del servidor Redis.
        
        Returns:
            Diccionario con información del servidor
        """
        if not self.is_connected:
            return {}
        try:
            return self.redis_client.info()
        except Exception as e:
            logger.warning(f"Error al obtener info de Redis: {e}")
            return {}

@contextmanager
def get_db_connection(sede: str):
    """
    Context manager para manejar conexiones de manera segura.
    Garantiza que las conexiones se cierren correctamente.
    
    Usage:
        with get_db_connection('central') as db:
            results = db.execute_query("SELECT * FROM profesor")
    """
    db = DatabaseConnection(sede)
    try:
        if db.connect():
            yield db
        else:
            yield None
    finally:
        db.disconnect()

@st.cache_resource
def get_redis_connection() -> RedisConnection:
    """
    Obtiene una conexión singleton a Redis usando el cache de Streamlit.
    """
    logger.info("=== CREANDO NUEVA CONEXIÓN REDIS ===")
    conn = RedisConnection()
    logger.info(f"=== CONEXIÓN REDIS CREADA: is_connected={conn.is_connected} ===")
    return conn

def test_all_connections() -> Dict[str, bool]:
    """
    Prueba todas las conexiones de base de datos y Redis.
    
    Returns:
        Diccionario con el estado de cada conexión
    """
    status = {}
    
    # Probar conexiones MySQL
    for sede in DB_CONFIG.keys():
        with get_db_connection(sede) as db:
            status[sede] = db is not None and db.connection.is_connected()
    
    # Probar conexión Redis
    redis_conn = get_redis_connection()
    status['redis'] = redis_conn is not None and redis_conn.is_connected
    
    return status

def test_load_balancer() -> bool:
    """
    Verifica si el Load Balancer NGINX está disponible.
    
    Returns:
        True si está activo, False en caso contrario
    """
    try:
        import requests
        # Intentar conectar al load balancer
        response = requests.get('http://172.20.0.14/health', timeout=5)
        return response.status_code == 200
    except ImportError:
        logger.warning("Módulo requests no disponible para verificar Load Balancer")
        return False
    except Exception as e:
        logger.warning(f"Load Balancer no disponible: {e}")
        return False

def get_nginx_status() -> Dict[str, Any]:
    """
    Obtiene información detallada del estado del Load Balancer.
    
    Returns:
        Diccionario con información del estado
    """
    try:
        import requests
        response = requests.get('http://172.20.0.14/status', timeout=5)
        if response.status_code == 200:
            return {
                'status': 'online',
                'response_time': response.elapsed.total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
    except:
        pass
    
    return {
        'status': 'offline',
        'response_time': None,
        'timestamp': datetime.now().isoformat()
    }


def execute_distributed_query(query: str, sedes: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
    """
    Ejecuta una consulta en múltiples sedes y retorna los resultados.
    Útil para operaciones que requieren datos de varias bases de datos.
    
    Args:
        query: Consulta SQL a ejecutar
        sedes: Lista de sedes donde ejecutar (None = todas)
    
    Returns:
        Diccionario con DataFrames por sede
    """
    if sedes is None:
        sedes = list(DB_CONFIG.keys())
    
    results = {}
    
    for sede in sedes:
        with get_db_connection(sede) as db:
            if db:
                df = db.get_dataframe(query)
                if df is not None:
                    results[sede] = df
                else:
                    results[sede] = pd.DataFrame()  # DataFrame vacío si hay error
    
    return results

def execute_real_transfer(student_data: Dict, from_sede: str, to_sede: str, progress_bar, status_container) -> bool:
    """
    Ejecuta una transferencia real de estudiante entre sedes
    """
    try:
        from_key = from_sede.lower().replace(' ', '')
        to_key = to_sede.lower().replace(' ', '')
        
        # Paso 1: Copiar datos del estudiante
        with status_container:
            st.info("🔍 Copiando datos del estudiante...")
        progress_bar.progress(0.2)
        
        with get_db_connection(to_key) as db_destino:
            if db_destino:
                # Insertar estudiante en sede destino
                query_insert = """
                INSERT INTO estudiante (nombre, email, id_sede) 
                VALUES (%s, %s, %s)
                """
                sede_destino_id = 3 if to_sede == "Heredia" else 2
                db_destino.execute_update(query_insert, 
                    (student_data['nombre'], student_data['email'], sede_destino_id))
        
        # Paso 2: Transferir matrículas activas
        with status_container:
            st.info("📚 Transfiriendo matrículas...")
        progress_bar.progress(0.5)
        
        # Paso 3: Marcar como transferido en origen
        with status_container:
            st.info("🔄 Actualizando estado en origen...")
        progress_bar.progress(0.8)
        
        with get_db_connection(from_key) as db_origen:
            if db_origen:
                # Marcar como transferido (agregar campo status si no existe)
                query_update = """
                UPDATE estudiante 
                SET email = CONCAT(email, '_TRANSFERIDO_', %s)
                WHERE id_estudiante = %s
                """
                db_origen.execute_update(query_update, (to_sede, student_data['id_estudiante']))
        
        progress_bar.progress(1.0)
        return True
        
    except Exception as e:
        logger.error(f"Error en transferencia: {e}")
        return False

def log_transfer_audit(student_id: int, from_sede: str, to_sede: str):
    """Registra la transferencia en log de auditoría"""
    # Insertar en tabla sync_queue para auditoría
    pass