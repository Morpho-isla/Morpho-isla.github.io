import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. Configuración de Conexión (vía Secrets)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def login():
    st.sidebar.title("🔐 Acceso Analista Senior")
    # Agregamos 'key' única para evitar el error de ID duplicado [9]
    user = st.sidebar.text_input("Usuario", key="user_input")
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_input")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

if login():
    st.title("📊 Dashboard Bursátil IPSA-29")
    
    # 2. CABECERA TÁCTICA (Datos estáticos por ahora o vía Boostr) [11]
    st.write("### 🚀 TACTICAL INTELLIGENCE | EN LÍNEA")
    
    # 3. FILTRO DE ACTIVOS (Basado en tu nueva carga SQL)
    # Lista de los 29 del IPSA + Masisa
    nemo_list = ["MASISA", "LTM", "CMPC", "VAPORES", "SQM-B", "CHILE", "BCI"] 
    selected_nemo = st.selectbox("Seleccione Nemotécnico:", nemo_list)

    # 4. CONSULTA A SUPABASE (Corregida con tus 10 campos)
    response = supabase.table("precios_historicos")\
        .select("fecha, precio_cierre, variacion, precio_mayor, precio_menor, monto")\
        .eq("nemotecnico", selected_nemo)\
        .order("fecha", ascending=True)\
        .execute()
    
    df = pd.DataFrame(response.data)

    if not df.empty:
        # CORRECCIÓN DE COLUMNAS: Aseguramos que 'variacion' sea la clave [7]
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        # Gráfico Maestro
        fig = px.line(df, x='fecha', y='precio_cierre', 
                     title=f"Serie Histórica: {selected_nemo}",
                     labels={'precio_cierre': 'Precio ($)', 'fecha': 'Fecha'})
        st.plotly_chart(fig, use_container_width=True)

        # Matriz de Auditoría (Sección que pediste depurar)
        with st.expander("🔍 Ver Matriz Completa (Auditoría Junio 2026)"):
            # Orden descendente para ver lo más reciente arriba [12]
            st.dataframe(df.sort_values(by="fecha", ascending=False))
    else:
        st.warning(f"No hay datos para {selected_nemo} en Supabase.")