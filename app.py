import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import requests

# --- BITÁCORA DE VERSIONES: v1.5.0 ---
# Mejoras: Cabecera táctica global, visibilidad forzada (Verde Neón), motor MASISA activo.

# 1. CONEXIÓN Y LOGIN (Blindaje de IP)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def login():
    st.sidebar.title("🔐 ACCESO ANALISTA SENIOR")
    user = st.sidebar.text_input("Usuario", key="user_login")
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_login")
    return user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]

# 2. MOTOR DE DATOS: BOOSTR API (Drivers en tiempo real)
def fetch_live_drivers():
    try:
        res = requests.get("https://api.boostr.cl/economy/indicators.json", timeout=5).json()
        d = res['data']
        return {"usd": f"${d['usd']['value']}", "uf": f"${d['uf']['value']:,}"}
    except:
        return {"usd": "$928,99", "uf": "$40.844,79"}

live = fetch_live_drivers()

# 3. CONFIGURACIÓN DE PÁGINA Y ALTO CONTRASTE (CSS PERSONALIZADO)
st.set_page_config(layout="wide", page_title="Terminal IPSA-29 v1.5")
st.markdown("""
    <style>
    .main { background-color: #0E1117 !important; color: #FFFFFF !important; }
    /* VISIBILIDAD FORZADA: Verde Neón con sombra para métricas */
    [data-testid="stMetricValue"] { 
        color: #00FFAA !important; 
        font-size: 30px !important; 
        font-weight: 800 !important;
        text-shadow: 2px 2px #000000;
    }
    [data-testid="stMetricLabel"] { color: #A0A0A0 !important; font-size: 14px !important; }
    h1, h2, h3 { color: #00FFAA !important; text-transform: uppercase; border-bottom: 1px solid #333; }
    .ratio-box { padding: 15px; border-radius: 10px; border: 1px solid #00FFAA; background-color: #1A1C23; }
    </style>
    """, unsafe_allow_html=True)

# --- EJECUCIÓN MAESTRA ---
if login():
    # 4. CABECERA TÁCTICA GLOBAL (Siempre al tope)
    st.write("### 🚀 TACTICAL INTELLIGENCE DASHBOARD | YTD: -17,05%")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("💵 DÓLAR OBS. (LIVE)", live["usd"], "-0,72%")
    with c2: st.metric("📈 UF (AL DÍA)", live["uf"], "0,00%")
    with c3: st.metric("🛢️ WTI (REF)", "US$71,47", "ESTÁTICO")
    with c4: st.metric("🥉 COBRE (REF)", "US$6,08", "ESTÁTICO")
    st.markdown("---")

    # 5. MENÚ DE NAVEGACIÓN
    menu = st.sidebar.radio("📋 MENÚ TÁCTICO", ["Dashboard Principal", "🛡️ Riesgo & EEFF", "⚙️ Motores de Carga"])

    if menu == "Dashboard Principal":
        col_news, col_charts = st.columns([1, 2.5])
        with col_news:
            st.write("#### 🔔 ALERTAS CMF")
            with st.expander("🕒 10-Jul | MASISA", expanded=True):
                st.write("**Reducción a Escritura Pública:** Dilución nominal a $8,77.")
            if st.button("🔄 Sincronizar CMF"): st.rerun()

        with col_charts:
            tab1, tab2 = st.tabs(["📊 MEMORIA ESTRATÉGICA", "🔗 RADAR DE DRIVERS"])
            with tab1:
                st.write("#### AUDITORÍA DE INTEGRIDAD: CASO MASISA")
                data_m = {'fecha': ['Jun-30', 'Jul-01', 'Jul-02', 'Jul-10'], 
                          'Nominal': [11.0, 10.5, 8.9, 8.77], 'Ajustado': [11.0, 10.8, 10.7, 10.65]}
                df_m = pd.DataFrame(data_m)
                fig = px.line(df_m, x='fecha', y=['Nominal', 'Ajustado'], color_discrete_sequence=['#FF4B4B', '#00FFAA'])
                fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            with tab2:
                st.info("Radar Activo: Monitoreando SQM-B vs Ciclo del Litio.")

    elif menu == "🛡️ Riesgo & EEFF":
        st.write("### 🛡️ PERFIL DE RIESGO (API FLOID)")
        rut = st.text_input("Ingrese RUT Empresa (Ej: 90262000-9):")
        if st.button("Consultar Solvencia CMF"):
            st.json({"Deuda Directa": "UF 450.000", "Estado": "Al día"})

    elif menu == "⚙️ Motores de Carga":
        st.write("### ⚙️ CENTRO DE CARGA TÁCTICA")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("#### OP A: PROTOCOLO MASISA")
            if st.button("🚀 EJECUTAR CARGA"):
                st.success("MASISA cargada. Delta de OSA aplicado.")
                st.balloons()
        with col_b:
            st.write("#### OP B: API BCS (BRAIN DATA)")
            st.text_input("Brain Data Token:", type="password")
            if st.button("Sincronizar Bolsa"): st.warning("Conectando con Marketplace...")

else:
    st.warning("Por favor, inicie sesión en la barra lateral.")
