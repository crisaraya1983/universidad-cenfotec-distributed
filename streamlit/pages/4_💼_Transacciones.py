"""
Página de demostración de Transacciones Distribuidas
Esta página muestra cómo se ejecutan transacciones que involucran múltiples sedes
manteniendo la consistencia y atomicidad en el sistema distribuido.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import random

# Importar utilidades
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG, COLORS, get_sede_info
from utils.db_connections import get_db_connection, execute_distributed_query, get_redis_connection

# Configuración de la página
st.set_page_config(
    page_title="Transacciones - Sistema Cenfotec",
    page_icon="💼",
    layout="wide"
)

# Título de la página
st.title("💼 Transacciones Distribuidas")

# Introducción
st.markdown("""
Las **transacciones distribuidas** son operaciones que involucran datos en múltiples nodos
del sistema. Deben mantener las propiedades ACID incluso cuando los datos están distribuidos.
""")

# Tabs principales
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Conceptos",
    "📊 Consultas Globales", 
    "💰 Transacción: Pago Global",
    "📈 Transacción: Reporte Consolidado",
    "🔍 Vistas de Usuario"
])

with tab1:
    st.header("Conceptos de Transacciones Distribuidas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Propiedades ACID Distribuidas
        
        **Atomicidad** ⚛️
        - Todas las operaciones se completan o ninguna
        - Protocolo 2PC (Two-Phase Commit)
        - Rollback en caso de fallo
        
        **Consistencia** ✅
        - Estado válido antes y después
        - Validaciones distribuidas
        - Integridad referencial entre nodos
        
        **Aislamiento** 🔒
        - Transacciones concurrentes no interfieren
        - Bloqueos distribuidos
        - Niveles de aislamiento configurables
        
        **Durabilidad** 💾
        - Cambios persisten tras confirmación
        - Logs distribuidos
        - Recuperación ante fallos
        """)
    
    with col2:
        st.markdown("""
        ### 🔧 Tipos de Transacciones
        
        **1. Transacciones Locales**
        - Solo afectan una sede
        - Ejemplo: Matricular estudiante local
        - Rápidas y simples
        
        **2. Transacciones Globales**
        - Afectan múltiples sedes
        - Ejemplo: Generar reporte consolidado
        - Requieren coordinación
        
        **3. Transacciones Compensatorias**
        - Permiten deshacer operaciones
        - Útiles cuando no hay 2PC
        - Mantienen consistencia eventual
        """)
        
        # Diagrama del protocolo 2PC
        st.markdown("### 📐 Protocolo Two-Phase Commit")
        
        fig = go.Figure()
        
        # Timeline
        fig.add_trace(go.Scatter(
            x=[0, 1, 2, 3, 4],
            y=[0, 0, 0, 0, 0],
            mode='markers+text',
            marker=dict(size=20, color=COLORS['primary']),
            text=['Inicio', 'Prepare', 'Vote', 'Commit', 'Complete'],
            textposition="top center",
            name='Fases'
        ))
        
        fig.update_layout(
            title="Fases del Protocolo 2PC",
            showlegend=False,
            height=200,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, 1])
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("📊 Consultas Globales")
    st.markdown("""
    Las consultas globales obtienen información de múltiples sedes para generar
    una vista unificada del sistema.
    """)
    
    # Consulta 1: Total de estudiantes por sede
    st.subheader("👥 Consulta Global: Distribución de Estudiantes")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Query distribuida:**")
        st.code("""
        -- Ejecutar en cada sede regional
        SELECT s.nombre as sede, 
               COUNT(DISTINCT e.id_estudiante) as estudiantes,
               COUNT(DISTINCT m.id_matricula) as matriculas,
               AVG(n.nota) as promedio_general
        FROM estudiante e
        JOIN sede s ON e.id_sede = s.id_sede
        LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
        LEFT JOIN nota n ON m.id_matricula = n.id_matricula
        GROUP BY s.nombre
        """, language='sql')
    
    with col2:
        if st.button("🔍 Ejecutar Consulta Global", key="query1"):
            with st.spinner("Ejecutando en todas las sedes..."):
                # Simular ejecución distribuida
                progress = st.progress(0)
                
                results = []
                sedes = ['sancarlos', 'heredia']
                
                for i, sede in enumerate(sedes):
                    progress.progress((i + 1) / len(sedes))
                    time.sleep(0.5)  # Simular latencia
                    
                    with get_db_connection(sede) as db:
                        if db:
                            query = """
                            SELECT s.nombre as sede, 
                                   COUNT(DISTINCT e.id_estudiante) as estudiantes,
                                   COUNT(DISTINCT m.id_matricula) as matriculas,
                                   AVG(n.nota) as promedio_general
                            FROM estudiante e
                            JOIN sede s ON e.id_sede = s.id_sede
                            LEFT JOIN matricula m ON e.id_estudiante = m.id_estudiante
                            LEFT JOIN nota n ON m.id_matricula = n.id_matricula
                            GROUP BY s.nombre
                            """
                            result = db.execute_query(query)
                            if result:
                                results.extend(result)
                
                progress.progress(1.0)
                st.success("✅ Consulta completada")
    
    # Mostrar resultados
    if 'results' in locals() and results:
        df_results = pd.DataFrame(results)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tabla de resultados
            st.markdown("**Resultados Consolidados:**")
            st.dataframe(df_results, use_container_width=True, hide_index=True)
        
        with col2:
            # Gráfico de distribución
            fig = px.bar(df_results, x='sede', y='estudiantes',
                        title='Estudiantes por Sede',
                        color='sede',
                        color_discrete_map={'San Carlos': COLORS['secondary'],
                                          'Heredia': COLORS['success']})
            st.plotly_chart(fig, use_container_width=True)
    
    # Consulta 2: Reporte financiero global
    st.subheader("💰 Consulta Global: Reporte Financiero")
    
    with st.expander("Ver consulta de reporte financiero"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Query distribuida compleja:**")
            st.code("""
            -- SEDE CENTRAL: Obtener planillas
            SELECT 'Planillas' as concepto, 
                   SUM(salario) as monto_total,
                   COUNT(*) as cantidad
            FROM planilla
            WHERE mes = MONTH(CURRENT_DATE)
            
            UNION ALL
            
            -- SEDES REGIONALES: Obtener pagos
            SELECT 'Pagos Estudiantes' as concepto,
                   SUM(monto) as monto_total,
                   COUNT(*) as cantidad
            FROM pago
            WHERE MONTH(fecha) = MONTH(CURRENT_DATE)
            """, language='sql')
        
        with col2:
            if st.button("🔍 Ejecutar Reporte Global", key="query2"):
                with st.spinner("Consolidando información financiera..."):
                    # Datos simulados
                    financial_data = pd.DataFrame({
                        'Concepto': ['Planillas (Central)', 'Pagos SC', 'Pagos HD', 'Pagarés'],
                        'Monto': [5000000, 3500000, 2800000, 1200000],
                        'Sede': ['Central', 'San Carlos', 'Heredia', 'Central']
                    })
                    
                    # Mostrar total
                    total = financial_data['Monto'].sum()
                    st.metric("💰 Total Consolidado", f"₡{total:,.2f}")
                    
                    # Gráfico
                    fig = px.pie(financial_data, values='Monto', names='Concepto',
                               title='Distribución Financiera Global')
                    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("💰 Transacción: Procesamiento de Pago Global")
    
    st.markdown("""
    Simula una transacción que registra un pago que afecta múltiples sistemas:
    - Registro del pago en la sede del estudiante
    - Actualización del pagaré en Central (si aplica)
    - Actualización del cache distribuido
    """)
    
    # Formulario de pago
    with st.form("pago_global_form"):
        st.markdown("### 📝 Registrar Pago")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleccionar estudiante
            sede_pago = st.selectbox("Sede del estudiante:", ["San Carlos", "Heredia"])
            
            # Obtener estudiantes con pagarés
            estudiantes_con_pagare = []
            sede_key = sede_pago.lower().replace(' ', '')
            
            with get_db_connection(sede_key) as db:
                if db:
                    # Simulamos que algunos estudiantes tienen pagarés
                    query = """
                    SELECT e.id_estudiante, e.nombre, e.email
                    FROM estudiante e
                    LIMIT 5
                    """
                    result = db.execute_query(query)
                    if result:
                        estudiantes_con_pagare = [(f"{r['nombre']}", r['id_estudiante']) 
                                                for r in result]
            
            if estudiantes_con_pagare:
                estudiante = st.selectbox("Estudiante:", 
                                        options=estudiantes_con_pagare,
                                        format_func=lambda x: x[0])
            
            monto = st.number_input("Monto del pago:", min_value=1000, max_value=1000000, 
                                  value=50000, step=1000)
        
        with col2:
            concepto = st.selectbox("Concepto:", 
                                  ["Matrícula", "Mensualidad", "Laboratorio", "Otro"])
            
            tiene_pagare = st.checkbox("¿Aplica a un pagaré existente?")
            
            if tiene_pagare:
                st.info("Se actualizará el pagaré en la sede Central")
        
        submitted = st.form_submit_button("💳 Procesar Pago", type="primary")
    
    # Procesar transacción
    if submitted:
        st.markdown("### 🔄 Procesando Transacción Distribuida")
        
        # Contenedor para los pasos
        steps_container = st.container()
        
        with steps_container:
            # Paso 1: Iniciar transacción
            step1 = st.empty()
            step1.info("📍 Paso 1/5: Iniciando transacción distribuida...")
            time.sleep(1)
            step1.success("✅ Paso 1/5: Transacción iniciada - ID: TRX-2025-0124-001")
            
            # Paso 2: Verificar estudiante
            step2 = st.empty()
            step2.info("📍 Paso 2/5: Verificando datos del estudiante...")
            time.sleep(1)
            step2.success(f"✅ Paso 2/5: Estudiante verificado en {sede_pago}")
            
            # Paso 3: Registrar pago local
            step3 = st.empty()
            step3.info(f"📍 Paso 3/5: Registrando pago en {sede_pago}...")
            time.sleep(1.5)
            step3.success(f"✅ Paso 3/5: Pago registrado - ID: PAY-{random.randint(1000, 9999)}")
            
            # Paso 4: Actualizar pagaré (si aplica)
            if tiene_pagare:
                step4 = st.empty()
                step4.info("📍 Paso 4/5: Actualizando pagaré en Central...")
                time.sleep(1.5)
                step4.success("✅ Paso 4/5: Pagaré actualizado en sede Central")
            else:
                step4 = st.empty()
                step4.info("📍 Paso 4/5: Sin pagarés pendientes")
            
            # Paso 5: Commit distribuido
            step5 = st.empty()
            step5.info("📍 Paso 5/5: Confirmando transacción en todos los nodos...")
            time.sleep(1)
            step5.success("✅ Paso 5/5: Transacción completada exitosamente")
        
        # Mostrar resumen
        st.balloons()
        
        st.markdown("### 📊 Resumen de la Transacción")
        
        summary_data = {
            'Campo': ['ID Transacción', 'Estudiante', 'Sede', 'Monto', 
                     'Concepto', 'Estado', 'Timestamp'],
            'Valor': [
                'TRX-2025-0124-001',
                estudiante[0] if 'estudiante' in locals() else 'Demo Student',
                sede_pago,
                f"₡{monto:,.2f}",
                concepto,
                '✅ Completada',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        
        df_summary = pd.DataFrame(summary_data)
        st.table(df_summary.set_index('Campo'))
        
        # Log de auditoría
        with st.expander("📜 Ver Log de Auditoría"):
            audit_log = f"""
            [2025-01-24 10:30:01] BEGIN DISTRIBUTED TRANSACTION TRX-2025-0124-001
            [2025-01-24 10:30:02] VERIFY student_id={estudiante[1] if 'estudiante' in locals() else '1'} AT {sede_pago}
            [2025-01-24 10:30:03] INSERT INTO pago (id_estudiante, monto, concepto) VALUES (...)
            [2025-01-24 10:30:04] {'UPDATE pagare SET saldo = saldo - ' + str(monto) if tiene_pagare else 'SKIP pagare update'}
            [2025-01-24 10:30:05] COMMIT TRANSACTION TRX-2025-0124-001
            [2025-01-24 10:30:05] INVALIDATE CACHE KEY: student_payments_{estudiante[1] if 'estudiante' in locals() else '1'}
            """
            st.code(audit_log, language='log')

with tab4:
    st.header("📈 Transacción: Generación de Reporte Consolidado")
    
    st.markdown("""
    Esta transacción recopila datos de todas las sedes para generar un reporte
    ejecutivo consolidado del estado de la universidad.
    """)
    
    # Configuración del reporte
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📅 Configuración del Reporte")
        
        tipo_reporte = st.selectbox(
            "Tipo de reporte:",
            ["Reporte Ejecutivo Mensual", "Análisis Académico", "Reporte Financiero", "Dashboard KPIs"]
        )
        
        periodo = st.date_input(
            "Período:",
            value=datetime.now().date(),
            max_value=datetime.now().date()
        )
    
    with col2:
        st.markdown("### 🎯 Sedes a Incluir")
        
        incluir_central = st.checkbox("Central", value=True)
        incluir_sc = st.checkbox("San Carlos", value=True)
        incluir_hd = st.checkbox("Heredia", value=True)
        
        formato = st.radio("Formato de salida:", ["Dashboard", "PDF", "Excel"])
    
    # Generar reporte
    if st.button("📊 Generar Reporte Consolidado", type="primary", use_container_width=True):
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Recopilar datos de cada sede
        report_data = {
            'estudiantes_total': 0,
            'profesores_total': 0,
            'matriculas_mes': 0,
            'ingresos_mes': 0,
            'promedio_notas': 0,
            'asistencia_promedio': 0,
            'datos_por_sede': {}
        }
        
        sedes_incluidas = []
        if incluir_central:
            sedes_incluidas.append('central')
        if incluir_sc:
            sedes_incluidas.append('sancarlos')
        if incluir_hd:
            sedes_incluidas.append('heredia')
        
        # Procesar cada sede
        for i, sede in enumerate(sedes_incluidas):
            progress_bar.progress((i + 1) / len(sedes_incluidas))
            status_text.text(f"Procesando {get_sede_info(sede)['name']}...")
            time.sleep(1)  # Simular procesamiento
            
            with get_db_connection(sede) as db:
                if db:
                    sede_data = {}
                    
                    if sede == 'central':
                        # Datos administrativos
                        query_profesores = "SELECT COUNT(*) as total FROM profesor"
                        result = db.execute_query(query_profesores)
                        if result:
                            report_data['profesores_total'] = result[0]['total']
                            sede_data['profesores'] = result[0]['total']
                        
                        # Planilla del mes
                        query_planilla = "SELECT SUM(salario) as total FROM planilla WHERE mes = MONTH(%s)"
                        result = db.execute_query(query_planilla, (periodo,))
                        if result and result[0]['total']:
                            sede_data['gastos_planilla'] = float(result[0]['total'])
                    
                    else:  # Sedes regionales
                        # Estudiantes
                        query_estudiantes = "SELECT COUNT(*) as total FROM estudiante"
                        result = db.execute_query(query_estudiantes)
                        if result:
                            report_data['estudiantes_total'] += result[0]['total']
                            sede_data['estudiantes'] = result[0]['total']
                        
                        # Matrículas del mes
                        query_matriculas = """
                        SELECT COUNT(*) as total 
                        FROM matricula 
                        WHERE MONTH(fecha_matricula) = MONTH(%s)
                        """
                        result = db.execute_query(query_matriculas, (periodo,))
                        if result:
                            report_data['matriculas_mes'] += result[0]['total'] or 0
                            sede_data['matriculas_mes'] = result[0]['total'] or 0
                        
                        # Ingresos del mes
                        query_ingresos = """
                        SELECT SUM(monto) as total 
                        FROM pago 
                        WHERE MONTH(fecha) = MONTH(%s)
                        """
                        result = db.execute_query(query_ingresos, (periodo,))
                        if result and result[0]['total']:
                            report_data['ingresos_mes'] += float(result[0]['total'])
                            sede_data['ingresos_mes'] = float(result[0]['total'])
                    
                    report_data['datos_por_sede'][sede] = sede_data
        
        progress_bar.progress(1.0)
        status_text.text("✅ Reporte generado exitosamente")
        time.sleep(0.5)
        status_text.empty()
        
        # Mostrar resultados
        st.markdown("### 📊 Reporte Ejecutivo Consolidado")
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Estudiantes Totales", f"{report_data['estudiantes_total']:,}")
        
        with col2:
            st.metric("👨‍🏫 Profesores", f"{report_data['profesores_total']:,}")
        
        with col3:
            st.metric("📝 Matrículas (Mes)", f"{report_data['matriculas_mes']:,}")
        
        with col4:
            st.metric("💰 Ingresos (Mes)", f"₡{report_data['ingresos_mes']:,.0f}")
        
        # Gráficos comparativos
        st.markdown("### 📈 Análisis por Sede")
        
        if report_data['datos_por_sede']:
            # Preparar datos para gráficos
            sede_names = []
            estudiantes = []
            ingresos = []
            
            for sede, data in report_data['datos_por_sede'].items():
                sede_names.append(get_sede_info(sede)['name'])
                estudiantes.append(data.get('estudiantes', 0))
                ingresos.append(data.get('ingresos_mes', 0))
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de estudiantes
                fig_est = px.bar(
                    x=sede_names, 
                    y=estudiantes,
                    title="Estudiantes por Sede",
                    color=sede_names,
                    color_discrete_map={
                        '🏛️ Sede Central': COLORS['primary'],
                        '🏢 Sede San Carlos': COLORS['secondary'],
                        '🏫 Sede Heredia': COLORS['success']
                    }
                )
                st.plotly_chart(fig_est, use_container_width=True)
            
            with col2:
                # Gráfico de ingresos
                fig_ing = px.pie(
                    values=ingresos,
                    names=sede_names,
                    title="Distribución de Ingresos",
                    color_discrete_map={
                        '🏛️ Sede Central': COLORS['primary'],
                        '🏢 Sede San Carlos': COLORS['secondary'],
                        '🏫 Sede Heredia': COLORS['success']
                    }
                )
                st.plotly_chart(fig_ing, use_container_width=True)
        
        # Opciones de exportación
        st.markdown("### 💾 Exportar Reporte")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Descargar PDF", use_container_width=True):
                st.info("Generando PDF... (función simulada)")
        
        with col2:
            if st.button("📊 Descargar Excel", use_container_width=True):
                st.info("Generando Excel... (función simulada)")
        
        with col3:
            if st.button("📧 Enviar por Email", use_container_width=True):
                st.info("Enviando reporte... (función simulada)")

with tab5:
    st.header("🔍 Vistas de Usuario")
    
    st.markdown("""
    Las vistas proporcionan acceso controlado a datos distribuidos según el rol del usuario,
    abstractando la complejidad de la distribución de datos.
    """)
    
    # Selector de vista/rol
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 👤 Seleccionar Rol")
        
        rol_selected = st.selectbox(
            "Rol de usuario:",
            ["Estudiante", "Profesor", "Administrativo", "Directivo"]
        )
        
        # Diccionario de permisos
        permisos = {
            "Estudiante": "- Ver sus calificaciones\n- Ver sus pagos\n- Ver horarios",
            "Profesor": "- Ver estudiantes matriculados\n- Registrar notas\n- Ver planilla",
            "Administrativo": "- Gestionar pagos\n- Ver reportes financieros\n- Gestionar pagarés",
            "Directivo": "- Ver todos los reportes\n- Análisis consolidados\n- KPIs globales"
        }

        # Obtener los permisos según el rol seleccionado
        descripcion = permisos[rol_selected]

        # Mostrar en Streamlit
        st.info(f"""**Permisos del rol {rol_selected}:**

        {descripcion}
        """)
    
    with col2:
        st.markdown(f"### 📊 Vista: {rol_selected}")
        
        if rol_selected == "Estudiante":
            # Vista de estudiante
            st.markdown("**Mis Calificaciones**")
            
            # Simulación de datos del estudiante
            notas_data = pd.DataFrame({
                'Curso': ['Bases de Datos', 'Programación III', 'Redes', 'Inglés'],
                'Profesor': ['Dr. García', 'Ing. López', 'Ing. Mora', 'Lic. Smith'],
                'Nota': [92, 88, 95, 90],
                'Estado': ['Aprobado', 'Aprobado', 'Aprobado', 'Aprobado']
            })
            
            st.dataframe(notas_data, use_container_width=True, hide_index=True)
            
            # Gráfico de rendimiento
            fig = px.bar(notas_data, x='Curso', y='Nota', 
                        title='Mi Rendimiento Académico',
                        color='Nota',
                        color_continuous_scale=['red', 'yellow', 'green'])
            fig.add_hline(y=70, line_dash="dash", 
                         annotation_text="Nota mínima de aprobación")
            st.plotly_chart(fig, use_container_width=True)
            
            # SQL de la vista
            with st.expander("Ver consulta SQL de esta vista"):
                st.code("""
                CREATE VIEW vista_estudiante_notas AS
                SELECT 
                    c.nombre as curso,
                    p.nombre as profesor,
                    n.nota,
                    CASE 
                        WHEN n.nota >= 70 THEN 'Aprobado'
                        ELSE 'Reprobado'
                    END as estado
                FROM nota n
                JOIN matricula m ON n.id_matricula = m.id_matricula
                JOIN curso c ON m.id_curso = c.id_curso
                JOIN profesor p ON c.id_profesor = p.id_profesor
                WHERE m.id_estudiante = :estudiante_id
                """, language='sql')
        
        elif rol_selected == "Profesor":
            # Vista de profesor
            st.markdown("**Mis Estudiantes Matriculados**")
            
            # Seleccionar curso
            curso = st.selectbox("Seleccionar curso:", 
                               ["Bases de Datos Distribuidas", "Cloud Computing"])
            
            # Datos de estudiantes
            estudiantes_data = pd.DataFrame({
                'Estudiante': ['Juan Pérez', 'María García', 'Carlos López', 'Ana Mora'],
                'Email': ['juan@cenfotec.cr', 'maria@cenfotec.cr', 'carlos@cenfotec.cr', 'ana@cenfotec.cr'],
                'Asistencia': ['95%', '100%', '88%', '92%'],
                'Promedio': [88, 92, 85, 90]
            })
            
            st.dataframe(estudiantes_data, use_container_width=True, hide_index=True)
            
            # Botón para registrar notas
            if st.button("📝 Registrar Notas", use_container_width=True):
                st.info("Redirigiendo al sistema de calificaciones...")
        
        elif rol_selected == "Administrativo":
            # Vista administrativa
            st.markdown("**Panel de Control Administrativo**")
            
            # Métricas financieras
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("💰 Ingresos del Mes", "₡12,500,000", "+15%")
            
            with col2:
                st.metric("📄 Pagarés Activos", "45", "-3")
            
            with col3:
                st.metric("⚠️ Pagos Pendientes", "23", "+5")
            
            # Tabla de pagos recientes
            st.markdown("**Últimos Pagos Registrados**")
            
            pagos_admin = pd.DataFrame({
                'Fecha': [datetime.now().date() - timedelta(days=i) for i in range(5)],
                'Estudiante': ['Est. ' + str(i) for i in range(1, 6)],
                'Monto': [50000, 75000, 100000, 50000, 125000],
                'Concepto': ['Matrícula', 'Mensualidad', 'Laboratorio', 'Matrícula', 'Curso Especial'],
                'Estado': ['✅ Procesado'] * 5
            })
            
            pagos_admin['Monto'] = pagos_admin['Monto'].apply(lambda x: f"₡{x:,}")
            st.dataframe(pagos_admin, use_container_width=True, hide_index=True)
        
        else:  # Directivo
            # Vista ejecutiva
            st.markdown("**Dashboard Ejecutivo**")
            
            # KPIs principales
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            
            with kpi1:
                st.metric("📈 Crecimiento Anual", "18.5%", "+3.2%")
            
            with kpi2:
                st.metric("💼 Tasa de Empleo", "92%", "+5%")
            
            with kpi3:
                st.metric("😊 Satisfacción", "4.7/5", "+0.2")
            
            with kpi4:
                st.metric("🎓 Tasa Graduación", "87%", "+2%")
            
            # Gráfico de tendencias
            months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
            tendencias = pd.DataFrame({
                'Mes': months,
                'Estudiantes Nuevos': [120, 135, 128, 142, 155, 168],
                'Ingresos (Millones)': [45, 48, 47, 52, 55, 58]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months, y=tendencias['Estudiantes Nuevos'],
                                   mode='lines+markers', name='Estudiantes Nuevos',
                                   yaxis='y'))
            fig.add_trace(go.Bar(x=months, y=tendencias['Ingresos (Millones)'],
                               name='Ingresos', yaxis='y2', opacity=0.6))
            
            fig.update_layout(
                title='Tendencias del Semestre',
                yaxis=dict(title='Estudiantes'),
                yaxis2=dict(title='Ingresos (M₡)', overlaying='y', side='right'),
                hovermode='x'
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Información sobre vistas
    st.markdown("### 📚 Acerca de las Vistas Distribuidas")
    
    with st.expander("¿Cómo funcionan las vistas en un sistema distribuido?"):
        st.markdown("""
        Las vistas en bases de datos distribuidas presentan desafíos únicos:
        
        1. **Vistas Locales**: Acceden solo a datos de una sede
           - Rápidas y simples
           - No requieren coordinación
        
        2. **Vistas Globales**: Combinan datos de múltiples sedes
           - Requieren consultas distribuidas
           - Mayor latencia pero información completa
        
        3. **Vistas Materializadas**: Pre-calculadas y almacenadas
           - Mejor rendimiento
           - Requieren actualización periódica
        
        4. **Vistas con Cache**: Utilizan Redis para mejorar rendimiento
           - Balance entre frescura y velocidad
           - Ideal para dashboards
        """)

# Sidebar con información
with st.sidebar:
    st.markdown("### 💼 Transacciones Distribuidas")
    
    st.markdown("""
    Esta sección demuestra:
    
    ✅ **Consultas globales** que obtienen datos de múltiples sedes
    
    ✅ **Transacciones ACID** manteniendo consistencia
    
    ✅ **Vistas de usuario** según roles y permisos
    
    ✅ **Reportes consolidados** con datos en tiempo real
    """)
    
    st.markdown("---")
    
    # Monitor de transacciones
    st.markdown("### 📊 Monitor de Transacciones")
    
    # Simulación de métricas
    st.metric("Transacciones/min", "42", "+5")
    st.metric("Tiempo promedio", "1.2s", "-0.1s")
    st.metric("Tasa de éxito", "99.8%", "0%")
    
    # Mini log
    st.markdown("### 📜 Últimas Transacciones")
    
    with st.container():
        for i in range(3):
            time_ago = datetime.now() - timedelta(minutes=i*2)
            st.text(f"{time_ago.strftime('%H:%M:%S')} - TRX-{1000+i}")
    
    st.markdown("---")
    
    st.markdown("""
    💡 **Tip**: Las transacciones distribuidas son más complejas
    pero esenciales para mantener la consistencia global del sistema.
    """)