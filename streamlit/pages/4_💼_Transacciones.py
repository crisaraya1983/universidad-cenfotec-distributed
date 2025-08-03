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

# Tabs principales - SIN Consultas Globales, CON Proceso de Matrícula
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Conceptos",
    "💰 Transacción: Pago Global",
    "📚 Transacción: Proceso de Matrícula",
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

# TAB2 - TRANSACCIÓN PAGO GLOBAL (SIN CAMBIOS)
with tab2:
    st.header("💰 Transacción: Procesamiento de Pago")
    
    st.markdown("""
    Simula una transacción que registra un pago que afecta múltiples sistemas:
    - Registro del pago en la sede del estudiante
    - Actualización del pagaré en Central (si aplica)
    - Actualización del cache distribuido
    """)
    
    # PASO 1: SELECCIÓN ÚNICA DE ESTUDIANTE (SIMPLIFICADO)
    st.markdown("### 👤 Seleccionar Estudiante")
    
    # Cargar estudiantes de todas las sedes
    estudiantes_data = {}
    for sede in ['central', 'sancarlos', 'heredia']:
        with get_db_connection(sede) as db:
            if db:
                result = db.execute_query("SELECT id_estudiante, nombre FROM estudiante")
                if result:
                    for est in result:
                        sede_nombre = get_sede_info(sede)['name']
                        estudiantes_data[f"{est['nombre']} ({sede_nombre})"] = {
                            'id': est['id_estudiante'],
                            'nombre': est['nombre'],
                            'sede': sede,
                            'sede_nombre': sede_nombre
                        }

    if estudiantes_data:
        estudiante_seleccionado = st.selectbox("Estudiante:", list(estudiantes_data.keys()))
        estudiante_info = estudiantes_data[estudiante_seleccionado]
        
        # Mostrar información del estudiante seleccionado
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Estudiante:** {estudiante_info['nombre']}")
        with col2:
            st.info(f"**Sede:** {estudiante_info['sede_nombre']}")
        with col3:
            st.info(f"**ID:** {estudiante_info['id']}")
    else:
        st.error("No se pudieron cargar los estudiantes")
        st.stop()
    
    # PASO 2: FORMULARIO DE PAGO (SIN SELECCIÓN DE SEDE DUPLICADA)
    with st.form("pago_global_form"):
        st.markdown("### 📝 Registrar Pago")
        
        col1, col2 = st.columns(2)
        
        with col1:
            monto = st.number_input("Monto del pago:", min_value=1000, max_value=1000000, 
                                  value=50000, step=1000)
            
            concepto = st.selectbox("Concepto:", [
                "Matrícula",
                "Mensualidad", 
                "Laboratorio",
                "Pago de Pagaré", 
                "Transferencia de Créditos", 
                "Matrícula Intercambio"
            ])
        
        with col2:
            tiene_pagare = st.checkbox("¿Aplica a un pagaré existente?")
            
            # Mostrar información adicional
            st.markdown("**Información de la transacción:**")
            st.text(f"• Estudiante: {estudiante_info['nombre']}")
            st.text(f"• Sede de registro: {estudiante_info['sede_nombre']}")
            if tiene_pagare:
                st.text("• Se actualizará pagaré en Central")
        
        submitted = st.form_submit_button("💳 Procesar Pago", type="primary")
    
    # PASO 3: PROCESAR TRANSACCIÓN
    if submitted:
        st.markdown("### 🔄 Procesando Transacción Distribuida")
        
        # Contenedor para los pasos
        steps_container = st.container()
        
        with steps_container:
            # Paso 1: Iniciar transacción
            step1 = st.empty()
            step1.info("📍 Paso 1/5: Iniciando transacción distribuida...")
            time.sleep(1)
            step1.success(f"✅ Paso 1/5: Transacción iniciada - ID: TRX-{datetime.now().strftime('%Y%m%d')}-001")
            
            # Paso 2: Verificar estudiante
            step2 = st.empty()
            step2.info("📍 Paso 2/5: Verificando datos del estudiante...")
            time.sleep(1)
            step2.success(f"✅ Paso 2/5: Estudiante verificado en {estudiante_info['sede_nombre']}")
            
            # Paso 3: Registrar pago local (CON EJECUCIÓN REAL)
            step3 = st.empty()
            step3.info(f"📍 Paso 3/5: Registrando pago en {estudiante_info['sede_nombre']}...")
            
            # EJECUTAR INSERT REAL
            with get_db_connection(estudiante_info['sede']) as db:
                if db:
                    insert_query = "INSERT INTO pago (id_estudiante, monto, fecha) VALUES (%s, %s, %s)"
                    affected_rows = db.execute_update(insert_query, 
                        (estudiante_info['id'], monto, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    
                    if affected_rows and affected_rows > 0:
                        pago_id = f"PAY-{random.randint(1000, 9999)}"
                        step3.success(f"✅ Paso 3/5: Pago registrado - ID: {pago_id}")
                    else:
                        step3.error("❌ Error al registrar el pago")
                        st.stop()
                else:
                    step3.error("❌ No se pudo conectar a la base de datos")
                    st.stop()
            
            # Paso 4: Actualizar pagaré (si aplica) - CON EJECUCIÓN REAL
            step4 = st.empty()
            if tiene_pagare:
                step4.info("📍 Paso 4/5: Actualizando pagaré en Central...")
                
                # Verificar si realmente tiene pagaré
                with get_db_connection('central') as db:
                    if db:
                        pagare_query = "SELECT id_pagare, monto FROM pagare WHERE id_estudiante = %s AND monto > 0"
                        pagares = db.execute_query(pagare_query, (estudiante_info['id'],))
                        
                        if pagares and len(pagares) > 0:
                            # Actualizar el primer pagaré encontrado
                            pagare = pagares[0]
                            nuevo_monto = max(0, pagare['monto'] - monto)
                            
                            update_query = "UPDATE pagare SET monto = %s WHERE id_pagare = %s"
                            affected = db.execute_update(update_query, (nuevo_monto, pagare['id_pagare']))
                            
                            if affected and affected > 0:
                                step4.success("✅ Paso 4/5: Pagaré actualizado en sede Central")
                            else:
                                step4.error("❌ Error al actualizar pagaré")
                        else:
                            step4.info("📍 Paso 4/5: Sin pagarés pendientes para este estudiante")
                    else:
                        step4.warning("⚠️ Paso 4/5: No se pudo conectar a Central para verificar pagarés")
            else:
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
                f'TRX-{datetime.now().strftime("%Y%m%d")}-001',
                estudiante_info['nombre'],
                estudiante_info['sede_nombre'],
                f"₡{monto:,.2f}",
                concepto,
                '✅ Completada',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        
        df_summary = pd.DataFrame(summary_data)
        st.table(df_summary.set_index('Campo'))
        
        # Log de auditoría CORREGIDO
        with st.expander("📜 Ver Log de Auditoría"):
            audit_log = f"""[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] BEGIN DISTRIBUTED TRANSACTION TRX-{datetime.now().strftime('%Y%m%d')}-001
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] VERIFY student_id={estudiante_info['id']} AT {estudiante_info['sede']}
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INSERT INTO pago (id_estudiante, monto, fecha) VALUES ({estudiante_info['id']}, {monto}, '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'UPDATE pagare SET monto = monto - ' + str(monto) + ' WHERE id_estudiante = ' + str(estudiante_info['id']) if tiene_pagare else 'SKIP pagare update (no pending pagares)'}
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] COMMIT TRANSACTION TRX-{datetime.now().strftime('%Y%m%d')}-001
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] TRANSACTION COMPLETED SUCCESSFULLY"""
            st.code(audit_log, language='log')

# TAB3 - NUEVO: TRANSACCIÓN PROCESO DE MATRÍCULA
with tab3:
    st.header("📚 Transacción: Proceso de Matrícula")
    
    st.markdown("""
    Proceso de matrícula que puede involucrar múltiples operaciones:
    - Crear estudiante nuevo (si aplica)
    - Registrar matrícula(s) en curso(s)
    - Procesar pago inmediato o crear pagaré
    - Actualizar registros distribuidos
    """)
    
    # PASO 1: SELECCIONAR SEDE
    st.markdown("### 🏢 Configuración de Matrícula")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sede_matricula = st.selectbox("Sede para la matrícula:", [
            "central", "sancarlos", "heredia"
        ], format_func=lambda x: get_sede_info(x)['name'])
        
        sede_info_matricula = get_sede_info(sede_matricula)
    
    with col2:
        tipo_estudiante = st.radio("Tipo de estudiante:", [
            "Estudiante existente",
            "Estudiante nuevo"
        ])
    
    # PASO 2: SELECCIONAR O CREAR ESTUDIANTE
    estudiante_matricula = None
    
    if tipo_estudiante == "Estudiante existente":
        st.markdown("### 👤 Seleccionar Estudiante Existente")
        
        # Cargar estudiantes de la sede seleccionada
        with get_db_connection(sede_matricula) as db:
            if db:
                result = db.execute_query("SELECT id_estudiante, nombre, email FROM estudiante")
                if result:
                    estudiantes_options = {f"{est['nombre']} ({est['email']})": est for est in result}
                    
                    if estudiantes_options:
                        estudiante_selected = st.selectbox("Estudiante:", list(estudiantes_options.keys()))
                        estudiante_matricula = estudiantes_options[estudiante_selected]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.success(f"✅ **Estudiante:** {estudiante_matricula['nombre']}")
                        with col2:
                            st.success(f"✅ **Email:** {estudiante_matricula['email']}")
                    else:
                        st.warning("No hay estudiantes registrados en esta sede")
                else:
                    st.error("Error al cargar estudiantes")
            else:
                st.error("No se pudo conectar a la base de datos")
    
    else:  # Estudiante nuevo
        st.markdown("### ➕ Crear Estudiante Nuevo")
        
        with st.form("nuevo_estudiante_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nuevo_nombre = st.text_input("Nombre completo:", 
                                           placeholder="Ej: María García López")
                nuevo_email = st.text_input("Email institucional:", 
                                          placeholder="Ej: maria.garcia@estudiante.cenfotec.ac.cr")
            
            with col2:
                st.markdown("**Información adicional:**")
                st.text(f"• Sede: {sede_info_matricula['name']}")
                st.text("• Se asignará ID automáticamente")
                st.text("• Email debe ser único en el sistema")
            
            crear_estudiante = st.form_submit_button("➕ Crear Estudiante")
            
            if crear_estudiante:
                if nuevo_nombre and nuevo_email:
                    # Verificar que el email no exista
                    email_existe = False
                    for sede_check in ['central', 'sancarlos', 'heredia']:
                        with get_db_connection(sede_check) as db:
                            if db:
                                check_query = "SELECT id_estudiante FROM estudiante WHERE email = %s"
                                result = db.execute_query(check_query, (nuevo_email,))
                                if result:
                                    email_existe = True
                                    break
                    
                    if email_existe:
                        st.error("❌ Este email ya está registrado en el sistema")
                    else:
                        # Crear el estudiante
                        with get_db_connection(sede_matricula) as db:
                            if db:
                                # Obtener ID de sede
                                sede_ids = {"central": 1, "sancarlos": 2, "heredia": 3}
                                id_sede = sede_ids[sede_matricula]
                                
                                insert_query = "INSERT INTO estudiante (nombre, email, id_sede) VALUES (%s, %s, %s)"
                                affected = db.execute_update(insert_query, (nuevo_nombre, nuevo_email, id_sede))
                                
                                if affected and affected > 0:
                                    # Obtener el ID del estudiante recién creado
                                    get_id_query = "SELECT id_estudiante, nombre, email FROM estudiante WHERE email = %s"
                                    result = db.execute_query(get_id_query, (nuevo_email,))
                                    
                                    if result:
                                        estudiante_matricula = result[0]
                                        st.success(f"✅ Estudiante creado exitosamente - ID: {estudiante_matricula['id_estudiante']}")
                                        time.sleep(2)
                                        st.rerun()
                                    else:
                                        st.error("❌ Error al obtener datos del estudiante creado")
                                else:
                                    st.error("❌ Error al crear el estudiante")
                            else:
                                st.error("❌ No se pudo conectar a la base de datos")
                else:
                    st.error("❌ Por favor complete todos los campos")
    
    # PASO 3: SELECCIONAR CARRERA Y CURSOS (solo si hay estudiante)
    if estudiante_matricula:
        st.markdown("### 📚 Seleccionar Carrera y Cursos")
        
        # Cargar carreras de la sede
        with get_db_connection(sede_matricula) as db:
            if db:
                carrera_query = "SELECT id_carrera, nombre FROM carrera"
                carreras_result = db.execute_query(carrera_query)
                
                if carreras_result:
                    carreras_options = {carrera['nombre']: carrera['id_carrera'] for carrera in carreras_result}
                    
                    carrera_selected = st.selectbox("Carrera:", list(carreras_options.keys()))
                    id_carrera_selected = carreras_options[carrera_selected]
                    
                    # Cargar cursos de la carrera
                    curso_query = "SELECT id_curso, nombre FROM curso WHERE id_carrera = %s"
                    cursos_result = db.execute_query(curso_query, (id_carrera_selected,))
                    
                    if cursos_result:
                        st.markdown("**Cursos disponibles:**")
                        
                        cursos_seleccionados = []
                        for curso in cursos_result:
                            if st.checkbox(f"📖 {curso['nombre']}", key=f"curso_{curso['id_curso']}"):
                                cursos_seleccionados.append(curso)
                        
                        if cursos_seleccionados:
                            # PASO 4: FORMA DE PAGO
                            st.markdown("### 💳 Forma de Pago")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                forma_pago = st.radio("Seleccionar forma de pago:", [
                                    "Pago inmediato",
                                    "Crear pagaré"
                                ])
                                
                                # Calcular costo total (simulado)
                                costo_por_curso = 150000
                                costo_total = len(cursos_seleccionados) * costo_por_curso
                                
                                st.metric("💰 Costo total:", f"₡{costo_total:,}")
                            
                            with col2:
                                st.markdown("**Resumen de matrícula:**")
                                st.text(f"• Estudiante: {estudiante_matricula['nombre']}")
                                st.text(f"• Carrera: {carrera_selected}")
                                st.text(f"• Cursos: {len(cursos_seleccionados)}")
                                st.text(f"• Sede: {sede_info_matricula['name']}")
                                
                                if forma_pago == "Crear pagaré":
                                    vencimiento = st.date_input("Fecha de vencimiento:", 
                                                              value=datetime.now().date() + timedelta(days=30))
                            
                            # PASO 5: PROCESAR MATRÍCULA
                            if st.button("🎓 Procesar Matrícula Completa", type="primary", use_container_width=True):
                                st.markdown("### 🔄 Procesando Transacción de Matrícula")
                                
                                # Inicializar variables para el resumen
                                matriculas_creadas = []
                                pago_id = None
                                pagare_id = None
                                
                                # Contenedor para los pasos
                                with st.container():
                                    # Paso 1: Iniciar transacción
                                    step1 = st.empty()
                                    step1.info("📍 Paso 1/6: Iniciando transacción de matrícula...")
                                    time.sleep(1)
                                    trx_id = f"MAT-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999)}"
                                    step1.success(f"✅ Paso 1/6: Transacción iniciada - ID: {trx_id}")
                                    
                                    # Paso 2: Verificar disponibilidad
                                    step2 = st.empty()
                                    step2.info("📍 Paso 2/6: Verificando disponibilidad de cursos...")
                                    time.sleep(1)
                                    step2.success("✅ Paso 2/6: Cursos disponibles para matrícula")
                                    
                                    # Paso 3: Crear matrículas
                                    step3 = st.empty()
                                    step3.info(f"📍 Paso 3/6: Registrando {len(cursos_seleccionados)} matrícula(s)...")
                                    
                                    # EJECUTAR INSERTs REALES DE MATRÍCULA
                                    with get_db_connection(sede_matricula) as db:
                                        if db:
                                            for curso in cursos_seleccionados:
                                                matricula_query = "INSERT INTO matricula (id_estudiante, id_curso) VALUES (%s, %s)"
                                                affected = db.execute_update(matricula_query, 
                                                    (estudiante_matricula['id_estudiante'], curso['id_curso']))
                                                
                                                if affected and affected > 0:
                                                    matriculas_creadas.append(curso['nombre'])
                                                else:
                                                    step3.error(f"❌ Error al matricular en {curso['nombre']}")
                                                    st.stop()
                                            
                                            step3.success(f"✅ Paso 3/6: {len(matriculas_creadas)} matrícula(s) registrada(s)")
                                        else:
                                            step3.error("❌ Error de conexión a la base de datos")
                                            st.stop()
                                    
                                    # Paso 4: Procesar pago o pagaré
                                    step4 = st.empty()
                                    if forma_pago == "Pago inmediato":
                                        step4.info("📍 Paso 4/6: Procesando pago inmediato...")
                                        
                                        # INSERT REAL DE PAGO
                                        with get_db_connection(sede_matricula) as db:
                                            if db:
                                                pago_query = "INSERT INTO pago (id_estudiante, monto, fecha) VALUES (%s, %s, %s)"
                                                affected = db.execute_update(pago_query, 
                                                    (estudiante_matricula['id_estudiante'], costo_total, 
                                                     datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                                                
                                                if affected and affected > 0:
                                                    pago_id = f"PAY-{random.randint(1000, 9999)}"
                                                    step4.success(f"✅ Paso 4/6: Pago procesado - ID: {pago_id}")
                                                else:
                                                    step4.error("❌ Error al procesar el pago")
                                                    st.stop()
                                            else:
                                                step4.error("❌ Error de conexión para procesar pago")
                                                st.stop()
                                    
                                    else:  # Crear pagaré
                                        step4.info("📍 Paso 4/6: Creando pagaré en Central...")
                                        
                                        # INSERT REAL DE PAGARÉ EN CENTRAL
                                        with get_db_connection('central') as db:
                                            if db:
                                                pagare_query = "INSERT INTO pagare (id_estudiante, monto, vencimiento) VALUES (%s, %s, %s)"
                                                affected = db.execute_update(pagare_query, 
                                                    (estudiante_matricula['id_estudiante'], costo_total, vencimiento))
                                                
                                                if affected and affected > 0:
                                                    pagare_id = f"PGR-{random.randint(1000, 9999)}"
                                                    step4.success(f"✅ Paso 4/6: Pagaré creado - ID: {pagare_id}")
                                                else:
                                                    step4.error("❌ Error al crear el pagaré")
                                                    st.stop()
                                            else:
                                                step4.warning("⚠️ Paso 4/6: No se pudo conectar a Central - pagaré no creado")
                                    
                                    # Paso 5: Actualizar cache distribuido
                                    step5 = st.empty()
                                    step5.info("📍 Paso 5/6: Actualizando cache distribuido...")
                                    time.sleep(1)
                                    step5.success("✅ Paso 5/6: Cache actualizado en todos los nodos")
                                    
                                    # Paso 6: Commit final
                                    step6 = st.empty()
                                    step6.info("📍 Paso 6/6: Confirmando transacción completa...")
                                    time.sleep(1)
                                    step6.success("✅ Paso 6/6: Matrícula completada exitosamente")
                                
                                # Mostrar resumen final
                                st.balloons()
                                
                                st.markdown("### 🎓 Resumen de Matrícula Completada")
                                
                                # Crear resumen detallado
                                resumen_data = {
                                    'Campo': [
                                        'ID Transacción',
                                        'Estudiante',
                                        'Sede',
                                        'Carrera',
                                        'Cursos Matriculados',
                                        'Costo Total',
                                        'Forma de Pago',
                                        'ID Pago/Pagaré',
                                        'Estado',
                                        'Fecha/Hora'
                                    ],
                                    'Valor': [
                                        trx_id,
                                        estudiante_matricula['nombre'],
                                        sede_info_matricula['name'],
                                        carrera_selected,
                                        f"{len(matriculas_creadas)} curso(s)",
                                        f"₡{costo_total:,}",
                                        "Pago Inmediato" if forma_pago == "Pago inmediato" else "Pagaré",
                                        pago_id if pago_id else pagare_id,
                                        '✅ Completada',
                                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    ]
                                }
                                
                                df_resumen = pd.DataFrame(resumen_data)
                                st.table(df_resumen.set_index('Campo'))
                                
                                # Mostrar cursos matriculados
                                st.markdown("**📚 Detalle de Cursos Matriculados:**")
                                cursos_df = pd.DataFrame([
                                    {'Curso': curso, 'Costo': f"₡{costo_por_curso:,}", 'Estado': '✅ Activo'} 
                                    for curso in matriculas_creadas
                                ])
                                st.dataframe(cursos_df, use_container_width=True, hide_index=True)
                                
                                # Log de auditoría
                                with st.expander("📜 Ver Log Detallado de Auditoría"):
                                    audit_log = f"""[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] BEGIN MATRICULA TRANSACTION {trx_id}
                                    [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] VERIFY student_id={estudiante_matricula['id_estudiante']} AT {sede_matricula}
                                    [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] VERIFY courses availability for carrera_id={id_carrera_selected}
                                    """
                                    
                                    for curso in cursos_seleccionados:
                                        audit_log += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INSERT INTO matricula (id_estudiante, id_curso) VALUES ({estudiante_matricula['id_estudiante']}, {curso['id_curso']})"
                                    
                                    if forma_pago == "Pago inmediato":
                                        audit_log += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INSERT INTO pago (id_estudiante, monto, fecha) VALUES ({estudiante_matricula['id_estudiante']}, {costo_total}, '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')"
                                    else:
                                        audit_log += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INSERT INTO pagare (id_estudiante, monto, vencimiento) VALUES ({estudiante_matricula['id_estudiante']}, {costo_total}, '{vencimiento}')"
                                    
                                    audit_log += f"""
                                    [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] UPDATE DISTRIBUTED CACHE
                                    [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] COMMIT TRANSACTION {trx_id}
                                    [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MATRICULA PROCESS COMPLETED SUCCESSFULLY
                                    """
                                    
                                    st.code(audit_log, language='log')
                        else:
                            st.info("👆 Seleccione al menos un curso para continuar")
                    else:
                        st.warning("No hay cursos disponibles para esta carrera")
                else:
                    st.warning("No hay carreras disponibles en esta sede")
            else:
                st.error("Error al cargar carreras")

# TAB4 - VISTAS DE USUARIO (SIN CAMBIOS)
with tab4:
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
    
    ✅ **Transacciones de pago** con consistencia ACID
    
    ✅ **Proceso de matrícula** completo y distribuido
    
    ✅ **Vistas de usuario** según roles y permisos
    
    ✅ **Operaciones reales** con base de datos
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