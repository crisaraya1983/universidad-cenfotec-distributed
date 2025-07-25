"""
Sistema de Monitoreo de Base de Datos Distribuida - Universidad Cenfotec
Aplicación principal que proporciona una interfaz visual para demostrar
la funcionalidad del sistema distribuido.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Agregar el directorio actual al path para importar módulos locales
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importar configuración y utilidades
from config import APP_CONFIG, DB_CONFIG, COLORS, get_all_sedes, get_sede_info
from utils.db_connections import test_all_connections, get_db_connection, execute_distributed_query

# Configuración de la página principal
st.set_page_config(
    page_title=APP_CONFIG['title'],
    page_icon=APP_CONFIG['page_icon'],
    layout=APP_CONFIG['layout'],
    initial_sidebar_state=APP_CONFIG['initial_sidebar_state'],
    menu_items=APP_CONFIG['menu_items']
)

# CSS personalizado para mejorar la apariencia
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
    Muestra el estado de conexión de todas las sedes y servicios.
    Utiliza indicadores visuales para mostrar si cada componente está operativo.
    """
    st.subheader("🔌 Estado de Conexiones")
    
    # Crear columnas para mostrar el estado de cada sede
    cols = st.columns(len(DB_CONFIG) + 1)  # +1 para Redis
    
    # Probar todas las conexiones
    with st.spinner("Verificando conexiones..."):
        status = test_all_connections()
    
    # Mostrar estado de cada sede MySQL
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
    
    # Mostrar estado de Redis
    with cols[-1]:
        if status.get('redis', False):
            st.success("✅ Redis Cache")
            st.caption("Conectado")
        else:
            st.error("❌ Redis Cache")
            st.caption("Desconectado")

def show_system_overview():
    """
    Muestra una visión general del sistema con métricas clave.
    Esta función recopila estadísticas básicas de cada sede.
    """
    st.subheader("📊 Visión General del Sistema")
    
    # Consultas para obtener métricas básicas
    queries = {
        'estudiantes': "SELECT COUNT(*) as total FROM estudiante",
        'profesores': "SELECT COUNT(*) as total FROM profesor",
        'carreras': "SELECT COUNT(*) as total FROM carrera",
        'cursos': "SELECT COUNT(*) as total FROM curso",
        'matriculas': "SELECT COUNT(*) as total FROM matricula",
        'planillas': "SELECT COUNT(*) as total FROM planilla",
        'pagares': "SELECT COUNT(*) as total FROM pagare"
    }
    
    # Recopilar métricas por sede
    metrics = {}
    for sede in get_all_sedes():
        metrics[sede] = {}
        with get_db_connection(sede) as db:
            if db:
                for metric_name, query in queries.items():
                    # Algunas tablas solo existen en ciertas sedes
                    if sede == 'central' and metric_name not in ['profesores', 'carreras', 'planillas', 'pagares']:
                        continue
                    elif sede != 'central' and metric_name in ['planillas', 'pagares']:
                        continue
                    
                    try:
                        result = db.execute_query(query)
                        if result and len(result) > 0:
                            metrics[sede][metric_name] = result[0]['total']
                        else:
                            metrics[sede][metric_name] = 0
                    except:
                        metrics[sede][metric_name] = 0
    
    # Mostrar métricas en columnas
    st.markdown("### 📈 Métricas por Sede")
    
    # Crear tabs para cada sede
    tabs = st.tabs([get_sede_info(sede)['name'] for sede in get_all_sedes()])
    
    for idx, sede in enumerate(get_all_sedes()):
        with tabs[idx]:
            sede_info = get_sede_info(sede)
            st.markdown(f"**{sede_info['description']}**")
            
            # Mostrar métricas en columnas
            if sede == 'central':
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("👨‍🏫 Profesores", metrics[sede].get('profesores', 0))
                with col2:
                    st.metric("🎓 Carreras", metrics[sede].get('carreras', 0))
                with col3:
                    st.metric("💰 Planillas", metrics[sede].get('planillas', 0))
                with col4:
                    st.metric("📄 Pagarés", metrics[sede].get('pagares', 0))
            else:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("👥 Estudiantes", metrics[sede].get('estudiantes', 0))
                with col2:
                    st.metric("📚 Cursos", metrics[sede].get('cursos', 0))
                with col3:
                    st.metric("📝 Matrículas", metrics[sede].get('matriculas', 0))
                with col4:
                    st.metric("🎓 Carreras", metrics[sede].get('carreras', 0))

