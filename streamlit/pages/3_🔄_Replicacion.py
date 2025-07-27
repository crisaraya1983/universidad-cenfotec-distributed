"""
Página de demostración de Replicación con Usuario Especializado
Sistema profesional que usa usuario 'replicacion' para verificación y 'root' para escritura
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

# Importar utilidades
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    DB_CONFIG, COLORS, get_sede_info, MESSAGES, 
    REPLICATION_CONFIG, get_connection_for_operation, get_user_info_for_operation
)
from utils.db_connections import get_db_connection, get_redis_connection, execute_real_transfer, log_transfer_audit
from utils.replication import execute_master_slave_replication, MasterSlaveReplication

# Configuración de la página
st.set_page_config(
    page_title="Replicación - Sistema Cenfotec",
    page_icon="🔄",
    layout="wide"
)

# Título de la página
st.title("🔄 Sistema de Replicación de Datos")

# Introducción mejorada con información de seguridad
st.markdown("""
### 🎯 **Replicación Master-Slave**

Este sistema implementa **replicación real** usando **usuarios especializados** para mayor seguridad:

- 🔍 **Usuario `replicacion`**: Verificación y monitoreo (solo lectura)
- 🔧 **Usuario `root`**: Operaciones de escritura (permisos completos)
- 📊 **Logging completo**: En tabla `replication_log` existente
- ✅ **Verificación de consistencia**: Usando ambos usuarios según corresponda
""")

# Información del usuario de replicación
with st.expander("🔐 **Información del Usuario de Replicación**", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 👤 Usuario: `replicacion`
        
        **Permisos Otorgados:**
        ```sql
        GRANT REPLICATION SLAVE ON *.* TO 'replicacion'@'%';
        GRANT SELECT ON cenfotec_central.sede TO 'replicacion'@'%';
        GRANT SELECT ON cenfotec_central.carrera TO 'replicacion'@'%';
        GRANT SELECT ON cenfotec_central.profesor TO 'replicacion'@'%';
        ```
        
        **Propósito:**
        - Verificación de datos maestros
        - Monitoreo de replicación
        - Validación de consistencia
        """)
    
    with col2:
        st.markdown("""
        ### 🛡️ Modelo de Seguridad
        
        **Separación de Responsabilidades:**
        - **Lectura/Verificación**: Usuario `replicacion`
        - **Escritura/Modificación**: Usuario `root`
        
        **Ventajas:**
        - ✅ Principio de menor privilegio
        - ✅ Auditoría granular
        - ✅ Menor superficie de ataque
        - ✅ Conformidad con buenas prácticas
        """)

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Arquitectura",
    "🎯 Replicación",
    "🔄 Sincronización", 
    "📊 Monitoreo Avanzado"
])

