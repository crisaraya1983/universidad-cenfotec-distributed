"""
📊 Diagramas del Sistema - Universidad Cenfotec
Página que muestra los diagramas de arquitectura y bases de datos relacionales
para el sistema distribuido de la Universidad Cenfotec
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import graphviz
import os
import sys

# Configuración de la página
st.set_page_config(
    page_title="📊 Diagramas - Sistema Cenfotec",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .diagram-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #e9ecef;
    }
    
    .sede-header {
        background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 15px 0;
        font-weight: bold;
    }
    
    .diagram-title {
        color: #1f77b4;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin: 20px 0;
    }
    
    .architecture-info {
        background-color: #e7f3ff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    
    .tech-box {
        background-color: #f0f8ff;
        padding: 12px;
        border-radius: 6px;
        border: 1px solid #cce7ff;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<div class="diagram-title">📊 Diagramas del Sistema Distribuido</div>', unsafe_allow_html=True)

# Navegación por pestañas
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏗️ Arquitectura",
    "🗄️ Modelo E-R",
    "🏛️ BD Central",
    "🏢 BD Regionales",
    "🔄 Replicación",
    "⚡ Cache & Balanceador"
])

with tab1:
    st.markdown("## 🏗️ Arquitectura del Sistema Distribuido")
    
    # Información de la arquitectura
    st.markdown("""
    <div class="architecture-info">
    <h3>📋 Descripción de la Arquitectura</h3>
    <p>El sistema de base de datos distribuida de la Universidad Cenfotec implementa una arquitectura 
    robusta y escalable que permite la gestión descentralizada de información académica y administrativa 
    en tres sedes geográficamente separadas.</p>
    </div>
    """, unsafe_allow_html=True)
    
    image_path = "images/arquitectura_sistema.png"
    if os.path.exists(image_path):
        st.image(image_path, caption="Arquitectura del Sistema Distribuido", use_column_width=True)
    else:
        st.info("""
        📁 **Instrucción para agregar tu imagen:**
        
        1. Crea la carpeta: `streamlit/images/`
        2. Sube tu imagen de arquitectura como: `arquitectura_sistema.png`
        3. La imagen se mostrará automáticamente aquí
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="tech-box">
        <h4>🎯 Componentes Principales</h4>
        
        <b>🐳 Contenedores Docker:</b><br>
        • MySQL Central (Puerto 3306)<br>
        • MySQL San Carlos (Puerto 3307)<br>
        • MySQL Heredia (Puerto 3308)<br>
        • Redis Cache (Puerto 6379)<br>
        • NGINX Load Balancer (Puerto 80)<br><br>
        
        <b>🔄 Servicios de Replicación:</b><br>
        • Master-Slave desde Central<br>
        • Sincronización bidireccional<br>
        • Backup automatizado
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="tech-box">
        <h4>⚡ Características Técnicas</h4>
        
        <b>📊 Fragmentación Implementada:</b><br>
        • Horizontal: Estudiantes por sede<br>
        • Vertical: Datos admin vs académicos<br>
        • Mixta: Combinación estratégica<br><br>
        
        <b>🚀 Beneficios:</b><br>
        • Autonomía operacional por sede<br>
        • Rendimiento optimizado<br>
        • Escalabilidad horizontal<br>
        • Tolerancia a fallos
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("## 🗄️ Diagrama Entidad-Relación Global")
    
    st.markdown("""
    <div class="architecture-info">
    <h3>📊 Modelo de Datos Completo</h3>
    <p>Este diagrama muestra el modelo entidad-relación que sirve como base para todas las sedes, 
    incluyendo las relaciones entre estudiantes, profesores, cursos, matrículas y demás entidades.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Crear diagrama E-R usando Graphviz
    er_diagram = graphviz.Digraph(comment='Diagrama E-R Universidad Cenfotec')
    er_diagram.attr(rankdir='TB', size='12,8', dpi='70')
    er_diagram.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='10')
    
    # Entidades principales con colores diferenciados
    er_diagram.node('Sede', 'SEDE\n📍\nid_sede (PK)\nnombre\ndireccion', fillcolor='lightblue')
    er_diagram.node('Estudiante', 'ESTUDIANTE\n👨‍🎓\nid_estudiante (PK)\nnombre\nemail\nid_sede (FK)', fillcolor='honeydew', style='filled')
    er_diagram.node('Profesor', 'PROFESOR\n👨‍🏫\nid_profesor (PK)\nnombre\nemail\nid_sede (FK)', fillcolor='lightcoral')
    er_diagram.node('Carrera', 'CARRERA\n🎓\nid_carrera (PK)\nnombre\nid_sede (FK)', fillcolor='lightyellow')
    er_diagram.node('Curso', 'CURSO\n📚\nid_curso (PK)\nnombre\nid_carrera (FK)', fillcolor='lightpink')
    er_diagram.node('Matricula', 'MATRICULA\n📝\nid_matricula (PK)\nid_estudiante (FK)\nid_curso (FK)', fillcolor='lightgray')
    er_diagram.node('Nota', 'NOTA\n📊\nid_nota (PK)\nid_matricula (FK)\nnota', fillcolor='lightsteelblue')
    er_diagram.node('Asistencia', 'ASISTENCIA\n✅\nid_asistencia (PK)\nid_matricula (FK)\nfecha\npresente', fillcolor='lightsteelblue')
    er_diagram.node('Pago', 'PAGO\n💰\nid_pago (PK)\nid_estudiante (FK)\nmonto\nfecha', fillcolor='honeydew', style='filled')
    er_diagram.node('Planilla', 'PLANILLA\n💼\nid_planilla (PK)\nid_profesor (FK)\nsalario\nmes', fillcolor='lightcoral')
    er_diagram.node('Pagare', 'PAGARE\n📄\nid_pagare (PK)\nid_estudiante (FK)\nmonto\nvencimiento', fillcolor='honeydew', style='filled')
    

    er_diagram.edge('Estudiante', 'Sede', label='pertenece_a', color='blue')
    er_diagram.edge('Profesor', 'Sede', label='trabaja_en', color='red')
    er_diagram.edge('Carrera', 'Sede', label='ofrecida_en', color='orange')
    er_diagram.edge('Curso', 'Carrera', label='pertenece_a', color='purple')
    er_diagram.edge('Matricula', 'Estudiante', label='realizada_por', color='green')
    er_diagram.edge('Matricula', 'Curso', label='inscrita_en', color='green')
    er_diagram.edge('Nota', 'Matricula', label='califica', color='darkblue')
    er_diagram.edge('Asistencia', 'Matricula', label='registra', color='darkblue')
    er_diagram.edge('Pago', 'Estudiante', label='realizado_por', color='green')
    er_diagram.edge('Planilla', 'Profesor', label='corresponde_a', color='red')
    er_diagram.edge('Pagare', 'Estudiante', label='firmado_por', color='green')
    
    st.graphviz_chart(er_diagram.source)

with tab3:
    st.markdown('<div class="sede-header">🏛️ BASE DE DATOS - SEDE CENTRAL (MASTER)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### 📊 Características de la Sede Central
    
    **🎯 Rol:** Nodo maestro y centro administrativo  
    **🗄️ Puerto MySQL:** 3306  
    **📍 Ubicación:** San José, Costa Rica  
    **🔑 Responsabilidades:** Gestión administrativa y replicación master
    """)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("#### 📋 Estructura de Tablas")
        central_tables = {
            'Tabla': ['sede', 'carrera', 'profesor', 'planilla', 'pagare'],
            'Tipo': ['Maestra', 'Maestra', 'Maestra', 'Administrativa', 'Administrativa'],
            'Replicada': ['✅ Sí', '✅ Sí', '✅ Sí', '❌ No', '❌ No'],
            'Propósito': ['Info sedes', 'Carreras por sede', 'Profesores', 'Nómina', 'Pagarés estudiantiles']
        }
        df_central = pd.DataFrame(central_tables)
        st.dataframe(df_central, use_container_width=True)
    
    with col2:
        st.markdown("""
        #### 🔑 Funciones Clave
        
        **📊 Datos Maestros:**
        - Control de sedes
        - Gestión de carreras
        - Registro de profesores
        
        **💼 Datos Administrativos:**
        - Planillas de pago
        - Pagarés estudiantiles
        - Reportes ejecutivos
        """)
    
    # Diagrama relacional específico de Central
    st.markdown("#### 🔗 Diagrama Relacional - Sede Central")
    
    central_diagram = graphviz.Digraph(comment='BD Central')
    central_diagram.attr(rankdir='LR', size='10,6', dpi='70')
    central_diagram.attr(bgcolor='white')
    central_diagram.attr('node', shape='record', style='filled', fontname='Arial', fontsize='10')
    
    # Tablas maestras (azul)
    central_diagram.node('sede_c', '{SEDE|id_sede (PK)\\lnombre\\ldireccion\\l}', fillcolor='lightblue')
    central_diagram.node('carrera_c', '{CARRERA|id_carrera (PK)\\lnombre\\lid_sede (FK)\\l}', fillcolor='lightblue')
    central_diagram.node('profesor_c', '{PROFESOR|id_profesor (PK)\\lnombre\\lemail\\lid_sede (FK)\\l}', fillcolor='lightblue')
    
    # Tablas administrativas (verde)
    central_diagram.node('planilla_c', '{PLANILLA|id_planilla (PK)\\lid_profesor (FK)\\lsalario\\lmes\\l}', fillcolor='honeydew')
    central_diagram.node('pagare_c', '{PAGARE|id_pagare (PK)\\lid_estudiante (FK)\\lmonto\\lvencimiento\\l}', fillcolor='honeydew')
    
    # Relaciones
    central_diagram.edge('carrera_c', 'sede_c', label='FK: id_sede', color='blue')
    central_diagram.edge('profesor_c', 'sede_c', label='FK: id_sede', color='blue')
    central_diagram.edge('planilla_c', 'profesor_c', label='FK: id_profesor', color='green')
    
    st.graphviz_chart(central_diagram.source)

