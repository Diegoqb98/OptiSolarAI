# Documentació Tècnica — UD1B
## OptiSolarAI — Consolidació del Desenvolupament

**Data:** Març 2026
**Autor:** Projecte Intermodular — Ciència de Dades
**Versió:** 2.0 (UD1B)

---

## 1. Evolució respecte a UD1A

| Aspecte | UD1A | UD1B |
|---|---|---|
| Tabs de l'aplicació | 4 | **6** |
| Dies de dades d'exemple | 7 dies | **30 dies** |
| Funcionalitats core | Dashboard, Bateria, ML, Financer | + **Previsió 7 Dies**, **Monitor Consum** |
| Taules BD | 4 | **5** (`registre_consum`) |
| Disseny visual | CSS bàsic | **Glassmorphism + gradient fosc** |
| Gestió d'errors | Bàsica | **Try/except + valors per defecte** |

---

## 2. Noves Funcionalitats Core

### 2.1 Previsió Solar 7 Dies (`tabs5` a `app.py`)

**Descripció:** Genera un pronòstic de producció solar per als propers 7 dies, classificant cada dia per qualitat (Excel·lent / Bona / Moderada / Baixa).

**Decisions tècniques:**
- La funció `generar_pronostico_7dias()` a `ml_engine.py` utilitza el model Random Forest entrenat si existeix. En cas contrari, aplica una estimació heurística basada en la corba sinusoïdal de radiació solar (`sin((hora-6) * π/12)`).
- La seed aleatòria es fixa per dia de l'any (`datetime.now().strftime('%j')`), de manera que el pronòstic és consistent durant el mateix dia però varia entre dies.
- La classificació de qualitat usa llindars fixos (≥35 kWh = Excel·lent, ≥25 = Bona, ≥15 = Moderada, <15 = Baixa).

**Valor afegit:** 
- Alerta intel·ligent del millor dia per vendre energia i del pitjor dia (per carregar la bateria).
- Gràfic de barres amb codi de colors per qualitat.

**Problemes trobats i solucions:**
- *Problema:* El pronòstic era diferent cada recarrega perquè la seed era completament aleatòria.  
  *Solució:* Seed basada en el dia de l'any, mantenint consistència dins del mateix dia.

---

### 2.2 Monitor de Consum del Llar (`tab6` a `app.py`)

**Descripció:** Permet registrar, visualitzar i analitzar el consum energètic per electrodomèstic i categoria, amb comparativa solar vs xarxa.

**Decisions tècniques:**
- **Nova taula BD** `registre_consum` amb camps: `id`, `data`, `hora`, `categoria`, `electrodomestic`, `kwh`, `hora_punta`.
- **Arquitectura CRUD**: Funcions `insert_consum()`, `delete_consum()`, `get_consum_per_periode()`, `get_consum_per_categoria()` a `database.py`.
- **Comparativa solar vs xarxa**: Calcula el % d'energia del llar coberta per la producció solar del rang de dates seleccionat al sidebar. Si la producció > consum, el 100% és solar; si no, proporcional.
- **Cost estimat**: Multiplicant l'energia comprada de la xarxa per un preu de referència de 0,14 €/kWh.

**Problemes trobats i solucions:**
- *Problema:* El formulari de registre recarregava tota la pàgina en afegir un registre, perdent el context d'altres tabs.  
  *Solució:* Ús de `st.rerun()` (Streamlit ≥1.18) que és la forma correcta per actualitzar l'estat sense navegació.

- *Problema:* La taula `registre_consum` no existia a la BD de la UD1A.  
  *Solució:* El sistema de `CREATE TABLE IF NOT EXISTS` a `_initialize_tables()` afegeix la taula automàticament si no existeix, mantenint compatibilitat retroactiva.

---

## 3. Millores Transversals

### 3.1 Ampliació de Dades d'Exemple (7 → 30 dies)

**Motivació:** 7 dies de dades eren insuficients per entrenar un model ML robust i per fer anàlisis estadísticament significatives.

**Implementació:**
- `cargar_datos_ejemplo()` ara genera 720 registres (30 × 24h).
- S'afegeix una variació sinusoïdal mensual als preus i a la producció solar per simular tendències realistes.
- La nuvolositat segueix una distribució Beta(2,3) en comptes de la distribució uniforme anterior, generant dies majoritàriament clars amb pics de nuvolositat menys freqüents (més realista).

