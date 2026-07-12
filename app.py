import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from supabase import create_client, Client

# 1. CONEXIÓN Y SEGURIDAD
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def login_blindado():
    st.sidebar.title("🔐 Acceso Terminal")
    # Llaves únicas para evitar duplicidad
    u = st.sidebar.text_input("Usuario", key="user_final_v1") 
    p = st.sidebar.text_input("Contraseña", type="password", key="pass_final_v1")
    if u == st.secrets["APP_USER"] and p == st.secrets["APP_PASSWORD"]:
        return True
    return False

def fetch_drivers():
    try:
        r = requests.get("https://api.boostr.cl/economy/indicators.json")
        return r.json().get('data')
    except: return None

# 2. EJECUCIÓN MODULAR
if login_blindado():
    st.sidebar.title("🗂️ Módulos IPSA-29")
    menu = st.sidebar.radio("Seleccione Vista:", 
                            ["📺 La Película (Vivo)", "📖 El Libro (Histórico)", "⚙️ Admin"],
                            key="menu_radio_v1")

    # Drivers Transversales
    data = fetch_drivers()
    if data:
        st.sidebar.markdown("---")
        st.sidebar.metric("Dólar", f"${data.get('dolar', {}).get('value')}")
        st.sidebar.metric("UF", f"${data.get('uf', {}).get('value')}")

    # --- MÓDULO 1: LA PELÍCULA ---
    if menu == "📺 La Película (Vivo)":
        st.title("📺 Flujo de Mercado Real-Time")
        st.info("Aquí monitorearemos el cierre diario y los drivers de exportación.")
        st.write("Estado: Conectado a la API de Boostr.")

    # --- MÓDULO 2: EL LIBRO ---
    elif menu == "📖 El Libro (Histórico)":
        st.title("📖 Memoria Estratégica: Ajustes y Correlación")
        try:
            res = supabase.table("vista_precios_ajustados").select("*").execute()
            df = pd.DataFrame(res.data)
            if not df.empty:
                nemos = sorted(df['nemotecnico'].unique())
                sel = st.selectbox("Analizar Activo:", nemos, key="sel_hist_v1")
                df_f = df[df['nemotecnico'] == sel].sort_values(by="fecha")
                
                # Gráfico de Integridad (Masisa OSA)
                st.subheader("🛠️ Ajuste de Serie Continua")
                fig = px.line(df_f, x='fecha', y=['precio_mercado', 'precio_ajustado'],
                              title=f"Evolución de {sel}")
                st.plotly_chart(fig, use_container_width=True)
                
                # Gráfico de Correlación (IPER)
                st.markdown("---")
                st.subheader("🔗 Radar de Drivers (Commodities)")
                driver = st.selectbox("Driver:", ["Cobre", "Hierro", "Litio"], key="drv_v1")
                st.line_chart(df_f.set_index('fecha')['precio_ajustado']) 
            else:
                st.warning("Base de datos sin registros históricos.")
        except Exception as e:
            st.error(f"Error de conexión al 'Libro': {e}")

else:
    st.info("Sistema blindado. Ingrese sus credenciales de Analista Senior.")
