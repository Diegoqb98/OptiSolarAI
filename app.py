"""
OptiSolarAI - Sistema Inteligente de Gestión Energética
Aplicación principal de Streamlit
"""

import streamlit as st

def main():
    st.set_page_config(
        page_title="OptiSolarAI",
        page_icon="☀️",
        layout="wide"
    )
    
    st.title("☀️ OptiSolarAI")
    st.subheader("Sistema Inteligente de Gestión Energética Solar")
    
    st.info("🚧 Proyecto en desarrollo - UT0B")
    
    st.markdown("""
    ### Bienvenido a OptiSolarAI
    
    Esta plataforma te permitirá:
    - 📊 Predecir producción solar y precios eléctricos
    - 🔋 Simular gestión inteligente de batería
    - 💰 Maximizar beneficios económicos
    - 📈 Visualizar resultados en tiempo real
    
    **Estado actual:** Configuración del entorno de desarrollo
    """)
    
    with st.expander("ℹ️ Sobre el Proyecto"):
        st.markdown("""
        **OptiSolarAI** combina Machine Learning con simulación de baterías 
        para optimizar el uso de energía solar en empresas y hogares.
        
        **Tecnologías:**
        - Python 3.x
        - Streamlit
        - Plotly
        - Scikit-learn / XGBoost
        - OpenWeatherMap API
        
        **Autor:** Diego Quiroga Bausa  
        **Curso:** 2025/2026
        """)

if __name__ == "__main__":
    main()