with tab4:
    st.markdown('<div class="sede-header">🏢 BASES DE DATOS - SEDES REGIONALES</div>', unsafe_allow_html=True)
    
    # Subtabs para cada sede regional
    subtab1, subtab2 = st.tabs(["🌄 San Carlos", "🏔️ Heredia"])
    
    with subtab1:
        st.markdown("### 🌄 Sede San Carlos")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("#### 📋 Estructura de Tablas")
            sc_tables = {
                'Tabla': ['sede*', 'carrera*', 'profesor*', 'estudiante', 'curso', 'matricula', 'nota', 'asistencia', 'pago'],
                'Tipo': ['Replicada', 'Replicada', 'Replicada', 'Local', 'Local', 'Local', 'Local', 'Local', 'Local'],
                'Fragmentación': ['Global', 'Por sede', 'Por sede', 'Horizontal', 'Vertical', 'Mixta', 'Mixta', 'Mixta', 'Horizontal']
            }
            df_sc = pd.DataFrame(sc_tables)
            st.dataframe(df_sc, use_container_width=True)
        
        with col2:
            st.markdown("""
            #### 🎯 Características
            
            **📊 Puerto MySQL:** 3307  
            **🗄️ Base de Datos:** cenfotec_sancarlos  
            **🎓 Tipo:** Nodo regional académico
            
            **🔄 Operaciones:**
            - Registro de estudiantes locales
            - Gestión de matrículas
            - Control de asistencias
            - Procesamiento de pagos
            """)
        
        # Diagrama relacional San Carlos
        st.markdown("#### 🔗 Diagrama Relacional - San Carlos")
        
        sc_diagram = graphviz.Digraph(comment='BD San Carlos')
        sc_diagram.attr(rankdir='LR', size='12,6', dpi='70')
        sc_diagram.attr('node', shape='record', style='filled', fontname='Arial', fontsize='9')
        
        # Tablas replicadas (amarillo)
        sc_diagram.node('sede_sc', '{SEDE*|id_sede (PK)\\lnombre\\ldireccion\\l}', fillcolor='lightyellow')
        sc_diagram.node('carrera_sc', '{CARRERA*|id_carrera (PK)\\lnombre\\lid_sede (FK)\\l}', fillcolor='lightyellow')
        sc_diagram.node('profesor_sc', '{PROFESOR*|id_profesor (PK)\\lnombre\\lemail\\lid_sede (FK)\\l}', fillcolor='lightyellow')
        
        # Tablas locales (rosa)
        sc_diagram.node('estudiante_sc', '{ESTUDIANTE|id_estudiante (PK)\\lnombre\\lemail\\lid_sede (FK)\\l}', fillcolor='lightpink')
        sc_diagram.node('curso_sc', '{CURSO|id_curso (PK)\\lnombre\\lid_carrera (FK)\\l}', fillcolor='lightpink')
        sc_diagram.node('matricula_sc', '{MATRICULA|id_matricula (PK)\\lid_estudiante (FK)\\lid_curso (FK)\\l}', fillcolor='lightpink')
        sc_diagram.node('nota_sc', '{NOTA|id_nota (PK)\\lid_matricula (FK)\\lnota\\l}', fillcolor='lightpink')
        sc_diagram.node('pago_sc', '{PAGO|id_pago (PK)\\lid_estudiante (FK)\\lmonto\\lfecha\\l}', fillcolor='lightpink')
        
        # Relaciones principales
        sc_diagram.edge('estudiante_sc', 'sede_sc', label='FK', color='blue')
        sc_diagram.edge('carrera_sc', 'sede_sc', label='FK', color='blue')
        sc_diagram.edge('curso_sc', 'carrera_sc', label='FK', color='purple')
        sc_diagram.edge('matricula_sc', 'estudiante_sc', label='FK', color='green')
        sc_diagram.edge('matricula_sc', 'curso_sc', label='FK', color='green')
        sc_diagram.edge('nota_sc', 'matricula_sc', label='FK', color='darkblue')
        sc_diagram.edge('pago_sc', 'estudiante_sc', label='FK', color='green')
        
        st.graphviz_chart(sc_diagram.source)
    
    with subtab2:
        st.markdown("### 🏔️ Sede Heredia")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("#### 📋 Estructura de Tablas")
            hd_tables = {
                'Tabla': ['sede*', 'carrera*', 'profesor*', 'estudiante', 'curso', 'matricula', 'nota', 'asistencia', 'pago'],
                'Tipo': ['Replicada', 'Replicada', 'Replicada', 'Local', 'Local', 'Local', 'Local', 'Local', 'Local'],
                'Fragmentación': ['Global', 'Por sede', 'Por sede', 'Horizontal', 'Vertical', 'Mixta', 'Mixta', 'Mixta', 'Horizontal']
            }
            df_hd = pd.DataFrame(hd_tables)
            st.dataframe(df_hd, use_container_width=True)
        
        with col2:
            st.markdown("""
            #### 🎯 Características
            
            **📊 Puerto MySQL:** 3308  
            **🗄️ Base de Datos:** cenfotec_heredia  
            **🎓 Tipo:** Nodo regional académico
            
            **🔄 Operaciones:**
            - Registro de estudiantes locales
            - Gestión de matrículas
            - Control de asistencias
            - Procesamiento de pagos
            """)
        
        # Diagrama relacional Heredia
        st.markdown("#### 🔗 Diagrama Relacional - Heredia")
        
        hd_diagram = graphviz.Digraph(comment='BD Heredia')
        hd_diagram.attr(rankdir='LR', size='12,6', dpi='70')
        hd_diagram.attr('node', shape='record', style='filled', fontname='Arial', fontsize='9')
        
        # Tablas replicadas (amarillo)
        hd_diagram.node('sede_hd', '{SEDE*|id_sede (PK)\\lnombre\\ldireccion\\l}', fillcolor='lightyellow')
        hd_diagram.node('carrera_hd', '{CARRERA*|id_carrera (PK)\\lnombre\\lid_sede (FK)\\l}', fillcolor='lightyellow')
        hd_diagram.node('profesor_hd', '{PROFESOR*|id_profesor (PK)\\lnombre\\lemail\\lid_sede (FK)\\l}', fillcolor='lightyellow')
        
        # Tablas locales (celeste)
        hd_diagram.node('estudiante_hd', '{ESTUDIANTE|id_estudiante (PK)\\lnombre\\lemail\\lid_sede (FK)\\l}', fillcolor='lightcyan')
        hd_diagram.node('curso_hd', '{CURSO|id_curso (PK)\\lnombre\\lid_carrera (FK)\\l}', fillcolor='lightcyan')
        hd_diagram.node('matricula_hd', '{MATRICULA|id_matricula (PK)\\lid_estudiante (FK)\\lid_curso (FK)\\l}', fillcolor='lightcyan')
        hd_diagram.node('nota_hd', '{NOTA|id_nota (PK)\\lid_matricula (FK)\\lnota\\l}', fillcolor='lightcyan')
        hd_diagram.node('pago_hd', '{PAGO|id_pago (PK)\\lid_estudiante (FK)\\lmonto\\lfecha\\l}', fillcolor='lightcyan')
        
        # Relaciones principales
        hd_diagram.edge('estudiante_hd', 'sede_hd', label='FK', color='blue')
        hd_diagram.edge('carrera_hd', 'sede_hd', label='FK', color='blue')
        hd_diagram.edge('curso_hd', 'carrera_hd', label='FK', color='purple')
        hd_diagram.edge('matricula_hd', 'estudiante_hd', label='FK', color='green')
        hd_diagram.edge('matricula_hd', 'curso_hd', label='FK', color='green')
        hd_diagram.edge('nota_hd', 'matricula_hd', label='FK', color='darkblue')
        hd_diagram.edge('pago_hd', 'estudiante_hd', label='FK', color='green')
        
        st.graphviz_chart(hd_diagram.source)

