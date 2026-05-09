# camera_debug.py
import cv2
import sys
from server.face_controller import FaceController

def main():
    print("\n" + "="*50)
    print("   📷 MODO DEBUG - PRUEBA DE CÁMARA")
    print("="*50)
    print("Este modo te permite probar el reconocimiento facial")
    print("sin ejecutar el juego completo.")
    print("\nCaracterísticas:")
    print("  • Detección de rostro")
    print("  • Seguimiento de nariz")
    print("  • Detección de boca")
    print("  • Detección de parpadeo")
    print("  • Inclinación de cabeza")
    print("\nControles:")
    print("  • ESC : Salir")
    print("="*50 + "\n")
    
    # Inicializar cámara en modo debug
    face_controller = FaceController(show_debug=True)
    
    if not face_controller.initialized:
        print("Error: No se pudo inicializar la cámara")
        return
    
    print("✓ Cámara inicializada correctamente")
    print("✓ Mostrando ventana de debug...")
    print("✓ Mueve tu cara para ver la detección en tiempo real\n")
    
    try:
        while True:
            # Actualizar detección
            face_controller.update()
            
            # Mostrar estadísticas en consola
            if face_controller.is_face_detected():
                nose_y = face_controller.get_nose_position()
                mouth = face_controller.get_mouth_open_ratio()
                tilt = face_controller.get_head_tilt()
                smile = face_controller.get_smile_ratio()
                
                # Limpiar línea y mostrar info
                print(f"\r📍 Nariz: {nose_y:.0f} | 👄 Boca: {mouth:.0%} | 📐 Inclinación: {tilt:.1f}° | 😊 Sonrisa: {smile:.0%}   ", end="")
            
            # Verificar tecla ESC para salir
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
                
    except KeyboardInterrupt:
        print("\n\nDebug interrumpido por el usuario")
    finally:
        face_controller.release()
        cv2.destroyAllWindows()
        print("\n✓ Modo debug finalizado")

if __name__ == "__main__":
    main()