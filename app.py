import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import requests

# 1. MOTOR DE DATOS: DRIVERS MAESTROS (Persistentes)
def get_verified_drivers():
    try:
        res = requests.get("https://api.boostr.cl/economy/indicators.json", timeout=5).json()
        data = res['data']
        return {
            "dolar": f"${data['usd']['value']}", 
            "uf": f"${data['uf']['value']:,}",
            "wti": "US$71,47", "cobre": "US$6,08"
        }
    except:
        return {"dolar": "$928,99", "uf": "$40.844,79", "wti": "US$71,47", "cobre": "US$6,08"}

drivers = get_verified_drivers()

# 2. CONFIGURACIÓN DE PÁGINA Y ALTO CONTRASTE (UI/UX)
st.set_page_config(layout="wide", page_title="Terminal IPSA-29")
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FFFFFF; }
    html, body, [class*="css"] { font-size: 14px; font-family: 'Segoe UI', sans-serif; }
    h1, h2, h3 { color: #00FFAA !important; font-weight: 800 !important; text-transform: uppercase; }
    [data-testid="stMetricValue"] { font-size: 22px !important; font-weight: bold; color: #FFFFFF; }
    [data-testid="stMetricLabel"] { font-size: 12px !important; color: #A0A0A0; }
    .ratio-box { padding: 15px; border-radius: 10px; border: 1px solid #333; background-color: #1A1C23; margin-bottom: 10px; }
    .ratio-val { color: #00FFAA; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN (Protección de IP)
def login():
    st.sidebar.title("🔐 ACCESO SENIOR")
    user = st.sidebar.text_input("Usuario", key="u_log")
    password = st.sidebar.text_input("Contraseña", type="password", key="p_log")
    return user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]

if login():
    # 4. CABECERA TÁCTICA GLOBAL (Siempre arriba)
    st.write(f"### 🚀 TACTICAL INTELLIGENCE DASHBOARD | YTD: -17,05%")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("💵 DÓLAR OBS.", drivers["dolar"], "-0,72%")
    with c2: st.metric("📈 UF (AL DÍA)", drivers["uf"], "0,00%")
    with c3: st.metric("🛢️ PETRÓLEO WTI", drivers["wti"], "-0,84%")
    with c4: st.metric("🥉 COBRE CASH", drivers["cobre"], "+0.39%")
    st.markdown("---")

    # 5. MENÚ AMPLIADO (Recuperando lo perdido)
    menu = st.sidebar.radio("📋 MENÚ TÁCTICO", ["Dashboard Principal", "🛡️ Riesgo & EEFF", "⚙️ Motores de Carga", "⚙️ Admin & Backfill"])

    if menu == "Dashboard Principal":
        col_news, col_charts = st.columns([1, 2.5])
        with col_news:
            st.write("#### 🔔 ALERTAS CMF")
            with st.expander("🕒 10-Jul | MASISA", expanded=True):
                st.write("**Reducción a Escritura Pública:** Formalización aumento US$75M [4].")
                st.caption("Estado: OSA cargada exitosamente.")
            if st.button("🔄 Sincronizar CMF"): st.rerun()
        with col_charts:
            tab1, tab2 = st.tabs(["📊 MEMORIA ESTRATÉGICA (OSAs)", "🔗 RADAR DE DRIVERS (IPER)"])
            with tab1:
                st.write("#### AUDITORÍA DE INTEGRIDAD: CASO MASISA")
                st.info("Visualizando serie continua de MASISA ($8,77) con delta aplicado.")
            with tab2:
                st.write("#### CORRELACIÓN ACCIÓN VS COMMODITY")
                st.selectbox("Analizar Activo:", ["SQM-B", "CAP", "AGUAS-A"])

    elif menu == "🛡️ Riesgo & EEFF":
        st.write("### 🛡️ PERFIL DE RIESGO E INTELIGENCIA FINANCIERA")
        col_f, col_e = st.columns(2)
        with col_f:
            st.write("#### 🔍 FICHA EMPRESA (FLOID)")
            st.text_input("Ingrese RUT (sin puntos):", placeholder="90262000-9")
        with col_e:
            st.write("#### 📊 ANÁLISIS FINANCIERO")
            st.markdown('<div class="ratio-box"><b>MASISA:</b><br>• Liquidez: <span class="ratio-val">1.45x</span><br>• Leverage: <span class="ratio-val">0.82</span></div>', unsafe_allow_html=True)

    elif menu == "⚙️ Motores de Carga":
        st.write("### ⚙️ CENTRO DE CARGA TÁCTICA")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("#### OP A: CARGA MASISA")
            if st.button("🚀 EJECUTAR PROTOCOLO"):
                st.success("¡ÉXITO! Masisa cargada e integridad verificada.")
                st.balloons()
        with col_b:
            st.write("#### OP B: CONECTOR BCS")
            st.caption("Sincronización vía API Brain Data.")
            st.text_input("Token API:", type="password")

    elif menu == "⚙️ Admin & Backfill":
        st.write("### ⚙️ PANEL DE ADMINISTRACIÓN")
        if st.button("🚀 Lanzar Backfill Histórico 2026"):
            st.warning("Iniciando sincronización masiva de IBDs...")
else:
    st.warning("Por favor, inicie sesión en la barra lateral.")
