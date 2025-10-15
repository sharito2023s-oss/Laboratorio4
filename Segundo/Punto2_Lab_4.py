import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import ListedColormap
import matplotlib.patches as mpatches

# Configuración de parámetros
MAP_SIZE = 20
NUM_DRONES = 8
NUM_SURVIVORS = 15
NUM_RESOURCES = 18  # Aumentado de 10 a 18
NUM_OBSTACLES = 15
MAX_STEPS = 300
EVAPORATION_RATE = 0.3
ALPHA = 1.0  # Influencia de la feromona
BETA = 2.0   # Influencia de la distancia (heurística)
INITIAL_PHEROMONE = 0.1
DYNAMIC_CHANGE_STEP = 150  # Paso para añadir nuevos obstáculos

# Estados de las celdas
EMPTY = 0
SURVIVOR = 1
RESOURCE = 2
OBSTACLE = 3
DRONE = 4
RESCUED = 5

# Colores para visualización
COLORS = {
    EMPTY: [1, 1, 1],      # Blanco
    SURVIVOR: [0, 1, 0],   # Verde
    RESOURCE: [0, 0.7, 1], # Azul claro (más visible)
    OBSTACLE: [0.3, 0.3, 0.3],  # Gris oscuro
    DRONE: [1, 0, 0],      # Rojo (todos los drones del mismo color)
    RESCUED: [1, 0.8, 0]   # Amarillo (supervivientes rescatados)
}

