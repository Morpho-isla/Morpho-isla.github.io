import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Inicializar cliente de Supabase usando los secrets
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    return supabase

def obtener_datos_accion(nemotecnico, fecha_inicio=None, fecha_fin=None):
    """
    Obtiene datos históricos de una acción específica desde Supabase.
    """
    supabase = init_connection()
    
    # Construir la consulta
    query = supabase.table("precios_historicos").select("*").eq("nemotecnico", nemotecnico)
    
    # Filtrar por fechas si se proporcionan
    if fecha_inicio:
        query = query.gte("fecha", fecha_inicio)
    if fecha_fin:
        query = query.lte("fecha", fecha_fin)
    
    # Ejecutar y ordenar por fecha
    response = query.order("fecha").execute()
    
    # Convertir a DataFrame de Pandas para fácil manejo en Streamlit/Plotly
    if response.data:
        df = pd.DataFrame(response.data)
        # Asegurar que la columna fecha sea datetime
        df['fecha'] = pd.to_datetime(df['fecha'])
        return df
    else:
        return pd.DataFrame()

def obtener_todos_los_nemotecnicos():
    """
    Obtiene una lista única de todos los nemotécnicos en la BD.
    """
    supabase = init_connection()
    # Truco: seleccionamos solo la columna nemotecnico y usamos distinct (si la API lo permite) 
    # o simplemente traemos una muestra y extraemos únicos.
    # Para simplificar, traemos una muestra grande y filtramos en Python:
    response = supabase.table("precios_historicos").select("nemotecnico").limit(10000).execute()
    
    if response.data:
        df = pd.DataFrame(response.data)
        return sorted(df['nemotecnico'].unique().tolist())
    return []   