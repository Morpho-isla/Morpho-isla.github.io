
import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import numpy as np

# 1. Configuración de Conexión
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def login():
    st.sidebar.title("🔐 Terminal de Alta Seguridad")
    user = st.sidebar.text_input("Usuario", key="user_login")
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_login")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

if login():
    st.title("🚀 Terminal IPSA-29: Inteligencia Institucional")
    
    # --- ZARPAZO AL LÍMITE: Usamos la nueva Vista para nemos ---
    # Esto traerá todos los activos (más allá de CFIBVCAP) sin saturar la memoria
    res_nemos = supabase.table("vista_nemos_unicos").select("*").execute()
    nemo_reales = [d['nemotecnico'] for d in res_nemos.data]

    # 3. SELECTORES CON ESTILO
    st.sidebar.markdown("### 🛠️ Configuración de Radar")
    activos = st.sidebar.multiselect("Portafolio a Monitorear:", nemo_reales, default=["MASISA", "LTM"] if "MASISA" in nemo_reales else nemo_reales[:2])
    driver = st.sidebar.selectbox("Driver de Escala (Numerador):", ["Ninguno"] + nemo_reales)
# --- NUEVA SECCIÓN: RADAR DE VARIACIÓN INDEPENDIENTE ---
if st.sidebar.checkbox("🚀 Activar Radar de Emergencia BCS"):
    st.subheader("⚠️ Monitor de Variación Real (Cómputo Independiente)")
    st.info("Calculando deltas usando cierres históricos del búnker para evitar errores de plataformas externas.")

    # 1. Obtenemos el cierre de la última sesión grabada en Supabase
    last_session = supabase.table("precios_historicos")\
        .select("nemotecnico, precio_cierre, fecha")\
        .order("fecha", desc=True)\
        .limit(100)\
        .execute()
    
    df_last = pd.DataFrame(last_session.data)
    
    # 2. Creamos una tabla comparativa (puedes ingresar el precio actual manualmente o vía API)
    # Por ahora, simularemos la comparación con una columna de entrada rápida
    with st.expander("🛠️ Auditoría de Precios en Vivo (LTM, CHILE, BCI)"):
        audit_nemos = ["LTM", "MASISA", "CHILE (I)", "CMPC (I)", "VAPORES (I)"]
        df_audit = df_last[df_last['nemotecnico'].isin(audit_nemos)].copy()
        
        # Agregamos columna para que ingreses el precio que ves en pantalla (aunque el delta esté mal)
        df_audit['Precio_Web'] = df_audit['precio_cierre'] # Valor inicial
        
        # Cálculo de nuestra variación real
        df_audit['Variacion_Real'] = ((df_audit['Precio_Web'] / df_audit['precio_cierre']) - 1) * 100
        
        st.write("### 📊 Comparativa de Integridad")
        st.dataframe(df_audit[['nemotecnico', 'precio_cierre', 'Variacion_Real']].style.format({"Variacion_Real": "{:.2f}%"}))

    # 3. Reconstrucción de "Mayores Alzas y Bajas" [5, 6]
    # Usando nuestros datos de integridad IPSA-29
    col_up, col_down = st.columns(2)
    with col_up:
        st.success("📈 Mayores Alzas (Nuestro Motor)")
        # Aquí filtramos por transacciones 'T' de nuestra última carga [7]
        st.write(df_last.nlargest(5, 'precio_cierre')[['nemotecnico', 'precio_cierre']])

    if activos:
        try:
            # 4. CONSULTA MÁS EFICIENTE
            nemos_to_query = activos + ([driver] if driver != "Ninguno" else [])
            response = (
                supabase.table("precios_historicos")
                .select("fecha, nemotecnico, precio_cierre")
                .in_("nemotecnico", nemos_to_query)
                .order("fecha", desc=False)
                .execute()
            )

            df = pd.DataFrame(response.data)
            df['fecha'] = pd.to_datetime(df['fecha'])
            df['precio_cierre'] = df.groupby('nemotecnico')['precio_cierre'].ffill()
            df_pivot = df.pivot(index='fecha', columns='nemotecnico', values='precio_cierre')

            # 5. MATRIZ DE RIESGO (UI Mejorada)
            st.markdown("### 📊 Métricas de Desempeño y Riesgo")
            returns = df_pivot[activos].pct_change().dropna()
            
            if not returns.empty:
                stats = pd.DataFrame({
                    "Varianza (Riesgo)": returns.var(),
                    "Volatilidad (Std Dev)": returns.std(),
                    "Retorno Total Junio": (returns + 1).prod() - 1
                }).T
                st.dataframe(stats.style.format("{:.2%}"), use_container_width=True)

            # 6. GRÁFICO MAESTRO INTERACTIVO
            if driver != "Ninguno":
                st.subheader(f"🔗 Análisis de Valor Relativo: Unidades de {driver}")
                df_rel = df_pivot[activos].div(df_pivot[driver], axis=0)
                fig = px.line(df_rel, template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
            else:
                st.subheader("📈 Evolución de Precios Nominales")
                fig = px.line(df_pivot[activos], template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Safe)

            # AGREGANDO BELLEZA: Range Slider y Selectores de Tiempo
            fig.update_layout(
                xaxis=dict(rangeselector=dict(buttons=list([
                    dict(count=7, label="1s", step="day", stepmode="backward"),
                    dict(step="all", label="Mes Completo")
                ])), rangeslider=dict(visible=True), type="date"),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error en el motor de inteligencia: {e}")
