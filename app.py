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

    # --- CONSULTA VÍA RPC (Instrucción Directa) ---
    try:
        # Llamamos a la función que creamos en el paso anterior
        response = supabase.rpc('buscar_nemo_debug', {'nemo_ingresado': selected_nemo}).execute()
        df = pd.DataFrame(response.data)
        
        if not df.empty:
            # Normalización (Aseguramos que las columnas existan)
            df['fecha'] = pd.to_datetime(df['fecha'])
            
            # --- VERIFICACIÓN DE COLUMNAS (Para evitar el KeyError 'variation') ---
            # Tus logs muestran que buscas 'variation', pero cargaste 'variacion' [1, 2]
            st.write(f"✅ Registros encontrados para {selected_nemo}: {len(df)}")
            
            fig = px.line(df, x='fecha', y='precio_cierre', 
                         title=f"Serie Histórica: {selected_nemo}")
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("🔍 Ver Matriz de Datos"):
                st.dataframe(df.sort_values(by="fecha", ascending=False))
        else:
            st.error(f"La base de datos respondió vacío para '{selected_nemo}'.")
            # Tip del Socio: Verifica si tienes activado RLS (Row Level Security) 
            # sin políticas de acceso, eso bloquea la app pero no el editor.
            
    except Exception as e:
        st.error(f"Error técnico en la consulta: {e}")
