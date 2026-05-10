# main.py
import pygame
import sys
import math
from server import Bird, Pipe, get_difficulty_config, FaceController, ScoreManager
from client import GameRenderer

def main():
    pygame.init()
    
    print("Inicializando cámara...")
    face_controller = FaceController(show_debug=False)
    if not face_controller.initialized:
        print("Error: No se pudo inicializar la cámara")
        return
        
    score_manager = ScoreManager()
    renderer = GameRenderer(width=1024, height=600)
    
    sensitivity = 1.0  # Ajusta este valor para cambiar la sensibilidad del control facial
    bird = Bird(sensitivity)
    pipes = []
    game_over = False
    waiting_for_start = True  # Solo True al iniciar el programa
    clock = renderer.get_clock()
    
    print("\n" + "="*50)
    print("   FLAPPY BIRD - CONTROL FACIAL")
    print("="*50)
    print("Mueve tu NARIZ arriba/abajo")
    print("R: Reiniciar")
    print("ESC: Salir")
    print("="*50 + "\n")
    
    while True:
        difficulty = get_difficulty_config(score_manager.get_current_score())
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                face_controller.release()
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    face_controller.release()
                    pygame.quit()
                    sys.exit()
                
                # Solo en pantalla de inicio, cualquier tecla empieza el juego
                if waiting_for_start:
                    waiting_for_start = False
                    print("✓ Juego iniciado!")
                    # Inicializar juego
                    bird = Bird(sensitivity)
                    pipes = []
                    score_manager.reset_score()
                    game_over = False
                
                # Reiniciar cuando está en game over (sin pasar por pantalla de inicio)
                if event.key == pygame.K_r and game_over:
                    # Reiniciar directamente, sin pantalla de inicio
                    bird = Bird(sensitivity)
                    pipes = []
                    score_manager.reset_score()
                    game_over = False
                    # waiting_for_start se mantiene en False
                    print("✓ Juego reiniciado!")
        
        # Si estamos en pantalla de inicio (solo al abrir el programa)
        if waiting_for_start:
            renderer.draw_start_screen()
            renderer.update()
            clock.tick(60)
            continue  # Saltar el resto del bucle
        
        # Si no, ejecutar el juego normal
        if not game_over:
            face_controller.update()
            
            nose_y = face_controller.get_nose_position()
            if nose_y is not None:
                bird.update_with_nose(nose_y)
            
            if len(pipes) == 0 or pipes[-1].x < renderer.width - difficulty['spawn_distance']:
                pipes.append(Pipe(renderer.width, difficulty['gap'], difficulty['velocity']))
                
            for pipe in pipes[:]:
                pipe.update()
                
                if not pipe.was_passed() and pipe.is_passed_by_bird(bird.x):
                    pipe.mark_as_passed()
                    score_manager.add_score()
                
                if pipe.off_screen():
                    pipes.remove(pipe)
            
            bird_rect = bird.get_rect()
            
            if bird.y - bird.radius <= 0 or bird.y + bird.radius >= renderer.height:
                game_over = True
                print(f"Game Over! Puntaje: {score_manager.get_current_score()}")
                
            for pipe in pipes:
                if pipe.collide(bird_rect):
                    game_over = True
                    print(f"Game Over! Puntaje: {score_manager.get_current_score()}")
        
        # Renderizar juego
        renderer.clear()
        renderer.draw_ground()
        renderer.draw_bird(bird.x, bird.y, bird.radius)
        
        for pipe in pipes:
            top_rect, bottom_rect = pipe.get_rects()
            renderer.draw_pipe(top_rect, bottom_rect)
        
        renderer.draw_score(score_manager.get_current_score(), score_manager.get_high_score())
        renderer.draw_instructions()
        
        if not game_over and not face_controller.is_face_detected():
            renderer.draw_warning("No se detecta tu rostro - Acercate a la camara")
        
        if game_over:
            renderer.draw_game_over(score_manager.get_current_score(), score_manager.get_high_score())
        
        renderer.update()
        clock.tick(60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()