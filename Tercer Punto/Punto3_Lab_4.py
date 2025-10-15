import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.animation import FuncAnimation, PillowWriter
import matplotlib.patches as mpatches
from matplotlib.markers import MarkerStyle

# Configuración de parámetros
GREENHOUSE_SIZE = 35
NUM_FLOWERS = 70
NUM_WORKER_DRONES = 12
NUM_OBSERVER_DRONES = 4
NUM_SCOUT_DRONES = 6  # Aumentado para mejor exploración
MAX_STEPS = 500
BASE_POSITION = (4, 4)
RECHARGE_THRESHOLD = 25

# Estados de los drones
WORKER = 0
OBSERVER = 1
SCOUT = 2
RECHARGING = 3

# Estados de las flores
FLOWER_IMMATURE = 0
FLOWER_READY = 1
FLOWER_POLLINATED = 2

# Colores para drones
DRONE_COLORS = {
    WORKER: [0.2, 0.6, 1.0],    # Azul para obreras
    OBSERVER: [1.0, 0.8, 0.2],  # Amarillo para observadoras
    SCOUT: [0.8, 0.2, 0.8],     # Magenta para exploradoras
    RECHARGING: [1.0, 0.0, 0.0] # Rojo para recargando
}

# Colores para flores
FLOWER_COLORS = {
    FLOWER_IMMATURE: [1.0, 0.5, 0.5],    # Rosa claro - inmadura
    FLOWER_READY: [1.0, 0.8, 0.2],       # Naranja - lista para polinizar
    FLOWER_POLLINATED: [0.2, 0.8, 0.2]   # Verde - polinizada
}

class Flower:
    def __init__(self, position, area_id):
        self.position = position
        self.area_id = area_id
        self.maturity = random.uniform(0.1, 0.3)
        self.state = FLOWER_IMMATURE
        self.pollen_level = 1.0
        self.pollination_count = 0
        self.size = 120
        # Formas diferentes para cada estado
        self.shape = {
            FLOWER_IMMATURE: 'h',  # Hexágono para inmaduras
            FLOWER_READY: '^',     # Triángulo para listas
            FLOWER_POLLINATED: 'D' # Diamante para polinizadas
        }
        
    def update_state(self):
        """Actualiza el estado de la flor basado en su madurez"""
        if self.maturity >= 0.75 and self.state != FLOWER_POLLINATED:
            self.state = FLOWER_READY
        elif self.maturity < 0.75:
            self.state = FLOWER_IMMATURE
            
    def pollinate(self, amount=0.25):
        """Realiza la polinización de la flor"""
        if self.state == FLOWER_READY and self.pollen_level > 0:
            old_maturity = self.maturity
            self.maturity = min(1.0, self.maturity + amount)
            self.pollen_level = max(0, self.pollen_level - amount/2)
            
            if self.maturity >= 0.95:
                self.state = FLOWER_POLLINATED
                self.size = 180
            return True
        return False
    
    def grow_naturally(self):
        """Crecimiento natural de la flor (sin polinización)"""
        if self.state != FLOWER_POLLINATED:
            self.maturity = min(0.75, self.maturity + 0.003)
            self.update_state()
        
    def get_priority(self):
        """Calcula la prioridad de la flor para polinización"""
        if self.state == FLOWER_POLLINATED:
            return 0
        elif self.state == FLOWER_READY:
            return 1.0
        else:
            return self.maturity * 0.7

