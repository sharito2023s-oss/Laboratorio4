# 🐝 Sistema de Polinización con Drones - Algoritmo ABC

## 📋 Descripción del Proyecto

Este proyecto simula un sistema inteligente de polinización en invernaderos utilizando drones que implementan el Algoritmo ABC (Artificial Bee Colony). El sistema optimiza la polinización de flores mediante tres tipos especializados de drones que cooperan para maximizar la eficiencia.

## 🎯 Características Principales

### 🏗️ Arquitectura del Sistema

- Invernadero: 35x35 celdas

- Flores: 70 distribuidas en 4 áreas

- Drones: 22 en total (12 obreras, 4 observadoras, 6 exploradoras)

- Simulación: 500 pasos máximo

## 🌸 Estados de las Flores


```text

Estado	     Color       Forma      Descripción
Inmadura     🟥 Rosa	 Hexágono   No lista para polinizar
Lista	     🟨 Naranja	 Triángulo  Preparada para polinización
Polinizada   🟩 Verde	 Diamante   Polinización completada

```

## 🚁 Tipos de Drones

```text

Tipo            Color         Función               Comportamiento
Obreras         🔵 Azul       Polinización local    Trabajan en área específica
Observadoras    🟡 Amarillo   Monitoreo             Posición fija en cada área
Exploradoras    🟣 Magenta    Búsqueda global       Exploración entre áreas
Recargando      🔴 Rojo	      Recarga               Retorno a base

```

## ⚙️ Algoritmo ABC Implementado

### 🔄 Comportamiento de los Drones

Drones Obreras (Worker Bees)

```python

def find_flower_for_worker(self, drone):
    # Busca flores en su área asignada
    # Prioriza flores listas para polinizar
    # Evita flores recientemente visitadas

```

Drones Exploradoras (Scout Bees)

```python

def find_flower_for_scout(self, drone):
    # Explora todas las áreas del invernadero
    # Busca flores listas en cualquier zona
    # Movimiento aleatorio cuando no hay objetivos

```

Sistema de Recarga Inteligente

```python

def update_state(self):
    # Recarga automática cuando batería ≤ 25%
    # Retorno a base para recargar
    # Reactivación cuando batería ≥ 95%

```

## 📊 Métricas de Rendimiento

### 🎯 Sistema de Evaluación

- Progreso de Polinización: Porcentaje de flores completamente polinizadas

- Energía Consumida: Total de energía utilizada por todos los drones

- Eficiencia por Tipo: Polinizaciones realizadas por cada categoría de drone

- Distribución de Estados: Conteo de flores en cada estado

### 📈 Visualizaciones en Tiempo Real

1. Mapa Principal del Invernadero

- División en 4 áreas con drones y flores

- Colores y formas distintivas para cada estado

- Base de recarga centralizada

- Movimiento en tiempo real de los drones

2. Gráficos de Métricas

- Progreso de Polinización: Tendencias de completitud

- Energía Consumida: Eficiencia energética

- Eficiencia por Tipo: Comparación entre obreras y exploradoras

- Distribución de Estados: Balance de flores por condición

## 🎮 Funcionamiento de la Simulación

### 🔄 Ciclo de Simulación

1. Actualización de Flores: Crecimiento natural y cambios de estado

2. Procesamiento de Drones:

    - Verificación de batería

    - Búsqueda de objetivos según tipo

    - Movimiento y polinización

    - Recarga cuando es necesario

3. Cálculo de Métricas: Actualización de todos los indicadores

4. Visualización: Renderizado en tiempo real

## ⚡ Comportamientos Especiales

Evitar Atascamiento

```python

if self.stuck_count > 10:
    self.target_flower = None  # Cambiar objetivo si está atascado

```

Movimiento Inteligente de Exploradoras

```python

if self.type == SCOUT and random.random() < 0.4:
    # Movimiento exploratorio en 8 direcciones
    directions = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]

```

## 📁 Archivos Generados

### 🎬 Animación en Tiempo Real

- bee_drone_pollination.gif: Animación completa de la simulación

- Formato: GIF animado a 10 FPS

- Duración: Hasta 500 pasos o polinización completa

![Simulation](https://raw.githubusercontent.com/sharito2023s-oss/Laboratorio4/main/Tercer%20Punto/tres.gif)
### 🖼️ Imagen Final

- bee_drone_pollination_final.png: Resumen visual del estado final

- Contenido: Mapa + 4 gráficos de métricas + leyenda

- Calidad: 150 DPI para alta definición

![Simulation](https://raw.githubusercontent.com/sharito2023s-oss/Laboratorio4/main/Tercer%20Punto/bee_drone_pollination_final.png)

## 👥 Autores

#### 🧑‍💻 Contribuidores Principales

- **Carlos Andrés Suárez Torres** → [Carlos23Andres](https://github.com/Carlos23Andres)  

- **Saira Sharid Sanabria Muñoz** → [sharito202](https://github.com/sharito202)
