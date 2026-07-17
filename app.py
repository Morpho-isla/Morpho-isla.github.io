import streamlit as st
import plotly.graph_objects as go
from db_utils import obtener_datos_accion, obtener_todos_los_nemotecnicos

# Configuración de la página
st.set_page_config(page_title="Dashboard Bolsa - Sinergia", layout="wide")

st.title("📈 Dashboard de Acciones: Mirada de Datos")
st.markdown("Visualización de series temporales con enfoque en **MASISA** y **ABC**.")

# Sidebar para controles
st.sidebar.header("Controles")
nemotecnico = st.sidebar.selectbox(
    "Selecciona un Nemotécnico:",
    obtener_todos_los_nemotecnicos()
)

# Botón rápido para los "protagonistas" del YTD
if st.sidebar.button("Ver MASISA (YTD -18%)"):
    nemotecnico = "MASISA"
if st.sidebar.button("Ver ABC (YTD -18%)"):
    nemotecnico = "ABC"

# Obtener datos
with st.spinner(f"Cargando datos de {nemotecnico}..."):
    df = obtener_datos_accion(nemotecnico)

if not df.empty:
    # Mostrar métricas clave
    col1, col2, col3 = st.columns(3)
    ultimo_cierre = df.iloc[-1]['precio_cierre']
    variacion = df.iloc[-1]['variacion']
    maximo_hist = df['precio_cierre'].max()
    
    col1.metric("Último Cierre", f"${ultimo_cierre:,.2f}")
    col2.metric("Variación Última", f"{variacion:.2f}%")
    col3.metric("Máximo Histórico (Periodo)", f"${maximo_hist:,.2f}")

    # Gráfico Principal con Plotly
    fig = go.Figure()

    # Línea de Precio
    fig.add_trace(go.Scatter(
        x=df['fecha'], 
        y=df['precio_cierre'], 
        mode='lines', 
        name='Precio Cierre',
        line=dict(color='#00CC96', width=3),
        fill='tozeroy', # Efecto de "sombra" bajo la línea
        fillcolor='rgba(0, 204, 150, 0.2)'
    ))

    # Puntos de Máximo y Mínimo (para ver la volatilidad)
    fig.add_trace(go.Scatter(
        x=df['fecha'], 
        y=df['precio_maximo'], 
        mode='markers', 
        name='Precio Máximo',
        marker=dict(color='orange', size=6),
        opacity=0.6
    ))

    fig.update_layout(
        title=f"Evolución de {nemotecnico} - Precio y Sombras",
        xaxis_title="Fecha",
        yaxis_title="Precio ($)",
        hovermode='x unified',
        template='plotly_dark', # Tema oscuro para combinar con la lluvia
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    # Mostrar tabla de datos recientes
    with st.expander("Ver datos detallados"):
        st.dataframe(df.sort_values(by='fecha', ascending=False).head(20))

else:
    st.warning(f"No se encontraron datos para {nemotecnico}.")

# Pie de página
st.markdown("---")
st.caption("Datos cargados desde Supabase | Desarrollado con Streamlit & Plotly")   
