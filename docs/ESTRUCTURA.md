# Estructura del Proyecto OptiSolarAI

```
OptiSolarAI/
│
├── README.md                 # Descripción principal del proyecto
├── LICENSE                   # Licencia MIT
├── requirements.txt          # Dependencias de Python
├── .gitignore               # Archivos ignorados por Git
│
├── app.py                   # Aplicación principal de Streamlit (próximamente)
│
├── src/                     # Código fuente
│   ├── __init__.py
│   ├── models/              # Modelos de Machine Learning
│   │   ├── __init__.py
│   │   ├── price_predictor.py
│   │   └── solar_predictor.py
│   │
│   ├── simulation/          # Lógica de simulación de batería
│   │   ├── __init__.py
│   │   └── battery_manager.py
│   │
│   ├── data/                # Procesamiento de datos
│   │   ├── __init__.py
│   │   └── data_loader.py
│   │
│   ├── api/                 # Integración con APIs externas
│   │   ├── __init__.py
│   │   └── weather_api.py
│   │
│   └── visualization/       # Gráficos y visualizaciones
│       ├── __init__.py
│       └── charts.py
│
├── data/                    # Datos del proyecto
│   ├── raw/                 # Datos sin procesar
│   ├── processed/           # Datos procesados
│   └── README.md            # Descripción de los datos
│
├── models/                  # Modelos entrenados guardados
│   └── README.md
│
├── docs/                    # Documentación
│   ├── UT0_proyecto_inicial.md
│   ├── UT0B_entorno_trabajo.md
│   └── wireframes/
│
└── tests/                   # Tests unitarios (próximamente)
    └── __init__.py
```

## Descripción de Directorios

### `/src`
Contiene todo el código fuente de la aplicación dividido en módulos:
- **models/**: Modelos de ML para predicción
- **simulation/**: Lógica de gestión de batería
- **data/**: Carga y procesamiento de datos
- **api/**: Conexión con APIs externas
- **visualization/**: Componentes de visualización

### `/data`
Almacena los datos utilizados en el proyecto:
- **raw/**: Datos originales sin modificar
- **processed/**: Datos limpiados y transformados

### `/models`
Guarda los modelos de ML entrenados en formato serializado (.pkl, .joblib)

### `/docs`
Documentación del proyecto, incluyendo entregas académicas y diseños

### `/tests`
Tests unitarios para asegurar calidad del código
