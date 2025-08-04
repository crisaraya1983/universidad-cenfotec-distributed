"""
Página de demostración de Replicación 
Implementa replicación funcional para Carreras y Profesores con visualización dinámica
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
from utils.replication import execute_master_slave_replication, execute_profesor_replication, MasterSlaveReplication

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

**¿Cómo funciona la replicación?** 
1. 📝 Se **inserta** un nuevo registro en la base de datos Central (Master)
2. 🔄 El sistema **propaga automáticamente** ese registro a **TODAS** las sedes (San Carlos y Heredia)
3. ✅ Se **verifica** que todas las sedes tengan la misma información maestral

**💡 Importante:** Después de la replicación, **todas las sedes** tendrán **todos los datos maestros**, 
independientemente de para qué sede sea el registro. Esto asegura consistencia completa.
""")

# Información técnica colapsable
with st.expander("ℹ️ Detalles Técnicos", expanded=False):
    st.markdown("""
    **Modelo de Replicación Completa (según instrucciones del proyecto):**
    - 🏛️ **Central**: Master que contiene todos los datos
    - 🏢 **San Carlos**: Slave que recibe TODOS los datos maestros
    - 🏫 **Heredia**: Slave que recibe TODOS los datos maestros
    
    **¿Por qué ahora las sedes no tienen todos los datos?**
    - Lo que ves son **datos de carga inicial** (fragmentación inicial)
    - La **replicación real** se activará cuando agregues un nuevo registro
    - Después de la primera replicación, verás todos los datos en todas las sedes
    
    **Sistema de Usuarios:**
    - 🔍 Usuario `replicacion`: Verificación y monitoreo
    - 🔧 Usuario `root`: Operaciones de escritura
    """)

def obtener_logs_replicacion():
    """
    Obtiene los logs de replicación de la base de datos central
    """
    query = """
    SELECT 
        id,
        tabla_afectada,
        operacion,
        registro_id,
        datos_nuevos,
        usuario,
        sede_destino,
        estado_replicacion,
        timestamp_operacion
    FROM replication_log 
    ORDER BY timestamp_operacion DESC 
    LIMIT 50
    """
    
    try:
        with get_db_connection('central') as db:
            if db:
                df = db.get_dataframe(query)
                return df
            else:
                st.error("❌ No se pudo conectar a la base de datos central")
                return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error al obtener logs: {str(e)}")
        return pd.DataFrame()

