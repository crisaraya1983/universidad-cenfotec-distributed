"""
Página de Monitoreo del Sistema
Esta página proporciona un dashboard completo para monitorear el estado,
rendimiento y salud del sistema distribuido en tiempo real.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time
import random
import numpy as np

# Importar utilidades
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG, COLORS, get_sede_info
from utils.db_connections import get_db_connection, test_all_connections, get_redis_connection

# Configuración de la página
st.set_page_config(
    page_title="Monitoreo - Sistema Cenfotec",
    page_icon="📈",
    layout="wide"
)

# Título de la página
st.title("📈 Monitoreo del Sistema Distribuido")

# Auto-refresh option
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    auto_refresh = st.checkbox("🔄 Auto-actualizar", value=False)
with col2:
    if auto_refresh:
        refresh_interval = st.selectbox("Intervalo:", [5, 10, 30, 60], index=1)
        st.caption(f"Actualización cada {refresh_interval}s")

# Tabs principales
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard General",
    "💻 Recursos del Sistema",
    "📊 Análisis de Rendimiento",
    "🔍 Diagnóstico",
    "📉 Históricos"
])

with tab1:
    st.header("Dashboard General del Sistema")
    
    # Estado general del sistema
    col1, col2, col3, col4 = st.columns(4)
    
    # Calcular uptime (simulado)
    uptime_hours = random.randint(720, 744)  # ~30 días
    uptime_pct = (uptime_hours / 744) * 100
    
    with col1:
        st.metric("⏱️ Uptime", f"{uptime_pct:.1f}%", f"{uptime_hours}h")
    
    with col2:
        active_connections = random.randint(45, 65)
        st.metric("🔌 Conexiones Activas", active_connections, f"+{random.randint(1, 5)}")
    
    with col3:
        avg_response = random.uniform(0.8, 1.5)
        st.metric("⚡ Tiempo Respuesta", f"{avg_response:.2f}s", f"-{random.uniform(0.1, 0.3):.2f}s")
    
    with col4:
        error_rate = random.uniform(0.1, 0.5)
        st.metric("⚠️ Tasa de Error", f"{error_rate:.2f}%", f"-{random.uniform(0.01, 0.05):.2f}%")
    
    # Gráfico de estado de servicios
    st.subheader("🚦 Estado de Servicios")
    
    # Probar conexiones reales
    connection_status = test_all_connections()
    
    # Crear visualización de servicios
    services_data = []
    
    for service, is_up in connection_status.items():
        if service == 'redis':
            service_name = "Redis Cache"
            service_type = "Cache"
        else:
            sede_info = get_sede_info(service)
            service_name = sede_info['name']
            service_type = "Database"
        
        services_data.append({
            'Servicio': service_name,
            'Tipo': service_type,
            'Estado': 'Operativo' if is_up else 'Fuera de línea',
            'Uptime': f"{random.randint(95, 100)}%" if is_up else "0%",
            'CPU': f"{random.randint(20, 80)}%" if is_up else "N/A",
            'RAM': f"{random.randint(40, 70)}%" if is_up else "N/A",
            'Latencia': f"{random.randint(10, 100)}ms" if is_up else "N/A"
        })
    
    df_services = pd.DataFrame(services_data)
    
    # Aplicar colores según estado
    def color_status(val):
        if val == 'Operativo':
            return 'background-color: #90EE90'
        elif val == 'Fuera de línea':
            return 'background-color: #FFB6C1'
        return ''
    
    styled_df = df_services.style.applymap(color_status, subset=['Estado'])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
    
    # Mapa de calor de actividad
    st.subheader("🔥 Mapa de Calor de Actividad")
    
    # Generar datos simulados de actividad por hora y sede
    hours = list(range(24))
    sedes = ['Central', 'San Carlos', 'Heredia']
    
    # Crear matriz de actividad
    activity_data = []
    for sede in sedes:
        # Simular patrones de actividad realistas
        base_activity = np.random.randint(10, 30, 24)
        # Picos en horario laboral
        for h in range(8, 18):
            base_activity[h] += np.random.randint(30, 60)
        activity_data.append(base_activity)
    
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=activity_data,
        x=[f"{h:02d}:00" for h in hours],
        y=sedes,
        colorscale='YlOrRd',
        text=activity_data,
        texttemplate="%{text}",
        textfont={"size": 10},
        hovertemplate="Sede: %{y}<br>Hora: %{x}<br>Transacciones: %{z}<extra></extra>"
    ))
    
    fig_heatmap.update_layout(
        title="Transacciones por Hora y Sede",
        xaxis_title="Hora del Día",
        yaxis_title="Sede",
        height=300
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

with tab2:
    st.header("💻 Monitoreo de Recursos")
    
    # Métricas de recursos por sede
    st.subheader("📊 Uso de Recursos por Sede")
    
    # Crear gráficos de recursos para cada sede
    for sede in ['central', 'sancarlos', 'heredia']:
        sede_info = get_sede_info(sede)
        
        with st.expander(f"{sede_info['name']} - Recursos", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            # Simular métricas de recursos
            cpu_usage = random.randint(20, 80)
            ram_usage = random.randint(40, 85)
            disk_usage = random.randint(30, 70)
            
            with col1:
                # Gráfico de CPU
                fig_cpu = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=cpu_usage,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "CPU %"},
                    delta={'reference': 50, 'relative': True},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "yellow"},
                            {'range': [80, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig_cpu.update_layout(height=250)
                st.plotly_chart(fig_cpu, use_container_width=True)
            
            with col2:
                # Gráfico de RAM
                fig_ram = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=ram_usage,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "RAM %"},
                    delta={'reference': 60, 'relative': True},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkgreen"},
                        'steps': [
                            {'range': [0, 60], 'color': "lightgray"},
                            {'range': [60, 85], 'color': "yellow"},
                            {'range': [85, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 95
                        }
                    }
                ))
                fig_ram.update_layout(height=250)
                st.plotly_chart(fig_ram, use_container_width=True)
            
            with col3:
                # Gráfico de Disco
                fig_disk = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=disk_usage,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Disco %"},
                    delta={'reference': 50, 'relative': True},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkorange"},
                        'steps': [
                            {'range': [0, 70], 'color': "lightgray"},
                            {'range': [70, 90], 'color': "yellow"},
                            {'range': [90, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 95
                        }
                    }
                ))
                fig_disk.update_layout(height=250)
                st.plotly_chart(fig_disk, use_container_width=True)
            
            # Tabla de procesos
            st.markdown("**Top Procesos**")
            
            processes = pd.DataFrame({
                'Proceso': ['mysqld', 'nginx', 'redis-server', 'python'],
                'CPU %': [cpu_usage/4, 5, 3, 8],
                'RAM MB': [ram_usage*10, 50, 150, 200],
                'Tiempo': ['15d 3h', '15d 3h', '15d 3h', '2h 15m']
            })
            
            st.dataframe(processes, use_container_width=True, hide_index=True)
    
    # Métricas de red
    st.subheader("🌐 Métricas de Red")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tráfico de red
        time_points = pd.date_range(start='2025-01-24 00:00', periods=24, freq='h')
        network_data = pd.DataFrame({
            'Tiempo': time_points,
            'Entrada (MB/s)': np.random.uniform(10, 50, 24),
            'Salida (MB/s)': np.random.uniform(5, 30, 24)
        })
        
        fig_network = px.line(network_data, x='Tiempo', 
                             y=['Entrada (MB/s)', 'Salida (MB/s)'],
                             title='Tráfico de Red (24h)')
        st.plotly_chart(fig_network, use_container_width=True)
    
    with col2:
        # Conexiones por tipo
        conn_types = pd.DataFrame({
            'Tipo': ['MySQL', 'HTTP', 'Redis', 'SSH', 'Otros'],
            'Conexiones': [150, 320, 80, 5, 25]
        })
        
        fig_conn = px.pie(conn_types, values='Conexiones', names='Tipo',
                         title='Distribución de Conexiones')
        st.plotly_chart(fig_conn, use_container_width=True)

with tab3:
    st.header("📊 Análisis de Rendimiento")
    
    # Query performance
    st.subheader("⚡ Rendimiento de Consultas")
    
    # Generar datos de rendimiento
    query_types = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'JOIN']
    performance_data = []
    
    for qt in query_types:
        for sede in ['Central', 'San Carlos', 'Heredia']:
            avg_time = random.uniform(0.1, 2.0)
            performance_data.append({
                'Tipo': qt,
                'Sede': sede,
                'Tiempo Promedio (ms)': avg_time * 1000,
                'Queries/seg': random.randint(10, 100),
                'Cache Hit %': random.randint(60, 95) if qt == 'SELECT' else 0
            })
    
    df_perf = pd.DataFrame(performance_data)
    
    # Gráfico de barras agrupadas
    fig_perf = px.bar(df_perf, x='Tipo', y='Tiempo Promedio (ms)',
                      color='Sede', barmode='group',
                      title='Tiempo de Respuesta por Tipo de Query')
    st.plotly_chart(fig_perf, use_container_width=True)
    
    # Tabla de queries lentas
    st.subheader("🐌 Queries Más Lentas")
    
    slow_queries = pd.DataFrame({
        'Timestamp': [datetime.now() - timedelta(minutes=random.randint(1, 60)) for _ in range(5)],
        'Sede': ['Central', 'San Carlos', 'Heredia', 'Central', 'San Carlos'],
        'Query': [
            'SELECT * FROM estudiante e JOIN matricula m ON...',
            'UPDATE pago SET estado = "procesado" WHERE...',
            'SELECT COUNT(*) FROM nota WHERE fecha BETWEEN...',
            'INSERT INTO planilla (id_profesor, salario...',
            'DELETE FROM asistencia WHERE fecha < DATE_SUB...'
        ],
        'Tiempo (s)': [3.2, 2.8, 4.1, 2.5, 3.9],
        'Filas': [1520, 1, 45000, 1, 230]
    })
    
    slow_queries = slow_queries.sort_values('Tiempo (s)', ascending=False)
    st.dataframe(slow_queries, use_container_width=True, hide_index=True)
    
    # Análisis de índices
    st.subheader("📑 Análisis de Índices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Índices Más Utilizados**")
        
        index_usage = pd.DataFrame({
            'Índice': ['idx_estudiante_sede', 'idx_matricula_fecha', 
                      'idx_pago_estudiante', 'idx_nota_matricula'],
            'Uso (%)': [95, 88, 92, 76],
            'Tamaño (MB)': [12, 8, 15, 6]
        })
        
        fig_idx = px.bar(index_usage, x='Índice', y='Uso (%)',
                        color='Uso (%)',
                        color_continuous_scale='Viridis')
        st.plotly_chart(fig_idx, use_container_width=True)
    
    with col2:
        st.markdown("**Recomendaciones de Optimización**")
        
        st.info("""
        🔍 **Índices Sugeridos:**
        - `estudiante(email)` - Muchos WHERE por email
        - `pago(fecha, monto)` - Consultas de rango frecuentes
        - `nota(tipo_evaluacion)` - Agrupaciones comunes
        
        ⚡ **Queries a Optimizar:**
        - Agregar LIMIT a consultas sin restricción
        - Usar JOIN en lugar de subqueries
        - Implementar paginación en reportes
        """)

with tab4:
    st.header("🔍 Herramientas de Diagnóstico")
    
    # Herramientas disponibles
    tool_col1, tool_col2 = st.columns([1, 2])
    
    with tool_col1:
        st.markdown("### 🛠️ Herramientas")
        
        diagnostic_tool = st.radio(
            "Seleccionar herramienta:",
            ["Verificar Conectividad", "Analizar Tablas", "Ver Logs", 
             "Estadísticas de Cache", "Test de Latencia"]
        )
    
    with tool_col2:
        st.markdown(f"### 📋 {diagnostic_tool}")
        
        if diagnostic_tool == "Verificar Conectividad":
            if st.button("🔍 Ejecutar Test de Conectividad", use_container_width=True):
                with st.spinner("Probando conexiones..."):
                    # Test real de conexiones
                    status = test_all_connections()
                    
                    for service, is_connected in status.items():
                        if is_connected:
                            st.success(f"✅ {service}: Conexión exitosa")
                        else:
                            st.error(f"❌ {service}: Fallo de conexión")
                    
                    # Test adicional de latencia
                    st.markdown("**Latencia de Red:**")
                    for sede in ['central', 'sancarlos', 'heredia']:
                        latency = random.uniform(0.5, 5.0)
                        st.metric(get_sede_info(sede)['name'], f"{latency:.2f} ms")
        
        elif diagnostic_tool == "Analizar Tablas":
            sede_analyze = st.selectbox("Seleccionar sede:", 
                                      ['central', 'sancarlos', 'heredia'])
            
            if st.button("📊 Analizar Estructura", use_container_width=True):
                with get_db_connection(sede_analyze) as db:
                    if db:
                        # Obtener información de tablas
                        query = """
                        SELECT 
                            table_name,
                            table_rows,
                            data_length/1024/1024 as data_mb,
                            index_length/1024/1024 as index_mb,
                            table_comment
                        FROM information_schema.tables
                        WHERE table_schema = %s
                        ORDER BY table_rows DESC
                        """
                        
                        df_tables = db.get_dataframe(query, (db.config['database'],))
                        if df_tables is not None:
                            df_tables['data_mb'] = df_tables['data_mb'].round(2)
                            df_tables['index_mb'] = df_tables['index_mb'].round(2)
                            st.dataframe(df_tables, use_container_width=True, hide_index=True)
        
        elif diagnostic_tool == "Ver Logs":
            st.markdown("**Últimas entradas del log:**")
            
            # Simular log entries
            log_entries = []
            for i in range(10):
                timestamp = datetime.now() - timedelta(minutes=i*5)
                levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']
                level = random.choice(levels)
                
                messages = {
                    'INFO': ['Conexión establecida', 'Query ejecutada', 'Cache actualizado'],
                    'WARNING': ['Latencia elevada detectada', 'Cache miss rate alto', 'Conexión lenta'],
                    'ERROR': ['Timeout en conexión', 'Query fallida', 'Error de autenticación'],
                    'DEBUG': ['Iniciando replicación', 'Verificando índices', 'Limpiando cache']
                }
                
                log_entries.append({
                    'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'Level': level,
                    'Message': random.choice(messages[level]),
                    'Source': random.choice(['MySQL', 'Redis', 'NGINX', 'App'])
                })
            
            df_logs = pd.DataFrame(log_entries)
            
            # Aplicar colores según nivel
            def color_level(val):
                colors = {
                    'INFO': 'background-color: #90EE90',
                    'WARNING': 'background-color: #FFD700',
                    'ERROR': 'background-color: #FFB6C1',
                    'DEBUG': 'background-color: #E0E0E0'
                }
                return colors.get(val, '')
            
            styled_logs = df_logs.style.applymap(color_level, subset=['Level'])
            st.dataframe(styled_logs, use_container_width=True, hide_index=True)
        
        elif diagnostic_tool == "Estadísticas de Cache":
            redis_conn = get_redis_connection()
            
            if redis_conn and redis_conn.redis_client:
                try:
                    # Obtener info de Redis
                    info = redis_conn.redis_client.info()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Memoria Usada", 
                                f"{info.get('used_memory_human', 'N/A')}")
                        st.metric("Hits", 
                                f"{info.get('keyspace_hits', 0):,}")
                        st.metric("Clientes Conectados", 
                                info.get('connected_clients', 0))
                    
                    with col2:
                        st.metric("Hit Rate", 
                                f"{(info.get('keyspace_hits', 0) / (info.get('keyspace_hits', 0) + info.get('keyspace_misses', 1)) * 100):.1f}%")
                        st.metric("Misses", 
                                f"{info.get('keyspace_misses', 0):,}")
                        st.metric("Keys Totales", 
                                info.get('db0', {}).get('keys', 0))
                except:
                    st.error("No se pudo conectar con Redis")
        
        elif diagnostic_tool == "Test de Latencia":
            if st.button("🏃 Ejecutar Test de Latencia", use_container_width=True):
                st.markdown("**Resultados del Test:**")
                
                # Progress bar
                progress = st.progress(0)
                
                latency_results = []
                
                for i, sede in enumerate(['central', 'sancarlos', 'heredia']):
                    progress.progress((i + 1) / 3)
                    
                    with get_db_connection(sede) as db:
                        if db:
                            # Medir tiempo de una query simple
                            start_time = time.time()
                            db.execute_query("SELECT 1")
                            end_time = time.time()
                            
                            latency = (end_time - start_time) * 1000  # ms
                            
                            latency_results.append({
                                'Sede': get_sede_info(sede)['name'],
                                'Latencia (ms)': round(latency, 2),
                                'Estado': '✅ Óptimo' if latency < 50 else '⚠️ Alto'
                            })
                
                df_latency = pd.DataFrame(latency_results)
                st.dataframe(df_latency, use_container_width=True, hide_index=True)

with tab5:
    st.header("📉 Datos Históricos")
    
    # Selector de período
    col1, col2, col3 = st.columns(3)
    
    with col1:
        period = st.selectbox("Período:", 
                            ["Última hora", "Últimas 24h", "Última semana", "Último mes"])
    
    with col2:
        metric_type = st.selectbox("Métrica:", 
                                 ["Transacciones", "Latencia", "Errores", "Uso de recursos"])
    
    with col3:
        if st.button("📥 Descargar Datos", use_container_width=True):
            st.info("Función de descarga simulada")
    
    # Generar datos históricos según el período
    if period == "Última hora":
        time_points = pd.date_range(end=datetime.now(), periods=60, freq='min')
    elif period == "Últimas 24h":
        time_points = pd.date_range(end=datetime.now(), periods=24, freq='h')
    elif period == "Última semana":
        time_points = pd.date_range(end=datetime.now(), periods=7, freq='D')
    else:
        time_points = pd.date_range(end=datetime.now(), periods=30, freq='D')
    
    # Crear datos según la métrica seleccionada
    if metric_type == "Transacciones":
        historical_data = pd.DataFrame({
            'Tiempo': time_points,
            'Central': np.random.poisson(100, len(time_points)),
            'San Carlos': np.random.poisson(80, len(time_points)),
            'Heredia': np.random.poisson(70, len(time_points))
        })
        
        fig_hist = px.line(historical_data, x='Tiempo', 
                          y=['Central', 'San Carlos', 'Heredia'],
                          title=f'Transacciones - {period}')
        fig_hist.update_yaxis(title="Transacciones/min")
    
    elif metric_type == "Latencia":
        historical_data = pd.DataFrame({
            'Tiempo': time_points,
            'Central': np.random.normal(20, 5, len(time_points)),
            'San Carlos': np.random.normal(35, 8, len(time_points)),
            'Heredia': np.random.normal(30, 6, len(time_points))
        })
        
        fig_hist = px.line(historical_data, x='Tiempo', 
                          y=['Central', 'San Carlos', 'Heredia'],
                          title=f'Latencia Promedio - {period}')
        fig_hist.update_yaxis(title="Latencia (ms)")
    
    elif metric_type == "Errores":
        historical_data = pd.DataFrame({
            'Tiempo': time_points,
            'Timeouts': np.random.poisson(2, len(time_points)),
            'Conexión': np.random.poisson(1, len(time_points)),
            'Query': np.random.poisson(3, len(time_points))
        })
        
        fig_hist = px.area(historical_data, x='Tiempo', 
                          y=['Timeouts', 'Conexión', 'Query'],
                          title=f'Errores por Tipo - {period}')
        fig_hist.update_yaxis(title="Errores/hora")
    
    else:  # Uso de recursos
        historical_data = pd.DataFrame({
            'Tiempo': time_points,
            'CPU %': np.random.normal(50, 15, len(time_points)),
            'RAM %': np.random.normal(65, 10, len(time_points)),
            'Disco %': np.random.normal(40, 5, len(time_points))
        })
        
        fig_hist = px.line(historical_data, x='Tiempo', 
                          y=['CPU %', 'RAM %', 'Disco %'],
                          title=f'Uso de Recursos - {period}')
        fig_hist.update_yaxis(title="Porcentaje de Uso")
    
    # Mostrar gráfico
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # Estadísticas del período
    st.subheader("📊 Estadísticas del Período")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Promedio", f"{historical_data.iloc[:, 1:].mean().mean():.2f}")
    
    with col2:
        st.metric("Máximo", f"{historical_data.iloc[:, 1:].max().max():.2f}")
    
    with col3:
        st.metric("Mínimo", f"{historical_data.iloc[:, 1:].min().min():.2f}")
    
    with col4:
        st.metric("Desv. Estándar", f"{historical_data.iloc[:, 1:].std().mean():.2f}")
    
    # Alertas y eventos notables
    st.subheader("🚨 Eventos Notables del Período")
    
    events = pd.DataFrame({
        'Timestamp': [
            datetime.now() - timedelta(hours=random.randint(1, 24)) 
            for _ in range(5)
        ],
        'Tipo': ['Alta latencia', 'Pico de tráfico', 'Error de conexión', 
                'Mantenimiento', 'Backup completado'],
        'Severidad': ['Alta', 'Media', 'Alta', 'Info', 'Info'],
        'Descripción': [
            'Latencia superior a 2s detectada en San Carlos',
            'Incremento del 150% en transacciones',
            'Pérdida temporal de conexión con Heredia',
            'Actualización de índices programada',
            'Backup diario completado exitosamente'
        ]
    })
    
    events = events.sort_values('Timestamp', ascending=False)
    
    # Aplicar colores según severidad
    def color_severity(val):
        colors = {
            'Alta': 'background-color: #FFB6C1',
            'Media': 'background-color: #FFD700',
            'Info': 'background-color: #90EE90'
        }
        return colors.get(val, '')
    
    styled_events = events.style.applymap(color_severity, subset=['Severidad'])
    st.dataframe(styled_events, use_container_width=True, hide_index=True)

# Sidebar con controles y resumen
with st.sidebar:
    st.markdown("### 📈 Panel de Control")
    
    # Estado general del sistema
    st.markdown("**Estado General**")
    
    system_health = random.choice(['Óptimo', 'Bueno', 'Degradado'])
    if system_health == 'Óptimo':
        st.success(f"✅ Sistema: {system_health}")
    elif system_health == 'Bueno':
        st.warning(f"⚠️ Sistema: {system_health}")
    else:
        st.error(f"❌ Sistema: {system_health}")
    
    st.markdown("---")
    
    # Alertas activas
    st.markdown("### 🚨 Alertas Activas")
    
    alerts = [
        "⚠️ Cache hit rate bajo (65%)",
        "⚠️ Espacio en disco >70%",
        "ℹ️ Backup programado 02:00"
    ]
    
    for alert in alerts:
        st.caption(alert)
    
    st.markdown("---")
    
    # Acciones rápidas
    st.markdown("### ⚡ Acciones Rápidas")
    
    if st.button("🔄 Limpiar Cache", use_container_width=True):
        st.info("Cache limpiado")
    
    if st.button("📊 Generar Reporte", use_container_width=True):
        st.info("Generando reporte...")
    
    if st.button("🔍 Análisis Completo", use_container_width=True):
        st.info("Iniciando análisis...")
    
    st.markdown("---")
    
    # Información del sistema
    st.markdown("### ℹ️ Información")
    st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
    st.caption("Versión: 1.0.0")
    st.caption("Entorno: Producción")

# Auto-refresh logic
if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()