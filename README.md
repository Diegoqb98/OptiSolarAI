# ☀️ OptiSolarAI — Sistema de Gestió d'Energia Solar

Sistema intel·ligent de gestió d'energia solar amb Machine Learning que optimitza l'ús de bateries per maximitzar beneficis econòmics.

## ✨ Funcionalitats Principals (UD1B)

| Tab | Descripció |
|---|---|
| 📊 Dashboard General | Preus, producció solar i clima en temps real |
| 🔋 Simulació de Bateria | Algorisme intel·ligent: cargar / descarregar / vendre |
| 🤖 Prediccions ML | Random Forest per predir producció solar |
| 💶 Anàlisi Financer | ROI, payback i TIR de la instal·lació |
| 📅 **Previsió 7 Dies** | Pronòstic solar setmanal amb alertes intel·ligents |
| 🏠 **Monitor Consum** | Registre de consum per electrodomèstic i categoria |

## 🏗️ Arquitectura

```
app.py          → Dashboard (Streamlit, 6 tabs)
database.py     → Capa de dades (DuckDB, 5 taules)
ml_engine.py    → Machine Learning (Random Forest)
logic.py        → Simulador de bateria i optimitzador
config.py       → Configuració centralitzada
utils.py        → Funcions utilitàries
```

## 🚀 Instal·lació i Execució

### Prerequisits
- Python 3.9+
- pip

### Instal·lació

```powershell
cd C:\Users\...\OptiSolarAI-main
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Execució

```powershell
streamlit run app.py
```

Obre `http://localhost:8501` al navegador.

### Primers passos

1. **Sidebar** → clic a "📦 Carregar Dades (30 dies)"
2. **Sidebar** → clic a "🤖 Entrenar Model ML"
3. Explora les 6 tabs del dashboard

## 🔬 Model de Machine Learning

**Algorisme:** Random Forest Regressor
**Features:** Temperatura, Nuvolositat, Humitat, Radiació solar
**Target:** Producció solar (kWh)
**Mètriques:** R² Score, MAE

## 🔋 Algorisme de Simulació de Bateria

| Condició | Decisió |
|---|---|
| Excés producció + preu baix | CARREGAR bateria |
| Dèficit + preu alt | DESCARREGAR bateria |
| Preu molt alt + bateria plena | VENDRE a la xarxa |
| Preu baix + bateria buida | COMPRAR de la xarxa |

## 📦 Dependències Principals

- **streamlit** — Framework web del dashboard
- **duckdb** — Base de dades analítica embeguda
- **plotly** — Visualitzacions interactives
- **pandas** — Manipulació de dades
- **scikit-learn** — Machine Learning

## 📁 Estructura

```
OptiSolarAI/
├── app.py            # Aplicació principal
├── database.py       # Capa de dades
├── ml_engine.py      # Motor ML
├── logic.py          # Lògica de negoci
├── config.py         # Configuració
├── utils.py          # Utilitats
├── data/             # BD DuckDB
├── models/           # Models ML
└── docs/             # Documentació
```

## 📄 Llicència

Projecte educatiu — UD1B Ciència de Dades

---

> **Nota:** Aquest projecte utilitza dades sintètiques per a demostració. Per a ús real, integra APIs de preus de llum (OMIE, REE) i meteorologia (OpenWeatherMap).
