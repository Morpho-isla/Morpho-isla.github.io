import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import numpy as np

# Configuración y Conexión
st.set_page_config(layout="wide", page_title="Terminal IPSA-29 v1.9.1")
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
def login():
    st.sidebar.title("🔐 Acceso Analista Senior")
    user = st.sidebar.text_input("Usuario", key="user_login")
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_login")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False
if login(): # Función login() persistente
    menu = st.sidebar.radio("📋 MENÚ TÁCTICO", ["🚨 Radar de Emergencia", "🧪 Laboratorio de Análisis"])
    
    # Zarpazo: Obtenemos nemos únicos desde la vista SQL que creamos
    res_nemos = supabase.table("vista_nemos_unicos").select("*").execute()
    nemo_reales = [d['nemotecnico'] for d in res_nemos.data]

    if menu == "🚨 Radar de Emergencia":
        st.title("🚀 Radar de Contingencia y Verdad")
        
        # 1. RECUPERACIÓN DE TABLA DE INTEGRIDAD (Auditores de LTM, Chile, BCI)
        with st.container():
            st.subheader("🛠️ Auditoría de Integridad: El Polígrafo del Búnker")
            audit_nemos = ["LTM", "MASISA", "CHILE (I)", "CMPC (I)", "VAPORES (I)", "BCI (I)", "BSANTANDER (I)"]
            
            # Consultamos los cierres más recientes de estos nemos específicos
            res_audit = supabase.table("precios_historicos")\
                .select("nemotecnico, precio_cierre, variacion, fecha")\
                .in_("nemotecnico", audit_nemos)\
                .order("fecha", desc=True).limit(50).execute()
            
            if res_audit.data:
                df_audit = pd.DataFrame(res_audit.data).drop_duplicates(subset=['nemotecnico'])
                st.write("📈 *Precios de Cierre Oficiales (Base para verificar Renta4/BancoEstado):*")
                st.dataframe(df_audit.style.format({
                    "precio_cierre": "$ {:,.2f}",
                    "variacion": "{:,.2f}%"
                }), use_container_width=True)

        # 2. RADAR DE ALZAS Y BAJAS (Filtrado Total de CFI e Índices)
        st.markdown("---")
        res_raw = supabase.table("precios_historicos").select("nemotecnico, precio_cierre, variacion")\
            .order("fecha", desc=True).limit(300).execute()
        
        df_all = pd.DataFrame(res_raw.data).drop_duplicates(subset=['nemotecnico'])
        
        # Filtro potente: Solo acciones puras (eliminamos CFI e índices) [3, 4]
        df_acciones = df_all[
            (~df_all['nemotecnico'].str.contains('CFI', na=False)) & 
            (~df_all['nemotecnico'].isin(['IPSA', 'IGPA', 'SPIPSA', 'SPCLX']))
        ].copy()

        c1, c2 = st.columns(2)
        with c1:
            st.success("📈 Top 10 Alzas Reales (Acciones)")
            st.dataframe(df_acciones.nlargest(10, 'variacion')[['nemotecnico', 'precio_cierre', 'variacion']]\
                         .style.format({"precio_cierre": "$ {:,.2f}", "variacion": "{:,.2f}%"}))
        with c2:
            st.error("📉 Top 10 Bajas Reales (Acciones)")
            st.dataframe(df_acciones.nsmallest(10, 'variacion')[['nemotecnico', 'precio_cierre', 'variacion']]\
                         .style.format({"precio_cierre": "$ {:,.2f}", "variacion": "{:,.2f}%"}))

    elif menu == "🧪 Laboratorio de Análisis":
        # (Aquí va tu código de Varianza, Volatilidad y Escala Cartográfica v1.9.0)
        st.title("🧪 Laboratorio de Inteligencia Institucional")
        # ... [Mantenemos la potencia de los gráficos y estadísticos] ...        
        # SELECTORES DEL LABORATORIO
        activos = st.multiselect("Seleccione Activos para Analizar:", nemo_reales, default=["MASISA", "LTM"])
        driver = st.selectbox("Driver de Escala Cartográfica:", ["Ninguno"] + nemo_reales)

        if activos:
            # RECUPERAMOS EL MOTOR DE LA v1.8.0
            query_list = activos + ([driver] if driver != "Ninguno" else [])
            res = supabase.table("precios_historicos").select("fecha, nemotecnico, precio_cierre")\
                .in_("nemotecnico", query_list).order("fecha", desc=False).execute()
            
            df_lab = pd.DataFrame(res.data)
            df_lab['fecha'] = pd.to_datetime(df_lab['fecha'])
            df_lab['precio_cierre'] = df_lab.groupby('nemotecnico')['precio_cierre'].ffill()
            df_pivot = df_lab.pivot(index='fecha', columns='nemotecnico', values='precio_cierre')

            # REINSTALACIÓN DE ESTADÍSTICOS (Perdidos en v1.8.6)
            st.markdown("### 📊 Métricas de Riesgo y Desempeño")
            returns = df_pivot[activos].pct_change().dropna()
            if not returns.empty:
                stats = pd.DataFrame({
                    "Varianza (Riesgo)": returns.var(),
                    "Volatilidad (Std Dev)": returns.std(),
                    "Retorno Total": (returns + 1).prod() - 1
                }).T
                st.dataframe(stats.style.format("{:.2%}"), use_container_width=True)

            # GRÁFICO CON RANGE SLIDER (Belleza v1.8.0)
            if driver != "Ninguno":
                df_rel = df_pivot[activos].div(df_pivot[driver], axis=0)
                fig = px.line(df_rel, title=f"Valor Relativo respecto a {driver}", template="plotly_dark")
            else:
                fig = px.line(df_pivot[activos], title="Evolución de Precios Nominales", template="plotly_dark")
            
            fig.update_layout(xaxis=dict(rangeslider=dict(visible=True), type="date"))
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("🔒 Ingrese credenciales para activar la Terminal IPSA-29.")
