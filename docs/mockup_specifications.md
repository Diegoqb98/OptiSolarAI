# Especificaciones Detalladas de Mockups para OptiSolarAI

## 📋 Instrucciones para generar con IA

Copia y pega cada sección en una IA generadora de imágenes (ChatGPT con DALL-E, Midjourney, Leonardo AI, etc.) usando este prompt:

```
Crea un mockup moderno y profesional de una aplicación web para [descripción de la pantalla]. 
Estilo: Interfaz limpia, colores verde/azul/blanco, diseño dashboard moderno.
```

---

## 🏠 PANTALLA 1: Home - Resumen General (Página de Inicio)

### Prompt para la IA:

```
Crea un mockup profesional de una aplicación web dashboard llamada "OptiSolarAI" para gestión de energía solar. 

ESTILO VISUAL:
- Fondo: Verde oscuro profundo (#1a3a2e o similar a forest green dark)
- Sidebar izquierda oscura con menú
- Cards con fondo semi-transparente verde oscuro
- Texto en color claro/blanco
- Estilo similar a un dashboard financiero moderno

ESTRUCTURA:

SIDEBAR IZQUIERDA (20% ancho, fondo más oscuro):
- Logo "OptiSolarAI" arriba con icono de sol/hoja
- Menú vertical:
  🏠 Home (resaltado en verde más claro)
  📊 Datos
  📈 Análisis  
  ⚙️ Configuración
  ℹ️ Información
- Abajo: "Última actualización: 08:25 - 03/12/25"

ÁREA PRINCIPAL (80% ancho, fondo verde oscuro):

HEADER:
- Título grande: "Resumen del Sistema - Hoy: 03/12/25"
- Subtítulo en azul claro: "Estado actual de producción y consumo"

SECCIÓN SUPERIOR - 4 CARDS GRANDES EN FILA:

1. Card "Producción Solar Hoy":
   - Icono de sol amarillo
   - Número grande: "28.5 kWh"
   - Indicador: ↑ +12.3% vs ayer
   - Fondo: Verde oscuro con borde sutil

2. Card "Consumo Total":
   - Icono de casa/rayo
   - Número grande: "21.8 kWh"  
   - Indicador: ↓ -5.2% vs ayer
   - Fondo: Verde oscuro con borde sutil

3. Card "Estado Batería":
   - Icono batería con 75%
   - Texto: "Cargando"
   - Potencia: "2.5 kW"
   - Barra de progreso verde brillante

4. Card "Ahorro del Día":
   - Icono de moneda/euro
   - Número grande verde brillante: "+12.50€"
   - Texto: "vs consumo red"
   - Indicador: ↑ +4.39%

SECCIÓN CENTRAL - 2 CARDS HORIZONTALES:

5. Card "Precio Actual Electricidad":
   - Título: "Tarifa Eléctrica Actual"
   - Número destacado: "0.18 €/kWh"
   - Estado: "PRECIO MEDIO" (en amarillo)
   - Recomendación: "Momento óptimo para autoconsumo"
   - Mini línea temporal con previsión de precios

6. Card "Energía Vendida a Red":
   - Título: "Excedente Vendido Hoy"
   - Número: "6.7 kWh"
   - Ingresos: "+1.20€"
   - Estado: Verde brillante "ACTIVO"

ESTILO DETALLADO:
- Fondo principal: #1a3a2e (verde oscuro bosque)
- Cards: rgba(255,255,255,0.05) con borde rgba(255,255,255,0.1)
- Números grandes: Blancos o verde brillante (#4ade80)
- Indicadores positivos: Verde brillante
- Indicadores negativos: Rojo suave
- Iconos: Estilo minimalista, colores suaves
- Tipografía: Sans-serif moderna (Inter, Poppins)
- Sin gráficos en esta pantalla (solo números y cards)
```

---

## ⚙️ PANTALLA 3: Configuración del Sistema

### Prompt para la IA:

