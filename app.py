import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Dashboard de Dotación Autosol",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Personalizados para lucir premium
st.markdown("""
<style>
    /* Fondo principal y textos */
    .stApp {
        background-color: #f4f6f9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Métrica cards */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 800;
        color: #002D62;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        font-weight: 600;
        color: #6c757d;
    }
    
    /* Headers de la página */
    h1 {
        color: #002D62;
        font-weight: 800;
        padding-bottom: 0px;
    }
    h2, h3 {
        color: #343a40;
        font-weight: 600;
    }
    
    /* Remueve margenes extra */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# URL de datos
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR7Ila8tzO3SEBZ5-faEFW-9VZY8eiPCUV3vPhryrlyqsmovw76hKqVRc-y18rTmz0NugYIUv6JTxRH/pub?output=csv"

@st.cache_data(ttl=3600)  # Refrescar cada 1 hora
def load_data():
    try:
        # Cargar CSV
        df = pd.read_csv(CSV_URL)
        
        # Limpieza básica
        df = df.dropna(subset=['Nombre y Apellido', 'Área', 'Fecha de Ingreso'])
        
        # Parseo de fechas (DD/MM/YYYY o similar)
        # Se asume formato compatible de Argentina
        df['Fecha de Ingreso'] = pd.to_datetime(df['Fecha de Ingreso'], errors='coerce', dayfirst=True)
        df['Fecha de Nacimiento'] = pd.to_datetime(df['Fecha de Nacimiento'], errors='coerce', dayfirst=True)
        
        # Cálculos de Edad y Antigüedad
        now = pd.Timestamp.now()
        df['Edad'] = (now - df['Fecha de Nacimiento']).dt.days / 365.25
        df['Antigüedad (Años)'] = (now - df['Fecha de Ingreso']).dt.days / 365.25
        
        # Rellenar nulos categóricos comunes
        df['Estado'] = df['Estado'].fillna('Desconocido')
        df['Localidad'] = df['Localidad'].fillna('Sin especificar')
        df['Sexo'] = df['Sexo'].fillna('Sin Especificar')
        df['Categoría'] = df.get('Categoría', pd.Series(['Sin Definir']*len(df))).fillna('Sin Definir')
        
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

# Cargar los datos
df_raw = load_data()

if df_raw.empty:
    st.warning("No se encontraron datos o hubo un error al leer la fuente. Revisa el link de Google Sheets.")
    st.stop()

# ----------------------------------------------------
# COMPONENTES DEL SIDEBAR (Filtros)
# ----------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100) # Logo placeholder
st.sidebar.title("Filtros de Dashboard")

# Selector de Estado
estados_disponibles = ["Todos"] + list(df_raw['Estado'].dropna().unique())
estado_seleccionado = st.sidebar.selectbox("Estado", estados_disponibles, index=estados_disponibles.index("Activo") if "Activo" in estados_disponibles else 0)

# Aplicar filtro estado temporalmente para obtener el resto de filtros relevantes
df_filtered = df_raw.copy()
if estado_seleccionado != "Todos":
    df_filtered = df_filtered[df_filtered['Estado'] == estado_seleccionado]

# Selector de Localidad
loc_disponibles = ["Todas"] + list(df_filtered['Localidad'].dropna().unique())
loc_seleccionada = st.sidebar.selectbox("Localidad", loc_disponibles)

# Selector de Área
area_disponibles = ["Todas"] + list(df_filtered['Área'].dropna().unique())
area_seleccionada = st.sidebar.selectbox("Área", area_disponibles)

# Selector de Sexo
sexo_disponibles = ["Todos"] + list(df_filtered['Sexo'].dropna().unique())
sexo_seleccionado = st.sidebar.selectbox("Sexo", sexo_disponibles)

# Aplicar todos los filtros
if loc_seleccionada != "Todas":
    df_filtered = df_filtered[df_filtered['Localidad'] == loc_seleccionada]
if area_seleccionada != "Todas":
    df_filtered = df_filtered[df_filtered['Área'] == area_seleccionada]
if sexo_seleccionado != "Todos":
    df_filtered = df_filtered[df_filtered['Sexo'] == sexo_seleccionado]

# ----------------------------------------------------
# MAIN DASHBOARD CONTENT
# ----------------------------------------------------
col_title, col_date = st.columns([3, 1])
with col_title:
    st.title("Dashboard Ejecutivo de Dotación")
with col_date:
    st.markdown(f"<div style='text-align: right; color: gray; padding-top: 25px;'>Última actualización<br><b>{datetime.now().strftime('%d/%m/%Y')}</b></div>", unsafe_allow_html=True)

st.markdown("---")

# 1. Row de KPIs Superiores
if not df_filtered.empty:
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    # KPI 1: Cantidad de Empleados (Dotación)
    total_dotacion = len(df_filtered)
    kpi1.metric("Dotación Total", f"{total_dotacion}")
    
    # KPI 2: Edad Promedio
    edad_promedio = df_filtered['Edad'].mean()
    kpi2.metric("Edad Promedio", f"{edad_promedio:.1f} años" if pd.notnull(edad_promedio) else "N/A")
    
    # KPI 3: Antigüedad Promedio
    ant_promedio = df_filtered['Antigüedad (Años)'].mean()
    kpi3.metric("Antigüedad Prom.", f"{ant_promedio:.1f} años" if pd.notnull(ant_promedio) else "N/A")
    
    # KPI 4: Ratio Género (Mujeres)
    if 'Femenino' in df_filtered['Sexo'].values:
        femenino_pct = (len(df_filtered[df_filtered['Sexo'] == 'Femenino']) / total_dotacion) * 100
        kpi4.metric("% Mujeres", f"{femenino_pct:.1f}%")
    else:
        kpi4.metric("% Mujeres", "0.0%")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Row de Gráficos (Histórico vs Demografía)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Histórico de Ingresos Acumulados")
        # Procesar datos históricos: Agrupar por Mes/Año de Ingreso
        df_hist = df_filtered.dropna(subset=['Fecha de Ingreso']).copy()
        if not df_hist.empty:
            df_hist['AÑO_MES'] = df_hist['Fecha de Ingreso'].dt.to_period('M')
            hist_counts = df_hist.groupby('AÑO_MES').size().reset_index(name='Ingresos')
            hist_counts['AÑO_MES'] = hist_counts['AÑO_MES'].dt.to_timestamp()
            hist_counts = hist_counts.sort_values('AÑO_MES')
            hist_counts['Dotación Acumulada'] = hist_counts['Ingresos'].cumsum()
            
            fig_hist = px.area(hist_counts, x='AÑO_MES', y='Dotación Acumulada', 
                               color_discrete_sequence=['#0056b3'])
            fig_hist.update_layout(xaxis_title="", yaxis_title="Empleados", margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No hay datos de fecha de ingreso suficientes.")
            
    with col2:
        st.subheader("👥 Distribución por Generación y Sexo")
        # Crear bins de edad
        df_age = df_filtered.dropna(subset=['Edad']).copy()
        if not df_age.empty:
            bins = [18, 25, 35, 45, 55, 100]
            labels = ['< 25', '26-35', '36-45', '46-55', '> 55']
            df_age['Rango Etario'] = pd.cut(df_age['Edad'], bins=bins, labels=labels, right=False)
            
            age_dist = df_age.groupby(['Rango Etario', 'Sexo'], observed=False).size().reset_index(name='Cantidad')
            
            fig_age = px.bar(age_dist, x='Rango Etario', y='Cantidad', color='Sexo', barmode='group',
                             color_discrete_map={'Femenino': '#e83e8c', 'Masculino': '#007bff'})
            fig_age.update_layout(xaxis_title="", yaxis_title="", margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("No hay datos de edades suficientes.")

    # 3. Row de Áreas & Sectores y Localidades
    col3, col4, col5 = st.columns([1.5, 1, 1])
    
    with col3:
        st.subheader("🏢 Composición por Área y Sector")
        if 'Sector' in df_filtered.columns and not df_filtered.empty:
            sunburst_data = df_filtered.groupby(['Área', 'Sector']).size().reset_index(name='Cantidad')
            fig_sunburst = px.sunburst(sunburst_data, path=['Área', 'Sector'], values='Cantidad', 
                                       color_discrete_sequence=px.colors.qualitative.Prism)
            fig_sunburst.update_layout(margin=dict(t=10, l=0, r=0, b=0))
            st.plotly_chart(fig_sunburst, use_container_width=True)
            
    with col4:
        st.subheader("📍 Geografía")
        loc_data = df_filtered['Localidad'].value_counts().reset_index()
        loc_data.columns = ['Localidad', 'Cantidad']
        fig_loc = px.pie(loc_data, names='Localidad', values='Cantidad', hole=0.5,
                         color_discrete_sequence=px.colors.sequential.Teal)
        fig_loc.update_traces(textposition='inside', textinfo='percent+label')
        fig_loc.update_layout(margin=dict(t=10, l=0, r=0, b=0), showlegend=False)
        st.plotly_chart(fig_loc, use_container_width=True)
        
    with col5:
        st.subheader("⚖️ Legal y Convenios")
        if 'Convenio' in df_filtered.columns:
            conv_data = df_filtered['Convenio'].fillna('S/D').value_counts().reset_index()
            conv_data.columns = ['Convenio', 'Cantidad']
            fig_conv = px.pie(conv_data, names='Convenio', values='Cantidad', hole=0.5,
                             color_discrete_sequence=px.colors.sequential.Sunset)
            fig_conv.update_traces(textposition='inside', textinfo='percent+label')
            fig_conv.update_layout(margin=dict(t=10, l=0, r=0, b=0), showlegend=False)
            st.plotly_chart(fig_conv, use_container_width=True)
            
    # 4. Tabla de Datos Crudos para Exportación Directa
    st.subheader("📋 Detalle Analítico")
    st.dataframe(df_filtered[['Nombre y Apellido', 'Localidad', 'Sexo', 'Fecha de Ingreso', 'Antigüedad (Años)', 'Convenio', 'Área', 'Puesto', 'Estado']].style.format({'Antigüedad (Años)': '{:.1f}'}), use_container_width=True)

else:
    st.info("No hay datos disponibles para los filtros seleccionados.")
    
# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray; font-size: 0.9em;'>Dashboard Autogenerado • Autosol • 2026</p>", unsafe_allow_html=True)