### 3.2 Disseny Visual Modern

**Motivació:** La UD1A tenia un disseny funcional però basic. La UD1B introdueix un aspecte de producte professional.

**Elements implementats:**
- Fons amb gradient fosc (`#0f0c29 → #24243e`).
- Efecte glassmorphism a les cards (blur + border semi-transparent).
- Tipografia Inter (Google Fonts).
- Plotly charts amb fons transparent per integrar-se al tema fosc.
- Indicador dinàmic del **Mode Energètic Actual** al sidebar (basat en l'hora del dia).
- KPIs amb deltes (variació respecte a referència).

### 3.3 Gestió d'Errors Robusta

**Motivació:** A la UD1A, qualsevol error en una query de BD o funció ML provocava un crash visible de tota la pàgina.

**Implementació:**  
Totes les funcions `get_*()` a `database.py` estan envoltades en blocs `try/except` que retornen DataFrames buits amb l'esquema correcte, permettent que l'app mostri un missatge amigable en lloc d'un error cru.

---

## 4. Arquitectura Actualitzada

```
OptiSolarAI/
├── app.py              # Dashboard principal (6 tabs)
│                       #  Tab 1: Dashboard General
│                       #  Tab 2: Simulació Bateria
│                       #  Tab 3: Prediccions ML
│                       #  Tab 4: Anàlisi Financer
│                       #  Tab 5: Previsió 7 Dies [NOU]
│                       #  Tab 6: Monitor Consum Llar [NOU]
│
├── database.py         # Capa de dades (DuckDB)
│                       #  5 taules: precios_luz, produccion_solar,
│                       #            clima, simulaciones_bateria,
│                       #            registre_consum [NOU]
│
├── ml_engine.py        # Motor ML (Random Forest)
│                       #  SolarPredictor (entrenar/predir)
│                       #  generar_pronostico_7dias() [NOU]
│                       #  OpenWeatherAPIClient
│
├── logic.py            # Lògica de negoci
│                       #  SimuladorBateria
│                       #  OptimizadorTarifas
│                       #  generar_recomendaciones()
│
├── config.py           # Configuració centralitzada
├── utils.py            # Utilitats generals
│
├── data/               # BD DuckDB
│   └── optisolar.duckdb
│
├── models/             # Models ML serialitzats
│   └── solar_predictor.pkl
│
└── docs/               # Documentació tècnica
    ├── UD1B_documentacion_tecnica.md  [NOU]
    ├── ESTRUCTURA.md
    ├── mockup_specifications.md
    └── trello_board_structure.md
```

### Flux de dades

```
Fonts de dades                 Capa lògica              Presentació
──────────────                 ───────────              ───────────
cargar_datos_ejemplo()   →     database.py      →       app.py (Tabs 1-4)
generar_pronostico_7dias() →   ml_engine.py     →       app.py (Tab 5)
insert_consum()          →     database.py      →       app.py (Tab 6)
```

---

## 5. Gestió del Projecte

### Commits descriptius realitzats:
- `feat: UD1B - add 7-day solar forecast tab with ML predictions`
- `feat: UD1B - add home consumption monitor with CRUD operations`
- `feat: UD1B - expand sample data from 7 to 30 days`
- `style: UD1B - dark glassmorphism design overhaul`
- `refactor: UD1B - add robust error handling to all DB queries`
- `docs: UD1B - technical documentation update`

### Trello:
La columna **En Curs** s'ha de moure a **Completat**:
- Previsió solar 7 dies
- Monitor de consum del llar
- Millora visual UD1B

---

## 6. Decisions Tècniques Justificades

| Decisió | Alternativa considerada | Justificació |
|---|---|---|
| Streamlit multipage via Tabs | Streamlit `pages/` multipage | Els Tabs mantenen l'estat de tota l'app i eviten recàrregues entre seccions |
| DuckDB com a BD | SQLite | DuckDB és natiu per a anàlisi columnar i DataFrames pandas, més eficient per a consultes agregades |
| Random Forest per a predicció | Regressió lineal | RF tolera bé la no-linealitat de la radiació solar i no requereix normalització |
| Seed per dia de l'any al pronòstic | Seed fixa | Resultat consistent dins del dia però evolutiu entre dies |
| `try/except` a totes les funcions BD | Deixar que els errors propaguin | L'app ha de ser robusta per a demostracions en classe sense setup perfecte |
