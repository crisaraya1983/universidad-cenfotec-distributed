"""
Módulo de Replicación Master-Slave Real con Usuario Especializado
Implementa replicación funcional usando usuario dedicado para mayor seguridad
"""

import logging
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import streamlit as st
from .db_connections import get_db_connection

logger = logging.getLogger(__name__)

class ReplicationConnection:
    """
    Clase especializada para conexiones de replicación usando el usuario 'replicacion'
    """
    
    def __init__(self):
        # Configuración del usuario de replicación
        self.replication_config = {
            'host': '172.20.0.10',  # Central
            'port': 3306,
            'user': 'replicacion',   # Usuario especializado
            'password': 'repl123',
            'database': 'cenfotec_central'
        }
        
    def get_master_connection(self, operation_type='read'):
        """
        Obtiene conexión apropiada según el tipo de operación
        
        Args:
            operation_type: 'read' para usuario replicacion, 'write' para admin
        
        Returns:
            Contexto de conexión a la base de datos
        """
        if operation_type == 'read':
            # Usar usuario de replicación para operaciones de solo lectura
            return self._get_replication_connection()
        else:
            # Usar usuario admin para escrituras
            return get_db_connection('central')
    
    def _get_replication_connection(self):
        """
        Crea una conexión usando el usuario de replicación
        """
        return ReplicationDatabaseConnection(self.replication_config)

