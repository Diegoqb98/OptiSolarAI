import sys

file_path = r'c:\Users\didac\Desktop\OptiSolarAI-main\app.py'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Add import for AgenteRL if not present
if "from rl_engine import " not in text:
    text = text.replace(
        "from ml_engine import (\n    SolarPredictor,\n    OpenWeatherAPIClient,\n    estimar_radiacion_solar,\n    generar_pronostico_7dias\n)", 
        "from ml_engine import (\n    SolarPredictor,\n    OpenWeatherAPIClient,\n    estimar_radiacion_solar,\n    generar_pronostico_7dias\n)\nfrom rl_engine import AgenteRL"
    )

# Substitute the battery form section
old_form = """    with st.form("form_simulacio"):
        st.subheader("Paràmetres de Simulació")
        col1, col2, col3 = st.columns(3)
        with col1:
            sim_capacitat = st.number_input("Capacitat Bateria (kWh)", value=capacidad_bateria, min_value=1.0)
        with col2:
            sim_carrega = st.number_input("Càrrega Inicial (kWh)", value=(carga_inicial / 100) * capacidad_bateria, min_value=0.0)
        with col3:
            sim_consum = st.number_input("Consum Base (kWh/h)", value=consumo_base, min_value=0.1)
        executar_sim = st.form_submit_button("▶️ Executar Simulació", use_container_width=True)

    if executar_sim:"""

new_form = """    with st.form("form_simulacio"):
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

    if executar_sim:"""

text = text.replace(old_form, new_form)

# Substitute the simulation execution
old_sim = """                if len(df_prod) > 0 and len(df_prec) > 0:
                    simulador = SimuladorBateria(capacidad_bateria=sim_capacitat, carga_inicial=sim_carrega)
                    resultat = simulador.simular(df_prod, df_prec, sim_consum)"""
                    
new_sim = """                if len(df_prod) > 0 and len(df_prec) > 0:
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
                    resultat = simulador.simular(df_prod, df_prec, sim_consum, entrenar_rl=False)"""

text = text.replace(old_sim, new_sim)


with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Actualizado app.py")