with tab1:
    st.header("🏗️ Arquitectura de Replicación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Modelo Master-Slave con Usuarios Especializados
        
        **Flujo de Operaciones:**
        
        1. **Verificación Inicial** 🔍
           - Usuario `replicacion` verifica permisos
           - Valida conectividad a tablas maestras
        
        2. **Inserción en Master** 🔧
           - Usuario `root` inserta nueva carrera
           - Control transaccional completo
        
        3. **Propagación a Slaves** 🔄
           - Usuario `root` replica a sedes regionales
           - Manejo de duplicados y conflictos
        
        4. **Verificación de Consistencia** ✅
           - Usuario `replicacion` valida datos
           - Comparación Master vs Slaves
        
        5. **Auditoría** 📊
           - Registro en `replication_log`
           - Metadatos de usuarios utilizados
        """)
    
    with col2:
        # Diagrama mejorado con usuarios
        fig = go.Figure()
        
        # Master con usuario info
        fig.add_trace(go.Scatter(
            x=[2], y=[3],
            mode='markers+text',
            marker=dict(size=80, color='#1f77b4', symbol='star'),
            text=['MASTER<br>Central<br>👤 replicacion (R)<br>👤 root (W)'],
            textposition="bottom center",
            name='Master'
        ))
        
        # Slaves
        fig.add_trace(go.Scatter(
            x=[0, 4], y=[1, 1],
            mode='markers+text',
            marker=dict(size=60, color='#ff7f0e', symbol='circle'),
            text=['SLAVE<br>San Carlos<br>👤 root (RW)', 'SLAVE<br>Heredia<br>👤 root (RW)'],
            textposition="bottom center",
            name='Slaves'
        ))
        
        # Flechas de replicación
        fig.add_annotation(x=0, y=1, ax=2, ay=3,
                          xref="x", yref="y", axref="x", ayref="y",
                          arrowhead=2, arrowsize=1, arrowwidth=3,
                          arrowcolor='#28a745', text="Replicación")
        
        fig.add_annotation(x=4, y=1, ax=2, ay=3,
                          xref="x", yref="y", axref="x", ayref="y",
                          arrowhead=2, arrowsize=1, arrowwidth=3,
                          arrowcolor='#28a745')
        
        # Flecha de verificación
        fig.add_annotation(x=2, y=2.5, ax=1, ay=1.5,
                          xref="x", yref="y", axref="x", ayref="y",
                          arrowhead=2, arrowsize=1, arrowwidth=2,
                          arrowcolor='#17a2b8', text="Verificación")
        
        fig.update_layout(
            title="Arquitectura con Usuarios Especializados",
            showlegend=False,
            height=400,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 5]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 4])
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("🎯 Replicación con Sistema de Usuarios")
    
    # Estado del sistema con información de usuarios
    st.subheader("📊 Estado del Sistema (EN VIVO)")
    
    col1, col2, col3 = st.columns(3)
    
    # Mostrar estado usando usuario de replicación
    replicator = MasterSlaveReplication()
    status = replicator.get_replication_status_detailed()
    
    for idx, (sede, info) in enumerate(status.items()):
        with [col1, col2, col3][idx]:
            st.markdown(f"### {sede.title()}")
            
            if info.get('disponible', False):
                st.success(f"✅ Conectado ({info['total_carreras']} carreras)")
                
                # Información del usuario
                user_type = info.get('user_type', 'unknown')
                permissions = info.get('permissions', 'unknown')
                
                if user_type == 'replication_user':
                    st.info("🔍 Usuario: `replicacion` (Solo lectura)")
                elif user_type == 'admin_user':
                    st.info("🔧 Usuario: `root` (Lectura/Escritura)")
                else:
                    st.warning(f"❓ Usuario: {user_type}")
                    
            else:
                st.error("❌ Desconectado")
    
    if st.button("🔄 Refrescar Estado del Sistema", type="secondary"):
        st.rerun()
    
    # Replicación con usuarios especializados
    st.subheader("🚀 Ejecutar Replicación Profesional")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### ⚡ **Proceso Automatizado de Replicación**
        
        Este proceso utiliza **automáticamente** el usuario apropiado para cada operación:
        
        1. 🔍 **Verificación inicial** con usuario `replicacion`
        2. 🔧 **Inserción en Master** con usuario `root`
        3. 🔄 **Replicación a Slaves** con usuario `root`
        4. ✅ **Verificación final** con usuario `replicacion`
        5. 📊 **Registro de auditoría** con usuario `root`
        """)
        
        with st.form("nueva_carrera_form_profesional"):
            st.markdown("**🎓 Agregar Nueva Carrera (Replicación Profesional)**")
            
            nombre_carrera = st.text_input("Nombre de la carrera:", 
                                         placeholder="Ej: Ciencia de Datos")
            sede_carrera = st.selectbox("Sede donde se impartirá:", 
                                       ["Central", "San Carlos", "Heredia"])
            
            st.info("ℹ️ El sistema seleccionará automáticamente el usuario apropiado para cada operación")
            
            submitted = st.form_submit_button("🚀 EJECUTAR REPLICACIÓN PROFESIONAL", type="primary")
            
            if submitted and nombre_carrera:
                # Contenedores para mostrar progreso
                progress_container = st.container()
                status_container = st.container()
                
                with progress_container:
                    st.markdown("### 📈 Progreso de Replicación")
                    progress_bar = st.progress(0)
                
                with status_container:
                    st.markdown("### 📝 Log de Operaciones")
                
                # Ejecutar replicación profesional
                success = execute_master_slave_replication(
                    nombre_carrera=nombre_carrera,
                    sede_destino=sede_carrera,
                    progress_bar=progress_bar,
                    status_container=status_container
                )
                
                if success:
                    st.balloons()
                    st.success("🎉 ¡Replicación profesional completada!")
                    
                    # Mostrar detalles de la operación
                    with st.expander("📋 **Detalles de la Operación**", expanded=True):
                        st.markdown("""
                        **✅ Operación completada exitosamente**
                        
                        **Usuarios utilizados:**
                        - 🔍 `replicacion`: Verificación de permisos y consistencia
                        - 🔧 `root`: Inserción en Master y Slaves
                        
                        **Verificaciones realizadas:**
                        - ✅ Permisos del usuario de replicación
                        - ✅ Inserción en base de datos Central
                        - ✅ Propagación a sedes regionales
                        - ✅ Consistencia entre todas las sedes
                        - ✅ Registro en audit log
                        """)
                    
                    if st.button("🔄 Ver Cambios Ahora", type="secondary"):
                        st.rerun()
                else:
                    st.error("❌ Error en la replicación profesional")
            
            elif submitted and not nombre_carrera:
                st.error("Por favor ingresa un nombre de carrera")
    
    with col2:
        st.markdown("### 📊 Métricas del Sistema")
        
        # Información de usuarios activos
        st.markdown("#### 👥 Usuarios Activos")
        
        # Usuario de replicación
        try:
            from utils.replication import ReplicationConnection
            repl_conn = ReplicationConnection()
            
            # Test de conexión con usuario replicación
            try:
                with repl_conn.get_master_connection('read') as db:
                    if db:
                        st.success("🔍 `replicacion`: ✅ Activo")
                    else:
                        st.error("🔍 `replicacion`: ❌ Error")
            except:
                st.error("🔍 `replicacion`: ❌ No disponible")
                
        except:
            st.warning("🔍 `replicacion`: ⚠️ Sin verificar")
        
        # Usuario admin
        with get_db_connection('central') as db:
            if db:
                st.success("🔧 `root`: ✅ Activo")
            else:
                st.error("🔧 `root`: ❌ Error")
        
        st.markdown("#### 📈 Estadísticas")
        
        # Estadísticas del replication log
        with get_db_connection('central') as db:
            if db:
                # Total operaciones hoy
                today_query = """
                SELECT COUNT(*) as total 
                FROM replication_log 
                WHERE DATE(timestamp_operacion) = CURDATE()
                """
                result = db.execute_query(today_query)
                total_hoy = result[0]['total'] if result else 0
                
                # Operaciones exitosas vs errores
                status_query = """
                SELECT estado_replicacion, COUNT(*) as count
                FROM replication_log 
                WHERE DATE(timestamp_operacion) = CURDATE()
                GROUP BY estado_replicacion
                """
                result = db.execute_query(status_query)
                
                exitosas = 0
                errores = 0
                for row in result or []:
                    if row['estado_replicacion'] == 'procesado':
                        exitosas = row['count']
                    elif row['estado_replicacion'] == 'error':
                        errores = row['count']
                
                st.metric("Ops. Hoy", total_hoy)
                st.metric("Exitosas", exitosas, delta=exitosas-errores if exitosas > errores else None)
                st.metric("Errores", errores, delta=-errores if errores > 0 else None)

