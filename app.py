import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import requests

# --- 1. CONFIGURACIÓN Y CONEXIÓN (Blindada) ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ Error Supabase: {e}")
        return None

supabase = init_connection()

def get_stock_data(nemotecnico):
    if supabase is None: return pd.DataFrame()
    try:
        response = supabase.table("precios_historicos").select("*").eq("nemotecnico", nemotecnico).order("fecha").execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # 1. Primero convertimos la fecha
            df['fecha'] = pd.to_datetime(df['fecha'])
            
            # 2. AHORA forzamos la conversión numérica (ANTES del return)
            df['precio_cierre'] = pd.to_numeric(df['precio_cierre'], errors='coerce')
            
            # Opcional: Haz lo mismo con otras columnas numéricas si es necesario
            # df['volumen'] = pd.to_numeric(df['volumen'], errors='coerce')
            
            return df  # <--- El return va AL FINAL, después de limpiar
            
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error datos: {e}")
        return pd.DataFrame()   
# --- 2. LOGIN SIMPLE ---
def login():
    st.sidebar.title("🔐 ACCESO")
    u = st.sidebar.text_input("Usuario", key="u")
    p = st.sidebar.text_input("Contraseña", type="password", key="p")
    # Credenciales por defecto si no están en secrets
    valid_u = st.secrets.get("APP_USER", "admin")
    valid_p = st.secrets.get("APP_PASSWORD", "1234")
    return u == valid_u and p == valid_p

# --- 3. UI & ESTILOS (Oscuro y Táctico) ---
st.set_page_config(layout="wide", page_title="Terminal IPSA-29")
st.markdown("""
    <style>
    .main { background-color: #0E1117 !important; color: #FFF !important; }
    h3 { color: #00FFAA !important; text-transform: uppercase; border-bottom: 1px solid #333; }
    [data-testid="stMetricValue"] { color: #00FFAA !important; font-size: 28px !important; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. EJECUCIÓN PRINCIPAL ---
if login():
    # Cabecera
    st.write("### 🚀 TACTICAL DASHBOARD | YTD: -17,05%")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💵 DÓLAR", "$928,99", "-0.7%")
    c2.metric("📈 UF", "$40.844", "0.0%")
    c3.metric("🛢️ WTI", "$76,67", "UP")
    c4.metric("🥉 COBRE", "$6,08", "STATIC")
    st.markdown("---")

    # Controles
    st.sidebar.markdown("### 🎯 OBJETIVOS")
    target = st.sidebar.selectbox("Nemotécnico", ["MASISA", "ABC", "CENCOSUD", "CHILE"])
    if st.sidebar.button("VER MASISA"): target = "MASISA"
    if st.sidebar.button("VER ABC"): target = "ABC"

    # Área Principal
    col_news, col_charts = st.columns([1, 2])
    
    with col_news:
        st.write("#### 🔔 NOTAS")
        st.success("✅ **VENTA LTM:** Ejecución magistral.")
        st.info(f"Analizando: **{target}**")

    with col_charts:
        tab1, tab2 = st.tabs(["📊 GRÁFICO REAL", "🔗 DRIVERS"])
        with tab1:
            st.write(f"#### AUDITORÍA: {target}")
            df = get_stock_data(target)
            
            if not df.empty:
                st.success(f"✅ {len(df)} registros cargados.")
                # Gráfico con sombra (fill)
                fig = px.line(df, x='fecha', y='precio_cierre', 
                              title=f"Evolución {target}",
                              color_discrete_sequence=['#00FFAA'])
                fig.update_traces(fill='tozeroy', fillcolor='rgba(0, 255, 170, 0.2)')
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                  font=dict(color='white'), height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # Métrica final
                st.metric("Cierre Reciente", f"${df.iloc[-1]['precio_cierre']:,.2f}")
            else:
                st.warning(f"⚠️ Sin datos para {target} en Supabase.")
                
        with tab2:
            st.write("#### Correlaciones Macro")
            st.info("Próximamente: Dólar, Cobre y WTI en tiempo real.")

else:
    st.warning("🔒 Inicie sesión para operar.")   
