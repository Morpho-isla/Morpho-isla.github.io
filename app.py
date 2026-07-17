import streamlit as st
import plotly.graph_objects as go
from db_utils import obtener_datos_accion, obtener_todos_los_nemotecnicos

st.set_page_config(page_title="Dashboard Bolsa - Sinergia", layout="wide")

# Diagnóstico inicial
if "SUPABASE_URL" not in st.secrets:
    st.error("🚨 FALTAN LOS SECRETS: No se encuentra 'SUPABASE_URL' en la configuración de Streamlit.")
    st.stop()

st.title("📈 Dashboard de Acciones: Mirada de Datos")

# Sidebar
st.sidebar.header("Controles")
lista_nemos = obtener_todos_los_nemotecnicos()

if not lista_nemos:
    st.warning("⚠️ No se pudieron cargar los nemotécnicos. Revisa la conexión a Supabase.")
    st.stop()

nemotecnico = st.sidebar.selectbox("Selecciona un Nemotécnico:", lista_nemos)

# Botones rápidos
col1, col2 = st.sidebar.columns(2)
if col1.button("Ver MASISA"):
    nemotecnico = "MASISA"
if col2.button("Ver ABC"):
    nemotecnico = "ABC"

# Carga de datos
with st.spinner(f"Cargando datos de {nemotecnico}..."):
    df = obtener_datos_accion(nemotecnico)

if not df.empty:
    # ... (El resto de tu código de gráficos va aquí) ...
    st.success(f"✅ Datos cargados: {len(df)} registros encontrados.")
    # (Aquí insertas el código de Plotly que ya tenías)
else:
    st.warning(f"⚠️ No hay datos disponibles para {nemotecnico} en el rango seleccionado.")   
