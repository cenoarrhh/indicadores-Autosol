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

# Paleta CY24SU10 extraida de Power BI
PBI_COLORS = ['#118DFF', '#12239E', '#E66C37', '#6B007B', '#E044A7', '#744EC2', '#D9B300', '#D64550', '#1AAB40']
PBI_BG_CANVAS = '#F3F2F1'
PBI_BG_CARD = '#FFFFFF'
PBI_TEXT_PRI = '#252423'
PBI_TEXT_SEC = '#605E5C'

# Estilos CSS Personalizados para simular Power BI
st.markdown(f"""
<style>
    /* Fondo principal y textos (simulando lienzo gris claro de Power BI) */
    .stApp {{
        background-color: {PBI_BG_CANVAS};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* Panel lateral / Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {PBI_BG_CARD} !important;
        border-right: 1px solid #E1DFDD;
    }}
    
    /* Formato estilo "Tarjetas" (Cards) de Power BI para métricas */
    [data-testid="stMetric"] {{
        background-color: {PBI_BG_CARD};
        padding: 15px 20px;
        border-radius: 2px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0,0,0,0.24);
        margin-bottom: 10px;
    }}
    
    /* Valores de los KPIs */
    [data-testid="stMetricValue"] {{
        font-size: 2.5rem !important;
        font-weight: 400 !important;
        color: {PBI_TEXT_PRI} !important;
        font-family: 'Segoe UI', Tahoma, sans-serif !important;
    }}
    /* Títulos de los KPIs */
    [data-testid="stMetricLabel"] {{
        font-size: 14px !important;
        font-weight: 600 !important;
        color: {PBI_TEXT_SEC} !important;
    }}
    
    /* Headers de la página */
    h1 {{
        color: {PBI_TEXT_PRI};
        font-weight: 600;
        padding-bottom: 0px;
        padding-top: 1rem;
    }}
    h2, h3 {{
        color: {PBI_TEXT_PRI};
        font-weight: 600;
        font-size: 1.1rem !important;
    }}
    
    /* Asegurar que los graficos tambien parezcan "tarjetas" flotantes */
    .stPlotlyChart {{
        background-color: {PBI_BG_CARD};
        padding: 10px;
        border-radius: 2px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0,0,0,0.24);
    }}

    /* Dataframe table styling to match PBI somewhat */
    [data-testid="stDataFrame"] {{
        background-color: {PBI_BG_CARD};
        padding: 15px;
        border-radius: 2px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0,0,0,0.24);
    }}
    
    /* Remueve margenes extra */
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 2rem;
    }}
</style>
""", unsafe_allow_html=True)

# URL de datos
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vR7Ila8tzO3SEBZ5-faEFW-9VZY8eiPCUV3vPhryrlyqsmovw76hKqVRc-y18rTmz0NugYIUv6JTxRH/pub?output=csv"

@st.cache_data(ttl=3600)
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        df = df.dropna(subset=['Nombre y Apellido', 'Área', 'Fecha de Ingreso'])
        
        df['Fecha de Ingreso'] = pd.to_datetime(df['Fecha de Ingreso'], errors='coerce', dayfirst=True)
        df['Fecha de Nacimiento'] = pd.to_datetime(df['Fecha de Nacimiento'], errors='coerce', dayfirst=True)
        
        now = pd.Timestamp.now()
        df['Edad'] = (now - df['Fecha de Nacimiento']).dt.days / 365.25
        df['Antigüedad (Años)'] = (now - df['Fecha de Ingreso']).dt.days / 365.25
        
        df['Estado'] = df['Estado'].fillna('Desconocido')
        df['Localidad'] = df['Localidad'].fillna('Sin especificar')
        df['Sexo'] = df['Sexo'].fillna('Sin Especificar')
        df['Categoría'] = df.get('Categoría', pd.Series(['Sin Definir']*len(df))).fillna('Sin Definir')
        
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame()

df_raw = load_data()

if df_raw.empty:
    st.warning("No se encontraron datos o hubo un error al leer la fuente. Revisa el link de Google Sheets.")
    st.stop()

