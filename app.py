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
    st.title("📊 Terminal IPSA-29: Escala Cartográfica")

    nemo_list = ["MASISA", "LTM", "CMPC", "VAPORES", "SQM-B", "CHILE", "BCI", "COPEC"]
    selected_nemos = st.multiselect("Seleccione Activos:", nemo_list, default=["MASISA", "LTM"])

    # Interruptor para el modo de visualización
    modo_escala = st.radio("Modo de Visualización:", 
                           ["Precios Nominales", "Escala de Ratio (Cartográfica)"],
                           help="El activo más barato servirá como base 1.")

    if selected_nemos:
        try:
            response = (
                supabase.table("precios_historicos")
                .select("fecha, nemotecnico, precio_cierre")
                .in_("nemotecnico", selected_nemos)
                .order("fecha", desc=False)
                .execute()
            )

            df = pd.DataFrame(response.data)

            if not df.empty:
                df['fecha'] = pd.to_datetime(df['fecha'])
                
                # --- TRATAMIENTO DE DATOS FALTANTES (MASISA) ---
                # Rellenamos huecos con el último precio conocido para que la línea no desaparezca
                df = df.sort_values(['nemotecnico', 'fecha'])
                df['precio_cierre'] = df.groupby('nemotecnico')['precio_cierre'].ffill()

                if modo_escala == "Escala de Ratio (Cartográfica)":
                    # 1. Identificamos el activo con el precio promedio más bajo
                    avg_prices = df.groupby('nemotecnico')['precio_cierre'].mean()
                    base_nemo = avg_prices.idxmin()
                    
                    # 2. Creamos una serie base con los precios del activo más barato
                    base_series = df[df['nemotecnico'] == base_nemo].set_index('fecha')['precio_cierre']
                    
                    # 3. Aplicamos la división (Numerador: cada activo / Denominador: el base)
                    df['valor_grafico'] = df.apply(
                        lambda row: row['precio_cierre'] / base_series.get(row['fecha'], row['precio_cierre']), axis=1
                    )
                    label_y = f"Unidades de {base_nemo}"
                    titulo = f"📈 Escala Cartográfica: Activos expresados en valor de {base_nemo}"
                else:
                    df['valor_grafico'] = df['precio_cierre']
                    label_y = "Precio de Cierre ($)"
                    titulo = "📈 Evolución de Precios Nominales"

                # 4. Gráfico Multi-Curva
                fig = px.line(df, x='fecha', y='valor_grafico', color='nemotecnico',
                             title=titulo,
                             labels={'valor_grafico': label_y, 'fecha': 'Fecha'},
                             template="plotly_dark")
                
                st.plotly_chart(fig, use_container_width=True)

                with st.expander("🔍 Ver Tabla de Datos"):
                    st.dataframe(df.pivot(index='fecha', columns='nemotecnico', values='precio_cierre').sort_index(ascending=False))
            else:
                st.warning("No hay registros en Supabase.")

        except Exception as e:
            st.error(f"❌ Error en el motor de escala: {e}")
