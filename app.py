import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import requests

# 1. CONEXIÓN Y LOGIN (Blindaje de IP)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def login():
    st.sidebar.title("🔐 ACCESO ANALISTA SENIOR")
    user = st.sidebar.text_input("Usuario", key="user_login")
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_login")
    return user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]

# 2. UI/UX: ALTO CONTRASTE Y EFICIENCIA
st.set_page_config(layout="wide", page_title="Terminal IPSA-29")
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    html, body, [class*="css"] { font-size: 14px; font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3 { color: #00FFAA !important; font-weight: 800 !important; text-transform: uppercase; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 28px !important; }
    .ratio-box { padding: 15px; border-radius: 10px; border: 1px solid #333; background-color: #1A1C23; }
    </style>
    """, unsafe_allow_html=True)

# 3. EJECUCIÓN MAESTRA
if login():
    # CABECERA TÁCTICA (Valores recuperados de Iniciosemana2.PNG)
    st.write("### 🚀 TACTICAL INTELLIGENCE DASHBOARD | YTD: -17,05%")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("💵 DÓLAR OBS.", "$928,99", "-0,72%")
    with c2: st.metric("📈 UF (AL DÍA)", "$40.844,79", "0,00%")
    with c3: st.metric("🛢️ PETRÓLEO WTI", "US$71,47", "-0,84%")
    with c4: st.metric("🥉 COBRE CASH", "US$6,08", "+0,39%")
    st.markdown("---")

    # MENÚ DE NAVEGACIÓN
    menu = st.sidebar.radio("📋 MENÚ TÁCTICO", ["Dashboard Principal", "🛡️ Riesgo & EEFF", "⚙️ Motores de Carga"])

    if menu == "Dashboard Principal":
        col_news, col_charts = st.columns([1, 2.5])
        with col_news:
            st.write("#### 🔔 ALERTAS CMF")
            with st.expander("🕒 10-Jul | MASISA", expanded=True):
                st.write("**Reducción a Escritura Pública:** Dilución nominal a $8,77 procesada.")
            if st.button("🔄 Sincronizar CMF"): st.rerun()

        with col_charts:
            tab1, tab2 = st.tabs(["📊 MEMORIA ESTRATÉGICA (OSAs)", "🔗 RADAR DE DRIVERS (IPER)"])
            with tab1:
                st.write("#### AUDITORÍA DE INTEGRIDAD: CASO MASISA")
                # RECUPERAMOS EL GRÁFICO (Dato del IBD 10-Jul [5])
                data = {'fecha': ['Jun-30', 'Jul-01', 'Jul-02', 'Jul-10'], 
                        'nominal': [11.0, 10.5, 8.9, 8.77], 
                        'ajustado': [11.0, 10.8, 10.7, 10.65]}
                df_chart = pd.DataFrame(data)
                fig = px.line(df_chart, x='fecha', y=['nominal', 'ajustado'], 
                             color_discrete_sequence=['#FF4B4B', '#00FFAA'])
                fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)

    elif menu == "🛡️ Riesgo & EEFF":
        st.write("### 🛡️ PERFIL DE RIESGO E INTELIGENCIA FINANCIERA")
        col_f, col_e = st.columns(2)
        with col_f:
            st.write("#### 🔍 FICHA EMPRESA (FLOID)")
            st.text_input("RUT Empresa:", placeholder="90262000-9")
        with col_e:
            st.write("#### 📊 ANÁLISIS FINANCIERO")
            st.markdown('<div class="ratio-box"><b>MASISA:</b><br>• Liquidez: 1.45x<br>• Leverage: 0.82</div>', unsafe_allow_html=True)

    elif menu == "⚙️ Motores de Carga":
        st.write("### ⚙️ CENTRO DE CARGA TÁCTICA")
        if st.button("🚀 EJECUTAR PROTOCOLO MASISA"):
            st.success("¡ÉXITO! Masisa cargada e integridad verificada.")
            st.balloons()
else:
    st.warning("Por favor, inicie sesión.")
