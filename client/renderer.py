# frontend/renderer.py
import pygame

class GameRenderer:
    def __init__(self, width=400, height=600):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Flappy Bird - Control por nariz")
        
        # Colores
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (135, 206, 235)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.WHITE = (255, 255, 255)
        
    def clear(self):
        self.screen.fill(self.BLUE)
        
    def draw_bird(self, x, y, radius):
        # Cuerpo
        pygame.draw.circle(self.screen, self.YELLOW, (int(x), int(y)), radius)
        # Ojo
        pygame.draw.circle(self.screen, self.BLACK, (int(x) + 5, int(y) - 5), 3)
        pygame.draw.circle(self.screen, self.BLACK, (int(x) + 7, int(y) - 5), 2)
        # Pico
        pygame.draw.polygon(self.screen, (255, 140, 0), 
                           [(int(x) + radius, int(y)), 
                            (int(x) + radius + 8, int(y)),
                            (int(x) + radius, int(y) + 5)])
        
    def draw_pipe(self, top_rect, bottom_rect):
        pygame.draw.rect(self.screen, self.GREEN, top_rect)
        pygame.draw.rect(self.screen, self.GREEN, bottom_rect)
        pygame.draw.rect(self.screen, (0, 100, 0), top_rect, 3)
        pygame.draw.rect(self.screen, (0, 100, 0), bottom_rect, 3)
        
    def draw_ground(self):
        for i in range(0, self.width, 40):
            pygame.draw.rect(self.screen, (100, 200, 255), (i, self.height - 50, 20, 50))
            
    def draw_score(self, current_score, high_score, difficulty_info):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {current_score}", True, self.BLACK)
        high_score_text = font.render(f"Best: {high_score}", True, self.BLACK)
        level_text = font.render(f"Speed: {abs(difficulty_info['velocity']):.1f}  Gap: {difficulty_info['gap']}", True, self.BLACK)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 50))
        self.screen.blit(level_text, (10, 90))
        
    def draw_instructions(self):
        font = pygame.font.Font(None, 20)
        inst1 = font.render("Control: Mueve tu NARIZ arriba/abajo", True, self.BLACK)
        inst2 = font.render("R-Reiniciar | ESC-Salir | +/- Sensibilidad", True, self.BLACK)
        self.screen.blit(inst1, (self.width//2 - inst1.get_width()//2, self.height - 55))
        self.screen.blit(inst2, (self.width//2 - inst2.get_width()//2, self.height - 35))
        
    def draw_nose_indicator(self, nose_y):
        indicator_x = self.width - 30
        bar_y = 50
        bar_height = self.height - 100
        pygame.draw.rect(self.screen, (200, 200, 200), (indicator_x - 5, bar_y, 10, bar_height))
        
        indicator_y = max(bar_y, min(bar_y + bar_height, nose_y))
        pygame.draw.circle(self.screen, self.RED, (indicator_x, int(indicator_y)), 8)
        
        font = pygame.font.Font(None, 20)
        text = font.render("Nariz", True, self.BLACK)
        self.screen.blit(text, (indicator_x - 20, bar_y - 20))
        
    def draw_sensitivity_indicator(self, sensitivity):
        bar_x = self.width - 30
        bar_y = self.height - 80
        bar_width = 10
        bar_height = 50
        
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x - 5, bar_y, bar_width, bar_height))
        fill_height = int(bar_height * sensitivity)
        pygame.draw.rect(self.screen, (0, 255, 0), (bar_x - 5, bar_y + bar_height - fill_height, bar_width, fill_height))
        
        font = pygame.font.Font(None, 16)
        text = font.render(f"Sens: {sensitivity:.1f}", True, self.BLACK)
        self.screen.blit(text, (bar_x - 25, bar_y - 20))
        
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
        self.screen.blit(warning, (self.width//2 - warning.get_width()//2, self.height - 120))
        
    def draw_difficulty_info(self, text):
        font = pygame.font.Font(None, 20)
        speed_text = font.render(text, True, (255, 140, 0))
        self.screen.blit(speed_text, (self.width//2 - speed_text.get_width()//2, 130))
        
    def update(self):
        pygame.display.flip()
        
    def get_clock(self):
        return pygame.time.Clock()