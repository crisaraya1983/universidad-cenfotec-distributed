import logging
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import streamlit as st
from .db_connections import get_db_connection

logger = logging.getLogger(__name__)

class ReplicationConnection:
    def __init__(self):
        self.replication_config = {
            'host': '172.20.0.10', 
            'port': 3306,
            'user': 'replicacion',
            'password': 'repl123',
            'database': 'cenfotec_central'
        }
        
    def get_master_connection(self, operation_type='read'):
        if operation_type == 'read':
            return self._get_replication_connection()
        else:
            return get_db_connection('central')
    
    def _get_replication_connection(self):
        return ReplicationDatabaseConnection(self.replication_config)

class ReplicationDatabaseConnection:
    
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
                logger.info("Conexión establecida con usuario de replicación")
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
                logger.info("Desconexión del usuario de replicación")
        except Exception as e:
            logger.error(f"Error desconectando usuario replicación: {e}")
    
    def execute_query(self, query: str, params: Optional[Tuple] = None):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error en consulta de replicación: {e}")
            return None

class MasterSlaveReplication:
    def __init__(self):
        self.master_sede = 'central'
        self.slave_sedes = ['sancarlos', 'heredia']
        self.replication_conn = ReplicationConnection()
        
    def replicate_carrera(self, nombre_carrera: str, id_sede: int, progress_callback=None, status_callback=None) -> bool:
        try:
            total_steps = 5
            current_step = 0
            
            if status_callback:
                status_callback("Procesando replicación de carrera...")
            
            verification_success = self._verify_replication_permissions()
            if not verification_success:
                raise Exception("Error en verificación de permisos de replicación")
                
            current_step += 1
            if progress_callback:
                progress_callback(current_step / total_steps)
            
            carrera_id = self._insert_carrera_master(nombre_carrera, id_sede)
            if not carrera_id:
                raise Exception("Error al insertar en Master")
                
            current_step += 1
            if progress_callback:
                progress_callback(current_step / total_steps)

            replication_results = {}
            
            for sede_slave in self.slave_sedes:
                success = self._replicate_carrera_to_slave(carrera_id, nombre_carrera, id_sede, sede_slave)
                replication_results[sede_slave] = success
                
                current_step += 1
                if progress_callback:
                    progress_callback(current_step / total_steps)
                
                time.sleep(0.5)
            
            consistency_check = self._verify_carrera_consistency(carrera_id)
            
            self._log_replication_audit('carrera', carrera_id, {
                'nombre': nombre_carrera, 
                'id_sede': id_sede
            }, replication_results, consistency_check)
            
            current_step += 1
            if progress_callback:
                progress_callback(1.0)
            
            all_success = all(replication_results.values()) and consistency_check
            
            if all_success:
                if status_callback:
                    status_callback("✅ Replicación completada exitosamente")
                logger.info(f"Replicación exitosa: carrera '{nombre_carrera}' (ID: {carrera_id})")
                return True
            else:
                error_details = []
                if not consistency_check:
                    error_details.append("verificación de consistencia falló")
                failed_sedes = [sede for sede, success in replication_results.items() if not success]
                if failed_sedes:
                    error_details.append(f"replicación falló en: {', '.join(failed_sedes)}")
                
                error_message = f"❌ Error: {'; '.join(error_details)}"
                if status_callback:
                    status_callback(error_message)
                return False
                
        except Exception as e:
            logger.error(f"Error en replicación Master-Slave de carrera: {e}")
            if status_callback:
                status_callback(f"❌ Error en replicación: {str(e)}")
            return False
    
    def replicate_profesor(self, nombre_profesor: str, email_profesor: str, id_sede: int, progress_callback=None, status_callback=None) -> bool:
        try:
            total_steps = 5
            current_step = 0
            
            if status_callback:
                status_callback("🔄 Procesando replicación de profesor...")
            
            verification_success = self._verify_replication_permissions()
            if not verification_success:
                raise Exception("Error en verificación de permisos de replicación")
                
            current_step += 1
            if progress_callback:
                progress_callback(current_step / total_steps)
            
            profesor_id = self._insert_profesor_master(nombre_profesor, email_profesor, id_sede)
            if not profesor_id:
                raise Exception("Error al insertar profesor en Master")
                
            current_step += 1
            if progress_callback:
                progress_callback(current_step / total_steps)
            
            replication_results = {}
            
            for sede_slave in self.slave_sedes:
                success = self._replicate_profesor_to_slave(profesor_id, nombre_profesor, email_profesor, id_sede, sede_slave)
                replication_results[sede_slave] = success
                
                current_step += 1
                if progress_callback:
                    progress_callback(current_step / total_steps)
                
                time.sleep(0.5)
            
            consistency_check = self._verify_profesor_consistency(profesor_id)
            
            self._log_replication_audit('profesor', profesor_id, {
                'nombre': nombre_profesor,
                'email': email_profesor, 
                'id_sede': id_sede
            }, replication_results, consistency_check)
            
            current_step += 1
            if progress_callback:
                progress_callback(1.0)
            
            all_success = all(replication_results.values()) and consistency_check
            
            if all_success:
                if status_callback:
                    status_callback("✅ Replicación completada exitosamente")
                logger.info(f"Replicación exitosa: profesor '{nombre_profesor}' (ID: {profesor_id})")
                return True
            else:
                error_details = []
                if not consistency_check:
                    error_details.append("verificación de consistencia falló")
                failed_sedes = [sede for sede, success in replication_results.items() if not success]
                if failed_sedes:
                    error_details.append(f"replicación falló en: {', '.join(failed_sedes)}")
                
                error_message = f"❌ Error: {'; '.join(error_details)}"
                if status_callback:
                    status_callback(error_message)
                return False
                
        except Exception as e:
            logger.error(f"Error en replicación Master-Slave de profesor: {e}")
            if status_callback:
                status_callback(f"❌ Error en replicación: {str(e)}")
            return False
    
    def _verify_replication_permissions(self) -> bool:
        try:
            with self.replication_conn.get_master_connection('read') as db:
                if not db:
                    return False
                
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
            logger.error(f"Error al insertar carrera en Master: {e}")
            return None
    
    def _insert_profesor_master(self, nombre_profesor: str, email_profesor: str, id_sede: int) -> Optional[int]:
        try:
            with self.replication_conn.get_master_connection('write') as db:
                if not db:
                    raise Exception("No se pudo conectar con usuario admin")
                
                query = "INSERT INTO profesor (nombre, email, id_sede) VALUES (%s, %s, %s)"
                affected_rows = db.execute_update(query, (nombre_profesor, email_profesor, id_sede))
                
                if affected_rows and affected_rows > 0:
                    query_id = "SELECT LAST_INSERT_ID() as id"
                    result = db.execute_query(query_id)
                    
                    if result and len(result) > 0:
                        profesor_id = result[0]['id']
                        logger.info(f"🔧 Profesor insertado con usuario admin: ID {profesor_id}")
                        return profesor_id
                
                raise Exception("No se pudo obtener el ID del profesor insertado")
                
        except Exception as e:
            logger.error(f"Error al insertar profesor en Master: {e}")
            return None
    
    def _replicate_carrera_to_slave(self, carrera_id: int, nombre_carrera: str, id_sede: int, sede_slave: str) -> bool:
        try:
            with get_db_connection(sede_slave) as db:
                if not db:
                    raise Exception(f"No se pudo conectar a {sede_slave}")
                
                check_query = "SELECT COUNT(*) as count FROM carrera WHERE id_carrera = %s"
                result = db.execute_query(check_query, (carrera_id,))
                
                if result and result[0]['count'] > 0:
                    logger.info(f"Carrera ID {carrera_id} ya existe en {sede_slave}, actualizando")
                    update_query = """
                    UPDATE carrera 
                    SET nombre = %s, id_sede = %s 
                    WHERE id_carrera = %s
                    """
                    affected_rows = db.execute_update(update_query, (nombre_carrera, id_sede, carrera_id))
                    return affected_rows is not None and affected_rows >= 0
                
                insert_query = """
                INSERT INTO carrera (id_carrera, nombre, id_sede) 
                VALUES (%s, %s, %s)
                """
                
                affected_rows = db.execute_update(insert_query, (carrera_id, nombre_carrera, id_sede))
                
                if affected_rows and affected_rows > 0:
                    logger.info(f"🔧 Carrera '{nombre_carrera}' REPLICADA COMPLETAMENTE a {sede_slave}")
                    return True
                else:
                    raise Exception(f"No se afectaron filas en {sede_slave}")
                    
        except Exception as e:
            logger.error(f"Error replicando carrera a {sede_slave}: {e}")
            return False
    
    def _replicate_profesor_to_slave(self, profesor_id: int, nombre_profesor: str, email_profesor: str, id_sede: int, sede_slave: str) -> bool:
        try:
            with get_db_connection(sede_slave) as db:
                if not db:
                    raise Exception(f"No se pudo conectar a {sede_slave}")
                
                check_query = "SELECT COUNT(*) as count FROM profesor WHERE id_profesor = %s OR email = %s"
                result = db.execute_query(check_query, (profesor_id, email_profesor))
                
                if result and result[0]['count'] > 0:
                    logger.info(f"Profesor ID {profesor_id} ya existe en {sede_slave}, actualizando")
                    update_query = """
                    UPDATE profesor 
                    SET nombre = %s, email = %s, id_sede = %s 
                    WHERE id_profesor = %s OR email = %s
                    """
                    affected_rows = db.execute_update(update_query, (nombre_profesor, email_profesor, id_sede, profesor_id, email_profesor))
                    return affected_rows is not None and affected_rows >= 0
                
                insert_query = """
                INSERT INTO profesor (id_profesor, nombre, email, id_sede) 
                VALUES (%s, %s, %s, %s)
                """
                
                affected_rows = db.execute_update(insert_query, (profesor_id, nombre_profesor, email_profesor, id_sede))
                
                if affected_rows and affected_rows > 0:
                    logger.info(f"🔧 Profesor '{nombre_profesor}' REPLICADO COMPLETAMENTE a {sede_slave}")
                    return True
                else:
                    raise Exception(f"No se afectaron filas en {sede_slave}")
                    
        except Exception as e:
            logger.error(f"Error replicando profesor a {sede_slave}: {e}")
            return False
    
    def _verify_carrera_consistency(self, carrera_id: int) -> bool:
        try:
            with self.replication_conn.get_master_connection('read') as db:
                if not db:
                    return False
                
                query = "SELECT nombre, id_sede FROM carrera WHERE id_carrera = %s"
                master_result = db.execute_query(query, (carrera_id,))
                
                if not master_result or len(master_result) == 0:
                    logger.error(f"Carrera {carrera_id} no encontrada en Master")
                    return False
                
                master_data = master_result[0]
            
            for sede_slave in self.slave_sedes:
                with get_db_connection(sede_slave) as db:
                    if not db:
                        return False
                    
                    result = db.execute_query(query, (carrera_id,))
                    
                    if not result or len(result) == 0:
                        logger.error(f"Carrera {carrera_id} no replicada en {sede_slave}")
                        return False
                    
                    slave_data = result[0]
                    
                    if (slave_data['nombre'] != master_data['nombre'] or 
                        slave_data['id_sede'] != master_data['id_sede']):
                        logger.error(f"Datos inconsistentes en {sede_slave}")
                        return False
            
            logger.info(f"🔍 Consistencia verificada para carrera {carrera_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error en verificación de consistencia de carrera: {e}")
            return False
    
    def _verify_profesor_consistency(self, profesor_id: int) -> bool:
        try:
            with self.replication_conn.get_master_connection('read') as db:
                if not db:
                    return False
                
                query = "SELECT nombre, email, id_sede FROM profesor WHERE id_profesor = %s"
                master_result = db.execute_query(query, (profesor_id,))
                
                if not master_result or len(master_result) == 0:
                    logger.error(f"Profesor {profesor_id} no encontrado en Master")
                    return False
                
                master_data = master_result[0]
            
            for sede_slave in self.slave_sedes:
                with get_db_connection(sede_slave) as db:
                    if not db:
                        return False
                    
                    result = db.execute_query(query, (profesor_id,))
                    
                    if not result or len(result) == 0:
                        logger.error(f"Profesor {profesor_id} no replicado en {sede_slave}")
                        return False
                    
                    slave_data = result[0]
                    
                    if (slave_data['nombre'] != master_data['nombre'] or 
                        slave_data['email'] != master_data['email'] or
                        slave_data['id_sede'] != master_data['id_sede']):
                        logger.error(f"Datos de profesor inconsistentes en {sede_slave}")
                        return False
            
            logger.info(f"Consistencia verificada para profesor {profesor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error en verificación de consistencia de profesor: {e}")
            return False
    
    def _log_replication_audit(self, tabla: str, registro_id: int, datos: Dict, replication_results: Dict[str, bool], consistency_check: bool):
        try:
            with self.replication_conn.get_master_connection('write') as db:
                if not db:
                    return
                
                audit_data = {
                    'registro_id': registro_id,
                    'datos': datos,
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
                    tabla,
                    'INSERT',
                    registro_id,
                    json.dumps(audit_data),
                    f'sistema_replicacion_{tabla}',
                    sedes_destino,
                    estado
                ))
                
                logger.info(f"Replication log registrado para {tabla} ID {registro_id}")
                
        except Exception as e:
            logger.error(f"Error al registrar replication log: {e}")
    
    def get_replication_status_detailed(self) -> Dict[str, Dict]:
        status = {}
        
        try:
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
    
    def get_last_inserted_profesor_id(self) -> Optional[int]:
        try:
            with self.replication_conn.get_master_connection('read') as db:
                if not db:
                    return None
                
                query = "SELECT MAX(id_profesor) as last_id FROM profesor"
                result = db.execute_query(query)
                
                if result and len(result) > 0 and result[0]['last_id']:
                    return result[0]['last_id']
                    
                return None
                
        except Exception as e:
            logger.error(f"Error obteniendo último ID de profesor: {e}")
            return None