class DisasterMap:
    def __init__(self, size):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.pheromone = np.ones((size, size)) * INITIAL_PHEROMONE
        self.covered = np.zeros((size, size), dtype=bool)
        self.base_position = (size//2, size//2)  # Base en el centro
        self.initial_survivors = 0
        self.initial_resources = 0
        
    def add_entities(self, num_survivors, num_resources, num_obstacles):
        # Añadir supervivientes, recursos y obstáculos aleatoriamente
        positions = [(r, c) for r in range(self.size) for c in range(self.size) 
                    if (r, c) != self.base_position and 
                    (abs(r - self.base_position[0]) > 2 or abs(c - self.base_position[1]) > 2)]
        random.shuffle(positions)
        
        self.initial_survivors = num_survivors
        self.initial_resources = num_resources
        
        for i in range(num_survivors):
            if positions:
                r, c = positions.pop()
                self.grid[r, c] = SURVIVOR
                
        for i in range(num_resources):
            if positions:
                r, c = positions.pop()
                self.grid[r, c] = RESOURCE
                
        for i in range(num_obstacles):
            if positions:
                r, c = positions.pop()
                self.grid[r, c] = OBSTACLE
                self.pheromone[r, c] = 0  # Sin feromona en obstáculos
                
    def add_dynamic_obstacles(self, num_obstacles):
        # Añadir nuevos obstáculos dinámicamente
        positions = [(r, c) for r in range(self.size) for c in range(self.size) 
                     if self.grid[r, c] == EMPTY and (r, c) != self.base_position]
        random.shuffle(positions)
        for i in range(min(num_obstacles, len(positions))):
            r, c = positions[i]
            self.grid[r, c] = OBSTACLE
            self.pheromone[r, c] = 0  # Reiniciar feromona en obstáculos

    def evaporate_pheromone(self):
        self.pheromone *= (1 - EVAPORATION_RATE)
        # Mantener un nivel mínimo de feromona
        self.pheromone = np.maximum(self.pheromone, 0.01)

    def update_pheromone(self, paths, fitness_values):
        for path, fitness in zip(paths, fitness_values):
            if fitness > 0:
                # Aumentar feromona en la ruta proporcional al fitness
                pheromone_deposit = fitness * 0.1
                for (r, c) in set(path[-20:]):  # Solo las últimas 20 posiciones
                    self.pheromone[r, c] += pheromone_deposit

    def get_neighbors(self, position):
        r, c = position
        neighbors = []
        # Movimiento en 4 direcciones
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size and self.grid[nr, nc] != OBSTACLE:
                neighbors.append((nr, nc))
        return neighbors

class Drone:
    def __init__(self, drone_id, start_position):
        self.id = drone_id
        self.position = start_position
        self.path = [start_position]
        self.visited = set([start_position])
        self.found_survivors = 0
        self.found_resources = 0
        self.energy_used = 0
        self.stuck_count = 0
        # Todos los drones del mismo color rojo
        self.color = np.array([1, 0, 0])  # Rojo
        
    def move(self, disaster_map):
        current_r, current_c = self.position
        neighbors = disaster_map.get_neighbors(self.position)
        
        # Si no hay vecinos, el dron está atascado
        if not neighbors:
            self.stuck_count += 1
            return False, "stuck"
            
        # Filtrar vecinos ya visitados recientemente (para evitar ciclos)
        recent_positions = set(self.path[-8:])  # Últimas 8 posiciones
        unexplored_neighbors = [n for n in neighbors if n not in recent_positions]
        
        # Si todos los vecinos han sido visitados recientemente, considerar todos
        if not unexplored_neighbors:
            unexplored_neighbors = neighbors
            
        # Calcular probabilidades de movimiento
        probabilities = []
        for nr, nc in unexplored_neighbors:
            pheromone = disaster_map.pheromone[nr, nc]
            # Preferir celdas no visitadas
            visited_bonus = 3.0 if (nr, nc) not in self.visited else 0.3
            # Preferir objetivos (supervivientes o recursos)
            cell_type = disaster_map.grid[nr, nc]
            if cell_type == SURVIVOR:
                objective_bonus = 10.0
            elif cell_type == RESOURCE:
                objective_bonus = 8.0  # Aumentado para priorizar recursos
            else:
                objective_bonus = 1.0
            
            probability = (pheromone ** ALPHA) * visited_bonus * objective_bonus
            probabilities.append(probability)
            
        # Normalizar probabilidades
        total = sum(probabilities)
        if total == 0:
            # Si no hay feromona, moverse aleatoriamente
            next_pos = random.choice(unexplored_neighbors)
        else:
            probabilities = [p / total for p in probabilities]
            next_pos = random.choices(unexplored_neighbors, weights=probabilities)[0]
            
        # Actualizar posición y path
        old_position = self.position
        self.position = next_pos
        self.path.append(next_pos)
        self.visited.add(next_pos)
        self.energy_used += 1
        
        # Reiniciar contador de atascos si se movió
        if old_position != next_pos:
            self.stuck_count = 0
        
        # Verificar si encontró superviviente o recurso
        r, c = next_pos
        event = None
        if disaster_map.grid[r, c] == SURVIVOR:
            self.found_survivors += 1
            disaster_map.grid[r, c] = RESCUED  # Marcar como rescatado
            event = "survivor"
        elif disaster_map.grid[r, c] == RESOURCE:
            self.found_resources += 1
            disaster_map.grid[r, c] = EMPTY  # Marcar como recogido
            event = "resource"
            
        return True, event

def calculate_fitness(drone, disaster_map):
    # Fitness basado en objetivos encontrados y eficiencia de la ruta
    survivors_score = drone.found_survivors * 20
    resources_score = drone.found_resources * 12  # Aumentado para valorar más los recursos
    distance_penalty = drone.energy_used * 0.05
    coverage = len(drone.visited) / (disaster_map.size ** 2)
    coverage_score = coverage * 50
    stuck_penalty = drone.stuck_count * 5
    fitness = survivors_score + resources_score + coverage_score - distance_penalty - stuck_penalty
    return max(fitness, 0)

# Configuración de la figura
fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(3, 2)

# Subplots
ax1 = fig.add_subplot(gs[0:2, 0])  # Mapa (2 filas, columna 0)
ax2 = fig.add_subplot(gs[0, 1])    # Cobertura
ax3 = fig.add_subplot(gs[1, 1])    # Energía
ax4 = fig.add_subplot(gs[2, :])    # Objetivos (fila completa abajo)

# Inicializar mapa y drones
disaster_map = DisasterMap(MAP_SIZE)
disaster_map.add_entities(NUM_SURVIVORS, NUM_RESOURCES, NUM_OBSTACLES)
drones = [Drone(i, disaster_map.base_position) for i in range(NUM_DRONES)]

# Métricas
total_covered_history = []
energy_consumed_history = []
survivors_found_history = []
resources_found_history = []
steps_history = []

# Elementos de la animación - Mapa
map_display = ax1.imshow(np.zeros((MAP_SIZE, MAP_SIZE, 3)))
ax1.set_title('Exploración en Tiempo Real - Rescate con Drones')
ax1.set_xticks([])
ax1.set_yticks([])

# Leyenda fuera del mapa
legend_elements = [
    mpatches.Patch(color='green', label='Supervivientes'),
    mpatches.Patch(color='cyan', label='Recursos'),
    mpatches.Patch(color='gray', label='Obstáculos'),
    mpatches.Patch(color='yellow', label='Rescatados'),
    mpatches.Patch(color='red', label='Drones')
]
ax1.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))

