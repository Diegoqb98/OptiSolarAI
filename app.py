"""
app.py - Dashboard Principal
OptiSolarAI - Sistema de Gestió d'Energia Solar
UD1B: Versió amb funcionalitats core consolidades
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

# Imports de mòduls propis
from database import (
    get_database_connection,
    get_precios_luz,
    get_produccion_solar,
    get_clima,
    get_datos_completos,
    cargar_datos_ejemplo,
    reset_datos_demo,
    get_estadisticas_resumen,
    insert_consum,
    delete_consum,
    get_consum_per_periode,
    get_consum_per_categoria
)
from ml_engine import (
    SolarPredictor,
    OpenWeatherAPIClient,
    estimar_radiacion_solar,
    generar_pronostico_7dias
)
from rl_engine import AgenteRL
from logic import (
    SimuladorBateria,
    OptimizadorTarifas,
    generar_recomendaciones
)


# ============================================================================
# CONFIGURACIÓ DE LA PÀGINA
# ============================================================================

st.set_page_config(
    page_title="OptiSolarAI",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalitzat — disseny modern fosc amb glassmorphism
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Fons general */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Header principal */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF9500, #FFD700, #FF6B35);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 0.5rem 0;
        letter-spacing: -0.5px;
    }

    .main-subtitle {
        text-align: center;
        color: #a0a0c0;
        font-size: 1.05rem;
        margin-top: -0.5rem;
        font-weight: 300;
        letter-spacing: 0.5px;
    }

    /* Cards de mètriques personalitzades */
    .metric-card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,149,0,0.2);
        padding: 1.2rem 1.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1rem;
        transition: border-color 0.3s;
    }
    .metric-card:hover {
        border-color: rgba(255,149,0,0.6);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        padding: 8px 18px;
        color: #a0a0c0;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF9500, #FF6B35) !important;
        color: white !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a3e 0%, #0f0c29 100%);
        border-right: 1px solid rgba(255,149,0,0.2);
    }
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #FF9500;
    }

    /* Mode energètic pill */
    .mode-pill {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.85rem;
        margin-top: 4px;
    }
    .mode-venda   { background: rgba(255,215,0,0.2);  color: #FFD700; border: 1px solid #FFD700; }
    .mode-carrega { background: rgba(72,199,142,0.2); color: #48c78e; border: 1px solid #48c78e; }
    .mode-compra  { background: rgba(255,100,100,0.2);color: #ff6464; border: 1px solid #ff6464; }
    .mode-neutre  { background: rgba(160,160,190,0.1);color: #a0a0c0; border: 1px solid #a0a0c0; }

    /* Insignes de qualitat dia */
    .badge-excellent { color: #FFD700; font-weight: 600; }
    .badge-bona      { color: #48c78e; font-weight: 600; }
    .badge-moderada  { color: #f0a500; font-weight: 600; }
    .badge-baixa     { color: #ff6464; font-weight: 600; }

    /* Botons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(255,149,0,0.3);
    }

    /* Dividers */
    hr { border-color: rgba(255,149,0,0.15) !important; }

    /* Expander */
    [data-testid="stExpander"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
    }

    /* Métriques st.metric */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 12px 16px;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# SIDEBAR — FILTRES I CONFIGURACIÓ
# ============================================================================

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/solar-panel.png", width=70)
    st.markdown("## ☀️ OptiSolarAI")
    st.markdown("---")

    # Selecció de dates
    st.markdown("### 📅 Rang de Dates")
    fecha_inicio = st.date_input(
        "Data Inici",
        value=datetime(2026, 1, 15),
        max_value=datetime.now()
    )
    fecha_fin = st.date_input(
        "Data Fi",
        value=datetime(2026, 2, 13),
        max_value=datetime.now()
    )

    st.markdown("---")

    # Configuració de bateria
    st.markdown("### 🔋 Configuració de Bateria")
    capacidad_bateria = st.slider(
        "Capacitat (kWh)",
        min_value=5.0, max_value=20.0, value=10.0, step=0.5
    )
    carga_inicial = st.slider(
        "Càrrega Inicial (%)",
        min_value=0, max_value=100, value=50
    )
    consumo_base = st.slider(
        "Consum Base (kWh/h)",
        min_value=1.0, max_value=5.0, value=2.0, step=0.1
    )

    st.markdown("---")

    # Mode energètic actual (simulació senzilla basada en hora)
    hora_actual = datetime.now().hour
    if 10 <= hora_actual <= 16:
        mode_text = "☀️ VENDA"
        mode_class = "mode-venda"
        mode_desc = "Hora de màxima producció"
    elif 7 <= hora_actual < 10:
        mode_text = "🔋 CÀRREGA"
        mode_class = "mode-carrega"
        mode_desc = "Carregant bateria"
    elif 18 <= hora_actual <= 22:
        mode_text = "⚡ COMPRA"
        mode_class = "mode-compra"
        mode_desc = "Hora punta — evitar consum"
    else:
        mode_text = "💤 NEUTRE"
        mode_class = "mode-neutre"
        mode_desc = "Baix consum nocturn"

    st.markdown("### ⚡ Mode Actual")
    st.markdown(
        f'<div class="mode-pill {mode_class}">{mode_text}</div>'
        f'<p style="color:#888;font-size:0.8rem;margin-top:4px">{mode_desc}</p>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Accions
    st.markdown("### ⚙️ Accions")
    if st.button("📦 Carregar Dades (30 dies)", use_container_width=True):
        with st.spinner("Carregant dades d'exemple..."):
            num_registres = cargar_datos_ejemplo()
            st.success(f"✅ {num_registres} registres carregats")
            st.rerun()

    if st.button("🧹 Reiniciar Dades Demo", use_container_width=True):
        with st.spinner("Netejant dades de demo..."):
            counts = reset_datos_demo()
            total = sum(counts.values())
            st.success(
                f"✅ Dades reiniciades ({total} registres eliminats: "
                f"preus {counts['preus_llum']}, producció {counts['produccio_solar']}, clima {counts['clima']})"
            )
            st.rerun()

    if st.button("🤖 Entrenar Model ML", use_container_width=True):
        with st.spinner("Entrenant model Random Forest..."):
            df_complet = get_datos_completos(
                datetime(2026, 1, 15),
                datetime(2026, 2, 13)
            )
            if len(df_complet) > 0:
                predictor_train = SolarPredictor()
                metriques = predictor_train.entrenar_modelo(df_complet)
                st.success(f"✅ Entrenat — R²: {metriques['r2']:.3f}")
            else:
                st.error("❌ Carrega dades primer.")

    st.markdown("---")

    # Resum BD
    stats = get_estadisticas_resumen()
    if stats:
        st.markdown("### 🗄️ Base de Dades")
        st.caption(f"Preus: {stats.get('preus_llum',0):,} registres")
        st.caption(f"Producció: {stats.get('produccio_solar',0):,} registres")
        st.caption(f"Clima: {stats.get('clima',0):,} registres")
        st.caption(f"Consums: {stats.get('consum_llar',0):,} registres")


# ============================================================================
# HEADER PRINCIPAL
# ============================================================================

st.markdown('<h1 class="main-header">☀️ OptiSolarAI</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="main-subtitle">Sistema Intel·ligent de Gestió d\'Energia Solar</p>',
    unsafe_allow_html=True
)
st.divider()


# ============================================================================
# TABS PRINCIPALS
# ============================================================================

tab1, tab2 = st.tabs([
    "🔋 Gestió de Bateria",
    "💶 Beneficis Venda d'Energia"
])

# ============================================================================
# TAB 1: GESTIÓ DE BATERIA
# ============================================================================

with tab1:
    st.header("🔋 Com s'ha gestionat la bateria")
    st.caption("Estat de càrrega i descàrrega de la bateria en funció de la producció i consum.")

    with st.form("form_simulacio"):
        st.subheader("Paràmetres de Simulació")
        col1, col2, col3 = st.columns(3)
        with col1:
            sim_capacitat = st.number_input("Capacitat Bateria (kWh)", value=capacidad_bateria, min_value=1.0)
        with col2:
            sim_carrega = st.number_input("Càrrega Inicial (kWh)", value=(carga_inicial / 100) * capacidad_bateria, min_value=0.0)
        with col3:
            sim_consum = st.number_input("Consum Base (kWh/h)", value=consumo_base, min_value=0.1)
            
        st.markdown("### 🤖 Intel·ligència Artificial")
        tipus_simulacio = st.radio(
            "Mètode de gestió de la bateria:",
            ["Regles Fixes (Clàssic)", "Agent d'Aprenentatge Automàtic (Q-Learning)"],
            help="El mode Q-Learning aprèn dels errors de pronòstic i adapta les seves decisions per maximitzar beneficis a llarg termini."
        )
        
        usar_rl = "Q-Learning" in tipus_simulacio
        entrenar_rl = False
        if usar_rl:
            entrenar_rl = st.checkbox("Entrenar agent durant la simulació", value=True)
            
        executar_sim = st.form_submit_button("▶️ Executar Simulació", use_container_width=True)

    if executar_sim:
        with st.spinner("Executant simulació..."):
            try:
                df_prod = get_produccion_solar(
                    datetime.combine(fecha_inicio, datetime.min.time()),
                    datetime.combine(fecha_fin, datetime.max.time())
                )
                df_prec = get_precios_luz(
                    datetime.combine(fecha_inicio, datetime.min.time()),
                    datetime.combine(fecha_fin, datetime.max.time())
                )

                if len(df_prod) > 0 and len(df_prec) > 0:
                    simulador = SimuladorBateria(
                        capacidad_bateria=sim_capacitat, 
                        carga_inicial=sim_carrega,
                        usar_rl=usar_rl
                    )
                    
                    if usar_rl:
                        st.info("🧠 Utilitzant Agent de Machine Learning (Q-Learning) per a l'optimització...")
                        # Si usemos RL y queremos entrenar, hacemos varias iteraciones rápidas por debajo
                        # para que aprenda mejor antes de mostrar el resultado final
                        if entrenar_rl:
                            my_bar = st.progress(0, text="Entrenant Agent de Machine Learning...")
                            epochs = 5
                            for i in range(epochs):
                                # Train round
                                _ = simulador.simular(df_prod, df_prec, sim_consum, entrenar_rl=True)
                                my_bar.progress((i + 1) / epochs, text=f"Entrenant Agent de Machine Learning... (Època {i+1}/{epochs})")
                                # Reset battery load for next epoch
                                simulador.carga_inicial = sim_carrega
                            my_bar.empty()
                            st.toast('Agent entrenat correctament!', icon='🧠')
                    
                    # Resultado final
                    resultat = simulador.simular(df_prod, df_prec, sim_consum, entrenar_rl=False)
                    st.session_state['simulacio_resultat'] = resultat

                    st.success("✅ Simulació completada")
                    
                    df_detalls = resultat['detalles']
                    
                    fig_bat = go.Figure()
                    fig_bat.add_trace(go.Scatter(
                        x=df_detalls['fecha_hora'],
                        y=df_detalls['carga_bateria'],
                        name='Càrrega Bateria',
                        fill='tozeroy',
                        line=dict(color='#48c78e', width=2),
                        fillcolor='rgba(72,199,142,0.15)'
                    ))
                    fig_bat.update_layout(
                        title="Estat de la Bateria",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#ccc'),
                        yaxis=dict(title='Càrrega (kWh)', gridcolor='rgba(255,255,255,0.05)'),
                        xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig_bat, use_container_width=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🔄 Cicles Bateria", f"{resultat['ciclos_bateria']}")
                    with col2:
                        st.metric("🔋 Càrrega Final", f"{resultat['carga_final']:.1f} kWh")

                else:
                    st.error("❌ No hi ha dades suficients per a la simulació.")
            except Exception as e:
                st.error(f"Error en la simulació: {e}")

# ============================================================================
# TAB 2: BENEFICIS VENDA ENERGIA
# ============================================================================

with tab2:
    st.header("💶 Beneficis de la Venda d'Energia")
    st.caption("Beneficis obtinguts amb la venda d'energia segons la inversió en cada moment del dia.")
    
    if 'simulacio_resultat' in st.session_state:
        resultat = st.session_state['simulacio_resultat']
        df_detalls = resultat['detalles']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💶 Benefici Total", f"{resultat['beneficio_total']:.2f} €")
        with col2:
            st.metric("📅 Benefici Diari", f"{resultat['beneficio_medio_diario']:.2f} €")
            
        st.divider()

        fig_ben = go.Figure()
        fig_ben.add_trace(go.Scatter(
            x=df_detalls['fecha_hora'],
            y=df_detalls['beneficio_acumulado'],
            name='Benefici Acumulat',
            line=dict(color='#FFD700', width=2),
            fill='tozeroy',
            fillcolor='rgba(255,215,0,0.1)'
        ))
        fig_ben.update_layout(
            title="Benefici Acumulat (€)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ccc'),
            yaxis=dict(title='Benefici (€)', gridcolor='rgba(255,255,255,0.05)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            hovermode='x unified'
        )
        st.plotly_chart(fig_ben, use_container_width=True)

        fig_hora = go.Figure()
        
        colors_decision = {
            'vender': '#48c78e',
            'comprar': '#ff6464',
            'descargar': '#FFD700',
            'cargar': '#60a5fa'
        }
        
        for desc in df_detalls['decision'].unique():
            df_subset = df_detalls[df_detalls['decision'] == desc]
            fig_hora.add_trace(go.Bar(
                x=df_subset['fecha_hora'],
                y=df_subset['beneficio_hora'],
                name=desc.capitalize(),
                marker_color=[colors_decision.get(d, '#888') for d in df_subset['decision']]
            ))
            
        fig_hora.update_layout(
            title="Benefici / Cost per Hora (Segons decisió)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#ccc'),
            yaxis=dict(title='€', gridcolor='rgba(255,255,255,0.05)'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            barmode='relative',
            hovermode='x unified'
        )
        st.plotly_chart(fig_hora, use_container_width=True)
        
        with st.expander("📋 Veure detalls hora per hora"):
            st.dataframe(
                df_detalls[['fecha_hora', 'produccion_kwh', 'consumo_kwh', 'precio_kwh',
                            'decision', 'cantidad_kwh', 'beneficio_hora', 'beneficio_acumulado']],
                use_container_width=True
            )
            
    else:
        st.info("ℹ️ Executa primer la simulació a la pestanya 'Gestió de Bateria' per veure els resultats financers.")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown(
    "<p style='text-align:center;color:#555;font-size:0.8rem'>"
    "OptiSolarAI © 2026 — UD1B · Streamlit · DuckDB · Random Forest · Plotly"
    "</p>",
    unsafe_allow_html=True
)