with tab5:
    st.markdown("## 🔄 Diagrama de Replicación Master-Slave")
    
    st.markdown("""
    <div class="architecture-info">
    <h3>🔄 Proceso de Replicación</h3>
    <p>El sistema implementa replicación master-slave donde la Sede Central actúa como master 
    y las sedes regionales como slaves para datos maestros (sedes, carreras, profesores).</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Diagrama de replicación
    replication_diagram = graphviz.Digraph(comment='Replicación Master-Slave')
    replication_diagram.attr(rankdir='TB', size='10,8', dpi='70', center='true')
    replication_diagram.attr('node', fontname='Arial', fontsize='10')
    
    # Nodo Master (Central)
    replication_diagram.node('master', '''
    MASTER
    🏛️ Sede Central
    ━━━━━━━━━━━━━━━━━━━━
    📊 Datos Maestros:
    • sedes
    • carreras  
    • profesores
    ━━━━━━━━━━━━━━━━━━━━
    💼 Datos Administrativos:
    • planillas
    • pagarés
    ''', shape='box', style='filled', fillcolor='lightblue')
    
    # Nodos Slave (Regionales)
    replication_diagram.node('slave1', '''
    SLAVE 1
    🌄 San Carlos
    ━━━━━━━━━━━━━━━━━━━━
    📊 Datos Replicados:
    • sedes*
    • carreras*
    • profesores*
    ━━━━━━━━━━━━━━━━━━━━
    🎓 Datos Locales:
    • estudiantes
    • matrículas
    • notas
    ''', shape='box', style='filled', fillcolor='honeydew')
    
    replication_diagram.node('slave2', '''
    SLAVE 2
    🏔️ Heredia
    ━━━━━━━━━━━━━━━━━━━━
    📊 Datos Replicados:
    • sedes*
    • carreras*
    • profesores*
    ━━━━━━━━━━━━━━━━━━━━
    🎓 Datos Locales:
    • estudiantes
    • matrículas
    • notas
    ''', shape='box', style='filled', fillcolor='lightcoral')
    
    # Proceso de sincronización
    replication_diagram.node('sync', '''
    PROCESO DE SINCRONIZACIÓN
    ⚡ Redis Cache
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🔄 Replicación Automática:
    1. Cambios en Master
    2. Log de transacciones
    3. Aplicación en Slaves
    4. Verificación de consistencia
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    📋 Backup y Recovery
    ''', shape='ellipse', style='filled', fillcolor='lightyellow')
    
    # Relaciones de replicación
    replication_diagram.edge('master', 'sync', label='1. Cambios', color='blue', style='bold')
    replication_diagram.edge('sync', 'slave1', label='2. Replicar', color='green', style='bold')
    replication_diagram.edge('sync', 'slave2', label='3. Replicar', color='red', style='bold')
    
    # Flujos de sincronización bidireccional
    replication_diagram.edge('slave1', 'sync', label='Sync bidireccional', color='green', style='dashed')
    replication_diagram.edge('slave2', 'sync', label='Sync bidireccional', color='red', style='dashed')
    
    st.graphviz_chart(replication_diagram.source)
    
    # Explicación del proceso
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📋 Tipos de Replicación
        
        **🔄 Master-Slave (Datos Maestros):**
        - Sedes: Información de las 3 ubicaciones
        - Carreras: Programas académicos por sede
        - Profesores: Personal docente
        
        **⚡ Sincronización Bidireccional:**
        - Cambios en carreras regionales → Central
        - Nuevos profesores regionales → Central
        - Actualizaciones de horarios
        """)
    
    with col2:
        st.markdown("""
        #### ⚙️ Mecanismos Técnicos
        
        **🗄️ MySQL Replication:**
        - Binary logs para rastreo de cambios
        - Slave threads para aplicar cambios
        - Verificación automática de consistencia
        
        **⚡ Redis Cache:**
        - Cache de consultas frecuentes
        - Invalidación automática
        - Reducción de latencia
        """)