# Puntos para los drones (todos rojos)
drone_positions = np.empty((0, 2))
drone_dots = ax1.scatter([], [], c='red', s=100, edgecolors='darkred', linewidths=2)

# Texto informativo (fuera del área del mapa)
info_text = fig.text(0.02, 0.95, '', fontsize=10, 
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

# Gráficos de métricas
coverage_line, = ax2.plot([], [], 'b-', linewidth=2)
ax2.set_xlim(0, MAX_STEPS)
ax2.set_ylim(0, 100)
ax2.set_xlabel('Pasos')
ax2.set_ylabel('Cobertura (%)')
ax2.set_title('Cobertura del Área')
ax2.grid(True, alpha=0.3)

energy_line, = ax3.plot([], [], 'r-', linewidth=2)
ax3.set_xlim(0, MAX_STEPS)
ax3.set_ylim(0, 2000)
ax3.set_xlabel('Pasos')
ax3.set_ylabel('Energía')
ax3.set_title('Energía Consumida')
ax3.grid(True, alpha=0.3)

survivors_line, = ax4.plot([], [], 'g-', label='Supervivientes', linewidth=2)
resources_line, = ax4.plot([], [], 'c-', label='Recursos', linewidth=2)
ax4.set_xlim(0, MAX_STEPS)
ax4.set_ylim(0, max(NUM_SURVIVORS, NUM_RESOURCES) + 2)
ax4.set_xlabel('Pasos')
ax4.set_ylabel('Encontrados')
ax4.set_title('Objetivos Encontrados')
ax4.legend()
ax4.grid(True, alpha=0.3)

# Variables para guardar la animación
frames_data = []

def init_animation():
    map_display.set_array(np.zeros((MAP_SIZE, MAP_SIZE, 3)))
    drone_dots.set_offsets(np.empty((0, 2)))
    coverage_line.set_data([], [])
    energy_line.set_data([], [])
    survivors_line.set_data([], [])
    resources_line.set_data([], [])
    info_text.set_text('Iniciando simulación...')
    return map_display, drone_dots, coverage_line, energy_line, survivors_line, resources_line, info_text

def update_animation(frame):
    global drones, disaster_map
    
    # Añadir obstáculos dinámicos en un paso específico
    if frame == DYNAMIC_CHANGE_STEP:
        disaster_map.add_dynamic_obstacles(3)
        print("¡Obstáculos dinámicos añadidos!")
            
    paths = []
    fitness_values = []
    events_this_step = []
    
    for drone in drones:
        # Mover el dron
        moved, event = drone.move(disaster_map)
        
        # Si el dron está atascado, intentar reposicionarlo
        if not moved or drone.stuck_count > 5:
            # Reposicionar cerca de la base
            neighbors = disaster_map.get_neighbors(disaster_map.base_position)
            if neighbors:
                drone.position = random.choice(neighbors)
                drone.path.append(drone.position)
                drone.visited.add(drone.position)
                drone.stuck_count = 0
                events_this_step.append(f"Dron {drone.id} reposicionado")
                
        # Registrar eventos
        if event and event != "stuck":
            events_this_step.append(f"Dron {drone.id} encontró {event}")
                
    # Calcular fitness para cada dron
    for drone in drones:
        fitness = calculate_fitness(drone, disaster_map)
        fitness_values.append(fitness)
        paths.append(drone.path)
            
    # Actualizar feromonas
    disaster_map.evaporate_pheromone()
    disaster_map.update_pheromone(paths, fitness_values)
        
    # Actualizar cobertura
    for drone in drones:
        for pos in drone.visited:
            disaster_map.covered[pos] = True
                
    # Calcular métricas
    total_covered = np.sum(disaster_map.covered)
    total_energy = sum(drone.energy_used for drone in drones)
    total_survivors_found = sum(drone.found_survivors for drone in drones)
    total_resources_found = sum(drone.found_resources for drone in drones)
    
    total_covered_history.append(total_covered)
    energy_consumed_history.append(total_energy)
    survivors_found_history.append(total_survivors_found)
    resources_found_history.append(total_resources_found)
    steps_history.append(frame)
    
    # Actualizar visualización del mapa (solo el fondo)
    grid_viz = np.zeros((MAP_SIZE, MAP_SIZE, 3))
    for r in range(MAP_SIZE):
        for c in range(MAP_SIZE):
            grid_viz[r, c] = COLORS[disaster_map.grid[r, c]]
    
    map_display.set_array(grid_viz)
    
    # Actualizar posiciones de los drones (todos rojos)
    drone_positions = np.array([drone.position for drone in drones])
    
    if len(drone_positions) > 0:
        # Invertir coordenadas Y para matplotlib
        drone_positions_display = np.column_stack([drone_positions[:, 1], drone_positions[:, 0]])
        drone_dots.set_offsets(drone_positions_display)
    
    # Actualizar gráficos de métricas
    total_cells = MAP_SIZE ** 2
    covered_percentage = [100 * x / total_cells for x in total_covered_history]
    
    coverage_line.set_data(steps_history, covered_percentage)
    energy_line.set_data(steps_history, energy_consumed_history)
    survivors_line.set_data(steps_history, survivors_found_history)
    resources_line.set_data(steps_history, resources_found_history)
    
    # Ajustar límites de los gráficos
    if steps_history:
        current_max_step = max(steps_history)
        ax2.set_xlim(0, current_max_step + 10)
        ax3.set_xlim(0, current_max_step + 10)
        ax4.set_xlim(0, current_max_step + 10)
        
        ax2.set_ylim(0, min(100, max(covered_percentage) + 10) if covered_percentage else 100)
        ax3.set_ylim(0, max(energy_consumed_history) + 50 if energy_consumed_history else 2000)
        max_obj = max(max(survivors_found_history) if survivors_found_history else 0, 
                     max(resources_found_history) if resources_found_history else 0)
        ax4.set_ylim(0, max_obj + 2)
    
    # Actualizar texto informativo
    info_text.set_text(f'Paso: {frame}\n'
                      f'Cobertura: {covered_percentage[-1]:.1f}%\n'
                      f'Supervivientes: {total_survivors_found}/{disaster_map.initial_survivors}\n'
                      f'Recursos: {total_resources_found}/{disaster_map.initial_resources}\n'
                      f'Energía: {total_energy}')
    
    # Mostrar eventos de este paso
    if events_this_step:
        for event in events_this_step:
            print(f"Paso {frame}: {event}")
    
    # Verificar si se cubrió el 100%
    if total_covered == MAP_SIZE ** 2:
        print(f"¡Cobertura del 100% alcanzada en el paso {frame}!")
        ani.event_source.stop()  # Detener la animación
            
    return map_display, drone_dots, coverage_line, energy_line, survivors_line, resources_line, info_text

# Crear animación
ani = FuncAnimation(fig, update_animation, frames=MAX_STEPS,
                    init_func=init_animation, blit=False, interval=150, repeat=False)

plt.tight_layout()

# Guardar GIF de la animación
print("Guardando animación como GIF...")
writer = PillowWriter(fps=10, bitrate=1800)
ani.save('drone_rescue_simulation.gif', writer=writer)
print("GIF guardado: drone_rescue_simulation.gif")

# Mostrar la animación
plt.show()

# Guardar imagen PNG final
print("Guardando imagen final PNG...")
final_fig = plt.figure(figsize=(14, 10))
final_gs = final_fig.add_gridspec(3, 2)

# Subplots para la imagen final
final_ax1 = final_fig.add_subplot(final_gs[0:2, 0])
final_ax2 = final_fig.add_subplot(final_gs[0, 1])
final_ax3 = final_fig.add_subplot(final_gs[1, 1])
final_ax4 = final_fig.add_subplot(final_gs[2, :])

# Crear visualización del estado final
grid_viz = np.zeros((MAP_SIZE, MAP_SIZE, 3))
for r in range(MAP_SIZE):
    for c in range(MAP_SIZE):
        grid_viz[r, c] = COLORS[disaster_map.grid[r, c]]

final_ax1.imshow(grid_viz)
final_ax1.set_title('Estado Final - Rescate con Drones')
final_ax1.set_xticks([])
final_ax1.set_yticks([])

# Añadir drones en rojo
drone_positions = np.array([drone.position for drone in drones])
if len(drone_positions) > 0:
    drone_positions_display = np.column_stack([drone_positions[:, 1], drone_positions[:, 0]])
    final_ax1.scatter(drone_positions_display[:, 0], drone_positions_display[:, 1], 
                     c='red', s=100, edgecolors='darkred', linewidths=2)

# Leyenda
final_ax1.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))

