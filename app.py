import streamlit as st
import pandas as pd
import plotly.express as px
import requests  # Herramienta para conectar con las APIs de mercado [1]
from supabase import create_client, Client

# 1. Configuración de Conexión (Secrets)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. DEFINICIÓN DE FUNCIONES (Deben ir primero)

def login():
    st.sidebar.title("🔐 Acceso Analista Senior")
    user = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

def fetch_realtime_drivers():
    """Captura indicadores desde la API de Boostr [1, 2]"""
    try:
        # Endpoint oficial para UF, Dólar e IPC en una sola consulta [2]
        url = "https://api.boostr.cl/economy/indicators.json"
        response = requests.get(url)
        data = response.json()['data']
        return data
    except Exception:
        return None

# 3. CUERPO PRINCIPAL DE LA APP
if login():
    st.title("📊 Dashboard Bursátil IPSA-29")
    st.markdown("---")

    # Ejecución de la captura en tiempo real (Línea 26 corregida)
    drivers = fetch_realtime_drivers()
    
    if drivers:
        st.sidebar.markdown("### 🕒 Drivers en Tiempo Real")
        
        # Extraemos los valores de forma segura
        val_dolar = drivers.get('dolar', {}).get('value', 'N/D')
        var_dolar = drivers.get('dolar', {}).get('variation') # Puede ser None
        
        # Mostramos la métrica: si var_dolar existe, se muestra como delta
        st.sidebar.metric(
            label="Dólar", 
            value=f"${val_dolar}", 
            delta=f"{var_dolar}%" if var_dolar else None
        )
        
        st.sidebar.metric("UF", f"${drivers.get('uf', {}).get('value', 'N/D')}")
        st.sidebar.metric("IPC", f"{drivers.get('ipc', {}).get('value', 'N/D')}%")
    # --- NUEVA SECCIÓN: ANÁLISIS DE CORRELACIÓN ---
            st.markdown("---")
            st.subheader("🔗 Análisis de Correlación: Acción vs Commodity")
            st.info("Esta sección permite contrastar el flujo de la acción con los Drivers Maetros del IPER.")

            # 1. Selectores de comparación
            col_corr1, col_corr2 = st.columns(2)
            with col_corr1:
                # Reutilizamos los nemos de los 29 constituyentes
                nemo_base = st.selectbox("Seleccione Acción IPSA-29:", nemos, key="corr_ipsa")
            with col_corr2:
                # Drivers definidos en nuestro Mapa de Drivers (IPER/Cochilco)
                commodity_driver = st.selectbox("Agregar Commodity Driver:", 
                                               ["Hierro", "Cobre", "Litio", "Oro", "WTI", "Dólar"])

            # 2. Lógica de visualización Dual (Película de Datos)
            # Nota: Esto asume que cargaremos los históricos de commodities en 'drivers_mercado'
            st.write(f"Comparando trayectoria de **{nemo_base}** vs **{commodity_driver}**")
            
            # Generamos un gráfico placeholder con los datos que ya tenemos (ajustados)
            fig_dual = px.line(df_filtered, x='fecha', y='precio_ajustado', 
                               title=f"Correlación: {nemo_base} vs {commodity_driver}")
            
            # (En la sesión nocturna configuraremos el doble eje Y para los commodities)
            st.plotly_chart(fig_dual, use_container_width=True)
    # Recuperación de datos históricos desde Supabase
    try:
        response = supabase.table("vista_precios_ajustados").select("*").execute()
        df = pd.DataFrame(response.data)
        
        if not df.empty:
            # Selector de Nemotécnico para el análisis de los 29 constituyentes [4, 5]
            nemos = sorted(df['nemotecnico'].unique())
            selected_nemo = st.selectbox("Seleccione Nemotécnico:", nemos)

            # Filtrado y Gráfico
            df_filtered = df[df['nemotecnico'] == selected_nemo].sort_values(by="fecha")
            st.subheader(f"Serie de Tiempo: {selected_nemo}")
            fig = px.line(df_filtered, x='fecha', y=['precio_mercado', 'precio_ajustado'],
                          title="Evolución de Precio con Ajuste OSAs")
            st.plotly_chart(fig, use_container_width=True)

            # Sección de Auditoría (Matriz Completa IPSA-29)
            with st.expander("🔍 Ver Matriz Completa de Registros (Auditoría)"):
                st.dataframe(df.sort_values(by="fecha", ascending=False), use_container_width=True)
        else:
            st.error("Base de datos vacía. Requiere carga de jornada.")

    except Exception as e:
        st.error(f"Error en conexión Supabase: {e}")

else:
    st.info("Sistema blindado bajo el Protocolo de Integridad IPSA-29.")