def mostrar_logs_replicacion():
    """
    Muestra los logs de replicación en una tabla formateada
    """
    st.subheader("📋 Logs de Replicaciones")
    
    # Obtener los logs
    df_logs = obtener_logs_replicacion()
    
    if df_logs.empty:
        st.info("ℹ️ No hay logs de replicación disponibles")
        return
    
    # Crear tabs para diferentes vistas de los logs
    tab_recientes, tab_filtros, tab_estadisticas = st.tabs([
        "🕐 Recientes", 
        "🔍 Filtros", 
        "📊 Estadísticas"
    ])
    
    with tab_recientes:
        st.markdown("**Últimas 20 replicaciones:**")
        
        # Formatear el DataFrame para mejor visualización
        df_display = df_logs.head(20).copy()
        
        # Formatear fechas
        if 'timestamp_operacion' in df_display.columns:
            df_display['timestamp_operacion'] = pd.to_datetime(df_display['timestamp_operacion']).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Agregar emojis según el estado
        if 'estado_replicacion' in df_display.columns:
            estado_emojis = {
                'procesado': '✅',
                'error': '❌',
                'pendiente': '⏳',
                'en_proceso': '🔄'
            }
            df_display['Estado'] = df_display['estado_replicacion'].map(
                lambda x: f"{estado_emojis.get(x, '❓')} {x}"
            )
        
        # Mostrar tabla
        st.dataframe(
            df_display[['tabla_afectada', 'operacion', 'registro_id', 'sede_destino', 'Estado', 'timestamp_operacion']],
            use_container_width=True,
            column_config={
                "tabla_afectada": "Tabla",
                "operacion": "Operación",
                "registro_id": "ID Registro",
                "sede_destino": "Sede Destino",
                "Estado": "Estado",
                "timestamp_operacion": "Fecha"
            }
        )
    
    with tab_filtros:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tablas_disponibles = ['Todas'] + df_logs['tabla_afectada'].unique().tolist()
            tabla_filtro = st.selectbox("🗃️ Filtrar por tabla:", tablas_disponibles)
        
        with col2:
            estados_disponibles = ['Todos'] + df_logs['estado_replicacion'].unique().tolist()
            estado_filtro = st.selectbox("📊 Filtrar por estado:", estados_disponibles)
        
        with col3:
            fecha_filtro = st.date_input("📅 Desde fecha:", value=datetime.now().date() - timedelta(days=7))
        
        # Aplicar filtros
        df_filtrado = df_logs.copy()
        
        if tabla_filtro != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['tabla_afectada'] == tabla_filtro]
        
        if estado_filtro != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['estado_replicacion'] == estado_filtro]
        
        df_filtrado = df_filtrado[pd.to_datetime(df_filtrado['timestamp_operacion']).dt.date >= fecha_filtro]
        
        st.dataframe(df_filtrado, use_container_width=True)
    
    with tab_estadisticas:
        col1, col2 = st.columns(2)
        
        with col1:
            # Estadísticas por estado
            estado_counts = df_logs['estado_replicacion'].value_counts()
            fig_estados = px.pie(
                values=estado_counts.values,
                names=estado_counts.index,
                title="Distribución por Estado"
            )
            st.plotly_chart(fig_estados, use_container_width=True)
        
        with col2:
            # Estadísticas por tabla
            tabla_counts = df_logs['tabla_afectada'].value_counts()
            fig_tablas = px.bar(
                x=tabla_counts.index,
                y=tabla_counts.values,
                title="Replicaciones por Tabla"
            )
            st.plotly_chart(fig_tablas, use_container_width=True)


# Tabs principales
tab1, tab2, tab3 = st.tabs([
    "🎯 Replicación en Acción",
    "🔄 Sincronización", 
    "📊 Monitoreo"
])