# Gráficos de métricas finales
total_cells = MAP_SIZE ** 2
covered_percentage = [100 * x / total_cells for x in total_covered_history]

final_ax2.plot(steps_history, covered_percentage, 'b-', linewidth=2)
final_ax2.set_xlim(0, max(steps_history) + 10 if steps_history else MAX_STEPS)
final_ax2.set_ylim(0, 100)
final_ax2.set_xlabel('Pasos')
final_ax2.set_ylabel('Cobertura (%)')
final_ax2.set_title('Cobertura del Área')
final_ax2.grid(True, alpha=0.3)

final_ax3.plot(steps_history, energy_consumed_history, 'r-', linewidth=2)
final_ax3.set_xlim(0, max(steps_history) + 10 if steps_history else MAX_STEPS)
final_ax3.set_ylim(0, max(energy_consumed_history) + 50 if energy_consumed_history else 2000)
final_ax3.set_xlabel('Pasos')
final_ax3.set_ylabel('Energía')
final_ax3.set_title('Energía Consumida')
final_ax3.grid(True, alpha=0.3)

final_ax4.plot(steps_history, survivors_found_history, 'g-', label='Supervivientes', linewidth=2)
final_ax4.plot(steps_history, resources_found_history, 'c-', label='Recursos', linewidth=2)
final_ax4.set_xlim(0, max(steps_history) + 10 if steps_history else MAX_STEPS)
max_obj = max(max(survivors_found_history) if survivors_found_history else 0, 
             max(resources_found_history) if resources_found_history else 0)
