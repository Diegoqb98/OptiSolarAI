#  OptiSolarAI - Sistema de Gestión de Energía Solar

Sistema inteligente de gestión de energía solar con Machine Learning que optimiza el uso de baterías para maximizar beneficios económicos.

##  Características Principales

- **Dashboard Interactivo**: Visualización en tiempo real de producción solar, precios de electricidad y datos climáticos
- **Simulación de Batería**: Algoritmo inteligente que decide cuándo cargar, descargar o vender energía
- **Machine Learning**: Predicción de producción solar usando Random Forest con datos meteorológicos
- **Análisis Financiero**: Cálculo de ROI, payback y TIR de la instalación solar
- **Base de Datos**: Gestión eficiente con DuckDB

##  Estructura del Proyecto

```
OptiSolarAI/

 app.py                 # Dashboard principal con Streamlit
 database.py            # Gestión de DuckDB (@st.cache_resource)
 ml_engine.py           # Modelo de Random Forest para predicciones
 logic.py               # Simulador de batería y optimización
 requirements.txt       # Dependencias del proyecto

 data/                  # Base de datos DuckDB
    optisolar.duckdb

 models/                # Modelos ML entrenados
    solar_predictor.pkl

 pages/                 # Páginas adicionales de Streamlit (opcional)

 templates/             # Plantillas HTML personalizadas (opcional)
```

##  Instalación

### 1. Clonar o crear el proyecto

```powershell
cd C:\OptiSolarAI
```

### 2. Crear entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias

```powershell
pip install -r requirements.txt
```

##  Ejecutar la Aplicación

```powershell
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

##  Uso del Dashboard

### 1. Cargar Datos Iniciales

- En el **sidebar**, haz clic en " Cargar Datos de Ejemplo"
- Esto generará 7 días de datos sintéticos realistas

### 2. Entrenar Modelo ML

- En el **sidebar**, haz clic en " Entrenar Modelo ML"
- El modelo Random Forest se entrenará con los datos disponibles

### 3. Explorar las Pestañas

####  Dashboard General
- Visualiza precios de electricidad
- Monitorea producción solar en tiempo real
- Revisa condiciones climáticas

####  Simulación de Batería
- Configura capacidad de batería y consumo
- Ejecuta simulaciones para optimizar beneficios
- Obtén recomendaciones inteligentes

####  Predicciones ML
- Realiza predicciones individuales de producción
- Analiza importancia de variables climáticas
- Visualiza métricas del modelo (R, MAE)

####  Análisis Financiero
- Calcula ROI de tu instalación solar
- Determina periodo de payback
- Proyecta beneficios a largo plazo

##  Configuración

### Base de Datos DuckDB

Las tablas se crean automáticamente:
- `precios_luz`: Precios horarios de electricidad
- `produccion_solar`: Producción histórica
- `clima`: Datos meteorológicos
- `simulaciones_bateria`: Historial de simulaciones

### API de OpenWeatherMap (Opcional)

Para datos climáticos reales, edita `ml_engine.py`:

```python
api_client = OpenWeatherAPIClient(api_key="TU_API_KEY")
```

Obtén tu API key gratis en: https://openweathermap.org/api

##  Dependencias Principales

- **streamlit**: Framework web para el dashboard
- **duckdb**: Base de datos analítica embebida
- **plotly**: Visualizaciones interactivas
- **pandas**: Manipulación de datos
- **scikit-learn**: Machine Learning (Random Forest)
- **requests**: Cliente HTTP para APIs

##  Algoritmo de Simulación de Batería

El simulador implementa una estrategia inteligente:

1. **Exceso de Producción + Precio Bajo**  CARGAR batería
2. **Déficit + Precio Alto**  DESCARGAR batería
3. **Precio Alto + Batería Llena**  VENDER a la red
4. **Precio Bajo + Batería Vacía**  COMPRAR de la red

##  Modelo de Machine Learning

**Algoritmo**: Random Forest Regressor
**Features**: 
- Temperatura (C)
- Nubosidad (%)
- Humedad (%)
- Radiación solar (W/m)

**Target**: Producción solar (kWh)

**Métricas**:
- R Score: Bondad de ajuste
- MAE: Error absoluto medio

##  Contribuciones

Este proyecto es educativo. Siéntete libre de:
- Añadir nuevas funcionalidades
- Mejorar los algoritmos
- Integrar APIs reales de precios de luz
- Crear tests unitarios

##  Licencia

Proyecto educativo - UD1A Ciencia de Datos

##  Autor

Desarrollado como proyecto de Sistema de Gestión de Energía Solar

---

** Nota**: Este proyecto utiliza datos sintéticos para demostración. Para uso en producción, integra APIs reales de precios de electricidad y meteorología.
