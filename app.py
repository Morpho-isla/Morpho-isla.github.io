import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# 1. Configuración de Conexión (Información de fuera de las fuentes)
# Estos datos se configuran en los 'Secrets' de Streamlit/GitHub
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. Validación de Usuario (Simple Login para proteger tu propiedad intelectual)
def login():
    st.sidebar.title("Acceso Analista Senior")
    user = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

if login():
    st.title("📊 Dashboard Bursátil IPSA-29")
    
    # 3. Selector de Activos (Basado en la Regla IPSA-29 de la Guía Maestra)
    # Extraemos la lista única de nemotécnicos de tu base de datos
    nemo_list = ["MASISA", "LTM", "SQM-B", "CHILE", "BCI"] # Ejemplo, se carga dinámicamente
    selected_nemo = st.selectbox("Seleccione Nemotécnico para Análisis:", nemo_list)

    # 4. Consulta a la Vista de Precios Ajustados
    # Esta consulta evita los 'saltos' de las OSAs sumando los deltas históricos [1]
    query = supabase.table("vista_precios_ajustados")\
                    .select("*")\
                    .eq("nemotecnico", selected_nemo)\
                    .order("fecha", desc=False)\
                    .execute()
    
    df = pd.DataFrame(query.data)

    if not df.empty:
        # 5. Gráfico Continuo con Plotly
        st.subheader(f"Serie de Tiempo: {selected_nemo}")
        fig = px.line(df, x="fecha", y=["precio_mercado", "precio_ajustado"],
                      title=f"Evolución de Precio (Ajuste por Variaciones de Capital)",
                      labels={"value": "Precio (CLP)", "fecha": "Jornada Bursátil"})
        st.plotly_chart(fig, use_container_width=True)

        # 6. LA CAJA DE INSIGHTS (Captura de la columna 'comentario')
        # Aquí desplegamos los comentarios analíticos que cargamos en cada paso [1]
        st.info("💡 **Insight del Analista Senior para la fecha seleccionada:**")
        last_comment = df.iloc[-1]['comentario']
        st.write(last_comment if last_comment else "Sin observaciones técnicas registradas.")
    else:
        st.warning("No hay datos cargados para este activo.")

else:
    st.warning("Por favor, inicie sesión en la barra lateral para visualizar los datos estratégicos.")
    # --- SECCIÓN DE AUDITORÍA DE DATOS (IPSA-29) ---
st.markdown("---")
with st.expander("🔍 Ver Matriz Completa de Registros (Auditoría)"):
    st.write(f"Mostrando registros para el activo seleccionado en la serie histórica")
    # Mostramos el dataframe completo que ya descargamos en la app
    st.dataframe(df.sort_values(by="fecha", ascending=False), use_container_width=True)
    
    if st.button("Actualizar Vista de Auditoría"):
        st.rerun()