```
Crea un mockup de la pantalla de configuración de OptiSolarAI, estilo dashboard oscuro profesional.

ESTILO VISUAL:
- Fondo: Verde oscuro profundo (#1a3a2e)
- Sidebar izquierda igual que otras pantallas
- Formularios con inputs modernos oscuros

SIDEBAR IZQUIERDA:
- Logo "OptiSolarAI"
- Menú con "⚙️ Configuración" resaltado
- Última actualización abajo

ÁREA PRINCIPAL:

HEADER:
- Título: "⚙️ Configuración del Sistema"
- Subtítulo: "Personaliza los parámetros de tu instalación solar"

CONTENIDO (FORMULARIO EN 2 COLUMNAS):

COLUMNA IZQUIERDA:

1. Card "Batería":
   - Fondo verde oscuro semi-transparente
   - Input: "Capacidad total (kWh)" → valor: 10
   - Slider oscuro: "Reserva mínima (%)" → 20%
   - Input: "Potencia máx carga/descarga (kW)" → 5

2. Card "Tarifas Eléctricas":
   - Dropdown: "Tipo de tarifa" → [2.0 TD | 3.0 TD]
   - Tabla pequeña con períodos:
     * Punta: 0.25 €/kWh
     * Llano: 0.18 €/kWh  
     * Valle: 0.10 €/kWh
   - Botón secundario: "Editar"

3. Card "Paneles Solares":
   - Input: "Potencia instalada (kWp)" → 5.2
   - Input: "Orientación" → Sur
   - Input: "Inclinación (°)" → 30

COLUMNA DERECHA:

4. Card "Consumo Habitual":
   - Mini gráfico de barras (consumo por hora)
   - Input: "Consumo base (kW)" → 0.5
   - Toggle switch: "Aprendizaje automático" (ON)

5. Card "Límites de Venta":
   - Checkbox: "Permitir venta a red" ✓
   - Input: "Precio mín venta (€/kWh)" → 0.08
   - Input: "Potencia máx venta (kW)" → 3

6. Card "Ubicación":
   - Input con icono: "Ciudad" → Valencia, España
   - Estado API: "✓ Conectada" (verde)
   - Botón: "Actualizar datos"

PARTE INFERIOR:
- Botón grande verde brillante: "💾 Guardar Configuración"
- Botón secundario gris: "Restaurar defaults"

ESTILO INPUTS:
- Fondo oscuro con borde sutil
- Texto blanco
- Focus en verde brillante
- Sliders y toggles con color verde
- Dropdowns estilo moderno
```

---

## 📊 PANTALLA 2: Análisis - Gráficos y Datos (Página de Análisis)

### Prompt para la IA:

```
Crea un mockup de la pantalla de análisis con gráficos de OptiSolarAI, estilo dashboard oscuro profesional.

ESTILO VISUAL:
- Fondo: Verde oscuro profundo (#1a3a2e)
- Sidebar izquierda igual que pantalla 1
- Gráficos con fondo semi-transparente
- Esta pantalla SÍ tiene gráficos grandes

SIDEBAR IZQUIERDA (igual que pantalla 1):
- Logo "OptiSolarAI"
- Menú con "📈 Análisis" resaltado en verde
- Última actualización abajo

ÁREA PRINCIPAL:

HEADER:
- Título: "Análisis de Producción y Consumo"
- Selector de período: [Hoy | Semana | Mes | Año] - "Semana" seleccionado
- Fecha: "Semana del 27/11 al 03/12/25"

GRÁFICO PRINCIPAL (ocupa 70% del ancho superior):
- Card grande con fondo verde oscuro semi-transparente
- Título: "Producción Solar vs Consumo - Últimos 7 días"
- GRÁFICO DE LÍNEAS GRANDE:
  * Línea amarilla/dorada: "Producción Solar" (curva suave)
  * Línea azul clara: "Consumo" (curva irregular)
  * Área sombreada verde: zona de excedente
  * Ejes con labels en blanco/gris claro
  * Grid sutil en gris oscuro
  * Leyenda arriba a la derecha
- Estilo: Gráfico moderno estilo Chart.js/Plotly con fondo transparente

GRÁFICO SECUNDARIO (abajo del principal, 70% ancho):
- Card con título: "Distribución Energética Diaria"
- GRÁFICO DE BARRAS APILADAS:
  * Eje X: Días de la semana (Lun, Mar, Mié, Jue, Vie, Sáb, Dom)
  * Barras con 3 segmentos apilados:
    - Verde brillante: Autoconsumo
    - Amarillo: Vendido a red
    - Azul: Almacenado en batería
  * Altura de barras variable por día
  * Leyenda abajo del gráfico

PANEL LATERAL DERECHO (30% ancho):

1. Card "Totales de la Semana":
   - Fondo verde oscuro con borde
   - Producción total: "187 kWh"
   - Consumo total: "142 kWh"
   - Excedente: "45 kWh"
   - Indicadores con iconos pequeños

2. Card "Estadísticas":
   - Promedio diario producción: "26.7 kWh"
   - Mejor día: "Lunes 28 kWh"
   - Peor día: "Jueves 21 kWh"
   - Autosuficiencia: "85%"

3. GRÁFICO CIRCULAR pequeño:
   - Título: "Uso de Energía"
   - Segmentos:
     * Verde 60%: Autoconsumo
     * Amarillo 25%: Vendido
     * Azul 15%: Almacenado
   - Leyenda con porcentajes

PARTE INFERIOR:
- Card horizontal: "Previsión próximos 3 días"
- Mini gráfico de barras con predicción
- Texto: "Producción estimada: 78-82 kWh"

ESTILO DETALLADO:
- Todos los gráficos con aspecto moderno y profesional
- Colores vivos sobre fondo oscuro (alto contraste)
- Grid de gráficos en gris muy oscuro (#2a4a3e)
- Labels y texto en blanco/gris claro
- Sin bordes gruesos, todo sutil
- Números grandes y legibles
- Similar a dashboards de Bloomberg o Grafana
```

---

## 🎨 Paleta de Colores General

```
ESTILO OSCURO (Como las capturas que enviaste):

Fondos:
- Fondo principal: #1a3a2e (verde oscuro bosque)
- Sidebar: #142a22 (verde más oscuro)
- Cards: rgba(255,255,255,0.05) con borde rgba(255,255,255,0.1)

Textos:
- Texto principal: #ffffff (blanco)
- Texto secundario: #a0aec0 (gris claro)
- Números destacados: #4ade80 (verde brillante)

Colores de datos:
- Producción Solar: #fbbf24 (amarillo/dorado brillante)
- Energía Verde/Autoconsumo: #4ade80 (verde brillante)
- Batería/Almacenamiento: #60a5fa (azul brillante)
- Venta a Red: #fb923c (naranja)
- Compra de Red: #f87171 (rojo suave)

Indicadores:
- Positivo/Subida: #4ade80 (verde brillante)
- Negativo/Bajada: #f87171 (rojo suave)
- Neutro/Info: #60a5fa (azul)

UI Elements:
- Botón primario: #4ade80 (verde brillante)
- Botón secundario: rgba(255,255,255,0.1)
- Input background: rgba(0,0,0,0.3)
- Input border: rgba(255,255,255,0.2)
- Hover: rgba(255,255,255,0.1)
```

---

## 📝 Instrucciones de Uso

1. Copia cada prompt (PANTALLA 1, 2 o 3)
2. Pégalo en ChatGPT-4 con DALL-E, Leonardo AI, Midjourney, o similar
3. Ajusta detalles si es necesario
4. Descarga las imágenes generadas
5. Guárdalas en `C:\OptiSolarAI\docs\wireframes\` con nombres:
   - `mockup_dashboard.png`
   - `mockup_configuracion.png`
   - `mockup_resultados.png`

---

## 🔧 Alternativa: Herramientas recomendadas

Si prefieres crear tú mismo:
- **Figma**: Más control y profesional
- **Canva**: Plantillas de dashboard listas
- **Excalidraw**: Wireframes rápidos y simples
- **Balsamiq**: Wireframes clásicos

---

**Nota:** Estos mockups son para la entrega UT0B. En fases posteriores se desarrollará la interfaz real en Streamlit.
