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
        # 1. Traemos los datos con un filtro más amplio (ilike ignora mayúsculas/minúsculas)
        # O traemos todo y filtramos en Python para mayor seguridad
        response = supabase.table("precios_historicos").select("*").execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # 2. Limpieza en Python: Eliminamos espacios en blanco de la columna nemotecnico
            df['nemotecnico'] = df['nemotecnico'].astype(str).str.strip().str.upper()
            
            # 3. Filtramos ahora sí, asegurando coincidencia exacta tras la limpieza
            df_filtrado = df[df['nemotecnico'] == nemotecnico.upper()]
            
            if df_filtrado.empty:
                return pd.DataFrame()
            
            # 4. Convertimos fechas y números
            df_filtrado['fecha'] = pd.to_datetime(df_filtrado['fecha'])
            df_filtrado['precio_cierre'] = pd.to_numeric(df_filtrado['precio_cierre'], errors='coerce')
            
            return df_filtrado
            
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
                
                # Obtener datos
                df = get_stock_data(target)
                
                # --- DEPURACIÓN: VER QUÉ HAY EN DF ---
                st.info(f"🔍 Depuración: Se encontraron {len(df)} registros crudos.")
                if not df.empty:
                    st.write("Primeras filas del DataFrame (antes de filtrar):")
                    st.write(df[['nemotecnico', 'fecha', 'precio_cierre']].head()) # Mostramos solo columnas clave
                    
                    # Mostramos cómo se ve el nemotécnico limpio vs sucio
                    st.write(f"Valor buscado: '{target}' | Valores únicos en BD: {df['nemotecnico'].unique()}")
                # -------------------------------------

                if not df.empty:
                    st.success(f"✅ {len(df)} registros cargados y limpios.")
                    # ... (resto del código del gráfico) ...
                else:
                    st.warning(f"⚠️ Sin datos para {target} en Supabase tras el filtrado.")               
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
