import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. Configuración de Conexión
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def login():
    st.sidebar.title("🔐 Acceso Analista Senior")
    # Llaves únicas para evitar el error de ID duplicado visto en tus logs
    user = st.sidebar.text_input("Usuario", key="user_field")
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_field")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False


if login():
    st.title("📊 Dashboard Bursátil IPSA-29")
    
    nemo_list = ["MASISA", "LTM", "CMPC", "VAPORES", "SQM-B", "CHILE", "BCI"]
    selected_nemo = st.selectbox("Seleccione Nemotécnico:", nemo_list)

    # --- SONDA 1: Verificación de Input ---
    st.info(f"🔍 DEBUG 1: Consultando nemotécnico: '{selected_nemo}' (Largo: {len(selected_nemo)})")

    try:
        # Llamada a la función RPC que creamos en el editor SQL
        response = supabase.rpc('buscar_nemo_debug', {'nemo_ingresado': selected_nemo}).execute()
        
        # --- SONDA 2: Respuesta Cruda del Servidor ---
        st.write("📡 DEBUG 2: Respuesta cruda del servidor:")
        st.json(response.data[:2] if response.data else "LISTA VACÍA") # Muestra solo los primeros 2 registros para no saturar

        if response.data:
            df = pd.DataFrame(response.data)
            
            # --- SONDA 3: Estructura del DataFrame ---
            st.write("📋 DEBUG 3: Columnas detectadas en el DataFrame:")
            st.write(list(df.columns))
            
            # Normalización de fecha
            df['fecha'] = pd.to_datetime(df['fecha'])
            
            st.success(f"✅ ÉXITO: Se encontraron {len(df)} registros.")
            
            fig = px.line(df, x='fecha', y='precio_cierre', 
                         title=f"Serie Histórica: {selected_nemo}")
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("🔍 Ver Matriz de Datos"):
                st.dataframe(df.sort_values(by="fecha", ascending=False))
        else:
            st.error(f"⚠️ DEBUG: La base de datos respondió una lista VACÍA para '{selected_nemo}'.")
            st.info("💡 Posible causa: Row Level Security (RLS) activo en Supabase. Verifica si la tabla tiene 'Enable Read Access' para todos los usuarios.")
            
    except Exception as e:
        st.error(f"❌ ERROR TÉCNICO: {e}")
