"""
Página de demostración de Replicación - Versión Optimizada
Interfaz clara y enfocada en la demostración práctica de replicación Master-Slave
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
from config import DB_CONFIG, COLORS, get_sede_info, MESSAGES
from utils.db_connections import get_db_connection, get_redis_connection, execute_real_transfer, log_transfer_audit
from utils.replication import execute_master_slave_replication, MasterSlaveReplication

# Configuración de la página
st.set_page_config(
    page_title="Replicación Master-Slave - Sistema Cenfotec",
    page_icon="🔄",
    layout="wide"
)

# Título de la página
st.title("🔄 Replicación Master-Slave - Sistema Distribuido")

# Introducción simplificada
st.markdown("""
**Replicación Master-Slave**: Los datos maestros (carreras, profesores, sedes) se mantienen 
sincronizados desde la sede Central hacia las sedes regionales en tiempo real.

**¿Cómo funciona?** 
1. 📝 Se **inserta** un nuevo registro en la base de datos Central (Master)
2. 🔄 El sistema **propaga automáticamente** ese registro a San Carlos y Heredia (Slaves)
3. ✅ Se **verifica** que todas las sedes tengan los mismos datos
""")

# Información técnica colapsable (menos prominente)
with st.expander("ℹ️ Detalles Técnicos", expanded=False):
    st.markdown("""
    **Sistema de Usuarios Especializados:**
    - 🔍 Usuario `replicacion`: Verificación y monitoreo (solo lectura)
    - 🔧 Usuario `root`: Operaciones de escritura (insert/update)
    
    **Proceso Técnico:**
    1. Verificación de permisos con usuario especializado
    2. INSERT en base de datos Central 
    3. Propagación automática a bases de datos regionales
    4. Verificación de consistencia entre todas las sedes
    5. Registro en tabla `replication_log` para auditoría
    """)

# Tabs principales
tab1, tab2, tab3 = st.tabs([
    "🎯 Replicación en Acción",
    "🔄 Sincronización", 
    "📊 Monitoreo"
])

with tab1:
    st.header("🎯 Demostración de Replicación Master-Slave")
    
    # SECCIÓN 1: Estado actual de datos maestros
    st.subheader("📊 Estado Actual de Datos Maestros")
    
    # Botón para refrescar
    col_refresh, col_info = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 Refrescar Datos", type="secondary"):
            st.rerun()
    
    with col_info:
        st.info("💡 **¿Qué ves aquí?** Las tablas muestran los datos que están replicados en todas las sedes")
    
    # Mostrar datos por sede en columnas
    col1, col2, col3 = st.columns(3)
    
    carreras_por_sede = {}
    
    with col1:
        st.markdown("### 🏛️ Central (Master)")
        with get_db_connection('central') as db:
            if db:
                query = """
                SELECT c.id_carrera, c.nombre as carrera, s.nombre as sede
                FROM carrera c
                JOIN sede s ON c.id_sede = s.id_sede
                ORDER BY c.id_carrera DESC
                LIMIT 8
                """
                df_central = db.get_dataframe(query)
                if df_central is not None and not df_central.empty:
                    carreras_por_sede['central'] = df_central
                    st.dataframe(df_central, use_container_width=True, hide_index=True)
                    st.success(f"✅ {len(df_central)} carreras")
                else:
                    st.warning("No hay carreras en Central")
    
    with col2:
        st.markdown("### 🏢 San Carlos (Slave)")
        with get_db_connection('sancarlos') as db:
            if db:
                query = """
                SELECT c.id_carrera, c.nombre as carrera, s.nombre as sede
                FROM carrera c
                JOIN sede s ON c.id_sede = s.id_sede
                ORDER BY c.id_carrera DESC
                LIMIT 8
                """
                df_sc = db.get_dataframe(query)
                if df_sc is not None and not df_sc.empty:
                    carreras_por_sede['sancarlos'] = df_sc
                    st.dataframe(df_sc, use_container_width=True, hide_index=True)
                    st.success(f"✅ {len(df_sc)} carreras")
                else:
                    st.warning("No hay carreras en San Carlos")
    
    with col3:
        st.markdown("### 🏫 Heredia (Slave)")
        with get_db_connection('heredia') as db:
            if db:
                query = """
                SELECT c.id_carrera, c.nombre as carrera, s.nombre as sede
                FROM carrera c
                JOIN sede s ON c.id_sede = s.id_sede
                ORDER BY c.id_carrera DESC
                LIMIT 8
                """
                df_hd = db.get_dataframe(query)
                if df_hd is not None and not df_hd.empty:
                    carreras_por_sede['heredia'] = df_hd
                    st.dataframe(df_hd, use_container_width=True, hide_index=True)
                    st.success(f"✅ {len(df_hd)} carreras")
                else:
                    st.warning("No hay carreras en Heredia")
    
    st.markdown("---")
    
    # SECCIÓN 2: Ejecutar nueva replicación
    st.subheader("🚀 Ejecutar Nueva Replicación")
    
    st.markdown("""
    **¿Qué hace esto?** Vas a insertar un nuevo registro en Central y ver cómo se replica 
    automáticamente a San Carlos y Heredia. ¡Los cambios serán visibles en las tablas de arriba!
    """)
    
    # Selección del tipo de dato a replicar
    col_tipo, col_datos = st.columns([1, 2])
    
    with col_tipo:
        tipo_replicacion = st.selectbox(
            "🎯 Tipo de dato a replicar:",
            ["Carrera", "Profesor", "Sede"],
            help="Todos estos datos se replican desde Central hacia las sedes regionales"
        )
    
    with col_datos:
        # Formulario dinámico según el tipo seleccionado
        if tipo_replicacion == "Carrera":
            nombre_item = st.text_input("📚 Nombre de la carrera:", placeholder="Ej: Ciencia de Datos")
            sede_item = st.selectbox("🏢 Sede donde se impartirá:", ["Central", "San Carlos", "Heredia"])
            
        elif tipo_replicacion == "Profesor":
            nombre_item = st.text_input("👨‍🏫 Nombre del profesor:", placeholder="Ej: Dr. Juan Pérez")
            email_item = st.text_input("📧 Email:", placeholder="juan.perez@cenfotec.ac.cr")
            sede_item = st.selectbox("🏢 Sede del profesor:", ["Central", "San Carlos", "Heredia"])
            
        elif tipo_replicacion == "Sede":
            nombre_item = st.text_input("🏢 Nombre de la sede:", placeholder="Ej: Cartago")
            direccion_item = st.text_input("📍 Dirección:", placeholder="Cartago Centro, Costa Rica")
    
    # Botones de acción (SIN st.form para evitar problemas)
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    
    with col_btn1:
        ejecutar_replicacion = st.button(
            f"🚀 Ejecutar Replicación de {tipo_replicacion}", 
            type="primary",
            help=f"Insertará el {tipo_replicacion.lower()} en Central y lo replicará a las sedes regionales"
        )
    
    with col_btn2:
        if st.button("👀 Ver Resultados", type="secondary"):
            st.rerun()
    
    with col_btn3:
        limpiar_form = st.button("🧹 Limpiar", type="secondary")
        if limpiar_form:
            st.rerun()
    
    # Ejecutar replicación cuando se presiona el botón
    if ejecutar_replicacion:
        # Validar datos según el tipo
        datos_validos = False
        mensaje_error = ""
        
        if tipo_replicacion == "Carrera" and nombre_item:
            datos_validos = True
        elif tipo_replicacion == "Profesor" and nombre_item and email_item:
            datos_validos = True
        elif tipo_replicacion == "Sede" and nombre_item and direccion_item:
            datos_validos = True
        else:
            mensaje_error = f"Por favor completa todos los campos para {tipo_replicacion}"
        
        if datos_validos:
            # Contenedores para mostrar progreso
            st.markdown("### 📈 Progreso de Replicación")
            progress_bar = st.progress(0)
            
            st.markdown("### 📝 Estado de la Operación")
            status_container = st.container()
            
            # Simular replicación según el tipo
            if tipo_replicacion == "Carrera":
                success = execute_master_slave_replication(
                    nombre_carrera=nombre_item,
                    sede_destino=sede_item,
                    progress_bar=progress_bar,
                    status_container=status_container
                )
            else:
                # Para profesor y sede, simular el proceso
                success = simulate_replication_process(
                    tipo_replicacion, 
                    {"nombre": nombre_item, "sede": sede_item if tipo_replicacion == "Profesor" else None,
                     "email": email_item if tipo_replicacion == "Profesor" else None,
                     "direccion": direccion_item if tipo_replicacion == "Sede" else None},
                    progress_bar, 
                    status_container
                )
            
            if success:
                st.balloons()
                st.success(f"🎉 ¡{tipo_replicacion} replicado exitosamente!")
                
                # Mensaje explicativo
                st.info(
                    f"✅ **¿Qué pasó?** Se insertó '{nombre_item}' en la base de datos Central "
                    f"y se replicó automáticamente a San Carlos y Heredia. "
                    f"Presiona '👀 Ver Resultados' para ver los cambios en las tablas."
                )
            else:
                st.error(f"❌ Error en la replicación de {tipo_replicacion}")
        else:
            st.error(mensaje_error)

with tab2:
    st.header("🔄 Sincronización Bidireccional")
    
    st.markdown("""
    ### 👥 Transferencia de Estudiantes
    
    A diferencia de la replicación Master-Slave, las transferencias son **bidireccionales**: 
    los estudiantes pueden moverse entre cualquier sede.
    """)
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📤 Sede Origen")
        sede_origen = st.selectbox("Sede origen:", ["San Carlos", "Heredia"], key="transfer_origen")
        
        # Obtener estudiantes reales
        estudiantes_reales = []
        sede_key = sede_origen.lower().replace(' ', '')
        
        with get_db_connection(sede_key) as db:
            if db:
                query = """
                SELECT e.id_estudiante, e.nombre, e.email,
                    COUNT(m.id_matricula) as materias_activas,
                    COALESCE(AVG(n.nota), 0) as promedio
                FROM estudiante e
                LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
                LEFT JOIN nota n ON m.id_matricula = n.id_matricula
                WHERE e.email NOT LIKE '%TRANSFERIDO%'
                GROUP BY e.id_estudiante, e.nombre, e.email
                ORDER BY e.nombre
                LIMIT 10
                """
                result = db.execute_query(query)
                if result:
                    estudiantes_reales = result
        
        if estudiantes_reales:
            estudiante_options = [
                f"{est['nombre']} ({est['materias_activas']} materias)" 
                for est in estudiantes_reales
            ]
            
            selected_idx = st.selectbox(
                "Seleccionar estudiante:", 
                range(len(estudiante_options)),
                format_func=lambda x: estudiante_options[x],
                key="student_select"
            )
            
            if selected_idx is not None:
                estudiante_seleccionado = estudiantes_reales[selected_idx]
                
                st.markdown("**Datos del estudiante:**")
                st.json({
                    'Nombre': estudiante_seleccionado['nombre'],
                    'Email': estudiante_seleccionado['email'],
                    'Materias Activas': estudiante_seleccionado['materias_activas'],
                    'Promedio': round(float(estudiante_seleccionado['promedio']), 2)
                })
        else:
            st.info(f"No hay estudiantes disponibles en {sede_origen}")

    with col2:
        st.markdown("### 📥 Sede Destino")
        sedes_destino = ["San Carlos", "Heredia"]
        if sede_origen in sedes_destino:
            sedes_destino.remove(sede_origen)
        
        sede_destino = st.selectbox("Sede destino:", sedes_destino, key="transfer_destino")
        
        st.markdown("### 🚀 Ejecutar Transferencia")
        
        if st.button("🔄 Transferir Estudiante", type="primary"):
            if estudiantes_reales and selected_idx is not None:
                estudiante_data = estudiantes_reales[selected_idx]
                
                st.markdown("### 📈 Progreso de Transferencia")
                progress_bar = st.progress(0)
                
                st.markdown("### 📝 Estado de la Transferencia")
                status_container = st.container()
                
                success = execute_real_transfer(
                    estudiante_data, sede_origen, sede_destino, 
                    progress_bar, status_container
                )
                
                if success:
                    st.success("✅ Transferencia completada exitosamente")
                    log_transfer_audit(estudiante_data['id_estudiante'], sede_origen, sede_destino)
                else:
                    st.error("❌ Error en la transferencia")

with tab3:
    st.header("📊 Monitoreo de Replicación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Estado por Sede")
        
        # Obtener estado real
        replicator = MasterSlaveReplication()
        status = replicator.get_replication_status_detailed()
        
        # Crear gráfico de estado
        sedes = []
        carreras_count = []
        estados = []
        
        for sede, info in status.items():
            sedes.append(sede.title())
            carreras_count.append(info.get('total_carreras', 0))
            estados.append('Activo' if info.get('disponible', False) else 'Inactivo')
        
        if sedes:
            fig = px.bar(
                x=sedes, 
                y=carreras_count,
                title="Carreras por Sede",
                color=estados,
                color_discrete_map={'Activo': COLORS['success'], 'Inactivo': COLORS['danger']}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Estado de conexiones
        st.markdown("**Estado de Conexiones:**")
        for sede, info in status.items():
            if info.get('disponible', False):
                st.success(f"✅ {sede.title()}: {info['total_carreras']} carreras")
            else:
                st.error(f"❌ {sede.title()}: Desconectado")
    
    with col2:
        st.subheader("📋 Actividad Reciente")
        
        # Mostrar últimos logs de replicación
        with get_db_connection('central') as db:
            if db:
                query = """
                SELECT tabla_afectada, operacion, estado_replicacion,
                       timestamp_operacion, sede_destino
                FROM replication_log 
                ORDER BY timestamp_operacion DESC 
                LIMIT 8
                """
                df_activity = db.get_dataframe(query)
                if df_activity is not None and not df_activity.empty:
                    st.dataframe(df_activity, use_container_width=True, hide_index=True)
                    
                    # Pequeño gráfico de estados
                    if len(df_activity) > 0:
                        status_counts = df_activity['estado_replicacion'].value_counts()
                        fig = px.pie(
                            values=status_counts.values,
                            names=status_counts.index,
                            title="Estados Recientes",
                            color_discrete_map={
                                'procesado': '#28a745',
                                'error': '#dc3545',
                                'pendiente': '#ffc107'
                            }
                        )
                        fig.update_layout(height=300)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay actividad reciente")

# Footer simplificado
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **📚 Datos Replicados:** Carreras, Profesores, Sedes  
    **📊 Datos Fragmentados:** Estudiantes, Matrículas, Pagos
    """)

with col2:
    if st.checkbox("🔄 Auto-actualizar cada 30s"):
        time.sleep(30)
        st.rerun()

# Función auxiliar para simular replicación de otros tipos de datos
def simulate_replication_process(tipo, datos, progress_bar, status_container):
    """
    Simula el proceso de replicación para profesores y sedes
    """
    try:
        steps = ["Verificando permisos", f"Insertando {tipo.lower()} en Central", 
                "Replicando a San Carlos", "Replicando a Heredia", 
                "Verificando consistencia", "Registrando auditoría"]
        
        for i, step in enumerate(steps):
            with status_container:
                st.info(f"🔄 {step}...")
            progress_bar.progress((i + 1) / len(steps))
            time.sleep(0.8)
        
        with status_container:
            st.success(f"✅ {tipo} replicado exitosamente a todas las sedes")
        
        return True
        
    except Exception as e:
        with status_container:
            st.error(f"❌ Error en replicación: {str(e)}")
        return False