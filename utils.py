"""
utils.py - Funciones Utilitarias
OptiSolarAI - Helpers y Utilidades Generales
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import streamlit as st


def formatear_fecha(fecha: datetime, formato: str = "%d/%m/%Y %H:%M") -> str:
    """
    Formatea una fecha al formato español.
    
    Args:
        fecha: Objeto datetime
        formato: String de formato
    
    Returns:
        str: Fecha formateada
    """
    return fecha.strftime(formato)


def calcular_estadisticas(serie: pd.Series) -> Dict:
    """
    Calcula estadísticas descriptivas de una serie.
    
    Args:
        serie: Serie de pandas
    
    Returns:
        dict: Estadísticas (media, mediana, min, max, std)
    """
    return {
        'media': serie.mean(),
        'mediana': serie.median(),
        'minimo': serie.min(),
        'maximo': serie.max(),
        'desviacion': serie.std(),
        'q25': serie.quantile(0.25),
        'q75': serie.quantile(0.75)
    }


def convertir_a_hora_solar(hora_utc: int, zona_horaria: str = 'Europe/Madrid') -> int:
    """
    Convierte hora UTC a hora solar local.
    
    Args:
        hora_utc: Hora en UTC (0-23)
        zona_horaria: Zona horaria destino
    
    Returns:
        int: Hora local
    """
    import pytz
    tz = pytz.timezone(zona_horaria)
    ahora = datetime.now(tz)
    offset = ahora.utcoffset().total_seconds() / 3600
    return int((hora_utc + offset) % 24)


def crear_rango_fechas(fecha_inicio: datetime, 
                       fecha_fin: datetime, 
                       frecuencia: str = 'H') -> List[datetime]:
    """
    Crea un rango de fechas con la frecuencia especificada.
    
    Args:
        fecha_inicio: Fecha de inicio
        fecha_fin: Fecha de fin
        frecuencia: 'H' (horaria), 'D' (diaria), etc.
    
    Returns:
        List[datetime]: Lista de fechas
    """
    return pd.date_range(start=fecha_inicio, end=fecha_fin, freq=frecuencia).tolist()


def validar_dataframe(df: pd.DataFrame, columnas_requeridas: List[str]) -> bool:
    """
    Valida que un DataFrame tenga las columnas requeridas.
    
    Args:
        df: DataFrame a validar
        columnas_requeridas: Lista de columnas que debe tener
    
    Returns:
        bool: True si es válido
    """
    return all(col in df.columns for col in columnas_requeridas)


def interpolar_datos_faltantes(df: pd.DataFrame, 
                               columna: str, 
                               metodo: str = 'linear') -> pd.DataFrame:
    """
    Interpola datos faltantes en una columna.
    
    Args:
        df: DataFrame
        columna: Nombre de la columna
        metodo: Método de interpolación
    
    Returns:
        pd.DataFrame: DataFrame con datos interpolados
    """
    df[columna] = df[columna].interpolate(method=metodo)
    return df


def calcular_ahorro_co2(kwh_solar: float, factor_emision: float = 0.25) -> float:
    """
    Calcula el ahorro de CO2 por uso de energía solar.
    
    Args:
        kwh_solar: kWh de energía solar producida
        factor_emision: kg CO2 por kWh de red eléctrica
    
    Returns:
        float: kg de CO2 ahorrados
    """
    return kwh_solar * factor_emision


def crear_tabla_resumen(datos: Dict) -> pd.DataFrame:
    """
    Crea una tabla resumen a partir de un diccionario.
    
    Args:
        datos: Diccionario con los datos
    
    Returns:
        pd.DataFrame: Tabla formateada
    """
    df = pd.DataFrame(list(datos.items()), columns=['Métrica', 'Valor'])
    return df


@st.cache_data(ttl=3600)
def cargar_datos_cache(ruta: str) -> pd.DataFrame:
    """
    Carga datos con caché de Streamlit.
    
    Args:
        ruta: Ruta al archivo
    
    Returns:
        pd.DataFrame: Datos cargados
    """
    if ruta.endswith('.csv'):
        return pd.read_csv(ruta)
    elif ruta.endswith('.json'):
        return pd.read_json(ruta)
    else:
        raise ValueError("Formato no soportado")


def generar_colores_gradiente(n: int, 
                             color_inicio: str = '#FFD700',
                             color_fin: str = '#FF6347') -> List[str]:
    """
    Genera una lista de colores en gradiente.
    
    Args:
        n: Número de colores
        color_inicio: Color inicial (hex)
        color_fin: Color final (hex)
    
    Returns:
        List[str]: Lista de colores en hex
    """
    import matplotlib.colors as mcolors
    cmap = mcolors.LinearSegmentedColormap.from_list("custom", [color_inicio, color_fin])
    return [mcolors.to_hex(cmap(i/n)) for i in range(n)]


def exportar_a_excel(dataframes: Dict[str, pd.DataFrame], ruta: str):
    """
    Exporta múltiples DataFrames a un archivo Excel con hojas separadas.
    
    Args:
        dataframes: Diccionario {nombre_hoja: DataFrame}
        ruta: Ruta del archivo de salida
    """
    with pd.ExcelWriter(ruta, engine='openpyxl') as writer:
        for nombre_hoja, df in dataframes.items():
            df.to_excel(writer, sheet_name=nombre_hoja, index=False)


def calcular_percentil_consumo(consumo: float, consumos_historicos: pd.Series) -> int:
    """
    Calcula en qué percentil está un consumo respecto al histórico.
    
    Args:
        consumo: Consumo actual
        consumos_historicos: Serie con consumos históricos
    
    Returns:
        int: Percentil (0-100)
    """
    return int((consumos_historicos < consumo).sum() / len(consumos_historicos) * 100)


def crear_notificacion(tipo: str, mensaje: str):
    """
    Crea una notificación en Streamlit.
    
    Args:
        tipo: 'success', 'error', 'warning', 'info'
        mensaje: Mensaje a mostrar
    """
    if tipo == 'success':
        st.success(mensaje)
    elif tipo == 'error':
        st.error(mensaje)
    elif tipo == 'warning':
        st.warning(mensaje)
    else:
        st.info(mensaje)


def generar_reporte_html(titulo: str, contenido: Dict) -> str:
    """
    Genera un reporte HTML simple.
    
    Args:
        titulo: Título del reporte
        contenido: Diccionario con secciones y contenido
    
    Returns:
        str: HTML del reporte
    """
    html = f"""
    <html>
    <head>
        <title>{titulo}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #FF9500; }}
            .metric {{ background: #f0f2f6; padding: 15px; margin: 10px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>{titulo}</h1>
    """
    
    for seccion, valores in contenido.items():
        html += f"<h2>{seccion}</h2>"
        for clave, valor in valores.items():
            html += f'<div class="metric"><strong>{clave}:</strong> {valor}</div>'
    
    html += "</body></html>"
    return html


def redondear_a_precision(numero: float, precision: int = 2) -> float:
    """
    Redondea un número a una precisión específica.
    
    Args:
        numero: Número a redondear
        precision: Número de decimales
    
    Returns:
        float: Número redondeado
    """
    return round(numero, precision)


def calcular_tendencia(serie: pd.Series, ventana: int = 24) -> str:
    """
    Calcula la tendencia de una serie temporal.
    
    Args:
        serie: Serie de valores
        ventana: Ventana para calcular la tendencia
    
    Returns:
        str: 'alcista', 'bajista' o 'estable'
    """
    if len(serie) < ventana:
        return 'insuficientes datos'
    
    media_reciente = serie.tail(ventana).mean()
    media_anterior = serie.head(ventana).mean()
    
    diferencia_pct = ((media_reciente - media_anterior) / media_anterior) * 100
    
    if diferencia_pct > 5:
        return 'alcista '
    elif diferencia_pct < -5:
        return 'bajista '
    else:
        return 'estable '