final_ax4.set_ylim(0, max_obj + 2)
final_ax4.set_xlabel('Pasos')
final_ax4.set_ylabel('Encontrados')
final_ax4.set_title('Objetivos Encontrados')
final_ax4.legend()
final_ax4.grid(True, alpha=0.3)

# Texto informativo final
final_coverage = 100 * total_covered_history[-1] / total_cells if total_covered_history else 0
final_info = (f'RESUMEN FINAL\n'
              f'Pasos totales: {steps_history[-1] if steps_history else 0}\n'
              f'Cobertura final: {final_coverage:.1f}%\n'
              f'Supervivientes: {survivors_found_history[-1] if survivors_found_history else 0}/{disaster_map.initial_survivors}\n'
              f'Recursos: {resources_found_history[-1] if resources_found_history else 0}/{disaster_map.initial_resources}\n'
              f'Energía total: {energy_consumed_history[-1] if energy_consumed_history else 0}')

final_fig.text(0.02, 0.95, final_info, fontsize=12, 
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

plt.tight_layout()
plt.savefig('drone_rescue_final.png', dpi=150, bbox_inches='tight')
plt.close()
print("Imagen final guardada: drone_rescue_final.png")

# Mostrar métricas finales después de la animación
if steps_history:
    final_coverage = 100 * total_covered_history[-1] / (MAP_SIZE ** 2)
    print(f"\n--- MÉTRICAS FINALES ---")
    print(f"Cobertura máxima: {final_coverage:.2f}%")
    print(f"Energía total consumida: {energy_consumed_history[-1]}")
    print(f"Supervivientes encontrados: {survivors_found_history[-1]}/{disaster_map.initial_survivors}")
    print(f"Recursos encontrados: {resources_found_history[-1]}/{disaster_map.initial_resources}")