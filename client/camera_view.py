# client/camera_view.py
import cv2

class CameraView:
    def __init__(self, window_name="Flappy Bird - Control Facial"):
        self.window_name = window_name
        
    def show(self, frame, score, velocity, gap, sensitivity, face_detected, face_rect=None):
        if frame is None:
            return
            
        display_frame = frame.copy()
        
        if face_detected and face_rect:
            x, y, w, h = face_rect
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            
            nose_x = x + w // 2
            nose_y = y + int(h * 0.7)
            cv2.circle(display_frame, (nose_x, nose_y), 8, (0, 0, 255), -1)
            cv2.putText(display_frame, "NARIZ", (nose_x - 30, nose_y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Mostrar información
        cv2.putText(display_frame, f"Score: {score}  Speed: {abs(velocity):.1f}  Gap: {gap}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(display_frame, f"Sensibilidad: {sensitivity:.2f} (+/- para ajustar)", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
        if not face_detected:
            cv2.putText(display_frame, "No se detecta rostro - Acercate a la camara", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        cv2.imshow(self.window_name, display_frame)
        cv2.waitKey(1)
        
    def close(self):
        cv2.destroyAllWindows()