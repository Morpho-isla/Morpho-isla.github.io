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
    
    # 2. SELECCIÓN DE ACTIVO
    # Incluimos los activos clave que mencionaste
    nemo_list = ["MASISA", "LTM", "CMPC", "VAPORES", "SQM-B", "CHILE", "BCI"]
    selected_nemo = st.selectbox("Seleccione Nemotécnico:", nemo_list)

    # 3. CONSULTA BLINDADA (Uso de paréntesis en lugar de \ para evitar el error en línea 35)
    response = (
        supabase.table("precios_historicos")
        .select("fecha, precio_cierre, variacion, precio_mayor, precio_menor, monto")
        .eq("nemotecnico", selected_nemo)
        .execute()
    )
    
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Normalización de fecha para el gráfico
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # 4. VISUALIZACIÓN GRÁFICA (Lo que ya ves en Supabase, ahora en la web)
        fig = px.line(df, x='fecha', y='precio_cierre', 
                     title=f"Evolución Histórica: {selected_nemo}",
                     labels={'precio_cierre': 'Precio ($)', 'fecha': 'Fecha'})
        st.plotly_chart(fig, use_container_width=True)

        # 5. MATRIZ DE AUDITORÍA (Sección depurada de logs anteriores)
        with st.expander("🔍 Ver Matriz de Datos (Detalle de Junio 2026)"):
            st.dataframe(df.sort_values(by="fecha", ascending=False))
    else:
        st.warning(f"No se encontraron registros para {selected_nemo} en la base de datos.")
