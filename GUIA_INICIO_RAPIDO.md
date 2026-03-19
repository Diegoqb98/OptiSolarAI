#  Guía de Inicio Rápido - OptiSolarAI

##  Instalación en 3 Pasos

### 1 Preparar el Entorno

```powershell
# Navegar al directorio del proyecto
cd C:\OptiSolarAI

# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
.\venv\Scripts\Activate.ps1
```

### 2 Instalar Dependencias

```powershell
pip install -r requirements.txt
```

### 3 Ejecutar la Aplicación

```powershell
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

---

##  Primeros Pasos en la Aplicación

### Paso 1: Cargar Datos de Ejemplo

1. En el **sidebar izquierdo**, busca la sección " Acciones"
2. Haz clic en el botón **" Cargar Datos de Ejemplo"**
3. Verás un mensaje de éxito: " 168 registros cargados"

> Esto generará 7 días de datos sintéticos (precios, producción solar y clima)

### Paso 2: Entrenar el Modelo ML

1. Justo debajo del botón anterior, haz clic en **" Entrenar Modelo ML"**
2. Espera unos segundos mientras se entrena
3. Verás: " Modelo entrenado - R Score: X.XXX"

> El modelo Random Forest aprenderá a predecir producción solar basándose en el clima

### Paso 3: Explorar el Dashboard

####  Tab "Dashboard General"
- Visualiza KPIs: Precio Medio, Producción Total, Temperatura, Nubosidad
- Revisa gráficos de precios y producción solar
- Analiza correlaciones climáticas

####  Tab "Simulación de Batería"
1. Ajusta los parámetros:
   - **Capacidad Batería**: 10 kWh (por defecto)
   - **Carga Inicial**: 5 kWh
   - **Consumo Base**: 2 kWh/h
2. Haz clic en **" Ejecutar Simulación"**
3. Analiza los resultados:
   - Beneficio Total y Diario
   - Estado de la Batería (gráfico)
   - Recomendaciones inteligentes

####  Tab "Predicciones ML"
1. Introduce valores climáticos:
   - Temperatura: 25C
   - Nubosidad: 30%
   - Humedad: 50%
   - Radiación: 600 W/m
2. Haz clic en **" Predecir Producción"**
3. Obtén la producción solar estimada

####  Tab "Análisis Financiero"
1. Introduce:
   - Inversión Inicial: 15,000€
   - Beneficio Anual: 1,200€
   - Vida Útil: 25 años
2. Haz clic en **" Calcular ROI"**
3. Revisa:
   - ROI total
   - Periodo de Payback
   - Proyección financiera

---

##  Configuración Personalizada

### Cambiar Parámetros en el Sidebar

- **Rango de Fechas**: Selecciona el periodo a analizar
- **Capacidad de Batería**: 5-20 kWh
- **Carga Inicial**: 0-100%
- **Consumo Base**: 1-5 kWh/h

### Modificar Configuración Avanzada

Edita el archivo `config.py` para cambiar:
- Eficiencias de carga/descarga
- Factor de precio de venta
- Parámetros del modelo ML
- Colores del dashboard

---

##  Solución de Problemas

### Error: "No hay datos disponibles"
**Solución**: Haz clic en " Cargar Datos de Ejemplo" en el sidebar

### Error: "Modelo no entrenado"
**Solución**: Haz clic en " Entrenar Modelo ML" después de cargar datos

### Error al instalar dependencias
**Solución**: 
```powershell
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### Puerto 8501 ocupado
**Solución**: 
```powershell
streamlit run app.py --server.port 8502
```

---

##  Estructura de Datos

### Tablas en DuckDB

1. **precios_luz**
   - fecha_hora (TIMESTAMP)
   - precio_kwh (FLOAT)

2. **produccion_solar**
   - fecha_hora (TIMESTAMP)
   - produccion_kwh (FLOAT)
   - radiacion (FLOAT)

3. **clima**
   - fecha_hora (TIMESTAMP)
   - temperatura (FLOAT)
   - nubosidad (INTEGER)
   - humedad (INTEGER)

4. **simulaciones_bateria**
   - id (INTEGER)
   - fecha_creacion (TIMESTAMP)
   - capacidad_bateria (FLOAT)
   - resultados (TEXT)

---

##  Casos de Uso

### 1. Analizar Rentabilidad
1. Cargar datos de tu instalación real
2. Ejecutar simulación con tus parámetros
3. Revisar análisis financiero (Tab 4)

### 2. Optimizar Uso de Batería
1. Probar diferentes capacidades de batería
2. Comparar beneficios en simulaciones
3. Seguir recomendaciones del sistema

### 3. Predecir Producción
1. Obtener pronóstico meteorológico
2. Usar Tab 3 para predecir producción
3. Planificar consumo/venta de energía

---

##  Próximos Pasos

1. **Integra Datos Reales**: Conecta APIs de precios de luz y meteorología
2. **Exporta Reportes**: Usa `utils.py` para generar reportes HTML
3. **Crea Alertas**: Implementa notificaciones cuando el precio sea óptimo
4. **Mejora el Modelo**: Entrena con más datos históricos

---

##  Soporte

Para más información, consulta:
- `README.md`: Documentación completa
- `config.py`: Parámetros configurables
- `utils.py`: Funciones auxiliares disponibles

---

**¡Disfruta optimizando tu energía solar! **
