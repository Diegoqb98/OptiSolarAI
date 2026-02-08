"""
ml_engine.py - Motor de Machine Learning
OptiSolarAI - Predicción de Producción Solar con Random Forest
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pickle
from pathlib import Path
from datetime import datetime
import streamlit as st
import requests


class SolarPredictor:
    """
    Clase para entrenar y realizar predicciones de producción solar
    utilizando Random Forest.
    """
    
    def __init__(self, model_path: str = "models/solar_predictor.pkl"):
        self.model_path = Path(model_path)
        self.model = None
        self.feature_importance = None
        self.metrics = {}
        
    def entrenar_modelo(self, df: pd.DataFrame):
        """
        Entrena el modelo Random Forest con datos históricos.
        
        Args:
            df: DataFrame con columnas [temperatura, nubosidad, humedad, radiacion, produccion_kwh]
        
        Returns:
            dict: Métricas de rendimiento del modelo
        """
        # Preparar features y target
        features = ['temperatura', 'nubosidad', 'humedad', 'radiacion']
        X = df[features].fillna(0)
        y = df['produccion_kwh'].fillna(0)
        
        # Dividir en train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Entrenar Random Forest
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluar
        y_pred = self.model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Importancia de features
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
        
        # Guardar modelo
        self._guardar_modelo()
        
        return self.metrics
    
    def _guardar_modelo(self):
        """Guarda el modelo entrenado en disco."""
        self.model_path.parent.mkdir(exist_ok=True)
        
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'feature_importance': self.feature_importance,
                'metrics': self.metrics
            }, f)
    
    def cargar_modelo(self) -> bool:
        """
        Carga un modelo previamente entrenado.
        
        Returns:
            bool: True si se cargó exitosamente, False en caso contrario
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
            print(f"Error al cargar modelo: {e}")
            return False
    
    def predecir(self, temperatura: float, nubosidad: int, 
                 humedad: int, radiacion: float) -> float:
        """
        Realiza una predicción de producción solar.
        
        Args:
            temperatura: Temperatura en C
            nubosidad: Porcentaje de nubosidad (0-100)
            humedad: Porcentaje de humedad (0-100)
            radiacion: Radiación solar en W/m
        
        Returns:
            float: Producción solar estimada en kWh
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado. Llama a entrenar_modelo() o cargar_modelo() primero.")
        
        features = pd.DataFrame([[temperatura, nubosidad, humedad, radiacion]], 
                               columns=['temperatura', 'nubosidad', 'humedad', 'radiacion'])
        
        prediccion = self.model.predict(features)[0]
        return max(0, prediccion)  # No puede ser negativa
    
    def predecir_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Realiza predicciones para múltiples registros.
        
        Args:
            df: DataFrame con columnas [temperatura, nubosidad, humedad, radiacion]
        
        Returns:
            DataFrame con columna adicional 'produccion_predicha'
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado.")
        
        features = ['temperatura', 'nubosidad', 'humedad', 'radiacion']
        X = df[features].fillna(0)
        
        df['produccion_predicha'] = self.model.predict(X)
        df['produccion_predicha'] = df['produccion_predicha'].clip(lower=0)
        
        return df


class OpenWeatherAPIClient:
    """
    Cliente para obtener datos meteorológicos de OpenWeatherMap API.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "YOUR_API_KEY_HERE"
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def obtener_clima_actual(self, ciudad: str = "Madrid") -> dict:
        """
        Obtiene el clima actual para una ciudad.
        
        Returns:
            dict: Datos climáticos (temperatura, nubosidad, humedad)
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
            print(f"Error al obtener datos de clima: {e}")
            # Devolver datos de ejemplo si falla la API
            return {
                'temperatura': 22.0,
                'nubosidad': 30,
                'humedad': 55,
                'descripcion': 'Datos de ejemplo (API no disponible)'
            }
    
    def obtener_pronostico(self, ciudad: str = "Madrid", dias: int = 5) -> pd.DataFrame:
        """
        Obtiene el pronóstico del tiempo para los próximos días.
        
        Returns:
            DataFrame con pronóstico por cada 3 horas
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
            print(f"Error al obtener pronóstico: {e}")
            # Devolver datos de ejemplo
            from datetime import timedelta
            fechas = [datetime.now() + timedelta(hours=i*3) for i in range(40)]
            return pd.DataFrame({
                'fecha_hora': fechas,
                'temperatura': [20 + 5*np.sin(i*0.2) for i in range(40)],
                'nubosidad': [np.random.randint(0, 80) for _ in range(40)],
                'humedad': [np.random.randint(40, 70) for _ in range(40)],
                'descripcion': ['Datos de ejemplo'] * 40
            })


@st.cache_resource
def cargar_predictor_solar():
    """
    Carga o inicializa el predictor solar con caché.
    Utilizado en la app de Streamlit.
    """
    predictor = SolarPredictor()
    if predictor.cargar_modelo():
        return predictor
    else:
        return predictor


def estimar_radiacion_solar(hora: int, nubosidad: int) -> float:
    """
    Estima la radiación solar basándose en la hora del día y nubosidad.
    
    Args:
        hora: Hora del día (0-23)
        nubosidad: Porcentaje de nubosidad (0-100)
    
    Returns:
        float: Radiación estimada en W/m
    """
    # Curva de radiación solar típica (pico al mediodía)
    if 6 <= hora <= 18:
        radiacion_maxima = 1000
        radiacion_base = radiacion_maxima * np.sin((hora - 6) * np.pi / 12)
        # Reducir por nubosidad
        factor_nubosidad = 1 - (nubosidad / 100) * 0.7
        return radiacion_base * factor_nubosidad
    else:
        return 0.0
