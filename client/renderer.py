# client/renderer.py
import pygame
import math
import os

# Constantes de dibujo
PIPE_WIDTH = 80

class GameRenderer:
    def __init__(self, width=1024, height=600):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Flappy Bird - Control Facial")
        
        # Colores
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (135, 206, 235)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.WHITE = (255, 255, 255)
        self.BROWN = (139, 69, 19)
        self.DARK_VIOLET = (88, 0, 128)
        self.VIOLET = (138, 43, 226)
        
        # Cargar imagen de fondo
        self.background = None
        self.background_image_path = os.path.join("assets", "imagenes", "background.jpg")
        
        if os.path.exists(self.background_image_path):
            try:
                self.background = pygame.image.load(self.background_image_path)
                self.background = pygame.transform.scale(self.background, (width, height))
                print(f"✓ Imagen de fondo cargada: {self.background_image_path}")
            except Exception as e:
                print(f"Error cargando imagen de fondo: {e}")
                print("Usando fondo azul por defecto")
        else:
            print(f"No se encontró la imagen en: {self.background_image_path}")
            print("Usando fondo azul por defecto")
        
        # Cargar imagen del pájaro
        self.bird_image = None
        self.bird_image_path = os.path.join("assets", "imagenes", "bird.PNG")
        self.bird_size = 170  # Tamaño de la imagen del pájaro (ancho y alto)
        
        if os.path.exists(self.bird_image_path):
            try:
                self.bird_image = pygame.image.load(self.bird_image_path)
                self.bird_image = pygame.transform.scale(self.bird_image, (self.bird_size, self.bird_size))
                print(f"✓ Imagen del pájaro cargada: {self.bird_image_path}")
            except Exception as e:
                print(f"Error cargando imagen del pájaro: {e}")
                print("Usando pájaro dibujado por defecto")
        else:
            print(f"No se encontró la imagen del pájaro en: {self.bird_image_path}")
            print("Usando pájaro dibujado por defecto")
        
    def clear(self):
        """Dibuja el fondo (imagen o color sólido)"""
        if self.background is not None:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.BLUE)
        
    # client/renderer.py - En el método draw_bird
    def draw_bird(self, x, y, radius):
        """Dibuja el pájaro (imagen o dibujado)"""
        if self.bird_image is not None:
            # Usar imagen - centrada en la posición
            # El tamaño de la imagen debe coincidir con el radio * 2
            bird_rect = self.bird_image.get_rect(center=(int(x), int(y)))
            self.screen.blit(self.bird_image, bird_rect)
        else:
            # Dibujar pájaro con formas geométricas (fallback)
            pygame.draw.circle(self.screen, self.YELLOW, (int(x), int(y)), radius)
            eye_size = max(3, radius // 5)
            pygame.draw.circle(self.screen, self.BLACK, (int(x) + radius//2, int(y) - radius//3), eye_size)
            pygame.draw.circle(self.screen, self.WHITE, (int(x) + radius//2 + 2, int(y) - radius//3 - 2), eye_size//2)
            pico_size = radius // 2
            pygame.draw.polygon(self.screen, (255, 140, 0), 
                            [(int(x) + radius, int(y)), 
                                (int(x) + radius + pico_size, int(y)),
                                (int(x) + radius, int(y) + pico_size//2)])
        
    def draw_start_screen(self):
        """Pantalla de inicio con imagen de fondo"""
        if self.background is not None:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.DARK_VIOLET)
        
        # Círculo de luz detrás del pájaro
        center_x = self.width // 2
        center_y = self.height // 2 + 50
        
        for i in range(3):
            radius = 100 - i * 20
            alpha = 100 - i * 30
            circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (138, 43, 226, alpha), (radius, radius), radius)
            self.screen.blit(circle_surface, (center_x - radius, center_y - radius))
        
        # Dibujar pájaro en el centro (más grande)
        # Guardar la imagen original y restaurarla temporalmente para la pantalla de inicio
        original_bird_image = self.bird_image
        original_bird_size = self.bird_size
        
        # Para la pantalla de inicio, usamos un pájaro más grande
        if original_bird_image is not None:
            self.bird_image = pygame.transform.scale(original_bird_image, (170, 170))
            self.bird_size = 170
        
        self.draw_bird(center_x, center_y, 25)
        
        # Restaurar la imagen original
        if original_bird_image is not None:
            self.bird_image = original_bird_image
            self.bird_size = original_bird_size
        
        # Título del juego
        font_title = pygame.font.Font(None, 72)
        title_text = font_title.render("FLAPPY BIRD", True, self.YELLOW)
        title_shadow = font_title.render("FLAPPY BIRD", True, (100, 100, 0))
        
        self.screen.blit(title_shadow, (self.width//2 - title_text.get_width()//2 + 3, 80 + 3))
        self.screen.blit(title_text, (self.width//2 - title_text.get_width()//2, 80))
        
        # Subtítulo con control facial
        font_sub = pygame.font.Font(None, 32)
        sub_text = font_sub.render("CONTROL FACIAL", True, self.WHITE)
        self.screen.blit(sub_text, (self.width//2 - sub_text.get_width()//2, 150))
        
        # Mensaje "Presiona cualquier tecla"
        font_press = pygame.font.Font(None, 36)
        
        time = pygame.time.get_ticks() / 500
        alpha_text = int(100 + (math.sin(time) * 100))
        
        press_text = font_press.render("PRESIONA CUALQUIER TECLA", True, self.YELLOW)
        
        text_surface = pygame.Surface((press_text.get_width(), press_text.get_height()), pygame.SRCALPHA)
        text_surface.blit(press_text, (0, 0))
        text_surface.set_alpha(alpha_text)
        self.screen.blit(text_surface, (self.width//2 - press_text.get_width()//2, self.height - 100))
        
        # Texto más pequeño con instrucciones
        font_small = pygame.font.Font(None, 24)
        inst_text = font_small.render("Mueve tu nariz arriba/abajo para controlar el pájaro", True, self.WHITE)
        self.screen.blit(inst_text, (self.width//2 - inst_text.get_width()//2, self.height - 60))
        
    def draw_pipe(self, top_rect, bottom_rect):
        """Dibuja tubos con bordes redondeados y extremos más anchos"""
        x, y, w, h = top_rect
        bx, by, bw, bh = bottom_rect
        
        # Colores más opacos (verde mate)
        MAIN_GREEN = (60, 120, 60)
        BORDER_GREEN = (40, 90, 40)
        RIM_GREEN = (50, 100, 50)
        
        # === TUBO SUPERIOR ===
        pygame.draw.rect(self.screen, MAIN_GREEN, top_rect)
        
        rim_width = w + 20
        rim_height = 30
        rim_x = x - 10
        rim_y = y + h - rim_height
        
        rim_rect = pygame.Rect(rim_x, rim_y, rim_width, rim_height)
        pygame.draw.rect(self.screen, RIM_GREEN, rim_rect, border_radius=10)
        pygame.draw.rect(self.screen, BORDER_GREEN, rim_rect, 2, border_radius=10)
        
        for i in range(3):
            line_y = rim_y + 8 + i * 7
            pygame.draw.line(self.screen, BORDER_GREEN, (rim_x + 5, line_y), (rim_x + rim_width - 5, line_y), 2)
        
        # === TUBO INFERIOR ===
        pygame.draw.rect(self.screen, MAIN_GREEN, bottom_rect)
        
        bottom_rim_width = bw + 20
        bottom_rim_height = 30
        bottom_rim_x = bx - 10
        bottom_rim_y = by
        
        bottom_rim_rect = pygame.Rect(bottom_rim_x, bottom_rim_y, bottom_rim_width, bottom_rim_height)
        pygame.draw.rect(self.screen, RIM_GREEN, bottom_rim_rect, border_radius=10)
        pygame.draw.rect(self.screen, BORDER_GREEN, bottom_rim_rect, 2, border_radius=10)
        
        for i in range(3):
            line_y = bottom_rim_y + 8 + i * 7
            pygame.draw.line(self.screen, BORDER_GREEN, (bottom_rim_x + 5, line_y), (bottom_rim_x + bottom_rim_width - 5, line_y), 2)
        
    def draw_ground(self):
        suelo_rect = pygame.Rect(0, self.height - 80, self.width, 80)
        pygame.draw.rect(self.screen, self.BROWN, suelo_rect)
        
        for i in range(0, self.width, 40):
            pygame.draw.line(self.screen, (0, 100, 0), (i, self.height - 80), (i + 15, self.height - 70), 3)
            pygame.draw.line(self.screen, (0, 100, 0), (i + 15, self.height - 80), (i + 30, self.height - 75), 3)
            
    def draw_score(self, current_score, high_score):
        font = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 32)
        
        score_rect = pygame.Rect(20, 20, 180, 80)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), score_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.WHITE, score_rect, 2, border_radius=10)
        
        score_text = font.render(f"Score: {current_score}", True, self.WHITE)
        high_score_text = font_small.render(f"Best: {high_score}", True, self.YELLOW)
        
        self.screen.blit(score_text, (30, 30))
        self.screen.blit(high_score_text, (30, 70))
        
    def draw_game_over(self, score, high_score):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        font_big = pygame.font.Font(None, 72)
        font_med = pygame.font.Font(None, 36)
        
        game_over_text = font_big.render("GAME OVER", True, self.RED)
        score_text = font_med.render(f"Puntaje: {score}", True, self.WHITE)
        high_text = font_med.render(f"Record: {high_score}", True, self.YELLOW)
        restart_text = font_med.render("Presiona R para reiniciar", True, self.WHITE)
        
        self.screen.blit(game_over_text, (self.width//2 - game_over_text.get_width()//2, self.height//2 - 100))
        self.screen.blit(score_text, (self.width//2 - score_text.get_width()//2, self.height//2 - 20))
        self.screen.blit(high_text, (self.width//2 - high_text.get_width()//2, self.height//2 + 20))
        self.screen.blit(restart_text, (self.width//2 - restart_text.get_width()//2, self.height//2 + 80))
        
    def draw_warning(self, text):
        font = pygame.font.Font(None, 24)
        warning = font.render(text, True, self.RED)
        
        bg_rect = pygame.Rect(self.width//2 - warning.get_width()//2 - 10, self.height - 130, 
                              warning.get_width() + 20, 40)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect, border_radius=5)
        self.screen.blit(warning, (self.width//2 - warning.get_width()//2, self.height - 120))
        
    def update(self):
        pygame.display.flip()
        
    def get_clock(self):
        return pygame.time.Clock()