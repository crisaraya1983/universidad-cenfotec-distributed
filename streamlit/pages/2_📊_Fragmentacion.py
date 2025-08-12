import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG, COLORS, get_sede_info
from utils.db_connections import get_db_connection, execute_distributed_query

st.set_page_config(
    page_title="Fragmentación - Sistema Cenfotec",
    page_icon="📊",
    layout="wide"
)

if 'fragmentos_estudiantes' not in st.session_state:
    st.session_state.fragmentos_estudiantes = {}

if 'fragmentos_cursos' not in st.session_state:
    st.session_state.fragmentos_cursos = {}

if 'datos_administrativos' not in st.session_state:
    st.session_state.datos_administrativos = {}

if 'datos_academicos' not in st.session_state:
    st.session_state.datos_academicos = {}

if 'fragmentacion_derivada' not in st.session_state:
    st.session_state.fragmentacion_derivada = {}

def limpiar_resultados(categoria):
    if categoria == 'estudiantes':
        st.session_state.fragmentos_estudiantes = {}
    elif categoria == 'cursos':
        st.session_state.fragmentos_cursos = {}
    elif categoria == 'administrativos':
        st.session_state.datos_administrativos = {}
    elif categoria == 'academicos':
        st.session_state.datos_academicos = {}
    elif categoria == 'derivada':
        st.session_state.fragmentacion_derivada = {}

st.title("Fragmentación de Bases de Datos Distribuidas")

tab1, tab2, tab3, tab4 = st.tabs([
    "Conceptos Fundamentales", 
    "Fragmentación Horizontal", 
    "Fragmentación Vertical", 
    "Fragmentación Derivada"
])