class Area:
    def __init__(self, area_id, bounds):
        self.area_id = area_id
        self.bounds = bounds
        self.flowers = []
        self.observer_position = self.calculate_center()
        
    def calculate_center(self):
        """Calcula el centro del área para posicionar al drone observador"""
        x_min, x_max, y_min, y_max = self.bounds
        return ((x_min + x_max) // 2, (y_min + y_max) // 2)
    
    def add_flower(self, flower):
        """Añade una flor al área"""
        self.flowers.append(flower)
    
    def get_flowers_by_priority(self):
        """Obtiene las flores del área ordenadas por prioridad"""
        return sorted(self.flowers, key=lambda f: f.get_priority(), reverse=True)
    
    def get_ready_flowers(self):
        """Obtiene las flores listas para polinizar en esta área"""
        return [f for f in self.flowers if f.state == FLOWER_READY]

class Drone:
    def __init__(self, drone_id, position, drone_type, area_id=None):
        self.id = drone_id
        self.position = position
        self.type = drone_type
        self.area_id = area_id
        self.battery = 100.0
        self.target_flower = None
        self.visited_flowers = []
        self.pollination_count = 0
        self.energy_used = 0
        self.state = drone_type
        self.recharge_time = 0
        self.size = 100
        self.battery_drain_rate = random.uniform(0.4, 0.7)
        self.stuck_count = 0  # Contador para evitar que se atasquen
        
    def move_towards(self, target_pos):
        """Mueve el dron hacia la posición objetivo"""
        if self.position == target_pos:
            return True
            
        current_x, current_y = self.position
        target_x, target_y = target_pos
        
        # Movimiento más inteligente para exploradoras
        if self.type == SCOUT and random.random() < 0.4:
            # Movimiento más exploratorio para exploradoras
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            dx, dy = random.choice(directions)
            new_x = current_x + dx
            new_y = current_y + dy
        else:
            # Movimiento directo hacia el objetivo
            if abs(target_x - current_x) > abs(target_y - current_y):
                new_x = current_x + (1 if target_x > current_x else -1)
                new_y = current_y
            else:
                new_x = current_x
                new_y = current_y + (1 if target_y > current_y else -1)
            
        # Asegurar que no se sale del invernadero
        new_x = max(0, min(GREENHOUSE_SIZE-1, new_x))
        new_y = max(0, min(GREENHOUSE_SIZE-1, new_y))
            
        # Verificar si se movió
        if (new_x, new_y) == self.position:
            self.stuck_count += 1
        else:
            self.stuck_count = 0
            
        self.position = (new_x, new_y)
        self.consume_energy(self.battery_drain_rate)
        
        # Si está atascado por mucho tiempo, cambiar objetivo
        if self.stuck_count > 10:
            self.target_flower = None
            self.stuck_count = 0
            
        return self.position == target_pos
        
    def consume_energy(self, amount):
        """Consume energía del dron"""
        self.battery = max(0, self.battery - amount)
        self.energy_used += amount
        
        # Priorizar recarga si la batería es baja
        if self.battery <= RECHARGE_THRESHOLD and self.state != RECHARGING:
            self.state = RECHARGING
            self.target_flower = None
        
    def recharge(self):
        """Recarga la batería del dron"""
        recharge_rate = 2.5
        self.battery = min(100, self.battery + recharge_rate)
        self.recharge_time += 1
        
        if self.battery >= 95:
            self.state = self.type
            self.recharge_time = 0
            return True
        return False
        
    def update_state(self):
        """Actualiza el estado del dron basado en la batería"""
        if self.battery <= RECHARGE_THRESHOLD and self.state != RECHARGING:
            self.state = RECHARGING
            self.target_flower = None
        return self.state

class ABCPollination:
    def __init__(self, greenhouse_size, num_flowers, num_workers, num_observers, num_scouts):
        self.greenhouse_size = greenhouse_size
        self.flowers = []
        self.drones = []
        self.areas = []
        self.base_position = BASE_POSITION
        self.step_count = 0
        self.total_pollination = 0
        self.energy_consumed = 0
        
        self._initialize_areas()
        self._initialize_flowers(num_flowers)
        self._initialize_drones(num_workers, num_observers, num_scouts)
    
    def _initialize_areas(self):
        """Divide el invernadero en 4 áreas"""
        mid_x = self.greenhouse_size // 2
        mid_y = self.greenhouse_size // 2
        
        self.areas.append(Area(0, (0, mid_x, 0, mid_y)))
        self.areas.append(Area(1, (mid_x, self.greenhouse_size, 0, mid_y)))
        self.areas.append(Area(2, (0, mid_x, mid_y, self.greenhouse_size)))
        self.areas.append(Area(3, (mid_x, self.greenhouse_size, mid_y, self.greenhouse_size)))
    
    def _initialize_flowers(self, num_flowers):
        """Inicializa las flores distribuidas en las áreas"""
        for area in self.areas:
            x_min, x_max, y_min, y_max = area.bounds
            for _ in range(num_flowers // 4):
                x = random.randint(x_min + 2, x_max - 2)
                y = random.randint(y_min + 2, y_max - 2)
                flower = Flower((x, y), area.area_id)
                self.flowers.append(flower)
                area.add_flower(flower)
    
    def _initialize_drones(self, num_workers, num_observers, num_scouts):
        """Inicializa los drones con sus respectivas áreas"""
        drone_id = 0
        
        # Drones observadores (uno por área, posiciones fijas)
        for area in self.areas:
            self.drones.append(Drone(drone_id, area.observer_position, OBSERVER, area.area_id))
            drone_id += 1
            
        # Drones obreros (asignados a áreas específicas)
        workers_per_area = num_workers // len(self.areas)
        for area in self.areas:
            for i in range(workers_per_area):
                obs_x, obs_y = area.observer_position
                start_x = random.randint(max(0, obs_x-3), min(self.greenhouse_size-1, obs_x+3))
                start_y = random.randint(max(0, obs_y-3), min(self.greenhouse_size-1, obs_y+3))
                self.drones.append(Drone(drone_id, (start_x, start_y), WORKER, area.area_id))
                drone_id += 1
            
        # Drones exploradores (sin área específica)
        for i in range(num_scouts):
            start_x = random.randint(5, self.greenhouse_size-5)
            start_y = random.randint(5, self.greenhouse_size-5)
            self.drones.append(Drone(drone_id, (start_x, start_y), SCOUT))
            drone_id += 1
    
    def get_flower_at_position(self, position):
        """Obtiene la flor en una posición específica"""
        for flower in self.flowers:
            if flower.position == position:
                return flower
        return None
    
    def find_flower_for_worker(self, drone):
        """Encuentra una flor para un drone obrero en su área"""
        if drone.area_id is None:
            return None
            
        area = self.areas[drone.area_id]
        ready_flowers = area.get_ready_flowers()
        
        if ready_flowers:
            return ready_flowers[0]
        else:
            prioritized_flowers = area.get_flowers_by_priority()
            for flower in prioritized_flowers:
                if flower not in drone.visited_flowers[-5:]:
                    return flower
        return None
    
    def find_flower_for_scout(self, drone):
        """Encuentra una flor para un drone explorador en cualquier área"""
        # Buscar flores listas para polinizar en cualquier área
        all_ready_flowers = []
        for area in self.areas:
            all_ready_flowers.extend(area.get_ready_flowers())
        
        if all_ready_flowers:
            # Para exploradoras, elegir aleatoriamente entre flores listas
            available_flowers = [f for f in all_ready_flowers if f not in drone.visited_flowers[-3:]]
            if available_flowers:
                return random.choice(available_flowers)
        
        # Si no hay flores listas, buscar cualquier flor no polinizada
        all_flowers = []
        for area in self.areas:
            all_flowers.extend([f for f in area.flowers if f.state != FLOWER_POLLINATED])
        
        if all_flowers:
            available_flowers = [f for f in all_flowers if f not in drone.visited_flowers[-5:]]
            if available_flowers:
                return random.choice(available_flowers)
                
        # Si no hay flores disponibles, explorar áreas aleatorias
        return None
    
    def run_step(self):
        """Ejecuta un paso de simulación"""
        self.step_count += 1
        
        # Actualizar estado de las flores
        for flower in self.flowers:
            flower.grow_naturally()
            flower.update_state()
        
        # Procesar cada dron
        for drone in self.drones:
            # Actualizar estado basado en batería
            drone.update_state()
            
            if drone.state == RECHARGING:
                if drone.position != self.base_position:
                    drone.move_towards(self.base_position)
                else:
                    drone.recharge()
                continue
                
            # Drones observadores no se mueven
            if drone.type == OBSERVER:
                continue
                
            # Si no tiene objetivo, buscar uno según su tipo
            if drone.target_flower is None:
                if drone.type == WORKER:
                    drone.target_flower = self.find_flower_for_worker(drone)
                elif drone.type == SCOUT:
                    drone.target_flower = self.find_flower_for_scout(drone)
                    # Si no encuentra flor, moverse aleatoriamente
                    if drone.target_flower is None:
                        self._move_scout_randomly(drone)
                        continue
                
            # Si tiene objetivo, moverse hacia él
            if drone.target_flower:
                arrived = drone.move_towards(drone.target_flower.position)
                
                if arrived:
                    # Polinizar la flor
                    flower = self.get_flower_at_position(drone.position)
                    if flower and flower.pollinate():
                        drone.pollination_count += 1
                        flower.pollination_count += 1
                        self.total_pollination += 0.25
                    
                    # Marcar como visitada y buscar nuevo objetivo
                    if flower and flower not in drone.visited_flowers:
                        drone.visited_flowers.append(flower)
                    
                    drone.target_flower = None
                    drone.consume_energy(0.3)
        
        # Calcular energía total consumida
        self.energy_consumed = sum(drone.energy_used for drone in self.drones)
        
        # Verificar si todas las flores están completamente polinizadas
        all_pollinated = all(flower.state == FLOWER_POLLINATED for flower in self.flowers)
        return all_pollinated
    
    def _move_scout_randomly(self, drone):
        """Mueve un drone explorador aleatoriamente cuando no tiene objetivo"""
        if random.random() < 0.7:  # 70% de probabilidad de moverse
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            dx, dy = random.choice(directions)
            new_x = drone.position[0] + dx
            new_y = drone.position[1] + dy
            
            # Asegurar que no se sale del invernadero
            new_x = max(0, min(self.greenhouse_size-1, new_x))
            new_y = max(0, min(self.greenhouse_size-1, new_y))
            
            drone.position = (new_x, new_y)
            drone.consume_energy(drone.battery_drain_rate * 0.5)  # Menor consumo en movimiento aleatorio

# Configuración de la figura con más espacio para la leyenda
fig = plt.figure(figsize=(22, 12))
gs = fig.add_gridspec(2, 3, width_ratios=[1.5, 1, 1], height_ratios=[1, 1])

# Subplots
ax1 = fig.add_subplot(gs[:, 0])  # Mapa principal
ax2 = fig.add_subplot(gs[0, 1])  # Polinización
ax3 = fig.add_subplot(gs[0, 2])  # Energía
ax4 = fig.add_subplot(gs[1, 1])  # Eficiencia por tipo
ax5 = fig.add_subplot(gs[1, 2])  # Estado de flores

# Inicializar simulación
abc_sim = ABCPollination(GREENHOUSE_SIZE, NUM_FLOWERS, 
                        NUM_WORKER_DRONES, NUM_OBSERVER_DRONES, NUM_SCOUT_DRONES)

# Configurar el mapa principal
ax1.set_xlim(0, GREENHOUSE_SIZE)
ax1.set_ylim(0, GREENHOUSE_SIZE)
ax1.set_aspect('equal')
ax1.set_title('SISTEMA DE POLINIZACIÓN CON DRONES - ALGORITMO ABC', 
              fontsize=16, fontweight='bold', pad=20)
ax1.set_xlabel('Coordenada X', fontsize=12)
ax1.set_ylabel('Coordenada Y', fontsize=12)

# Dibujar división de áreas
mid_x = GREENHOUSE_SIZE // 2
mid_y = GREENHOUSE_SIZE // 2
ax1.axvline(x=mid_x, color='gray', linestyle='--', alpha=0.5, linewidth=2)
ax1.axhline(y=mid_y, color='gray', linestyle='--', alpha=0.5, linewidth=2)

# Etiquetar áreas
ax1.text(mid_x/2, mid_y/2, 'ÁREA 0', ha='center', va='center', 
         fontweight='bold', fontsize=11, alpha=0.7)
ax1.text(mid_x*1.5, mid_y/2, 'ÁREA 1', ha='center', va='center', 
         fontweight='bold', fontsize=11, alpha=0.7)
ax1.text(mid_x/2, mid_y*1.5, 'ÁREA 2', ha='center', va='center', 
         fontweight='bold', fontsize=11, alpha=0.7)
ax1.text(mid_x*1.5, mid_y*1.5, 'ÁREA 3', ha='center', va='center', 
         fontweight='bold', fontsize=11, alpha=0.7)

# Base de recarga
base_circle = plt.Circle(BASE_POSITION, 2.0, color='gray', alpha=0.7)
ax1.add_patch(base_circle)
ax1.text(BASE_POSITION[0], BASE_POSITION[1], 'BASE', ha='center', va='center', 
         fontweight='bold', color='white', fontsize=10)

# Elementos gráficos para flores y drones
# Scatter plots separados para cada tipo de flor con formas diferentes
immature_flowers_scatter = ax1.scatter([], [], s=[], c=[], marker='H', alpha=0.8, 
                                       edgecolors='darkred', linewidths=1.5)
ready_flowers_scatter = ax1.scatter([], [], s=[], c=[], marker='^', alpha=0.8, 
                                    edgecolors='darkorange', linewidths=1.5)
pollinated_flowers_scatter = ax1.scatter([], [], s=[], c=[], marker='D', alpha=0.8, 
                                         edgecolors='darkgreen', linewidths=1.5)

# Drones con forma circular
drone_scatter = ax1.scatter([], [], s=[], c=[], alpha=1.0, 
                            edgecolors='black', linewidths=2, marker='o')

# LEYENDA MEJORADA - Fuera del área del gráfico
legend_elements = [
    mpatches.Patch(color=DRONE_COLORS[WORKER], label='Obreras'),
    mpatches.Patch(color=DRONE_COLORS[OBSERVER], label='Observadoras'),
    mpatches.Patch(color=DRONE_COLORS[SCOUT], label='Exploradoras'),
    mpatches.Patch(color=DRONE_COLORS[RECHARGING], label='Recargando'),
    plt.Line2D([0], [0], marker='H', color='w', markerfacecolor=FLOWER_COLORS[FLOWER_IMMATURE], 
               markersize=10, label='Flores Inmaduras (Hexágono)'),
    plt.Line2D([0], [0], marker='^', color='w', markerfacecolor=FLOWER_COLORS[FLOWER_READY], 
               markersize=10, label='Flores Listas (Triángulo)'),
    plt.Line2D([0], [0], marker='D', color='w', markerfacecolor=FLOWER_COLORS[FLOWER_POLLINATED], 
               markersize=10, label='Flores Polinizadas (Diamante)')
]

# Crear una leyenda separada fuera del gráfico principal
fig.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(0.92, 0.5), 
           fontsize=12, title="LEYENDA", title_fontsize=13, frameon=True, 
           fancybox=True, shadow=True, ncol=1)

# Gráficos de métricas
maturity_line, = ax2.plot([], [], 'g-', linewidth=3)
ax2.set_xlim(0, MAX_STEPS)
ax2.set_ylim(0, 100)
ax2.set_xlabel('Pasos', fontsize=11)
ax2.set_ylabel('Polinización (%)', fontsize=11)
ax2.set_title('PROGRESO DE POLINIZACIÓN', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.tick_params(axis='both', which='major', labelsize=10)

energy_line, = ax3.plot([], [], 'r-', linewidth=3)
ax3.set_xlim(0, MAX_STEPS)
ax3.set_ylim(0, 1000)
ax3.set_xlabel('Pasos', fontsize=11)
ax3.set_ylabel('Energía Consumida', fontsize=11)
ax3.set_title('ENERGÍA TOTAL CONSUMIDA', fontsize=13, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.tick_params(axis='both', which='major', labelsize=10)

worker_line, = ax4.plot([], [], 'b-', label='Obreras', linewidth=3)
scout_line, = ax4.plot([], [], 'm-', label='Exploradoras', linewidth=3)
ax4.set_xlim(0, MAX_STEPS)
ax4.set_ylim(0, 100)
ax4.set_xlabel('Pasos', fontsize=11)
ax4.set_ylabel('Polinizaciones', fontsize=11)
ax4.set_title('EFICIENCIA POR TIPO DE DRON', fontsize=13, fontweight='bold')
ax4.legend(fontsize=11)
ax4.grid(True, alpha=0.3)
ax4.tick_params(axis='both', which='major', labelsize=10)

# Gráfico de estado de flores
flower_state_bars = ax5.bar([0, 1, 2], [0, 0, 0], 
                           color=[FLOWER_COLORS[FLOWER_IMMATURE], 
                                  FLOWER_COLORS[FLOWER_READY], 
                                  FLOWER_COLORS[FLOWER_POLLINATED]],
                           width=0.6)
ax5.set_ylim(0, NUM_FLOWERS)
ax5.set_xlabel('Estado de Flores', fontsize=11)
ax5.set_ylabel('Cantidad', fontsize=11)
ax5.set_title('DISTRIBUCIÓN DE ESTADOS DE FLORES', fontsize=13, fontweight='bold')
ax5.set_xticks([0, 1, 2])
ax5.set_xticklabels(['Inmaduras', 'Listas', 'Polinizadas'], fontsize=10)
ax5.tick_params(axis='both', which='major', labelsize=10)

# Texto informativo - Fuera del área del gráfico
info_text = fig.text(0.02, 0.95, '', transform=fig.transFigure, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9),
                    fontsize=11, fontweight='bold')

# Métricas para gráficos
steps_history = []
maturity_history = []
energy_history = []
worker_pollination_history = []
scout_pollination_history = []

def init_animation():
    immature_flowers_scatter.set_offsets(np.empty((0, 2)))
    immature_flowers_scatter.set_sizes(np.empty(0))
    immature_flowers_scatter.set_color(np.empty((0, 3)))
    
    ready_flowers_scatter.set_offsets(np.empty((0, 2)))
    ready_flowers_scatter.set_sizes(np.empty(0))
    ready_flowers_scatter.set_color(np.empty((0, 3)))
    
    pollinated_flowers_scatter.set_offsets(np.empty((0, 2)))
    pollinated_flowers_scatter.set_sizes(np.empty(0))
    pollinated_flowers_scatter.set_color(np.empty((0, 3)))
    
    drone_scatter.set_offsets(np.empty((0, 2)))
    drone_scatter.set_sizes(np.empty(0))
    drone_scatter.set_color(np.empty((0, 3)))
    
    maturity_line.set_data([], [])
    energy_line.set_data([], [])
    worker_line.set_data([], [])
    scout_line.set_data([], [])
    
    info_text.set_text('INICIANDO SIMULACIÓN...\nPreparando drones y flores...')
    
    return (immature_flowers_scatter, ready_flowers_scatter, pollinated_flowers_scatter,
            drone_scatter, maturity_line, energy_line, worker_line, scout_line, info_text)

def update_animation(frame):
    global abc_sim
    
    # Ejecutar un paso de simulación
    all_pollinated = abc_sim.run_step()
    
    # Separar flores por estado
    immature_flowers = [f for f in abc_sim.flowers if f.state == FLOWER_IMMATURE]
    ready_flowers = [f for f in abc_sim.flowers if f.state == FLOWER_READY]
    pollinated_flowers = [f for f in abc_sim.flowers if f.state == FLOWER_POLLINATED]
    
    # Preparar datos para visualización de flores
    immature_positions = [f.position for f in immature_flowers]
    immature_sizes = [f.size for f in immature_flowers]
    immature_colors = [FLOWER_COLORS[FLOWER_IMMATURE] for _ in immature_flowers]
    
    ready_positions = [f.position for f in ready_flowers]
    ready_sizes = [f.size for f in ready_flowers]
    ready_colors = [FLOWER_COLORS[FLOWER_READY] for _ in ready_flowers]
    
    pollinated_positions = [f.position for f in pollinated_flowers]
    pollinated_sizes = [f.size for f in pollinated_flowers]
    pollinated_colors = [FLOWER_COLORS[FLOWER_POLLINATED] for _ in pollinated_flowers]
    
    # Preparar datos para drones
    drone_positions = [d.position for d in abc_sim.drones]
    drone_sizes = [d.size for d in abc_sim.drones]
    drone_colors = [DRONE_COLORS[d.state] for d in abc_sim.drones]
    
    # Actualizar scatter plots de flores
    if immature_positions:
        immature_flowers_scatter.set_offsets(immature_positions)
        immature_flowers_scatter.set_sizes(immature_sizes)
        immature_flowers_scatter.set_color(immature_colors)
    else:
        immature_flowers_scatter.set_offsets(np.empty((0, 2)))
    
    if ready_positions:
        ready_flowers_scatter.set_offsets(ready_positions)
        ready_flowers_scatter.set_sizes(ready_sizes)
        ready_flowers_scatter.set_color(ready_colors)
    else:
        ready_flowers_scatter.set_offsets(np.empty((0, 2)))
    
    if pollinated_positions:
        pollinated_flowers_scatter.set_offsets(pollinated_positions)
        pollinated_flowers_scatter.set_sizes(pollinated_sizes)
        pollinated_flowers_scatter.set_color(pollinated_colors)
    else:
        pollinated_flowers_scatter.set_offsets(np.empty((0, 2)))
    
    # Actualizar scatter plot de drones
    if drone_positions:
        drone_scatter.set_offsets(drone_positions)
        drone_scatter.set_sizes(drone_sizes)
        drone_scatter.set_color(drone_colors)
    
    # Calcular métricas
    pollinated_count = len(pollinated_flowers)
    pollinated_percentage = (pollinated_count / len(abc_sim.flowers)) * 100
    
    worker_pollinations = sum(d.pollination_count for d in abc_sim.drones if d.type == WORKER)
    scout_pollinations = sum(d.pollination_count for d in abc_sim.drones if d.type == SCOUT)
    
    # Contar flores por estado
    immature_count = len(immature_flowers)
    ready_count = len(ready_flowers)
    pollinated_count = len(pollinated_flowers)
    
    # Contar drones exploradores activos
    active_scouts = sum(1 for d in abc_sim.drones if d.type == SCOUT and d.state != RECHARGING)
    
    # Contar drones recargando
    recharging_drones = sum(1 for d in abc_sim.drones if d.state == RECHARGING)
    
    # Actualizar historiales
    steps_history.append(frame)
    maturity_history.append(pollinated_percentage)
    energy_history.append(abc_sim.energy_consumed)
    worker_pollination_history.append(worker_pollinations)
    scout_pollination_history.append(scout_pollinations)
    
    # Actualizar gráficos
    maturity_line.set_data(steps_history, maturity_history)
    energy_line.set_data(steps_history, energy_history)
    worker_line.set_data(steps_history, worker_pollination_history)
    scout_line.set_data(steps_history, scout_pollination_history)
    
    # Actualizar barras de estado de flores
    for bar, height in zip(flower_state_bars, [immature_count, ready_count, pollinated_count]):
        bar.set_height(height)
    
    # Ajustar límites de los gráficos
    if steps_history:
        current_max_step = max(steps_history)
        ax2.set_xlim(0, current_max_step + 10)
        ax3.set_xlim(0, current_max_step + 10)
        ax4.set_xlim(0, current_max_step + 10)
        
        ax2.set_ylim(0, min(100, max(maturity_history) + 10) if maturity_history else 100)
        ax3.set_ylim(0, max(energy_history) + 50 if energy_history else 1000)
        max_poll = max(max(worker_pollination_history) if worker_pollination_history else 0,
                      max(scout_pollination_history) if scout_pollination_history else 0)
        ax4.set_ylim(0, max_poll + 5)
    
    # Actualizar texto informativo
    avg_battery = np.mean([d.battery for d in abc_sim.drones])
    
    info_text.set_text(f'PASO: {frame}\n'
                      f'FLORES POLINIZADAS: {pollinated_count}/{len(abc_sim.flowers)}\n'
                      f'FLORES LISTAS: {ready_count}\n'
                      f'EXPLORADORAS ACTIVAS: {active_scouts}/{NUM_SCOUT_DRONES}\n'
                      f'DRONES ACTIVOS: {len(abc_sim.drones) - recharging_drones}/{len(abc_sim.drones)}\n'
                      f'BATERÍA PROMEDIO: {avg_battery:.1f}%')
    
    # Verificar si se completó la polinización
    if all_pollinated:
        print(f"¡Polinización completa alcanzada en el paso {frame}!")
        return (immature_flowers_scatter, ready_flowers_scatter, pollinated_flowers_scatter,
                drone_scatter, maturity_line, energy_line, worker_line, scout_line, info_text)
    
    if frame >= MAX_STEPS - 1:
        print("Límite de pasos alcanzado")
        return (immature_flowers_scatter, ready_flowers_scatter, pollinated_flowers_scatter,
                drone_scatter, maturity_line, energy_line, worker_line, scout_line, info_text)
            
    return (immature_flowers_scatter, ready_flowers_scatter, pollinated_flowers_scatter,
            drone_scatter, maturity_line, energy_line, worker_line, scout_line, info_text)

# Crear animación
ani = FuncAnimation(fig, update_animation, frames=MAX_STEPS,
                    init_func=init_animation, blit=False, interval=100, repeat=False)

# Ajustar el layout para dar espacio a la leyenda
plt.tight_layout()
plt.subplots_adjust(right=0.88)  # Dejar espacio a la derecha para la leyenda

# Guardar GIF de la animación
print("Guardando animación como GIF...")
writer = PillowWriter(fps=10, bitrate=1800)
ani.save('bee_drone_pollination.gif', writer=writer)
print("GIF guardado: bee_drone_pollination.gif")

# Mostrar la animación
plt.show()

# Guardar imagen PNG final
print("Guardando imagen final PNG...")
final_fig = plt.figure(figsize=(20, 12))
final_gs = final_fig.add_gridspec(2, 3, width_ratios=[1.5, 1, 1], height_ratios=[1, 1])

# Subplots para la imagen final
final_ax1 = final_fig.add_subplot(final_gs[:, 0])
final_ax2 = final_fig.add_subplot(final_gs[0, 1])
final_ax3 = final_fig.add_subplot(final_gs[1, 1])
final_ax4 = final_fig.add_subplot(final_gs[0, 2])
final_ax5 = final_fig.add_subplot(final_gs[1, 2])

# Crear visualización del estado final
final_ax1.set_xlim(0, GREENHOUSE_SIZE)
final_ax1.set_ylim(0, GREENHOUSE_SIZE)
final_ax1.set_aspect('equal')
final_ax1.set_title('ESTADO FINAL - SISTEMA DE POLINIZACIÓN CON DRONES', 
                    fontsize=16, fontweight='bold', pad=20)

# Dibujar división de áreas en la imagen final
final_ax1.axvline(x=mid_x, color='gray', linestyle='--', alpha=0.5, linewidth=2)
final_ax1.axhline(y=mid_y, color='gray', linestyle='--', alpha=0.5, linewidth=2)

# Etiquetar áreas en imagen final
final_ax1.text(mid_x/2, mid_y/2, 'ÁREA 0', ha='center', va='center', 
               fontweight='bold', fontsize=11, alpha=0.7)
final_ax1.text(mid_x*1.5, mid_y/2, 'ÁREA 1', ha='center', va='center', 
               fontweight='bold', fontsize=11, alpha=0.7)
final_ax1.text(mid_x/2, mid_y*1.5, 'ÁREA 2', ha='center', va='center', 
               fontweight='bold', fontsize=11, alpha=0.7)
final_ax1.text(mid_x*1.5, mid_y*1.5, 'ÁREA 3', ha='center', va='center', 
               fontweight='bold', fontsize=11, alpha=0.7)

# Base de recarga
final_base_circle = plt.Circle(BASE_POSITION, 2.0, color='gray', alpha=0.7)
final_ax1.add_patch(final_base_circle)
final_ax1.text(BASE_POSITION[0], BASE_POSITION[1], 'BASE', ha='center', va='center', 
               fontweight='bold', color='white', fontsize=10)

# Separar flores por estado para la imagen final
immature_flowers = [f for f in abc_sim.flowers if f.state == FLOWER_IMMATURE]
ready_flowers = [f for f in abc_sim.flowers if f.state == FLOWER_READY]
pollinated_flowers = [f for f in abc_sim.flowers if f.state == FLOWER_POLLINATED]

# Dibujar flores en la imagen final
if immature_flowers:
    immature_positions = [f.position for f in immature_flowers]
    immature_sizes = [f.size for f in immature_flowers]
    final_ax1.scatter([p[0] for p in immature_positions], [p[1] for p in immature_positions], 
                     s=immature_sizes, c=[FLOWER_COLORS[FLOWER_IMMATURE] for _ in immature_flowers], 
                     marker='H', alpha=0.8, edgecolors='darkred', linewidths=1.5)

if ready_flowers:
    ready_positions = [f.position for f in ready_flowers]
    ready_sizes = [f.size for f in ready_flowers]
    final_ax1.scatter([p[0] for p in ready_positions], [p[1] for p in ready_positions], 
                     s=ready_sizes, c=[FLOWER_COLORS[FLOWER_READY] for _ in ready_flowers], 
                     marker='^', alpha=0.8, edgecolors='darkorange', linewidths=1.5)

if pollinated_flowers:
    pollinated_positions = [f.position for f in pollinated_flowers]
    pollinated_sizes = [f.size for f in pollinated_flowers]
    final_ax1.scatter([p[0] for p in pollinated_positions], [p[1] for p in pollinated_positions], 
                     s=pollinated_sizes, c=[FLOWER_COLORS[FLOWER_POLLINATED] for _ in pollinated_flowers], 
                     marker='D', alpha=0.8, edgecolors='darkgreen', linewidths=1.5)

# Dibujar drones en la imagen final
drone_positions = [d.position for d in abc_sim.drones]
drone_sizes = [d.size for d in abc_sim.drones]
drone_colors = [DRONE_COLORS[d.state] for d in abc_sim.drones]
final_ax1.scatter([p[0] for p in drone_positions], [p[1] for p in drone_positions], 
                 s=drone_sizes, c=drone_colors, alpha=1.0, 
                 edgecolors='black', linewidths=2, marker='o')

# Gráficos de métricas finales
total_cells = GREENHOUSE_SIZE ** 2
covered_percentage = [100 * x / total_cells for x in maturity_history]

final_ax2.plot(steps_history, maturity_history, 'g-', linewidth=3)
final_ax2.set_xlim(0, max(steps_history) + 10 if steps_history else MAX_STEPS)
final_ax2.set_ylim(0, 100)
final_ax2.set_xlabel('Pasos', fontsize=11)
final_ax2.set_ylabel('Polinización (%)', fontsize=11)
final_ax2.set_title('PROGRESO DE POLINIZACIÓN', fontsize=13, fontweight='bold')
final_ax2.grid(True, alpha=0.3)

final_ax3.plot(steps_history, energy_history, 'r-', linewidth=3)
final_ax3.set_xlim(0, max(steps_history) + 10 if steps_history else MAX_STEPS)
final_ax3.set_ylim(0, max(energy_history) + 50 if energy_history else 1000)
final_ax3.set_xlabel('Pasos', fontsize=11)
final_ax3.set_ylabel('Energía Consumida', fontsize=11)
final_ax3.set_title('ENERGÍA TOTAL CONSUMIDA', fontsize=13, fontweight='bold')
final_ax3.grid(True, alpha=0.3)

final_ax4.plot(steps_history, worker_pollination_history, 'b-', label='Obreras', linewidth=3)
final_ax4.plot(steps_history, scout_pollination_history, 'm-', label='Exploradoras', linewidth=3)
final_ax4.set_xlim(0, max(steps_history) + 10 if steps_history else MAX_STEPS)
max_poll = max(max(worker_pollination_history) if worker_pollination_history else 0,
              max(scout_pollination_history) if scout_pollination_history else 0)
final_ax4.set_ylim(0, max_poll + 5)
final_ax4.set_xlabel('Pasos', fontsize=11)
final_ax4.set_ylabel('Polinizaciones', fontsize=11)
final_ax4.set_title('EFICIENCIA POR TIPO DE DRON', fontsize=13, fontweight='bold')
final_ax4.legend()
final_ax4.grid(True, alpha=0.3)

# Gráfico de estado de flores final
final_flower_counts = [len(immature_flowers), len(ready_flowers), len(pollinated_flowers)]
final_flower_bars = final_ax5.bar([0, 1, 2], final_flower_counts,
                                color=[FLOWER_COLORS[FLOWER_IMMATURE], 
                                       FLOWER_COLORS[FLOWER_READY], 
                                       FLOWER_COLORS[FLOWER_POLLINATED]],
                                width=0.6)
final_ax5.set_ylim(0, NUM_FLOWERS)
final_ax5.set_xlabel('Estado de Flores', fontsize=11)
final_ax5.set_ylabel('Cantidad', fontsize=11)
final_ax5.set_title('DISTRIBUCIÓN FINAL DE FLORES', fontsize=13, fontweight='bold')
final_ax5.set_xticks([0, 1, 2])
final_ax5.set_xticklabels(['Inmaduras', 'Listas', 'Polinizadas'], fontsize=10)

# Añadir valores en las barras
for i, v in enumerate(final_flower_counts):
    final_ax5.text(i, v + 0.5, str(v), ha='center', va='bottom', fontweight='bold')

# Texto informativo final
final_pollinated_percentage = (len(pollinated_flowers) / len(abc_sim.flowers)) * 100
final_worker_pollinations = sum(d.pollination_count for d in abc_sim.drones if d.type == WORKER)
final_scout_pollinations = sum(d.pollination_count for d in abc_sim.drones if d.type == SCOUT)
final_avg_battery = np.mean([d.battery for d in abc_sim.drones])

final_info = (f'RESUMEN FINAL - POLINIZACIÓN CON DRONES\n\n'
              f'Pasos totales: {steps_history[-1] if steps_history else 0}\n'
              f'Flores polinizadas: {len(pollinated_flowers)}/{len(abc_sim.flowers)}\n'
              f'Porcentaje de polinización: {final_pollinated_percentage:.1f}%\n'
              f'Polinizaciones por obreras: {final_worker_pollinations}\n'
              f'Polinizaciones por exploradoras: {final_scout_pollinations}\n'
              f'Energía total consumida: {energy_history[-1]:.1f}\n'
              f'Batería promedio final: {final_avg_battery:.1f}%')

final_fig.text(0.02, 0.95, final_info, transform=final_fig.transFigure, 
               verticalalignment='top', fontsize=12, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9))

# Leyenda en la imagen final
final_fig.legend(handles=legend_elements, loc='center right', 
                 bbox_to_anchor=(0.98, 0.5), fontsize=11, 
                 title="LEYENDA", title_fontsize=12)

plt.tight_layout()
plt.subplots_adjust(right=0.85)
plt.savefig('bee_drone_pollination_final.png', dpi=150, bbox_inches='tight')
plt.close()
print("Imagen final guardada: bee_drone_pollination_final.png")

# Mostrar métricas finales
if steps_history:
    print(f"\n--- MÉTRICAS FINALES DE POLINIZACIÓN ---")
    print(f"Flores polinizadas: {sum(1 for f in abc_sim.flowers if f.state == FLOWER_POLLINATED)}/{len(abc_sim.flowers)}")
    print(f"Porcentaje de polinización: {final_pollinated_percentage:.2f}%")
    print(f"Energía total consumida: {energy_history[-1]:.2f}")
    print(f"Polinizaciones por obreras: {worker_pollination_history[-1]}")
    print(f"Polinizaciones por exploradoras: {scout_pollination_history[-1]}")
    print(f"Total de polinizaciones: {worker_pollination_history[-1] + scout_pollination_history[-1]}")
    print(f"Batería promedio final: {np.mean([d.battery for d in abc_sim.drones]):.1f}%")