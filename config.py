"""
config.py - Configuración del Proyecto
OptiSolarAI - Parámetros Centralizados
"""

# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================

DB_PATH = "data/optisolar.duckdb"
DB_BACKUP_PATH = "data/backups/"


# ============================================================================
# CONFIGURACIÓN DE MODELOS ML
# ============================================================================

MODEL_PATH = "models/solar_predictor.pkl"
MODEL_PARAMS = {
    'n_estimators': 100,
    'max_depth': 15,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42
}


# ============================================================================
# CONFIGURACIÓN DE BATERÍA
# ============================================================================

BATERIA_CONFIG = {
    'capacidad_default': 10.0,      # kWh
    'carga_inicial_pct': 50,        # %
    'eficiencia_carga': 0.95,       # 95%
    'eficiencia_descarga': 0.95,    # 95%
    'precio_venta_factor': 0.8,     # 80% del precio de compra
    'vida_util_ciclos': 5000        # ciclos de vida útil
}


# ============================================================================
# CONFIGURACIÓN DE CONSUMO
# ============================================================================

CONSUMO_CONFIG = {
    'consumo_base_kwh': 2.0,        # kWh por hora
    'consumo_minimo': 0.5,          # kWh
    'consumo_maximo': 5.0           # kWh
}


# ============================================================================
# CONFIGURACIÓN DE API EXTERNA
# ============================================================================

OPENWEATHER_CONFIG = {
    'api_key': 'YOUR_API_KEY_HERE',
    'ciudad_default': 'Madrid',
    'unidades': 'metric',
    'timeout': 10                   # segundos
}


# ============================================================================
# CONFIGURACIÓN DE VISUALIZACIÓN
# ============================================================================

PLOTLY_THEME = "plotly_white"
COLOR_PALETTE = {
    'produccion': 'gold',
    'precio': '#FF9500',
    'bateria': 'green',
    'beneficio': 'blue',
    'temperatura': 'red',
    'nubosidad': 'gray'
}


# ============================================================================
# CONFIGURACIÓN DE FECHAS
# ============================================================================

from datetime import datetime, timedelta

FECHA_INICIO_DEFAULT = datetime(2026, 2, 1)
FECHA_FIN_DEFAULT = datetime(2026, 2, 7)
DIAS_HISTORICO = 7
DIAS_PRONOSTICO = 5


# ============================================================================
# CONFIGURACIÓN DE PRECIOS
# ============================================================================

PRECIOS_CONFIG = {
    'precio_min': 0.05,             # €/kWh
    'precio_max': 0.30,             # €/kWh
    'precio_medio': 0.12,           # €/kWh
    'umbral_precio_bajo': 0.85,    # 85% del precio medio
    'umbral_precio_alto': 1.15     # 115% del precio medio
}


# ============================================================================
# CONFIGURACIÓN FINANCIERA
# ============================================================================

FINANCIERO_CONFIG = {
    'inversion_inicial_default': 15000.0,   # €
    'vida_util_anos': 25,                   # años
    'beneficio_anual_estimado': 1200.0,     # €/año
    'tasa_descuento': 0.03                  # 3%
}


# ============================================================================
# MENSAJES Y TEXTOS
# ============================================================================

MENSAJES = {
    'carga_datos_exito': ' Datos cargados correctamente',
    'modelo_entrenado': ' Modelo entrenado exitosamente',
    'simulacion_completada': ' Simulación completada',
    'error_datos': ' No hay datos disponibles',
    'error_modelo': ' Error al cargar el modelo',
}


# ============================================================================
# VALIDACIONES
# ============================================================================

def validar_capacidad_bateria(capacidad: float) -> bool:
    """Valida que la capacidad de batería esté en un rango razonable"""
    return 1.0 <= capacidad <= 50.0


def validar_rango_fechas(fecha_inicio, fecha_fin) -> bool:
    """Valida que el rango de fechas sea válido"""
    return fecha_inicio < fecha_fin


def validar_precio(precio: float) -> bool:
    """Valida que el precio esté en un rango razonable"""
    return PRECIOS_CONFIG['precio_min'] <= precio <= PRECIOS_CONFIG['precio_max']
