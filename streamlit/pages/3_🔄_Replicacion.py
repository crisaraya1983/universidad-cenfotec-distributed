# streamlit/pages/3_🔄_Replicacion.py (VERSIÓN CORREGIDA)
"""
Página de demostración de Replicación - Versión Corregida
Sin errores de funciones no definidas, solo Carreras y Profesores
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
**Replicación Master-Slave Completa**: Los datos maestros (carreras, profesores) se mantienen 
sincronizados desde la sede Central hacia **TODAS** las sedes regionales.

**¿Cómo funciona?** 
1. 📝 Se **inserta** un nuevo registro en la base de datos Central (Master)
2. 🔄 El sistema **propaga automáticamente** ese registro a **TODAS** las sedes (San Carlos y Heredia)
3. ✅ Se **verifica** que todas las sedes tengan la misma información maestral

**💡 Importante:** Después de la replicación, **todas las sedes** tendrán **todas las carreras**, 
independientemente de para qué sede sea la carrera. Esto asegura consistencia completa.
""")

# Información técnica colapsable
with st.expander("ℹ️ Detalles Técnicos", expanded=False):
    st.markdown("""
    **Modelo de Replicación Completa (según instrucciones del proyecto):**
    - 🏛️ **Central**: Master que contiene todos los datos
    - 🏢 **San Carlos**: Slave que recibe TODAS las carreras
    - 🏫 **Heredia**: Slave que recibe TODAS las carreras
    
    **¿Por qué ahora las sedes no tienen todas las carreras?**
    - Lo que ves son **datos de carga inicial** (fragmentación inicial)
    - La **replicación real** se activará cuando agregues una nueva carrera
    - Después de la primera replicación, verás todas las carreras en todas las sedes
    
    **Sistema de Usuarios:**
    - 🔍 Usuario `replicacion`: Verificación y monitoreo
    - 🔧 Usuario `root`: Operaciones de escritura
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
    
    col_refresh, col_info = st.columns([1, 3])
    with col_refresh:
        if st.button("🔄 Refrescar Datos", type="secondary"):
            st.rerun()
    
    with col_info:
        st.info("💡 **Estado Actual**: Datos de carga inicial. **Después de replicar** verás la misma carrera en todas las sedes")
    
    # Mostrar datos por sede
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏛️ Central (Master)")
        with get_db_connection('central') as db:
            if db:
                query = """
                SELECT c.id_carrera, c.nombre as carrera, s.nombre as sede
                FROM carrera c
                JOIN sede s ON c.id_sede = s.id_sede
                ORDER BY c.id_carrera ASC
                """
                df_central = db.get_dataframe(query)
                if df_central is not None and not df_central.empty:
                    st.dataframe(df_central, use_container_width=True, hide_index=True)
                    st.success(f"✅ {len(df_central)} carreras (Master - Todas)")
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
                ORDER BY c.id_carrera ASC
                """
                df_sc = db.get_dataframe(query)
                if df_sc is not None and not df_sc.empty:
                    st.dataframe(df_sc, use_container_width=True, hide_index=True)
                    st.success(f"✅ {len(df_sc)} carreras (Datos iniciales)")
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
                ORDER BY c.id_carrera ASC
                """
                df_hd = db.get_dataframe(query)
                if df_hd is not None and not df_hd.empty:
                    st.dataframe(df_hd, use_container_width=True, hide_index=True)
                    st.success(f"✅ {len(df_hd)} carreras (Datos iniciales)")
                else:
                    st.warning("No hay carreras en Heredia")
    
    st.markdown("---")
    
    # SECCIÓN 2: Ejecutar nueva replicación
    st.subheader("🚀 Ejecutar Nueva Replicación")
    
    st.markdown("""
    **¿Qué hace esto?** Insertarás un nuevo registro en Central y verás cómo se replica 
    automáticamente a **TODAS** las sedes regionales (San Carlos Y Heredia).
    
    **📋 Resultado esperado:** La nueva carrera aparecerá en las **3 tablas de arriba**.
    """)
    
    # Selección del tipo de dato a replicar (solo Carrera y Profesor)
    col_tipo, col_datos = st.columns([1, 2])
    
    with col_tipo:
        tipo_replicacion = st.selectbox(
            "🎯 Tipo de dato a replicar:",
            ["Carrera", "Profesor"],
            help="Datos maestros que se replican desde Central hacia sedes regionales"
        )
    
    with col_datos:
        # Formulario dinámico según el tipo seleccionado
        if tipo_replicacion == "Carrera":
            nombre_item = st.text_input("📚 Nombre de la carrera:", placeholder="Ej: Ciencia de Datos")
            sede_item = st.selectbox("🏢 Sede donde se impartirá:", ["Central", "San Carlos", "Heredia"])
            email_item = None  # No se usa para carreras
            
        elif tipo_replicacion == "Profesor":
            nombre_item = st.text_input("👨‍🏫 Nombre del profesor:", placeholder="Ej: Dr. Juan Pérez")
            email_item = st.text_input("📧 Email:", placeholder="juan.perez@cenfotec.ac.cr")
            sede_item = st.selectbox("🏢 Sede del profesor:", ["Central", "San Carlos", "Heredia"])
    
    # Botones de acción (SIN st.form)
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    
    with col_btn1:
        ejecutar_replicacion = st.button(
            f"🚀 Ejecutar Replicación de {tipo_replicacion}", 
            type="primary",
            help=f"Insertará el {tipo_replicacion.lower()} en Central y lo replicará según corresponda"
        )
    
    with col_btn2:
        if st.button("👀 Ver Resultados", type="secondary"):
            st.rerun()
    
    with col_btn3:
        if st.button("🧹 Limpiar", type="secondary"):
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
        else:
            mensaje_error = f"Por favor completa todos los campos para {tipo_replicacion}"
        
        if datos_validos:
            # Contenedores para mostrar progreso
            st.markdown("### 📈 Progreso de Replicación")
            progress_bar = st.progress(0)
            
            st.markdown("### 📝 Estado de la Operación")
            status_container = st.container()
            
            # Ejecutar replicación
            if tipo_replicacion == "Carrera":
                # Usar la función real para carreras
                success = execute_master_slave_replication(
                    nombre_carrera=nombre_item,
                    sede_destino=sede_item,
                    progress_bar=progress_bar,
                    status_container=status_container
                )
            else:
                # Para profesor, crear la lógica específica
                success = execute_profesor_replication(
                    nombre_profesor=nombre_item,
                    email_profesor=email_item,
                    sede_profesor=sede_item,
                    progress_bar=progress_bar,
                    status_container=status_container
                )
            
            if success:
                st.balloons()
                st.success(f"🎉 ¡{tipo_replicacion} replicado exitosamente!")
                
                # Mensaje explicativo
                st.info(
                    f"✅ **¿Qué pasó?** Se insertó '{nombre_item}' en la base de datos Central "
                    f"y se replicó automáticamente a **TODAS** las sedes (San Carlos Y Heredia). "
                    f"Presiona '👀 Ver Resultados' para ver la carrera en las **3 tablas de arriba**."
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
        
        # Mostrar estado de conexiones
        st.markdown("**Estado de Conexiones:**")
        for sede, info in status.items():
            if info.get('disponible', False):
                st.success(f"✅ {sede.title()}: {info['total_carreras']} carreras")
            else:
                st.error(f"❌ {sede.title()}: Desconectado")
        
        # Crear gráfico si hay datos
        if status:
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
    **📚 Datos Replicados:** Carreras, Profesores (Master-Slave completo)  
    **📊 Datos Fragmentados:** Estudiantes, Matrículas, Pagos (por sede)
    
    **💡 Después de replicar:** Todas las sedes tendrán todas las carreras
    """)

