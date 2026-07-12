import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from supabase import create_client, Client

# 1. CONEXIÓN Y SEGURIDAD (Protocolo IPSA-29)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def login_blindado():
    st.sidebar.title("🔐 Acceso Analista Senior")
    # Keys únicas para evitar el error de duplicidad
    u = st.sidebar.text_input("Usuario", key="usr_session_final") 
    p = st.sidebar.text_input("Contraseña", type="password", key="pass_session_final")
    if u == st.secrets["APP_USER"] and p == st.secrets["APP_PASSWORD"]:
        return True
    return False

def fetch_drivers():
    """Captura de drivers monetarios (API Boostr)"""
    try:
        r = requests.get("https://api.boostr.cl/economy/indicators.json")
        return r.json().get('data')
    except: return None

# 2. CUERPO PRINCIPAL MODULAR
if login_blindado():
    st.sidebar.title("🗂️ Módulos de Inteligencia")
    menu = st.sidebar.radio("Navegación:", 
                            ["📺 La Película (Real-Time)", "📖 El Libro (Histórico)", "🛡️ Riesgo", "⚙️ Admin"],
                            key="menu_principal_v2")

    # Indicadores en Tiempo Real (Sidebar)
    data = fetch_drivers()
    if data:
        st.sidebar.markdown("---")
        st.sidebar.metric("Dólar", f"${data.get('dolar', {}).get('value')}")
        st.sidebar.metric("UF", f"${data.get('uf', {}).get('value')}")

    # --- MÓDULO: LA PELÍCULA ---
    if menu == "📺 La Película (Real-Time)":
        st.title("📺 Flujo de Mercado en Vivo")
        st.info("Monitoreo dinámico de los 29 constituyentes y drivers de exportación.")
        st.write("Estado: Conectado a la API de Boostr.")

    # --- MÓDULO: EL LIBRO ---
    elif menu == "📖 El Libro (Histórico)":
        st.title("📖 Memoria Estratégica: Ajustes por OSAs")
        try:
            res = supabase.table("vista_precios_ajustados").select("*").execute()
            df = pd.DataFrame(res.data)
            if not df.empty:
                nemos = sorted(df['nemotecnico'].unique())
                sel = st.selectbox("Seleccione Acción:", nemos, key="sel_stock_v2")
                df_f = df[df['nemotecnico'] == sel].sort_values(by="fecha")
                
                # Gráfico 1: Integridad (Precio Ajustado)
                st.subheader("🛠️ Auditoría de Serie Continua")
                fig = px.line(df_f, x='fecha', y=['precio_mercado', 'precio_ajustado'],
                              title=f"Evolución Ajustada: {sel}")
                st.plotly_chart(fig, use_container_width=True)
                
                # Gráfico 2: Correlación Dual
                st.markdown("---")
                st.subheader("🔗 Correlación: Acción vs Commodity (IPER)")
                # Aquí configuraremos el doble eje Y en la próxima sesión
                st.line_chart(df_f.set_index('fecha')['precio_ajustado'])
            else:
                st.warning("Base de datos sin registros. Pendiente PVI del 01 de julio.")
        except Exception as e:
            st.error(f"Error al conectar con el 'Libro': {e}")

    # --- MÓDULO: ADMIN ---
    elif menu == "⚙️ Admin":
        st.title("⚙️ Gestión de Datos")
        if st.button("Lanzar Backfill Histórico 2026", key="btn_backfill_final"):
            st.success("Script de carga de indicadores iniciado...")

else:
    st.info("Esperando ingreso bajo el Protocolo de Integridad IPSA-29.")
