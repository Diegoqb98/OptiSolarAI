"""
logic.py - Lógica de Negocio
OptiSolarAI - Simulación de Batería y Optimización Energética
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class SimuladorBateria:
    """
    Simula el comportamiento de una batería solar tomando decisiones
    óptimas para maximizar beneficios económicos.
    """
    
    def __init__(self, 
                 capacidad_bateria: float = 10.0,
                 carga_inicial: float = 5.0,
                 eficiencia_carga: float = 0.95,
                 eficiencia_descarga: float = 0.95,
                 precio_venta_factor: float = 0.8):
        """
        Inicializa el simulador de batería.
        
        Args:
            capacidad_bateria: Capacidad máxima en kWh
            carga_inicial: Carga inicial en kWh
            eficiencia_carga: Eficiencia al cargar (0-1)
            eficiencia_descarga: Eficiencia al descargar (0-1)
            precio_venta_factor: Factor del precio de venta respecto al de compra
        """
        self.capacidad_bateria = capacidad_bateria
        self.carga_inicial = min(carga_inicial, capacidad_bateria)
        self.eficiencia_carga = eficiencia_carga
        self.eficiencia_descarga = eficiencia_descarga
        self.precio_venta_factor = precio_venta_factor
        
        self.historial = []
        self.beneficio_acumulado = 0.0
    
    def simular(self, 
                df_produccion: pd.DataFrame,
                df_precios: pd.DataFrame,
                consumo_base: float = 2.0) -> Dict:
        """
        Ejecuta la simulación de gestión de batería.
        
        Args:
            df_produccion: DataFrame con ['fecha_hora', 'produccion_kwh']
            df_precios: DataFrame con ['fecha_hora', 'precio_kwh']
            consumo_base: Consumo base por hora en kWh
        
        Returns:
            dict: Resultados de la simulación
        """
        # Merge de datos
        df = pd.merge(df_produccion, df_precios, on='fecha_hora', how='inner')
        df = df.sort_values('fecha_hora').reset_index(drop=True)
        
        # Inicializar variables
        carga_actual = self.carga_inicial
        beneficio = 0.0
        self.historial = []
        
        for idx, row in df.iterrows():
            fecha_hora = row['fecha_hora']
            produccion = row['produccion_kwh']
            precio_compra = row['precio_kwh']
            precio_venta = precio_compra * self.precio_venta_factor
            consumo = consumo_base
            
            # Balance energético inicial
            energia_disponible = produccion - consumo
            
            # Decisión de gestión de batería
            decision, cantidad = self._tomar_decision(
                energia_disponible=energia_disponible,
                carga_actual=carga_actual,
                precio_compra=precio_compra,
                precio_venta=precio_venta,
                df_futuro=df.iloc[idx:idx+24] if idx+24 < len(df) else df.iloc[idx:]
            )
            
            # Ejecutar acción
            carga_nueva, coste_operacion = self._ejecutar_accion(
                decision=decision,
                cantidad=cantidad,
                carga_actual=carga_actual,
                precio_compra=precio_compra,
                precio_venta=precio_venta
            )
            
            # Registrar estado
            beneficio += coste_operacion
            
            self.historial.append({
                'fecha_hora': fecha_hora,
                'produccion_kwh': produccion,
                'consumo_kwh': consumo,
                'precio_kwh': precio_compra,
                'carga_bateria': carga_nueva,
                'decision': decision,
                'cantidad_kwh': cantidad,
                'beneficio_hora': coste_operacion,
                'beneficio_acumulado': beneficio
            })
            
            carga_actual = carga_nueva
        
        # Calcular resumen
        df_resultado = pd.DataFrame(self.historial)
        
        return {
            'beneficio_total': beneficio,
            'beneficio_medio_diario': beneficio / (len(df) / 24) if len(df) > 0 else 0,
            'energia_vendida_total': df_resultado[df_resultado['decision'] == 'vender']['cantidad_kwh'].sum(),
            'energia_comprada_total': df_resultado[df_resultado['decision'] == 'comprar']['cantidad_kwh'].sum(),
            'carga_final': carga_actual,
            'ciclos_bateria': self._calcular_ciclos(df_resultado),
            'detalles': df_resultado
        }
    
    def _tomar_decision(self,
                       energia_disponible: float,
                       carga_actual: float,
                       precio_compra: float,
                       precio_venta: float,
                       df_futuro: pd.DataFrame) -> Tuple[str, float]:
        """
        Toma la decisión óptima: cargar, descargar o vender.
        
        Estrategia:
        1. Si hay exceso de producción y precio bajo: CARGAR batería
        2. Si hay déficit y precio alto: DESCARGAR batería si hay carga
        3. Si precio muy alto y batería cargada: VENDER a la red
        4. Si precio bajo y batería descargada: COMPRAR de la red
        
        Returns:
            Tuple[str, float]: (decisión, cantidad_kwh)
        """
        # Calcular precio medio futuro (próximas 6 horas)
        precio_medio_futuro = df_futuro['precio_kwh'].head(6).mean() if len(df_futuro) > 0 else precio_compra
        
        # CASO 1: Exceso de energía solar
        if energia_disponible > 0:
            # Cargar batería si hay espacio y el precio no es muy alto
            espacio_disponible = self.capacidad_bateria - carga_actual
            if espacio_disponible > 0.1 and precio_compra < precio_medio_futuro * 1.2:
                cantidad_cargar = min(energia_disponible, espacio_disponible) * self.eficiencia_carga
                return ('cargar', cantidad_cargar)
            else:
                # Vender excedente a la red
                return ('vender', energia_disponible)
        
        # CASO 2: Déficit de energía
        else:
            deficit = abs(energia_disponible)
            
            # Descargar batería si el precio es alto o si tenemos suficiente carga
            if carga_actual > 1.0 and (precio_compra > precio_medio_futuro * 0.9 or carga_actual > self.capacidad_bateria * 0.7):
                cantidad_descargar = min(deficit, carga_actual) * self.eficiencia_descarga
                return ('descargar', cantidad_descargar)
            else:
                # Comprar de la red
                return ('comprar', deficit)
    
    def _ejecutar_accion(self,
                        decision: str,
                        cantidad: float,
                        carga_actual: float,
                        precio_compra: float,
                        precio_venta: float) -> Tuple[float, float]:
        """
        Ejecuta la acción decidida y retorna el nuevo estado.
        
        Returns:
            Tuple[float, float]: (nueva_carga, beneficio/coste)
        """
        nueva_carga = carga_actual
        coste = 0.0
        
        if decision == 'cargar':
            nueva_carga = min(carga_actual + cantidad, self.capacidad_bateria)
            coste = 0  # No hay coste directo, usamos energía solar
        
        elif decision == 'descargar':
            nueva_carga = max(carga_actual - cantidad / self.eficiencia_descarga, 0)
            coste = cantidad * precio_compra  # Ahorro al no comprar
        
        elif decision == 'vender':
            coste = cantidad * precio_venta  # Ingreso por venta
        
        elif decision == 'comprar':
            coste = -cantidad * precio_compra  # Gasto
        
        return (nueva_carga, coste)
    
    def _calcular_ciclos(self, df: pd.DataFrame) -> float:
        """
        Calcula el número aproximado de ciclos de carga/descarga de la batería.
        """
        energia_total_cargada = df[df['decision'] == 'cargar']['cantidad_kwh'].sum()
        ciclos = energia_total_cargada / self.capacidad_bateria if self.capacidad_bateria > 0 else 0
        return round(ciclos, 2)


class OptimizadorTarifas:
    """
    Optimiza las decisiones basándose en tarifas horarias.
    """
    
    @staticmethod
    def calcular_ventanas_optimas(df_precios: pd.DataFrame, 
                                   ventana_horas: int = 3) -> Dict[str, List[datetime]]:
        """
        Identifica las mejores ventanas horarias para comprar/vender.
        
        Args:
            df_precios: DataFrame con ['fecha_hora', 'precio_kwh']
            ventana_horas: Tamaño de la ventana en horas
        
        Returns:
            dict: {'comprar': [fechas], 'vender': [fechas]}
        """
        df = df_precios.sort_values('fecha_hora').reset_index(drop=True)
        
        # Calcular media móvil
        df['precio_promedio'] = df['precio_kwh'].rolling(window=ventana_horas, center=True).mean()
        precio_medio_global = df['precio_kwh'].mean()
        
        # Identificar ventanas
        ventanas_compra = df[df['precio_kwh'] < precio_medio_global * 0.85]['fecha_hora'].tolist()
        ventanas_venta = df[df['precio_kwh'] > precio_medio_global * 1.15]['fecha_hora'].tolist()
        
        return {
            'comprar': ventanas_compra,
            'vender': ventanas_venta,
            'precio_medio': precio_medio_global
        }
    
    @staticmethod
    def calcular_roi(inversion_inicial: float,
                    beneficio_anual: float,
                    vida_util_anos: int = 25) -> Dict:
        """
        Calcula el ROI de la instalación solar.
        
        Returns:
            dict: Métricas financieras
        """
        beneficio_total = beneficio_anual * vida_util_anos
        roi_porcentaje = (beneficio_total - inversion_inicial) / inversion_inicial * 100
        payback_anos = inversion_inicial / beneficio_anual if beneficio_anual > 0 else float('inf')
        
        return {
            'roi_porcentaje': round(roi_porcentaje, 2),
            'payback_anos': round(payback_anos, 2),
            'beneficio_total': round(beneficio_total, 2),
            'tir_aproximado': round((beneficio_anual / inversion_inicial) * 100, 2)
        }


def generar_recomendaciones(simulacion: Dict, precios_futuro: pd.DataFrame) -> List[str]:
    """
    Genera recomendaciones basadas en los resultados de la simulación.
    
    Args:
        simulacion: Resultados de SimuladorBateria.simular()
        precios_futuro: Precios futuros para análisis
    
    Returns:
        List[str]: Lista de recomendaciones
    """
    recomendaciones = []
    
    # Analizar beneficio
    if simulacion['beneficio_total'] < 0:
        recomendaciones.append(" La simulación muestra pérdidas. Considera aumentar la capacidad de la batería.")
    elif simulacion['beneficio_total'] > 50:
        recomendaciones.append(" Excelente gestión energética. El sistema está optimizado.")
    
    # Analizar uso de batería
    if simulacion['ciclos_bateria'] > 1.5:
        recomendaciones.append(" Alto uso de batería. Esto maximiza el ahorro pero puede reducir su vida útil.")
    elif simulacion['ciclos_bateria'] < 0.5:
        recomendaciones.append(" La batería se utiliza poco. Considera ajustar la estrategia de carga/descarga.")
    
    # Analizar venta/compra
    df = simulacion['detalles']
    ratio_venta = len(df[df['decision'] == 'vender']) / len(df) if len(df) > 0 else 0
    if ratio_venta > 0.3:
        recomendaciones.append(" Alta venta de energía a la red. Buen aprovechamiento de precios altos.")
    
    # Análisis de precios futuros
    if len(precios_futuro) > 0:
        precio_max_futuro = precios_futuro['precio_kwh'].max()
        precio_actual = precios_futuro['precio_kwh'].iloc[0]
        if precio_max_futuro > precio_actual * 1.3:
            recomendaciones.append(" Se esperan picos de precio próximamente. Prepara la batería para vender.")
    
    if len(recomendaciones) == 0:
        recomendaciones.append("? Sistema funcionando dentro de parámetros normales.")
    
    return recomendaciones
