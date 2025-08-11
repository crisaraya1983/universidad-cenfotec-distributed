import streamlit as st
from .db_connections import get_redis_connection

def show_redis_widget():
    st.markdown("### Cache Redis")
    
    redis_conn = get_redis_connection()
    if redis_conn and redis_conn.is_connected:
        try:
            info = redis_conn.get_info()
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Hit Rate", f"{hit_rate:.1f}%")
            with col2:
                st.metric("Keys", info.get('db0', {}).get('keys', 0))
            
            st.progress(hit_rate / 100)
            
        except:
            st.metric("Estado", "Conectado")
            st.caption("Estadísticas no disponibles")
    else:
        st.error("❌ Desconectado")