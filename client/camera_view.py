# client/camera_view.py
import cv2

class CameraView:
    def __init__(self, window_name="Flappy Bird - Filtros Instagram"):
        self.window_name = window_name
        
    def show(self, frame, score, velocity, gap, sensitivity, face_detected, 
             mouth_open_ratio=0, is_blinking=False, head_tilt=0, smile_ratio=0):
        
        if frame is None:
            return
            
        display_frame = frame.copy()
        h, w, _ = display_frame.shape
        
        # Barra superior con información del juego
        overlay = display_frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 100), (0, 0, 0), -1)
        display_frame = cv2.addWeighted(overlay, 0.5, display_frame, 0.5, 0)
        
        # Información del juego
        cv2.putText(display_frame, f"FLAPPY BIRD - CONTROL FACIAL", (w//2 - 150, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(display_frame, f"Score: {score}  |  Speed: {abs(velocity):.1f}  |  Gap: {gap}", (w//2 - 180, 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(display_frame, f"Sensibilidad: {sensitivity:.2f} (+/- para ajustar)", (w//2 - 150, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        # Panel de expresiones (derecha)
        if face_detected:
            # Barra de apertura de boca
            bar_x = w - 120
            bar_y = 120
            bar_width = 100
            bar_height = 15
            
            cv2.rectangle(display_frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), -1)
            cv2.rectangle(display_frame, (bar_x, bar_y), (bar_x + int(bar_width * mouth_open_ratio), bar_y + bar_height), (0, 255, 255), -1)
            cv2.putText(display_frame, f"BOCA {int(mouth_open_ratio*100)}%", (bar_x, bar_y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            # Barra de sonrisa
            bar_y = 150
            cv2.rectangle(display_frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), -1)
            cv2.rectangle(display_frame, (bar_x, bar_y), (bar_x + int(bar_width * smile_ratio), bar_y + bar_height), (0, 255, 0), -1)
            cv2.putText(display_frame, f"SONRISA {int(smile_ratio*100)}%", (bar_x, bar_y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            # Indicador de inclinación
            bar_y = 180
            tilt_offset = int((head_tilt / 45) * 40)
            cv2.rectangle(display_frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (100, 100, 100), -1)
            cv2.circle(display_frame, (bar_x + bar_width//2 + tilt_offset, bar_y + bar_height//2), 8, (255, 165, 0), -1)
            cv2.putText(display_frame, f"INCLINACION {int(head_tilt)}°", (bar_x, bar_y - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            # Indicador de parpadeo
            if is_blinking:
                cv2.putText(display_frame, "😉 PARPADEO DETECTADO 😉", (w//2 - 100, h - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        else:
            cv2.putText(display_frame, "⚠️ NO SE DETECTA ROSTRO ⚠️", (w//2 - 150, h - 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            cv2.putText(display_frame, "ACERCATE A LA CAMARA", (w//2 - 120, h - 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        # Texto de filtro Instagram
        cv2.putText(display_frame, "✨ INSTAGRAM FILTERS ✨", (10, h - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)
        
        cv2.imshow(self.window_name, display_frame)
        cv2.waitKey(1)
        
    def close(self):
        cv2.destroyAllWindows()