# ----------------------------------------------------
# COMPONENTES DEL SIDEBAR (Filtros - Slicers)
# ----------------------------------------------------
st.sidebar.markdown(f"<h2 style='color:{PBI_TEXT_PRI};'>Filtros</h2>", unsafe_allow_html=True)

estados_disponibles = ["Todos"] + list(df_raw['Estado'].dropna().unique())
estado_seleccionado = st.sidebar.selectbox("Estado", estados_disponibles, index=estados_disponibles.index("Activo") if "Activo" in estados_disponibles else 0)

df_filtered = df_raw.copy()
if estado_seleccionado != "Todos":
    df_filtered = df_filtered[df_filtered['Estado'] == estado_seleccionado]

loc_disponibles = ["Todas"] + list(df_filtered['Localidad'].dropna().unique())
loc_seleccionada = st.sidebar.selectbox("Localidad", loc_disponibles)

area_disponibles = ["Todas"] + list(df_filtered['Área'].dropna().unique())
area_seleccionada = st.sidebar.selectbox("Área", area_disponibles)

sexo_disponibles = ["Todos"] + list(df_filtered['Sexo'].dropna().unique())
sexo_seleccionado = st.sidebar.selectbox("Sexo", sexo_disponibles)

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
    st.title("Dotación, Rotación, Ausentismo y Formación")
with col_date:
    st.markdown(f"<div style='text-align: right; color: {PBI_TEXT_SEC}; padding-top: 35px; font-size:12px;'>Última actualización<br><b>{datetime.now().strftime('%d/%m/%Y')}</b></div>", unsafe_allow_html=True)

st.markdown("---")

