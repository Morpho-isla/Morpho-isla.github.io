import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import requests

# --- CONFIGURACIÓN DE CONEXIÓN SUPABASE ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error conectando a Supabase: {e}")
        return None

supabase = init_connection()

# --- FUNCIÓN PARA OBTENER DATOS REALES ---
def get_stock_data(nemotecnico):
    if supabase is None:
        return pd.DataFrame()
    try:
        response = supabase.table("precios_historicos").select("*").eq("nemotecnico", nemotecnico).order("fecha").execute()
        if response.data:
            df = pd.DataFrame(response.data)
            df['fecha'] = pd.to_datetime(df['fecha'])
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error leyendo {nemotecnico}: {e}")
        return pd.DataFrame()

# --- 1. CONEXIÓN Y LOGIN (Tu estilo v1.5.1) ---
def login():
    st.sidebar.title("🔐 ACCESO SENIOR")
    # Usamos keys únicas para evitar conflictos de caché
    user = st.sidebar.text_input("Usuario", key="u_login")
    password = st.sidebar.text_input("Contraseña", type="password", key="p_login")
    
    # Validación simple (puedes poner tus credenciales en secrets también)
    valid_user = st.secrets.get("APP_USER", "admin")
    valid_pass = st.secrets.get("APP_PASSWORD", "1234")
    
    return user == valid_user and password == valid_pass

# --- 2. MOTOR DE DATOS: BOOSTR API (Dólar/UF) ---
def fetch_live_drivers():
    try:
        res = requests.get("https://api.boostr.cl/economy/indicators.json", timeout=5).json()
        d = res['data']
        return {"usd": f"${d['usd']['value']}", "uf": f"${d['uf']['value']:,}"}
    except:
        return {"usd": "$928,99", "uf": "$40.844,79"}

live = fetch_live_drivers()

# --- 3. UI/UX: ALTO CONTRASTE (CSS v1.5.1) ---
st.set_page_config(layout="wide", page_title="Terminal IPSA-29 v1.6")
st.markdown("""
    <style>
    .main { 
        background-color: #0E1117 !important; 
        color: #FFFFFF !important; 
        position: relative !important;
        z-index: 1 !important;
    }
    
    /* Ajuste específico para el título de 3 hashes (###) */
    h3 { 
        color: #00FFAA !important; 
        text-transform: uppercase; 
        border-bottom: 1px solid #333; 
        position: relative !important;
        z-index: 100 !important; /* Prioridad máxima */
        margin-top: 10px !important; /* Más espacio arriba */
        padding-top: 80px !important; /* Relleno interno */
        background-color: #0E1117 !important; /* Mismo fondo para tapar lo que haya detrás */
        display: inline-block; /* Para que el fondo funcione solo en el texto */
        width: 100%;
    }

    [data-testid="stMetricValue"] { 
        color: #00FFAA !important; font-size: 30px !important; font-weight: 800 !important;
        text-shadow: 2px 2px #000000;
    }
    [data-testid="stMetricLabel"] { color: #A0A0A0 !important; font-size: 14px !important; }
        /* Forzar que las columnas principales tengan altura visible */
    .stColumn {
        min-height: 200px !important;
        overflow: visible !important; /* Evita que el contenido se recorte */
    }
    
    /* Asegurar que el contenedor del gráfico no tenga margen negativo */
    [data-testid="stVerticalBlock"] {
        margin-top: 0px !important;
    }

    /* Tu estilo del título (ajustado) */
    h3 { 
        color: #00FFAA !important; 
        text-transform: uppercase; 
        border-bottom: 1px solid #333; 
        position: relative !important;
        z-index: 100 !important;
        margin-top: 20px !important;
        padding-top: 10px !important;
        background-color: #0E1117 !important;
        display: block;
        width: 100%;
    }   
    </style>   
    """, unsafe_allow_html=True)

# --- EJECUCIÓN MAESTRA ---
if login():
    # 4. CABECERA TÁCTICA GLOBAL
    st.write("### 🚀 TACTICAL INTELLIGENCE DASHBOARD | YTD: -17,05%")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("💵 DÓLAR OBS. (LIVE)", live["usd"], "-0,72%")
    with c2: st.metric("📈 UF (AL DÍA)", live["uf"], "0.00%")
    with c3: st.metric("🛢️ WTI OIL (UPDATE)", "US$76,67", "UP 7.2%") 
    with c4: st.metric("🥉 COBRE (REF)", "US$6,08", "STATIC")
    st.markdown("---")

    menu = st.sidebar.radio("📋 MENÚ TÁCTICO", ["Dashboard Principal", "🛡️ Riesgo & EEFF", "⚙️ Motores de Carga"])

    if menu == "Dashboard Principal":
        # Controles para seleccionar acción (Aquí está la clave)
        st.sidebar.markdown("### 🎯 OBJETIVOS")
        target = st.sidebar.selectbox("Seleccionar Nemotécnico", ["MASISA", "ABC", "CENCOSUD", "CHILE"])
        
        # Botones rápidos de emergencia
        c_btn1, c_btn2 = st.sidebar.columns(2)
        if c_btn1.button("VER MASISA"):
            target = "MASISA"
        if c_btn2.button("VER ABC"):
            target = "ABC"

        col_news, col_charts = st.columns(2) # División 50/50 estándar   
        
        with col_news:
            st.write("#### 🔔 NOTAS DE CIERRE")
            st.success("✅ **VENTA LTM (9:30 AM):** Ejecución magistral antes de caída IPSA.")
            with st.expander(f"🕒 10-Jul | {target}", expanded=True):
                st.write(f"**Integridad:** Datos cargados desde Supabase para {target}.")
        
        with col_charts:
            tab1, tab2 = st.tabs(["📊 MEMORIA ESTRATÉGICA (REAL)", "🔗 RADAR DE DRIVERS"])
            
            with tab1:
                st.write(f"#### AUDITORÍA: CASO {target}")
                
                # AQUÍ CONECTAMOS CON TUS DATOS REALES
                df = get_stock_data(target)
                
                if not df.empty:
                    # Gráfico con Plotly Express usando tus datos reales
                    fig = px.line(df, x='fecha', y='precio_cierre', 
                                  title=f"Evolución Real de {target} (Junio 2026)",
                                  color_discrete_sequence=['#00FFAA'])
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                      font=dict(color='white'))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Mostrar métricas reales del último día
                    last_close = df.iloc[-1]['precio_cierre']
                    st.metric(f"Cierre Real {target}", f"${last_close:,.2f}")
                else:
                    st.warning(f"⚠️ No hay datos en Supabase para {target}. Revisa la carga masiva.")

            with tab2:
                st.warning("⚠️ Alerta WTI: Divergencia detectada. Revisar costos logísticos IPSA-29.")

    elif menu == "⚙️ Motores de Carga":
        st.write("### ⚙️ CENTRO DE CARGA TÁCTICA")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("#### OP A: PROTOCOLO MASISA")
            if st.button("🚀 EJECUTAR CARGA"): st.balloons()
        with col_b:
            st.write("#### OP B: API BRAIN DATA (BCS)")
            st.info("Estructura v1.6-Alpha: Sincronización automática vía API Bolsa de Santiago.")

else:
    st.warning("🔒 Por favor, inicie sesión para acceder a la terminal.")   
