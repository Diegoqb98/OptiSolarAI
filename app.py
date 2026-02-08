"""
app.py - Dashboard Principal
OptiSolarAI - Sistema de Gestión de Energía Solar
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Imports de módulos propios
from database import (
    get_database_connection, 
    get_precios_luz, 
    get_produccion_solar,
    get_clima,
    get_datos_completos,
    cargar_datos_ejemplo
)
from ml_engine import (
    SolarPredictor, 
    OpenWeatherAPIClient,
    estimar_radiacion_solar
)
from logic import (
    SimuladorBateria, 
    OptimizadorTarifas,
    generar_recomendaciones
)


# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="OptiSolarAI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #FF9500;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px 20px;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# SIDEBAR - FILTROS Y CONFIGURACIÓN
# ============================================================================

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/solar-panel.png", width=80)
    st.title(" Configuración")
    
    # Selección de fechas
    st.subheader(" Rango de Fechas")
    fecha_inicio = st.date_input(
        "Fecha Inicio",
        value=datetime(2026, 2, 1),
        max_value=datetime.now()
    )
    fecha_fin = st.date_input(
        "Fecha Fin",
        value=datetime(2026, 2, 7),
        max_value=datetime.now()
    )
    
    st.divider()
    
    # Configuración de batería
    st.subheader(" Configuración de Batería")
    capacidad_bateria = st.slider(
        "Capacidad (kWh)", 
        min_value=5.0, 
        max_value=20.0, 
        value=10.0, 
        step=0.5
    )
    carga_inicial = st.slider(
        "Carga Inicial (%)", 
        min_value=0, 
        max_value=100, 
        value=50
    )
    consumo_base = st.slider(
        "Consumo Base (kWh/h)", 
        min_value=1.0, 
        max_value=5.0, 
        value=2.0, 
        step=0.1
    )
    
    st.divider()
    
    # Acciones
    st.subheader(" Acciones")
    if st.button(" Cargar Datos de Ejemplo", use_container_width=True):
        with st.spinner("Cargando datos de ejemplo..."):
            num_registros = cargar_datos_ejemplo()
            st.success(f" {num_registros} registros cargados")
            st.rerun()
    
    if st.button(" Entrenar Modelo ML", use_container_width=True):
        with st.spinner("Entrenando modelo Random Forest..."):
            df_completo = get_datos_completos(
                datetime(2026, 2, 1), 
                datetime(2026, 2, 7)
            )
            if len(df_completo) > 0:
                predictor = SolarPredictor()
                metricas = predictor.entrenar_modelo(df_completo)
                st.success(f" Modelo entrenado - R Score: {metricas['r2']:.3f}")
            else:
                st.error("No hay datos suficientes. Carga datos de ejemplo primero.")


# ============================================================================
# HEADER PRINCIPAL
# ============================================================================

st.markdown('<h1 class="main-header"> OptiSolarAI</h1>', unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #666;'>Sistema Inteligente de Gestión de Energía Solar</p>",
    unsafe_allow_html=True
)
st.divider()


# ============================================================================
# TABS PRINCIPALES
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    " Dashboard General", 
    " Simulación de Batería",
    " Predicciones ML",
    " Análisis Financiero"
])


# ============================================================================
# TAB 1: DASHBOARD GENERAL
# ============================================================================

with tab1:
    st.header("Dashboard General")
    
    # Obtener datos
    try:
        df_precios = get_precios_luz(
            datetime.combine(fecha_inicio, datetime.min.time()),
            datetime.combine(fecha_fin, datetime.max.time())
        )
        df_produccion = get_produccion_solar(
            datetime.combine(fecha_inicio, datetime.min.time()),
            datetime.combine(fecha_fin, datetime.max.time())
        )
        df_clima = get_clima(
            datetime.combine(fecha_inicio, datetime.min.time()),
            datetime.combine(fecha_fin, datetime.max.time())
        )
        
        if len(df_precios) == 0:
            st.warning(" No hay datos disponibles. Usa el botón 'Cargar Datos de Ejemplo' en el sidebar.")
        else:
            # KPIs principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                precio_medio = df_precios['precio_kwh'].mean()
                st.metric(" Precio Medio", f"{precio_medio:.3f} €/kWh")
            
            with col2:
                prod_total = df_produccion['produccion_kwh'].sum()
                st.metric(" Producción Total", f"{prod_total:.1f} kWh")
            
            with col3:
                temp_media = df_clima['temperatura'].mean() if len(df_clima) > 0 else 0
                st.metric(" Temperatura Media", f"{temp_media:.1f} C")
            
            with col4:
                nubosidad_media = df_clima['nubosidad'].mean() if len(df_clima) > 0 else 0
                st.metric(" Nubosidad Media", f"{nubosidad_media:.0f} %")
            
            st.divider()
            
            # Gráfico de precios y producción
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(" Evolución de Precios")
                fig_precios = px.line(
                    df_precios, 
                    x='fecha_hora', 
                    y='precio_kwh',
                    title="Precio de la Electricidad",
                    labels={'precio_kwh': 'Precio (€/kWh)', 'fecha_hora': 'Fecha'}
                )
                fig_precios.update_traces(line_color='#FF9500')
                st.plotly_chart(fig_precios, use_container_width=True)
            
            with col2:
                st.subheader(" Producción Solar")
                fig_produccion = px.area(
                    df_produccion,
                    x='fecha_hora',
                    y='produccion_kwh',
                    title="Producción de Energía Solar",
                    labels={'produccion_kwh': 'Producción (kWh)', 'fecha_hora': 'Fecha'}
                )
                fig_produccion.update_traces(fillcolor='rgba(255, 215, 0, 0.3)', line_color='gold')
                st.plotly_chart(fig_produccion, use_container_width=True)
            
            # Datos climáticos
            if len(df_clima) > 0:
                st.subheader(" Condiciones Climáticas")
                fig_clima = go.Figure()
                fig_clima.add_trace(go.Scatter(
                    x=df_clima['fecha_hora'],
                    y=df_clima['temperatura'],
                    name='Temperatura',
                    yaxis='y',
                    line=dict(color='red')
                ))
                fig_clima.add_trace(go.Scatter(
                    x=df_clima['fecha_hora'],
                    y=df_clima['nubosidad'],
                    name='Nubosidad',
                    yaxis='y2',
                    line=dict(color='gray')
                ))
                fig_clima.update_layout(
                    yaxis=dict(title='Temperatura (C)'),
                    yaxis2=dict(title='Nubosidad (%)', overlaying='y', side='right'),
                    hovermode='x unified'
                )
                st.plotly_chart(fig_clima, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")


# ============================================================================
# TAB 2: SIMULACIÓN DE BATERÍA
# ============================================================================

with tab2:
    st.header(" Simulación de Batería")
    
    with st.form("form_simulacion"):
        st.subheader("Parámetros de Simulación")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sim_capacidad = st.number_input(
                "Capacidad Batería (kWh)", 
                value=capacidad_bateria, 
                min_value=1.0
            )
        with col2:
            sim_carga = st.number_input(
                "Carga Inicial (kWh)", 
                value=(carga_inicial/100) * capacidad_bateria,
                min_value=0.0
            )
        with col3:
            sim_consumo = st.number_input(
                "Consumo Base (kWh/h)", 
                value=consumo_base,
                min_value=0.1
            )
        
        ejecutar_sim = st.form_submit_button(" Ejecutar Simulación", use_container_width=True)
    
    if ejecutar_sim:
        with st.spinner("Ejecutando simulación..."):
            try:
                # Obtener datos
                df_prod = get_produccion_solar(
                    datetime.combine(fecha_inicio, datetime.min.time()),
                    datetime.combine(fecha_fin, datetime.max.time())
                )
                df_prec = get_precios_luz(
                    datetime.combine(fecha_inicio, datetime.min.time()),
                    datetime.combine(fecha_fin, datetime.max.time())
                )
                
                if len(df_prod) > 0 and len(df_prec) > 0:
                    # Ejecutar simulación
                    simulador = SimuladorBateria(
                        capacidad_bateria=sim_capacidad,
                        carga_inicial=sim_carga
                    )
                    resultado = simulador.simular(df_prod, df_prec, sim_consumo)
                    
                    # Mostrar resultados
                    st.success(" Simulación completada")
                    
                    # Métricas
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric(" Beneficio Total", f"{resultado['beneficio_total']:.2f} €")
                    with col2:
                        st.metric(" Beneficio Diario", f"{resultado['beneficio_medio_diario']:.2f} €")
                    with col3:
                        st.metric(" Ciclos Batería", f"{resultado['ciclos_bateria']}")
                    with col4:
                        st.metric(" Carga Final", f"{resultado['carga_final']:.1f} kWh")
                    
                    st.divider()
                    
                    # Gráficos
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Gráfico de balance energético
                        df_detalles = resultado['detalles']
                        fig_balance = go.Figure()
                        fig_balance.add_trace(go.Scatter(
                            x=df_detalles['fecha_hora'],
                            y=df_detalles['carga_bateria'],
                            name='Carga Batería',
                            fill='tozeroy',
                            line=dict(color='green')
                        ))
                        fig_balance.update_layout(
                            title="Estado de la Batería",
                            yaxis_title="Carga (kWh)",
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig_balance, use_container_width=True)
                    
                    with col2:
                        # Gráfico de beneficios acumulados
                        fig_beneficio = px.line(
                            df_detalles,
                            x='fecha_hora',
                            y='beneficio_acumulado',
                            title="Beneficio Acumulado",
                            labels={'beneficio_acumulado': 'Beneficio (€)'}
                        )
                        fig_beneficio.update_traces(line_color='gold')
                        st.plotly_chart(fig_beneficio, use_container_width=True)
                    
                    # Recomendaciones
                    st.subheader(" Recomendaciones")
                    recomendaciones = generar_recomendaciones(resultado, df_prec)
                    for rec in recomendaciones:
                        st.info(rec)
                    
                    # Tabla de detalles
                    with st.expander(" Ver detalles hora por hora"):
                        st.dataframe(
                            df_detalles[['fecha_hora', 'produccion_kwh', 'precio_kwh', 
                                       'decision', 'cantidad_kwh', 'carga_bateria', 'beneficio_hora']],
                            use_container_width=True
                        )
                
                else:
                    st.error("No hay datos suficientes para la simulación.")
            
            except Exception as e:
                st.error(f"Error en la simulación: {e}")


# ============================================================================
# TAB 3: PREDICCIONES ML
# ============================================================================

with tab3:
    st.header(" Predicciones con Machine Learning")
    
    # Cargar predictor
    predictor = SolarPredictor()
    modelo_cargado = predictor.cargar_modelo()
    
    if not modelo_cargado:
        st.warning(" No hay modelo entrenado. Usa el botón 'Entrenar Modelo ML' en el sidebar.")
    else:
        st.success(f" Modelo cargado - Entrenado el: {predictor.metrics.get('fecha_entrenamiento', 'N/A')}")
        
        # Métricas del modelo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(" R Score", f"{predictor.metrics.get('r2', 0):.3f}")
        with col2:
            st.metric(" MAE", f"{predictor.metrics.get('mae', 0):.3f} kWh")
        with col3:
            st.metric(" Muestras", predictor.metrics.get('n_samples', 0))
        
        st.divider()
        
        # Predicción individual
        st.subheader(" Predicción Individual")
        
        with st.form("form_prediccion"):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                temp = st.number_input("Temperatura (C)", value=25.0, min_value=-10.0, max_value=50.0)
            with col2:
                nubos = st.slider("Nubosidad (%)", 0, 100, 30)
            with col3:
                hum = st.slider("Humedad (%)", 0, 100, 50)
            with col4:
                rad = st.number_input("Radiación (W/m)", value=600.0, min_value=0.0, max_value=1200.0)
            
            predecir = st.form_submit_button(" Predecir Producción", use_container_width=True)
        
        if predecir:
            prediccion = predictor.predecir(temp, nubos, hum, rad)
            st.success(f" Producción estimada: **{prediccion:.2f} kWh**")
        
        # Importancia de features
        st.divider()
        st.subheader(" Importancia de Variables")
        if predictor.feature_importance is not None:
            fig_importance = px.bar(
                predictor.feature_importance,
                x='importance',
                y='feature',
                orientation='h',
                title="Importancia de Características en el Modelo"
            )
            st.plotly_chart(fig_importance, use_container_width=True)


# ============================================================================
# TAB 4: ANÁLISIS FINANCIERO
# ============================================================================

with tab4:
    st.header(" Análisis Financiero")
    
    with st.form("form_financiero"):
        st.subheader(" Parámetros de Inversión")
        
        col1, col2 = st.columns(2)
        with col1:
            inversion_inicial = st.number_input(
                "Inversión Inicial (€)", 
                value=15000.0, 
                min_value=1000.0,
                step=1000.0
            )
            vida_util = st.slider("Vida Útil (años)", 10, 30, 25)
        
        with col2:
            beneficio_anual = st.number_input(
                "Beneficio Anual Estimado (€)", 
                value=1200.0,
                min_value=0.0,
                step=100.0
            )
        
        calcular = st.form_submit_button(" Calcular ROI", use_container_width=True)
    
    if calcular:
        optimizador = OptimizadorTarifas()
        roi = optimizador.calcular_roi(inversion_inicial, beneficio_anual, vida_util)
        
        # Mostrar resultados
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(" ROI", f"{roi['roi_porcentaje']:.1f}%")
        with col2:
            st.metric(" Payback", f"{roi['payback_anos']:.1f} años")
        with col3:
            st.metric(" Beneficio Total", f"{roi['beneficio_total']:,.0f} €")
        with col4:
            st.metric(" TIR Aprox.", f"{roi['tir_aproximado']:.1f}%")
        
        st.divider()
        
        # Gráfico de proyección
        anos = list(range(vida_util + 1))
        beneficios = [beneficio_anual * i - inversion_inicial for i in anos]
        
        fig_proyeccion = go.Figure()
        fig_proyeccion.add_trace(go.Scatter(
            x=anos,
            y=beneficios,
            mode='lines+markers',
            name='Beneficio Neto',
            line=dict(color='green', width=3)
        ))
        fig_proyeccion.add_hline(y=0, line_dash="dash", line_color="red")
        fig_proyeccion.update_layout(
            title="Proyección Financiera",
            xaxis_title="Años",
            yaxis_title="Beneficio Neto (€)",
            hovermode='x unified'
        )
        st.plotly_chart(fig_proyeccion, use_container_width=True)


# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown(
    "<p style='text-align: center; color: #999;'>OptiSolarAI  2026 | Desarrollado con Streamlit, DuckDB y Random Forest</p>",
    unsafe_allow_html=True
)
