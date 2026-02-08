"""
database.py - Gestión de Base de Datos con DuckDB
OptiSolarAI - Sistema de Gestión de Energía Solar
"""

import duckdb
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path


@st.cache_resource
def get_database_connection():
    """
    Crea y retorna una conexión persistente a DuckDB.
    Utiliza st.cache_resource para mantener la conexión activa entre reruns.
    """
    db_path = Path("data/optisolar.duckdb")
    db_path.parent.mkdir(exist_ok=True)
    
    conn = duckdb.connect(str(db_path))
    _initialize_tables(conn)
    return conn


def _initialize_tables(conn):
    """
    Inicializa las tablas necesarias si no existen.
    """
    # Tabla de precios de luz por hora
    conn.execute("""
        CREATE TABLE IF NOT EXISTS precios_luz (
            fecha_hora TIMESTAMP,
            precio_kwh FLOAT,
            PRIMARY KEY (fecha_hora)
        )
    """)
    
    # Tabla de producción solar real
    conn.execute("""
        CREATE TABLE IF NOT EXISTS produccion_solar (
            fecha_hora TIMESTAMP,
            produccion_kwh FLOAT,
            radiacion FLOAT,
            PRIMARY KEY (fecha_hora)
        )
    """)
    
    # Tabla de datos climáticos
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clima (
            fecha_hora TIMESTAMP,
            temperatura FLOAT,
            nubosidad INTEGER,
            humedad INTEGER,
            PRIMARY KEY (fecha_hora)
        )
    """)
    
    # Tabla de simulaciones de batería
    conn.execute("""
        CREATE TABLE IF NOT EXISTS simulaciones_bateria (
            id INTEGER PRIMARY KEY,
            fecha_creacion TIMESTAMP,
            capacidad_bateria FLOAT,
            carga_inicial FLOAT,
            resultados TEXT
        )
    """)


def insert_precios_luz(df: pd.DataFrame):
    """
    Inserta o actualiza datos de precios de luz.
    
    Args:
        df: DataFrame con columnas ['fecha_hora', 'precio_kwh']
    """
    conn = get_database_connection()
    conn.execute("INSERT OR REPLACE INTO precios_luz SELECT * FROM df")


def insert_produccion_solar(df: pd.DataFrame):
    """
    Inserta o actualiza datos de producción solar.
    
    Args:
        df: DataFrame con columnas ['fecha_hora', 'produccion_kwh', 'radiacion']
    """
    conn = get_database_connection()
    conn.execute("INSERT OR REPLACE INTO produccion_solar SELECT * FROM df")


def insert_clima(df: pd.DataFrame):
    """
    Inserta o actualiza datos climáticos.
    
    Args:
        df: DataFrame con columnas ['fecha_hora', 'temperatura', 'nubosidad', 'humedad']
    """
    conn = get_database_connection()
    conn.execute("INSERT OR REPLACE INTO clima SELECT * FROM df")


def get_precios_luz(fecha_inicio: datetime, fecha_fin: datetime) -> pd.DataFrame:
    """
    Obtiene precios de luz en un rango de fechas.
    """
    conn = get_database_connection()
    query = """
        SELECT * FROM precios_luz 
        WHERE fecha_hora BETWEEN ? AND ?
        ORDER BY fecha_hora
    """
    return conn.execute(query, [fecha_inicio, fecha_fin]).df()


def get_produccion_solar(fecha_inicio: datetime, fecha_fin: datetime) -> pd.DataFrame:
    """
    Obtiene producción solar en un rango de fechas.
    """
    conn = get_database_connection()
    query = """
        SELECT * FROM produccion_solar 
        WHERE fecha_hora BETWEEN ? AND ?
        ORDER BY fecha_hora
    """
    return conn.execute(query, [fecha_inicio, fecha_fin]).df()


def get_clima(fecha_inicio: datetime, fecha_fin: datetime) -> pd.DataFrame:
    """
    Obtiene datos climáticos en un rango de fechas.
    """
    conn = get_database_connection()
    query = """
        SELECT * FROM clima 
        WHERE fecha_hora BETWEEN ? AND ?
        ORDER BY fecha_hora
    """
    return conn.execute(query, [fecha_inicio, fecha_fin]).df()


def get_datos_completos(fecha_inicio: datetime, fecha_fin: datetime) -> pd.DataFrame:
    """
    Obtiene todos los datos combinados mediante JOIN.
    Útil para entrenar el modelo de ML.
    """
    conn = get_database_connection()
    query = """
        SELECT 
            p.fecha_hora,
            p.precio_kwh,
            ps.produccion_kwh,
            ps.radiacion,
            c.temperatura,
            c.nubosidad,
            c.humedad
        FROM precios_luz p
        LEFT JOIN produccion_solar ps ON p.fecha_hora = ps.fecha_hora
        LEFT JOIN clima c ON p.fecha_hora = c.fecha_hora
        WHERE p.fecha_hora BETWEEN ? AND ?
        ORDER BY p.fecha_hora
    """
    return conn.execute(query, [fecha_inicio, fecha_fin]).df()


def cargar_datos_ejemplo():
    """
    Carga datos de ejemplo para pruebas iniciales.
    Genera una semana de datos sintéticos.
    """
    fecha_inicio = datetime(2026, 2, 1, 0, 0)
    fechas = [fecha_inicio + timedelta(hours=i) for i in range(168)]  # 7 días
    
    # Datos de ejemplo de precios (patrón realista)
    import numpy as np
    precios_base = [0.10, 0.09, 0.08, 0.08, 0.09, 0.12, 0.15, 0.18,
                    0.16, 0.14, 0.13, 0.12, 0.11, 0.12, 0.13, 0.14,
                    0.15, 0.18, 0.22, 0.20, 0.18, 0.15, 0.12, 0.11]
    
    df_precios = pd.DataFrame({
        'fecha_hora': fechas,
        'precio_kwh': [precios_base[i % 24] + np.random.uniform(-0.02, 0.02) 
                      for i in range(len(fechas))]
    })
    
    # Producción solar (mayor entre 8:00 y 18:00)
    df_produccion = pd.DataFrame({
        'fecha_hora': fechas,
        'produccion_kwh': [max(0, 5 * np.sin((i % 24 - 6) * np.pi / 12) + np.random.uniform(-0.5, 0.5))
                          for i in range(len(fechas))],
        'radiacion': [max(0, 800 * np.sin((i % 24 - 6) * np.pi / 12) + np.random.uniform(-100, 100))
                     for i in range(len(fechas))]
    })
    
    # Datos climáticos
    df_clima = pd.DataFrame({
        'fecha_hora': fechas,
        'temperatura': [20 + 8 * np.sin((i % 24 - 6) * np.pi / 12) + np.random.uniform(-2, 2)
                       for i in range(len(fechas))],
        'nubosidad': [np.random.randint(0, 100) for _ in range(len(fechas))],
        'humedad': [np.random.randint(30, 80) for _ in range(len(fechas))]
    })
    
    # Insertar datos
    insert_precios_luz(df_precios)
    insert_produccion_solar(df_produccion)
    insert_clima(df_clima)
    
    return len(fechas)


def guardar_simulacion(capacidad: float, carga_inicial: float, resultados: dict):
    """
    Guarda los resultados de una simulación de batería.
    """
    import json
    conn = get_database_connection()
    
    # Obtener el próximo ID
    max_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM simulaciones_bateria").fetchone()[0]
    nuevo_id = max_id + 1
    
    conn.execute("""
        INSERT INTO simulaciones_bateria (id, fecha_creacion, capacidad_bateria, carga_inicial, resultados)
        VALUES (?, ?, ?, ?, ?)
    """, [nuevo_id, datetime.now(), capacidad, carga_inicial, json.dumps(resultados)])


def get_simulaciones_recientes(limite: int = 10) -> pd.DataFrame:
    """
    Obtiene las simulaciones más recientes.
    """
    conn = get_database_connection()
    query = """
        SELECT id, fecha_creacion, capacidad_bateria, carga_inicial
        FROM simulaciones_bateria
        ORDER BY fecha_creacion DESC
        LIMIT ?
    """
    return conn.execute(query, [limite]).df()
