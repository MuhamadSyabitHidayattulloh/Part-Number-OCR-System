import cv2
import numpy as np
import base64
import io
from PIL import Image
import threading
import time

class CameraService:
    def __init__(self):
        self.cameras = {}
        self.active_streams = {}
        self.lock = threading.Lock()

    def get_available_cameras(self):
        """Mendeteksi kamera yang tersedia di sistem"""
        available_cameras = []
        for i in range(10):  # Check first 10 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    available_cameras.append({
                        'index': i,
                        'name': f'Camera {i}',
                        'resolution': (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                                     int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                    })
                cap.release()
        return available_cameras

    def initialize_camera(self, camera_config):
        """Inisialisasi kamera dengan konfigurasi tertentu"""
        camera_id = camera_config['id']
        camera_index = camera_config['index']
        
        with self.lock:
            if camera_id in self.cameras:
                self.cameras[camera_id].release()
            
            cap = cv2.VideoCapture(camera_index)
            if not cap.isOpened():
                raise Exception(f"Cannot open camera with index {camera_index}")
            
            # Set camera properties
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_config.get('resolution_width', 640))
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_config.get('resolution_height', 480))
            cap.set(cv2.CAP_PROP_BRIGHTNESS, camera_config.get('brightness', 50) / 100.0)
            cap.set(cv2.CAP_PROP_CONTRAST, camera_config.get('contrast', 50) / 100.0)
            
            self.cameras[camera_id] = cap
            return True

    def capture_frame(self, camera_id):
        """Mengambil satu frame dari kamera"""
        with self.lock:
            if camera_id not in self.cameras:
                raise Exception(f"Camera {camera_id} not initialized")
            
            cap = self.cameras[camera_id]
            ret, frame = cap.read()
            if not ret:
                raise Exception(f"Failed to capture frame from camera {camera_id}")
            
            return frame

    def frame_to_base64(self, frame):
        """Konversi frame OpenCV ke base64 string untuk frontend"""
        _, buffer = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{img_base64}"

    def preprocess_image(self, image, enhance_contrast=True, denoise=True):
        """Pra-pemrosesan gambar untuk meningkatkan akurasi OCR"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Enhance contrast using CLAHE
        if enhance_contrast:
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            gray = clahe.apply(gray)
        
        # Denoise
        if denoise:
            gray = cv2.medianBlur(gray, 3)
        
        # Threshold to binary
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary

    def detect_text_regions(self, image):
        """Deteksi area yang kemungkinan mengandung teks menggunakan OpenCV"""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply morphological operations to detect text regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        grad = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
        
        # Binarize
        _, bw = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Connect horizontally oriented regions
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
        connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter based on size (adjust these values based on your needs)
            if w > 20 and h > 10 and w < 500 and h < 100:
                text_regions.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h),
                    'area': w * h
                })
        
        # Sort by area (largest first)
        text_regions.sort(key=lambda x: x['area'], reverse=True)
        return text_regions

    def crop_region(self, image, region):
        """Crop gambar berdasarkan region yang ditentukan"""
        x, y, w, h = region['x'], region['y'], region['width'], region['height']
        return image[y:y+h, x:x+w]

    def release_camera(self, camera_id):
        """Release kamera"""
        with self.lock:
            if camera_id in self.cameras:
                self.cameras[camera_id].release()
                del self.cameras[camera_id]

    def release_all_cameras(self):
        """Release semua kamera"""
        with self.lock:
            for camera_id in list(self.cameras.keys()):
                self.cameras[camera_id].release()
            self.cameras.clear()

    def __del__(self):
        """Destructor untuk memastikan semua kamera di-release"""
        self.release_all_cameras()

