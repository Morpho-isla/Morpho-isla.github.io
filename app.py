import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Conexión a la Fuente de Verdad
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)
# Asumimos la función login() ya definida
if login(): 
    st.title("🚀 Terminal IPSA-29: Inteligencia Avanzada")

    # --- ZARPAZO TÁCTICO: Obtener Nemos Reales de la DB ---
    res_nemos = supabase.table("precios_historicos").select("nemotecnico").execute()
    nemo_reales = sorted(list(set([d['nemotecnico'] for d in res_nemos.data])))

    # 2. Selectores de Activos y Drivers
    col1, col2 = st.columns(2)
    with col1:
        activos = st.multiselect("Seleccione Activos (Portafolio):", nemo_reales, default=nemo_reales[:2])
    with col2:
        # Aquí puedes elegir un activo para usarlo como "Denominador" o Driver (Cobre, Dólar, etc.)
        driver = st.selectbox("Seleccione Driver de Comparación (Opcional):", ["Ninguno"] + nemo_reales)

    if activos:
        try:
            # 3. Consulta Masiva
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

            # 4. MODULO ESTADÍSTICO (Varianza y Volatilidad)
            st.subheader("📊 Análisis de Riesgo y Varianza")
            df_pivot = df.pivot(index='fecha', columns='nemotecnico', values='precio_cierre')
            returns = df_pivot[activos].pct_change().dropna()
            
            if not returns.empty:
                stats = pd.DataFrame({
                    "Varianza": returns.var(),
                    "Volatilidad (Std)": returns.std(),
                    "Retorno Acum.": (returns + 1).prod() - 1
                })
                st.table(stats.style.format("{:.4%}"))

            # 5. VISUALIZACIÓN DE RATIOS (Tu concepto cartográfico)
            if driver != "Ninguno":
                st.subheader(f"🔗 Valor Relativo respecto a {driver}")
                base_series = df_pivot[driver]
                df_rel = df_pivot[activos].div(base_series, axis=0)
                fig_rel = px.line(df_rel, title=f"Precios expresados en unidades de {driver}", template="plotly_dark")
                st.plotly_chart(fig_rel, use_container_width=True)
            else:
                fig_nom = px.line(df_pivot[activos], title="Evolución de Precios Nominales", template="plotly_dark")
                st.plotly_chart(fig_nom, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error en el motor analítico: {e}")
