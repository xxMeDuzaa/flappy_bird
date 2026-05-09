# server/game_logic.py
import random

# Constantes del juego
WIDTH, HEIGHT = 400, 600
PIPE_WIDTH = 70

# Configuración de dificultad
DIFFICULTY_CONFIG = {
    0: {'gap': 200, 'velocity': -5, 'spawn_distance': 280},   # Más rápido desde el inicio
    5: {'gap': 190, 'velocity': -5.5, 'spawn_distance': 270},
    10: {'gap': 180, 'velocity': -6, 'spawn_distance': 260},
    15: {'gap': 170, 'velocity': -6.5, 'spawn_distance': 250},
    20: {'gap': 160, 'velocity': -7, 'spawn_distance': 240},
}

def get_difficulty_config(score):
    """Obtener configuración de dificultad según el puntaje"""
    level = 0
    for threshold in sorted(DIFFICULTY_CONFIG.keys()):
        if score >= threshold:
            level = threshold
    return DIFFICULTY_CONFIG[level]

class Bird:
    def __init__(self, sensitivity=1.0):
        self.x = 100
        self.y = HEIGHT // 2
        self.radius = 15
        self.sensitivity = sensitivity
        
    def reset(self):
        self.y = HEIGHT // 2
        
    def update_with_nose(self, nose_y):
        if nose_y is not None:
            self.y = self.y * (1 - self.sensitivity) + max(self.radius, min(HEIGHT - self.radius, nose_y)) * self.sensitivity
        
    def get_rect(self):
        return (self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
    
    def get_position(self):
        return (self.x, self.y)
    
    def get_radius(self):
        return self.radius

class Pipe:
    def __init__(self, x, gap_size, velocity):
        self.x = x
        self.gap_size = gap_size
        self.velocity = velocity
        self.height = random.randint(100, HEIGHT - gap_size - 100)
        self.top_rect = (x, 0, PIPE_WIDTH, self.height)
        self.bottom_rect = (x, self.height + gap_size, PIPE_WIDTH, HEIGHT - self.height - gap_size)
        
    def update(self):
        self.x += self.velocity
        self.top_rect = (self.x, 0, PIPE_WIDTH, self.height)
        self.bottom_rect = (self.x, self.height + self.gap_size, PIPE_WIDTH, HEIGHT - self.height - self.gap_size)
        
    def off_screen(self):
        return self.x + PIPE_WIDTH < 0
    
    def collide(self, bird_rect):
        bx, by, bw, bh = bird_rect
        bird_rect_pg = (bx, by, bw, bh)
        
        # Colisión con tubo superior
        tx, ty, tw, th = self.top_rect
        if (bx < tx + tw and bx + bw > tx and
            by < ty + th and by + bh > ty):
            return True
            
        # Colisión con tubo inferior
        bx, by, bw, bh = self.bottom_rect
        if (bird_rect_pg[0] < bx + bw and bird_rect_pg[0] + bird_rect_pg[2] > bx and
            bird_rect_pg[1] < by + bh and bird_rect_pg[1] + bird_rect_pg[3] > by):
            return True
            
        return False
    
    def get_rects(self):
        return self.top_rect, self.bottom_rect