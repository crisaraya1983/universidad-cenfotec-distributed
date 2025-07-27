"""
Página de demostración de Replicación
Esta página muestra cómo funcionan los procesos de replicación Master-Slave
y sincronización bidireccional en el sistema distribuido.
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
from utils.db_connections import get_db_connection, get_redis_connection

# Configuración de la página
st.set_page_config(
    page_title="Replicación - Sistema Cenfotec",
    page_icon="🔄",
    layout="wide"
)

# Título de la página
st.title("🔄 Demostración de Replicación de Datos")

# Introducción
st.markdown("""
La **replicación** es el proceso de mantener copias de datos en múltiples nodos para garantizar
disponibilidad, rendimiento y tolerancia a fallos. En nuestro sistema, implementamos:

- **Replicación Master-Slave**: Datos maestros desde Central hacia sedes regionales
- **Sincronización Bidireccional**: Para operaciones que afectan múltiples sedes
""")

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Conceptos",
    "🎯 Master-Slave",
    "🔄 Sincronización",
    "📊 Monitoreo"
])

with tab1:
    st.header("Conceptos de Replicación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Tipos de Replicación
        
        **1. Replicación Síncrona**
        - Actualización inmediata en todos los nodos
        - Mayor consistencia
        - Mayor latencia
        - Usado para datos críticos
        
        **2. Replicación Asíncrona**
        - Actualización diferida
        - Mejor rendimiento
        - Eventual consistencia
        - Usado para datos no críticos
        """)
        
        # Diagrama de replicación
        fig = go.Figure()
        
        # Nodo Master
        fig.add_trace(go.Scatter(
            x=[2], y=[2],
            mode='markers+text',
            marker=dict(size=60, color=COLORS['primary'], symbol='star'),
            text=['MASTER<br>(Central)'],
            textposition="top center",
            name='Master'
        ))
        
        # Nodos Slave
        fig.add_trace(go.Scatter(
            x=[0, 4], y=[0, 0],
            mode='markers+text',
            marker=dict(size=50, color=COLORS['secondary'], symbol='circle'),
            text=['SLAVE<br>(San Carlos)', 'SLAVE<br>(Heredia)'],
            textposition="bottom center",
            name='Slaves'
        ))
        
        # Flechas de replicación
        fig.add_annotation(x=0, y=0, ax=2, ay=2,
                          xref="x", yref="y", axref="x", ayref="y",
                          arrowhead=2, arrowsize=1, arrowwidth=2,
                          arrowcolor=COLORS['info'])
        
        fig.add_annotation(x=4, y=0, ax=2, ay=2,
                          xref="x", yref="y", axref="x", ayref="y",
                          arrowhead=2, arrowsize=1, arrowwidth=2,
                          arrowcolor=COLORS['info'])
        
        fig.update_layout(
            title="Arquitectura Master-Slave",
            showlegend=True,
            height=300,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 5]),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 3])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        ### 🔧 Implementación en Cenfotec
        
        **Datos Replicados (Master → Slaves):**
        - ✅ Catálogo de Carreras
        - ✅ Información de Profesores
        - ✅ Configuraciones del Sistema
        - ✅ Catálogo de Sedes
        
        **Datos NO Replicados:**
        - ❌ Estudiantes (fragmentación horizontal)
        - ❌ Matrículas (datos locales)
        - ❌ Planillas (solo en Central)
        - ❌ Pagos (datos locales)
        """)
        
        # Estado de replicación
        st.markdown("### 📊 Estado Actual")
        
        # Simular estado de replicación
        replication_status = {
            'San Carlos': {
                'estado': 'Sincronizado',
                'ultimo_sync': datetime.now() - timedelta(minutes=5),
                'lag': '0.5s',
                'color': COLORS['success']
            },
            'Heredia': {
                'estado': 'Sincronizado',
                'ultimo_sync': datetime.now() - timedelta(minutes=3),
                'lag': '0.3s',
                'color': COLORS['success']
            }
        }
        
        for sede, status in replication_status.items():
            st.markdown(f"**{sede}**: <span style='color: {status['color']}'>{status['estado']}</span> "
                       f"(lag: {status['lag']})", unsafe_allow_html=True)

with tab2:
    st.header("🎯 Replicación Master-Slave")
    
    st.markdown("""
    En esta sección puedes ver y probar cómo los datos maestros se replican desde
    la sede Central hacia las sedes regionales.
    """)
    
    # Verificar datos maestros
    st.subheader("📊 Verificación de Datos Maestros")
    
    # Comparar carreras entre sedes
    col1, col2, col3 = st.columns(3)
    
    carreras_por_sede = {}
    
    with col1:
        st.markdown("### 🏛️ Central (Master)")
        with get_db_connection('central') as db:
            if db:
                query = """
                SELECT c.nombre as carrera, s.nombre as sede
                FROM carrera c
                JOIN sede s ON c.id_sede = s.id_sede
                ORDER BY s.nombre, c.nombre
                """
                df_central = db.get_dataframe(query)
                if df_central is not None:
                    carreras_por_sede['central'] = df_central
                    st.dataframe(df_central, use_container_width=True, hide_index=True)
                    st.success(f"✅ {len(df_central)} carreras")
    
    with col2:
        st.markdown("### 🏢 San Carlos (Slave)")
        with get_db_connection('sancarlos') as db:
            if db:
                query = """
                SELECT c.nombre as carrera, s.nombre as sede
                FROM carrera c
                JOIN sede s ON c.id_sede = s.id_sede
                WHERE s.id_sede = 2
                ORDER BY c.nombre
                """
                df_sc = db.get_dataframe(query)
                if df_sc is not None:
                    carreras_por_sede['sancarlos'] = df_sc
                    st.dataframe(df_sc, use_container_width=True, hide_index=True)
                    st.success(f"✅ {len(df_sc)} carreras")
    
    with col3:
        st.markdown("### 🏫 Heredia (Slave)")
        with get_db_connection('heredia') as db:
            if db:
                query = """
                SELECT c.nombre as carrera, s.nombre as sede
                FROM carrera c
                JOIN sede s ON c.id_sede = s.id_sede
                WHERE s.id_sede = 3
                ORDER BY c.nombre
                """
                df_hd = db.get_dataframe(query)
                if df_hd is not None:
                    carreras_por_sede['heredia'] = df_hd
                    st.dataframe(df_hd, use_container_width=True, hide_index=True)
                    st.success(f"✅ {len(df_hd)} carreras")
    
    # Simulación de replicación
    st.subheader("🚀 Simulación de Replicación")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        Puedes simular el proceso de replicación agregando una nueva carrera en Central
        y viendo cómo se propaga a las sedes regionales.
        """)
        
        with st.form("nueva_carrera_form"):
            st.markdown("**Agregar Nueva Carrera (en Central)**")
            
            nombre_carrera = st.text_input("Nombre de la carrera:")
            sede_carrera = st.selectbox("Sede donde se impartirá:", 
                                       ["Central", "San Carlos", "Heredia"])
            
            sede_map = {"Central": 1, "San Carlos": 2, "Heredia": 3}
            
            if st.form_submit_button("➕ Agregar Carrera", type="primary"):
                if nombre_carrera:
                    # Simular inserción en Central
                    with st.spinner("Insertando en sede Central..."):
                        time.sleep(1)  # Simular latencia
                        
                        # Aquí normalmente harías el INSERT real
                        st.success(f"✅ Carrera '{nombre_carrera}' agregada en Central")
                    
                    # Simular propagación
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i in range(101):
                        progress_bar.progress(i)
                        if i < 30:
                            status_text.text(f"📤 Preparando replicación... {i}%")
                        elif i < 60:
                            status_text.text(f"🔄 Replicando a San Carlos... {i}%")
                        elif i < 90:
                            status_text.text(f"🔄 Replicando a Heredia... {i}%")
                        else:
                            status_text.text(f"✅ Replicación completada... {i}%")
                        time.sleep(0.02)
                    
                    st.balloons()
                    st.success(MESSAGES['replication_success'])
                else:
                    st.error("Por favor ingresa un nombre de carrera")
    
    with col2:
        st.markdown("### 📈 Métricas de Replicación")
        
        # Métricas simuladas
        st.metric("Lag Promedio", "0.4s", "-0.1s")
        st.metric("Transacciones/seg", "127", "+12")
        st.metric("Cola de Replicación", "0", "0")
        
        # Gráfico de rendimiento
        time_data = pd.DataFrame({
            'Tiempo': pd.date_range(start='2025-01-24 12:00', periods=20, freq='min'),
            'Transacciones': [120, 125, 130, 127, 135, 140, 138, 142, 145, 150,
                            148, 152, 155, 160, 158, 162, 165, 170, 168, 172]
        })
        
        fig = px.line(time_data, x='Tiempo', y='Transacciones',
                     title='Rendimiento de Replicación')
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("👥 Transferencia de Estudiante")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📤 Sede Origen")
        sede_origen = st.selectbox("Sede origen:", ["San Carlos", "Heredia"], key="transfer_origen")
        
        # Obtener estudiantes REALES de la sede
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
                GROUP BY e.id_estudiante, e.nombre, e.email
                LIMIT 5
                """
                result = db.execute_query(query)
                if result:
                    estudiantes_reales = result

        if estudiantes_reales:
            estudiante_options = [(f"{est['nombre']} ({est['materias_activas']} materias)", est) for est in estudiantes_reales]
            estudiante_sel = st.selectbox("Estudiante:", estudiante_options, format_func=lambda x: x[0])
            estudiante_data = estudiante_sel[1]
            
            # Mostrar información del estudiante
            st.info(f"""
            **Estudiante:** {estudiante_data['nombre']}
            **Email:** {estudiante_data['email']}
            **Materias activas:** {estudiante_data['materias_activas']}
            **Promedio:** {estudiante_data['promedio']:.1f}
            """)

    with col2:
        st.markdown("### 📥 Sede Destino")
        sede_destino = st.selectbox("Sede destino:", 
                                ["Heredia" if sede_origen == "San Carlos" else "San Carlos"],
                                key="transfer_destino")
        
        st.markdown("**Proceso de Transferencia:**")
        st.markdown("""
        1. ✅ Verificar datos del estudiante
        2. ✅ Crear registro en sede destino  
        3. ✅ Transferir matrículas activas
        4. ✅ Migrar historial académico
        5. ✅ Actualizar referencias en pagarés
        6. ✅ Marcar como transferido en origen
        """)

    # Botón de transferencia mejorado
    if st.button("🚀 Ejecutar Transferencia Completa", type="primary", use_container_width=True):
        if 'estudiante_data' in locals():
            # Simulación realista paso a paso
            progress = st.progress(0)
            status_container = st.container()
            
            steps = [
                ("🔍 Verificando estudiante en origen...", 0.15),
                ("📋 Copiando datos personales...", 0.30),
                ("📚 Transfiriendo matrículas activas...", 0.50),  
                ("📊 Migrando historial académico...", 0.65),
                ("💰 Actualizando referencias financieras...", 0.80),
                ("🔄 Sincronizando entre sedes...", 0.95),
                ("✅ Transferencia completada", 1.0)
            ]
            
            for step_text, progress_val in steps:
                with status_container:
                    st.info(step_text)
                progress.progress(progress_val)
                time.sleep(1)
            
            st.success(f"✅ {estudiante_data['nombre']} transferido exitosamente de {sede_origen} a {sede_destino}")
            
            # Mostrar tabla de cambios
            cambios = pd.DataFrame({
                'Campo': ['Sede', 'Estado', 'ID Sede', 'Fecha Transferencia'],
                'Antes': [sede_origen, 'Activo', '2' if sede_origen == 'San Carlos' else '3', '-'],
                'Después': [sede_destino, 'Transferido', '3' if sede_destino == 'Heredia' else '2', datetime.now().strftime('%Y-%m-%d')]
            })
            st.table(cambios.set_index('Campo'))
    
    with col2:
        st.markdown("### 📥 Sede Destino")
        
        sede_destino = st.selectbox("Seleccionar sede destino:",
                                   ["Heredia" if sede_origen == "San Carlos" else "San Carlos"],
                                   key="sede_destino")
        
        st.info(f"""
        **Proceso de Transferencia:**
        1. Verificar datos del estudiante
        2. Crear registro en sede destino
        3. Transferir matrículas activas
        4. Marcar como inactivo en origen
        5. Sincronizar cambios
        """)
    
    # Botón de transferencia
    if st.button("🔄 Iniciar Transferencia", type="primary", use_container_width=True):
        # Simulación del proceso
        placeholder = st.empty()
        
        steps = [
            ("🔍 Verificando datos del estudiante...", 1),
            ("📋 Copiando información personal...", 1.5),
            ("📚 Transfiriendo matrículas activas...", 2),
            ("💰 Actualizando registros de pagos...", 1),
            ("🔄 Sincronizando con sede destino...", 1.5),
            ("✅ Transferencia completada", 0.5)
        ]
        
        progress_bar = st.progress(0)
        
        for i, (step, duration) in enumerate(steps):
            placeholder.info(step)
            progress_bar.progress((i + 1) / len(steps))
            time.sleep(duration)
        
        placeholder.success("✅ Estudiante transferido exitosamente")
        
        # Mostrar resumen
        st.markdown("### 📊 Resumen de la Transferencia")
        
        transfer_summary = {
            'Detalle': ['Estudiante', 'Sede Origen', 'Sede Destino', 
                       'Matrículas Transferidas', 'Fecha'],
            'Valor': [estudiante_selected[0] if 'estudiante_selected' in locals() else 'Demo Student',
                     sede_origen, sede_destino, '3', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        }
        
        df_summary = pd.DataFrame(transfer_summary)
        st.table(df_summary.set_index('Detalle'))
    
    # Historial de sincronizaciones
    st.subheader("📜 Historial de Sincronizaciones")
    
    # Datos simulados de sincronizaciones
    sync_history = pd.DataFrame({
        'Fecha': [datetime.now() - timedelta(hours=i) for i in range(5)],
        'Tipo': ['Transferencia', 'Actualización', 'Transferencia', 'Replicación', 'Actualización'],
        'Origen': ['San Carlos', 'Central', 'Heredia', 'Central', 'San Carlos'],
        'Destino': ['Heredia', 'Todas', 'San Carlos', 'Todas', 'Central'],
        'Estado': ['✅ Exitoso', '✅ Exitoso', '✅ Exitoso', '⚠️ Con advertencias', '✅ Exitoso'],
        'Registros': [1, 15, 1, 45, 8]
    })
    
    st.dataframe(sync_history, use_container_width=True, hide_index=True)

with tab4:
    st.header("📊 Monitoreo de Replicación")
    
    st.markdown("""
    Panel de monitoreo en tiempo real del estado de replicación y sincronización
    entre todas las sedes del sistema.
    """)
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🟢 Sedes Activas", "3/3", "100%")
    
    with col2:
        st.metric("📊 Lag Promedio", "0.45s", "-0.05s")
    
    with col3:
        st.metric("🔄 Sync Rate", "98.5%", "+1.2%")
    
    with col4:
        st.metric("⚡ TPS", "142", "+15")
    
    # Gráficos de monitoreo
    st.subheader("📈 Métricas en Tiempo Real")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de lag por sede
        lag_data = pd.DataFrame({
            'Sede': ['San Carlos', 'Heredia'],
            'Lag (ms)': [450, 320]
        })
        
        fig_lag = px.bar(lag_data, x='Sede', y='Lag (ms)',
                        title='Latencia de Replicación por Sede',
                        color='Sede',
                        color_discrete_map={'San Carlos': COLORS['secondary'],
                                          'Heredia': COLORS['success']})
        fig_lag.add_hline(y=1000, line_dash="dash", 
                         annotation_text="Límite aceptable (1s)")
        fig_lag.update_layout(height=350)
        st.plotly_chart(fig_lag, use_container_width=True)
    
    with col2:
        # Gráfico de transacciones
        time_range = pd.date_range(start='2025-01-24 12:00', periods=30, freq='min')
        trans_data = pd.DataFrame({
            'Tiempo': time_range,
            'Central': [100 + i*2 + (i%5)*3 for i in range(30)],
            'San Carlos': [80 + i*1.5 + (i%3)*2 for i in range(30)],
            'Heredia': [70 + i*1.2 + (i%4)*2 for i in range(30)]
        })
        
        fig_trans = px.line(trans_data, x='Tiempo', 
                           y=['Central', 'San Carlos', 'Heredia'],
                           title='Transacciones por Minuto',
                           color_discrete_map={'Central': COLORS['primary'],
                                             'San Carlos': COLORS['secondary'],
                                             'Heredia': COLORS['success']})
        fig_trans.update_layout(height=350, yaxis_title='TPS')
        st.plotly_chart(fig_trans, use_container_width=True)
    
    # Estado detallado por sede
    st.subheader("🔍 Estado Detallado por Sede")
    
    tabs_sedes = st.tabs(["🏛️ Central", "🏢 San Carlos", "🏫 Heredia"])
    
    for idx, (sede_key, tab) in enumerate(zip(['central', 'sancarlos', 'heredia'], tabs_sedes)):
        with tab:
            sede_info = get_sede_info(sede_key)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**{sede_info['description']}**")
                
                # Verificar conexión y mostrar información
                with get_db_connection(sede_key) as db:
                    if db and db.connection.is_connected():
                        st.success("✅ Conexión activa")
                        
                        # Información de la base de datos
                        query = """
                        SELECT 
                            table_name,
                            table_rows,
                            ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
                        FROM information_schema.tables
                        WHERE table_schema = %s
                        ORDER BY table_rows DESC
                        """
                        df_tables = db.get_dataframe(query, (db.config['database'],))
                        
                        if df_tables is not None and not df_tables.empty:
                            st.markdown("**Tablas y tamaños:**")
                            st.dataframe(df_tables, use_container_width=True, hide_index=True)
                    else:
                        st.error("❌ Conexión inactiva")
            
            with col2:
                # Métricas específicas de la sede
                if sede_key == 'central':
                    st.metric("Rol", "MASTER", None)
                    st.metric("Slaves conectados", "2", None)
                    st.metric("Binlog activo", "Sí", None)
                else:
                    st.metric("Rol", "SLAVE", None)
                    st.metric("Master", "Central", None)
                    st.metric("Delay", f"{450 if sede_key == 'sancarlos' else 320}ms", None)
    
    # Log de eventos
    st.subheader("📜 Log de Eventos Recientes")
    
    # Simular log de eventos
    events = []
    for i in range(10):
        timestamp = datetime.now() - timedelta(minutes=i*5)
        event_types = ['Replicación', 'Sincronización', 'Conexión', 'Error', 'Advertencia']
        event_type = event_types[i % len(event_types)]
        
        if event_type == 'Error':
            level = '❌ ERROR'
            message = f"Fallo en replicación a {'San Carlos' if i%2 else 'Heredia'}"
        elif event_type == 'Advertencia':
            level = '⚠️ WARN'
            message = f"Lag elevado detectado: {800+i*50}ms"
        else:
            level = '✅ INFO'
            message = f"{event_type} completada exitosamente"
        
        events.append({
            'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Nivel': level,
            'Evento': event_type,
            'Mensaje': message
        })
    
    df_events = pd.DataFrame(events)
    st.dataframe(df_events, use_container_width=True, hide_index=True)

# Sidebar con información y controles
with st.sidebar:
    st.markdown("### 🔄 Control de Replicación")
    
    # Controles simulados
    st.markdown("**Estado del Sistema**")
    replication_enabled = st.toggle("Replicación Activa", value=True)
    
    if replication_enabled:
        st.success("✅ Replicación activa")
    else:
        st.warning("⚠️ Replicación pausada")
    
    st.markdown("---")
    
    # Cache Redis
    st.markdown("### 💾 Cache Redis")
    
    redis_conn = get_redis_connection()
    if redis_conn and redis_conn.redis_client:
        try:
            # Simular estadísticas de cache
            st.metric("Entradas en cache", "1,247", "+45")
            st.metric("Hit Rate", "87.3%", "+2.1%")
            
            if st.button("🗑️ Limpiar Cache", use_container_width=True):
                st.info("Cache limpiado")
                time.sleep(1)
                st.rerun()
        except:
            st.error("Redis no disponible")
    
    st.markdown("---")
    
    # Información educativa
    st.markdown("### 📚 Conceptos Clave")
    
    with st.expander("Binary Log"):
        st.markdown("""
        El **binary log** registra todos los cambios en la base de datos
        para permitir la replicación a otros servidores.
        """)
    
    with st.expander("Lag de Replicación"):
        st.markdown("""
        El **lag** es el tiempo de retraso entre un cambio en el master
        y su aplicación en los slaves. Menor es mejor.
        """)
    
    with st.expander("Consistencia Eventual"):
        st.markdown("""
        Garantiza que todos los nodos tendrán los mismos datos
        **eventualmente**, aunque no inmediatamente.
        """)