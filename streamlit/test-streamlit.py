"""
Script de diagnóstico para verificar conexiones y dependencias
"""

import streamlit as st
import sys
import os

st.title("🔍 Diagnóstico del Sistema")

# Verificar versión de Streamlit
st.header("1. Información del Sistema")
st.write(f"**Python version:** {sys.version}")
st.write(f"**Streamlit version:** {st.__version__}")
st.write(f"**Working directory:** {os.getcwd()}")

# Verificar importaciones
st.header("2. Verificación de Dependencias")

dependencies = {
    "mysql.connector": False,
    "redis": False,
    "pandas": False,
    "plotly": False,
    "numpy": False
}

for module_name in dependencies:
    try:
        __import__(module_name)
        dependencies[module_name] = True
        st.success(f"✅ {module_name} - OK")
    except ImportError:
        st.error(f"❌ {module_name} - NO INSTALADO")

# Verificar conexiones a bases de datos
st.header("3. Prueba de Conexiones")

# Test MySQL Central
try:
    import mysql.connector
    
    conn = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='admin123',
        database='cenfotec_central'
    )
    if conn.is_connected():
        st.success("✅ MySQL Central - CONECTADO")
        conn.close()
    else:
        st.error("❌ MySQL Central - NO CONECTADO")
except Exception as e:
    st.error(f"❌ MySQL Central - ERROR: {str(e)}")

# Test MySQL San Carlos
try:
    conn = mysql.connector.connect(
        host='localhost',
        port=3307,
        user='root',
        password='admin123',
        database='cenfotec_sancarlos'
    )
    if conn.is_connected():
        st.success("✅ MySQL San Carlos - CONECTADO")
        conn.close()
    else:
        st.error("❌ MySQL San Carlos - NO CONECTADO")
except Exception as e:
    st.error(f"❌ MySQL San Carlos - ERROR: {str(e)}")

# Test MySQL Heredia
try:
    conn = mysql.connector.connect(
        host='localhost',
        port=3308,
        user='root',
        password='admin123',
        database='cenfotec_heredia'
    )
    if conn.is_connected():
        st.success("✅ MySQL Heredia - CONECTADO")
        conn.close()
    else:
        st.error("❌ MySQL Heredia - NO CONECTADO")
except Exception as e:
    st.error(f"❌ MySQL Heredia - ERROR: {str(e)}")

# Test Redis
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    r.ping()
    st.success("✅ Redis Cache - CONECTADO")
except Exception as e:
    st.error(f"❌ Redis Cache - ERROR: {str(e)}")

st.header("4. Acciones Recomendadas")

if not all(dependencies.values()):
    st.warning("⚠️ Faltan dependencias. Ejecuta:")
    st.code("pip install -r requirements.txt")

st.info("💡 Si todo está verde pero la app principal no funciona, intenta:")
st.code("""
# Opción 1: Reinstalar Streamlit
pip uninstall streamlit -y
pip install streamlit==1.37.0

# Opción 2: Limpiar caché
streamlit cache clear

# Opción 3: Ejecutar con más detalle
streamlit run app.py --logger.level=debug
""")