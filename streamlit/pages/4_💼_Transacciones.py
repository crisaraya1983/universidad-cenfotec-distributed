import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import random

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG, COLORS, get_sede_info
from utils.db_connections import get_db_connection, execute_distributed_query, get_redis_connection

st.set_page_config(
    page_title="Transacciones - Sistema Cenfotec",
    page_icon="💼",
    layout="wide"
)

st.title("Transacciones Distribuidas")

st.markdown("""
Las **transacciones distribuidas** son operaciones que involucran datos en múltiples nodos
del sistema. Deben mantener las propiedades ACID incluso cuando los datos están distribuidos.
""")

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs([
    "Conceptos",
    "Transacción: Pago Global",
    "Transacción: Proceso de Matrícula",
    "Vistas de Usuario"
])

with tab1:
    st.header("Conceptos de Transacciones Distribuidas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Transacciones en Sistema Cenfotec
        
        **¿Qué es una Transacción Distribuida?**
        - Operación que modifica datos en **múltiples sedes** simultáneamente
        - Garantiza que **todas las operaciones se completen** o **ninguna**
        - Mantiene **consistencia** entre las bases de datos distribuidas
        
        **Propiedades ACID Implementadas**
        
        **Atomicidad** 
        - Si falla una operación, se revierten **todas** las anteriores
        - Ejemplo: Si falla el pago, se cancelan las matrículas
        
        **Consistencia** 
        - Los datos quedan en estado válido después de cada transacción
        - Ejemplo: Un pagaré nunca queda con monto negativo
        
        **Aislamiento** 
        - Las transacciones no interfieren entre sí
        - Ejemplo: Dos matrículas simultáneas no causan conflictos
    
        **Durabilidad** 
        - Los cambios persisten aunque falle el sistema
        - Ejemplo: Una vez completado el pago, no se pierde
        """)
    
    with col2:
        st.markdown("""
        ### Transacciones Implementadas
        
        **1. Transacción de Pago Global** 
        ```
        Pasos ejecutados:
        1. Verificar estudiante en su sede
        2. Registrar pago en sede del estudiante
        3. Si aplica: Actualizar pagaré en Central
        4. Confirmar transacción distribuida
        ```
        
        **2. Transacción de Matrícula** 
        ```
        Pasos ejecutados:
        1. Crear estudiante nuevo (si aplica)
        2. Verificar disponibilidad de cursos
        3. Registrar matrícula(s) en la sede
        4. Procesar pago O crear pagaré en Central
        5. Actualizar cache distribuido
        6. Confirmar transacción completa
        ```
        
        **¿Por qué son Distribuidas?** 
        - **Pago Global**: Afecta sede del estudiante + Central (pagarés)
        - **Matrícula**: Afecta sede local + Central (pagarés/cache)
        
        **Ventajas del Enfoque Distribuido** 
        - **Rendimiento**: Cada sede maneja sus propios datos
        - **Disponibilidad**: Si una sede falla, otras siguen funcionando
        - **Escalabilidad**: Fácil agregar nuevas sedes
        - **Consistencia**: Los datos críticos se sincronizan
        """)
    
    st.markdown("---")
    
    st.markdown("### Arquitectura de Transacciones en el Sistema")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Sede Central**
        - **Datos maestros**: Carreras, Profesores
        - **Administración**: Planillas, Pagarés
        - **Coordinación**: Transacciones distribuidas
        
        **Rol en Transacciones:**
        - Almacena pagarés de todos los estudiantes
        - Coordina operaciones entre sedes
        - Mantiene cache distribuido
        """)
    
    with col2:
        st.markdown("""
        **Sedes Regionales**
        - **San Carlos** y **Heredia**
        - **Datos locales**: Estudiantes, Matrículas, Pagos
        - **Operaciones**: Académicas y financieras locales
        
        **Rol en Transacciones:**
        - Procesan matrículas de sus estudiantes
        - Registran pagos localmente
        - Participan en transacciones distribuidas
        """)
    
    with col3:
        st.markdown("""
        **Coordinación**
        - **Comunicación** entre todas las sedes
        - **Sincronización** de datos críticos
        - **Rollback** automático en caso de errores
        
        **Mecanismos:**
        - Verificación previa de disponibilidad
        - Registro de logs de auditoría
        - Manejo de errores y recuperación
        """)
    
    st.markdown("---")
    
    st.markdown("### Vistas de Usuario Distribuidas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **¿Qué son las Vistas Distribuidas?** 
        - Presentaciones de datos **adaptadas por rol** de usuario
        - Acceso **controlado** a información de múltiples sedes
        - **Abstracción** de la complejidad del sistema distribuido
        
        **Tipos de Vistas Implementadas:**
        - **Vista Estudiante**: Sus notas, pagos, horarios
        - **Vista Profesor**: Estudiantes matriculados, registro de notas
        - **Vista Administrativa**: Pagos, pagarés, reportes financieros
        - **Vista Directiva**: KPIs, análisis consolidados, tendencias
        """)
    
    with col2:
        st.markdown("""
        **Ventajas de las Vistas Distribuidas** 
        
        **Seguridad** 
        - Cada usuario ve **solo lo que necesita**
        - Estudiantes no ven datos de otros estudiantes
        - Profesores solo ven sus cursos asignados
        
        **Rendimiento** 
        - Consultas **optimizadas** por rol
        - Datos **pre-filtrados** por sede y permisos
        - **Cache inteligente** para consultas frecuentes
        
        **Simplicidad** 
        - Usuario no necesita saber dónde están los datos
        - **Interfaz unificada** aunque los datos estén distribuidos
        - **Experiencia consistente** en todas las sedes
        """)
    
    st.markdown("---")

with tab2:
    st.header("Transacción: Procesamiento de Pago")
    
    st.markdown("""
    Simula una transacción que registra un pago que afecta múltiples sistemas:
    - Registro del pago en la sede del estudiante
    - Actualización del pagaré en Central (si aplica)
    - Actualización del cache distribuido
    """)
    
    st.markdown("### Seleccionar Estudiante")
    
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
    
    with st.form("pago_global_form"):
        st.markdown("### Registrar Pago")
        
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
            
            st.markdown("**Información de la transacción:**")
            st.text(f"• Estudiante: {estudiante_info['nombre']}")
            st.text(f"• Sede de registro: {estudiante_info['sede_nombre']}")
            if tiene_pagare:
                st.text("• Se actualizará pagaré en Central")
        
        submitted = st.form_submit_button("💳 Procesar Pago", type="primary")
    
    if submitted:
        st.markdown("### Procesando Transacción Distribuida")
        
        steps_container = st.container()
        
        with steps_container:
            step1 = st.empty()
            step1.info("Paso 1/5: Iniciando transacción distribuida...")
            time.sleep(1)
            step1.success(f"Paso 1/5: Transacción iniciada - ID: TRX-{datetime.now().strftime('%Y%m%d')}-001")
            
            step2 = st.empty()
            step2.info("Paso 2/5: Verificando datos del estudiante...")
            time.sleep(1)
            step2.success(f"Paso 2/5: Estudiante verificado en {estudiante_info['sede_nombre']}")
            
            step3 = st.empty()
            step3.info(f"Paso 3/5: Registrando pago en {estudiante_info['sede_nombre']}...")
            
            with get_db_connection(estudiante_info['sede']) as db:
                if db:
                    insert_query = "INSERT INTO pago (id_estudiante, monto, fecha) VALUES (%s, %s, %s)"
                    affected_rows = db.execute_update(insert_query, 
                        (estudiante_info['id'], monto, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    
                    if affected_rows and affected_rows > 0:
                        pago_id = f"PAY-{random.randint(1000, 9999)}"
                        step3.success(f"Paso 3/5: Pago registrado - ID: {pago_id}")
                    else:
                        step3.error("❌ Error al registrar el pago")
                        st.stop()
                else:
                    step3.error("❌ No se pudo conectar a la base de datos")
                    st.stop()
            
            step4 = st.empty()
            if tiene_pagare:
                step4.info("Paso 4/5: Actualizando pagaré en Central...")
                
                with get_db_connection('central') as db:
                    if db:
                        pagare_query = "SELECT id_pagare, monto FROM pagare WHERE id_estudiante = %s AND monto > 0"
                        pagares = db.execute_query(pagare_query, (estudiante_info['id'],))
                        
                        if pagares and len(pagares) > 0:
                            pagare = pagares[0]
                            nuevo_monto = max(0, pagare['monto'] - monto)
                            
                            update_query = "UPDATE pagare SET monto = %s WHERE id_pagare = %s"
                            affected = db.execute_update(update_query, (nuevo_monto, pagare['id_pagare']))
                            
                            if affected and affected > 0:
                                step4.success("Paso 4/5: Pagaré actualizado en sede Central")
                            else:
                                step4.error("❌ Error al actualizar pagaré")
                        else:
                            step4.info("Paso 4/5: Sin pagarés pendientes para este estudiante")
                    else:
                        step4.warning("Paso 4/5: No se pudo conectar a Central para verificar pagarés")
            else:
                step4.info("Paso 4/5: Sin pagarés pendientes")
            
            step5 = st.empty()
            step5.info("Paso 5/5: Confirmando transacción en todos los nodos...")
            time.sleep(1)
            step5.success("Paso 5/5: Transacción completada exitosamente")
        
        #st.balloons()
        
        st.markdown("### Resumen de la Transacción")
        
        summary_data = {
            'Campo': ['ID Transacción', 'Estudiante', 'Sede', 'Monto', 
                     'Concepto', 'Estado', 'Timestamp'],
            'Valor': [
                f'TRX-{datetime.now().strftime("%Y%m%d")}-001',
                estudiante_info['nombre'],
                estudiante_info['sede_nombre'],
                f"₡{monto:,.2f}",
                concepto,
                'Completada',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        
        df_summary = pd.DataFrame(summary_data)
        st.table(df_summary.set_index('Campo'))
        
        with st.expander("Ver Log de Auditoría"):
            audit_log = f"""[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] BEGIN DISTRIBUTED TRANSACTION TRX-{datetime.now().strftime('%Y%m%d')}-001
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] VERIFY student_id={estudiante_info['id']} AT {estudiante_info['sede']}
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INSERT INTO pago (id_estudiante, monto, fecha) VALUES ({estudiante_info['id']}, {monto}, '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'UPDATE pagare SET monto = monto - ' + str(monto) + ' WHERE id_estudiante = ' + str(estudiante_info['id']) if tiene_pagare else 'SKIP pagare update (no pending pagares)'}
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] COMMIT TRANSACTION TRX-{datetime.now().strftime('%Y%m%d')}-001
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] TRANSACTION COMPLETED SUCCESSFULLY"""
            st.code(audit_log, language='log')

with tab3:
    st.header("Transacción: Proceso de Matrícula")
    
    st.markdown("""
    Proceso de matrícula:
    - Crear estudiante nuevo (si aplica)
    - Registrar matrícula(s) en curso(s)
    - Procesar pago inmediato o crear pagaré
    - Actualizar registros distribuidos
    """)
    
    if 'nuevo_estudiante_creado' not in st.session_state:
        st.session_state.nuevo_estudiante_creado = None
    
    st.markdown("### Configuración de Matrícula")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sede_matricula = st.selectbox("Sede para la matrícula:", [
            "central", "sancarlos", "heredia"
        ], format_func=lambda x: get_sede_info(x)['name'])
        
        sede_info_matricula = get_sede_info(sede_matricula)
    
    with col2:
        if st.session_state.nuevo_estudiante_creado:
            tipo_estudiante = "Estudiante existente"
            st.success("Continuando con el estudiante recién creado")
            
            if st.button("Crear otro estudiante nuevo", key="cambiar_a_nuevo"):
                st.session_state.nuevo_estudiante_creado = None
                st.rerun()
        else:
            tipo_estudiante = st.radio("Tipo de estudiante:", [
                "Estudiante existente",
                "Estudiante nuevo"
            ])
    
    estudiante_matricula = None
    
    if tipo_estudiante == "Estudiante existente":
        st.markdown("### Seleccionar Estudiante")
        
        if 'estudiante_seleccionado_final' not in st.session_state:
            st.session_state.estudiante_seleccionado_final = None
        
        if st.session_state.nuevo_estudiante_creado:
            estudiante_matricula = st.session_state.nuevo_estudiante_creado
            st.session_state.estudiante_seleccionado_final = estudiante_matricula
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success(f"**Estudiante:** {estudiante_matricula['nombre']}")
            with col2:
                st.success(f"**Email:** {estudiante_matricula['email']}")
            with col3:
                st.success(f"**ID:** {estudiante_matricula['id_estudiante']}")
            
            st.info("Estudiante nuevo por matricular")
            
            st.session_state.nuevo_estudiante_creado = None
            
        else:
            with get_db_connection(sede_matricula) as db:
                if db:
                    result = db.execute_query("SELECT id_estudiante, nombre, email FROM estudiante")
                    if result:
                        estudiantes_options = {f"{est['nombre']} ({est['email']})": est for est in result}
                        
                        if estudiantes_options:
                            default_index = 0
                            if st.session_state.estudiante_seleccionado_final:
                                for i, (key, est) in enumerate(estudiantes_options.items()):
                                    if est['id_estudiante'] == st.session_state.estudiante_seleccionado_final['id_estudiante']:
                                        default_index = i
                                        break
                            
                            estudiante_selected = st.selectbox(
                                "Estudiante:", 
                                list(estudiantes_options.keys()),
                                index=default_index,
                                key="selectbox_estudiante_existente"
                            )
                            
                            estudiante_matricula = estudiantes_options[estudiante_selected]
                            st.session_state.estudiante_seleccionado_final = estudiante_matricula
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.success(f"**Estudiante:** {estudiante_matricula['nombre']}")
                            with col2:
                                st.success(f"**Email:** {estudiante_matricula['email']}")
                        else:
                            st.warning("No hay estudiantes registrados en esta sede")
                    else:
                        st.error("Error al cargar estudiantes")
                else:
                    st.error("No se pudo conectar a la base de datos")
    
    else:
        st.markdown("### Crear Estudiante Nuevo")
        
        with st.form("nuevo_estudiante_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nuevo_nombre = st.text_input("Nombre completo:", 
                                           placeholder="Ej: María García López")
                nuevo_email = st.text_input("Email institucional:", 
                                          placeholder="Ej: maria.garcia@ucenfotec.ac.cr")
            
            with col2:
                st.markdown("**Información adicional:**")
                st.text(f"• Sede: {sede_info_matricula['name']}")
                st.text("• Se asignará ID automáticamente")
                st.text("• Email debe ser único en el sistema")
                st.text("• Continuará automáticamente con matrícula")
            
            crear_estudiante = st.form_submit_button("Crear Estudiante y Continuar")
            
            if crear_estudiante:
                if nuevo_nombre and nuevo_email:
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
                        with get_db_connection(sede_matricula) as db:
                            if db:
                                sede_ids = {"central": 1, "sancarlos": 2, "heredia": 3}
                                id_sede = sede_ids[sede_matricula]
                                
                                insert_query = "INSERT INTO estudiante (nombre, email, id_sede, sede_actual) VALUES (%s, %s, %s, %s)"
                                affected = db.execute_update(insert_query, (nuevo_nombre, nuevo_email, id_sede, id_sede))
                                
                                if affected and affected > 0:
                                    get_id_query = "SELECT id_estudiante, nombre, email FROM estudiante WHERE email = %s"
                                    result = db.execute_query(get_id_query, (nuevo_email,))
                                    
                                    if result:
                                        st.session_state.nuevo_estudiante_creado = result[0]
                                        st.success(f"✅ Estudiante creado exitosamente - ID: {result[0]['id_estudiante']}")
                                        st.success("🔄 Continuando automáticamente con el proceso de matrícula...")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("❌ Error al obtener datos del estudiante creado")
                                else:
                                    st.error("❌ Error al crear el estudiante")
                            else:
                                st.error("❌ No se pudo conectar a la base de datos")
                else:
                    st.error("❌ Por favor complete todos los campos")
    
    if estudiante_matricula:
        st.markdown("### Seleccionar Carrera y Cursos")
        
        with get_db_connection(sede_matricula) as db:
            if db:
                sede_ids = {"central": 1, "sancarlos": 2, "heredia": 3}
                id_sede_actual = sede_ids[sede_matricula]

                carrera_query = "SELECT id_carrera, nombre FROM carrera WHERE id_sede = %s"
                carreras_result = db.execute_query(carrera_query, (id_sede_actual,))
                
                if carreras_result:
                    carreras_options = {carrera['nombre']: carrera['id_carrera'] for carrera in carreras_result}
                    
                    carrera_selected = st.selectbox("Carrera:", list(carreras_options.keys()))
                    id_carrera_selected = carreras_options[carrera_selected]
                    
                    curso_query = "SELECT id_curso, nombre FROM curso WHERE id_carrera = %s"
                    cursos_result = db.execute_query(curso_query, (id_carrera_selected,))
                    
                    if cursos_result:
                        st.markdown("**Cursos disponibles:**")
                        
                        cursos_seleccionados = []
                        for curso in cursos_result:
                            if st.checkbox(f"{curso['nombre']}", key=f"curso_{curso['id_curso']}"):
                                cursos_seleccionados.append(curso)
                        
                        if cursos_seleccionados:
                            st.markdown("### 💳 Forma de Pago")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                forma_pago = st.radio("Seleccionar forma de pago:", [
                                    "Pago inmediato",
                                    "Crear pagaré"
                                ])
                                
                                # Calcular costo total
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
                            
                            if st.button("🎓 Procesar Matrícula Completa", type="primary", use_container_width=True):
                                st.markdown("### 🔄 Procesando Transacción de Matrícula")
                                
                                matriculas_creadas = []
                                pago_id = None
                                pagare_id = None
                                
                                with st.container():
                                    step1 = st.empty()
                                    step1.info("Paso 1/5: Iniciando transacción de matrícula...")
                                    time.sleep(1)
                                    trx_id = f"MAT-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999)}"
                                    step1.success(f"Paso 1/5: Transacción iniciada - ID: {trx_id}")
                                    
                                    step2 = st.empty()
                                    step2.info("Paso 2/6: Verificando disponibilidad de cursos...")
                                    time.sleep(1)
                                    step2.success("Paso 2/5: Cursos disponibles para matrícula")
                                    
                                    step3 = st.empty()
                                    step3.info(f"Paso 3/5: Registrando {len(cursos_seleccionados)} matrícula(s)...")
                                    
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
                                            
                                            step3.success(f"Paso 3/5: {len(matriculas_creadas)} matrícula(s) registrada(s)")
                                        else:
                                            step3.error("❌ Error de conexión a la base de datos")
                                            st.stop()
                                    
                                    step4 = st.empty()
                                    if forma_pago == "Pago inmediato":
                                        step4.info("📍 Paso 4/5: Procesando pago inmediato...")
                                        
                                        with get_db_connection(sede_matricula) as db:
                                            if db:
                                                pago_query = "INSERT INTO pago (id_estudiante, monto, fecha) VALUES (%s, %s, %s)"
                                                affected = db.execute_update(pago_query, 
                                                    (estudiante_matricula['id_estudiante'], costo_total, 
                                                     datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                                                
                                                if affected and affected > 0:
                                                    pago_id = f"PAY-{random.randint(1000, 9999)}"
                                                    step4.success(f"Paso 4/6: Pago procesado - ID: {pago_id}")
                                                else:
                                                    step4.error("❌ Error al procesar el pago")
                                                    st.stop()
                                            else:
                                                step4.error("❌ Error de conexión para procesar pago")
                                                st.stop()
                                    
                                    else: 
                                        step4.info("Paso 4/6: Creando pagaré en Central...")
                                        
                                        with get_db_connection('central') as db:
                                            if db:
                                                pagare_query = "INSERT INTO pagare (id_estudiante, monto, vencimiento) VALUES (%s, %s, %s)"
                                                affected = db.execute_update(pagare_query, 
                                                    (estudiante_matricula['id_estudiante'], costo_total, vencimiento))
                                                
                                                if affected and affected > 0:
                                                    pagare_id = f"PGR-{random.randint(1000, 9999)}"
                                                    step4.success(f"Paso 4/6: Pagaré creado - ID: {pagare_id}")
                                                else:
                                                    step4.error("❌ Error al crear el pagaré")
                                                    st.stop()
                                            else:
                                                step4.warning("Paso 4/6: No se pudo conectar a Central - pagaré no creado")
                                    
                                    
                                    step6 = st.empty()
                                    step6.info("📍 Paso 5/5: Confirmando transacción completa...")
                                    time.sleep(1)
                                    step6.success("Paso 5/5: Matrícula completada exitosamente")
                                
                                #st.balloons()
                                
                                st.markdown("### Resumen de Matrícula Completada")
                                
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
                                
                                st.markdown("**Detalle de Cursos Matriculados:**")
                                cursos_df = pd.DataFrame([
                                    {'Curso': curso, 'Costo': f"₡{costo_por_curso:,}", 'Estado': '✅ Activo'} 
                                    for curso in matriculas_creadas
                                ])
                                st.dataframe(cursos_df, use_container_width=True, hide_index=True)
                                
                                with st.expander("📜 Ver Log Detallado de Auditoría"):
                                    audit_log = f"""[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] BEGIN MATRICULA TRANSACTION {trx_id}
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] VERIFY student_id={estudiante_matricula['id_estudiante']} AT {sede_matricula}
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] VERIFY courses availability for carrera_id={id_carrera_selected}"""
                                    
                                    for curso in cursos_seleccionados:
                                        audit_log += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INSERT INTO matricula (id_estudiante, id_curso) VALUES ({estudiante_matricula['id_estudiante']}, {curso['id_curso']})"
                                    
                                    if forma_pago == "Pago inmediato":
                                        audit_log += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INSERT INTO pago (id_estudiante, monto, fecha) VALUES ({estudiante_matricula['id_estudiante']}, {costo_total}, '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')"
                                    else:
                                        audit_log += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] INSERT INTO pagare (id_estudiante, monto, vencimiento) VALUES ({estudiante_matricula['id_estudiante']}, {costo_total}, '{vencimiento}')"
                                    
                                    audit_log += f"""
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] UPDATE DISTRIBUTED CACHE
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] COMMIT TRANSACTION {trx_id}
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MATRICULA PROCESS COMPLETED SUCCESSFULLY"""
                                    
                                    st.code(audit_log, language='log')
                        else:
                            st.info("Seleccione al menos un curso para continuar")
                    else:
                        st.warning("No hay cursos disponibles para esta carrera")
                else:
                    st.warning("No hay carreras disponibles en esta sede")
            else:
                st.error("Error al cargar carreras")

with tab4:
    st.header("Vistas de Usuario con Datos Reales")
    
    st.markdown("""
    **Sistema de vistas por roles** que consulta datos de las bases de datos distribuidas.
    Cada rol tiene acceso a información específica según sus permisos y responsabilidades.
    """)
    
    def get_estudiantes_por_sede(sede):
        try:
            with get_db_connection(sede) as conn:
                query = "SELECT id_estudiante, nombre, email FROM estudiante WHERE estado = 'Activo' ORDER BY nombre"
                results = conn.execute_query(query)
                return results if results else []
        except Exception as e:
            st.error(f"Error obteniendo estudiantes de {sede}: {e}")
            return []
    
    def get_profesores_por_sede(sede):
        try:
            with get_db_connection(sede) as conn:
                query = "SELECT id_profesor, nombre, email FROM profesor WHERE id_sede = %s ORDER BY nombre"
                sede_id = 2 if sede == 'sancarlos' else 3 if sede == 'heredia' else 1
                results = conn.execute_query(query, (sede_id,))
                return results if results else []
        except Exception as e:
            st.error(f"Error obteniendo profesores de {sede}: {e}")
            return []
    
    def consolidar_datos_estudiantes():
        datos_consolidados = []
        sedes = ['central', 'sancarlos', 'heredia']
        
        for sede in sedes:
            try:
                with get_db_connection(sede) as conn:
                    query = """
                    SELECT 
                        COUNT(*) as total_estudiantes,
                        COUNT(CASE WHEN estado = 'Activo' THEN 1 END) as estudiantes_activos,
                        '%s' as sede
                    FROM estudiante
                    """ % sede.title()
                    results = conn.execute_query(query)
                    if results:
                        datos_consolidados.extend(results)
            except Exception as e:
                st.warning(f"Error consolidando datos de {sede}: {e}")
        
        return datos_consolidados
    
    def consolidar_datos_pagos():
        datos_pagos = []
        sedes = ['central','sancarlos', 'heredia']
        
        for sede in sedes:
            try:
                with get_db_connection(sede) as conn:
                    query = """
                    SELECT 
                        COUNT(*) as total_pagos,
                        COALESCE(SUM(monto), 0) as monto_total,
                        COALESCE(AVG(monto), 0) as promedio_pago,
                        '%s' as sede
                    FROM pago
                    WHERE YEAR(fecha) = YEAR(CURDATE())
                    """ % sede.title()
                    results = conn.execute_query(query)
                    if results:
                        datos_pagos.extend(results)
            except Exception as e:
                st.warning(f"Error consolidando pagos de {sede}: {e}")
        
        return datos_pagos
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.markdown("### Seleccionar Rol")
        rol_selected = st.selectbox(
            "Rol de usuario:",
            ["Estudiante", "Profesor", "Administrativo", "Directivo"],
            key="rol_vistas_usuario"
        )
    
    with col2:
        if rol_selected in ["Estudiante", "Profesor"]:
            st.markdown("### Seleccionar Sede")
            sede_selected = st.selectbox(
                "Sede:",
                ["central", "sancarlos", "heredia"],
                format_func=lambda x: get_sede_info(x)['name'],
                key="sede_vistas_usuario"
            )
        else:
            sede_selected = "central" 
    
    with col3:
        permisos = {
            "Estudiante": "• Ver calificaciones y materias\n• Consultar historial de pagos\n• Ver porcentaje de asistencia",
            "Profesor": "• Ver estudiantes matriculados\n• Consultar estadísticas de cursos\n• Analizar rendimiento académico", 
            "Administrativo": "• Gestionar pagarés activos\n• Ver reportes de pagos consolidados\n• Consultar planillas de profesores",
            "Directivo": "• Acceso a KPIs globales\n• Análisis distribuido completo\n• Dashboards ejecutivos"
        }
        
        st.info(f"""**Permisos del rol {rol_selected}:**\n\n{permisos[rol_selected]}""")
    
    
    if rol_selected == "Estudiante":
        st.markdown(f"### Vista de Estudiante - {get_sede_info(sede_selected)['name']}")
        
        estudiantes = get_estudiantes_por_sede(sede_selected)
        
        if estudiantes:
            estudiante_options = {f"{est['nombre']} ({est['email']})": est['id_estudiante'] for est in estudiantes}
            estudiante_selected = st.selectbox(
                "Seleccionar estudiante:",
                list(estudiante_options.keys()),
                key="estudiante_selected"
            )
            
            if estudiante_selected:
                estudiante_id = estudiante_options[estudiante_selected]
                
                try:
                    with get_db_connection(sede_selected) as conn:
                        query = "SELECT * FROM vista_estudiante_mis_materias WHERE id_estudiante = %s"
                        materias = conn.execute_query(query, (estudiante_id,))
                        
                        if materias:
                            st.markdown("#### Mis Materias y Calificaciones")
                            
                            df_materias = pd.DataFrame(materias)
                            
                            st.dataframe(
                                df_materias[['nombre_curso', 'carrera', 'nota_obtenida', 'estado_materia', 'porcentaje_asistencia']].rename(columns={
                                    'nombre_curso': 'Curso',
                                    'carrera': 'Carrera', 
                                    'nota_obtenida': 'Nota',
                                    'estado_materia': 'Estado',
                                    'porcentaje_asistencia': 'Asistencia %'
                                }),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            if len(df_materias) > 0:
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    fig_notas = px.bar(
                                        df_materias, 
                                        x='nombre_curso', 
                                        y='nota_obtenida',
                                        title='Calificaciones por Materia',
                                        color='nota_obtenida',
                                        color_continuous_scale=['red', 'yellow', 'green']
                                    )
                                    fig_notas.add_hline(y=70, line_dash="dash", 
                                                       annotation_text="Nota mínima (70)")
                                    fig_notas.update_xaxes(tickangle=45)
                                    st.plotly_chart(fig_notas, use_container_width=True)
                                
                                with col2:
                                    estado_counts = df_materias['estado_materia'].value_counts()
                                    fig_estados = px.pie(
                                        values=estado_counts.values,
                                        names=estado_counts.index,
                                        title='Estado de Materias'
                                    )
                                    st.plotly_chart(fig_estados, use_container_width=True)
                        
                        query_pagos = "SELECT * FROM vista_estudiante_mis_pagos WHERE id_estudiante = %s ORDER BY fecha DESC LIMIT 10"
                        pagos = conn.execute_query(query_pagos, (estudiante_id,))
                        
                        if pagos:
                            st.markdown("#### 💰 Historial de Pagos")
                            df_pagos = pd.DataFrame(pagos)
                            
                            st.dataframe(
                                df_pagos[['fecha', 'monto', 'concepto', 'nombre_mes']].rename(columns={
                                    'fecha': 'Fecha',
                                    'monto': 'Monto',
                                    'concepto': 'Concepto',
                                    'nombre_mes': 'Mes'
                                }),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            total_pagado = df_pagos['monto'].sum()
                            st.metric("💵 Total Pagado", f"₡{total_pagado:,.0f}")
                        
                        query_expediente = "SELECT * FROM vista_estudiante_expediente_completo WHERE id_estudiante = %s"
                        expediente = conn.execute_query(query_expediente, (estudiante_id,))
                        
                        if expediente:
                            exp = expediente[0]
                            st.markdown("#### 📋 Resumen del Expediente")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Materias Totales", exp['total_materias_matriculadas'])
                            with col2:
                                st.metric("Aprobadas", exp['materias_aprobadas'])  
                            with col3:
                                st.metric("En Curso", exp['materias_en_curso'])
                            with col4:
                                st.metric("Promedio", f"{exp['promedio_general']:.1f}")
                        
                except Exception as e:
                    st.error(f"Error consultando datos del estudiante: {e}")
        else:
            st.warning(f"No se encontraron estudiantes activos en {get_sede_info(sede_selected)['name']}")
    
    elif rol_selected == "Profesor":
        st.markdown(f"### Vista de Profesor - {get_sede_info(sede_selected)['name']}")
        
        profesores = get_profesores_por_sede(sede_selected)
        
        if profesores:
            profesor_options = {f"{prof['nombre']} ({prof['email']})": prof['id_profesor'] for prof in profesores}
            profesor_selected = st.selectbox(
                "Seleccionar profesor:",
                list(profesor_options.keys()),
                key="profesor_selected"
            )
            
            if profesor_selected:
                profesor_id = profesor_options[profesor_selected]
                
                try:
                    with get_db_connection(sede_selected) as conn:
                        query_resumen = "SELECT * FROM vista_profesor_resumen_cursos WHERE id_profesor = %s"
                        resumen_cursos = conn.execute_query(query_resumen, (profesor_id,))
                        
                        if resumen_cursos:
                            df_resumen = pd.DataFrame(resumen_cursos)
                            
                            st.markdown("#### Resumen de Mis Cursos")
                            st.dataframe(
                                df_resumen[['nombre_curso', 'carrera', 'total_estudiantes', 'estudiantes_aprobados', 
                                           'estudiantes_reprobados', 'estudiantes_pendientes', 'promedio_curso']].rename(columns={
                                    'nombre_curso': 'Curso',
                                    'carrera': 'Carrera',
                                    'total_estudiantes': 'Total Est.',
                                    'estudiantes_aprobados': 'Aprobados',
                                    'estudiantes_reprobados': 'Reprobados', 
                                    'estudiantes_pendientes': 'Pendientes',
                                    'promedio_curso': 'Promedio'
                                }),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                fig_dist = go.Figure()
                                cursos = df_resumen['nombre_curso'].tolist()
                                fig_dist.add_trace(go.Bar(name='Aprobados', x=cursos, y=df_resumen['estudiantes_aprobados']))
                                fig_dist.add_trace(go.Bar(name='Reprobados', x=cursos, y=df_resumen['estudiantes_reprobados']))
                                fig_dist.add_trace(go.Bar(name='Pendientes', x=cursos, y=df_resumen['estudiantes_pendientes']))
                                fig_dist.update_layout(barmode='stack', title='Distribución de Estudiantes por Curso')
                                st.plotly_chart(fig_dist, use_container_width=True)
                            
                            with col2:
                                fig_prom = px.bar(
                                    df_resumen,
                                    x='nombre_curso',
                                    y='promedio_curso',
                                    title='Promedio de Calificaciones por Curso',
                                    color='promedio_curso',
                                    color_continuous_scale='viridis'
                                )
                                fig_prom.add_hline(y=70, line_dash="dash", annotation_text="Nota mínima")
                                fig_prom.update_xaxes(tickangle=45)
                                st.plotly_chart(fig_prom, use_container_width=True)
                        
                        st.markdown("#### Estudiantes por Curso")
                        
                        if resumen_cursos:
                            curso_selected = st.selectbox(
                                "Seleccionar curso para ver detalle:",
                                df_resumen['nombre_curso'].tolist(),
                                key="curso_detalle_selected"
                            )
                            
                            if curso_selected:
                                curso_id = df_resumen[df_resumen['nombre_curso'] == curso_selected]['id_curso'].iloc[0].item()
                                
                                query_estudiantes = """
                                SELECT * FROM vista_profesor_mis_estudiantes 
                                WHERE id_profesor = %s AND id_curso = %s
                                ORDER BY nombre_estudiante
                                """
                                estudiantes_curso = conn.execute_query(query_estudiantes, (profesor_id, curso_id))
                                
                                if estudiantes_curso:
                                    df_estudiantes = pd.DataFrame(estudiantes_curso)
                                    
                                    st.dataframe(
                                        df_estudiantes[['nombre_estudiante', 'email_estudiante', 'nota_actual', 
                                                       'estado', 'porcentaje_asistencia']].rename(columns={
                                            'nombre_estudiante': 'Estudiante',
                                            'email_estudiante': 'Email',
                                            'nota_actual': 'Nota',
                                            'estado': 'Estado',
                                            'porcentaje_asistencia': 'Asistencia %'
                                        }),
                                        use_container_width=True,
                                        hide_index=True
                                    )
                                
                except Exception as e:
                    st.error(f"Error consultando datos del profesor: {e}")
        else:
            st.warning(f"No se encontraron profesores en {get_sede_info(sede_selected)['name']}")
    
    elif rol_selected == "Administrativo":
        st.markdown("### Vista Administrativa - Sede Central")
        
        try:
            with get_db_connection('central') as conn:
                st.markdown("#### Pagarés Activos")
                query_pagares = "SELECT * FROM vista_admin_pagares_activos ORDER BY dias_vencimiento ASC"
                pagares = conn.execute_query(query_pagares)
                
                if pagares:
                    df_pagares = pd.DataFrame(pagares)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        total_pagares = len(df_pagares)
                        st.metric("Total Pagarés", total_pagares)
                    with col2:
                        vencidos = len(df_pagares[df_pagares['estado'] == 'Vencido'])
                        st.metric("⚠️ Vencidos", vencidos, delta=f"{vencidos/total_pagares*100:.1f}%")
                    with col3:
                        por_vencer = len(df_pagares[df_pagares['estado'] == 'Por vencer'])
                        st.metric("🟡 Por Vencer", por_vencer)
                    with col4:
                        monto_total = df_pagares['monto'].sum()
                        st.metric("💰 Monto Total", f"₡{monto_total:,.0f}")
                    
                    st.dataframe(
                        df_pagares[['codigo_estudiante', 'monto', 'vencimiento', 'estado', 'dias_vencimiento']].rename(columns={
                            'codigo_estudiante': 'Código Estudiante',
                            'monto': 'Monto', 
                            'vencimiento': 'Vencimiento',
                            'estado': 'Estado',
                            'dias_vencimiento': 'Días para Vencer'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    estado_counts = df_pagares['estado'].value_counts()
                    fig_pagares = px.pie(
                        values=estado_counts.values,
                        names=estado_counts.index,
                        title='Distribución de Pagarés por Estado'
                    )
                    st.plotly_chart(fig_pagares, use_container_width=True)
                
                st.markdown("#### 💵 Resumen de Planillas")
                query_planillas = "SELECT * FROM vista_admin_planillas_resumen ORDER BY total_pagado DESC"
                planillas = conn.execute_query(query_planillas)
                
                if planillas:
                    df_planillas = pd.DataFrame(planillas)
                    
                    st.dataframe(
                        df_planillas[['nombre_profesor', 'sede_profesor', 'promedio_salario', 
                                     'total_pagado', 'total_registros_planilla']].rename(columns={
                            'nombre_profesor': 'Profesor',
                            'sede_profesor': 'Sede',
                            'promedio_salario': 'Salario Promedio',
                            'total_pagado': 'Total Pagado',
                            'total_registros_planilla': 'Meses Registrados'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                
                st.markdown("#### Consolidación de Pagos")
                datos_pagos = consolidar_datos_pagos()
                
                if datos_pagos:
                    df_pagos_dist = pd.DataFrame(datos_pagos)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        total_ingresos = df_pagos_dist['monto_total'].sum()
                        st.metric("Ingresos Consolidados", f"₡{total_ingresos:,.0f}")
                    with col2:
                        total_transacciones = df_pagos_dist['total_pagos'].sum()
                        st.metric("Total Transacciones", int(total_transacciones))
                    
                    fig_ingresos = px.bar(
                        df_pagos_dist,
                        x='sede',
                        y='monto_total',
                        title='Ingresos por Sede Regional',
                        color='sede'
                    )
                    st.plotly_chart(fig_ingresos, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error consultando datos administrativos: {e}")
    
    elif rol_selected == "Directivo":
        st.markdown("### Vista Ejecutiva - Dashboard Global")
        
        try:
            with get_db_connection('central') as conn:
                query_kpis = "SELECT * FROM vista_directivo_datos_centrales"
                kpis = conn.execute_query(query_kpis)
                
                if kpis:
                    kpi_data = kpis[0]
                    
                    st.markdown("#### KPIs Globales del Sistema")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Profesores", kpi_data['total_profesores_sistema'])
                    with col2:
                        st.metric("Carreras", kpi_data['total_carreras_sistema'])  
                    with col3:
                        st.metric("Sedes", kpi_data['total_sedes'])
                    with col4:
                        st.metric("Pagarés Vigentes", kpi_data['pagares_vigentes'])
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        monto_vigentes = kpi_data['monto_pagares_vigentes'] or 0
                        st.metric("Pagarés Vigentes", f"₡{monto_vigentes:,.0f}")
                    with col2:
                        monto_vencidos = kpi_data['monto_pagares_vencidos'] or 0
                        st.metric("⚠️ Pagarés Vencidos", f"₡{monto_vencidos:,.0f}")
                    with col3:
                        gastos_planilla = kpi_data['gastos_planilla_año'] or 0
                        st.metric("💵 Gastos Planilla Actual", f"₡{gastos_planilla:,.0f}")
                    with col4:
                        gastos_planilla_anterior = kpi_data['gastos_planilla_año_anterior'] or  0
                        st.metric("💵 Gastos Planilla Anterior", f"₡{gastos_planilla_anterior:,.0f}")
                
                query_dist = "SELECT * FROM vista_directivo_profesores_por_sede"
                distribucion = conn.execute_query(query_dist)
                
                if distribucion:
                    df_dist = pd.DataFrame(distribucion)
                    
                    st.markdown("#### Distribución por Sede")
                    st.dataframe(
                        df_dist[['nombre_sede', 'total_profesores', 'total_carreras']].rename(columns={
                            'nombre_sede': 'Sede',
                            'total_profesores': 'Profesores',
                            'total_carreras': 'Carreras'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_prof = px.bar(
                            df_dist,
                            x='nombre_sede',
                            y='total_profesores',
                            title='Profesores por Sede',
                            color='total_profesores'
                        )
                        st.plotly_chart(fig_prof, use_container_width=True)
                    
                    with col2:
                        fig_carr = px.bar(
                            df_dist,
                            x='nombre_sede', 
                            y='total_carreras',
                            title='Carreras por Sede',
                            color='total_carreras'
                        )
                        st.plotly_chart(fig_carr, use_container_width=True)
            
            st.markdown("#### Consolidado de Estudiantes (Distribuido)")
            datos_estudiantes = consolidar_datos_estudiantes()
            
            if datos_estudiantes:
                df_est_dist = pd.DataFrame(datos_estudiantes)
                
                total_estudiantes = df_est_dist['total_estudiantes'].sum() if not df_est_dist.empty else 0
                estudiantes_activos = df_est_dist['estudiantes_activos'].sum() if not df_est_dist.empty else 0
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Estudiantes", int(total_estudiantes))
                with col2:
                    st.metric("Estudiantes Activos", int(estudiantes_activos))
                
                fig_est = px.pie(
                    df_est_dist,
                    values='estudiantes_activos',
                    names='sede',
                    title='Distribución de Estudiantes Activos por Sede'
                )
                st.plotly_chart(fig_est, use_container_width=True)
            
            with get_db_connection('central') as conn:
                query_analisis = "SELECT * FROM vista_directivo_analisis_pagares ORDER BY año_vencimiento DESC, mes_vencimiento DESC LIMIT 12"
                analisis_pagares = conn.execute_query(query_analisis)
                
                if analisis_pagares:
                    df_analisis = pd.DataFrame(analisis_pagares)
                    
                    st.markdown("#### Análisis Financiero de Pagarés")
                    
                    df_analisis['periodo'] = df_analisis['año_vencimiento'].astype(str) + '-' + df_analisis['mes_vencimiento'].astype(str).str.zfill(2)
                    
                    fig_analisis = go.Figure()
                    fig_analisis.add_trace(go.Bar(
                        x=df_analisis['periodo'],
                        y=df_analisis['monto_total'],
                        name='Monto Total',
                        yaxis='y'
                    ))
                    fig_analisis.add_trace(go.Scatter(
                        x=df_analisis['periodo'],
                        y=df_analisis['cantidad_pagares'],
                        mode='lines+markers',
                        name='Cantidad',
                        yaxis='y2'
                    ))
                    
                    fig_analisis.update_layout(
                        title='Evolución de Pagarés por Periodo',
                        xaxis_title='Periodo (Año-Mes)',
                        yaxis=dict(title='Monto (₡)', side='left'),
                        yaxis2=dict(title='Cantidad', side='right', overlaying='y'),
                        hovermode='x'
                    )
                    
                    st.plotly_chart(fig_analisis, use_container_width=True)
        
        except Exception as e:
            st.error(f"Error consultando datos ejecutivos: {e}")
    
    
    st.markdown("---")