import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from supabase import create_client, Client

# 1. CONFIGURACIÓN DE CONEXIÓN
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. DEFINICIÓN DE FUNCIONES (Solo una vez cada una)
def login():
    st.sidebar.title("🔐 Acceso Analista Senior")
    # Se agrega una 'key' única para evitar el error de duplicidad
    user = st.sidebar.text_input("Usuario", key="user_input") 
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_input")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

def fetch_realtime_drivers():
    try:
        url = "https://api.boostr.cl/economy/indicators.json"
        response = requests.get(url)
        return response.json().get('data')
    except Exception: return None

# 3. CUERPO ÚNICO DE LA APP
if login():
    st.sidebar.title("🗂️ Terminal IPSA-29")
    
    # Menú de Navegación
    menu = st.sidebar.radio("Módulos:", [
        "📺 La Película (Real-Time)", 
        "📖 El Libro (Histórico)", 
        "🛡️ Perfil de Riesgo",
        "⚙️ El Motor (Admin)"
    ])

    # Captura de Drivers (Dólar y UF vía Boostr)
    drivers = fetch_realtime_drivers()
    if drivers:
        st.sidebar.markdown("---")
        val_dolar = drivers.get('dolar', {}).get('value', 'N/D')
        st.sidebar.metric("Dólar", f"${val_dolar}")
        val_uf = drivers.get('uf', {}).get('value', 'N/D')
        st.sidebar.metric("UF", f"${val_uf}")

    # --- LÓGICA DE MÓDULOS ---
    if menu == "📺 La Película (Real-Time)":
        st.title("📺 Flujo de Mercado en Vivo")
        st.info("Monitoreo dinámico de los 29 constituyentes.")

    elif menu == "📖 El Libro (Histórico)":
        st.title("📖 Memoria Estratégica")
        try:
            # Carga de datos para gráficos
            response = supabase.table("vista_precios_ajustados").select("*").execute()
            df = pd.DataFrame(response.data)
            
            if not df.empty:
                nemos = sorted(df['nemotecnico'].unique())
                selected_nemo = st.selectbox("Seleccione Acción:", nemos)
                df_filtered = df[df['nemotecnico'] == selected_nemo].sort_values(by="fecha")
                
                # Gráfico de Integridad
                fig = px.line(df_filtered, x='fecha', y=['precio_mercado', 'precio_ajustado'],
                              title=f"Serie Continua: {selected_nemo}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No hay datos en la tabla 'vista_precios_ajustados'.")
        except Exception as e:
            st.error(f"Error de base de datos: {e}")

    elif menu == "🛡️ Perfil de Riesgo":
        st.title("🛡️ Evaluación de Solvencia")
        st.write("Módulo para deudas CMF vía Floid.")

    elif menu == "⚙️ El Motor (Admin)":
        st.title("⚙️ Gestión de Datos")
        st.button("Lanzar Backfill Drivers 2026")

else:
    st.info("Sistema blindado bajo el Protocolo de Integridad IPSA-29.")