if not df_filtered.empty:
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_dotacion = len(df_filtered)
    kpi1.metric("Dotación Total", f"{total_dotacion:,}")
    
    edad_promedio = df_filtered['Edad'].mean()
    kpi2.metric("Edad Promedio", f"{edad_promedio:.1f} años" if pd.notnull(edad_promedio) else "0.0")
    
    ant_promedio = df_filtered['Antigüedad (Años)'].mean()
    kpi3.metric("Antigüedad Promedio", f"{ant_promedio:.1f} años" if pd.notnull(ant_promedio) else "0.0")
    
    if 'Femenino' in df_filtered['Sexo'].values:
        femenino_pct = (len(df_filtered[df_filtered['Sexo'] == 'Femenino']) / total_dotacion) * 100
        kpi4.metric("% Mujeres", f"{femenino_pct:.1f}%")
    else:
        kpi4.metric("% Mujeres", "0.0%")
        
    st.write("") # Spacing
    
    # Base layout para todos los charts de plotly (PBI Style)
    plotly_layout_defaults = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Segoe UI, Tahoma, sans-serif", color=PBI_TEXT_SEC, size=11),
        margin=dict(l=10, r=10, t=30, b=10)
    )

    col1, col2 = st.columns(2)
    
    with col1:
        # st.subheader no es necesario si lo ponemos en el chart de plotly como title
        df_hist = df_filtered.dropna(subset=['Fecha de Ingreso']).copy()
        if not df_hist.empty:
            df_hist['AÑO_MES'] = df_hist['Fecha de Ingreso'].dt.to_period('M')
            hist_counts = df_hist.groupby('AÑO_MES').size().reset_index(name='Ingresos')
            hist_counts['AÑO_MES'] = hist_counts['AÑO_MES'].dt.to_timestamp()
            hist_counts = hist_counts.sort_values('AÑO_MES')
            hist_counts['Dotación Acumulada'] = hist_counts['Ingresos'].cumsum()
            
            fig_hist = px.area(hist_counts, x='AÑO_MES', y='Dotación Acumulada', title="Histórico de Ingresos Acumulados")
            fig_hist.update_traces(line_color=PBI_COLORS[0])
            fig_hist.update_layout(**plotly_layout_defaults, xaxis_title="", yaxis_title="")
            fig_hist.update_xaxes(showgrid=False)
            fig_hist.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E1DFDD')
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("No hay datos históricos")
            
    with col2:
        df_age = df_filtered.dropna(subset=['Edad']).copy()
        if not df_age.empty:
            bins = [18, 25, 35, 45, 55, 100]
            labels = ['< 25', '26-35', '36-45', '46-55', '> 55']
            df_age['Rango Etario'] = pd.cut(df_age['Edad'], bins=bins, labels=labels, right=False)
            
            age_dist = df_age.groupby(['Rango Etario', 'Sexo'], observed=False).size().reset_index(name='Cantidad')
            
            fig_age = px.bar(age_dist, x='Rango Etario', y='Cantidad', color='Sexo', barmode='group',
                             color_discrete_map={'Femenino': PBI_COLORS[4], 'Masculino': PBI_COLORS[0], 'Sin Especificar': PBI_COLORS[2]},
                             title="Distribución por Rango Etario y Sexo")
            fig_age.update_layout(**plotly_layout_defaults, xaxis_title="", yaxis_title="")
            fig_age.update_xaxes(showgrid=False)
            fig_age.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E1DFDD')
            st.plotly_chart(fig_age, use_container_width=True)
        else:
            st.info("No hay datos de edad")

    # 3. Row de Áreas & Sectores y Localidades
    col3, col4, col5 = st.columns([2, 1.5, 1.5])
    
    with col3:
        if 'Sector' in df_filtered.columns and not df_filtered.empty:
            sunburst_data = df_filtered.groupby(['Área', 'Sector']).size().reset_index(name='Cantidad')
            fig_sunburst = px.sunburst(sunburst_data, path=['Área', 'Sector'], values='Cantidad', 
                                       title="Composición por Área (Árbol)", color_discrete_sequence=PBI_COLORS)
            fig_sunburst.update_layout(**plotly_layout_defaults)
            st.plotly_chart(fig_sunburst, use_container_width=True)
            
    with col4:
        loc_data = df_filtered['Localidad'].value_counts().reset_index()
        loc_data.columns = ['Localidad', 'Cantidad']
        fig_loc = px.pie(loc_data, names='Localidad', values='Cantidad', hole=0.6,
                         title="Geografía Local", color_discrete_sequence=PBI_COLORS)
        fig_loc.update_traces(textposition='inside', textinfo='percent+label')
        fig_loc.update_layout(**plotly_layout_defaults, showlegend=False)
        st.plotly_chart(fig_loc, use_container_width=True)
        
    with col5:
        if 'Convenio' in df_filtered.columns or 'Estado' in df_filtered.columns:
            # Reutilizamos Estado si Convenio no es el foco del PBI actual
            est_data = df_filtered['Estado'].value_counts().reset_index()
            est_data.columns = ['Estado', 'Cantidad']
            pbi_estado_colors = ['#1AAB40', '#D64550', '#D9B300'] # Verde Activo, Rojo Inactivo
            fig_estado = px.pie(est_data, names='Estado', values='Cantidad', hole=0.6,
                             title="Distribución de Estado", color_discrete_sequence=pbi_estado_colors)
            fig_estado.update_traces(textposition='inside', textinfo='percent+label')
            fig_estado.update_layout(**plotly_layout_defaults, showlegend=False)
            st.plotly_chart(fig_estado, use_container_width=True)
            
    # 4. Tabla de Datos Crudos
    st.markdown(f"<h3 style='color:{PBI_TEXT_PRI};'>Detalles Analíticos de la Nómina</h3>", unsafe_allow_html=True)
    st.dataframe(df_filtered[['Nombre y Apellido', 'Localidad', 'Sexo', 'Fecha de Ingreso', 'Antigüedad (Años)', 'Convenio', 'Área', 'Puesto', 'Estado']].style.format({'Antigüedad (Años)': '{:.1f}'}), use_container_width=True)

else:
    st.info("No hay datos disponibles para los filtros seleccionados.")
    
# Footer
st.markdown("---")
st.markdown(f"<p style='text-align: center; color: {PBI_TEXT_SEC}; font-size: 0.8em;'>Dashboard Integrado (Estilo PBI CY24SU10) • Autosol</p>", unsafe_allow_html=True)