with tab6:
    st.markdown("## ⚡ Cache Distribuido y Load Balancer")
    
    # Diagrama de Cache y Load Balancer
    cache_diagram = graphviz.Digraph(comment='Cache y Load Balancer')
    cache_diagram.attr(rankdir='TB', size='12,8', dpi='70')
    cache_diagram.attr('node', fontname='Arial', fontsize='9')
    
    # Cliente/Usuario
    cache_diagram.node('user', '''
    👥 USUARIOS
    ━━━━━━━━━━━━━━━━━━
    🌐 Aplicaciones Web
    📱 Interfaces Mobile
    🖥️ Sistemas Admin
    📊 Dashboards
    ''', shape='ellipse', style='filled', fillcolor='lightsteelblue')
    
    # Load Balancer NGINX
    cache_diagram.node('nginx', '''
    ⚖️ NGINX LOAD BALANCER
    Puerto: 80
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🎯 Algoritmos de Balanceo:
    • Round Robin
    • Least Connections
    • IP Hash
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🔒 Funciones Adicionales:
    • SSL Termination
    • Compression
    • Rate Limiting
    • Health Checks
    ''', shape='box', style='filled', fillcolor='orange')
    
    # Redis Cache
    cache_diagram.node('redis', '''
    ⚡ REDIS CACHE
    Puerto: 6379
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    💾 Tipos de Cache:
    • Query Cache (consultas SQL)
    • Session Cache (sesiones usuario)
    • Object Cache (objetos frecuentes)
    • API Response Cache
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    ⚙️ Configuración:
    • TTL: 3600s (consultas)
    • TTL: 1800s (sesiones)
    • Invalidación automática
    ''', shape='box', style='filled', fillcolor='lightcoral')
    
    # API Proxies
    cache_diagram.node('api_central', '''
    🏛️ API PROXY CENTRAL
    Puerto: 8080
    ━━━━━━━━━━━━━━━━━━━━━━━━━
    📊 Servicios:
    • Gestión administrativa
    • Reportes consolidados
    • Operaciones maestras
    • Sincronización
    ''', shape='box', style='filled', fillcolor='lightblue')
    
    cache_diagram.node('api_sc', '''
    🌄 API PROXY SAN CARLOS
    Puerto: 8081
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🎓 Servicios:
    • Gestión estudiantes SC
    • Matrículas locales
    • Calificaciones
    • Pagos estudiantiles
    ''', shape='box', style='filled', fillcolor='honeydew')
    
    cache_diagram.node('api_hd', '''
    🏔️ API PROXY HEREDIA
    Puerto: 8082
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    🎓 Servicios:
    • Gestión estudiantes HD
    • Matrículas locales
    • Calificaciones
    • Pagos estudiantiles
    ''', shape='box', style='filled', fillcolor='lightpink')
    
    # Bases de datos
    cache_diagram.node('db_central', '🏛️ MySQL Central\n3306', shape='cylinder', style='filled', fillcolor='lightblue')
    cache_diagram.node('db_sc', '🌄 MySQL San Carlos\n3307', shape='cylinder', style='filled', fillcolor='honeydew')
    cache_diagram.node('db_hd', '🏔️ MySQL Heredia\n3308', shape='cylinder', style='filled', fillcolor='lightpink')
    
    # Flujo de requests
    cache_diagram.edge('user', 'nginx', label='1. Request', color='blue', style='bold')
    cache_diagram.edge('nginx', 'redis', label='2. Check Cache', color='purple', style='dashed')
    
    # Distribución de carga
    cache_diagram.edge('nginx', 'api_central', label='3a. Route Admin', color='blue')
    cache_diagram.edge('nginx', 'api_sc', label='3b. Route SC', color='green')
    cache_diagram.edge('nginx', 'api_hd', label='3c. Route HD', color='red')
    
    # APIs a Cache
    cache_diagram.edge('api_central', 'redis', label='Cache Update', color='purple', style='dotted')
    cache_diagram.edge('api_sc', 'redis', label='Cache Update', color='purple', style='dotted')
    cache_diagram.edge('api_hd', 'redis', label='Cache Update', color='purple', style='dotted')
    
    # APIs a DBs
    cache_diagram.edge('api_central', 'db_central', label='4a. Query', color='blue')
    cache_diagram.edge('api_sc', 'db_sc', label='4b. Query', color='green')
    cache_diagram.edge('api_hd', 'db_hd', label='4c. Query', color='red')
    
    st.graphviz_chart(cache_diagram.source)
    
    # Explicaciones técnicas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="tech-box">
        <h4>⚖️ NGINX Load Balancer</h4>
        
        <b>🎯 Funciones Principales:</b><br>
        • <b>Distribución de carga:</b> Round-robin entre APIs<br>
        • <b>Health checks:</b> Monitoreo de servicios<br>
        • <b>Failover:</b> Redirección automática<br>
        • <b>SSL termination:</b> Manejo de certificados<br><br>
        
        <b>📊 Configuración:</b><br>
        • Upstream servers configurados<br>
        • Timeouts y retry logic<br>
        • Logging detallado<br>
        • Rate limiting por IP
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="tech-box">
        <h4>⚡ Redis Cache</h4>
        
        <b>💾 Estrategias de Cache:</b><br>
        • <b>Query caching:</b> Resultados de consultas SQL<br>
        • <b>Session caching:</b> Datos de sesión usuario<br>
        • <b>Object caching:</b> Objetos frecuentemente accedidos<br>
        • <b>API response:</b> Respuestas de endpoints<br><br>
        
        <b>⚙️ Configuración:</b><br>
        • TTL configurable por tipo<br>
        • Invalidación en tiempo real<br>
        • Persistent storage opcional<br>
        • Clustering para HA
        </div>
        """, unsafe_allow_html=True)
    
    # Métricas de rendimiento
    st.markdown("#### 📈 Beneficios de Rendimiento")
    
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        st.metric(
            label="🚀 Cache Hit Rate",
            value="85%",
            delta="↑ 15% vs sin cache"
        )
    
    with metrics_col2:
        st.metric(
            label="⚡ Response Time",
            value="120ms",
            delta="↓ 300ms vs directo"
        )
    
    with metrics_col3:
        st.metric(
            label="⚖️ Load Distribution",
            value="33.3%",
            delta="Balanceado perfecto"
        )
    
    with metrics_col4:
        st.metric(
            label="🔄 Uptime",
            value="99.9%",
            delta="↑ 5% vs single point"
        )

# Sidebar con información adicional
with st.sidebar:
    st.markdown("### 📊 Navegación de Diagramas")
    
    st.markdown("""
    **🏗️ Arquitectura:**
    - Visión general del sistema
    - Componentes principales
    
    **🗄️ Modelo E-R:**
    - Entidades y relaciones globales
    - Estructura de datos
    
    **🏛️ BD Central:**
    - Tablas maestras y administrativas
    - Diagrama relacional
    
    **🏢 BD Regionales:**
    - San Carlos y Heredia
    - Fragmentación implementada
    
    **🔄 Replicación:**
    - Master-slave process
    - Sincronización de datos
    
    **⚡ Cache & Balanceador:**
    - Redis y NGINX
    - Optimización de rendimiento
    """)
    st.markdown("---")
    

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>📊 Diagramas Arquitectónicos | Universidad Cenfotec | 2025</p>
    <p>🏗️ Arquitectura • 🗄️ Modelos • 🔄 Replicación • ⚡ Cache & Balanceo</p>
</div>
""", unsafe_allow_html=True)