class ReplicationDatabaseConnection:
    """
    Conexión específica para el usuario de replicación
    """
    
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.cursor = None
        
    def __enter__(self):
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        
    def connect(self):
        try:
            import mysql.connector
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                logger.info("🔍 Conexión establecida con usuario de replicación")
                return True
        except Exception as e:
            logger.error(f"Error conectando con usuario replicación: {e}")
            return False
    
    def disconnect(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logger.info("🔍 Desconexión del usuario de replicación")
        except Exception as e:
            logger.error(f"Error desconectando usuario replicación: {e}")
    
    def execute_query(self, query: str, params: Optional[Tuple] = None):
        """Ejecuta consulta SELECT (solo lectura)"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error en consulta de replicación: {e}")
            return None

class MasterSlaveReplication:
    """
    Implementa replicación Master-Slave con usuarios especializados
    """
    
    def __init__(self):
        self.master_sede = 'central'
        self.slave_sedes = ['sancarlos', 'heredia']
        self.replication_conn = ReplicationConnection()
        
    def replicate_carrera(self, nombre_carrera: str, id_sede: int, progress_callback=None, status_callback=None) -> bool:
        """
        Replica una nueva carrera usando usuarios apropiados para cada operación
        """
        try:
            total_steps = 5  # Agregamos paso de verificación
            current_step = 0
            
            # Paso 1: Verificar permisos y conectividad con usuario de replicación
            if status_callback:
                status_callback("🔍 Verificando permisos con usuario de replicación...")
            
            verification_success = self._verify_replication_permissions()
            if not verification_success:
                raise Exception("Error en verificación de permisos de replicación")
                
            current_step += 1
            if progress_callback:
                progress_callback(current_step / total_steps)
            
            # Paso 2: Insertar en Master usando usuario admin
            if status_callback:
                status_callback("🔧 Insertando carrera en Central (usuario admin)...")
            
            carrera_id = self._insert_carrera_master(nombre_carrera, id_sede)
            if not carrera_id:
                raise Exception("Error al insertar en Master")
                
            current_step += 1
            if progress_callback:
                progress_callback(current_step / total_steps)
            
            # Paso 3: Replicar a Sedes Slaves
            replication_results = {}
            
            for sede_slave in self.slave_sedes:
                if status_callback:
                    status_callback(f"🔄 Replicando a sede {sede_slave.upper()}...")
                
                success = self._replicate_to_slave(carrera_id, nombre_carrera, id_sede, sede_slave)
                replication_results[sede_slave] = success
                
                current_step += 1
                if progress_callback:
                    progress_callback(current_step / total_steps)
                
                time.sleep(0.5)
            
            # Paso 4: Verificar consistencia usando usuario de replicación
            if status_callback:
                status_callback("🔍 Verificando consistencia con usuario de replicación...")
            
            consistency_check = self._verify_replication_consistency(carrera_id)
            
            # Paso 5: Registrar en replication log
            if status_callback:
                status_callback("📊 Registrando en replication log...")
            
            self._log_replication_audit(carrera_id, nombre_carrera, id_sede, replication_results, consistency_check)
            
            current_step += 1
            if progress_callback:
                progress_callback(1.0)
            
            all_success = all(replication_results.values()) and consistency_check
            
            if all_success:
                if status_callback:
                    status_callback("✅ Replicación completada y verificada exitosamente")
                logger.info(f"Replicación exitosa: carrera '{nombre_carrera}' (ID: {carrera_id})")
                return True
            else:
                failed_info = []
                if not consistency_check:
                    failed_info.append("verificación de consistencia")
                failed_sedes = [sede for sede, success in replication_results.items() if not success]
                if failed_sedes:
                    failed_info.append(f"replicación a: {', '.join(failed_sedes)}")
                
                if status_callback:
                    status_callback(f"⚠️ Fallos en: {', '.join(failed_info)}")
                return False
                
        except Exception as e:
            logger.error(f"Error en replicación Master-Slave: {e}")
            if status_callback:
                status_callback(f"❌ Error en replicación: {str(e)}")
            return False
    
    def _verify_replication_permissions(self) -> bool:
        """
        Verifica que el usuario de replicación tenga los permisos necesarios
        """
        try:
            with self.replication_conn.get_master_connection('read') as db:
                if not db:
                    return False
                
                # Verificar acceso a tablas críticas
                test_queries = [
                    "SELECT COUNT(*) as count FROM sede LIMIT 1",
                    "SELECT COUNT(*) as count FROM carrera LIMIT 1", 
                    "SELECT COUNT(*) as count FROM profesor LIMIT 1"
                ]
                
                for query in test_queries:
                    result = db.execute_query(query)
                    if result is None:
                        logger.error(f"Usuario replicación no puede ejecutar: {query}")
                        return False
                
                logger.info("✅ Usuario de replicación verificado exitosamente")
                return True
                
        except Exception as e:
            logger.error(f"Error verificando permisos de replicación: {e}")
            return False
    
    def _insert_carrera_master(self, nombre_carrera: str, id_sede: int) -> Optional[int]:
        """
        Inserta la carrera usando usuario admin (permisos de escritura)
        """
        try:
            with self.replication_conn.get_master_connection('write') as db:
                if not db:
                    raise Exception("No se pudo conectar con usuario admin")
                
                query = "INSERT INTO carrera (nombre, id_sede) VALUES (%s, %s)"
                affected_rows = db.execute_update(query, (nombre_carrera, id_sede))
                
                if affected_rows and affected_rows > 0:
                    query_id = "SELECT LAST_INSERT_ID() as id"
                    result = db.execute_query(query_id)
                    
                    if result and len(result) > 0:
                        carrera_id = result[0]['id']
                        logger.info(f"🔧 Carrera insertada con usuario admin: ID {carrera_id}")
                        return carrera_id
                
                raise Exception("No se pudo obtener el ID de la carrera insertada")
                
        except Exception as e:
            logger.error(f"Error al insertar en Master: {e}")
            return None
    
    def _replicate_to_slave(self, carrera_id: int, nombre_carrera: str, id_sede: int, sede_slave: str) -> bool:
        """
        Replica la carrera a una sede slave usando usuario admin
        """
        try:
            with get_db_connection(sede_slave) as db:  # Usuario admin para escritura
                if not db:
                    raise Exception(f"No se pudo conectar a {sede_slave}")
                
                # Verificar si ya existe
                check_query = """
                SELECT COUNT(*) as count 
                FROM carrera 
                WHERE id_carrera = %s OR (nombre = %s AND id_sede = %s)
                """
                result = db.execute_query(check_query, (carrera_id, nombre_carrera, id_sede))
                
                if result and result[0]['count'] > 0:
                    logger.info(f"Carrera ya existe en {sede_slave}")
                    return True
                
                # Insertar con mismo ID
                insert_query = """
                INSERT INTO carrera (id_carrera, nombre, id_sede) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                nombre = VALUES(nombre), 
                id_sede = VALUES(id_sede)
                """
                
                affected_rows = db.execute_update(insert_query, (carrera_id, nombre_carrera, id_sede))
                
                if affected_rows and affected_rows > 0:
                    logger.info(f"🔧 Carrera replicada a {sede_slave} con usuario admin")
                    return True
                else:
                    raise Exception(f"No se afectaron filas en {sede_slave}")
                    
        except Exception as e:
            logger.error(f"Error replicando a {sede_slave}: {e}")
            return False
    
    def _verify_replication_consistency(self, carrera_id: int) -> bool:
        """
        Verifica consistencia usando usuario de replicación (solo lectura)
        """
        try:
            # Verificar en Master con usuario de replicación
            with self.replication_conn.get_master_connection('read') as db:
                if not db:
                    return False
                
                query = "SELECT nombre, id_sede FROM carrera WHERE id_carrera = %s"
                master_result = db.execute_query(query, (carrera_id,))
                
                if not master_result or len(master_result) == 0:
                    logger.error(f"Carrera {carrera_id} no encontrada en Master")
                    return False
                
                master_data = master_result[0]
            
            # Verificar en Slaves con usuario admin (no tenemos usuario replicación en slaves)
            for sede_slave in self.slave_sedes:
                with get_db_connection(sede_slave) as db:
                    if not db:
                        return False
                    
                    result = db.execute_query(query, (carrera_id,))
                    
                    if not result or len(result) == 0:
                        logger.error(f"Carrera {carrera_id} no replicada en {sede_slave}")
                        return False
                    
                    slave_data = result[0]
                    
                    # Verificar que los datos coincidan
                    if (slave_data['nombre'] != master_data['nombre'] or 
                        slave_data['id_sede'] != master_data['id_sede']):
                        logger.error(f"Datos inconsistentes en {sede_slave}")
                        return False
            
            logger.info(f"🔍 Consistencia verificada para carrera {carrera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error en verificación de consistencia: {e}")
            return False
    
    def _log_replication_audit(self, carrera_id: int, nombre_carrera: str, id_sede: int, 
                              replication_results: Dict[str, bool], consistency_check: bool):
        """
        Registra en replication_log usando usuario admin
        """
        try:
            with self.replication_conn.get_master_connection('write') as db:
                if not db:
                    return
                
                audit_data = {
                    'carrera_id': carrera_id,
                    'nombre_carrera': nombre_carrera,
                    'id_sede': id_sede,
                    'replication_results': replication_results,
                    'consistency_check': consistency_check,
                    'user_info': {
                        'verification_user': 'replicacion',
                        'write_user': 'root',
                        'security_model': 'separated_permissions'
                    },
                    'timestamp': datetime.now().isoformat()
                }
                
                query = """
                INSERT INTO replication_log (
                    tabla_afectada, 
                    operacion, 
                    registro_id, 
                    datos_nuevos, 
                    usuario, 
                    sede_destino, 
                    estado_replicacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                estado = 'procesado' if (all(replication_results.values()) and consistency_check) else 'error'
                sedes_destino = ','.join(self.slave_sedes)
                
                db.execute_update(query, (
                    'carrera',
                    'INSERT',
                    carrera_id,
                    json.dumps(audit_data),
                    'sistema_replicacion_v2',  # Indicar versión mejorada
                    sedes_destino,
                    estado
                ))
                
                logger.info(f"📊 Replication log registrado para carrera ID {carrera_id}")
                
        except Exception as e:
            logger.error(f"Error al registrar replication log: {e}")
    
    def get_replication_status_detailed(self) -> Dict[str, Dict]:
        """
        Obtiene estado detallado usando usuario de replicación para Master
        """
        status = {}
        
        try:
            # Estado del Master usando usuario de replicación
            with self.replication_conn.get_master_connection('read') as db:
                if not db:
                    status['central'] = {'disponible': False, 'user_type': 'replication_failed'}
                else:
                    query = "SELECT COUNT(*) as total FROM carrera"
                    result = db.execute_query(query)
                    total_carreras = result[0]['total'] if result else 0
                    
                    status['central'] = {
                        'disponible': True,
                        'total_carreras': total_carreras,
                        'user_type': 'replication_user',
                        'permissions': 'read_only',
                        'ultima_verificacion': datetime.now().isoformat()
                    }
            
            # Estado de Slaves usando usuario admin
            for sede in self.slave_sedes:
                with get_db_connection(sede) as db:
                    if not db:
                        status[sede] = {'disponible': False, 'user_type': 'admin_failed'}
                        continue
                    
                    query = "SELECT COUNT(*) as total FROM carrera"
                    result = db.execute_query(query)
                    total_carreras = result[0]['total'] if result else 0
                    
                    status[sede] = {
                        'disponible': True,
                        'total_carreras': total_carreras,
                        'user_type': 'admin_user',
                        'permissions': 'read_write',
                        'ultima_verificacion': datetime.now().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"Error obteniendo estado detallado: {e}")
        
        return status


def execute_master_slave_replication(nombre_carrera: str, sede_destino: str, progress_bar=None, status_container=None) -> bool:
    """
    Función mejorada que usa el sistema de usuarios especializados
    """
    sede_map = {"Central": 1, "San Carlos": 2, "Heredia": 3}
    id_sede = sede_map.get(sede_destino, 1)
    
    # Mostrar información de usuarios
    if status_container:
        with status_container:
            st.info("🔐 Sistema de seguridad mejorado: usuario 'replicacion' para verificación, 'root' para escritura")
    
    replicator = MasterSlaveReplication()
    
    def update_progress(progress):
        if progress_bar:
            progress_bar.progress(progress)
    
    def update_status(message):
        if status_container:
            with status_container:
                st.info(message)
    
    success = replicator.replicate_carrera(
        nombre_carrera=nombre_carrera,
        id_sede=id_sede,
        progress_callback=update_progress,
        status_callback=update_status
    )
    
    if success:
        if status_container:
            with status_container:
                st.success(f"✅ Carrera '{nombre_carrera}' replicada y verificada exitosamente")
                st.info("🔍 Verificación realizada con usuario de replicación especializado")
    
    return success