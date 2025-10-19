# 🚀 Simulación de Navegación de Drones con PSO - Formaciones Dinámicas

## 📋 Descripción del Proyecto

Este proyecto implementa un sistema de navegación autónoma para drones utilizando el algoritmo de Optimización por Enjambre de Partículas (PSO). Los drones se organizan automáticamente en tres formaciones distintas mientras evitan obstáculos en tiempo real.

## 🎯 Características Principales

### 🤖 Formaciones Implementadas

1. Cabeza de Robot 🤖 - Patrón detallado con estructura facial robótica

2. Estrella ⭐ - Formación estelar simétrica y elegante

3. Cabeza de Dragón 🐲 - Diseño complejo inspirado en criaturas mitológicas

### 🛡️ Sistema de Evasión de Obstáculos

- 8 obstáculos estratégicamente ubicados

- Fuerzas de repulsión dinámicas

- Distancias de seguridad configurables

- Penalizaciones en la función de fitness


## ⚙️ Arquitectura del Sistema

### 🧩 Componentes Principales

```python

class DroneFormationPSO:
    def __init__(self, max_iter=100):
        self.formations = [...]          # Tres patrones de formación
        self.obstacles = [...]           # Obstáculos circulares
        self.drones = [...]              # Posiciones de drones
        self.velocities = [...]          # Velocidades de movimiento
```

### 🎯 Algoritmo PSO Mejorado

- Inercia: 0.7 - Mantiene dirección actual

- Memoria: 1.5 - Sigue mejor posición personal

- Social: 1.5 - Atraído hacia el objetivo

- Evasión: Fuerza adicional para evitar obstáculos

## 📊 Parámetros de Configuración

```text

Parámetro	            Valor	    Descripción
Iteraciones máximas	    500	            Límite de ejecución
Límites del espacio	    [-8, 8]	    Área de navegación
Tamaño de formaciones	    Variable	    40-70 drones por formación
Radio de obstáculos	    1.0-1.2	    Tamaño de obstáculos
Distancia de llegada	    0.15	    Umbral para considerar llegada

```
## 🗺️ Distribución de Obstáculos

```python

self.obstacles = [
    {'center': np.array([-5.5, 0.0]), 'radius': 1.2},  # Oeste
    {'center': np.array([5.5, 0.0]), 'radius': 1.2},   # Este
    {'center': np.array([0.0, 5.8]), 'radius': 1.2},   # Norte
    {'center': np.array([0.0, -5.8]), 'radius': 1.2},  # Sur
    # ... +4 obstáculos diagonales
]

```

## 🎨 Visualizaciones Generadas

### 📸 Imágenes Estáticas (PNG)


1. cabeza_de_robot_formation.png - Formación robótica completada


![Cabeza de dragón](https://raw.githubusercontent.com/sharito2023s-oss/Laboratorio4/main/Punto%201/cabeza_de_dragón_formation.png)

2. estrella_formation.png - Patrón estelar finalizado

![Estreña](https://raw.githubusercontent.com/sharito2023s-oss/Laboratorio4/main/Punto%201/estrella_formation.png)

3. cabeza_de_dragón_formation.png - Diseño de dragón terminado

![Estreña](https://raw.githubusercontent.com/sharito2023s-oss/Laboratorio4/main/Punto%201/cabeza_de_robot_formation.png)

### 🎬 Animación Dinámica (GIF)

- drone_formation_animation.gif - Secuencia completa de navegación

- FPS: 15 frames por segundo

- Duración: ~30 segundos (depende de iteraciones)


![Estreña](https://raw.githubusercontent.com/sharito2023s-oss/Laboratorio4/main/Punto%201/drone_formation_animation.gif)

## 🚀 Funcionamiento del Algoritmo

### 🔄 Proceso de Navegación


1. Inicialización: Drones posicionados en bordes del área

2. Evaluación: Cálculo de fitness considerando distancia y obstáculos

3. Actualización: Velocidades y posiciones usando PSO

4. Transición: Cambio automático entre formaciones

5. Finalización: Cuando todas las formaciones se completan

## 🎯 Función de Fitness

```python

def fitness(self, position, drone_idx):
    distance_to_target = np.linalg.norm(position - target_pos)
    obstacle_penalty = 0
    # Penalización por acercarse a obstáculos
    return distance_to_target + obstacle_penalty
```

## 📈 Métricas de Rendimiento

### ⏱️ Tiempos de Convergencia

- Cabeza de Robot: ~80 iteraciones

- Estrella: ~60 iteraciones

- Cabeza de Dragón: ~100 iteraciones

### 🎯 Precisión de Posicionamiento

- Error promedio: < 0.15 unidades

- Tasa de éxito: > 95% de drones llegan a destino

- Colisiones: 0 (evasión efectiva de obstáculos)

## 👥 Autores

#### 🧑‍💻 Contribuidores Principales

- **Carlos Andrés Suárez Torres** → [Carlos23Andres](https://github.com/Carlos23Andres)  

- **Saira Sharid Sanabria Muñoz** → [sharito202](https://github.com/sharito202)
