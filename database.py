"""
database.py - Gestió de Base de Dades amb DuckDB
OptiSolarAI - Sistema de Gestió d'Energia Solar
"""

import duckdb
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path


@st.cache_resource
def get_database_connection():
    """
    Crea i retorna una connexió persistent a DuckDB.
    Utilitza st.cache_resource per mantenir la connexió activa entre reruns.
    """
    db_path = Path("data/optisolar.duckdb")
    db_path.parent.mkdir(exist_ok=True)

    conn = duckdb.connect(str(db_path))
    _initialize_tables(conn)
    return conn


def _initialize_tables(conn):
    """
    Inicialitza les taules necessàries si no existeixen.
    """
    # Taula de preus de llum per hora
    conn.execute("""
        CREATE TABLE IF NOT EXISTS precios_luz (
            fecha_hora TIMESTAMP,
            precio_kwh FLOAT,
            PRIMARY KEY (fecha_hora)
        )
    """)

    # Taula de producció solar real
    conn.execute("""
        CREATE TABLE IF NOT EXISTS produccion_solar (
            fecha_hora TIMESTAMP,
            produccion_kwh FLOAT,
            radiacion FLOAT,
            PRIMARY KEY (fecha_hora)
        )
    """)

    # Taula de dades climàtiques
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clima (
            fecha_hora TIMESTAMP,
            temperatura FLOAT,
            nubosidad INTEGER,
            humedad INTEGER,
            PRIMARY KEY (fecha_hora)
        )
    """)

    # Taula de simulacions de bateria
    conn.execute("""
        CREATE TABLE IF NOT EXISTS simulaciones_bateria (
            id INTEGER PRIMARY KEY,
            fecha_creacion TIMESTAMP,
            capacidad_bateria FLOAT,
            carga_inicial FLOAT,
            resultados TEXT
        )
    """)

    # Taula de registre de consum del llar (NOVA UD1B)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS registre_consum (
            id INTEGER PRIMARY KEY,
            data DATE,
            hora INTEGER,
            categoria VARCHAR,
            electrodomestic VARCHAR,
            kwh FLOAT,
            hora_punta BOOLEAN
        )
    """)


# ============================================================================
# INSERCIONS
# ============================================================================

def insert_precios_luz(df: pd.DataFrame):
    """
    Insereix o actualitza dades de preus de llum.

    Args:
        df: DataFrame amb columnes ['fecha_hora', 'precio_kwh']
    """
    conn = get_database_connection()
    conn.execute("INSERT OR REPLACE INTO precios_luz SELECT * FROM df")


def insert_produccion_solar(df: pd.DataFrame):
    """
    Insereix o actualitza dades de producció solar.

    Args:
        df: DataFrame amb columnes ['fecha_hora', 'produccion_kwh', 'radiacion']
    """
    conn = get_database_connection()
    conn.execute("INSERT OR REPLACE INTO produccion_solar SELECT * FROM df")


def insert_clima(df: pd.DataFrame):
    """
    Insereix o actualitza dades climàtiques.

    Args:
        df: DataFrame amb columnes ['fecha_hora', 'temperatura', 'nubosidad', 'humedad']
    """
    conn = get_database_connection()
    conn.execute("INSERT OR REPLACE INTO clima SELECT * FROM df")


