import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. Configuración de Conexión
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def login():
    st.sidebar.title("🔐 Acceso Analista Senior")
    # Llaves únicas para evitar el error de ID duplicado visto en tus logs
    user = st.sidebar.text_input("Usuario", key="user_field")
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_field")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False


if login():
    st.title("📊 Dashboard Bursátil IPSA-29")
    
    # 1. Selector Múltiple para Correlación
    nemo_list = ["MASISA", "LTM", "CMPC", "VAPORES", "SQM-B", "CHILE", "BCI", "COPEC"]
    selected_nemos = st.multiselect("Seleccione Activos para Correlacionar:", nemo_list, default=["MASISA"])

    if selected_nemos:
        try:
            # Consulta masiva usando el operador 'in' de Supabase
            response = (
                supabase.table("precios_historicos")
                .select("fecha, nemotecnico, precio_cierre")
                .in_("nemotecnico", selected_nemos)
                .order("fecha", ascending=True)
                .execute()
            )
            
            df = pd.DataFrame(response.data)

            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'])
                
                # --- MOTOR DE NORMALIZACIÓN (BASE 100) ---
                # Esto permite comparar activos de distinto valor nominal
                df['base_100'] = df.groupby('nemotecnico')['precio_cierre'].transform(
                    lambda x: (x / x.iloc) * 100
                )

                # 2. Gráfico de Correlación Relativa
                fig = px.line(df, x='fecha', y='base_100', color='nemotecnico',
                             title="📈 Correlación de Rendimiento Relativo (Base 100)",
                             labels={'base_100': 'Rendimiento (%)', 'fecha': 'Fecha'})
                
                st.plotly_chart(fig, use_container_width=True)

                # 3. Matriz de Auditoría Consolidada
                with st.expander("🔍 Ver Datos Crudos de Correlación"):
                    st.dataframe(df.pivot(index='fecha', columns='nemotecnico', values='precio_cierre'))
            else:
                st.error("No se encontraron datos para los activos seleccionados.")
        except Exception as e:
            st.error(f"Error en el motor de correlación: {e}")
