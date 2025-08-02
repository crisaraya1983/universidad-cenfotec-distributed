"""
Página de demostración de Fragmentación - 
Esta página demuestra los conceptos de fragmentación de bases de datos distribuidas
usando ejemplos que muestran cómo los datos están DISTRIBUIDOS entre sedes.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime

# Importar utilidades
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG, COLORS, get_sede_info
from utils.db_connections import get_db_connection, execute_distributed_query

# Configuración de la página
st.set_page_config(
    page_title="Fragmentación - Sistema Cenfotec",
    page_icon="📊",
    layout="wide"
)

# Título de la página
st.title("📊 Fragmentación de Bases de Datos Distribuidas - Universidad Cenfotec")

# Introducción educativa CORREGIDA
st.markdown("""
## 🎯 **¿Qué es la Fragmentación en Bases de Datos Distribuidas?**

La **fragmentación** es dividir los datos de una tabla lógica en **pedazos físicamente separados** que se almacenan 
en diferentes ubicaciones. **Cada fragmento contiene PARTE de los datos totales** del sistema.
""")

# Tabs para diferentes tipos de fragmentación
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Conceptos Fundamentales", 
    "↔️ Fragmentación Horizontal", 
    "↕️ Fragmentación Vertical", 
    "🔗 Fragmentación Derivada"
])

with tab1:
    st.header("📋 Conceptos Fundamentales de Fragmentación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 **Fragmentación Horizontal** ↔️
        
        **Definición:** Dividir una tabla por **filas** según algún criterio.
        
        **Datos:**
        - `estudiante` WHERE `id_sede = 1` → Central
        - `estudiante` WHERE `id_sede = 2` → San Carlos
        - `estudiante` WHERE `id_sede = 3` → Heredia  
        - **Cada sede tiene PARTE de los estudiantes totales**
        
        ✅ **Beneficio:** Consultas locales más rápidas  
        ❗ **Consulta global:** Requiere UNIR datos de múltiples sedes
        """)
        
        st.markdown("""
        ### 🎯 **Fragmentación Derivada** 🔗
        
        **Definición:** Una tabla se fragmenta basándose en cómo está fragmentada otra tabla relacionada.
        
        **Datos:**
        - `matricula` sigue a `estudiante` 
        - Si estudiante está en SC → sus matrículas están en SC
        - Si estudiante está en HD → sus matrículas están en HD
        
        ✅ **Beneficio:** Mantiene datos relacionados juntos
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 **Fragmentación Vertical** ↕️
        
        **Definición:** Dividir por **tipo de función** o **columnas**.
        
        **Datos:**
        - **Central:** Datos administrativos (`planilla`, `pagare`)
        - **Regionales:** Solo datos académicos (`matricula`, `nota`, `asistencia`)
        
        ✅ **Beneficio:** Separación funcional y seguridad  
        ❗ **Consulta mixta:** Requiere datos de Central + Regional
        """)
        
    
    # Diagrama de fragmentación
    st.markdown("### 📐 Visualización de Fragmentación")
    
    fig = go.Figure()
    
    # Tabla lógica (concepto)
    fig.add_trace(go.Scatter(
        x=[0], y=[4],
        mode='markers+text',
        marker=dict(size=120, color='gold'),
        text=['<b>TABLA LÓGICA</b><br>📊 ESTUDIANTES<br>🔢<br>💭 Vista conceptual'],
        textposition="bottom center",
        name='Concepto Lógico'
    ))
    
    # Fragmentos físicos
    fig.add_trace(go.Scatter(
        x=[-3], y=[1],
        mode='markers+text',
        marker=dict(size=100, color=COLORS['secondary']),
        text=['<b>FRAGMENTO SC</b><br>👨‍🎓<br>🏷️ id_sede = 2<br>📍 Físico en SC'],
        textposition="bottom center",
        name='Fragmento San Carlos'
    ))
    
    fig.add_trace(go.Scatter(
        x=[3], y=[1],
        mode='markers+text',
        marker=dict(size=100, color=COLORS['success']),
        text=['<b>FRAGMENTO HD</b><br>👨‍🎓<br>🏷️ id_sede = 3<br>📍 Físico en HD'],
        textposition="bottom center",
        name='Fragmento Heredia'
    ))
    
    # Flechas de fragmentación
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
    st.header("↔️ Fragmentación Horizontal - Datos Distribuidos por Filas")
    
    st.markdown("""
    ## 🎯 **Concepto Clave de Fragmentación Horizontal**
    
    La tabla `estudiante` está **dividida por filas** según `id_sede`. Cada sede física 
    almacena **solo una parte** de todos los estudiantes del sistema.
    
    🔑 **Para obtener TODOS los estudiantes** necesitas consultar **múltiples sedes**.
    """)
    
    # Ejemplo 1: Demostrar fragmentación
    st.markdown("### 🧪 Ejemplo 1: Estudiantes Fragmentados por Sede")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔍 Ver Fragmento: Central", type="primary"):
            with st.spinner('Consultando fragmento en Sede Central...'):
                query_sc = """
                    SELECT 
                        e.nombre as estudiante,
                        e.email,
                        s.nombre as sede,
                        e.id_sede
                    FROM estudiante e
                    JOIN sede s ON e.id_sede = s.id_sede
                    WHERE e.id_sede = 1
                    ORDER BY e.nombre
                    LIMIT 20;
                """
                
                with get_db_connection('central') as db:
                    if db:
                        df_sc = db.get_dataframe(query_sc)
                        if df_sc is not None and not df_sc.empty:
                            st.success(f"✅ Fragmento Central: {len(df_sc)} estudiantes")
                            st.dataframe(df_sc, use_container_width=True, hide_index=True)
                            
                            # Contar total en San Carlos
                            count_query = "SELECT COUNT(*) as total FROM estudiante WHERE id_sede = 1"
                            total_sc = db.get_dataframe(count_query)
                            if total_sc is not None:
                                st.metric("Total Estudiantes en Sede Central", total_sc.iloc[0]['total'])
                        else:
                            st.warning("No hay estudiantes en Sede Central")
    
    with col2:
        if st.button("🔍 Ver Fragmento: San Carlos", type="primary"):
            with st.spinner('Consultando fragmento en San Carlos...'):
                query_sc = """
                    SELECT 
                        e.nombre as estudiante,
                        e.email,
                        s.nombre as sede,
                        e.id_sede
                    FROM estudiante e
                    JOIN sede s ON e.id_sede = s.id_sede
                    WHERE e.id_sede = 2
                    ORDER BY e.nombre
                    LIMIT 20;
                """
                
                with get_db_connection('sancarlos') as db:
                    if db:
                        df_sc = db.get_dataframe(query_sc)
                        if df_sc is not None and not df_sc.empty:
                            st.success(f"✅ Fragmento San Carlos: {len(df_sc)} estudiantes")
                            st.dataframe(df_sc, use_container_width=True, hide_index=True)
                            
                            # Contar total en San Carlos
                            count_query = "SELECT COUNT(*) as total FROM estudiante WHERE id_sede = 2"
                            total_sc = db.get_dataframe(count_query)
                            if total_sc is not None:
                                st.metric("Total Estudiantes en San Carlos", total_sc.iloc[0]['total'])
                        else:
                            st.warning("No hay estudiantes en San Carlos")
    
    with col3:
        if st.button("🔍 Ver Fragmento: Heredia", type="primary"):
            with st.spinner('Consultando fragmento en Heredia...'):
                query_hd = """
                    SELECT 
                        e.nombre as estudiante,
                        e.email,
                        s.nombre as sede,
                        e.id_sede
                    FROM estudiante e
                    JOIN sede s ON e.id_sede = s.id_sede
                    WHERE e.id_sede = 3
                    ORDER BY e.nombre
                    LIMIT 20;
                """
                
                with get_db_connection('heredia') as db:
                    if db:
                        df_hd = db.get_dataframe(query_hd)
                        if df_hd is not None and not df_hd.empty:
                            st.success(f"✅ Fragmento Heredia: {len(df_hd)} estudiantes")
                            st.dataframe(df_hd, use_container_width=True, hide_index=True)
                            
                            # Contar total en Heredia
                            count_query = "SELECT COUNT(*) as total FROM estudiante WHERE id_sede = 3"
                            total_hd = db.get_dataframe(count_query)
                            if total_hd is not None:
                                st.metric("Total Estudiantes en Heredia", total_hd.iloc[0]['total'])
                        else:
                            st.warning("No hay estudiantes en Heredia")
    
    # Ejemplo 2: Consulta distribuida (fragmentación en acción)
    st.markdown("### 🌐 Ejemplo 2: Consulta Distribuida - Todos los Estudiantes")
    st.markdown("""
    **💡 Concepto:** Para obtener **TODOS** los estudiantes del sistema, necesitas consultar 
    **todas sedes** y **unir** los resultados. Esto demuestra que los datos están **fragmentados**.
    """)
    
    if st.button("🔄 Ejecutar Consulta Distribuida: TODOS los Estudiantes"):
        with st.spinner('Consultando TODAS las sedes para unir fragmentos...'):
            try:
                estudiantes_distribuidos = []
                sedes_consultadas = []
                
                # Consulta para cada sede
                query_fragmento = """
                    SELECT 
                        e.nombre as estudiante,
                        s.nombre as sede,
                        e.id_sede,
                        COUNT(m.id_matricula) as matriculas
                    FROM estudiante e
                    JOIN sede s ON e.id_sede = s.id_sede
                    LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
                    GROUP BY e.id_estudiante, e.nombre, s.nombre, e.id_sede
                    ORDER BY e.nombre;
                """
                # Central
                with get_db_connection('central') as db:
                    if db:
                        df_hd = db.get_dataframe(query_fragmento)
                        if df_hd is not None and not df_hd.empty:
                            estudiantes_distribuidos.append(df_hd)
                            sedes_consultadas.append("Central")

                # San Carlos
                with get_db_connection('sancarlos') as db:
                    if db:
                        df_sc = db.get_dataframe(query_fragmento)
                        if df_sc is not None and not df_sc.empty:
                            estudiantes_distribuidos.append(df_sc)
                            sedes_consultadas.append("San Carlos")
                
                # Heredia
                with get_db_connection('heredia') as db:
                    if db:
                        df_hd = db.get_dataframe(query_fragmento)
                        if df_hd is not None and not df_hd.empty:
                            estudiantes_distribuidos.append(df_hd)
                            sedes_consultadas.append("Heredia")
                
                if estudiantes_distribuidos:
                    # Unir todos los fragmentos
                    df_todos = pd.concat(estudiantes_distribuidos, ignore_index=True)
                    
                    st.success(f"✅ Consulta Distribuida Exitosa - Consultadas: {', '.join(sedes_consultadas)}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### 📊 Datos Unificados")
                        st.dataframe(df_todos.head(15), use_container_width=True, hide_index=True)
                    
                    with col2:
                        st.markdown("#### 📈 Análisis de Fragmentación")
                        resumen = df_todos.groupby('sede').agg({
                            'estudiante': 'count',
                            'matriculas': 'sum'
                        }).reset_index()
                        resumen.columns = ['sede', 'estudiantes', 'total_matriculas']
                        
                        st.dataframe(resumen, use_container_width=True, hide_index=True)
                        
                        # Gráfico de distribución
                        fig = px.pie(resumen, values='estudiantes', names='sede',
                                   title="Distribución de Estudiantes por Fragmento")
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Estadísticas globales
                    st.markdown("#### 🎯 Estadísticas del Sistema Distribuido")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Estudiantes", len(df_todos))
                    with col2:
                        st.metric("Sedes Consultadas", len(sedes_consultadas))
                    with col3:
                        st.metric("Total Matrículas", df_todos['matriculas'].sum())
                    with col4:
                        promedio_mat = df_todos['matriculas'].mean()
                        st.metric("Matrículas por Estudiante", f"{promedio_mat:.1f}")
                
            except Exception as e:
                st.error(f"❌ Error en consulta distribuida: {str(e)}")
    
    # Ejemplo 3: Fragmentación por curso/materia
    st.markdown("### 📚 Ejemplo 3: Cursos y Matrículas por Sede")
    st.markdown("""
    **💡 Concepto:** Los cursos y matrículas también siguen la fragmentación por sede.
    """)
    
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📖 Cursos en Sede Central"):
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
                WHERE car.id_sede = 1
                GROUP BY c.id_curso, c.nombre, car.nombre, s.nombre
                ORDER BY estudiantes_matriculados DESC
                LIMIT 20;
            """
            
            with get_db_connection('central') as db:
                if db:
                    df_cursos_sc = db.get_dataframe(query_cursos_sc)
                    if df_cursos_sc is not None and not df_cursos_sc.empty:
                        st.dataframe(df_cursos_sc, use_container_width=True, hide_index=True)

    with col2:
        if st.button("📖 Cursos en San Carlos"):
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
                ORDER BY estudiantes_matriculados DESC
                LIMIT 20;
            """
            
            with get_db_connection('sancarlos') as db:
                if db:
                    df_cursos_sc = db.get_dataframe(query_cursos_sc)
                    if df_cursos_sc is not None and not df_cursos_sc.empty:
                        st.dataframe(df_cursos_sc, use_container_width=True, hide_index=True)
    
    
    with col3:
        if st.button("📖 Cursos en Heredia"):
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
                ORDER BY estudiantes_matriculados DESC
                LIMIT 20;
            """
            
            with get_db_connection('heredia') as db:
                if db:
                    df_cursos_hd = db.get_dataframe(query_cursos_hd)
                    if df_cursos_hd is not None and not df_cursos_hd.empty:
                        st.dataframe(df_cursos_hd, use_container_width=True, hide_index=True)

with tab3:
    st.header("↕️ Fragmentación Vertical - Separación Funcional")
    
    st.markdown("""
    ## 🎯 **Concepto Clave de Fragmentación Vertical**
    
    Los datos se separan por **función/tipo** en diferentes ubicaciones:
    - **Central:** Solo datos administrativos (`planilla`, `pagare`) 
    - **Regionales:** Solo operaciones académicas (`matricula`, `nota`, `asistencia`)
    
    🔑 **Para operaciones mixtas** necesitas consultar **múltiples tipos de sedes**.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏛️ Fragmento Administrativo (Central)")
        
        if st.button("💰 Ver Datos Administrativos", type="primary"):
            with st.spinner('Consultando datos administrativos en Central...'):
                # Planillas
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
                
                # Pagarés
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
                        # Mostrar planillas
                        df_planilla = db.get_dataframe(planilla_query)
                        if df_planilla is not None and not df_planilla.empty:
                            st.markdown("**📊 Planillas (Solo en Central):**")
                            st.dataframe(df_planilla, use_container_width=True, hide_index=True)
                        
                        # Mostrar pagarés
                        df_pagare = db.get_dataframe(pagare_query)
                        if df_pagare is not None and not df_pagare.empty:
                            st.markdown("**📄 Pagarés (Solo en Central):**")
                            st.dataframe(df_pagare, use_container_width=True, hide_index=True)
                        
                        # Resumen
                        resumen_admin = """
                            SELECT 'Planillas' as tabla, COUNT(*) as registros FROM planilla
                            UNION ALL
                            SELECT 'Pagarés' as tabla, COUNT(*) as registros FROM pagare;
                        """
                        df_resumen = db.get_dataframe(resumen_admin)
                        if df_resumen is not None:
                            st.markdown("**📈 Resumen Administrativo:**")
                            st.dataframe(df_resumen, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### 🎓 Fragmento Académico (Regionales)")
        
        sede_academica = st.selectbox("Selecciona sede académica:", ["San Carlos", "Heredia"])
        
        if st.button("📚 Ver Datos Académicos", type="primary"):
            sede_key = 'sancarlos' if sede_academica == "San Carlos" else 'heredia'
            sede_id = 2 if sede_academica == "San Carlos" else 3
            
            with st.spinner(f'Consultando datos académicos en {sede_academica}...'):
                # Notas recientes
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
                
                # Asistencias
                asistencia_query = """
                    SELECT 
                        COUNT(*) as total_registros,
                        SUM(CASE WHEN presente = 1 THEN 1 ELSE 0 END) as presentes,
                        SUM(CASE WHEN presente = 0 THEN 1 ELSE 0 END) as ausentes,
                        ROUND(SUM(CASE WHEN presente = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as porcentaje_asistencia
                    FROM asistencia;
                """
                
                with get_db_connection(sede_key) as db:
                    if db:
                        # Mostrar notas
                        df_notas = db.get_dataframe(notas_query)
                        if df_notas is not None and not df_notas.empty:
                            st.markdown(f"**📝 Notas en {sede_academica}:**")
                            st.dataframe(df_notas, use_container_width=True, hide_index=True)
                        
                        # Mostrar asistencia
                        df_asistencia = db.get_dataframe(asistencia_query)
                        if df_asistencia is not None and not df_asistencia.empty:
                            st.markdown(f"**📅 Resumen Asistencia:**")
                            st.dataframe(df_asistencia, use_container_width=True, hide_index=True)
                        
                        # Resumen académico
                        resumen_acad = """
                            SELECT 'Estudiantes' as tabla, COUNT(*) as registros FROM estudiante
                            UNION ALL
                            SELECT 'Matrículas' as tabla, COUNT(*) as registros FROM matricula
                            UNION ALL
                            SELECT 'Notas' as tabla, COUNT(*) as registros FROM nota
                            UNION ALL
                            SELECT 'Asistencias' as tabla, COUNT(*) as registros FROM asistencia;
                        """
                        df_resumen_acad = db.get_dataframe(resumen_acad)
                        if df_resumen_acad is not None:
                            st.markdown(f"**📊 Resumen {sede_academica}:**")
                            st.dataframe(df_resumen_acad, use_container_width=True, hide_index=True)


with tab4:
    st.header("🔗 Fragmentación Derivada - Datos que Siguen a Otros")
    
    st.markdown("""
    ## 🎯 **Concepto de Fragmentación Derivada**
    
    Cuando una tabla se fragmenta **basándose en cómo está fragmentada otra tabla relacionada**.
    
    **Datos:**
    - `estudiante` está fragmentado por `id_sede`
    - `matricula` se fragmenta siguiendo al `estudiante` 
    - `nota` se fragmenta siguiendo a `matricula`
    - `asistencia` se fragmenta siguiendo a `matricula`
    
    🔑 **Resultado:** Si un estudiante está en San Carlos, **todas** sus matrículas, notas y asistencias también están en San Carlos.
    """)
    
    # Selector de sede para demostración
    col1, col2 = st.columns([1, 3])
    
    with col1:
        sede_derivada = st.selectbox("Sede para demostración:", ["Central", "San Carlos", "Heredia"])
    
    with col2:
        st.info(f"📍 Demostrando fragmentación derivada en **{sede_derivada}**")
    
    if st.button("🔄 Demostrar Fragmentación Derivada", type="primary"):
        sede_mapeo = {
            "Central": {"key": "central", "id": 1},
            "San Carlos": {"key": "sancarlos", "id": 2},
            "Heredia": {"key": "heredia", "id": 3}
        }

        # Obtener valores según sede_derivada
        sede_info = sede_mapeo.get(sede_derivada, {"key": "desconocido", "id": 0})
        sede_key = sede_info["key"]
        sede_id = sede_info["id"]

        
        with st.spinner(f'Analizando fragmentación derivada en {sede_derivada}...'):
            try:
                # Consulta que muestra la cadena de fragmentación derivada
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
                    JOIN sede s ON e.id_sede = s.id_sede
                    LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
                    LEFT JOIN nota n ON m.id_matricula = n.id_matricula
                    LEFT JOIN asistencia a ON m.id_matricula = a.id_matricula
                    WHERE e.id_sede = {}
                    GROUP BY e.id_estudiante, e.nombre, e.id_sede, s.nombre
                    ORDER BY total_matriculas DESC
                    LIMIT 20;
                """.format(sede_id)
                
                with get_db_connection(sede_key) as db:
                    if db:
                        df_derivada = db.get_dataframe(query_derivada)
                        if df_derivada is not None and not df_derivada.empty:
                            st.success(f"✅ Fragmentación derivada demostrada en {sede_derivada}")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("#### 📊 Datos Relacionados por Estudiante")
                                st.dataframe(df_derivada, use_container_width=True, hide_index=True)
                            
                            with col2:
                                st.markdown("#### 📈 Análisis de Fragmentación Derivada")
                                
                                # Estadísticas
                                total_estudiantes = len(df_derivada)
                                total_matriculas = df_derivada['total_matriculas'].sum()
                                total_notas = df_derivada['total_notas'].sum()
                                total_asistencias = df_derivada['total_asistencias'].sum()
                                
                                st.metric("Estudiantes en Fragment", total_estudiantes)
                                st.metric("Matrículas Derivadas", total_matriculas)
                                st.metric("Notas Derivadas", total_notas) 
                                st.metric("Asistencias Derivadas", total_asistencias)
                                
                                # Gráfico de distribución
                                fig = px.histogram(df_derivada, x='total_matriculas', 
                                                 title=f"Distribución de Matrículas por Estudiante - {sede_derivada}")
                                st.plotly_chart(fig, use_container_width=True)
                            
                            # Verificación de integridad
                            st.markdown("#### ✅ Verificación de Integridad Derivada")
                            
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
                                WHERE e.id_sede = {sede_id};
                            """
                            
                            df_verificacion = db.get_dataframe(verificacion_query)
                            if df_verificacion is not None and not df_verificacion.empty:
                                st.dataframe(df_verificacion, use_container_width=True, hide_index=True)
                                
                                st.success(f"""
                                ✅ **Fragmentación Derivada Confirmada:**
                                - Todos los estudiantes de {sede_derivada} están en esta sede
                                - Todas sus matrículas están en la misma sede
                                - Todas sus notas están en la misma sede  
                                - Todas sus asistencias están en la misma sede
                                
                                🔑 **Beneficio:** Consultas completamente locales sin dependencias externas
                                """)
                        else:
                            st.warning(f"No hay datos para mostrar fragmentación derivada en {sede_derivada}")
                            
            except Exception as e:
                st.error(f"❌ Error en demostración de fragmentación derivada: {str(e)}")
    
    # Ejemplo de consulta que NO requiere múltiples sedes (gracias a fragmentación derivada)
    st.markdown("### 🎯 Ejemplo: Consulta Completamente Local")
    st.markdown("""
    **💡 Beneficio de la Fragmentación Derivada:** Puedes obtener información completa de un estudiante 
    consultando **solo una sede** porque todos sus datos relacionados están en la misma ubicación.
    """)
    
    sede_consulta = st.selectbox("Selecciona sede para consulta local:", ["San Carlos", "Heredia"], key="consulta_local")
    
    if st.button("📋 Ejecutar Consulta Completamente Local"):
        sede_key = 'sancarlos' if sede_consulta == "San Carlos" else 'heredia'
        sede_id = 2 if sede_consulta == "San Carlos" else 3
        
        query_local = f"""
            SELECT 
                e.nombre as estudiante,
                c.nombre as curso,
                n.nota,
                CASE WHEN n.nota >= 70 THEN 'Aprobado' ELSE 'Reprobado' END as estado,
                a.fecha as ultima_clase,
                CASE WHEN a.presente = 1 THEN 'Presente' ELSE 'Ausente' END as asistio
            FROM estudiante e
            JOIN matricula m ON e.id_estudiante = m.id_estudiante
            JOIN curso c ON m.id_curso = c.id_curso
            LEFT JOIN nota n ON m.id_matricula = n.id_matricula
            LEFT JOIN asistencia a ON m.id_matricula = a.id_matricula
            WHERE e.id_sede = {sede_id}
            ORDER BY e.nombre, c.nombre
            LIMIT 40;
        """
        
        with get_db_connection(sede_key) as db:
            if db:
                df_local = db.get_dataframe(query_local)
                if df_local is not None and not df_local.empty:
                    st.success(f"✅ Consulta LOCAL exitosa en {sede_consulta} - Sin necesidad de consultar otras sedes")
                    st.dataframe(df_local, use_container_width=True, hide_index=True)
                    
                    st.info(f"""
                    🔑 **Fragmentación Derivada en Acción:**
                    - Consultamos solo la base de datos de {sede_consulta}
                    - Obtuvimos datos completos: estudiante + curso + nota + asistencia
                    - No necesitamos consultar ninguna otra sede
                    - Rendimiento optimizado por localidad de datos
                    """)

# Footer con resumen de conceptos
st.markdown("---")
st.markdown("## 📚 Resumen de Conceptos de Fragmentación")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### ↔️ **Horizontal**
    - División por **filas**
    - Criterio: `id_sede`
    - Ejemplo: Estudiantes por sede
    - Beneficio: Localidad geográfica
    """)

with col2:
    st.markdown("""
    ### ↕️ **Vertical** 
    - División por **función**
    - Central: Admin / Regional: Académico
    - Ejemplo: Planillas vs Matrículas
    - Beneficio: Separación funcional
    """)

with col3:
    st.markdown("""
    ### 🔗 **Derivada**
    - Sigue a tabla relacionada
    - Matrículas → Estudiantes
    - Notas → Matrículas
    - Beneficio: Integridad local
    """)

st.markdown(
    f"<p style='text-align: center; color: gray; font-size: 12px;'>Conceptos de Fragmentación Correctos | Sistema Cenfotec | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
    unsafe_allow_html=True
)