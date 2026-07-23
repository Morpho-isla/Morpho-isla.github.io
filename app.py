import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from supabase import create_client, Client
from datetime import datetime

# 1. CONFIGURACIÓN DE ALTO NIVEL
st.set_page_config(layout="wide", page_title="Terminal IPSA-29 v2.0")
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# 2. SISTEMA DE ACCESO (Login persistente)
def login():
    st.sidebar.title("🔐 Acceso Analista Senior")
    user = st.sidebar.text_input("Usuario", key="user_login")
    password = st.sidebar.text_input("Contraseña", type="password", key="pass_login")
    if user == st.secrets["APP_USER"] and password == st.secrets["APP_PASSWORD"]:
        return True
    return False

# 1. ACTUALIZACIÓN DE LA FUNCIÓN DE DRIVERS
def get_and_save_drivers():
    try:
        url_boostr = "https://api.boostr.cl/economy/indicators.json"
        response = requests.get(url_boostr)
        data = response.json()['data']
        
        usd_val = data['dolar']['value']
        fecha_hoy = datetime.now().strftime('%Y-%m-%d')

        # ZARPAZO: Especificamos 'on_conflict' para evitar el error 23505
        # Esto permite actualizar el valor si ya existe para esa fecha
        supabase.table("drivers_historicos").upsert(
            {"fecha": fecha_hoy, "driver_nemo": "USD_OBS", "valor": usd_val},
            on_conflict="fecha, driver_nemo" 
        ).execute()
        
        return data
    except Exception as e:
        # Si hay un error de llave duplicada, igual devolvemos los datos para que la web funcione
        return data if 'data' in locals() else None

