# 🚁 Simulación de Rescate con Drones - Algoritmo de Colonias de Hormigas

## 📋 Descripción del Proyecto

Esta simulación implementa un sistema multi-dron inteligente para operaciones de rescate en zonas de desastre, utilizando un algoritmo inspirado en colonias de hormigas para optimizar la exploración y localización de supervivientes y recursos.

## 🎯 Objetivos del Sistema

- Exploración eficiente de áreas de desastre

- Localización rápida de supervivientes

- Recolección estratégica de recursos

- Evitación inteligente de obstáculos

- Maximización de cobertura del terreno

## ⚙️ Configuración del Sistema

#### Parámetros Principales

```python

MAP_SIZE = 20           # Tamaño del mapa 20x20
NUM_DRONES = 8          # Flota de 8 drones
NUM_SURVIVORS = 15      # Supervivientes a rescatar
NUM_RESOURCES = 18      # Recursos a recolectar
NUM_OBSTACLES = 15      # Obstáculos iniciales
MAX_STEPS = 300         # Duración máxima de la simulación

```

#### Estados del Mapa

```text

Estado	  Color  	Descripción
EMPTY	  ⬜ Blanco	Celda vacía
SURVIVOR  🟢 Verde	Superviviente
RESOURCE  🔵 Azul	Recurso
OBSTACLE  ⚫ Gris	Obstáculo
DRONE	  🔴 Rojo	Dron
RESCUED	  🟡 Amarillo	Superviviente rescatado

```

## 🧠 Algoritmo Inteligente Implementado

#### Sistema de Feromonas

```python

EVAPORATION_RATE = 0.3   # Tasa de evaporación
ALPHA = 1.0             # Influencia de feromonas
BETA = 2.0              # Influencia de heurística

```

#### Toma de Decisiones de los Drones

- Feromonas: Siguen rastros dejados por otros drones

- Exploración: Prefieren áreas no visitadas

- Objetivos: Priorizan supervivientes y recursos

- Evitación: Esquivan obstáculos dinámicamente


## 📊 Métricas de Rendimiento

#### Función de Fitness

```python

fitness = (supervivientes * 20) + (recursos * 12) + (cobertura * 50) 
          - (energía * 0.05) - (atascos * 5)

```

#### Métricas Monitoreadas

- Cobertura del área (% del mapa explorado)

- Energía consumida total

- Supervivientes encontrados

- Recursos recolectados

- Eficiencia de rutas

## 🎨 Visualizaciones Generadas

### 1. 🎬 Animación en Tiempo Real (drone_rescue_simulation.gif)

- Exploración en tiempo real de los drones

- Evolución de la cobertura del mapa

- Actualización dinámica de métricas

- Eventos en tiempo real (rescates, recolecciones)


![Drone Simulation](https://raw.githubusercontent.com/sharito2023s-oss/Laboratorio4/main/Segundo/drone_rescue_final.png)

2. 📊 Dashboard Final (drone_rescue_final.png)

- Estado final del mapa de rescate

- Gráficos de evolución de métricas

- Resumen estadístico completo

- Análisis de eficiencia

![Drone Simulation](https://raw.githubusercontent.com/sharito2023s-oss/Laboratorio4/main/Segundo/drone_rescue_simulation.gif)

### 🔄 Dinámica de la Simulación


#### Comportamiento de los Drones

- Movimiento coordinado mediante feromonas

- Comunicación indirecta a través del mapa

- Adaptación dinámica a cambios en el entorno

- Recuperación de fallos (reposicionamiento)

#### Eventos Dinámicos

```python

DYNAMIC_CHANGE_STEP = 150  # Nuevos obstáculos en paso 150

```

- Obstáculos emergentes que modifican el terreno

- Readaptación de rutas en tiempo real

- Mantenimiento de eficiencia ante cambios


## 📈 Resultados Esperados

#### Métricas Típicas

```text

Cobertura máxima: 85-100%
Supervivientes encontrados: 12-15/15
Recursos recolectados: 15-18/18
Energía consumida: 800-1200 unidades

```

## 🔧 Personalización

#### Modificación de Parámetros

```python

# Ajustar tamaño y complejidad
MAP_SIZE = 30
NUM_DRONES = 12
NUM_SURVIVORS = 25

# Modificar comportamiento algorítmico
EVAPORATION_RATE = 0.2
ALPHA = 1.5
BETA = 1.8

```

#### Escenarios de Prueba

- Alta densidad de obstáculos
 
- Distribuciones específicas de objetivos

- Condiciones iniciales variables

- Eventos de emergencia programados

## 📊 Análisis de Resultados

#### Interpretación de Métricas

- Cobertura > 90%: Exploración muy eficiente

- Energía baja: Rutas optimizadas

- Todos objetivos encontrados: Éxito completo

- Recuperación rápida: Robustez del algoritmo

#### Optimizaciones Identificadas

- Tasa de evaporación óptima: 0.2-0.3

- Balance ALPHA/BETA: 1.0/2.0

- Tamaño óptimo de flota: 6-10 drones

- Estrategia de reposicionamiento efectiva

## 👥 Autores

#### 🧑‍💻 Contribuidores Principales

- **Carlos Andrés Suárez Torres** → [Carlos23Andres](https://github.com/Carlos23Andres)  

- **Saira Sharid Sanabria Muñoz** → [sharito202](https://github.com/sharito202)