def show_data_distribution():
    """
    Visualiza la distribución de datos entre las sedes usando gráficos.
    Esto ayuda a entender visualmente cómo está fragmentada la información.
    """
    st.subheader("🗂️ Distribución de Datos")
    
    # Obtener conteo de estudiantes por sede
    estudiantes_data = []
    
    for sede in ['sancarlos', 'heredia']:
        with get_db_connection(sede) as db:
            if db:
                query = """
                SELECT s.nombre as sede, COUNT(e.id_estudiante) as total
                FROM estudiante e
                JOIN sede s ON e.id_sede = s.id_sede
                GROUP BY s.nombre
                """
                result = db.execute_query(query)
                if result:
                    for row in result:
                        estudiantes_data.append({
                            'Sede': row['sede'],
                            'Estudiantes': row['total']
                        })
    
    if estudiantes_data:
        df_estudiantes = pd.DataFrame(estudiantes_data)
        
        # Crear gráfico de distribución
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras
            fig_bar = px.bar(df_estudiantes, 
                            x='Sede', 
                            y='Estudiantes',
                            title='Estudiantes por Sede',
                            color='Sede',
                            color_discrete_map={'San Carlos': COLORS['secondary'], 
                                              'Heredia': COLORS['success']})
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Gráfico de pie
            fig_pie = px.pie(df_estudiantes, 
                           values='Estudiantes', 
                           names='Sede',
                           title='Distribución Porcentual de Estudiantes',
                           color_discrete_map={'San Carlos': COLORS['secondary'], 
                                             'Heredia': COLORS['success']})
            st.plotly_chart(fig_pie, use_container_width=True)

def show_recent_activity():
    """
    Muestra actividad reciente del sistema como nuevas matrículas o pagos.
    Esto demuestra que el sistema está activo y procesando transacciones.
    """
    st.subheader("🔄 Actividad Reciente")
    
    # Crear tabs para diferentes tipos de actividad
    tab1, tab2, tab3 = st.tabs(["📝 Últimas Matrículas", "💰 Últimos Pagos", "📊 Notas Recientes"])
    
    with tab1:
        # Obtener últimas matrículas de ambas sedes regionales
        matriculas = []
        for sede in ['sancarlos', 'heredia']:
            with get_db_connection(sede) as db:
                if db:
                    query = """
                    SELECT e.nombre as estudiante, c.nombre as curso, 
                           m.fecha_matricula, s.nombre as sede
                    FROM matricula m
                    JOIN estudiante e ON m.id_estudiante = e.id_estudiante
                    JOIN curso c ON m.id_curso = c.id_curso
                    JOIN sede s ON e.id_sede = s.id_sede
                    ORDER BY m.fecha_matricula DESC
                    LIMIT 5
                    """
                    result = db.get_dataframe(query)
                    if result is not None and not result.empty:
                        matriculas.append(result)
        
        if matriculas:
            df_matriculas = pd.concat(matriculas, ignore_index=True)
            df_matriculas = df_matriculas.sort_values('fecha_matricula', ascending=False).head(10)
            st.dataframe(df_matriculas, use_container_width=True, hide_index=True)
        else:
            st.info("No hay matrículas recientes")
    
    with tab2:
        # Obtener últimos pagos
        pagos = []
        for sede in ['sancarlos', 'heredia']:
            with get_db_connection(sede) as db:
                if db:
                    query = """
                    SELECT e.nombre as estudiante, p.monto, p.fecha, 
                           p.concepto, s.nombre as sede
                    FROM pago p
                    JOIN estudiante e ON p.id_estudiante = e.id_estudiante
                    JOIN sede s ON e.id_sede = s.id_sede
                    ORDER BY p.fecha DESC
                    LIMIT 5
                    """
                    result = db.get_dataframe(query)
                    if result is not None and not result.empty:
                        pagos.append(result)
        
        if pagos:
            df_pagos = pd.concat(pagos, ignore_index=True)
            df_pagos = df_pagos.sort_values('fecha', ascending=False).head(10)
            # Formatear el monto como moneda
            df_pagos['monto'] = df_pagos['monto'].apply(lambda x: f"₡{x:,.2f}")
            st.dataframe(df_pagos, use_container_width=True, hide_index=True)
        else:
            st.info("No hay pagos recientes")
    
    with tab3:
        # Obtener notas recientes
        notas = []
        for sede in ['sancarlos', 'heredia']:
            with get_db_connection(sede) as db:
                if db:
                    query = """
                    SELECT e.nombre as estudiante, c.nombre as curso, 
                           n.nota, n.tipo_evaluacion, s.nombre as sede
                    FROM nota n
                    JOIN matricula m ON n.id_matricula = m.id_matricula
                    JOIN estudiante e ON m.id_estudiante = e.id_estudiante
                    JOIN curso c ON m.id_curso = c.id_curso
                    JOIN sede s ON e.id_sede = s.id_sede
                    ORDER BY n.id_nota DESC
                    LIMIT 5
                    """
                    result = db.get_dataframe(query)
                    if result is not None and not result.empty:
                        notas.append(result)
        
        if notas:
            df_notas = pd.concat(notas, ignore_index=True).head(10)
            st.dataframe(df_notas, use_container_width=True, hide_index=True)
        else:
            st.info("No hay notas recientes")

