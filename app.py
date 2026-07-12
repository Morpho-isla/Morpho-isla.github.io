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
    # Este es el widget que generaba el error por duplicidad
    user = st.sidebar.text_input("Usuario") 
    password = st.sidebar.text_input("Contraseña", type="password")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

def fetch_realtime_drivers():
    try:
        url = "https://api.boostr.cl/economy/indicators.json"
        response = requests.get(url)
        return response.json().get('data')
    except Exception: return None

# 3. CUERPO ÚNICO DE LA APP (Línea 72 corregida)
if login():
    st.sidebar.title("🗂️ Terminal IPSA-29")
    
    # Menú de Navegación del Analista
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

    # --- LÓGICA DE LOS MÓDULOS ---
    if menu == "📺 La Película (Real-Time)":
        st.title("📺 Flujo de Mercado en Vivo")
        st.info("Monitoreo dinámico de los 29 constituyentes [Protocolo IPSA-29].")
        # Aquí va la tabla de precios del día

    elif menu == "📖 El Libro (Histórico)":
        st.title("📖 Memoria Estratégica y Ajustes")
        st.info("Consulta de integridad histórica y ajuste por eventos corporativos (OSAs).")

        try:
            # 1. Carga de datos desde la Vista de Integridad
            response = supabase.table("vista_precios_ajustados").select("*").execute()
            df = pd.DataFrame(response.data)
            
            if not df.empty:
                nemos = sorted(df['nemotecnico'].unique())
                
                # --- GRÁFICO 1: INTEGRIDAD (Arriba) ---
                st.subheader("🛠️ Auditoría de Precio Ajustado")
                selected_nemo = st.selectbox("Seleccione Acción para validar ajuste:", nemos)
                df_filtered = df[df['nemotecnico'] == selected_nemo].sort_values(by="fecha")
                
                fig_adj = px.line(df_filtered, x='fecha', y=['precio_mercado', 'precio_ajustado'],
                                  title=f"Serie Continua: {selected_nemo}")
                st.plotly_chart(fig_adj, use_container_width=True)

                # --- GRÁFICO 2: CORRELACIÓN (Abajo) ---
                st.markdown("---")
                st.subheader("🔗 Radar de Drivers (IPER)")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    nemo_corr = st.selectbox("Acción Base:", nemos, key="c_base")
                with col_c2:
                    driver_opt = st.selectbox("Commodity Driver:", ["Cobre", "Litio", "Hierro", "WTI"], key="c_driver")
                
                st.write(f"Comparando flujo de **{nemo_corr}** vs fundamental de **{driver_opt}**")
                # Placeholder del gráfico dual (usamos df_filtered por ahora)
                fig_dual = px.line(df_filtered, x='fecha', y='precio_ajustado', 
                                   title=f"Divergencia Estratégica: {nemo_corr} vs {driver_opt}")
                st.plotly_chart(fig_dual, use_container_width=True)

            else:
                st.warning("La base de datos está esperando el PVI de la jornada.")

        except Exception as e:
            st.error(f"Error al conectar con el 'Libro': {e}")        # Aquí van tus gráficos de Precios Ajustados y Correlación
        
    elif menu == "🛡️ Perfil de Riesgo":
        st.title("🛡️ Evaluación de Solvencia")
        st.write("Módulo para integración con **Floid** para deudas CMF.")

    elif menu == "⚙️ El Motor (Admin)":
        st.title("⚙️ Gestión de Base de Datos")
        st.button("Lanzar Backfill Drivers 2026")

else:
    st.info("Sistema blindado bajo el Protocolo de Integridad IPSA-29.")