def execute_master_slave_replication(nombre_carrera: str, sede_destino: str, progress_bar=None, status_container=None) -> bool:
    sede_map = {"Central": 1, "San Carlos": 2, "Heredia": 3}
    id_sede = sede_map.get(sede_destino, 1)
    
    if status_container:
        with status_container:
            st.info("Sistema de seguridad: usuario 'replicacion' para verificación, 'root' para escritura")
    
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
                st.success(f"Carrera '{nombre_carrera}' replicada  exitosamente")
    
    return success


def execute_profesor_replication(nombre_profesor: str, email_profesor: str, sede_profesor: str, salario: float = None, progress_bar=None, status_container=None) -> bool:

    sede_map = {"Central": 1, "San Carlos": 2, "Heredia": 3}
    id_sede = sede_map.get(sede_profesor, 1)
    
    if status_container:
        with status_container:
            st.info("Sistema de seguridad: usuario 'replicacion' para verificación, 'root' para escritura")
    
    replicator = MasterSlaveReplication()
    
    def update_progress(progress):
        if progress_bar:
            progress_bar.progress(progress)
    
    def update_status(message):
        if status_container:
            with status_container:
                st.info(message)
    
    success = replicator.replicate_profesor(
        nombre_profesor=nombre_profesor,
        email_profesor=email_profesor,
        id_sede=id_sede,
        progress_callback=update_progress,
        status_callback=update_status
    )
    
    if success and salario is not None:
        try:
            if status_container:
                with status_container:
                    st.info("Registrando salario en planillas...")
            
            profesor_id = replicator.get_last_inserted_profesor_id()
            
            if profesor_id:
                planilla_success = _insert_profesor_planilla(profesor_id, salario)
                
                if planilla_success:
                    if status_container:
                        with status_container:
                            st.success(f"Salario ₡{salario:,} registrado en planillas para profesor ID {profesor_id}")
                else:
                    if status_container:
                        with status_container:
                            st.warning("Profesor replicado exitosamente, pero hubo un problema al registrar el salario en planilla")
            else:
                if status_container:
                    with status_container:
                        st.warning("No se pudo obtener el ID del profesor para registrar en planilla")
                        
        except Exception as e:
            if status_container:
                with status_container:
                    st.warning(f"Profesor replicado exitosamente, pero error al registrar salario: {str(e)}")
    
    if success:
        if status_container:
            with status_container:
                st.success(f"Profesor '{nombre_profesor}' replicado exitosamente")
                st.info("🔍 Verificación realizada con usuario de replicación especializado")
    
    return success


def _insert_profesor_planilla(profesor_id: int, salario: float) -> bool:
    try:
        from datetime import datetime
        from utils.db_connections import get_db_connection
        
        mes_actual = datetime.now().strftime("%Y-%m")
        
        with get_db_connection('central') as db:
            if not db:
                raise Exception("No se pudo conectar a la base de datos Central")
            
            query = """
            INSERT INTO planilla (id_profesor, salario, mes) 
            VALUES (%s, %s, %s)
            """
            
            affected_rows = db.execute_update(query, (profesor_id, salario, mes_actual))
            
            if affected_rows and affected_rows > 0:
                logger.info(f"💰 Salario registrado en planilla: Profesor ID {profesor_id}, Salario: ₡{salario:,}, Mes: {mes_actual}")
                return True
            else:
                raise Exception("No se afectaron filas en la tabla planilla")
                
    except Exception as e:
        logger.error(f"Error al insertar en planilla: {e}")
        return False