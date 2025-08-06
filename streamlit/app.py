import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from config import APP_CONFIG, DB_CONFIG, COLORS, get_all_sedes, get_sede_info
from utils.db_connections import test_all_connections, get_db_connection, execute_distributed_query, test_load_balancer, get_nginx_status

st.set_page_config(
    page_title=APP_CONFIG['title'],
    page_icon=APP_CONFIG['page_icon'],
    layout=APP_CONFIG['layout'],
    initial_sidebar_state=APP_CONFIG['initial_sidebar_state'],
    menu_items=APP_CONFIG['menu_items']
)

st.markdown("""
<style>
    /* Estilo para las métricas */
    [data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.2);
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    
    /* Estilo para los contenedores de información */
    .info-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #1f77b4;
    }
    
    /* Estilo para mensajes de estado */
    .status-online {
        color: #2ca02c;
        font-weight: bold;
    }
    
    .status-offline {
        color: #d62728;
        font-weight: bold;
    }
    
    /* Estilo para el título principal */
    .main-header {
        text-align: center;
        padding: 20px 0;
        background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

def show_connection_status():
    """
    Muestra el estado de conexión de todas las sedes, servicios y Load Balancer.
    """
    st.subheader(" Estado de Conexiones")
    
    cols = st.columns(len(DB_CONFIG) + 2) 
    
    with st.spinner("Verificando conexiones..."):
        status = test_all_connections()
        lb_status = test_load_balancer()
        nginx_info = get_nginx_status()
    
    for idx, (sede, is_connected) in enumerate(status.items()):
        if sede != 'redis':
            with cols[idx]:
                sede_info = get_sede_info(sede)
                if is_connected:
                    st.success(f"✅ {sede_info['name']}")
                    st.caption("Conectado")
                else:
                    st.error(f"❌ {sede_info['name']}")
                    st.caption("Desconectado")
    
    with cols[-2]:
        if status.get('redis', False):
            st.success("✅ Redis Cache")
            st.caption("Conectado")
        else:
            st.error("❌ Redis Cache")
            st.caption("Desconectado")
    
    with cols[-1]:
        if lb_status:
            st.success("✅ Load Balancer")
            st.caption(f"Tiempo: {nginx_info.get('response_time', 'N/A')}s")
        else:
            st.error("❌ Load Balancer")
            st.caption("Desconectado")

    st.markdown("### Salud General del Sistema")

    # Calcular score de salud
    conexiones_activas = sum(1 for s in status.values() if s) + (1 if lb_status else 0)
    total_conexiones = len(status) + 1  # +1 para load balancer
    health_score = (conexiones_activas / total_conexiones) * 100

    # Determinar estado
    if health_score == 100:
        health_status = "🟢 Excelente"
        health_color = "green"
    elif health_score >= 80:
        health_status = "🟡 Bueno" 
        health_color = "orange"
    else:
        health_status = "🔴 Degradado"
        health_color = "red"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Score de Salud",
            f"{health_score:.0f}%",
            help="Porcentaje de servicios operativos"
        )

    with col2:
        st.metric(
            "Estado General", 
            health_status,
            help="Estado consolidado del sistema"
        )

    with col3:
        st.metric(
            "Servicios Activos",
            f"{conexiones_activas}/{total_conexiones}",
            help="Conexiones activas vs total"
        )

    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = health_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Salud del Sistema"},
        delta = {'reference': 90},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 60], 'color': "lightgray"},
                {'range': [60, 80], 'color': "yellow"},
                {'range': [80, 95], 'color': "lightgreen"},
                {'range': [95, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

def show_system_overview():
    st.subheader("Visión General del Sistema")
    
    queries = {
        'estudiantes': "SELECT COUNT(*) as total FROM estudiante",
        'profesores': "SELECT COUNT(*) as total FROM profesor",
        'carreras': "SELECT COUNT(*) as total FROM carrera",
        'cursos': "SELECT COUNT(*) as total FROM curso",
        'matriculas': "SELECT COUNT(*) as total FROM matricula",
        'planillas': "SELECT COUNT(*) as total FROM planilla",
        'pagares': "SELECT COUNT(*) as total FROM pagare"
    }
    
    metrics = {}
    for sede in get_all_sedes():
        metrics[sede] = {}
        with get_db_connection(sede) as db:
            if db:
                for metric_name, query in queries.items():
                    if metric_name in ['planillas', 'pagares'] and sede != 'central':
                        continue
          
                    try:
                        result = db.execute_query(query)
                        if result and len(result) > 0:
                            metrics[sede][metric_name] = result[0]['total']
                        else:
                            metrics[sede][metric_name] = 0
                    except:
                        metrics[sede][metric_name] = 0
    

    st.markdown("### Métricas por Sede")
    
    tabs = st.tabs([get_sede_info(sede)['name'] for sede in get_all_sedes()])
    
    for idx, sede in enumerate(get_all_sedes()):
        with tabs[idx]:
            sede_info = get_sede_info(sede)
            st.markdown(f"**{sede_info['description']}**")
            
            if sede == 'central':
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                with col1:
                    st.metric("Estudiantes", metrics[sede].get('estudiantes', 0))
                with col2:
                    st.metric("Profesores", metrics[sede].get('profesores', 0))
                with col3:
                    st.metric("Carreras", metrics[sede].get('carreras', 0))
                with col4:
                    st.metric("Cursos", metrics[sede].get('cursos', 0))
                with col5:
                    st.metric("Planillas", metrics[sede].get('planillas', 0))
                with col6:
                    st.metric("Pagarés", metrics[sede].get('pagares', 0))
            else:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Estudiantes", metrics[sede].get('estudiantes', 0))
                with col2:
                    st.metric("Cursos", metrics[sede].get('cursos', 0))
                with col3:
                    st.metric("Matrículas", metrics[sede].get('matriculas', 0))
                with col4:
                    st.metric("Carreras", metrics[sede].get('carreras', 0))

    st.markdown("### Vista Consolidada del Sistema")

    total_estudiantes = sum(metrics[sede].get('estudiantes', 0) for sede in get_all_sedes())
    total_profesores = sum(metrics[sede].get('profesores', 0) for sede in get_all_sedes())
    total_cursos = sum(metrics[sede].get('cursos', 0) for sede in get_all_sedes())
    total_matriculas = sum(metrics[sede].get('matriculas', 0) for sede in get_all_sedes())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Estudiantes", f"{total_estudiantes:,}", 
                help="Suma de estudiantes en todas las sedes")
    with col2:
        st.metric("Total Profesores", f"{total_profesores:,}",
                help="Profesores activos en el sistema")
    with col3:
        st.metric("otal Cursos", f"{total_cursos:,}",
                help="Cursos ofrecidos en todas las sedes")
    with col4:
        st.metric("Total Matrículas", f"{total_matriculas:,}",
                help="Matrículas activas en el sistema")

    col1, col2 = st.columns(2)

    with col1:
        estudiantes_data = []
        for sede in get_all_sedes():
            sede_info = get_sede_info(sede)
            estudiantes_data.append({
                'Sede': sede_info['name'].replace('🏛️ ', '').replace('🏢 ', '').replace('🏫 ', ''),
                'Estudiantes': metrics[sede].get('estudiantes', 0),
                'Color': sede_info['color']
            })
        
        df_estudiantes = pd.DataFrame(estudiantes_data)
        
        if not df_estudiantes.empty:
            fig_estudiantes = px.bar(
                df_estudiantes, 
                x='Sede', 
                y='Estudiantes',
                title='Distribución de Estudiantes por Sede',
                color='Sede',
                color_discrete_map={row['Sede']: row['Color'] for _, row in df_estudiantes.iterrows()}
            )
            fig_estudiantes.update_layout(
                showlegend=False,
                height=400,
                xaxis_title="Sede",
                yaxis_title="Número de Estudiantes"
            )
            st.plotly_chart(fig_estudiantes, use_container_width=True)

    with col2:
        if not df_estudiantes.empty and df_estudiantes['Estudiantes'].sum() > 0:
            fig_pie = px.pie(
                df_estudiantes, 
                values='Estudiantes', 
                names='Sede',
                title='Distribución Porcentual de Estudiantes',
                color='Sede',
                color_discrete_map={row['Sede']: row['Color'] for _, row in df_estudiantes.iterrows()}
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)

def show_recent_activity():
    st.subheader("Actividad Reciente")
    
    tab1, tab2, tab3 = st.tabs(["Últimas Matrículas", "Últimos Pagos", "Notas Recientes"])
    
    with tab1:
        matriculas = []
        for sede in ['sancarlos', 'heredia', 'central']:
            with get_db_connection(sede) as db:
                if db:
                    query = """
                    SELECT e.nombre as estudiante, c.nombre as curso, 
                        m.fecha_creacion, s.nombre as sede
                    FROM matricula m
                    JOIN estudiante e ON m.id_estudiante = e.id_estudiante
                    JOIN curso c ON m.id_curso = c.id_curso
                    JOIN sede s ON e.id_sede = s.id_sede
                    ORDER BY m.fecha_creacion DESC
                    LIMIT 10
                    """
                    result = db.get_dataframe(query)
                    if result is not None and not result.empty:
                        matriculas.append(result)
        
        if matriculas:
            df_matriculas = pd.concat(matriculas, ignore_index=True)
            df_matriculas = df_matriculas.sort_values('fecha_creacion', ascending=False).head(10)
            st.dataframe(df_matriculas, use_container_width=True, hide_index=True)
        else:
            st.info("No hay matrículas recientes")
    
    with tab2:
        pagos = []
        for sede in ['sancarlos', 'heredia', 'central']:
            with get_db_connection(sede) as db:
                if db:
                    query = """
                    SELECT e.nombre as estudiante, p.monto, p.fecha, 
                           s.nombre as sede
                    FROM pago p
                    JOIN estudiante e ON p.id_estudiante = e.id_estudiante
                    JOIN sede s ON e.id_sede = s.id_sede
                    ORDER BY p.fecha DESC
                    LIMIT 10
                    """
                    result = db.get_dataframe(query)
                    if result is not None and not result.empty:
                        pagos.append(result)
        
        if pagos:
            df_pagos = pd.concat(pagos, ignore_index=True)
            df_pagos = df_pagos.sort_values('fecha', ascending=False).head(10)
            df_pagos['monto'] = df_pagos['monto'].apply(lambda x: f"₡{x:,.2f}")
            st.dataframe(df_pagos, use_container_width=True, hide_index=True)
        else:
            st.info("No hay pagos recientes")
    
    with tab3:
        notas = []
        for sede in ['sancarlos', 'heredia', 'central']:
            with get_db_connection(sede) as db:
                if db:
                    query = """
                    SELECT e.nombre as estudiante, c.nombre as curso, 
                           n.nota, n.fecha_creacion, s.nombre as sede
                    FROM nota n
                    JOIN matricula m ON n.id_matricula = m.id_matricula
                    JOIN estudiante e ON m.id_estudiante = e.id_estudiante
                    JOIN curso c ON m.id_curso = c.id_curso
                    JOIN sede s ON e.id_sede = s.id_sede
                    ORDER BY n.id_nota DESC
                    LIMIT 10
                    """
                    result = db.get_dataframe(query)
                    if result is not None and not result.empty:
                        notas.append(result)
        
        if notas:
            df_notas = pd.concat(notas, ignore_index=True).head(10)
            st.dataframe(df_notas, use_container_width=True, hide_index=True)
        else:
            st.info("No hay notas recientes")

def main():
    st.markdown("""
    <div class="main-header">
        <h1>Sistema Distribuido Universidad Cenfotec</h1>
        <p>Dashboard de Monitoreo y Administración</p>
    </div>
    """, unsafe_allow_html=True)
    
        
    # Mostrar las diferentes secciones del dashboard
    show_connection_status()
    st.divider()
    
    show_system_overview()
    st.divider()
    
    show_recent_activity()
    
    st.markdown("---")

with st.sidebar:
    
    if st.button("🔄 Actualizar Dashboard", use_container_width=True):
        st.rerun()
    

# Ejecutar la aplicación
if __name__ == "__main__":
    main()