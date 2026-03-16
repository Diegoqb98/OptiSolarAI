import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

try:
    from rl_engine import AgenteRL
except ImportError:
    AgenteRL = None


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
                 precio_venta_factor: float = 0.8,
                 usar_rl: bool = False):
        """
        Inicializa el simulador de batería.
        
        Args:
            capacidad_bateria: Capacidad máxima en kWh
            carga_inicial: Carga inicial en kWh
            eficiencia_carga: Eficiencia al cargar (0-1)
            eficiencia_descarga: Eficiencia al descargar (0-1)
            precio_venta_factor: Factor del precio de venta respecto al de compra
            usar_rl: Si es True, usa Reinforcement Learning para tomar decisiones
        """
        self.capacidad_bateria = capacidad_bateria
        self.carga_inicial = min(carga_inicial, capacidad_bateria)
        self.eficiencia_carga = eficiencia_carga
        self.eficiencia_descarga = eficiencia_descarga
        self.precio_venta_factor = precio_venta_factor
        self.usar_rl = usar_rl
        
        self.historial = []
        self.beneficio_acumulado = 0.0
        
        if self.usar_rl and AgenteRL is not None:
            self.agente = AgenteRL(capacidad_bateria=self.capacidad_bateria)
            # Try to load existing model
            if not self.agente.cargar_modelo():
                print("No pre-trained RL model found. Starting fresh.")
        else:
            self.agente = None
    
    def simular(self, 
                df_produccion: pd.DataFrame,
                df_precios: pd.DataFrame,
                consumo_base: float = 2.0,
                entrenar_rl: bool = False) -> Dict:
        """
        Ejecuta la simulación de gestión de batería.
        
        Args:
            df_produccion: DataFrame con ['fecha_hora', 'produccion_kwh']
            df_precios: DataFrame con ['fecha_hora', 'precio_kwh']
            consumo_base: Consumo base por hora en kWh
            entrenar_rl: Si es True, entrena el agente RL durante la simulación
        
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
            if self.usar_rl and self.agente is not None:
                estado, decision, cantidad = self._tomar_decision_rl(
                    fecha_hora=fecha_hora,
                    energia_disponible=energia_disponible,
                    carga_actual=carga_actual,
                    precio_compra=precio_compra,
                    precio_venta=precio_venta,
                    entrenar=entrenar_rl
                )
            else:
                decision, cantidad = self._tomar_decision(
                    energia_disponible=energia_disponible,
                    carga_actual=carga_actual,
                    precio_compra=precio_compra,
                    precio_venta=precio_venta,
                    df_futuro=df.iloc[idx:idx+24] if idx+24 < len(df) else df.iloc[idx:]
                )
                estado = None
            
            # Ejecutar acción
            carga_nueva, coste_operacion = self._ejecutar_accion(
                decision=decision,
                cantidad=cantidad,
                carga_actual=carga_actual,
                precio_compra=precio_compra,
                precio_venta=precio_venta
            )
            
            # Recompensa RL y actualización
            if self.usar_rl and self.agente is not None and entrenar_rl and estado is not None:
                # RL feedback loop
                recompensa = coste_operacion
                siguiente_estado = self.agente._get_estado(
                    (fecha_hora + timedelta(hours=1)).hour,
                    carga_nueva,
                    precio_compra, # Simplified: Using current price for next state proxy
                    energia_disponible # Simplified proxy
                )
                accion_idx = self.agente.acciones.index(decision) if decision in self.agente.acciones else 4
                self.agente.aprender(estado, accion_idx, recompensa, siguiente_estado)
            
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
            
        if self.usar_rl and self.agente is not None and entrenar_rl:
            self.agente.guardar_modelo()
        
        # Calcular resumen
        df_resultado = pd.DataFrame(self.historial)
        
        return {
            'beneficio_total': beneficio,
            'beneficio_medio_diario': beneficio / (len(df) / 24) if len(df) > 0 else 0,
            'energia_vendida_total': df_resultado[df_resultado['decision'] == 'vender']['cantidad_kwh'].sum() if len(df_resultado) > 0 else 0,
            'energia_comprada_total': df_resultado[df_resultado['decision'] == 'comprar']['cantidad_kwh'].sum() if len(df_resultado) > 0 else 0,
            'carga_final': carga_actual,
            'ciclos_bateria': self._calcular_ciclos(df_resultado),
            'detalles': df_resultado
        }
        
    def _tomar_decision_rl(self, fecha_hora, energia_disponible, carga_actual, precio_compra, precio_venta, entrenar):
        """
        Usa el agente de Reinforcement Learning para tomar una decisión.
        """
        estado = self.agente._get_estado(fecha_hora.hour, carga_actual, precio_compra, energia_disponible)
        accion_idx = self.agente.elegir_accion(estado, is_training=entrenar)
        decision = self.agente.acciones[accion_idx]
        
        # Traducir decisión a cantidad basada en físicas de batería
        cantidad = 0.0
        
        if decision == 'cargar' and energia_disponible > 0:
            espacio = self.capacidad_bateria - carga_actual
            cantidad = min(energia_disponible, espacio) * self.eficiencia_carga
            if cantidad <= 0.1: decision = 'mantener'
            
        elif decision == 'descargar' and energia_disponible < 0:
            deficit = abs(energia_disponible)
            cantidad = min(deficit, carga_actual) * self.eficiencia_descarga
            if cantidad <= 0.1: decision = 'comprar' # Forzar compra si no podemos descargar
            
        elif decision == 'vender' and energia_disponible > 0:
            cantidad = energia_disponible
            
        elif decision == 'comprar' and energia_disponible < 0:
            cantidad = abs(energia_disponible)
            
        elif decision == 'mantener':
            cantidad = 0.0
            # Si hay déficit, forzamos compra
            if energia_disponible < 0:
                decision = 'comprar'
                cantidad = abs(energia_disponible)
            # Si hay exceso, forzamos venta
            elif energia_disponible > 0:
                decision = 'vender'
                cantidad = energia_disponible
                
        return estado, decision, cantidad
    
    def _tomar_decision(self,
                       energia_disponible: float,
                       carga_actual: float,
                       precio_compra: float,
                       precio_venta: float,
                       df_futuro: pd.DataFrame) -> Tuple[str, float]:
        """
        Toma la decisión óptima con reglas fijas (Heurística).
        """
        precio_medio_futuro = df_futuro['precio_kwh'].head(6).mean() if len(df_futuro) > 0 else precio_compra
        
        if energia_disponible > 0:
            espacio_disponible = self.capacidad_bateria - carga_actual
            if espacio_disponible > 0.1 and precio_compra < precio_medio_futuro * 1.2:
                cantidad_cargar = min(energia_disponible, espacio_disponible) * self.eficiencia_carga
                return ('cargar', cantidad_cargar)
            else:
                return ('vender', energia_disponible)
        else:
            deficit = abs(energia_disponible)
            if carga_actual > 1.0 and (precio_compra > precio_medio_futuro * 0.9 or carga_actual > self.capacidad_bateria * 0.7):
                cantidad_descargar = min(deficit, carga_actual) * self.eficiencia_descarga
                return ('descargar', cantidad_descargar)
            else:
                return ('comprar', deficit)
    
    def _ejecutar_accion(self,
                        decision: str,
                        cantidad: float,
                        carga_actual: float,
                        precio_compra: float,
                        precio_venta: float) -> Tuple[float, float]:
        """
        Ejecuta la acción decidida y retorna el nuevo estado.
        """
        nueva_carga = carga_actual
        coste = 0.0
        
        if decision == 'cargar':
            nueva_carga = min(carga_actual + cantidad, self.capacidad_bateria)
            coste = 0
        elif decision == 'descargar':
            nueva_carga = max(carga_actual - cantidad / self.eficiencia_descarga, 0)
            coste = cantidad * precio_compra
        elif decision == 'vender':
            coste = cantidad * precio_venta
        elif decision == 'comprar':
            coste = -cantidad * precio_compra
        elif decision == 'mantener':
            coste = 0
            
        return (nueva_carga, coste)
    
    def _calcular_ciclos(self, df: pd.DataFrame) -> float:
        """
        Calcula el número aproximado de ciclos de carga/descarga de la batería.
        """
        if len(df) == 0: return 0.0
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
        df = df_precios.sort_values('fecha_hora').reset_index(drop=True)
        df['precio_promedio'] = df['precio_kwh'].rolling(window=ventana_horas, center=True).mean()
        precio_medio_global = df['precio_kwh'].mean()
        
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
    """
    recomendaciones = []
    
    if simulacion['beneficio_total'] < 0:
        recomendaciones.append(" La simulación muestra pérdidas. Considera aumentar la capacidad de la batería.")
    elif simulacion['beneficio_total'] > 50:
        recomendaciones.append(" Excelente gestión energética. El sistema está optimizado.")
    
    if simulacion['ciclos_bateria'] > 1.5:
        recomendaciones.append(" Alto uso de batería. Esto maximiza el ahorro pero puede reducir su vida útil.")
    elif simulacion['ciclos_bateria'] < 0.5:
        recomendaciones.append(" La batería se utiliza poco. Considera ajustar la estrategia de carga/descarga.")
    
    df = simulacion['detalles']
    if len(df) > 0:
        ratio_venta = len(df[df['decision'] == 'vender']) / len(df)
        if ratio_venta > 0.3:
            recomendaciones.append(" Alta venta de energía a la red. Buen aprovechamiento de precios altos.")
            
    if len(precios_futuro) > 0:
        precio_max_futuro = precios_futuro['precio_kwh'].max()
        precio_actual = precios_futuro['precio_kwh'].iloc[0]
        if precio_max_futuro > precio_actual * 1.3:
            recomendaciones.append(" Se esperan picos de precio próximamente. Prepara la batería para vender.")
            
    if len(recomendaciones) == 0:
        recomendaciones.append("? Sistema funcionando dentro de parámetros normales.")
        
    return recomendaciones
