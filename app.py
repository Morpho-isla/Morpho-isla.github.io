import streamlit as st
import pandas as pd
import plotly.express as px
import requests  # <--- NUEVO IMPORT AL PRINCIPIO
from supabase import create_client, Client

# 1. Configuración de Conexión (Protegida por Secrets)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. Función de Validación de Acceso
def login():
    st.sidebar.title("🔐 Acceso Analista Senior")
    user = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

# 3. Flujo Principal de la Aplicación
if login():
    st.title("📊 Dashboard Bursátil IPSA-29")
    st.markdown("---")
    # 2. Captura de la "Película" (Tiempo Real)
    drivers = fetch_realtime_drivers()
    if drivers:
        st.sidebar.markdown("### 🕒 Drivers en Tiempo Real")
        st.sidebar.metric("Dólar", f"${drivers['dolar']['value']}", f"{drivers['dolar']['variation']}%")
        st.sidebar.metric("UF", f"${drivers['uf']['value']}")
        # Agregamos el IPC para el análisis de inflación [3]
        st.sidebar.metric("IPC", f"{drivers['ipc']['value']}%")
    # Recuperación de datos desde la Vista de Precios Ajustados
    # Esto asegura que la Memoria Analítica (comentarios) fluya al Dashboard
    try:
        response = supabase.table("vista_precios_ajustados").select("*").execute()
        df = pd.DataFrame(response.data)
        
        if not df.empty:
            # Selector de Nemotécnico (Se actualizará dinámicamente según la carga)
            nemos = sorted(df['nemotecnico'].unique())
            selected_nemo = st.selectbox("Seleccione Nemotécnico para Análisis:", nemos)

            # Filtrado de datos para el gráfico
            df_filtered = df[df['nemotecnico'] == selected_nemo].sort_values(by="fecha")

            # --- SERIE DE TIEMPO ---
            st.subheader(f"Serie de Tiempo: {selected_nemo}")
            fig = px.line(df_filtered, x='fecha', y=['precio_mercado', 'precio_ajustado'],
                          title="Evolución de Precio (Ajuste por Variaciones de Capital)",
                          labels={'value': 'Precio (CLP)', 'fecha': 'Jornada Bursátil'})
            st.plotly_chart(fig, use_container_width=True)

            # --- MEMORIA ANALÍTICA (INSIGHTS) ---
            st.info("💡 Insight del Analista Senior para la última jornada:")
            last_comment = df_filtered.iloc[-1]['comentario']
            if pd.isna(last_comment) or last_comment == "":
                st.write("*Sin comentarios registrados para esta fecha.*")
            else:
                st.write(last_comment)

            # --- SECCIÓN DE AUDITORÍA DE DATOS (IPSA-29) ---
            st.markdown("---")
            with st.expander("🔍 Ver Matriz Completa de Registros (Auditoría)"):
                st.write("Mostrando registros históricos (Ordenados por fecha descendente)")
                # Aquí se soluciona el NameError al estar dentro del bloque df
                st.dataframe(df.sort_values(by="fecha", ascending=False), use_container_width=True)
        else:
            st.error("No se encontraron datos en la base de datos de Supabase.")

    except Exception as e:
        st.error(f"Error técnico en la conexión: {e}")

else:
    # Pantalla de bienvenida previa al login
    st.warning("Por favor, inicie sesión en la barra lateral para visualizar la matriz de datos estratégicos.")
    st.info("Sistema blindado bajo el Protocolo de Integridad IPSA-29.")
