
import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Configuración de Conexión
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def login():
    st.sidebar.title("🔐 Terminal de Alta Seguridad")
    user = st.sidebar.text_input("Usuario", key="user_login")
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_login")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

if login():
    st.title("🚀 Terminal IPSA-29: Inteligencia Institucional")
    
    # --- ZARPAZO AL LÍMITE: Usamos la nueva Vista para nemos ---
    # Esto traerá todos los activos (más allá de CFIBVCAP) sin saturar la memoria
    res_nemos = supabase.table("vista_nemos_unicos").select("*").execute()
    nemo_reales = [d['nemotecnico'] for d in res_nemos.data]

    # 3. SELECTORES CON ESTILO
    st.sidebar.markdown("### 🛠️ Configuración de Radar")
    activos = st.sidebar.multiselect("Portafolio a Monitorear:", nemo_reales, default=["MASISA", "LTM"] if "MASISA" in nemo_reales else nemo_reales[:2])
    driver = st.sidebar.selectbox("Driver de Escala (Numerador):", ["Ninguno"] + nemo_reales)

    if activos:
        try:
            # 4. CONSULTA MÁS EFICIENTE
            nemos_to_query = activos + ([driver] if driver != "Ninguno" else [])
            response = (
                supabase.table("precios_historicos")
                .select("fecha, nemotecnico, precio_cierre")
                .in_("nemotecnico", nemos_to_query)
                .order("fecha", desc=False)
                .execute()
            )

            df = pd.DataFrame(response.data)
            df['fecha'] = pd.to_datetime(df['fecha'])
            df['precio_cierre'] = df.groupby('nemotecnico')['precio_cierre'].ffill()
            df_pivot = df.pivot(index='fecha', columns='nemotecnico', values='precio_cierre')

            # 5. MATRIZ DE RIESGO (UI Mejorada)
            st.markdown("### 📊 Métricas de Desempeño y Riesgo")
            returns = df_pivot[activos].pct_change().dropna()
            
            if not returns.empty:
                stats = pd.DataFrame({
                    "Varianza (Riesgo)": returns.var(),
                    "Volatilidad (Std Dev)": returns.std(),
                    "Retorno Total Junio": (returns + 1).prod() - 1
                }).T
                st.dataframe(stats.style.format("{:.2%}"), use_container_width=True)

            # 6. GRÁFICO MAESTRO INTERACTIVO
            if driver != "Ninguno":
                st.subheader(f"🔗 Análisis de Valor Relativo: Unidades de {driver}")
                df_rel = df_pivot[activos].div(df_pivot[driver], axis=0)
                fig = px.line(df_rel, template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
            else:
                st.subheader("📈 Evolución de Precios Nominales")
                fig = px.line(df_pivot[activos], template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Safe)

            # AGREGANDO BELLEZA: Range Slider y Selectores de Tiempo
            fig.update_layout(
                xaxis=dict(rangeselector=dict(buttons=list([
                    dict(count=7, label="1s", step="day", stepmode="backward"),
                    dict(step="all", label="Mes Completo")
                ])), rangeslider=dict(visible=True), type="date"),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error en el motor de inteligencia: {e}")
