import streamlit as st
from supabase import create_client, Client
import pandas as pd

@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        supabase: Client = create_client(url, key)
        return supabase
    except Exception as e:
        st.error(f"❌ Error conectando a Supabase: {e}")
        return None

def obtener_datos_accion(nemotecnico, fecha_inicio=None, fecha_fin=None):
    supabase = init_connection()
    if supabase is None:
        return pd.DataFrame()
    
    try:
        query = supabase.table("precios_historicos").select("*").eq("nemotecnico", nemotecnico)
        
        if fecha_inicio:
            query = query.gte("fecha", fecha_inicio)
        if fecha_fin:
            query = query.lte("fecha", fecha_fin)
        
        response = query.order("fecha").execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            df['fecha'] = pd.to_datetime(df['fecha'])
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error obteniendo datos de {nemotecnico}: {e}")
        return pd.DataFrame()

def obtener_todos_los_nemotecnicos():
    supabase = init_connection()
    if supabase is None:
        return []
    try:
        response = supabase.table("precios_historicos").select("nemotecnico").limit(10000).execute()
        if response.data:
            df = pd.DataFrame(response.data)
            return sorted(df['nemotecnico'].unique().tolist())
        return []
    except Exception as e:
        st.error(f"❌ Error listando nemotécnicos: {e}")
        return []   