with tab3:
    st.header("🔄 Sincronización Bidireccional")
    
    st.markdown("""
    ### 👥 Transferencia de Estudiantes
    
    Las transferencias de estudiantes usan el **usuario administrativo** ya que requieren 
    permisos de escritura en múltiples sedes.
    """)
    
    # ... (código de transferencias existente)
    st.info("🚧 Funcionalidad de transferencias mantiene el sistema de usuarios existente")

with tab4:
    st.header("📊 Monitoreo Avanzado con Usuarios Especializados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Verificación con Usuario de Replicación")
        
        # Verificar estado usando usuario de replicación
        try:
            from utils.replication import ReplicationConnection
            repl_conn = ReplicationConnection()
            
            with repl_conn.get_master_connection('read') as db:
                if db:
                    st.success("✅ Conexión con usuario `replicacion` exitosa")
                    
                    # Verificar acceso a tablas
                    tables_to_check = ['sede', 'carrera', 'profesor']
                    access_results = {}
                    
                    for table in tables_to_check:
                        try:
                            query = f"SELECT COUNT(*) as count FROM {table} LIMIT 1"
                            result = db.execute_query(query)
                            access_results[table] = result[0]['count'] if result else 0
                        except Exception as e:
                            access_results[table] = f"Error: {str(e)}"
                    
                    st.markdown("**Acceso a Tablas:**")
                    for table, result in access_results.items():
                        if isinstance(result, int):
                            st.success(f"✅ {table}: {result} registros")
                        else:
                            st.error(f"❌ {table}: {result}")
                            
                else:
                    st.error("❌ No se pudo conectar con usuario `replicacion`")
                    
        except Exception as e:
            st.error(f"❌ Error en verificación: {str(e)}")
    
    with col2:
        st.subheader("📈 Actividad del Replication Log")
        
        # Mostrar actividad reciente del replication log
        with get_db_connection('central') as db:
            if db:
                query = """
                SELECT tabla_afectada, operacion, estado_replicacion,
                       timestamp_operacion, usuario
                FROM replication_log 
                ORDER BY timestamp_operacion DESC 
                LIMIT 10
                """
                df_activity = db.get_dataframe(query)
                if df_activity is not None and not df_activity.empty:
                    st.dataframe(df_activity, use_container_width=True, hide_index=True)
                    
                    # Gráfico de estados
                    if len(df_activity) > 0:
                        status_counts = df_activity['estado_replicacion'].value_counts()
                        fig = px.pie(
                            values=status_counts.values,
                            names=status_counts.index,
                            title="Distribución de Estados (Últimas 10 ops)",
                            color_discrete_map={
                                'procesado': '#28a745',
                                'error': '#dc3545',
                                'pendiente': '#ffc107'
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay actividad reciente en replication_log")

# Footer con información adicional
st.markdown("---")
with st.expander("ℹ️ **Información Técnica del Sistema**"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔐 Configuración de Seguridad
        
        **Usuario de Replicación:**
        - Host: `172.20.0.10` (Central)
        - Usuario: `replicacion`
        - Permisos: Solo lectura en tablas maestras
        
        **Usuario Administrativo:**
        - Host: Variable por sede
        - Usuario: `root`
        - Permisos: Lectura/Escritura completa
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Tablas del Sistema
        
        **Replicadas (Master→Slaves):**
        - `sede` - Información de sedes
        - `carrera` - Catálogo de carreras  
        - `profesor` - Información de profesores
        
        **Locales por Sede:**
        - `estudiante` - Datos de estudiantes
        - `matricula` - Inscripciones
        - `pago` - Transacciones financieras
        """)

# Auto-refresh opcional
if st.sidebar.checkbox("🔄 Auto-actualizar (30s)", help="Actualiza automáticamente el estado del sistema"):
    time.sleep(30)
    st.rerun()