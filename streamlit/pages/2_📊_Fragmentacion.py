"""
Página de demostración de Fragmentación
Esta página muestra cómo los datos están fragmentados horizontal, vertical y mixta
en el sistema distribuido de la Universidad Cenfotec.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
st.title("📊 Demostración de Fragmentación de Datos")

# Introducción educativa
st.markdown("""
La **fragmentación** es una técnica en bases de datos distribuidas que consiste en dividir 
las tablas en partes más pequeñas que se almacenan en diferentes nodos. Esto mejora el rendimiento 
y la escalabilidad del sistema.
""")

# Tabs para diferentes tipos de fragmentación
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Conceptos", 
    "↔️ Fragmentación Horizontal", 
    "↕️ Fragmentación Vertical", 
    "🔀 Fragmentación Mixta"
])

with tab1:
    st.header("Conceptos de Fragmentación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Tipos de Fragmentación
        
        **1. Fragmentación Horizontal** ↔️
        - Divide una tabla por **filas**
        - Cada fragmento contiene un subconjunto de tuplas
        - Ejemplo: Estudiantes por sede geográfica
        - Beneficio: Datos locales más accesibles
        
        **2. Fragmentación Vertical** ↕️
        - Divide una tabla por **columnas**
        - Cada fragmento contiene diferentes atributos
        - Ejemplo: Separar datos sensibles de públicos
        - Beneficio: Seguridad y optimización de acceso
        """)
    
    with col2:
        st.markdown("""
        ### 🔧 Implementación en Cenfotec
        
        **3. Fragmentación Mixta** 🔀
        - Combina horizontal y vertical
        - Mayor flexibilidad en la distribución
        - Ejemplo: Pagos por sede y tipo
        
        **4. Fragmentación Derivada** 🔗
        - Basada en la fragmentación de otra tabla
        - Mantiene integridad referencial
        - Ejemplo: Notas siguen a estudiantes
        """)
    
    # Diagrama visual de fragmentación
    st.markdown("### 📐 Visualización de la Arquitectura")
    
    # Crear un diagrama simple con Plotly
    fig = go.Figure()
    
    # Nodo Central
    fig.add_trace(go.Scatter(
        x=[0], y=[2],
        mode='markers+text',
        marker=dict(size=80, color=COLORS['primary']),
        text=['<b>SEDE CENTRAL</b><br>Planillas<br>Pagarés<br>Datos Maestros'],
        textposition="bottom center",
        name='Central'
    ))
    
    # Nodo San Carlos
    fig.add_trace(go.Scatter(
        x=[-2], y=[0],
        mode='markers+text',
        marker=dict(size=80, color=COLORS['secondary']),
        text=['<b>SAN CARLOS</b><br>Estudiantes SC<br>Matrículas SC<br>Notas SC'],
        textposition="bottom center",
        name='San Carlos'
    ))
    
    # Nodo Heredia
    fig.add_trace(go.Scatter(
        x=[2], y=[0],
        mode='markers+text',
        marker=dict(size=80, color=COLORS['success']),
        text=['<b>HEREDIA</b><br>Estudiantes HD<br>Matrículas HD<br>Notas HD'],
        textposition="bottom center",
        name='Heredia'
    ))
    
    # Conexiones
    fig.add_trace(go.Scatter(
        x=[0, -2, None, 0, 2],
        y=[2, 0, None, 2, 0],
        mode='lines',
        line=dict(width=2, color='gray', dash='dash'),
        showlegend=False
    ))
    
    fig.update_layout(
        title="Distribución de Datos por Sede",
        showlegend=True,
        height=400,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("↔️ Fragmentación Horizontal")
    st.markdown("""
    La fragmentación horizontal divide las tablas por **filas** según un criterio específico.
    En nuestro sistema, los estudiantes están fragmentados por sede geográfica.
    """)
    
    # Mostrar distribución de estudiantes
    st.subheader("👥 Distribución de Estudiantes por Sede")
    
    # Obtener datos de cada sede
    estudiantes_por_sede = []
    
    for sede in ['sancarlos', 'heredia']:
        with get_db_connection(sede) as db:
            if db:
                query = """
                SELECT 
                    s.nombre as sede,
                    COUNT(DISTINCT e.id_estudiante) as total_estudiantes,
                    COUNT(DISTINCT m.id_matricula) as total_matriculas,
                    COUNT(DISTINCT p.id_pago) as total_pagos
                FROM estudiante e
                JOIN sede s ON e.id_sede = s.id_sede
                LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
                LEFT JOIN pago p ON e.id_estudiante = p.id_estudiante
                GROUP BY s.nombre
                """
                result = db.execute_query(query)
                if result:
                    estudiantes_por_sede.extend(result)
    
    if estudiantes_por_sede:
        df_dist = pd.DataFrame(estudiantes_por_sede)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de barras agrupadas
            fig_bar = go.Figure()
            
            fig_bar.add_trace(go.Bar(
                name='Estudiantes',
                x=df_dist['sede'],
                y=df_dist['total_estudiantes'],
                marker_color=COLORS['primary']
            ))
            
            fig_bar.add_trace(go.Bar(
                name='Matrículas',
                x=df_dist['sede'],
                y=df_dist['total_matriculas'],
                marker_color=COLORS['secondary']
            ))
            
            fig_bar.add_trace(go.Bar(
                name='Pagos',
                x=df_dist['sede'],
                y=df_dist['total_pagos'],
                marker_color=COLORS['success']
            ))
            
            fig_bar.update_layout(
                title="Registros por Sede",
                barmode='group',
                height=400
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Mostrar tabla con datos
            st.markdown("**Resumen de Fragmentación Horizontal:**")
            st.dataframe(df_dist, use_container_width=True, hide_index=True)
            
            # Explicación
            st.info("""
            💡 **Observación**: Cada sede mantiene únicamente los datos de sus propios estudiantes.
            Esto reduce el tráfico de red y mejora el rendimiento local.
            """)
    
    # Ejemplo de consulta fragmentada
    st.subheader("🔍 Ejemplo de Consulta Fragmentada")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Consulta en San Carlos:**")
        st.code("""
        SELECT * FROM estudiante 
        WHERE id_sede = 2;  -- Solo estudiantes de SC
        """, language='sql')
        
        # Mostrar algunos estudiantes de San Carlos
        with get_db_connection('sancarlos') as db:
            if db:
                query = "SELECT nombre, email FROM estudiante LIMIT 5"
                df_sc = db.get_dataframe(query)
                if df_sc is not None:
                    st.dataframe(df_sc, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**Consulta en Heredia:**")
        st.code("""
        SELECT * FROM estudiante 
        WHERE id_sede = 3;  -- Solo estudiantes de HD
        """, language='sql')
        
        # Mostrar algunos estudiantes de Heredia
        with get_db_connection('heredia') as db:
            if db:
                query = "SELECT nombre, email FROM estudiante LIMIT 5"
                df_hd = db.get_dataframe(query)
                if df_hd is not None:
                    st.dataframe(df_hd, use_container_width=True, hide_index=True)

with tab3:
    st.header("↕️ Fragmentación Vertical")
    st.markdown("""
    La fragmentación vertical divide las tablas por **columnas**, separando diferentes tipos
    de información según su uso y nivel de acceso.
    """)
    
    # Mostrar ejemplo de fragmentación vertical
    st.subheader("🏢 Separación de Datos Administrativos y Académicos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏛️ Sede Central")
        st.markdown("**Datos Administrativos** (Solo en Central)")
        
        # Mostrar tablas administrativas
        with get_db_connection('central') as db:
            if db:
                # Verificar qué tablas existen
                query = "SHOW TABLES"
                tables = db.execute_query(query)
                
                admin_tables = []
                if tables:
                    for table in tables:
                        table_name = list(table.values())[0]
                        if table_name in ['planilla', 'pagare']:
                            admin_tables.append(table_name)
                
                if admin_tables:
                    st.success(f"✅ Tablas administrativas: {', '.join(admin_tables)}")
                    
                    # Mostrar ejemplo de planilla
                    if 'planilla' in admin_tables:
                        st.markdown("**Ejemplo: Planilla de Profesores**")
                        query = """
                        SELECT p.nombre as profesor, pl.salario, pl.mes
                        FROM planilla pl
                        JOIN profesor p ON pl.id_profesor = p.id_profesor
                        LIMIT 3
                        """
                        df_planilla = db.get_dataframe(query)
                        if df_planilla is not None and not df_planilla.empty:
                            df_planilla['salario'] = df_planilla['salario'].apply(lambda x: f"₡{x:,.2f}")
                            st.dataframe(df_planilla, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### 🏫 Sedes Regionales")
        st.markdown("**Datos Académicos** (San Carlos y Heredia)")
        
        # Mostrar tablas académicas
        academic_tables = ['estudiante', 'matricula', 'nota', 'asistencia', 'pago']
        st.success(f"✅ Tablas académicas: {', '.join(academic_tables)}")
        
        # Mostrar ejemplo de datos académicos
        with get_db_connection('sancarlos') as db:
            if db:
                st.markdown("**Ejemplo: Notas de Estudiantes**")
                query = """
                SELECT e.nombre as estudiante, c.nombre as curso, n.nota
                FROM nota n
                JOIN matricula m ON n.id_matricula = m.id_matricula
                JOIN estudiante e ON m.id_estudiante = e.id_estudiante
                JOIN curso c ON m.id_curso = c.id_curso
                LIMIT 3
                """
                df_notas = db.get_dataframe(query)
                if df_notas is not None and not df_notas.empty:
                    st.dataframe(df_notas, use_container_width=True, hide_index=True)
    
    # Visualización de la fragmentación vertical
    st.subheader("📊 Visualización de Fragmentación Vertical")
    
    # Crear diagrama de fragmentación vertical
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Tabla Original', 'Fragmento Admin', 'Fragmento Académico'),
        specs=[[{'type': 'table'}, {'type': 'table'}, {'type': 'table'}]]
    )
    
    # Tabla original (conceptual)
    fig.add_trace(
        go.Table(
            header=dict(
                values=['ID', 'Nombre', 'Email', 'Salario', 'Notas', 'Pagos'],
                fill_color='lightgray'
            ),
            cells=dict(
                values=[
                    ['1', '2', '3'],
                    ['Juan', 'María', 'Pedro'],
                    ['juan@...', 'maria@...', 'pedro@...'],
                    ['₡500k', '₡600k', '₡550k'],
                    ['85', '90', '88'],
                    ['✓', '✓', '✗']
                ],
                fill_color='white'
            )
        ),
        row=1, col=1
    )
    
    # Fragmento administrativo
    fig.add_trace(
        go.Table(
            header=dict(
                values=['ID', 'Nombre', 'Salario'],
                fill_color=COLORS['primary']
            ),
            cells=dict(
                values=[
                    ['1', '2', '3'],
                    ['Juan', 'María', 'Pedro'],
                    ['₡500k', '₡600k', '₡550k']
                ],
                fill_color='lightblue'
            )
        ),
        row=1, col=2
    )
    
    # Fragmento académico
    fig.add_trace(
        go.Table(
            header=dict(
                values=['ID', 'Nombre', 'Notas', 'Pagos'],
                fill_color=COLORS['success']
            ),
            cells=dict(
                values=[
                    ['1', '2', '3'],
                    ['Juan', 'María', 'Pedro'],
                    ['85', '90', '88'],
                    ['✓', '✓', '✗']
                ],
                fill_color='lightgreen'
            )
        ),
        row=1, col=3
    )
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("🔀 Fragmentación Mixta")
    st.markdown("""
    La fragmentación mixta combina las técnicas horizontal y vertical para lograr
    una distribución más granular y eficiente de los datos.
    """)
    
    # Ejemplo de fragmentación mixta con pagos
    st.subheader("💰 Ejemplo: Fragmentación Mixta de Pagos")
    
    st.markdown("""
    Los pagos están fragmentados de la siguiente manera:
    1. **Horizontalmente** por sede (cada sede mantiene sus propios pagos)
    2. **Verticalmente** separando información sensible de información pública
    """)
    
    # Mostrar distribución de pagos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Fragmentación Horizontal de Pagos")
        
        pagos_data = []
        for sede, color in [('sancarlos', COLORS['secondary']), ('heredia', COLORS['success'])]:
            with get_db_connection(sede) as db:
                if db:
                    query = """
                    SELECT s.nombre as sede, 
                           COUNT(*) as total_pagos,
                           SUM(p.monto) as monto_total
                    FROM pago p
                    JOIN estudiante e ON p.id_estudiante = e.id_estudiante
                    JOIN sede s ON e.id_sede = s.id_sede
                    GROUP BY s.nombre
                    """
                    result = db.execute_query(query)
                    if result:
                        for row in result:
                            row['color'] = color
                            pagos_data.append(row)
        
        if pagos_data:
            df_pagos = pd.DataFrame(pagos_data)
            
            # Gráfico de pagos por sede
            fig_pagos = go.Figure()
            
            for _, row in df_pagos.iterrows():
                fig_pagos.add_trace(go.Bar(
                    name=row['sede'],
                    x=[row['sede']],
                    y=[row['monto_total']],
                    marker_color=row['color'],
                    text=[f"₡{row['monto_total']:,.0f}"],
                    textposition='auto'
                ))
            
            fig_pagos.update_layout(
                title="Monto Total de Pagos por Sede",
                showlegend=False,
                height=300
            )
            
            st.plotly_chart(fig_pagos, use_container_width=True)
    
    with col2:
        st.markdown("### 🔐 Fragmentación Vertical de Pagos")
        st.markdown("""
        **Fragmento Público** (accesible por estudiantes):
        - ID del pago
        - Fecha
        - Concepto
        - Estado
        
        **Fragmento Privado** (solo administración):
        - Monto
        - Método de pago
        - Datos bancarios
        - Información fiscal
        """)
        
        # Mostrar ejemplo conceptual
        st.info("""
        💡 **Beneficio**: La fragmentación mixta permite que:
        - Los estudiantes vean su historial de pagos sin acceder a montos
        - La administración acceda a información financiera completa
        - Cada sede maneje sus propios datos financieros
        """)
    
    # Resumen de fragmentación en el sistema
    st.subheader("📋 Resumen de Fragmentación en el Sistema")
    
    fragmentation_summary = {
        'Tabla': ['Estudiante', 'Profesor', 'Carrera', 'Curso', 'Matricula', 
                  'Nota', 'Asistencia', 'Pago', 'Planilla', 'Pagaré'],
        'Tipo de Fragmentación': [
            'Horizontal (por sede)',
            'Replicada (master en Central)',
            'Replicada (master en Central)',
            'Horizontal (por sede)',
            'Derivada (sigue a estudiante)',
            'Derivada (sigue a matricula)',
            'Derivada (sigue a matricula)',
            'Mixta (H: sede, V: público/privado)',
            'No fragmentada (solo Central)',
            'No fragmentada (solo Central)'
        ],
        'Ubicación': [
            'SC, HD', 'Central → SC, HD', 'Central → SC, HD', 'SC, HD',
            'SC, HD', 'SC, HD', 'SC, HD', 'SC, HD', 'Central', 'Central'
        ]
    }
    
    df_summary = pd.DataFrame(fragmentation_summary)
    
    # Aplicar colores según el tipo
    def color_row(row):
        if 'Horizontal' in row['Tipo de Fragmentación']:
            return ['background-color: #ffe6e6'] * len(row)
        elif 'Vertical' in row['Tipo de Fragmentación']:
            return ['background-color: #e6f3ff'] * len(row)
        elif 'Mixta' in row['Tipo de Fragmentación']:
            return ['background-color: #fff0e6'] * len(row)
        elif 'Replicada' in row['Tipo de Fragmentación']:
            return ['background-color: #e6ffe6'] * len(row)
        else:
            return [''] * len(row)
    
    st.dataframe(
        df_summary.style.apply(color_row, axis=1),
        use_container_width=True,
        hide_index=True
    )

# Sidebar con información adicional
with st.sidebar:
    st.markdown("### 📊 Acerca de la Fragmentación")
    
    st.markdown("""
    La fragmentación es esencial para:
    
    ✅ **Rendimiento**: Datos locales = consultas más rápidas
    
    ✅ **Escalabilidad**: Fácil agregar nuevas sedes
    
    ✅ **Seguridad**: Separación de datos sensibles
    
    ✅ **Autonomía**: Cada sede opera independientemente
    """)
    
    st.markdown("---")
    
    # Selector de sede para explorar
    st.markdown("### 🔍 Explorar Datos")
    
    sede_selected = st.selectbox(
        "Selecciona una sede:",
        options=['sancarlos', 'heredia', 'central'],
        format_func=lambda x: get_sede_info(x)['name']
    )
    
    if st.button("📊 Ver estadísticas", use_container_width=True):
        with get_db_connection(sede_selected) as db:
            if db:
                # Contar tablas
                query = "SELECT COUNT(*) as total FROM information_schema.tables WHERE table_schema = %s"
                result = db.execute_query(query, (db.config['database'],))
                if result:
                    st.metric("Total de tablas", result[0]['total'])
                
                # Mostrar tablas disponibles
                query = "SHOW TABLES"
                tables = db.execute_query(query)
                if tables:
                    table_names = [list(t.values())[0] for t in tables]
                    st.markdown("**Tablas disponibles:**")
                    for table in table_names:
                        st.markdown(f"- {table}")
    
    st.markdown("---")
    st.markdown("""
    💡 **Tip**: Usa las pestañas para explorar diferentes tipos de fragmentación
    y ver ejemplos reales del sistema.
    """)