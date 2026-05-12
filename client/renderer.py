# client/renderer.py
import pygame
import math

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
        
    def clear(self):
        self.screen.fill(self.BLUE)
        
    def draw_start_screen(self):
        """Pantalla de inicio con violeta oscuro"""
        # Fondo violeta oscuro
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
        self.draw_bird(center_x, center_y, 25)
        
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
        
        # Mensaje "Presiona cualquier tecla" con efecto de parpadeo
        font_press = pygame.font.Font(None, 36)
        
        time = pygame.time.get_ticks() / 500
        alpha = int(100 + (math.sin(time) * 100))
        
        press_text = font_press.render("PRESIONA CUALQUIER TECLA", True, self.YELLOW)
        
        text_surface = pygame.Surface((press_text.get_width(), press_text.get_height()), pygame.SRCALPHA)
        text_surface.blit(press_text, (0, 0))
        text_surface.set_alpha(alpha)
        self.screen.blit(text_surface, (self.width//2 - press_text.get_width()//2, self.height - 100))
        
        # Texto más pequeño con instrucciones
        font_small = pygame.font.Font(None, 24)
        inst_text = font_small.render("Mueve tu nariz arriba/abajo para controlar el pájaro", True, self.WHITE)
        self.screen.blit(inst_text, (self.width//2 - inst_text.get_width()//2, self.height - 60))
        
    def draw_bird(self, x, y, radius):
        """Dibuja el pájaro con tamaño variable"""
        # Cuerpo
        pygame.draw.circle(self.screen, self.YELLOW, (int(x), int(y)), radius)
        # Ojo
        eye_size = max(3, radius // 5)
        pygame.draw.circle(self.screen, self.BLACK, (int(x) + radius//2, int(y) - radius//3), eye_size)
        pygame.draw.circle(self.screen, self.WHITE, (int(x) + radius//2 + 2, int(y) - radius//3 - 2), eye_size//2)
        # Pico
        pico_size = radius // 2
        pygame.draw.polygon(self.screen, (255, 140, 0), 
                           [(int(x) + radius, int(y)), 
                            (int(x) + radius + pico_size, int(y)),
                            (int(x) + radius, int(y) + pico_size//2)])
        
    def draw_pipe(self, top_rect, bottom_rect):
        """Dibuja tubos con bordes redondeados y extremos más anchos"""
        x, y, w, h = top_rect
        bx, by, bw, bh = bottom_rect
        
        # Colores más opacos (verde mate)
        MAIN_GREEN = (60, 120, 60)      # Verde mate
        BORDER_GREEN = (40, 90, 40)     # Borde más oscuro
        RIM_GREEN = (50, 100, 50)       # Color del extremo
        
        # === TUBO SUPERIOR ===
        # Cuerpo del tubo
        pygame.draw.rect(self.screen, MAIN_GREEN, top_rect)
        
        # Borde redondeado en la parte inferior (extremo más ancho)
        rim_width = w + 20
        rim_height = 30
        rim_x = x - 10
        rim_y = y + h - rim_height
        
        # Extremo redondeado
        rim_rect = pygame.Rect(rim_x, rim_y, rim_width, rim_height)
        pygame.draw.rect(self.screen, RIM_GREEN, rim_rect, border_radius=10)
        pygame.draw.rect(self.screen, BORDER_GREEN, rim_rect, 2, border_radius=10)
        
        # Líneas decorativas en el extremo
        for i in range(3):
            line_y = rim_y + 8 + i * 7
            pygame.draw.line(self.screen, BORDER_GREEN, (rim_x + 5, line_y), (rim_x + rim_width - 5, line_y), 2)
        
        # === TUBO INFERIOR ===
        # Cuerpo del tubo
        pygame.draw.rect(self.screen, MAIN_GREEN, bottom_rect)
        
        # Borde redondeado en la parte superior (extremo más ancho)
        bottom_rim_width = bw + 20
        bottom_rim_height = 30
        bottom_rim_x = bx - 10
        bottom_rim_y = by
        
        # Extremo redondeado
        bottom_rim_rect = pygame.Rect(bottom_rim_x, bottom_rim_y, bottom_rim_width, bottom_rim_height)
        pygame.draw.rect(self.screen, RIM_GREEN, bottom_rim_rect, border_radius=10)
        pygame.draw.rect(self.screen, BORDER_GREEN, bottom_rim_rect, 2, border_radius=10)
        
        # Líneas decorativas en el extremo
        for i in range(3):
            line_y = bottom_rim_y + 8 + i * 7
            pygame.draw.line(self.screen, BORDER_GREEN, (bottom_rim_x + 5, line_y), (bottom_rim_x + bottom_rim_width - 5, line_y), 2)
        
    def draw_ground(self):
        # Suelo
        suelo_rect = pygame.Rect(0, self.height - 80, self.width, 80)
        pygame.draw.rect(self.screen, self.BROWN, suelo_rect)
        
        # Líneas de pasto
        for i in range(0, self.width, 40):
            pygame.draw.line(self.screen, (0, 100, 0), (i, self.height - 80), (i + 15, self.height - 70), 3)
            pygame.draw.line(self.screen, (0, 100, 0), (i + 15, self.height - 80), (i + 30, self.height - 75), 3)
            
    def draw_score(self, current_score, high_score):
        font = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 32)
        
        # Marco para el score
        score_rect = pygame.Rect(20, 20, 180, 80)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), score_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.WHITE, score_rect, 2, border_radius=10)
        
        # Textos
        score_text = font.render(f"Score: {current_score}", True, self.WHITE)
        high_score_text = font_small.render(f"Best: {high_score}", True, self.YELLOW)
        
        self.screen.blit(score_text, (30, 30))
        self.screen.blit(high_score_text, (30, 70))
        
        
    def draw_game_over(self, score, high_score):
        # Overlay semitransparente
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Fuentes
        font_big = pygame.font.Font(None, 72)
        font_med = pygame.font.Font(None, 36)
        
        # Textos
        game_over_text = font_big.render("GAME OVER", True, self.RED)
        score_text = font_med.render(f"Puntaje: {score}", True, self.WHITE)
        high_text = font_med.render(f"Record: {high_score}", True, self.YELLOW)
        restart_text = font_med.render("Presiona R para reiniciar", True, self.WHITE)
        
        # Posiciones
        self.screen.blit(game_over_text, (self.width//2 - game_over_text.get_width()//2, self.height//2 - 100))
        self.screen.blit(score_text, (self.width//2 - score_text.get_width()//2, self.height//2 - 20))
        self.screen.blit(high_text, (self.width//2 - high_text.get_width()//2, self.height//2 + 20))
        self.screen.blit(restart_text, (self.width//2 - restart_text.get_width()//2, self.height//2 + 80))
        
    def draw_warning(self, text):
        font = pygame.font.Font(None, 24)
        warning = font.render(text, True, self.RED)
        
        # Fondo del warning
        bg_rect = pygame.Rect(self.width//2 - warning.get_width()//2 - 10, self.height - 130, 
                              warning.get_width() + 20, 40)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect, border_radius=5)
        self.screen.blit(warning, (self.width//2 - warning.get_width()//2, self.height - 120))
        
    def update(self):
        pygame.display.flip()
        
    def get_clock(self):
        return pygame.time.Clock()