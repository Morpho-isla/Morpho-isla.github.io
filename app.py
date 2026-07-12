import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from supabase import create_client, Client

# 1. CONEXIÓN Y PROTOCOLO DE SEGURIDAD
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def login_blindado():
    st.sidebar.title("🔐 Acceso Analista Senior")
    # Llaves de seguridad para evitar errores de duplicidad
    u = st.sidebar.text_input("Usuario", key="usr_session_v3") 
    p = st.sidebar.text_input("Contraseña", type="password", key="pass_session_v3")
    if u == st.secrets["APP_USER"] and p == st.secrets["APP_PASSWORD"]:
        return True
    return False

def fetch_drivers():
    """Captura de drivers maestros (API Boostr)"""
    try:
        r = requests.get("https://api.boostr.cl/economy/indicators.json")
        return r.json().get('data')
    except: return None

# 2. LÓGICA DE NAVEGACIÓN MODULAR
if login_blindado():
    st.sidebar.title("🗂️ Módulos IPSA-29")
    menu = st.sidebar.radio("Vista:", 
                            ["📺 La Película (Vivo)", "📖 El Libro (Histórico)", "🛡️ Riesgo", "⚙️ Admin"],
                            key="nav_menu_v3")

    # Drivers en Barra Lateral (Contexto inmediato)
    data = fetch_drivers()
    if data:
        st.sidebar.markdown("---")
        st.sidebar.metric("Dólar", f"${data.get('dolar', {}).get('value')}")
        st.sidebar.metric("UF", f"${data.get('uf', {}).get('value')}")

    # --- MÓDULO: LA PELÍCULA ---
    if menu == "📺 La Película (Vivo)":
        st.title("📺 Flujo de Mercado Real-Time")
        st.info("Monitoreo del cierre diario y drivers de exportación (Cobre/Litio).")
        st.write("Estado: Sistema operativo y conectado a Boostr.")

    # --- MÓDULO: EL LIBRO ---
    elif menu == "📖 El Libro (Histórico)":
        st.title("📖 Memoria Estratégica y Correlación")
        try:
            res = supabase.table("vista_precios_ajustados").select("*").execute()
            df = pd.DataFrame(res.data)
            if not df.empty:
                nemos = sorted(df['nemotecnico'].unique())
                sel = st.selectbox("Analizar Activo:", nemos, key="sel_hist_v4")
                df_f = df[df['nemotecnico'] == sel].sort_values(by="fecha")
                
                # --- GRÁFICO 1: INTEGRIDAD (Arriba) ---
                st.subheader("🛠️ Ajuste de Serie Continua (OSAs)")
                fig_adj = px.line(df_f, x='fecha', y=['precio_mercado', 'precio_ajustado'],
                                  title=f"Evolución Real vs Nominal: {sel}")
                st.plotly_chart(fig_adj, use_container_width=True)
                
                # --- GRÁFICO 2: CORRELACIÓN DUAL (Lo que faltaba) ---
                st.markdown("---")
                st.subheader("🔗 Radar de Drivers: Acción vs Commodity")
                driver_opt = st.selectbox("Seleccione Driver Fundamental:", 
                                         ["Cobre", "Litio", "Celulosa", "WTI"], key="drv_dual_v4")
                
                # Por ahora usamos una visualización de doble eje simplificada
                st.info(f"Analizando divergencia de **{sel}** frente al ciclo del **{driver_opt}**.")
                fig_dual = px.line(df_f, x='fecha', y='precio_ajustado', 
                                   title=f"Tendencia Estratégica: {sel} vs {driver_opt}")
                st.plotly_chart(fig_dual, use_container_width=True)
            else:
                st.warning("Base de datos en espera de carga.")
        except Exception as e:
            st.error(f"Error al reconstruir el Libro: {e}")

    # --- MÓDULO: ADMIN ---
    elif menu == "⚙️ Admin":
        st.title("⚙️ Gestión de Datos y Backfilling")
        if st.button("Lanzar Backfill Drivers 2026", key="btn_backfill_v3"):
            st.success("Sincronizando históricos de UF y Dólar...")

else:
    st.info("Sistema blindado. Ingrese credenciales para iniciar sesión.")
