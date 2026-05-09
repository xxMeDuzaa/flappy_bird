# client/renderer.py
import pygame

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
        self.DARK_BLUE = (100, 150, 250)
        self.BROWN = (139, 69, 19)
        
    def clear(self):
        # Cielo degradado
        for i in range(self.height):
            color_ratio = i / self.height
            r = int(135 * (1 - color_ratio) + 50 * color_ratio)
            g = int(206 * (1 - color_ratio) + 100 * color_ratio)
            b = int(235 * (1 - color_ratio) + 150 * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, i), (self.width, i))
        
    def draw_bird(self, x, y, radius):
        # Cuerpo principal
        pygame.draw.circle(self.screen, self.YELLOW, (int(x), int(y)), radius)
        
        # Ala (para dar sensación de movimiento)
        wing_offset = pygame.time.get_ticks() % 400
        if wing_offset < 200:
            wing_y = y - radius//2
        else:
            wing_y = y + radius//2
        pygame.draw.ellipse(self.screen, (255, 200, 0), (x - radius, wing_y - radius//2, radius, radius))
        
        # Ojo
        pygame.draw.circle(self.screen, self.BLACK, (int(x) + radius//2, int(y) - radius//3), radius//3)
        pygame.draw.circle(self.screen, self.WHITE, (int(x) + radius//2 + 2, int(y) - radius//3 - 2), radius//6)
        
        # Pico
        pygame.draw.polygon(self.screen, (255, 140, 0), 
                           [(int(x) + radius, int(y)), 
                            (int(x) + radius + 12, int(y)),
                            (int(x) + radius, int(y) + 5)])
        
    def draw_pipe(self, top_rect, bottom_rect):
        # Tubo superior
        pygame.draw.rect(self.screen, self.GREEN, top_rect)
        pygame.draw.rect(self.screen, (0, 100, 0), top_rect, 4)
        # Borde del tubo superior
        pygame.draw.rect(self.screen, (0, 150, 0), (top_rect[0] - 10, top_rect[1] + top_rect[3] - 30, PIPE_WIDTH + 20, 30))
        
        # Tubo inferior
        pygame.draw.rect(self.screen, self.GREEN, bottom_rect)
        pygame.draw.rect(self.screen, (0, 100, 0), bottom_rect, 4)
        # Borde del tubo inferior
        pygame.draw.rect(self.screen, (0, 150, 0), (bottom_rect[0] - 10, bottom_rect[1], PIPE_WIDTH + 20, 30))
        
    def draw_ground(self):
        # Suelo con textura
        suelo_rect = pygame.Rect(0, self.height - 80, self.width, 80)
        pygame.draw.rect(self.screen, self.BROWN, suelo_rect)
        
        # Líneas de pasto
        for i in range(0, self.width, 30):
            pygame.draw.line(self.screen, (0, 100, 0), (i, self.height - 80), (i + 15, self.height - 70), 3)
            pygame.draw.line(self.screen, (0, 100, 0), (i + 15, self.height - 80), (i + 30, self.height - 75), 3)
        
        # Nubes decorativas
        if pygame.time.get_ticks() % 2000 < 1000:
            self._draw_cloud(100, 80)
            self._draw_cloud(600, 120)
            self._draw_cloud(800, 60)
            
    def _draw_cloud(self, x, y):
        pygame.draw.circle(self.screen, (255, 255, 255, 180), (x, y), 30)
        pygame.draw.circle(self.screen, (255, 255, 255, 180), (x + 30, y - 10), 35)
        pygame.draw.circle(self.screen, (255, 255, 255, 180), (x + 60, y), 30)
        pygame.draw.circle(self.screen, (255, 255, 255, 180), (x + 30, y + 10), 30)
            
    def draw_score(self, current_score, high_score):
        """Dibuja solo el score y el récord (sin velocidad ni gap)"""
        font = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 32)
        
        # Marco más pequeño para el score (solo para score y best)
        score_rect = pygame.Rect(20, 20, 180, 80)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), score_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.WHITE, score_rect, 2, border_radius=10)
        
        score_text = font.render(f"Score: {current_score}", True, self.WHITE)
        high_score_text = font_small.render(f"Best: {high_score}", True, self.YELLOW)
        
        self.screen.blit(score_text, (30, 30))
        self.screen.blit(high_score_text, (30, 70))
        
    def draw_instructions(self):
        font = pygame.font.Font(None, 24)
        
        # Panel de instrucciones en la parte inferior
        panel_rect = pygame.Rect(self.width//2 - 250, self.height - 70, 600, 60)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), panel_rect, border_radius=5)
        
        inst1 = font.render("🎮 Mueve NARIZ arriba/abajo", True, self.WHITE)
        inst2 = font.render("🔄 R: Reiniciar", True, self.WHITE)
        inst3 = font.render("❌ ESC: Salir", True, self.WHITE)
        
        self.screen.blit(inst1, (self.width//2 - 230, self.height - 45))
        self.screen.blit(inst2, (self.width//2 - 1, self.height - 45))
        self.screen.blit(inst3, (self.width//2 + 150, self.height - 45))
        
    def draw_nose_indicator(self, nose_y):
        indicator_x = self.width - 50
        bar_y = 100
        bar_height = self.height - 200
        bar_width = 15
        
        # Barra vertical con efecto neón
        pygame.draw.rect(self.screen, (50, 50, 50), (indicator_x - bar_width//2, bar_y, bar_width, bar_height), border_radius=8)
        pygame.draw.rect(self.screen, (100, 100, 100), (indicator_x - bar_width//2, bar_y, bar_width, bar_height), 2, border_radius=8)
        
        indicator_y = max(bar_y, min(bar_y + bar_height, nose_y))
        
        # Punto indicador con glow
        for radius in range(8, 2, -2):
            alpha = 255 - radius * 20
            pygame.draw.circle(self.screen, (255, 0, 0, alpha), (indicator_x, int(indicator_y)), radius)
        pygame.draw.circle(self.screen, self.RED, (indicator_x, int(indicator_y)), 8)
        
        font = pygame.font.Font(None, 24)
        text = font.render("Posición", True, self.WHITE)
        text2 = font.render("de tu", True, self.WHITE)
        text3 = font.render("nariz", True, self.RED)
        self.screen.blit(text, (indicator_x - 35, bar_y - 30))
        self.screen.blit(text2, (indicator_x - 35, bar_y - 10))
        self.screen.blit(text3, (indicator_x - 30, bar_y + 10))
        
    def draw_game_over(self, score, high_score):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        font_big = pygame.font.Font(None, 96)
        font_med = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        game_over_text = font_big.render("GAME OVER", True, self.RED)
        score_text = font_med.render(f"Puntaje: {score}", True, self.WHITE)
        high_text = font_med.render(f"Record: {high_score}", True, self.YELLOW)
        restart_text = font_small.render("Presiona R para reiniciar", True, self.WHITE)
        
        # Centrar textos
        self.screen.blit(game_over_text, (self.width//2 - game_over_text.get_width()//2, self.height//2 - 120))
        self.screen.blit(score_text, (self.width//2 - score_text.get_width()//2, self.height//2 - 30))
        self.screen.blit(high_text, (self.width//2 - high_text.get_width()//2, self.height//2 + 30))
        self.screen.blit(restart_text, (self.width//2 - restart_text.get_width()//2, self.height//2 + 100))
        
    def draw_warning(self, text):
        font = pygame.font.Font(None, 28)
        warning = font.render(text, True, self.RED)
        
        # Fondo semitransparente
        bg_rect = pygame.Rect(self.width//2 - warning.get_width()//2 - 10, self.height - 130, 
                              warning.get_width() + 20, 40)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect, border_radius=5)
        self.screen.blit(warning, (self.width//2 - warning.get_width()//2, self.height - 120))
        
    def draw_difficulty_info(self, text):
        font = pygame.font.Font(None, 24)
        speed_text = font.render(text, True, (255, 140, 0))
        
        # Fondo semitransparente
        bg_rect = pygame.Rect(self.width//2 - speed_text.get_width()//2 - 10, 180, 
                              speed_text.get_width() + 20, 30)
        pygame.draw.rect(self.screen, (0, 0, 0, 150), bg_rect, border_radius=5)
        self.screen.blit(speed_text, (self.width//2 - speed_text.get_width()//2, 185))
        
    def update(self):
        pygame.display.flip()
        
    def get_clock(self):
        return pygame.time.Clock()