with tab1:
    st.header("🎯 Demostración de Replicación Master-Slave")
    
    # SECCIÓN 1: Selección de tipo de dato
    st.subheader("📋 Seleccionar Tipo de Dato a Visualizar")
    
    col_tipo_vista, col_info_vista = st.columns([1, 3])
    
    with col_tipo_vista:
        tipo_vista = st.selectbox(
            "🔍 Ver datos de:",
            ["Carreras", "Profesores"],
            help="Selecciona qué tipo de datos maestros quieres visualizar"
        )
    
    with col_info_vista:
        if tipo_vista == "Carreras":
            st.info("💡 **Estado Actual**: Datos de carga inicial. **Después de replicar** verás la misma carrera en todas las sedes")
        else:
            st.info("💡 **Estado Actual**: Datos de carga inicial. **Después de replicar** verás el mismo profesor en todas las sedes")
    
    # Botón para refrescar
    if st.button("🔄 Refrescar Datos", type="secondary"):
        st.rerun()
    
    st.subheader(f"📊 Estado Actual de {tipo_vista}")
    
    col1, col2, col3 = st.columns(3)
    
    if tipo_vista == "Carreras":
        # Mostrar carreras
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
    
    else:  # tipo_vista == "Profesores"
        # Mostrar profesores
        with col1:
            st.markdown("### 🏛️ Central (Master)")
            with get_db_connection('central') as db:
                if db:
                    query = """
                    SELECT p.id_profesor, p.nombre as profesor, p.email, s.nombre as sede
                    FROM profesor p
                    JOIN sede s ON p.id_sede = s.id_sede
                    ORDER BY p.id_profesor ASC
                    """
                    df_central = db.get_dataframe(query)
                    if df_central is not None and not df_central.empty:
                        st.dataframe(df_central, use_container_width=True, hide_index=True)
                        st.success(f"✅ {len(df_central)} profesores (Master - Todos)")
                    else:
                        st.warning("No hay profesores en Central")
        
        with col2:
            st.markdown("### 🏢 San Carlos (Slave)")
            with get_db_connection('sancarlos') as db:
                if db:
                    query = """
                    SELECT p.id_profesor, p.nombre as profesor, p.email, s.nombre as sede
                    FROM profesor p
                    JOIN sede s ON p.id_sede = s.id_sede
                    ORDER BY p.id_profesor ASC
                    """
                    df_sc = db.get_dataframe(query)
                    if df_sc is not None and not df_sc.empty:
                        st.dataframe(df_sc, use_container_width=True, hide_index=True)
                        st.success(f"✅ {len(df_sc)} profesores (Datos iniciales)")
                    else:
                        st.warning("No hay profesores en San Carlos")
        
        with col3:
            st.markdown("### 🏫 Heredia (Slave)")
            with get_db_connection('heredia') as db:
                if db:
                    query = """
                    SELECT p.id_profesor, p.nombre as profesor, p.email, s.nombre as sede
                    FROM profesor p
                    JOIN sede s ON p.id_sede = s.id_sede
                    ORDER BY p.id_profesor ASC
                    """
                    df_hd = db.get_dataframe(query)
                    if df_hd is not None and not df_hd.empty:
                        st.dataframe(df_hd, use_container_width=True, hide_index=True)
                        st.success(f"✅ {len(df_hd)} profesores (Datos iniciales)")
                    else:
                        st.warning("No hay profesores en Heredia")
    
    st.markdown("---")
    
    # SECCIÓN 2: Ejecutar nueva replicación
    st.subheader("🚀 Ejecutar Nueva Replicación")
    
    st.markdown("""
    **¿Qué hace esto?** Insertarás un nuevo registro en Central y verás cómo se replica 
    automáticamente a **TODAS** las sedes regionales (San Carlos Y Heredia).
    
    **📋 Resultado esperado:** El nuevo registro aparecerá en las **3 tablas de arriba**.
    """)
    
    # Selección del tipo de dato a replicar
    col_tipo, col_datos = st.columns([1, 2])
    
    with col_tipo:
        tipo_replicacion = st.selectbox(
            "🎯 Tipo de dato a replicar:",
            ["Carrera", "Profesor"],
            help="Datos maestros que se replican desde Central hacia todas las sedes regionales"
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
            
            salario_item = st.number_input(
                "💰 Salario mensual:", 
                min_value=100000, 
                max_value=5000000, 
                value=800000, 
                step=50000,
                help="Salario mensual en colones."
            )
    
    # Botones de acción
    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
    
    with col_btn1:
        ejecutar_replicacion = st.button(
            f"🚀 Ejecutar Replicación de {tipo_replicacion}", 
            type="primary",
            help=f"Insertará el {tipo_replicacion.lower()} en Central y lo replicará a TODAS las sedes"
        )
    
    with col_btn2:
        if st.button("🔄 Refrescar", type="secondary"):
            st.rerun()
    
    #with col_btn3:
        
    
    # Ejecutar replicación cuando se presiona el botón
    if ejecutar_replicacion:
        # Validar datos según el tipo
        datos_validos = False
        mensaje_error = ""
        
        if tipo_replicacion == "Carrera" and nombre_item:
            datos_validos = True
        elif tipo_replicacion == "Profesor" and nombre_item and email_item and salario_item and salario_item > 0:
            datos_validos = True
        else:
            if tipo_replicacion == "Profesor":
                mensaje_error = "Por favor completa todos los campos para Profesor (nombre, email y salario válido)"
            else:
                mensaje_error = f"Por favor completa todos los campos para {tipo_replicacion}"
        
        if datos_validos:
            # Contenedores para mostrar progreso
            st.markdown("### 📈 Progreso de Replicación")
            progress_bar = st.progress(0)
            
            st.markdown("### 📝 Estado de la Operación")
            status_container = st.container()
            
            # Ejecutar replicación según el tipo
            if tipo_replicacion == "Carrera":
                success = execute_master_slave_replication(
                    nombre_carrera=nombre_item,
                    sede_destino=sede_item,
                    progress_bar=progress_bar,
                    status_container=status_container
                )
            else:
                success = execute_profesor_replication(
                    nombre_profesor=nombre_item,
                    email_profesor=email_item,
                    sede_profesor=sede_item,
                    salario=salario_item,
                    progress_bar=progress_bar,
                    status_container=status_container
                )
            
            if success:
                st.balloons()
                if tipo_replicacion == "Profesor":
                    st.success(f"🎉 ¡Profesor replicado exitosamente y salario registrado en planilla!")
                else:
                    st.success(f"🎉 ¡{tipo_replicacion} replicado exitosamente!")
                
                # Mensaje explicativo específico
                if tipo_replicacion == "Carrera":
                    st.info(
                        f"✅ **¿Qué pasó?** Se insertó la carrera '{nombre_item}' en la base de datos Central "
                        f"y se replicó automáticamente a **TODAS** las sedes (San Carlos Y Heredia). "
                        f"Cambia a vista 'Carreras' y presiona '👀 Ver Resultados' para ver la carrera en las **3 tablas**."
                    )
                else:  # Profesor
                    st.info(
                        f"✅ **¿Qué pasó?** Se insertó el profesor '{nombre_item}' en la base de datos Central "
                        f"y se replicó automáticamente a **TODAS** las sedes (San Carlos Y Heredia). "
                        f"Además, se registró su salario (₡{salario_item:,}) en la planilla de Central. "
                        f"Cambia a vista 'Profesores' y presiona '👀 Ver Resultados' para ver el profesor en las **3 tablas**."
                    )
        else:
            st.error(mensaje_error)

    if st.button("📋 Ver Logs", type="secondary"):
            with st.expander("📋 Logs de Replicaciones", expanded=True):
                mostrar_logs_replicacion()

with tab2:
    st.header("🔄 Sincronización Bidireccional")

    st.markdown("### 📊 Estado Actual de Estudiantes por Sede")

    # Tabs para mostrar datos de cada sede
    tab_central, tab_sc, tab_hd = st.tabs(["🏛️ Central", "🏢 San Carlos", "🏫 Heredia"])

    def get_students_by_sede(sede_key):
        """Obtiene estudiantes ACTIVOS de una sede específica"""
        with get_db_connection(sede_key) as db:
            if db:
                # Estudiantes activos en esta sede
                query = """
                SELECT e.id_estudiante, e.nombre, e.email, 
                    COALESCE(e.estado, 'activo') as estado,
                    COUNT(m.id_matricula) as materias_activas,
                    COALESCE(AVG(n.nota), 0) as promedio
                FROM estudiante e
                LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
                LEFT JOIN nota n ON m.id_matricula = n.id_matricula
                WHERE COALESCE(e.estado, 'activo') = 'activo' 
                OR e.estado IS NULL
                GROUP BY e.id_estudiante, e.nombre, e.email, e.estado
                ORDER BY e.nombre
                """
                return db.get_dataframe(query)
        return pd.DataFrame()
    
    with tab_central:
        st.markdown("**👥 Estudiantes en Central**")
        estudiantes_central = get_students_by_sede('central')
        if not estudiantes_central.empty:
            st.dataframe(estudiantes_central, use_container_width=True, hide_index=True)
            st.info(f"📊 Total estudiantes: {len(estudiantes_central)}")
        else:
            st.info("No hay estudiantes en Central")

    with tab_sc:
        st.markdown("**👥 Estudiantes en San Carlos**")
        estudiantes_sc = get_students_by_sede('sancarlos')
        if not estudiantes_sc.empty:
            st.dataframe(estudiantes_sc, use_container_width=True, hide_index=True)
            st.info(f"📊 Total estudiantes: {len(estudiantes_sc)}")
        else:
            st.info("No hay estudiantes en San Carlos")

    with tab_hd:
        st.markdown("**👥 Estudiantes en Heredia**")
        estudiantes_hd = get_students_by_sede('heredia')
        if not estudiantes_hd.empty:
            st.dataframe(estudiantes_hd, use_container_width=True, hide_index=True)
            st.info(f"📊 Total estudiantes: {len(estudiantes_hd)}")
        else:
            st.info("No hay estudiantes en Heredia")

    # Botón para refrescar datos
    if st.button("🔄 Actualizar Datos", key="refresh_students"):
        st.rerun()

    st.divider()
    
    st.markdown("""
    ### 👥 Transferencia de Estudiantes
    
    A diferencia de la replicación Master-Slave, las transferencias son **bidireccionales**: 
    los estudiantes pueden moverse entre cualquier sede.
    """)
    
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📤 Sede Origen")
        sede_origen = st.selectbox("Sede origen:", ["Central", "San Carlos", "Heredia"], key="transfer_origen")
        
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
                WHERE (e.email NOT LIKE '%TRANSFERIDO%' OR e.email IS NULL)
                AND (COALESCE(e.estado, 'activo') = 'activo' OR e.estado IS NULL)
                GROUP BY e.id_estudiante, e.nombre, e.email
                ORDER BY e.nombre
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
        sedes_destino = ["Central", "San Carlos", "Heredia"]
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
                
                success, new_student_id = execute_real_transfer(
                    estudiante_data, sede_origen, sede_destino, 
                    progress_bar, status_container
                )
                
                if success:
                    st.balloons()
                    st.success("✅ Transferencia completada: Estudiante movido exitosamente")
                    
                    st.markdown("### 🔍 Verificación de Transferencia")
                    
                    col1, col2 = st.columns(2)
                    
                    # Obtener las claves de conexión
                    from_key = sede_origen.lower().replace(' ', '')
                    to_key = sede_destino.lower().replace(' ', '')
                    
                    with col1:
                        st.markdown(f"**📍 {sede_origen} (Origen)**")
                        with get_db_connection(from_key) as db:
                            if db:
                                check_query = """
                                SELECT COUNT(*) as count, 
                                    SUM(CASE WHEN estado = 'transferido' THEN 1 ELSE 0 END) as transferidos
                                FROM estudiante 
                                WHERE nombre = %s
                                """
                                result = db.get_dataframe(check_query, (estudiante_data['nombre'],))
                                if not result.empty:
                                    total = result.iloc[0]['count']
                                    transferidos = result.iloc[0]['transferidos'] or 0
                                    
                                    if transferidos > 0:
                                        st.success(f"✅ Estudiante marcado como transferido ({transferidos}/{total})")
                                    else:
                                        st.warning("⚠️ Estudiante no marcado como transferido")
                                else:
                                    st.error("❌ Error al verificar estado")

                    with col2:
                        st.markdown(f"**🎯 {sede_destino} (Destino)**")
                        with get_db_connection(to_key) as db:
                            if db:
                                check_query = """
                                SELECT COUNT(*) as count,
                                    SUM(CASE WHEN estado = 'activo' THEN 1 ELSE 0 END) as activos
                                FROM estudiante 
                                WHERE nombre = %s
                                """
                                result = db.get_dataframe(check_query, (estudiante_data['nombre'],))
                                if not result.empty:
                                    total = result.iloc[0]['count']
                                    activos = result.iloc[0]['activos'] or 0
                                    
                                    if activos > 0:
                                        st.success(f"✅ Estudiante activo en destino ({activos}/{total})")
                                    else:
                                        st.error("❌ Estudiante no encontrado en destino")
                                else:
                                    st.error("❌ Error al verificar estado")
                    
                    # Mostrar detalles de la transferencia
                    if new_student_id:
                        st.markdown("### 📊 Detalles de la Transferencia Lógica")
                        
                        audit_details = {
                            'ID Original': estudiante_data['id_estudiante'],
                            'ID Nuevo': new_student_id,
                            'Estudiante': estudiante_data['nombre'],
                            'Email': estudiante_data['email'],  # Email SIN modificar
                            'Desde': sede_origen,
                            'Hacia': sede_destino,
                            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'Operación': 'UPDATE (origen) + INSERT (destino)',
                            'Tipo': 'Transferencia Lógica',
                            'Estado': '✅ Completada'
                        }
                        st.json(audit_details)
                    
                    # Botón para actualizar vista
                    if st.button("🔄 Actualizar Vista de Estudiantes", key="refresh_after_transfer"):
                        st.rerun()

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
    
    **💡 Después de replicar:** Todas las sedes tendrán todos los datos maestros
    """)

with col2:
    if st.checkbox("🔄 Auto-actualizar cada 30s"):
        time.sleep(30)
        st.rerun()