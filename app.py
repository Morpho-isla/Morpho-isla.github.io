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
    user = st.sidebar.text_input("Usuario", key="user_field")
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_field")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

if login():
    st.title("📊 Terminal IPSA-29: Comparativa")

    # 2. Selector Múltiple (Para graficar dos o más curvas)
    nemo_list = ["MASISA", "LTM", "CMPC", "VAPORES", "SQM-B", "CHILE", "BCI", "COPEC"]
    selected_nemos = st.multiselect("Seleccione Activos para el Gráfico:", nemo_list, default=["MASISA", "LTM"])

    # 3. Interruptor de Normalización
    normalizar = st.checkbox("Normalizar Rendimiento (Base 100)", value=False, 
                             help="Activa esto para comparar activos con precios muy diferentes (ej: Masisa vs CMPC)")

    if selected_nemos:
        try:
            # 4. Consulta Masiva a Supabase
            response = (
                supabase.table("precios_historicos")
                .select("fecha, nemotecnico, precio_cierre")
                .in_("nemotecnico", selected_nemos)
                .order("fecha", desc=False) # desc=False para orden cronológico
                .execute()
            )

            df = pd.DataFrame(response.data)

            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'])

                # Lógica Táctica de Visualización
                if normalizar:
                    # Se corrige el error usando .iloc para obtener el primer precio del mes
                    df['valor_grafico'] = df.groupby('nemotecnico')['precio_cierre'].transform(
                        lambda x: (x / x.iloc) * 100 if len(x) > 0 else 0
                    )
                    label_y = "Rendimiento (%)"
                    titulo = "📈 Comparativa de Rendimiento Relativo"
                else:
                    df['valor_grafico'] = df['precio_cierre']
                    label_y = "Precio de Cierre ($)"
                    titulo = "📈 Evolución de Precios Nominales"

                # 5. Gráfico Multi-Curva Estilo Búnker
                fig = px.line(df, x='fecha', y='valor_grafico', color='nemotecnico',
                             title=titulo,
                             labels={'valor_grafico': label_y, 'fecha': 'Fecha', 'nemotecnico': 'Activo'},
                             template="plotly_dark") # Fondo oscuro profesional
                
                st.plotly_chart(fig, use_container_width=True)

                # 6. Matriz de Auditoría Lado a Lado
                with st.expander("🔍 Ver Tabla de Datos"):
                    df_pivot = df.pivot(index='fecha', columns='nemotecnico', values='precio_cierre')
                    st.dataframe(df_pivot.sort_index(ascending=False))
            else:
                st.warning("No se encontraron registros para los activos seleccionados.")

        except Exception as e:
            st.error(f"❌ Error en el motor visual: {e}")
