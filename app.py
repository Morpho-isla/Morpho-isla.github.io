import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. Conexión Blindada
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def login():
    st.sidebar.title("🔐 Acceso Analista Senior")
    user = st.sidebar.text_input("Usuario", key="user_login")
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_login")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

if login():
    st.title("🚀 Terminal IPSA-29: Inteligencia Institucional")
    
    # --- BLOQUE 1: RADAR DE EMERGENCIA (Independiente) ---
    st.sidebar.markdown("---")
    radar_activo = st.sidebar.checkbox("🚀 Activar Radar de Emergencia BCS")
    
    if radar_activo:
        st.subheader("⚠️ Monitor de Variación Real (Sin CFI)")
        
        # Obtenemos la última sesión para calcular deltas
        last_data = supabase.table("precios_historicos")\
            .select("nemotecnico, precio_cierre, variacion, fecha")\
            .order("fecha", desc=True).limit(500).execute()
        
        df_emergency = pd.DataFrame(last_data.data)
        
        if not df_emergency.empty:
            # FILTRO CRÍTICO: Eliminamos índices y fondos (CFI) para ver solo acciones [1]
            indices = ['IPSA', 'IGPA', 'SPIPSA', 'SPCLX']
            df_acciones = df_emergency[
                (~df_emergency['nemotecnico'].str.contains('CFI', na=False)) & 
                (~df_emergency['nemotecnico'].isin(indices))
            ].copy()

            # TABLA DE INTEGRIDAD (Corregida: busca nemos reales)
            with st.expander("🛠️ Auditoría de Integridad (LTM, Chile, BCI)"):
                audit_nemos = ["LTM", "MASISA", "CHILE (I)", "CMPC (I)", "VAPORES (I)"]
                df_audit = df_acciones[df_acciones['nemotecnico'].isin(audit_nemos)].copy()
                if not df_audit.empty:
                    st.dataframe(df_audit[['nemotecnico', 'precio_cierre', 'variacion']].style.format({
                        "precio_cierre": "$ {:,.2f}",
                        "variacion": "{:,.2f}%"
                    }))
                else:
                    st.warning("No se detectaron los nemos de auditoría en la última carga.")

            # TOP 10 ALZAS Y BAJAS (Formato Moneda)
            col_up, col_down = st.columns(2)
            with col_up:
                st.success("📈 Top 10 Alzas (Acciones)")
                st.dataframe(df_acciones.nlargest(10, 'variacion')[['nemotecnico', 'precio_cierre', 'variacion']]\
                             .style.format({"precio_cierre": "$ {:,.2f}", "variacion": "{:,.2f}%"}))
            with col_down:
                st.error("📉 Top 10 Bajas (Acciones)")
                st.dataframe(df_acciones.nsmallest(10, 'variacion')[['nemotecnico', 'precio_cierre', 'variacion']]\
                             .style.format({"precio_cierre": "$ {:,.2f}", "variacion": "{:,.2f}%"}))
        st.markdown("---")

    # --- BLOQUE 2: DASHBOARD PRINCIPAL (Fuera del if del radar) ---
    # Este bloque siempre se verá, arreglando el problema de la página en blanco
    st.subheader("📊 Visualizador Táctico")
    
    res_nemos = supabase.table("vista_nemos_unicos").select("*").execute()
    nemo_reales = [d['nemotecnico'] for d in res_nemos.data]
    
    activos = st.multiselect("Radar de Portafolio:", nemo_reales, default=["MASISA", "LTM"])
    
    if activos:
        # (Aquí sigue tu lógica de gráficos v1.8.0...)
        response = supabase.table("precios_historicos").select("fecha, nemotecnico, precio_cierre")\
            .in_("nemotecnico", activos).order("fecha", desc=False).execute()
        df_plot = pd.DataFrame(response.data)
        if not df_plot.empty:
            fig = px.line(df_plot, x='fecha', y='precio_cierre', color='nemotecnico', template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

else:
    st.info("🔒 Ingrese credenciales para activar el búnker.")
