# main.py
import pygame
import sys
from server import Bird, Pipe, get_difficulty_config, FaceController, ScoreManager
from client import GameRenderer, CameraView

def main():
    # Inicializar componentes
    pygame.init()
    
    # Backend (server)
    face_controller = FaceController()
    if not face_controller.initialized:
        print("Error: No se pudo inicializar la cámara")
        return
        
    score_manager = ScoreManager()
    
    # Frontend (client)
    renderer = GameRenderer()
    camera_view = CameraView()
    
    # Variables del juego
    sensitivity = 0.7
    bird = Bird(sensitivity)
    pipes = []
    game_over = False
    clock = renderer.get_clock()
    
    print("\n=== JUEGO INICIADO ===")
    print("✓ Colócate frente a la cámara")
    print("✓ Mueve tu CARA arriba/abajo para controlar el pájaro")
    print("✓ Presiona + / - para ajustar la SENSIBILIDAD del control")
    print("✓ La dificultad aumenta automáticamente con tu puntaje")
    print("=====================\n")
    
    while True:
        # Obtener dificultad actual
        difficulty = get_difficulty_config(score_manager.get_current_score())
        
        # Procesar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                face_controller.release()
                camera_view.close()
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    face_controller.release()
                    camera_view.close()
                    pygame.quit()
                    sys.exit()
                    
                if event.key == pygame.K_r and game_over:
                    # Reiniciar juego
                    bird = Bird(sensitivity)
                    pipes = []
                    score_manager.reset_score()
                    game_over = False
                    print("✓ Juego reiniciado!")
                    
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    sensitivity = min(1.0, sensitivity + 0.05)
                    bird.sensitivity = sensitivity
                    print(f"Sensibilidad aumentada a: {sensitivity:.2f}")
                    
                if event.key == pygame.K_MINUS:
                    sensitivity = max(0.1, sensitivity - 0.05)
                    bird.sensitivity = sensitivity
                    print(f"Sensibilidad reducida a: {sensitivity:.2f}")
        
        if not game_over:
            # Actualizar detección facial
            face_controller.update()
            
            # Obtener posición de la nariz
            nose_y = face_controller.get_nose_position()
            if nose_y is not None:
                bird.update_with_nose(nose_y)
            
            # Generar nuevos tubos
            if len(pipes) == 0 or pipes[-1].x < renderer.width - difficulty['spawn_distance']:
                pipes.append(Pipe(renderer.width, difficulty['gap'], difficulty['velocity']))
                
            # Actualizar tubos
            for pipe in pipes[:]:
                pipe.update()
                if pipe.off_screen():
                    pipes.remove(pipe)
                    is_new_record = score_manager.add_score()
                    if is_new_record:
                        print(f"¡Nuevo récord: {score_manager.get_high_score()}!")
            
            # Verificar colisiones
            bird_rect = bird.get_rect()
            
            if bird.y - bird.radius <= 0 or bird.y + bird.radius >= renderer.height:
                game_over = True
                print(f"¡Game Over! Puntaje final: {score_manager.get_current_score()}")
                
            for pipe in pipes:
                if pipe.collide(bird_rect):
                    game_over = True
                    print(f"¡Game Over! Puntaje final: {score_manager.get_current_score()}")
        
        # Renderizar juego
        renderer.clear()
        renderer.draw_ground()
        renderer.draw_bird(bird.x, bird.y, bird.radius)
        
        for pipe in pipes:
            top_rect, bottom_rect = pipe.get_rects()
            renderer.draw_pipe(top_rect, bottom_rect)
        
        renderer.draw_score(
            score_manager.get_current_score(),
            score_manager.get_high_score(),
            difficulty
        )
        
        renderer.draw_instructions()
        renderer.draw_sensitivity_indicator(sensitivity)
        
        if not game_over and face_controller.is_face_detected():
            nose_y = face_controller.get_nose_position()
            if nose_y:
                renderer.draw_nose_indicator(nose_y)
        
        if not game_over and not face_controller.is_face_detected():
            renderer.draw_warning("No se detecta tu rostro - Acercate a la camara")
        
        if not game_over and score_manager.get_current_score() >= 5:
            renderer.draw_difficulty_info(
                f"Dificultad: Velocidad {abs(difficulty['velocity']):.1f} | Gap {difficulty['gap']}"
            )
        
        if game_over:
            renderer.draw_game_over(
                score_manager.get_current_score(),
                score_manager.get_high_score()
            )
        
        # Mostrar vista de cámara
        if face_controller.get_frame() is not None:
            camera_view.show(
                face_controller.get_frame(),
                score_manager.get_current_score(),
                difficulty['velocity'],
                difficulty['gap'],
                sensitivity,
                face_controller.is_face_detected(),
                face_controller.get_face_rect()
            )
        
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