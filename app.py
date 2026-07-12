import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from supabase import create_client, Client

# 1. Configuración de Conexión (Secrets)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. DEFINICIÓN DE FUNCIONES
def login():
    st.sidebar.title("🔐 Acceso Analista Senior")
    user = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False
# 1. DEFINICIÓN DE FUNCIONES ESTRATÉGICAS
def fetch_realtime_drivers():
    """Captura de la 'Película' en tiempo real (API Boostr)"""
    try:
        url = "https://api.boostr.cl/economy/indicators.json"
        response = requests.get(url)
        return response.json()['data']
    except Exception: return None

# 2. ACCESO Y NAVEGACIÓN
if login(): # Asumimos la función login definida arriba
    st.sidebar.title("🗂️ Terminal IPSA-29")
    
    # Menú de Navegación Basado en Flujo vs Stock
    menu = st.sidebar.radio("Módulos:", [
        "📺 La Película (Real-Time)", 
        "📖 El Libro (Histórico)", 
        "🛡️ Perfil de Riesgo",
        "⚙️ El Motor (Admin)"
    ])

    # --- INDICADORES TRANSVERSALES ---
    drivers = fetch_realtime_drivers()
    if drivers:
        st.sidebar.markdown("---")
        st.sidebar.metric("Dólar", f"${drivers.get('dolar', {}).get('value')}")
        st.sidebar.metric("UF", f"${drivers.get('uf', {}).get('value')}")

    # 3. LÓGICA DE MÓDULOS
    if menu == "📺 La Película (Real-Time)":
        st.title("📺 Flujo de Mercado en Vivo")
        st.info("Monitoreo dinámico de los 29 constituyentes y drivers monetarios [Boostr].")
        # Aquí va la tabla de precios del día (Condición 'T' vs 'N') [4]

    elif menu == "📖 El Libro (Histórico)":
        st.title("📖 Memoria Estratégica y Ajustes")
        # Aquí van tus dos gráficos:
        # 1. El de Integridad (Precio Ajustado OSAs) [5]
        # 2. El Dual (Correlación con IPER: Cobre, Litio, Hierro) [6]

    elif menu == "🛡️ Perfil de Riesgo":
        st.title("🛡️ Evaluación de Solvencia Institucional")
        st.write("Integración vía **Floid** para el Certificado de Deudas CMF [1, 2].")
        st.warning("Este módulo permite auditar la salud financiera de emisores como Masisa.")

    elif menu == "⚙️ El Motor (Admin)":
        st.title("⚙️ Gestión de la Base de Datos")
        if st.button("Lanzar Backfill Drivers 2026"):
            # Aquí activaremos el script independiente que conversamos
            st.success("Sincronizando históricos de UF y Dólar...")
def fetch_realtime_drivers():
    try:
        url = "https://api.boostr.cl/economy/indicators.json"
        response = requests.get(url)
        data = response.json()['data']
        return data
    except Exception:
        return None

# 3. CUERPO PRINCIPAL DE LA APP
if login():
    st.title("📊 Dashboard Bursátil IPSA-29")
    
    # Captura de Drivers (Flujo en tiempo real)
    drivers = fetch_realtime_drivers()
    if drivers:
        st.sidebar.markdown("### 🕒 Drivers en Tiempo Real")
        val_dolar = drivers.get('dolar', {}).get('value', 'N/D')
        st.sidebar.metric("Dólar", f"${val_dolar}")
        st.sidebar.metric("UF", f"${drivers.get('uf', {}).get('value', 'N/D')}")

    # Carga de Datos de Supabase (Stock Histórico)
    try:
        response = supabase.table("vista_precios_ajustados").select("*").execute()
        df = pd.DataFrame(response.data)
        
        if not df.empty:
            nemos = sorted(df['nemotecnico'].unique())
            
            # --- SECCIÓN 1: EVOLUCIÓN DE PRECIO ---
            selected_nemo = st.selectbox("Seleccione Nemotécnico para Análisis:", nemos)
            df_filtered = df[df['nemotecnico'] == selected_nemo].sort_values(by="fecha")
            
            fig = px.line(df_filtered, x='fecha', y=['precio_mercado', 'precio_ajustado'],
                          title=f"Evolución: {selected_nemo} (Ajustado por OSAs)")
            st.plotly_chart(fig, use_container_width=True)

            # --- SECCIÓN 2: ANÁLISIS DE CORRELACIÓN (Línea 58 Corregida) ---
            st.markdown("---")
            st.subheader("🔗 Análisis de Correlación: Acción vs Commodity")
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                nemo_corr = st.selectbox("Acción Base:", nemos, key="c1")
            with col_c2:
                # Basado en la canasta IPER (Cobre, Litio, Celulosa)
                driver_opt = st.selectbox("Commodity Driver:", ["Cobre", "Litio", "Hierro", "WTI"])
            
            st.info(f"Trayectoria estratégica de **{nemo_corr}** frente al driver **{driver_opt}**")
            
            # Placeholder del gráfico dual
            fig_dual = px.line(df_filtered, x='fecha', y='precio_ajustado', 
                               title=f"Correlación Histórica: {nemo_corr} vs {driver_opt}")
            st.plotly_chart(fig_dual, use_container_width=True)

            # --- SECCIÓN 3: AUDITORÍA ---
            with st.expander("🔍 Ver Matriz Completa de Registros"):
                st.dataframe(df.sort_values(by="fecha", ascending=False))

    except Exception as e:
        st.error(f"Error de sistema: {e}")

else:
    st.info("Sistema blindado bajo el Protocolo de Integridad IPSA-29.")
