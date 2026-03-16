import numpy as np
import pandas as pd
import pickle
from pathlib import Path

class AgenteRL:
    """
    Agente de Reinforcement Learning (Q-Learning) para la optimización 
    de la gestión de baterías solares.
    """
    def __init__(self, capacidad_bateria=10.0, file_path="models/q_learning_agent.pkl"):
        self.capacidad_bateria = capacidad_bateria
        self.file_path = Path(file_path)
        
        # Hyperparameters
        self.alpha = 0.1      # Learning rate
        self.gamma = 0.95     # Discount factor
        self.epsilon = 0.1    # Exploration rate
        
        self.acciones = ['cargar', 'descargar', 'vender', 'comprar', 'mantener']
        
        # Q-Table
        self.q_table = {}
        
    def _get_estado(self, hora, carga_actual, precio_actual, energia_disponible):
        """
        Discretiza las variables continuas en estados.
        """
        # Hora: 4 bloques del día
        hora_b = hora // 6 
        
        # Carga: 0 (vacía), 1 (media), 2 (llena)
        if carga_actual < self.capacidad_bateria * 0.2:
            carga_b = 0
        elif carga_actual > self.capacidad_bateria * 0.8:
            carga_b = 2
        else:
            carga_b = 1
            
        # Precio: 0 (barato), 1 (normal), 2 (caro)
        if precio_actual < 0.08:
            precio_b = 0
        elif precio_actual > 0.15:
            precio_b = 2
        else:
            precio_b = 1
            
        # Energía sol: 0 (déficit), 1 (exceso)
        energia_b = 1 if energia_disponible > 0 else 0
            
        return (hora_b, carga_b, precio_b, energia_b)
        
    def elegir_accion(self, estado, is_training=True):
        """
        Elige una acción usando política epsilon-greedy
        """
        if estado not in self.q_table:
            self.q_table[estado] = np.zeros(len(self.acciones))
            
        if is_training and np.random.uniform(0, 1) < self.epsilon:
            # Exploración
            return np.random.choice(len(self.acciones))
        else:
            # Explotación
            return np.argmax(self.q_table[estado])
            
    def aprender(self, estado, accion_idx, recompensa, siguiente_estado):
        """
        Actualiza el valor en la tabla Q usando la ecuación de Bellman
        """
        if estado not in self.q_table:
            self.q_table[estado] = np.zeros(len(self.acciones))
        if siguiente_estado not in self.q_table:
            self.q_table[siguiente_estado] = np.zeros(len(self.acciones))
            
        antiguo_valor = self.q_table[estado][accion_idx]
        siguiente_max = np.max(self.q_table[siguiente_estado])
        
        # Q-Learning update rule
        nuevo_valor = (1 - self.alpha) * antiguo_valor + self.alpha * (recompensa + self.gamma * siguiente_max)
        self.q_table[estado][accion_idx] = nuevo_valor
        
    def guardar_modelo(self):
        self.file_path.parent.mkdir(exist_ok=True)
        with open(self.file_path, 'wb') as f:
            pickle.dump(self.q_table, f)
            
    def cargar_modelo(self):
        if self.file_path.exists():
            with open(self.file_path, 'rb') as f:
                self.q_table = pickle.load(f)
            return True
        return False