def insert_consum(data: str, hora: int, categoria: str,
                  electrodomestic: str, kwh: float, hora_punta: bool):
    """
    Insereix un registre de consum del llar.

    Args:
        data: Data en format 'YYYY-MM-DD'
        hora: Hora del dia (0-23)
        categoria: Categoria (Cuina, Clima, Il·luminació, etc.)
        electrodomestic: Nom de l'electrodomèstic
        kwh: Energia consumida en kWh
        hora_punta: Si és hora punta (True/False)
    """
    conn = get_database_connection()
    max_id = conn.execute("SELECT COALESCE(MAX(id), 0) FROM registre_consum").fetchone()[0]
    nou_id = max_id + 1
    conn.execute("""
        INSERT INTO registre_consum (id, data, hora, categoria, electrodomestic, kwh, hora_punta)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [nou_id, data, hora, categoria, electrodomestic, kwh, hora_punta])


def delete_consum(consum_id: int):
    """
    Elimina un registre de consum per ID.
    """
    conn = get_database_connection()
    conn.execute("DELETE FROM registre_consum WHERE id = ?", [consum_id])


# ============================================================================
# CONSULTES
# ============================================================================

def get_precios_luz(fecha_inicio: datetime, fecha_fin: datetime) -> pd.DataFrame:
    """
    Obté preus de llum en un rang de dates.
    """
    try:
        conn = get_database_connection()
        query = """
            SELECT * FROM precios_luz
            WHERE fecha_hora BETWEEN ? AND ?
            ORDER BY fecha_hora
        """
        return conn.execute(query, [fecha_inicio, fecha_fin]).df()
    except Exception:
        return pd.DataFrame(columns=['fecha_hora', 'precio_kwh'])


def get_produccion_solar(fecha_inicio: datetime, fecha_fin: datetime) -> pd.DataFrame:
    """
    Obté producció solar en un rang de dates.
    """
    try:
        conn = get_database_connection()
        query = """
            SELECT * FROM produccion_solar
            WHERE fecha_hora BETWEEN ? AND ?
            ORDER BY fecha_hora
        """
        return conn.execute(query, [fecha_inicio, fecha_fin]).df()
    except Exception:
        return pd.DataFrame(columns=['fecha_hora', 'produccion_kwh', 'radiacion'])


def get_clima(fecha_inicio: datetime, fecha_fin: datetime) -> pd.DataFrame:
    """
    Obté dades climàtiques en un rang de dates.
    """
    try:
        conn = get_database_connection()
        query = """
            SELECT * FROM clima
            WHERE fecha_hora BETWEEN ? AND ?
            ORDER BY fecha_hora
        """
        return conn.execute(query, [fecha_inicio, fecha_fin]).df()
    except Exception:
        return pd.DataFrame(columns=['fecha_hora', 'temperatura', 'nubosidad', 'humedad'])


def get_datos_completos(fecha_inicio: datetime, fecha_fin: datetime) -> pd.DataFrame:
    """
    Obté totes les dades combinades mitjançant JOIN.
    Útil per entrenar el model de ML.
    """
    try:
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
    except Exception:
        return pd.DataFrame()


def get_consum_per_periode(data_inici: str = None, data_fi: str = None) -> pd.DataFrame:
    """
    Obté tots els registres de consum, opcionalment filtrats per dates.

    Args:
        data_inici: Data inici en format 'YYYY-MM-DD' (opcional)
        data_fi: Data fi en format 'YYYY-MM-DD' (opcional)

    Returns:
        DataFrame amb tots els registres de consum
    """
    try:
        conn = get_database_connection()
        if data_inici and data_fi:
            query = """
                SELECT * FROM registre_consum
                WHERE data BETWEEN ? AND ?
                ORDER BY data DESC, hora DESC
            """
            return conn.execute(query, [data_inici, data_fi]).df()
        else:
            return conn.execute(
                "SELECT * FROM registre_consum ORDER BY data DESC, hora DESC"
            ).df()
    except Exception:
        return pd.DataFrame(columns=['id', 'data', 'hora', 'categoria',
                                     'electrodomestic', 'kwh', 'hora_punta'])


def get_consum_per_categoria() -> pd.DataFrame:
    """
    Agrega el consum total per categoria.

    Returns:
        DataFrame amb columnes ['categoria', 'total_kwh', 'num_registres']
    """
    try:
        conn = get_database_connection()
        return conn.execute("""
            SELECT
                categoria,
                SUM(kwh) AS total_kwh,
                COUNT(*) AS num_registres
            FROM registre_consum
            GROUP BY categoria
            ORDER BY total_kwh DESC
        """).df()
    except Exception:
        return pd.DataFrame(columns=['categoria', 'total_kwh', 'num_registres'])


def get_estadisticas_resumen() -> dict:
    """
    Retorna estadístiques generals de la base de dades.

    Returns:
        dict amb recomptes de registres per taula
    """
    try:
        conn = get_database_connection()
        n_precios = conn.execute("SELECT COUNT(*) FROM precios_luz").fetchone()[0]
        n_prod = conn.execute("SELECT COUNT(*) FROM produccion_solar").fetchone()[0]
        n_clima = conn.execute("SELECT COUNT(*) FROM clima").fetchone()[0]
        n_consum = conn.execute("SELECT COUNT(*) FROM registre_consum").fetchone()[0]
        return {
            'preus_llum': n_precios,
            'produccio_solar': n_prod,
            'clima': n_clima,
            'consum_llar': n_consum
        }
    except Exception:
        return {}


# ============================================================================
# CÀRREGA DE DADES D'EXEMPLE
# ============================================================================

def cargar_datos_ejemplo():
    """
    Carrega dades d'exemple per a proves inicials.
    Genera 30 dies de dades sintètiques realistes.
    """
    import numpy as np

    fecha_inicio = datetime(2026, 1, 15, 0, 0)
    n_hores = 30 * 24  # 30 dies
    fechas = [fecha_inicio + timedelta(hours=i) for i in range(n_hores)]

    # Preus realistes (patró diari + variació setmanal lleugera)
    precios_base = [0.10, 0.09, 0.08, 0.08, 0.09, 0.12, 0.15, 0.18,
                    0.16, 0.14, 0.13, 0.12, 0.11, 0.12, 0.13, 0.14,
                    0.15, 0.18, 0.22, 0.20, 0.18, 0.15, 0.12, 0.11]

    np.random.seed(42)
    df_precios = pd.DataFrame({
        'fecha_hora': fechas,
        'precio_kwh': [
            max(0.04, precios_base[i % 24]
                + np.random.uniform(-0.02, 0.02)
                + 0.01 * np.sin(i * np.pi / (24 * 7)))  # variació setmanal
            for i in range(n_hores)
        ]
    })

    # Producció solar (major entre 8:00 i 18:00, amb variació estacional)
    df_produccion = pd.DataFrame({
        'fecha_hora': fechas,
        'produccion_kwh': [
            max(0, 5.5 * np.sin((i % 24 - 6) * np.pi / 12)
                * (1 - 0.3 * np.sin(i * np.pi / (24 * 30)))  # variació mensual
                + np.random.uniform(-0.4, 0.4))
            for i in range(n_hores)
        ],
        'radiacion': [
            max(0, 850 * np.sin((i % 24 - 6) * np.pi / 12)
                + np.random.uniform(-80, 80))
            for i in range(n_hores)
        ]
    })

    # Dades climàtiques
    df_clima = pd.DataFrame({
        'fecha_hora': fechas,
        'temperatura': [
            round(18 + 7 * np.sin((i % 24 - 6) * np.pi / 12)
                  + 3 * np.sin(i * np.pi / (24 * 30))  # tendència mensual
                  + np.random.uniform(-1.5, 1.5), 1)
            for i in range(n_hores)
        ],
        'nubosidad': [
            int(np.clip(50 * np.random.beta(2, 3), 0, 100))
            for _ in range(n_hores)
        ],
        'humedad': [
            int(np.clip(np.random.normal(55, 15), 20, 95))
            for _ in range(n_hores)
        ]
    })

    # Inserir dades
    insert_precios_luz(df_precios)
    insert_produccion_solar(df_produccion)
    insert_clima(df_clima)

    return len(fechas)


# ============================================================================
# GESTIÓ DE SIMULACIONS
# ============================================================================

def guardar_simulacion(capacidad: float, carga_inicial: float, resultados: dict):
    """
    Guarda els resultats d'una simulació de bateria.
    """
    import json
    conn = get_database_connection()
    max_id = conn.execute(
        "SELECT COALESCE(MAX(id), 0) FROM simulaciones_bateria"
    ).fetchone()[0]
    nou_id = max_id + 1
    # Eliminar 'detalles' DataFrame per poder serialitzar
    resultados_net = {k: v for k, v in resultados.items() if k != 'detalles'}
    conn.execute("""
        INSERT INTO simulaciones_bateria (id, fecha_creacion, capacidad_bateria, carga_inicial, resultados)
        VALUES (?, ?, ?, ?, ?)
    """, [nou_id, datetime.now(), capacidad, carga_inicial, json.dumps(resultados_net)])


def get_simulaciones_recientes(limite: int = 10) -> pd.DataFrame:
    """
    Obté les simulacions més recents.
    """
    try:
        conn = get_database_connection()
        query = """
            SELECT id, fecha_creacion, capacidad_bateria, carga_inicial
            FROM simulaciones_bateria
            ORDER BY fecha_creacion DESC
            LIMIT ?
        """
        return conn.execute(query, [limite]).df()
    except Exception:
        return pd.DataFrame()
