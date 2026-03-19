# Estructura del Projecte OptiSolarAI (UD1B)

```
OptiSolarAI/
│
├── app.py                    # Dashboard principal (Streamlit) — 6 tabs
├── database.py               # Capa de dades — DuckDB (5 taules)
├── ml_engine.py              # Motor ML — Random Forest + previsió 7 dies
├── logic.py                  # Lògica de negoci — simulador bateria, ROI
├── config.py                 # Configuració centralitzada
├── utils.py                  # Funcions utilitàries generals
│
├── requirements.txt          # Dependències de Python
├── .gitignore                # Fitxers ignorats per Git
├── LICENSE                   # Llicència MIT
├── README.md                 # Documentació principal
├── EJECUTAR.bat              # Script per executar l'app (Windows)
├── INSTALAR.bat              # Script d'instal·lació (Windows)
│
├── data/                     # Base de dades
│   └── optisolar.duckdb      # DuckDB (generat automàticament)
│
├── models/                   # Models ML entrenats
│   └── solar_predictor.pkl   # Random Forest (generat en entrenar)
│
├── docs/                     # Documentació tècnica
│   ├── UD1B_documentacion_tecnica.md   # [NOU] Decisions UD1B
│   ├── ESTRUCTURA.md                   # Aquest fitxer
│   ├── mockup_specifications.md        # Especificacions visuals
│   └── trello_board_structure.md       # Estructura del Trello
│
└── MockUps/                  # Imatges de mockups UI
```

## Taules de la Base de Dades

| Taula | Descripció | Columnes principals |
|---|---|---|
| `precios_luz` | Preus horaris de l'electricitat | `fecha_hora`, `precio_kwh` |
| `produccion_solar` | Producció solar horària | `fecha_hora`, `produccion_kwh`, `radiacion` |
| `clima` | Dades meteorològiques | `fecha_hora`, `temperatura`, `nubosidad`, `humedad` |
| `simulaciones_bateria` | Historial de simulacions | `id`, `fecha_creacion`, `resultados` |
| `registre_consum` | **[NOU UD1B]** Consum del llar | `id`, `data`, `categoria`, `electrodomestic`, `kwh` |

## Tabs de l'Aplicació

| Tab | Funcionalitat |
|---|---|
| 📊 Dashboard | Visió general: preus, producció solar, clima |
| 🔋 Simulació Bateria | Algoritme intel·ligent de gestió de bateria |
| 🤖 Prediccions ML | Random Forest per a predicció de producció |
| 💶 Anàlisi Financer | ROI, payback, TIR de la instal·lació |
| 📅 Previsió 7 Dies | **[NOU UD1B]** Pronòstic solar setmanal |
| 🏠 Consum del Llar | **[NOU UD1B]** Monitor de consum per electrodomèstic |
