import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from supabase import create_client, Client
from datetime import datetime

# 1. CONFIGURACIÓN DE ALTO NIVEL
st.set_page_config(layout="wide", page_title="Terminal IPSA-29 v2.0")
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. SISTEMA DE ACCESO (Login persistente)
def login():
    st.sidebar.title("🔐 Acceso Analista Senior")
    user = st.sidebar.text_input("Usuario", key="user_login")
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_login")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

# 3. MOTOR DE AUTOMATIZACIÓN: DRIVERS MACRO (Real-Time API)
def get_and_save_drivers():
    """Captura datos de Boostr y los guarda en la nueva tabla drivers_historicos"""
    try:
        # 1. Llamada real a la API de Boostr [1, 2]
        url_boostr = "https://api.boostr.cl/economy/indicators.json"
        response = requests.get(url_boostr)
        data = response.json()['data']
        
        # 2. Extracción de valores clave
        usd_val = data['dolar']['value']
        uf_val = data['uf']['value']
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')

        # 3. ZARPAZO TÁCTICO: Persistencia en Supabase
        # Guardamos el Dólar Observado
        supabase.table("drivers_historicos").upsert({
            "fecha": fecha_hoy, "driver_nemo": "USD_OBS", "valor": usd_val
        }).execute()
        
        return data
    except Exception as e:
        st.sidebar.error(f"Pestañeo en API Boostr: {e}")
        return None

if login():
    # --- PROCESAMIENTO DE DATOS ---
    drivers_data = get_and_save_drivers()
    res_nemos = supabase.table("vista_nemos_unicos").select("*").execute()
    nemo_reales = [d['nemotecnico'] for d in res_nemos.data]

# --- CABECERA ESTRATÉGICA BLINDADA (v2.0.1) ---
if drivers_data:
    c1, c2, c3, c4 = st.columns(4)
    
    # Dólar: Usamos .get() para evitar el KeyError en 'variation' [2]
    usd_val = drivers_data['dolar']['value']
    usd_var = drivers_data['dolar'].get('variation', '0.00') # Si no hay var, pone 0.00
    c1.metric("💵 Dólar Obs.", f"${usd_val}", f"{usd_var}%")
    
    # UF: Generalmente no trae variación diaria
    uf_val = drivers_data['uf']['value']
    c2.metric("🏠 UF Hoy", f"${uf_val:,.2f}")
    
    # Petróleo WTI: Aplicamos la misma lógica de seguridad
    wti_val = drivers_data['wti']['value']
    wti_var = drivers_data['wti'].get('variation', '0.00')
    c3.metric("Petróleo WTI", f"US$ {wti_val}", f"{wti_var}%")
    
    # IPC
    ipc_val = drivers_data['ipc']['value']
    c4.metric("📈 IPC", f"{ipc_val}%", "Mensual")

    st.sidebar.markdown("---")
    menu = st.sidebar.radio("📋 MENÚ DE COMANDO", 
                            ["🚨 Radar de Verdad", "🧪 Laboratorio (Masisa/SQM-B)", "📡 Monitor de Drivers"])

    if menu == "🚨 Radar de Verdad":
        st.title("🚀 Radar de Contingencia y Verdad")
        # Aquí recuperamos tu "Polígrafo" de integridad [17, Conversación previa]
        audit_nemos = ["LTM", "MASISA", "CHILE (I)", "CMPC (I)", "SQM-B"]
        res_audit = supabase.table("precios_historicos").select("nemotecnico, precio_cierre, variacion, fecha")\
            .in_("nemotecnico", audit_nemos).order("fecha", desc=True).limit(50).execute()
        
        if res_audit.data:
            st.subheader("🛠️ Auditoría de Cierres Oficiales")
            df_audit = pd.DataFrame(res_audit.data).drop_duplicates(subset=['nemotecnico'])
            st.dataframe(df_audit.style.format({"precio_cierre": "$ {:,.2f}", "variacion": "{:,.2f}%"}), use_container_width=True)

    elif menu == "🧪 Laboratorio (Masisa/SQM-B)":
        st.title("🧪 Laboratorio: Análisis de Ratio y Brechas")
        st.info("Variable Control: MASISA vs SQM-B (Efecto Lupa)")
        
        # Selector dinámico
        activos = st.multiselect("Activos a Analizar:", nemo_reales, default=["MASISA", "SQM-B"])
        denominador = st.selectbox("Escala Cartográfica (Denominador):", ["Ninguno"] + nemo_reales, index=1) # Default MASISA

        if activos:
            res = supabase.table("precios_historicos").select("fecha, nemotecnico, precio_cierre")\
                .in_("nemotecnico", activos + ([denominador] if denominador != "Ninguno" else [])).order("fecha").execute()
            df_lab = pd.DataFrame(res.data)
            df_pivot = df_lab.pivot(index='fecha', columns='nemotecnico', values='precio_cierre').ffill()

            # --- RATIO Y BETA TÁCTICO ---
            if denominador != "Ninguno" and "SQM-B" in activos:
                ratio = df_pivot["SQM-B"] / df_pivot[denominador]
                st.metric(f"Ratio SQM-B / {denominador}", f"{ratio.iloc[-1]:,.2f} uds", 
                          help="Indica cuántas unidades de Masisa se necesitan para comprar 1 SQM-B.")
                
                fig = px.line(ratio, title=f"Escala Cartográfica: SQM-B expresado en {denominador}", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

    elif menu == "📡 Monitor de Drivers":
        st.title("📡 Radar de Indicadores Adelantados")
        # Aquí consultamos la nueva tabla de drivers
        res_drivers = supabase.table("drivers_historicos").select("*").order("fecha", desc=True).limit(10).execute()
        st.write("### Historial de Drivers (Captura Autónoma)")
        st.table(pd.DataFrame(res_drivers.data))

else:
    st.info("🔒 Ingrese credenciales para activar la Terminal IPSA-29 v2.0.")
