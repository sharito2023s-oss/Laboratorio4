import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import os

class DroneFormationPSO:
    def __init__(self, max_iter=100):
        self.bounds = [-8, 8]
        # Tres formaciones: cabeza de robot, estrella y cabeza de dragón
        self.formations = [
            self.create_robot_head_pattern(),
            self.create_star_pattern(),
            self.create_dragon_head_pattern()
        ]
        self.current_formation_index = 0
        self.target_formation = self.formations[self.current_formation_index]
        self.n_drones = len(self.target_formation)

        # Obstáculos: cerca pero sin tocar la figura
        self.obstacles = [
            {'center': np.array([-5.5, 0.0]), 'radius': 1.2},
            {'center': np.array([5.5, 0.0]), 'radius': 1.2},
            {'center': np.array([0.0, 5.8]), 'radius': 1.2},
            {'center': np.array([0.0, -5.8]), 'radius': 1.2},
            {'center': np.array([-4.8, -4.8]), 'radius': 1.0},
            {'center': np.array([4.8, -4.8]), 'radius': 1.0},
            {'center': np.array([-4.8, 4.8]), 'radius': 1.0},
            {'center': np.array([4.8, 4.8]), 'radius': 1.0}
        ]

        # Inicializar drones en el borde
        self.drones = self.initialize_drones_on_border(self.n_drones)
        self.velocities = np.random.uniform(-0.5, 0.5, (self.n_drones, 2))

        # Mejor fitness
        self.personal_best = self.drones.copy()
        self.personal_best_fitness = np.array([self.fitness(p, i) for i, p in enumerate(self.drones)])
        self.global_best_fitness = np.min(self.personal_best_fitness)

        self.history = [self.drones.copy()]
        self.max_iter = max_iter
        self.best_fitness_history = [self.global_best_fitness]

        self.arrived = np.zeros(self.n_drones, dtype=bool)
        
        # Para rastrear qué objetivos deben mostrarse
        self.targets_visible = np.ones(self.n_drones, dtype=bool)
        
        # Historial de visibilidad de objetivos
        self.history_targets_visible = [self.targets_visible.copy()]
        
        # Historial de índices de formación
        self.history_formation_index = [0]
        
        # Contador de iteraciones por formación
        self.formation_iterations = 0
        self.max_formation_iterations = 100  # Máximo de iteraciones por formación
        
        # Para guardar imágenes de cada formación completada
        self.formation_completed_frames = []

    def initialize_drones_on_border(self, n_drones):
        """Inicializa los drones en posiciones aleatorias en el borde del área"""
        drones = []
        border_margin = 0.5  # Pequeño margen desde el borde exacto
        
        for _ in range(n_drones):
            # Elegir un lado del borde aleatoriamente (0: arriba, 1: derecha, 2: abajo, 3: izquierda)
            side = np.random.randint(0, 4)
            
            if side == 0:  # Borde superior
                x = np.random.uniform(self.bounds[0] + border_margin, self.bounds[1] - border_margin)
                y = self.bounds[1] - border_margin
            elif side == 1:  # Borde derecho
                x = self.bounds[1] - border_margin
                y = np.random.uniform(self.bounds[0] + border_margin, self.bounds[1] - border_margin)
            elif side == 2:  # Borde inferior
                x = np.random.uniform(self.bounds[0] + border_margin, self.bounds[1] - border_margin)
                y = self.bounds[0] + border_margin
            else:  # Borde izquierdo
                x = self.bounds[0] + border_margin
                y = np.random.uniform(self.bounds[0] + border_margin, self.bounds[1] - border_margin)
            
            drones.append([x, y])
        
        return np.array(drones)

    # ======== Formaciones ========
    def create_robot_head_pattern(self, center=[0.0, 0.0]):
        formation = []
        spacing_x, spacing_y = 0.5, 0.5
        pattern = [
            [0,0,1,0,0,0,0,0,1,0,0], 
            [0,0,1,0,0,0,0,0,1,0,0],
            [0,0,1,0,0,0,0,0,1,0,0],
            [1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,1,0,1,1,1,0,1], 
            [1,0,1,0,1,0,1,0,1,0,1], 
            [1,0,1,1,1,0,1,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,1,1,1,1,1,0,0,1],
            [1,0,0,1,0,0,0,1,0,0,1],
            [1,0,0,1,1,1,1,1,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1],
        ]
        rows, cols = len(pattern), len(pattern[0])
        for row in range(rows):
            for col in range(cols):
                if pattern[row][col] == 1:
                    x = center[0] + (col - cols/2 + 0.5) * spacing_x
                    y = center[1] + (rows/2 - row - 0.5) * spacing_y
                    formation.append([x, y])
        return np.array(formation)

    def create_star_pattern(self, center=[0.0, 0.0], spacing=0.8):
        """Estrella basada en el patrón específico proporcionado"""
        formation = []
        
        # Definir el patrón de la estrella según el diseño proporcionado
        star_pattern = [
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],  # Fila 0:                     x
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # Fila 1:                     x
            [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0],  # Fila 2:                   x   x
            [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0],  # Fila 3: x x x x         x x x x
            [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],  # Fila 4:     x               x
            [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],  # Fila 5:       x           x        x       x
            [0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0],  # Fila 7:       x   x   x
            [0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0],  # Fila 8:       x x     x x
            [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]   # Fila 9:       x         x
        ]
        
        rows = len(star_pattern)
        cols = len(star_pattern[0])
        
        for row in range(rows):
            for col in range(cols):
                if star_pattern[row][col] == 1:
                    x = center[0] + (col - cols/2 + 0.5) * spacing
                    y = center[1] + (rows/2 - row - 0.5) * spacing
                    formation.append([x, y])
                    
        return np.array(formation)

    def create_dragon_head_pattern(self, center=[0.0, 0.0], spacing=0.7):
        """Cabeza de dragón según el patrón proporcionado con 'x'."""
        formation = []
        # Patrón del dragón (cada '1' representa un dron)
        dragon_pattern = [
            [0,0,0,0,1,0,1,0,0,0,1,0,0,0,0],
            [0,0,0,0,1,0,1,0,0,0,1,0,0,0,0],
            [0,0,0,0,1,0,1,1,1,1,1,0,0,0,0],
            [0,0,0,0,1,1,0,0,0,0,1,0,0,0,0],
            [0,0,0,0,1,1,0,0,1,0,0,1,0,0,0],
            [0,0,0,0,1,0,0,0,0,0,0,1,0,0,0],
            [0,0,0,1,0,0,0,0,0,0,1,1,1,1,0],
            [0,0,0,1,0,0,0,0,0,0,0,0,0,1,0],
            [0,0,0,1,0,0,0,0,0,0,1,1,1,1,0],
            [0,0,1,0,0,0,1,1,1,1,1,0,0,0,0],
            [0,0,1,0,0,0,1,0,0,0,0,0,0,0,0],
            [0,0,0,0,1,0,0,0,0,0,0,0,0,0,0],
        ]

        rows, cols = len(dragon_pattern), len(dragon_pattern[0])

        for row in range(rows):
            for col in range(cols):
                if dragon_pattern[row][col] == 1:
                    x = center[0] + (col - cols / 2 + 0.5) * spacing
                    y = center[1] + (rows / 2 - row - 0.5) * spacing
                    formation.append([x, y])

        return np.array(formation)

    # ======== Movimiento ========
    def fitness(self, position, drone_idx):
        target_pos = self.target_formation[drone_idx]
        distance_to_target = np.linalg.norm(position - target_pos)
        obstacle_penalty = 0
        for obstacle in self.obstacles:
            dist = np.linalg.norm(position - obstacle['center'])
            safe_distance = obstacle['radius'] + 0.5
            if dist < safe_distance:
                obstacle_penalty += 20 * (safe_distance - dist)
        return distance_to_target + obstacle_penalty

    def calculate_obstacle_avoidance(self, position):
        avoidance_force = np.zeros(2)
        for obstacle in self.obstacles:
            diff = position - obstacle['center']
            dist = np.linalg.norm(diff)
            safe_distance = obstacle['radius'] + 1.0
            if dist < safe_distance + 2.5:
                if dist < 0.1:
                    dist = 0.1
                strength = np.exp(-(dist - obstacle['radius'])**2 / 1.2)
                direction = diff / dist
                avoidance_force += direction * (strength * 6.0 / (dist ** 1.2))
        return avoidance_force

    def adjust_drones_to_targets(self, n_targets):
        """Ajusta el número de drones para que coincida con el número de objetivos"""
        n_drones = len(self.drones)
        
        if n_drones != n_targets:
            if n_drones < n_targets:
                # Agregar nuevos drones si faltan - colocarlos en el borde
                extra = n_targets - n_drones
                new_positions = self.initialize_drones_on_border(extra)
                new_velocities = np.random.uniform(-0.5, 0.5, (extra, 2))
                
                self.drones = np.vstack((self.drones, new_positions))
                self.velocities = np.vstack((self.velocities, new_velocities))
                self.arrived = np.concatenate((self.arrived, np.zeros(extra, dtype=bool)))
                self.targets_visible = np.concatenate((self.targets_visible, np.ones(extra, dtype=bool)))
                
                # Actualizar personal best para los nuevos drones
                new_personal_best = new_positions.copy()
                new_personal_best_fitness = np.array([self.fitness(p, (i + n_drones) % n_targets) 
                                                    for i, p in enumerate(new_positions)])
                
                self.personal_best = np.vstack((self.personal_best, new_personal_best))
                self.personal_best_fitness = np.concatenate((self.personal_best_fitness, new_personal_best_fitness))
                
            else:
                # Eliminar drones sobrantes si hay más de los necesarios
                self.drones = self.drones[:n_targets]
                self.velocities = self.velocities[:n_targets]
                self.arrived = self.arrived[:n_targets]
                self.targets_visible = self.targets_visible[:n_targets]
                self.personal_best = self.personal_best[:n_targets]
                self.personal_best_fitness = self.personal_best_fitness[:n_targets]
            
            self.n_drones = n_targets

    def navigate(self):
        for iteration in range(self.max_iter):
            all_arrived = True
            
            # Ajustar número de drones al cambiar de formación
            n_targets = len(self.target_formation)
            self.adjust_drones_to_targets(n_targets)

            for i in range(self.n_drones):
                if self.arrived[i]:
                    continue
                    
                r1, r2 = np.random.rand(2)
                inertia = 0.7 * self.velocities[i]
                memory = 1.5 * r1 * (self.personal_best[i] - self.drones[i])
                social = 1.5 * r2 * (self.target_formation[i] - self.drones[i])
                avoidance = self.calculate_obstacle_avoidance(self.drones[i])
                
                self.velocities[i] = inertia + memory + social + avoidance * 6.0
                speed = np.linalg.norm(self.velocities[i])
                if speed > 1.0:
                    self.velocities[i] /= speed
                    
                self.drones[i] += self.velocities[i]
                self.drones[i] = np.clip(self.drones[i], self.bounds[0], self.bounds[1])
                
                current_fitness = self.fitness(self.drones[i], i)
                if current_fitness < self.personal_best_fitness[i]:
                    self.personal_best[i] = self.drones[i]
                    self.personal_best_fitness[i] = current_fitness
                    
                if np.linalg.norm(self.drones[i] - self.target_formation[i]) < 0.15:
                    self.arrived[i] = True
                    self.targets_visible[i] = False
                    
                if not self.arrived[i]:
                    all_arrived = False

            self.history.append(self.drones.copy())
            self.history_targets_visible.append(self.targets_visible.copy())
            self.history_formation_index.append(self.current_formation_index)
            
            self.best_fitness_history.append(np.mean(self.personal_best_fitness))

            # Incrementar contador de iteraciones por formación
            self.formation_iterations += 1
            
            # Cambiar de figura cuando todos lleguen O cuando se alcance el máximo de iteraciones por formación
            formation_names = ['Cabeza de Robot', 'Estrella', 'Cabeza de Dragón']
            
            if all_arrived or self.formation_iterations >= self.max_formation_iterations:
                print(f"Formación '{formation_names[self.current_formation_index]}' completada después de {self.formation_iterations} iteraciones")
                print(f"  - Drones que llegaron: {np.sum(self.arrived)}/{len(self.arrived)}")
                
                # Guardar el frame actual como imagen PNG
                self.save_formation_image(formation_names[self.current_formation_index])
                
                self.current_formation_index += 1
                if self.current_formation_index >= len(self.formations):
                    print("¡Todas las formaciones completadas!")
                    break
                    
                # Reiniciar para la nueva formación
                self.target_formation = self.formations[self.current_formation_index]
                self.arrived = np.zeros(len(self.target_formation), dtype=bool)
                self.targets_visible = np.ones(len(self.target_formation), dtype=bool)
                self.formation_iterations = 0
                
                # Ajustar inmediatamente los drones a la nueva formación
                self.adjust_drones_to_targets(len(self.target_formation))
                
                # Reiniciar velocidades para la nueva formación
                self.velocities = np.random.uniform(-0.5, 0.5, (self.n_drones, 2))
                
                # Reiniciar posiciones de los drones al borde
                self.drones = self.initialize_drones_on_border(self.n_drones)
                self.personal_best = self.drones.copy()
                self.personal_best_fitness = np.array([self.fitness(p, i) for i, p in enumerate(self.drones)])
                
                print(f"Cambiando a formación: '{formation_names[self.current_formation_index]}' con {len(self.target_formation)} drones")
                
        return self.history

    def save_formation_image(self, formation_name):
        """Guarda una imagen PNG de la formación completada"""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Configurar límites del gráfico
        ax.set_xlim(self.bounds[0], self.bounds[1])
        ax.set_ylim(self.bounds[0], self.bounds[1])
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        # Dibujar obstáculos
        for obstacle in self.obstacles:
            circle = plt.Circle(obstacle['center'], obstacle['radius'], 
                               color='red', alpha=0.3)
            ax.add_patch(circle)
        
        # Obtener la última posición de los drones
        drones_pos = self.history[-1]
        
        # Dibujar drones
        ax.scatter(drones_pos[:, 0], drones_pos[:, 1], c='green', s=80, marker='^', label='Drones')
        
        # Dibujar objetivos (todos ocultos ya que la formación está completada)
        ax.scatter(self.target_formation[:, 0], self.target_formation[:, 1], 
                 c='orange', marker='X', s=100, alpha=0.7, label='Posiciones objetivo')
        
        # Etiquetas y leyenda
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(f'Formación Completada: {formation_name}')
        ax.legend()
        
        # Guardar imagen
        filename = f"{formation_name.lower().replace(' ', '_')}_formation.png"
        plt.tight_layout()
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"Imagen guardada: {filename}")

    def visualize_navigation(self, save_gif=False):
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Configurar límites del gráfico
        ax.set_xlim(self.bounds[0], self.bounds[1])
        ax.set_ylim(self.bounds[0], self.bounds[1])
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        # Dibujar obstáculos
        for i, obstacle in enumerate(self.obstacles):
            label = 'Obstáculo' if i == 0 else ""  # Solo mostrar etiqueta una vez
            circle = plt.Circle(obstacle['center'], obstacle['radius'], 
                               color='red', alpha=0.3, label=label)
            ax.add_patch(circle)
        
        # Inicializar scatter para drones y objetivos con colores diferentes
        drone_scatter = ax.scatter([], [], c='blue', s=60, label='Drones', marker='^')
        target_scatter = ax.scatter([], [], c='orange', marker='X', s=80, alpha=0.8, label='Posiciones objetivo')
        
        # Mostrar información de formación actual
        formation_info = ax.text(0.02, 0.98, '', transform=ax.transAxes, fontsize=12,
                               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # Etiquetas y leyenda
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title('Navegación de Drones con PSO - Formaciones Dinámicas')
        ax.legend()
        
        def animate(frame):
            if frame < len(self.history):
                drones_pos = self.history[frame]
                drone_scatter.set_offsets(drones_pos)
                
                # Obtener la formación activa en este frame
                formation_idx = self.history_formation_index[frame]
                target_formation = self.formations[formation_idx]
                
                # Obtener qué objetivos deben mostrarse en este frame
                if frame < len(self.history_targets_visible):
                    current_targets_visible = self.history_targets_visible[frame]
                    
                    # Asegurar que los arrays tengan el mismo tamaño
                    min_len = min(len(current_targets_visible), len(target_formation))
                    if min_len > 0:
                        current_targets_visible = current_targets_visible[:min_len]
                        target_formation_visible = target_formation[:min_len]
                        
                        visible_targets = target_formation_visible[current_targets_visible]
                        target_scatter.set_offsets(visible_targets)
                
                # Actualizar información de la formación
                formation_names = ['Cabeza de Robot', 'Estrella', 'Cabeza de Dragón']
                current_name = formation_names[formation_idx]
                
                # Calcular cuántos drones han llegado en esta formación
                if frame < len(self.history_targets_visible):
                    arrived_count = np.sum(~self.history_targets_visible[frame][:len(target_formation)])
                else:
                    arrived_count = 0
                    
                total_drones = len(target_formation)
                
                formation_info.set_text(f'Formación: {current_name}\n'
                                      f'Drones: {arrived_count}/{total_drones} llegaron\n'
                                      f'Frame: {frame}/{len(self.history)-1}')
                
                # Cambiar color de drones que han llegado
                if len(drones_pos) > 0:
                    # Para este frame, determinar qué drones han llegado
                    if frame < len(self.history_targets_visible):
                        # Un dron ha llegado si su objetivo no es visible
                        current_arrived = ~self.history_targets_visible[frame][:len(drones_pos)]
                    else:
                        current_arrived = np.zeros(len(drones_pos), dtype=bool)
                    
                    colors = ['green' if arrived else 'blue' for arrived in current_arrived]
                    drone_scatter.set_color(colors)
                
            return drone_scatter, target_scatter, formation_info
        
        anim = FuncAnimation(fig, animate, frames=len(self.history), 
                           interval=50, blit=False, repeat=True)
        
        # Guardar GIF si se solicita
        if save_gif:
            print("Guardando animación como GIF...")
            writer = PillowWriter(fps=15, bitrate=1800)
            anim.save('drone_formation_animation.gif', writer=writer)
            print("GIF guardado: drone_formation_animation.gif")
        
        plt.tight_layout()
        plt.show()
        
        return anim


# ======== Ejecutar simulación ========
if __name__ == "__main__":
    drone_formation = DroneFormationPSO(max_iter=500)  # Aumentamos iteraciones
    history = drone_formation.navigate()
    
    # Mostrar estadísticas finales
    print(f"\nSimulación completada:")
    print(f"- Total de iteraciones: {len(history)}")
    print(f"- Drones en formación final: {len(drone_formation.drones)}")
    print(f"- Formaciones completadas: {min(drone_formation.current_formation_index + 1, len(drone_formation.formations))}")
    
    # Mostrar número de drones en cada formación
    for i, formation in enumerate(drone_formation.formations):
        print(f"- Formación {i}: {len(formation)} drones")
    
    # Visualizar y guardar GIF
    drone_formation.visualize_navigation(save_gif=True)