with tab1:
    st.header("Conceptos Fundamentales de Fragmentación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### **Fragmentación Horizontal** 
        
        **Definición:** Dividir una tabla por **filas** según algún criterio.
        
        **Datos:**
        - `estudiante` WHERE `id_sede = 1` → Central
        - `estudiante` WHERE `id_sede = 2` → San Carlos
        - `estudiante` WHERE `id_sede = 3` → Heredia  
        - **Cada sede tiene PARTE de los estudiantes totales**
        
        **Consulta global:** Requiere UNIR datos de múltiples sedes
        """)
        
        st.markdown("""
        ### **Fragmentación Derivada** 
        
        **Definición:** Una tabla se fragmenta basándose en cómo está fragmentada otra tabla relacionada.
        
        **Datos:**
        - `matricula` sigue a `estudiante` 
        - Si estudiante está en SC → sus matrículas están en SC
        - Si estudiante está en HD → sus matrículas están en HD
        
        """)
    
    with col2:
        st.markdown("""
        ### **Fragmentación Vertical** 
        
        **Definición:** Dividir por **tipo de función** o **columnas**.
        
        **Datos:**
        - **Central:** Datos administrativos (`planilla`, `pagare`)
        - **Regionales:** Solo datos académicos (`matricula`, `nota`, `asistencia`)
        
        **Consulta mixta:** Requiere datos de Central + Regional
        """)
    
    st.markdown("### Visualización de Fragmentación")
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[0], y=[4],
        mode='markers+text',
        marker=dict(size=120, color='gold'),
        text=['<b>TABLA LÓGICA</b><br> ESTUDIANTES<br><br> Vista conceptual'],
        textposition="bottom center",
        name='Concepto Lógico'
    ))
    
    fig.add_trace(go.Scatter(
        x=[-3], y=[1],
        mode='markers+text',
        marker=dict(size=100, color=COLORS['secondary']),
        text=['<b>FRAGMENTO SC</b><br><br> id_sede = 2<br> Físico en SC'],
        textposition="bottom center",
        name='Fragmento San Carlos'
    ))
    
    fig.add_trace(go.Scatter(
        x=[3], y=[1],
        mode='markers+text',
        marker=dict(size=100, color=COLORS['success']),
        text=['<b>FRAGMENTO HD</b><br><br> id_sede = 3<br> Físico en HD'],
        textposition="bottom center",
        name='Fragmento Heredia'
    ))
    
    fig.add_annotation(x=-1.5, y=2.5, ax=0, ay=4, xref='x', yref='y', axref='x', ayref='y',
                      text="Fragmentación<br>Horizontal", showarrow=True, arrowhead=2, arrowcolor='red')
    fig.add_annotation(x=1.5, y=2.5, ax=0, ay=4, xref='x', yref='y', axref='x', ayref='y',
                      text="Fragmentación<br>Horizontal", showarrow=True, arrowhead=2, arrowcolor='red')
    
    fig.update_layout(
        title="🌐 Fragmentación Horizontal - Concepto vs Realidad Física",
        showlegend=True,
        height=500,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-5, 5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 5]),
        font=dict(size=11)
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Fragmentación Horizontal - Datos Distribuidos por Filas")
    
    st.markdown("### Ejemplo 1: Estudiantes Fragmentados por Sede")
    
    col_clear, col_dist = st.columns([1, 2])
    with col_clear:
        if st.button("Limpiar Resultados", key="clear_estudiantes"):
            limpiar_resultados('estudiantes')
    
    with col_dist:
        if st.button("Ejecutar Consulta Distribuida: TODOS los Estudiantes", key="dist_estudiantes"):
            with st.spinner('Consultando TODAS las sedes para unir fragmentos...'):
                try:
                    estudiantes_distribuidos = []
                    sedes_consultadas = []
                    
                    query_fragmento = """
                        SELECT 
                            e.nombre as estudiante,
                            s.nombre as sede,
                            e.sede_actual as id_sede,
                            COUNT(m.id_matricula) as matriculas
                        FROM estudiante e
                        JOIN sede s ON e.sede_actual = s.id_sede
                        LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
                        GROUP BY e.id_estudiante, e.nombre, s.nombre, e.sede_actual
                        ORDER BY e.nombre;
                    """
                    with get_db_connection('central') as db:
                        if db:
                            df_central = db.get_dataframe(query_fragmento)
                            if df_central is not None and not df_central.empty:
                                estudiantes_distribuidos.append(df_central)
                                sedes_consultadas.append("Central")

                    with get_db_connection('sancarlos') as db:
                        if db:
                            df_sc = db.get_dataframe(query_fragmento)
                            if df_sc is not None and not df_sc.empty:
                                estudiantes_distribuidos.append(df_sc)
                                sedes_consultadas.append("San Carlos")
                    
                    with get_db_connection('heredia') as db:
                        if db:
                            df_hd = db.get_dataframe(query_fragmento)
                            if df_hd is not None and not df_hd.empty:
                                estudiantes_distribuidos.append(df_hd)
                                sedes_consultadas.append("Heredia")
                    
                    if estudiantes_distribuidos:
                        df_todos = pd.concat(estudiantes_distribuidos, ignore_index=True)
                        
                        st.session_state.fragmentos_estudiantes['distribuida'] = {
                            'data': df_todos,
                            'sedes': sedes_consultadas,
                            'timestamp': datetime.now()
                        }
                
                except Exception as e:
                    st.error(f"❌ Error en consulta distribuida: {str(e)}")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Ver Fragmento: Central", type="primary", key="frag_central"):
            with st.spinner('Consultando fragmento en Sede Central...'):
                query_central = """
                    SELECT 
                        e.nombre as estudiante,
                        e.email,
                        s.nombre as sede,
                        e.id_sede
                    FROM estudiante e
                    JOIN sede s ON e.id_sede = s.id_sede
                    WHERE e.sede_actual = 1
                    ORDER BY e.nombre
                    LIMIT 20;
                """
                
                with get_db_connection('central') as db:
                    if db:
                        df_central = db.get_dataframe(query_central)
                        if df_central is not None and not df_central.empty:
                            count_query = "SELECT COUNT(*) as total FROM estudiante WHERE id_sede = 1"
                            total_central = db.get_dataframe(count_query)
                            total_count = total_central.iloc[0]['total'] if total_central is not None else 0
                            
                            st.session_state.fragmentos_estudiantes['central'] = {
                                'data': df_central,
                                'total': total_count,
                                'timestamp': datetime.now()
                            }
                        else:
                            st.session_state.fragmentos_estudiantes['central'] = {
                                'data': None,
                                'total': 0,
                                'timestamp': datetime.now()
                            }

    with col2:
        if st.button("Ver Fragmento: San Carlos", type="primary", key="frag_sc"):
            with st.spinner('Consultando fragmento en San Carlos...'):
                query_sc = """
                    SELECT 
                        e.nombre as estudiante,
                        e.email,
                        s.nombre as sede,
                        e.id_sede
                    FROM estudiante e
                    JOIN sede s ON e.id_sede = s.id_sede
                    WHERE e.sede_actual = 2
                    ORDER BY e.nombre
                    LIMIT 20;
                """
                
                with get_db_connection('sancarlos') as db:
                    if db:
                        df_sc = db.get_dataframe(query_sc)
                        if df_sc is not None and not df_sc.empty:
                            count_query = "SELECT COUNT(*) as total FROM estudiante WHERE id_sede = 2"
                            total_sc = db.get_dataframe(count_query)
                            total_count = total_sc.iloc[0]['total'] if total_sc is not None else 0
                            
                            st.session_state.fragmentos_estudiantes['sancarlos'] = {
                                'data': df_sc,
                                'total': total_count,
                                'timestamp': datetime.now()
                            }
                        else:
                            st.session_state.fragmentos_estudiantes['sancarlos'] = {
                                'data': None,
                                'total': 0,
                                'timestamp': datetime.now()
                            }

    with col3:
        if st.button("Ver Fragmento: Heredia", type="primary", key="frag_hd"):
            with st.spinner('Consultando fragmento en Heredia...'):
                query_hd = """
                    SELECT 
                        e.nombre as estudiante,
                        e.email,
                        s.nombre as sede,
                        e.id_sede
                    FROM estudiante e
                    JOIN sede s ON e.id_sede = s.id_sede
                    WHERE e.sede_actual = 3
                    ORDER BY e.nombre;
                """
                
                with get_db_connection('heredia') as db:
                    if db:
                        df_hd = db.get_dataframe(query_hd)
                        if df_hd is not None and not df_hd.empty:
                            count_query = "SELECT COUNT(*) as total FROM estudiante WHERE id_sede = 3"
                            total_hd = db.get_dataframe(count_query)
                            total_count = total_hd.iloc[0]['total'] if total_hd is not None else 0
                            
                            st.session_state.fragmentos_estudiantes['heredia'] = {
                                'data': df_hd,
                                'total': total_count,
                                'timestamp': datetime.now()
                            }
                        else:
                            st.session_state.fragmentos_estudiantes['heredia'] = {
                                'data': None,
                                'total': 0,
                                'timestamp': datetime.now()
                            }
    
    st.markdown("### Resultados de Fragmentación")
    
    if 'distribuida' in st.session_state.fragmentos_estudiantes:
        dist_data = st.session_state.fragmentos_estudiantes['distribuida']
        st.markdown("#### Consulta - Todos los Estudiantes Unidos")
        
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"Consulta Exitosa - Estudiantes de Sedes: {', '.join(dist_data['sedes'])}")
            st.dataframe(dist_data['data'].head(50), use_container_width=True, hide_index=True)
        
        with col2:
            resumen = dist_data['data'].groupby('sede').agg({
                'estudiante': 'count',
                'matriculas': 'sum'
            }).reset_index()
            resumen.columns = ['sede', 'estudiantes', 'total_matriculas']
            
            st.dataframe(resumen, use_container_width=True, hide_index=True)
            
            fig = px.pie(resumen, values='estudiantes', names='sede',
                       title="Distribución de Estudiantes por Fragmento")
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("#### Estadísticas del Sistema Distribuido")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Estudiantes", len(dist_data['data']))
        with col2:
            st.metric("Sedes Consultadas", len(dist_data['sedes']))
        with col3:
            st.metric("Total Matrículas", dist_data['data']['matriculas'].sum())
        with col4:
            promedio_mat = dist_data['data']['matriculas'].mean()
            st.metric("Matrículas por Estudiante", f"{promedio_mat:.1f}")
    
    fragmentos_orden = [
        ('central', 'Central', '🏛️'),
        ('sancarlos', 'San Carlos', '🏢'), 
        ('heredia', 'Heredia', '🏫')
    ]
    
    for key, nombre, icono in fragmentos_orden:
        if key in st.session_state.fragmentos_estudiantes:
            frag_data = st.session_state.fragmentos_estudiantes[key]
            
            with st.expander(f"{icono} Fragmento {nombre} - Consultado a las {frag_data['timestamp'].strftime('%H:%M:%S')}", expanded=True):
                if frag_data['data'] is not None and not frag_data['data'].empty:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.dataframe(frag_data['data'], use_container_width=True, hide_index=True)
                    with col2:
                        st.metric(f"Total en {nombre}", frag_data['total'])
                        st.metric("Fragmentos Mostrados", len(frag_data['data']))
                else:
                    st.warning(f"No hay estudiantes en {nombre}")
    
    st.markdown("### Ejemplo 2: Cursos y Matrículas por Sede")
    
    if st.button("Limpiar Resultados de Cursos", key="clear_cursos"):
        limpiar_resultados('cursos')
    
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Cursos en Sede Central", key="cursos_central"):
            query_cursos_central = """
                SELECT 
                    c.nombre as curso,
                    car.nombre as carrera,
                    s.nombre as sede,
                    COUNT(m.id_matricula) as estudiantes_matriculados
                FROM curso c
                JOIN carrera car ON c.id_carrera = car.id_carrera
                JOIN sede s ON car.id_sede = s.id_sede
                LEFT JOIN matricula m ON c.id_curso = m.id_curso
                WHERE car.id_sede = 1
                GROUP BY c.id_curso, c.nombre, car.nombre, s.nombre
                ORDER BY estudiantes_matriculados DESC
                LIMIT 20;
            """
            
            with get_db_connection('central') as db:
                if db:
                    df_cursos_central = db.get_dataframe(query_cursos_central)
                    st.session_state.fragmentos_cursos['central'] = {
                        'data': df_cursos_central,
                        'timestamp': datetime.now()
                    }

    with col2:
        if st.button("Cursos en San Carlos", key="cursos_sc"):
            query_cursos_sc = """
                SELECT 
                    c.nombre as curso,
                    car.nombre as carrera,
                    s.nombre as sede,
                    COUNT(m.id_matricula) as estudiantes_matriculados
                FROM curso c
                JOIN carrera car ON c.id_carrera = car.id_carrera
                JOIN sede s ON car.id_sede = s.id_sede
                LEFT JOIN matricula m ON c.id_curso = m.id_curso
                WHERE car.id_sede = 2
                GROUP BY c.id_curso, c.nombre, car.nombre, s.nombre
                ORDER BY estudiantes_matriculados DESC;
            """
            
            with get_db_connection('sancarlos') as db:
                if db:
                    df_cursos_sc = db.get_dataframe(query_cursos_sc)
                    st.session_state.fragmentos_cursos['sancarlos'] = {
                        'data': df_cursos_sc,
                        'timestamp': datetime.now()
                    }
    
    with col3:
        if st.button("Cursos en Heredia", key="cursos_hd"):
            query_cursos_hd = """
                SELECT 
                    c.nombre as curso,
                    car.nombre as carrera,
                    s.nombre as sede,
                    COUNT(m.id_matricula) as estudiantes_matriculados
                FROM curso c
                JOIN carrera car ON c.id_carrera = car.id_carrera
                JOIN sede s ON car.id_sede = s.id_sede
                LEFT JOIN matricula m ON c.id_curso = m.id_curso
                WHERE car.id_sede = 3
                GROUP BY c.id_curso, c.nombre, car.nombre, s.nombre
                ORDER BY estudiantes_matriculados DESC;
            """
            
            with get_db_connection('heredia') as db:
                if db:
                    df_cursos_hd = db.get_dataframe(query_cursos_hd)
                    st.session_state.fragmentos_cursos['heredia'] = {
                        'data': df_cursos_hd,
                        'timestamp': datetime.now()
                    }
    
    if st.session_state.fragmentos_cursos:
        st.markdown("#### Resultados de Cursos por Sede")
        
        for key, nombre, icono in fragmentos_orden:
            if key in st.session_state.fragmentos_cursos:
                curso_data = st.session_state.fragmentos_cursos[key]
                
                with st.expander(f"📖 Cursos en {nombre} - {icono} - Consultado a las {curso_data['timestamp'].strftime('%H:%M:%S')}", expanded=True):
                    if curso_data['data'] is not None and not curso_data['data'].empty:
                        st.dataframe(curso_data['data'], use_container_width=True, hide_index=True)
                    else:
                        st.warning(f"No hay cursos en {nombre}")

with tab3:
    st.header("Fragmentación Vertical - Separación Funcional")
    
    if st.button("Limpiar Resultados Verticales", key="clear_vertical"):
        limpiar_resultados('administrativos')
        limpiar_resultados('academicos')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Fragmento Administrativo (Central)")
        
        if st.button("Ver Datos Administrativos", type="primary", key="admin_data"):
            with st.spinner('Consultando datos administrativos en Central...'):
                planilla_query = """
                    SELECT 
                        p.nombre as profesor,
                        pl.salario,
                        pl.mes,
                        'Planilla' as tipo_dato
                    FROM planilla pl
                    JOIN profesor p ON pl.id_profesor = p.id_profesor
                    ORDER BY pl.mes DESC;
                """
                
                pagare_query = """
                    SELECT 
                        pg.monto,
                        pg.vencimiento,
                        pg.fecha_creacion,
                        'Pagare' as tipo_dato
                    FROM pagare pg
                    ORDER BY pg.vencimiento ASC;
                """
                
                with get_db_connection('central') as db:
                    if db:
                        df_planilla = db.get_dataframe(planilla_query)
                        
                        df_pagare = db.get_dataframe(pagare_query)
                        
                        resumen_admin = """
                            SELECT 'Planillas' as tabla, COUNT(*) as registros FROM planilla
                            UNION ALL
                            SELECT 'Pagarés' as tabla, COUNT(*) as registros FROM pagare;
                        """
                        df_resumen = db.get_dataframe(resumen_admin)
                        
                        # Guardar en session_state
                        st.session_state.datos_administrativos['central'] = {
                            'planillas': df_planilla,
                            'pagares': df_pagare,
                            'resumen': df_resumen,
                            'timestamp': datetime.now()
                        }
    
    with col2:
        st.markdown("### Fragmento Académico (Regionales)")
        
        sede_academica = st.selectbox("Selecciona sede académica:", ["San Carlos", "Heredia"])
        
        if st.button("Ver Datos Académicos", type="primary", key="acad_data"):
            sede_key = 'sancarlos' if sede_academica == "San Carlos" else 'heredia'
            sede_id = 2 if sede_academica == "San Carlos" else 3
            
            with st.spinner(f'Consultando datos académicos en {sede_academica}...'):
                notas_query = """
                    SELECT 
                        e.nombre as estudiante,
                        c.nombre as curso,
                        n.nota,
                        'Academico' as tipo_dato
                    FROM nota n
                    JOIN matricula m ON n.id_matricula = m.id_matricula
                    JOIN estudiante e ON m.id_estudiante = e.id_estudiante
                    JOIN curso c ON m.id_curso = c.id_curso
                    ORDER BY n.fecha_creacion DESC;
                """
                
                asistencia_query = """
                    SELECT 
                        COUNT(*) as total_registros,
                        SUM(CASE WHEN presente = 1 THEN 1 ELSE 0 END) as presentes,
                        SUM(CASE WHEN presente = 0 THEN 1 ELSE 0 END) as ausentes,
                        ROUND(SUM(CASE WHEN presente = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as porcentaje_asistencia
                    FROM asistencia;
                """
                
                resumen_acad = """
                    SELECT 'Estudiantes' as tabla, COUNT(*) as registros FROM estudiante
                    UNION ALL
                    SELECT 'Matrículas' as tabla, COUNT(*) as registros FROM matricula
                    UNION ALL
                    SELECT 'Notas' as tabla, COUNT(*) as registros FROM nota
                    UNION ALL
                    SELECT 'Asistencias' as tabla, COUNT(*) as registros FROM asistencia;
                """
                
                with get_db_connection(sede_key) as db:
                    if db:
                        df_notas = db.get_dataframe(notas_query)
                        df_asistencia = db.get_dataframe(asistencia_query)
                        df_resumen_acad = db.get_dataframe(resumen_acad)
                        
                        st.session_state.datos_academicos[sede_key] = {
                            'notas': df_notas,
                            'asistencia': df_asistencia,
                            'resumen': df_resumen_acad,
                            'sede_nombre': sede_academica,
                            'timestamp': datetime.now()
                        }
    
    if 'central' in st.session_state.datos_administrativos:
        admin_data = st.session_state.datos_administrativos['central']
        
        st.markdown("### Datos Administrativos")
        with st.expander(f"Datos Administrativos - Central - Consultado a las {admin_data['timestamp'].strftime('%H:%M:%S')}", expanded=True):
            
            if admin_data['planillas'] is not None and not admin_data['planillas'].empty:
                st.markdown("**Planillas:**")
                st.dataframe(admin_data['planillas'], use_container_width=True, hide_index=True)
            
            if admin_data['pagares'] is not None and not admin_data['pagares'].empty:
                st.markdown("**Pagarés:**")
                st.dataframe(admin_data['pagares'], use_container_width=True, hide_index=True)
            
            if admin_data['resumen'] is not None:
                st.markdown("**Resumen Administrativo:**")
                st.dataframe(admin_data['resumen'], use_container_width=True, hide_index=True)
    
    for sede_key in ['sancarlos', 'heredia']:
        if sede_key in st.session_state.datos_academicos:
            acad_data = st.session_state.datos_academicos[sede_key]
            icono = '🏢' if sede_key == 'sancarlos' else '🏫'
            
            st.markdown(f"### Datos Académicos - {acad_data['sede_nombre']}")
            with st.expander(f"{icono} Datos Académicos - {acad_data['sede_nombre']} - Consultado a las {acad_data['timestamp'].strftime('%H:%M:%S')}", expanded=True):
                
                if acad_data['notas'] is not None and not acad_data['notas'].empty:
                    st.markdown(f"**Notas en {acad_data['sede_nombre']}:**")
                    st.dataframe(acad_data['notas'], use_container_width=True, hide_index=True)
                
                if acad_data['asistencia'] is not None and not acad_data['asistencia'].empty:
                    st.markdown(f"**Resumen Asistencia:**")
                    st.dataframe(acad_data['asistencia'], use_container_width=True, hide_index=True)
                
                if acad_data['resumen'] is not None:
                    st.markdown(f"**Resumen {acad_data['sede_nombre']}:**")
                    st.dataframe(acad_data['resumen'], use_container_width=True, hide_index=True)

with tab4:
    st.header("Fragmentación Derivada - Datos que Siguen a Otros")
    
    if st.button("🗑️ Limpiar Resultados Derivada", key="clear_derivada"):
        limpiar_resultados('derivada')
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        sede_derivada = st.selectbox("Sede para demostración:", ["Central", "San Carlos", "Heredia"])
    
    with col2:
        st.info(f"Demostrando fragmentación derivada en **{sede_derivada}**")
    
    if st.button("Demostrar Fragmentación Derivada", type="primary", key="demo_derivada"):
        sede_mapeo = {
            "Central": {"key": "central", "id": 1},
            "San Carlos": {"key": "sancarlos", "id": 2},
            "Heredia": {"key": "heredia", "id": 3}
        }

        sede_info = sede_mapeo.get(sede_derivada, {"key": "desconocido", "id": 0})
        sede_key = sede_info["key"]
        sede_id = sede_info["id"]

        with st.spinner(f'Analizando fragmentación derivada en {sede_derivada}...'):
            try:
                query_derivada = """
                    SELECT 
                        e.nombre as estudiante,
                        e.id_sede,
                        s.nombre as sede,
                        COUNT(DISTINCT m.id_matricula) as total_matriculas,
                        COUNT(DISTINCT n.id_nota) as total_notas,
                        COUNT(DISTINCT a.id_asistencia) as total_asistencias,
                        AVG(n.nota) as promedio_notas
                    FROM estudiante e
                    JOIN sede s ON e.sede_actual = s.id_sede
                    LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
                    LEFT JOIN nota n ON m.id_matricula = n.id_matricula
                    LEFT JOIN asistencia a ON m.id_matricula = a.id_matricula
                    WHERE e.sede_actual = {}
                    GROUP BY e.id_estudiante, e.nombre, e.id_sede, s.nombre
                    ORDER BY total_matriculas DESC
                    LIMIT 20;
                """.format(sede_id)
                
                verificacion_query = f"""
                    SELECT 
                        'Todos los datos están en {sede_derivada}' as verificacion,
                        COUNT(DISTINCT e.id_estudiante) as estudiantes,
                        COUNT(DISTINCT m.id_matricula) as matriculas_relacionadas,
                        COUNT(DISTINCT n.id_nota) as notas_relacionadas,
                        COUNT(DISTINCT a.id_asistencia) as asistencias_relacionadas
                    FROM estudiante e
                    LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
                    LEFT JOIN nota n ON m.id_matricula = n.id_matricula
                    LEFT JOIN asistencia a ON m.id_matricula = a.id_matricula
                    WHERE e.sede_actual = {sede_id};
                """
                
                with get_db_connection(sede_key) as db:
                    if db:
                        df_derivada = db.get_dataframe(query_derivada)
                        df_verificacion = db.get_dataframe(verificacion_query)
                        
                        st.session_state.fragmentacion_derivada[sede_derivada] = {
                            'data': df_derivada,
                            'verificacion': df_verificacion,
                            'sede_id': sede_id,
                            'timestamp': datetime.now()
                        }
                        
            except Exception as e:
                st.error(f"❌ Error en demostración de fragmentación derivada: {str(e)}")
    
    if st.session_state.fragmentacion_derivada:
        st.markdown("### Resultados de Fragmentación Derivada")
        
        for sede_nombre, data in st.session_state.fragmentacion_derivada.items():
            icono_map = {"Central": "🏛️", "San Carlos": "🏢", "Heredia": "🏫"}
            icono = icono_map.get(sede_nombre, "📍")
            
            with st.expander(f"{icono} Fragmentación Derivada - {sede_nombre} - Consultado a las {data['timestamp'].strftime('%H:%M:%S')}", expanded=True):
                if data['data'] is not None and not data['data'].empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Datos Relacionados por Estudiante")
                        st.dataframe(data['data'], use_container_width=True, hide_index=True)
                    
                    with col2:
                        st.markdown("#### Análisis de Fragmentación Derivada")
                        
                        total_estudiantes = len(data['data'])
                        total_matriculas = data['data']['total_matriculas'].sum()
                        total_notas = data['data']['total_notas'].sum()
                        total_asistencias = data['data']['total_asistencias'].sum()
                        
                        st.metric("Estudiantes en Fragmento", total_estudiantes)
                        st.metric("Matrículas Derivadas", total_matriculas)
                        st.metric("Notas Derivadas", total_notas) 
                        st.metric("Asistencias Derivadas", total_asistencias)
                    
                    #if data['verificacion'] is not None and not data['verificacion'].empty:
                    #    st.markdown("#### Verificación de Integridad Derivada")
                    #    st.dataframe(data['verificacion'], use_container_width=True, hide_index=True)
                else:
                    st.warning(f"No hay datos para mostrar fragmentación derivada en {sede_nombre}")


st.markdown("---")