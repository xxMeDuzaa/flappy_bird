# server/face_controller.py
import cv2
import numpy as np

class FaceController:
    def __init__(self, camera_index=0, show_debug=False):
        # Inicializar cámara
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        self.initialized = False
        self.show_debug = show_debug  # Modo debug sin juego
        
        if not self.cap.isOpened():
            print("Error: No se pudo abrir la cámara")
            return
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Cargar clasificadores de OpenCV
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
        self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
        
        if self.face_cascade.empty():
            print("Error: No se pudo cargar el clasificador de rostros")
            return
            
        self.initialized = True
        self.frame = None
        self.face_rect = None
        self.face_detected = False
        
        # Características faciales
        self.nose_y = None
        self.nose_x = None
        self.mouth_open_ratio = 0
        self.left_eye_blink = False
        self.right_eye_blink = False
        self.head_tilt = 0
        self.smile_ratio = 0
        
        # Para suavizado
        self.smooth_factor = 0.3
        self.prev_nose_y = None
        self.prev_face_center = None
        
    def update(self):
        """Actualizar frame y detectar rostro"""
        if not self.initialized:
            return False
            
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return False
            
        self.frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        
        # Detectar rostros
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
        
        self.face_detected = False
        if len(faces) > 0:
            x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])
            self.face_rect = (x, y, w, h)
            self.face_detected = True
            
            # Detectar ojos
            face_roi = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 5, minSize=(20, 20))
            
            # Calcular posición de la nariz
            nose_x_px = x + w // 2
            nose_y_px = y + int(h * 0.65)
            
            # Suavizar movimiento
            nose_y_normalized = nose_y_px * 600 / self.frame.shape[0]
            if self.prev_nose_y is not None:
                self.nose_y = self.prev_nose_y * (1 - self.smooth_factor) + nose_y_normalized * self.smooth_factor
            else:
                self.nose_y = nose_y_normalized
                
            self.nose_x = nose_x_px * 400 / self.frame.shape[1]
            self.prev_nose_y = self.nose_y
            
            # Calcular apertura de boca
            mouth_y = y + int(h * 0.85)
            mouth_height_px = (y + h) - mouth_y
            self.mouth_open_ratio = min(1.0, mouth_height_px / (h * 0.2))
            
            # Detectar parpadeo
            self.left_eye_blink = len(eyes) < 2
            self.right_eye_blink = len(eyes) < 2
            
            # Calcular inclinación de cabeza
            if len(eyes) >= 2:
                eye1_x, eye1_y, eye1_w, eye1_h = eyes[0]
                eye2_x, eye2_y, eye2_w, eye2_h = eyes[1]
                if eye1_x < eye2_x:
                    left_eye_center = (eye1_x + eye1_w//2, eye1_y + eye1_h//2)
                    right_eye_center = (eye2_x + eye2_w//2, eye2_y + eye2_h//2)
                else:
                    left_eye_center = (eye2_x + eye2_w//2, eye2_y + eye2_h//2)
                    right_eye_center = (eye1_x + eye1_w//2, eye1_y + eye1_h//2)
                
                dx = right_eye_center[0] - left_eye_center[0]
                dy = right_eye_center[1] - left_eye_center[1]
                self.head_tilt = np.degrees(np.arctan2(dy, dx))
            
            # Detectar sonrisa
            mouth_width_px = w * 0.6
            self.smile_ratio = min(1.0, mouth_width_px / (w * 0.8))
            
            current_center = (x + w//2, y + h//2)
            if self.prev_face_center is not None:
                head_movement = np.sqrt((current_center[0] - self.prev_face_center[0])**2 + 
                                       (current_center[1] - self.prev_face_center[1])**2)
            self.prev_face_center = current_center
            
            # Si está en modo debug, mostrar la ventana
            if self.show_debug:
                self._show_debug_window()
            
        return True
    
    def _show_debug_window(self):
        """Mostrar ventana de debug con efectos (solo para pruebas)"""
        if self.frame is None or not self.face_detected:
            return
            
        display_frame = self.frame.copy()
        x, y, w, h = self.face_rect
        
        # Dibujar círculo alrededor de la cara
        center_x = x + w//2
        center_y = y + h//2
        radius = int(max(w, h) * 0.6)
        cv2.circle(display_frame, (center_x, center_y), radius, (0, 255, 255), 3)
        
        # Dibujar puntos clave
        nose_pos = (x + w//2, y + int(h * 0.65))
        cv2.circle(display_frame, nose_pos, 8, (0, 0, 255), -1)
        
        left_eye_pos = (x + int(w * 0.35), y + int(h * 0.4))
        right_eye_pos = (x + int(w * 0.65), y + int(h * 0.4))
        cv2.circle(display_frame, left_eye_pos, 6, (255, 0, 0), -1)
        cv2.circle(display_frame, right_eye_pos, 6, (255, 0, 0), -1)
        
        # Mostrar información
        cv2.putText(display_frame, f"DEBUG - Posicion nariz Y: {int(self.nose_y)}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(display_frame, f"Boca: {int(self.mouth_open_ratio*100)}%", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.putText(display_frame, f"Inclinacion: {int(self.head_tilt)}°", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        
        cv2.imshow('Camera Debug - Presiona ESC para salir', display_frame)
        
    def get_nose_position(self):
        """Obtener posición Y de la nariz (0-600)"""
        return self.nose_y if self.face_detected else None
        
    def get_nose_x_position(self):
        """Obtener posición X de la nariz (0-400)"""
        return self.nose_x if self.face_detected else None
        
    def get_mouth_open_ratio(self):
        return self.mouth_open_ratio if self.face_detected else 0
        
    def is_blinking(self):
        return self.left_eye_blink or self.right_eye_blink if self.face_detected else False
        
    def get_head_tilt(self):
        return self.head_tilt if self.face_detected else 0
        
    def get_smile_ratio(self):
        return self.smile_ratio if self.face_detected else 0
        
    def is_face_detected(self):
        return self.face_detected
        
    def get_face_rect(self):
        return self.face_rect
        
    def release(self):
        if self.cap is not None:
            self.cap.release()
        if self.show_debug:
            cv2.destroyAllWindows()