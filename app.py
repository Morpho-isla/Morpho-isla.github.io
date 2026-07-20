import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Configuración de Conexión (Uso de Secrets) [1, 2]
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. DEFINICIÓN DE LOGIN (Debe ir antes del llamado) [2]
def login():
    st.sidebar.title("🔐 Acceso Analista Senior")
    # Usamos 'key' única para evitar errores de DuplicateWidgetID vistos en logs [3]
    user = st.sidebar.text_input("Usuario", key="user_login")
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_login")
    
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

# 3. EJECUCIÓN DEL DASHBOARD
if login():
    st.title("🚀 Terminal IPSA-29: Inteligencia Avanzada")

    # --- ZARPAZO TÁCTICO: Obtener Nemos Reales de la DB ---
    # Esto soluciona el problema de los activos que no cargaban por tener el marcador '(I)' [Conversación previa]
    res_nemos = supabase.table("precios_historicos").select("nemotecnico").execute()
    nemo_reales = sorted(list(set([d['nemotecnico'] for d in res_nemos.data])))

    # 4. Selectores de Activos y Drivers
    col1, col2 = st.columns(2)
    with col1:
        activos = st.multiselect("Seleccione Activos (Portafolio):", nemo_reales, default=["MASISA", "LTM"] if "MASISA" in nemo_reales else nemo_reales[:2])
    with col2:
        driver = st.selectbox("Seleccione Driver de Comparación (Escala Cartográfica):", ["Ninguno"] + nemo_reales)

    if activos:
        try:
            # 5. Consulta Masiva a Supabase
            nemos_to_query = activos + ([driver] if driver != "Ninguno" else [])
            response = (
                supabase.table("precios_historicos")
                .select("fecha, nemotecnico, precio_cierre")
                .in_("nemotecnico", nemos_to_query)
                .order("fecha", desc=False) # desc=False para orden cronológico [Conversación previa]
                .execute()
            )

            df = pd.DataFrame(response.data)
            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'])
                # Rellenamos huecos (ffill) para que Masisa no "pestañee" si falta un cierre [Conversación previa]
                df['precio_cierre'] = df.groupby('nemotecnico')['precio_cierre'].ffill()
                df_pivot = df.pivot(index='fecha', columns='nemotecnico', values='precio_cierre')

                # 6. MODULO ESTADÍSTICO (Varianza y Volatilidad)
                st.subheader("📊 Análisis de Riesgo y Varianza")
                returns = df_pivot[activos].pct_change().dropna()
                
                if not returns.empty:
                    stats = pd.DataFrame({
                        "Varianza": returns.var(),
                        "Volatilidad (Std)": returns.std(),
                        "Retorno Acum.": (returns + 1).prod() - 1
                    })
                    st.table(stats.style.format("{:.4%}"))

                # 7. VISUALIZACIÓN DE RATIOS (Concepto cartográfico)
                if driver != "Ninguno":
                    st.subheader(f"🔗 Valor Relativo respecto a {driver}")
                    base_series = df_pivot[driver]
                    df_rel = df_pivot[activos].div(base_series, axis=0)
                    fig_rel = px.line(df_rel, title=f"Precios expresados en unidades de {driver}", template="plotly_dark")
                    st.plotly_chart(fig_rel, use_container_width=True)
                else:
                    fig_nom = px.line(df_pivot[activos], title="Evolución de Precios Nominales", template="plotly_dark")
                    st.plotly_chart(fig_nom, use_container_width=True)
            else:
                st.warning("No se encontraron datos para los activos seleccionados.")
        except Exception as e:
            st.error(f"❌ Error en el motor analítico: {e}")
else:
    st.info("🔒 Por favor, ingrese sus credenciales en la barra lateral para activar la terminal.")