# Función principal
def main():
    """
    Función principal que organiza el layout del dashboard.
    """
    # Título principal con estilo
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Sistema Distribuido Universidad Cenfotec</h1>
        <p>Dashboard de Monitoreo y Administración</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Información del sistema
    with st.expander("ℹ️ Acerca del Sistema", expanded=False):
        st.markdown("""
        ### Arquitectura del Sistema
        
        Este sistema demuestra una implementación de base de datos distribuida con:
        
        - **3 Sedes Geográficas**: Central (San José), San Carlos y Heredia
        - **Fragmentación Horizontal**: Estudiantes separados por sede
        - **Fragmentación Vertical**: Datos administrativos en Central, académicos en regionales
        - **Replicación Master-Slave**: Datos maestros replicados desde Central
        - **Cache Distribuido**: Redis para optimización de consultas
        - **Load Balancer**: NGINX para distribución de carga
        
        ### Tecnologías Utilizadas
        - 🐳 Docker para contenerización
        - 🗄️ MySQL 8.0 para bases de datos
        - 🔄 Redis para cache
        - ⚖️ NGINX para balanceo de carga
        - 🐍 Python + Streamlit para la interfaz
        """)
    
    # Mostrar las diferentes secciones del dashboard
    show_connection_status()
    st.divider()
    
    show_system_overview()
    st.divider()
    
    show_data_distribution()
    st.divider()
    
    show_recent_activity()
    
    # Footer con información adicional
    st.markdown("---")
    st.markdown(
        f"<p style='text-align: center; color: gray;'>Sistema actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
        unsafe_allow_html=True
    )

# Sidebar con navegación e información
with st.sidebar:
    st.markdown("### 🗺️ Navegación")
    st.markdown("""
    Esta es la página principal del sistema. 
    Usa el menú de páginas para explorar:
    
    - **📊 Fragmentación**: Ver cómo están distribuidos los datos
    - **🔄 Replicación**: Monitorear la sincronización entre sedes
    - **💼 Transacciones**: Ejecutar operaciones distribuidas
    - **📈 Monitoreo**: Análisis detallado del rendimiento
    """)
    
    st.markdown("---")
    
    # Botón para refrescar la página
    if st.button("🔄 Actualizar Dashboard", use_container_width=True):
        st.rerun()
    
    # Información de contexto
    st.markdown("---")
    st.markdown("### ℹ️ Información")
    st.markdown("""
    **Proyecto Final**  
    Base de Datos Distribuidas  
    Universidad Cenfotec  
    2025
    """)

# Ejecutar la aplicación
if __name__ == "__main__":
    main()