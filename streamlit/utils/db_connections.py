"""
Módulo de gestión de conexiones a bases de datos
"""
import mysql.connector
from mysql.connector import Error
import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any, List, Tuple
import time
from contextlib import contextmanager
import logging
from datetime import datetime, date, timedelta
import time 
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG, TIMEOUT_CONFIG, MESSAGES, REDIS_CONFIG, REDIS_ENABLED

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseConnection:
    
    def __init__(self, sede: str):
        self.sede = sede
        self.config = DB_CONFIG.get(sede)
        if not self.config:
            raise ValueError(f"Sede '{sede}' no encontrada en la configuración")
        
        self.connection = None
        self.cursor = None
        
    def connect(self) -> bool:
        for attempt in range(TIMEOUT_CONFIG['retry_attempts']):
            try:
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
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logger.info(f"Desconexión exitosa de {self.config['name']}")
        except Error as e:
            logger.error(f"Error al desconectar de {self.sede}: {e}")
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> Optional[List[Dict]]:
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
            
            logger.debug(f"Ejecutando consulta en {self.sede}: {query[:100]}...")
            
            self.cursor.execute(query, params)
            results = self.cursor.fetchall()
            
            logger.info(f"Consulta exitosa en {self.sede}: {len(results)} registros")
            return results
            
        except Error as e:
            logger.error(f"Error en consulta {self.sede}: {e}")
            st.error(MESSAGES['query_error'].format(error=str(e)))
            return None
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> Optional[int]:
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
        results = self.execute_query(query, params)
        if results is not None:
            return pd.DataFrame(results)
        return None