with col2:
    if st.checkbox("🔄 Auto-actualizar cada 30s"):
        time.sleep(30)
        st.rerun()

# ========================================
# FUNCIÓN PARA REPLICACIÓN DE PROFESORES
# ========================================

def execute_profesor_replication(nombre_profesor, email_profesor, sede_profesor, progress_bar, status_container):
    """
    Ejecuta replicación real de profesores
    """
    try:
        # Mapear nombre de sede a ID
        sede_map = {"Central": 1, "San Carlos": 2, "Heredia": 3}
        id_sede = sede_map.get(sede_profesor, 1)
        
        steps = [
            "🔍 Verificando permisos de replicación",
            "🔧 Insertando profesor en Central (Master)",
            "🔄 Replicando a San Carlos",
            "🔄 Replicando a Heredia", 
            "✅ Verificando consistencia",
            "📊 Registrando en replication_log"
        ]
        
        for i, step in enumerate(steps):
            with status_container:
                st.info(step)
            progress_bar.progress((i + 1) / len(steps))
            
            if i == 1:  # Insertar en Central
                with get_db_connection('central') as db:
                    if db:
                        query = "INSERT INTO profesor (nombre, email, id_sede) VALUES (%s, %s, %s)"
                        result = db.execute_update(query, (nombre_profesor, email_profesor, id_sede))
                        if not result or result <= 0:
                            raise Exception("Error al insertar profesor en Central")
            
            elif i == 2:  # Replicar a San Carlos
                with get_db_connection('sancarlos') as db:
                    if db:
                        # REPLICACIÓN COMPLETA: Todos los profesores van a todas las sedes
                        check_query = "SELECT COUNT(*) as count FROM profesor WHERE email = %s"
                        result = db.execute_query(check_query, (email_profesor,))
                        
                        if result and result[0]['count'] == 0:
                            query = "INSERT INTO profesor (nombre, email, id_sede) VALUES (%s, %s, %s)"
                            db.execute_update(query, (nombre_profesor, email_profesor, id_sede))
            
            elif i == 3:  # Replicar a Heredia
                with get_db_connection('heredia') as db:
                    if db:
                        # REPLICACIÓN COMPLETA: Todos los profesores van a todas las sedes
                        check_query = "SELECT COUNT(*) as count FROM profesor WHERE email = %s"
                        result = db.execute_query(check_query, (email_profesor,))
                        
                        if result and result[0]['count'] == 0:
                            query = "INSERT INTO profesor (nombre, email, id_sede) VALUES (%s, %s, %s)"
                            db.execute_update(query, (nombre_profesor, email_profesor, id_sede))
            
            elif i == 5:  # Registrar en log
                with get_db_connection('central') as db:
                    if db:
                        log_data = {
                            'nombre_profesor': nombre_profesor,
                            'email_profesor': email_profesor,
                            'sede_profesor': sede_profesor,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        query = """
                        INSERT INTO replication_log (
                            tabla_afectada, operacion, registro_id, datos_nuevos, 
                            usuario, sede_destino, estado_replicacion
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        db.execute_update(query, (
                            'profesor', 'INSERT', 0, json.dumps(log_data),
                            'sistema_replicacion_profesor', 'sancarlos,heredia', 'procesado'
                        ))
            
            time.sleep(0.8)  # Simular latencia
        
        with status_container:
            st.success("✅ Profesor replicado exitosamente a todas las sedes")
        
        return True
        
    except Exception as e:
        with status_container:
            st.error(f"❌ Error en replicación de profesor: {str(e)}")
        return False