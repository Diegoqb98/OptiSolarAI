"""
ml_engine.py - Motor de Machine Learning
OptiSolarAI - Predicció de Producció Solar amb Random Forest
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import streamlit as st
import requests


class SolarPredictor:
    """
    Classe per entrenar i realitzar prediccions de producció solar
    utilitzant Random Forest.
    """

    def __init__(self, model_path: str = "models/solar_predictor.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.feature_importance = None
        self.metrics = {}

    def entrenar_modelo(self, df: pd.DataFrame):
        """
        Entrena el model Random Forest amb dades històriques.

        Args:
            df: DataFrame amb columnes [temperatura, nubosidad, humedad, radiacion, produccion_kwh]

        Returns:
            dict: Mètriques de rendiment del model
        """
        features = ['temperatura', 'nubosidad', 'humedad', 'radiacion']
        X = df[features].fillna(0)
        y = df['produccion_kwh'].fillna(0)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )

        self.model.fit(X_train, y_train)

        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        self.feature_importance = pd.DataFrame({
            'feature': features,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)

        self.metrics = {
            'mae': mae,
            'r2': r2,
            'n_samples': len(X),
            'fecha_entrenamiento': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        self._guardar_modelo()
        return self.metrics

    def _guardar_modelo(self):
        """Guarda el model entrenat al disc."""
        self.model_path.parent.mkdir(exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'feature_importance': self.feature_importance,
                'metrics': self.metrics
            }, f)

    def cargar_modelo(self) -> bool:
        """
        Carrega un model prèviament entrenat.

        Returns:
            bool: True si s'ha carregat correctament
        """
        if not self.model_path.exists():
            return False
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.feature_importance = data['feature_importance']
                self.metrics = data['metrics']
            return True
        except Exception as e:
            print(f"Error al carregar model: {e}")
            return False

    def predecir(self, temperatura: float, nubosidad: int,
                 humedad: int, radiacion: float) -> float:
        """
        Realitza una predicció de producció solar.

        Args:
            temperatura: Temperatura en °C
            nubosidad: Percentatge de nuvolositat (0-100)
            humedad: Percentatge d'humitat (0-100)
            radiacion: Radiació solar en W/m²

        Returns:
            float: Producció solar estimada en kWh
        """
        if self.model is None:
            raise ValueError("Model no entrenat. Crida a entrenar_modelo() o cargar_modelo() primer.")

        features = pd.DataFrame([[temperatura, nubosidad, humedad, radiacion]],
                               columns=['temperatura', 'nubosidad', 'humedad', 'radiacion'])
        prediccion = self.model.predict(features)[0]
        return max(0, prediccion)

    def predecir_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Realitza prediccions per a múltiples registres.
        """
        if self.model is None:
            raise ValueError("Model no entrenat.")

        features = ['temperatura', 'nubosidad', 'humedad', 'radiacion']
        X = df[features].fillna(0)
        df = df.copy()
        df['produccion_predicha'] = self.model.predict(X)
        df['produccion_predicha'] = df['produccion_predicha'].clip(lower=0)
        return df


# ============================================================================
# PREVISIÓ 7 DIES (NOVA FUNCIONALITAT UD1B)
# ============================================================================