class RedisConnection:
    
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
        if not self.is_connected:
            return None
        try:
            value = self.redis_client.get(key)
            return value.decode('utf-8') if value else None
        except Exception as e:
            logger.warning(f"Error al obtener del cache: {e}")
            return None
    
    def set(self, key: str, value: str, expiry: int = 300):
        if not self.is_connected:
            return
        try:
            self.redis_client.setex(key, expiry, value)
            logger.debug(f"Valor guardado en cache: {key}")
        except Exception as e:
            logger.warning(f"Error al guardar en cache: {e}")
    
    def delete(self, key: str):
        if not self.is_connected:
            return
        try:
            self.redis_client.delete(key)
            logger.debug(f"Clave eliminada del cache: {key}")
        except Exception as e:
            logger.warning(f"Error al eliminar del cache: {e}")
    
    def flush(self):
        if not self.is_connected:
            return
        try:
            self.redis_client.flushdb()
            logger.info("Cache limpiado exitosamente")
        except Exception as e:
            logger.warning(f"Error al limpiar cache: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        if not self.is_connected:
            return {}
        try:
            return self.redis_client.info()
        except Exception as e:
            logger.warning(f"Error al obtener info de Redis: {e}")
            return {}

@contextmanager
def get_db_connection(sede: str):
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
    logger.info("=== CREANDO NUEVA CONEXIÓN REDIS ===")
    conn = RedisConnection()
    logger.info(f"=== CONEXIÓN REDIS CREADA: is_connected={conn.is_connected} ===")
    return conn

def test_all_connections() -> Dict[str, bool]:
    status = {}
    
    for sede in DB_CONFIG.keys():
        with get_db_connection(sede) as db:
            status[sede] = db is not None and db.connection.is_connected()
    
    redis_conn = get_redis_connection()
    status['redis'] = redis_conn is not None and redis_conn.is_connected
    
    return status

def test_load_balancer() -> bool:
    try:
        import requests
        response = requests.get('http://172.20.0.14/health', timeout=5)
        return response.status_code == 200
    except ImportError:
        logger.warning("Módulo requests no disponible para verificar Load Balancer")
        return False
    except Exception as e:
        logger.warning(f"Load Balancer no disponible: {e}")
        return False

def get_nginx_status() -> Dict[str, Any]:
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
                    results[sede] = pd.DataFrame()
    
    return results

def execute_real_transfer(student_data: Dict, from_sede: str, to_sede: str, progress_bar, status_container) -> tuple:
    try:
        from_key = from_sede.lower().replace(' ', '')
        to_key = to_sede.lower().replace(' ', '')
        
        def get_sede_id(sede_name):
            sede_ids = {"Central": 1, "San Carlos": 2, "Heredia": 3}
            return sede_ids.get(sede_name, 1)

        sede_origen_id = get_sede_id(from_sede)
        sede_destino_id = get_sede_id(to_sede)
        
        progress_bar.progress(0.2)

        existing_student = None
        with get_db_connection(to_key) as db_destino:
            if db_destino:
                check_query = """
                SELECT id_estudiante, estado, sede_actual FROM estudiante 
                WHERE nombre = %s AND email = %s
                """
                result = db_destino.get_dataframe(check_query, 
                    (student_data['nombre'], student_data['email']))
                if not result.empty:
                    existing_student = result.iloc[0]

        progress_bar.progress(0.4)

        with get_db_connection(from_key) as db_origen:
            if db_origen:
                query_update_origin = """
                UPDATE estudiante 
                SET estado = 'transferido',
                    sede_actual = %s,
                    fecha_transferencia = NOW()
                WHERE id_estudiante = %s
                """
                db_origen.execute_update(query_update_origin, 
                    (sede_destino_id, int(student_data['id_estudiante'])))

        progress_bar.progress(0.6)

        new_student_id = None
        with get_db_connection(to_key) as db_destino:
            if db_destino:
                if existing_student is not None:
                    query_update_return = """
                    UPDATE estudiante 
                    SET estado = 'activo',
                        sede_actual = %s,
                        fecha_transferencia = NOW()
                    WHERE id_estudiante = %s
                    """
                    existing_id = int(existing_student['id_estudiante'])
                    db_destino.execute_update(query_update_return, 
                        (sede_destino_id, existing_id))
                    new_student_id = existing_id
                else:
                    query_insert = """
                    INSERT INTO estudiante (nombre, email, id_sede, estado, sede_actual, fecha_transferencia) 
                    VALUES (%s, %s, %s, 'activo', %s, NOW())
                    """
                    db_destino.execute_update(query_insert, 
                        (student_data['nombre'], student_data['email'], 
                         sede_destino_id, sede_destino_id))
                    
                    try:
                        result = db_destino.get_dataframe("SELECT LAST_INSERT_ID() as new_id")
                        if not result.empty:
                            new_student_id = int(result.iloc[0]['new_id'])
                    except:
                        pass

        progress_bar.progress(0.8)

        audit_query = """
        INSERT INTO transferencia_estudiante 
        (id_estudiante, sede_origen, sede_destino, estado, motivo) 
        VALUES (%s, %s, %s, 'completada', %s)
        """

        motivo = 'Transferencia de retorno' if existing_student is not None else 'Transferencia bidireccional'

        with get_db_connection(from_key) as db:
            if db:
                db.execute_update(audit_query, 
                    (int(student_data['id_estudiante']), sede_origen_id, sede_destino_id, motivo))

        if new_student_id:
            with get_db_connection(to_key) as db:
                if db:
                    db.execute_update(audit_query, 
                        (new_student_id, sede_origen_id, sede_destino_id, motivo))

        progress_bar.progress(1.0)
        
        return True, new_student_id
        
    except Exception as e:
        with status_container:
            st.error(f"❌ Error en transferencia: {str(e)}")
        return False, None

def log_transfer_audit(student_id: int, from_sede: str, to_sede: str):
    log_transfer_audit_improved(
        old_id=student_id,
        new_id=None,
        from_sede=from_sede,
        to_sede=to_sede,
        student_name="Unknown",
        student_email="Unknown"
    )

def log_transfer_audit_improved(old_id: int, new_id: int, from_sede: str, to_sede: str, student_name: str, student_email: str):
    try:
        
        redis_conn = get_redis_connection()
        if redis_conn:
            audit_log = {
                'timestamp': datetime.now().isoformat(),
                'type': 'student_transfer',
                'student_name': student_name,
                'student_email': student_email,
                'old_id': old_id,
                'new_id': new_id,
                'from_sede': from_sede,
                'to_sede': to_sede,
                'status': 'completed',
                'operation': 'DELETE_INSERT'
            }
            
            key = f"transfer_log_{datetime.now().strftime('%Y%m%d')}"
            redis_conn.lpush(key, json.dumps(audit_log))
            
            redis_conn.ltrim(key, 0, 99)
            
    except Exception as e:
        pass    