# 2. BLOQUE PRINCIPAL (Verifica la indentación)
if login():
    # 1. CARGA DE DRIVERS (Macro)
    drivers_data = get_and_save_drivers()
    
    # 2. CARGA DE NEMOTÉCNICOS (IPSA-29) - Blindado e independiente
    try:
        res_nemos = supabase.table("vista_nemos_unicos").select("*").execute()
        nemo_reales = [d['nemotecnico'] for d in res_nemos.data] if res_nemos.data else []
    except Exception as e:
        st.error(f"Error cargando activos del IPSA: {e}")
        nemo_reales = ["MASISA", "SQM-B", "LTM"] # Fallback de emergencia
    
    # --- CABECERA ESTRATÉGICA: BLINDAJE DE SEGUNDO GRADO ---
    if drivers_data:
        c1, c2, c3, c4 = st.columns(4)
        
        # 1. DÓLAR: Si la clave existe pero es None, 'or {}' lo convierte en dict vacío
        usd = drivers_data.get('dolar') or {} 
        usd_val = usd.get('value', 'N/A')
        usd_var = usd.get('variation', '0.00')
        c1.metric("💵 Dólar Obs.", f"${usd_val}", f"{usd_var}%")
        
        # 2. UF: Aplicamos la misma lógica de seguridad
        uf = drivers_data.get('uf') or {}
        uf_val = uf.get('value', 0)
        c2.metric("🏠 UF Hoy", f"${uf_val:,.2f}")
        
        # 3. PETRÓLEO WTI: Ya vimos en la Captura menu1 que este puede fallar
        wti = drivers_data.get('wti') or {}
        wti_val = wti.get('value', 'N/A')
        wti_var = wti.get('variation', '0.00')
        c3.metric("Petróleo WTI", f"US$ {wti_val}", f"{wti_var}%")
        
        # 4. IPC
        ipc = drivers_data.get('ipc') or {}
        ipc_val = ipc.get('value', 'N/A')
        c4.metric("📈 IPC", f"{ipc_val}%", "Mensual")        
    # El resto del menú sigue aquí abajo (todo indentado)
    st.sidebar.markdown("---")
    # ... resto del código ...
    menu = st.sidebar.radio("📋 MENÚ DE COMANDO", 
                            ["🚨 Radar de Verdad", "🧪 Laboratorio (Masisa/SQM-B)", "📡 Monitor de Drivers"])

    if menu == "🚨 Radar de Verdad":
        st.title("🚀 Radar de Contingencia y Verdad")
        # Aquí recuperamos tu "Polígrafo" de integridad [17, Conversación previa]
        audit_nemos = ["LTM", "MASISA", "CHILE (I)", "CMPC (I)", "SQM-B"]
        res_audit = supabase.table("precios_historicos").select("nemotecnico, precio_cierre, variacion, fecha")\
            .in_("nemotecnico", audit_nemos).order("fecha", desc=True).limit(50).execute()
        
        if res_audit.data:
            st.subheader("🛠️ Auditoría de Cierres Oficiales")
            df_audit = pd.DataFrame(res_audit.data).drop_duplicates(subset=['nemotecnico'])
            st.dataframe(df_audit.style.format({"precio_cierre": "$ {:,.2f}", "variacion": "{:,.2f}%"}), use_container_width=True)


    elif menu == "🧪 Laboratorio (Masisa/SQM-B)":
        st.title("🧪 Laboratorio de Correlación Macro")
        
        # 1. CARGA DE COMBUSTIBLE (Nemos y Drivers)
        res_nemos = supabase.table("vista_nemos_unicos").select("nemotecnico").execute()
        nemo_reales = [d['nemotecnico'] for d in res_nemos.data]
        
        res_drivers = supabase.table("drivers_historicos").select("driver_nemo").execute()
        drivers_list = list(set([d['driver_nemo'] for d in res_drivers.data]))

        col1, col2 = st.columns(2)
        with col1:
            activo_foco = st.selectbox("Activo Principal:", nemo_reales, index=nemo_reales.index("SQM-B") if "SQM-B" in nemo_reales else 0)
        with col2:
            tipo_analisis = st.radio("Tipo de Comparativa:", ["Escala Cartográfica (Ratio)", "Correlación Macro (Driver)"])

        # 2. SELECTOR DINÁMICO
        if tipo_analisis == "Escala Cartográfica (Ratio)":
            denominador = st.selectbox("Dividido por (Denominador):", ["Ninguno"] + nemo_reales, index=1 if "MASISA" in nemo_reales else 0)
        else:
            denominador = st.selectbox("Driver de Referencia:", drivers_list, index=drivers_list.index("WTI") if "WTI" in drivers_list else 0)

        # 3. PROCESAMIENTO DEL OSCILOSCOPIO
        if denominador != "Ninguno":
            # Obtener Precios
            res_p = supabase.table("precios_historicos").select("fecha, precio_cierre").eq("nemotecnico", activo_foco).order("fecha").execute()
            df_p = pd.DataFrame(res_p.data).set_index('fecha')

            if tipo_analisis == "Escala Cartográfica (Ratio)":
                res_d = supabase.table("precios_historicos").select("fecha, precio_cierre").eq("nemotecnico", denominador).order("fecha").execute()
                label_y2 = f"Ratio {activo_foco}/{denominador}"
            else:
                res_d = supabase.table("drivers_historicos").select("fecha, valor").eq("driver_nemo", denominador).order("fecha").execute()
                label_y2 = f"Valor {denominador} (US$)"
            
            df_d = pd.DataFrame(res_d.data).set_index('fecha')
            
            # Unir y graficar
            df_final = df_p.join(df_d, how='inner', lsuffix='_p', rsuffix='_d').ffill()
            
            if not df_final.empty:
                import plotly.graph_objects as go
                from plotly.subplots import make_subplots

                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                # Eje Y1: El Activo (SQM-B)
                fig.add_trace(go.Scatter(x=df_final.index, y=df_final.iloc[:, 0], name=f"Precio {activo_foco} ($)", line=dict(color='orange', width=3)), secondary_y=False)
                
                # Eje Y2: El Driver o el Ratio
                y2_values = (df_final.iloc[:, 0] / df_final.iloc[:, 1]) if tipo_analisis == "Escala Cartográfica (Ratio)" else df_final.iloc[:, 1]
                fig.add_trace(go.Scatter(x=df_final.index, y=y2_values, name=label_y2, line=dict(color='cyan', dash='dash')), secondary_y=True)

                fig.update_layout(title=f"Auditoría: {activo_foco} vs {denominador}", template="plotly_dark", hovermode="x unified")
                fig.update_yaxes(title_text="<b>Precio Activo</b> ($)", secondary_y=False)
                fig.update_yaxes(title_text=f"<b>{label_y2}</b>", secondary_y=True)
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"Esperando datos de {denominador} o SQM-B para calcular la brecha...")
    elif menu == "📡 Monitor de Drivers":
        st.title("📡 Radar de Indicadores Adelantados")
        # Aquí consultamos la nueva tabla de drivers
        res_drivers = supabase.table("drivers_historicos").select("*").order("fecha", desc=True).limit(10).execute()
        st.write("### Historial de Drivers (Captura Autónoma)")
        st.table(pd.DataFrame(res_drivers.data))

else:
    st.info("🔒 Ingrese credenciales para activar la Terminal IPSA-29 v2.0.")