def generar_pronostico_7dias(predictor: SolarPredictor = None) -> pd.DataFrame:
    """
    Genera una previsió de producció solar per als propers 7 dies.

    Utilitza el model ML si está disponible; en cas contrari,
    fa servir una estimació heurística basada en radiació solar.

    Args:
        predictor: SolarPredictor opcionalment entrenat

    Returns:
        DataFrame amb columnes:
            - data (date)
            - dia_setmana (str)
            - temperatura_min, temperatura_max, temperatura_mitja (float)
            - nubositat (int, %)
            - humitat (int, %)
            - produccio_estimada_kwh (float)
            - produccio_per_hora (list)
            - qualitat (str: 'Excel·lent', 'Bona', 'Moderada', 'Baixa')
            - preu_venda_recomanat (str)
    """
    np.random.seed(int(datetime.now().strftime('%j')))  # seed per dia de l'any (consistent per dia)

    dies_setmana_ca = ['Dilluns', 'Dimarts', 'Dimecres', 'Dijous',
                       'Divendres', 'Dissabte', 'Diumenge']

    registres = []
    avui = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for d in range(1, 8):  # 7 dies endavant
        data = avui + timedelta(days=d)
        dia_idx = data.weekday()

        # Generar condicions meteorològiques sintètiques realistes
        nubositat = int(np.clip(np.random.normal(35, 25), 0, 100))
        humitat = int(np.clip(np.random.normal(55, 15), 20, 90))
        temp_base = 16 + 5 * np.sin(d * np.pi / 7)
        temp_mitja = round(temp_base + np.random.uniform(-2, 2), 1)
        temp_min = round(temp_mitja - np.random.uniform(3, 6), 1)
        temp_max = round(temp_mitja + np.random.uniform(4, 8), 1)

        # Calcular producció horàri (kWh per hora)
        produccio_per_hora = []
        for h in range(24):
            radiacio = estimar_radiacion_solar(h, nubositat)
            if predictor is not None and predictor.model is not None:
                kwh = predictor.predecir(temp_mitja, nubositat, humitat, radiacio)
            else:
                # Estimació heurística: pic de 5.5 kWh al migdia
                kwh = max(0, 5.5 * np.sin((h - 6) * np.pi / 12)
                          * (1 - nubositat / 100 * 0.7)
                          + np.random.uniform(-0.2, 0.2))
            produccio_per_hora.append(round(kwh, 3))

        produccio_total = round(sum(produccio_per_hora), 2)

        # Classificar qualitat del dia
        if produccio_total >= 35:
            qualitat = 'Excel·lent'
            emoji = '☀️'
        elif produccio_total >= 25:
            qualitat = 'Bona'
            emoji = '🌤️'
        elif produccio_total >= 15:
            qualitat = 'Moderada'
            emoji = '⛅'
        else:
            qualitat = 'Baixa'
            emoji = '☁️'

        registres.append({
            'data': data.date(),
            'dia_setmana': dies_setmana_ca[dia_idx],
            'temperatura_min': temp_min,
            'temperatura_max': temp_max,
            'temperatura_mitja': temp_mitja,
            'nubositat': nubositat,
            'humitat': humitat,
            'produccio_estimada_kwh': produccio_total,
            'qualitat': qualitat,
            'emoji': emoji,
        })

    return pd.DataFrame(registres)


# ============================================================================
# CLIENT API OPENWEATHERMAP
# ============================================================================

class OpenWeatherAPIClient:
    """
    Client per obtenir dades meteorològiques de OpenWeatherMap API.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or "YOUR_API_KEY_HERE"
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def obtener_clima_actual(self, ciudad: str = "Barcelona") -> dict:
        """
        Obté el clima actual per a una ciutat.
        """
        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': ciudad,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {
                'temperatura': data['main']['temp'],
                'nubosidad': data['clouds']['all'],
                'humedad': data['main']['humidity'],
                'descripcion': data['weather'][0]['description']
            }
        except Exception as e:
            print(f"Error al obtenir dades de clima: {e}")
            return {
                'temperatura': 20.0,
                'nubosidad': 30,
                'humedad': 55,
                'descripcion': 'Dades d\'exemple (API no disponible)'
            }

    def obtener_pronostico(self, ciudad: str = "Barcelona", dias: int = 5) -> pd.DataFrame:
        """
        Obté el pronòstic del temps per als propers dies.
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': ciudad,
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            registros = []
            for item in data['list']:
                registros.append({
                    'fecha_hora': pd.to_datetime(item['dt'], unit='s'),
                    'temperatura': item['main']['temp'],
                    'nubosidad': item['clouds']['all'],
                    'humedad': item['main']['humidity'],
                    'descripcion': item['weather'][0]['description']
                })
            return pd.DataFrame(registros)

        except Exception as e:
            print(f"Error al obtenir pronòstic: {e}")
            fechas = [datetime.now() + timedelta(hours=i * 3) for i in range(40)]
            return pd.DataFrame({
                'fecha_hora': fechas,
                'temperatura': [18 + 5 * np.sin(i * 0.2) for i in range(40)],
                'nubosidad': [np.random.randint(0, 80) for _ in range(40)],
                'humedad': [np.random.randint(40, 70) for _ in range(40)],
                'descripcion': ['Dades d\'exemple'] * 40
            })


# ============================================================================
# UTILITATS
# ============================================================================

@st.cache_resource
def cargar_predictor_solar():
    """
    Carrega o inicialitza el predictor solar amb caché.
    """
    predictor = SolarPredictor()
    predictor.cargar_modelo()
    return predictor


def estimar_radiacion_solar(hora: int, nubosidad: int) -> float:
    """
    Estima la radiació solar basant-se en l'hora del dia i la nuvolositat.

    Args:
        hora: Hora del dia (0-23)
        nubosidad: Percentatge de nuvolositat (0-100)

    Returns:
        float: Radiació estimada en W/m²
    """
    if 6 <= hora <= 18:
        radiacion_maxima = 1000
        radiacion_base = radiacion_maxima * np.sin((hora - 6) * np.pi / 12)
        factor_nubosidad = 1 - (nubosidad / 100) * 0.7
        return max(0, radiacion_base * factor_nubosidad)
    else:
        return 0.0
