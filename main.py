# main.py
import pygame
import sys
from server import Bird, Pipe, get_difficulty_config, FaceController, ScoreManager
from client import GameRenderer

def main():
    # Inicializar componentes
    pygame.init()
    
    # Backend (server) - SIN modo debug
    print("Inicializando cámara (modo oculto)...")
    face_controller = FaceController(show_debug=False)
    if not face_controller.initialized:
        print("Error: No se pudo inicializar la cámara")
        return
        
    score_manager = ScoreManager()
    
    # Frontend (client)
    renderer = GameRenderer(width=1024, height=600)
    
    # Variables del juego - sensibilidad fija
    sensitivity = 0.85  # Valor fijo, no modificable
    bird = Bird(sensitivity)
    pipes = []
    game_over = False
    clock = renderer.get_clock()
    
    print("\n" + "="*60)
    print("   🐦 FLAPPY BIRD - CONTROL FACIAL")
    print("="*60)
    print(f"📺 RESOLUCIÓN: 1024x600")
    print("🎮 CONTROL: Mueve tu NARIZ arriba/abajo")
    print("📷 CÁMARA: Modo oculto (sin ventana)")
    print("\n🎛️ CONTROLES:")
    print("   • R   : Reiniciar juego")
    print("   • ESC : Salir")
    print("\n💡 Para probar la cámara ejecuta: python camera_debug.py")
    print("="*60 + "\n")
    
    while True:
        # Obtener dificultad actual
        difficulty = get_difficulty_config(score_manager.get_current_score())
        
        # Procesar eventos
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
                    
                if event.key == pygame.K_r and game_over:
                    bird = Bird(sensitivity)
                    pipes = []
                    score_manager.reset_score()
                    game_over = False
                    print("✓ Juego reiniciado!")
        
        if not game_over:
            # Actualizar detección facial
            face_controller.update()
            
            # Control principal: posición de la nariz
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
                        print(f"🎉 ¡NUEVO RÉCORD! {score_manager.get_high_score()} puntos 🎉")
            
            # Verificar colisiones
            bird_rect = bird.get_rect()
            
            if bird.y - bird.radius <= 0 or bird.y + bird.radius >= renderer.height:
                game_over = True
                print(f"💀 Game Over! Puntaje final: {score_manager.get_current_score()}")
                
            for pipe in pipes:
                if pipe.collide(bird_rect):
                    game_over = True
                    print(f"💀 Game Over! Puntaje final: {score_manager.get_current_score()}")
        
        # Renderizar juego
        renderer.clear()
        renderer.draw_ground()
        renderer.draw_bird(bird.x, bird.y, bird.radius)
        
        for pipe in pipes:
            top_rect, bottom_rect = pipe.get_rects()
            renderer.draw_pipe(top_rect, bottom_rect)
        
        # Dibujar solo score y récord
        renderer.draw_score(
            score_manager.get_current_score(),
            score_manager.get_high_score()
        )
        
        renderer.draw_instructions()
        
        # Mostrar advertencia si no detecta rostro
        if not game_over and not face_controller.is_face_detected():
            renderer.draw_warning("⚠️ No se detecta tu rostro - Acercate a la camara")
        
        # Cartel de dificultad ELIMINADO - ya no se muestra cuando aumenta la velocidad
        
        if game_over:
            renderer.draw_game_over(
                score_manager.get_current_score(),
                score_manager.get_high_score()
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