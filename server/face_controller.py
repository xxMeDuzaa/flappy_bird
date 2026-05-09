# server/face_controller.py
import cv2

class FaceController:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        self.face_cascade = None
        self.initialized = False
        
        if not self.cap.isOpened():
            print("Error: No se pudo abrir la cámara")
            return
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            print("Error: No se pudo cargar el clasificador de rostros")
            return
            
        self.initialized = True
        self.frame = None
        self.nose_y = None
        self.face_detected = False
        self.face_rect = None
        
    def update(self):
        """Actualizar frame y detectar rostro"""
        if not self.initialized:
            return False
            
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return False
            
        self.frame = cv2.flip(frame, 1)
        
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))
        
        self.face_detected = False
        if len(faces) > 0:
            x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])
            self.face_rect = (x, y, w, h)
            
            nose_x = x + w // 2
            nose_y_pixel = y + int(h * 0.7)
            self.nose_y = nose_y_pixel * 600 / self.frame.shape[0]
            self.face_detected = True
            return True
            
        return True
        
    def get_nose_position(self):
        """Obtener posición Y de la nariz (0-600)"""
        return self.nose_y if self.face_detected else None
        
    def is_face_detected(self):
        return self.face_detected
        
    def get_face_rect(self):
        return self.face_rect
        
    def get_frame(self):
        """Obtener frame actual para visualización"""
        return self.frame
        
    def release(self):
        if self.cap is not None:
            self.cap.release()