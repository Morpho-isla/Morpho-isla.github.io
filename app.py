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
            # 1. CONSULTA A SUPABASE (Usando desc=False para evitar error previo)
            response = (
                supabase.table("precios_historicos")
                .select("fecha, nemotecnico, precio_cierre")
                .in_("nemotecnico", selected_nemos)
                .order("fecha", desc=False) # Parámetro correcto para v2.31.0
                .execute()
            )
            
            df = pd.DataFrame(response.data)

            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'])
                
                # 2. MOTOR DE NORMALIZACIÓN (BASE 100)
                # Calculamos el rendimiento relativo para comparar activos de distinto valor
                df['base_100'] = df.groupby('nemotecnico')['precio_cierre'].transform(
                    lambda x: (x / x.iloc) * 100 if not x.empty else 0
                )

                # 3. VISUALIZACIÓN ELEGANTE (ESTILO BÚNKER)
                fig = px.line(df, x='fecha', y='base_100', color='nemotecnico',
                             title="📈 Correlación de Rendimiento Relativo (Base 100)",
                             labels={'base_100': 'Rendimiento (%)', 'fecha': 'Fecha'},
                             template="plotly_dark") # Fondo oscuro para resaltar las líneas
                
                st.plotly_chart(fig, use_container_width=True)

                # 4. MATRIZ DE AUDITORÍA CONSOLIDADA
                with st.expander("🔍 Ver Datos Crudos de Correlación"):
                    # Pivoteamos la tabla para ver los precios lado a lado
                    df_pivot = df.pivot(index='fecha', columns='nemotecnico', values='precio_cierre')
                    st.dataframe(df_pivot.sort_index(ascending=False))
            else:
                # Línea 62: Ahora está dentro de una estructura try-except completa
                st.error("No se encontraron datos para los activos seleccionados en Supabase.")
        
        except Exception as e:
            # ESTE ES EL BLOQUE QUE Python reclama: el cierre del try
            st.error(f"❌ Error en el motor de correlación: {e}")
