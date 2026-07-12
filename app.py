import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from supabase import create_client, Client

# 1. CONFIGURACIÓN ÚNICA
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. DEFINICIÓN DE FUNCIONES (Sin duplicados)
def login():
    st.sidebar.title("🔐 Acceso Analista Senior")
    # Usamos 'key' para que Streamlit identifique estos campos como únicos
    user = st.sidebar.text_input("Usuario", key="login_user_final") 
    password = st.sidebar.text_input("Contraseña", type="password", key="login_pass_final")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

def fetch_realtime_drivers():
    try:
        url = "https://api.boostr.cl/economy/indicators.json"
        response = requests.get(url)
        return response.json().get('data')
    except Exception: return None

# 3. CUERPO DE LA APP (Un solo bloque 'if login')
if login():
    st.sidebar.title("🗂️ Terminal IPSA-29")
    
    # Menú de Navegación Profesional
    menu = st.sidebar.radio("Módulos:", [
        "📺 La Película (Real-Time)", 
        "📖 El Libro (Histórico)", 
        "🛡️ Perfil de Riesgo",
        "⚙️ El Motor (Admin)"
    ])

    # Captura de Drivers (Dólar y UF)
    drivers = fetch_realtime_drivers()
    if drivers:
        st.sidebar.markdown("---")
        val_dolar = drivers.get('dolar', {}).get('value', 'N/D')
        st.sidebar.metric("Dólar", f"${val_dolar}")
        val_uf = drivers.get('uf', {}).get('value', 'N/D')
        st.sidebar.metric("UF", f"${val_uf}")

    # LÓGICA DE MÓDULOS
    if menu == "📺 La Película (Real-Time)":
        st.title("📺 Flujo de Mercado en Vivo")
        st.info("Monitoreo dinámico de los 29 constituyentes.")

    elif menu == "📖 El Libro (Histórico)":
        st.title("📖 Memoria Estratégica")
        try:
            response = supabase.table("vista_precios_ajustados").select("*").execute()
            df = pd.DataFrame(response.data)
            if not df.empty:
                nemos = sorted(df['nemotecnico'].unique())
                sel_nemo = st.selectbox("Acción:", nemos, key="sel_nemo_hist")
                df_f = df[df['nemotecnico'] == sel_nemo].sort_values(by="fecha")
                
                # Gráfico de Integridad (Precio Ajustado por OSAs)
                fig = px.line(df_f, x='fecha', y=['precio_mercado', 'precio_ajustado'],
                              title=f"Serie Continua: {sel_nemo}")
                st.plotly_chart(fig, width='stretch')
            else:
                st.warning("Esperando carga de datos...")
        except Exception as e:
            st.error(f"Error en el Libro: {e}")

    elif menu == "🛡️ Perfil de Riesgo":
        st.title("🛡️ Evaluación de Solvencia")
        st.write("Integración futura con API Floid para deudas CMF.")

    elif menu == "⚙️ El Motor (Admin)":
        st.title("⚙️ Gestión de Datos")
        st.button("Lanzar Backfill 2026", key="btn_backfill")

else:
    st.info("Sistema blindado bajo el Protocolo de Integridad IPSA-29.")
