import sys

file_path = r'c:\Users\didac\Desktop\OptiSolarAI-main\app.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 298 is where "tab1, tab2, ..." begins in zero-indexed Python (line 299 in the editor)
# We keep lines up to 298 (which is index 298)
new_lines = lines[:298]

new_content = """tab1, tab2 = st.tabs([
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
                    simulador = SimuladorBateria(capacidad_bateria=sim_capacitat, carga_inicial=sim_carrega)
                    resultat = simulador.simular(df_prod, df_prec, sim_consum)
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

"""

new_lines.append(new_content)
# from line 930 (index 929) to the end
new_lines.extend(lines[929:])

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Updated successfully!")
