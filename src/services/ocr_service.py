import pytesseract
import cv2
import numpy as np
import re
from PIL import Image
import json

class OCRService:
    def __init__(self):
        # Configure Tesseract
        self.tesseract_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
        
    def extract_text_from_image(self, image, region=None):
        """Ekstrak teks dari gambar menggunakan Tesseract OCR"""
        try:
            # Crop image if region is specified
            if region:
                x, y, w, h = region['x'], region['y'], region['width'], region['height']
                image = image[y:y+h, x:x+w]
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_for_ocr(image)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(processed_image)
            
            # Extract text with confidence scores
            data = pytesseract.image_to_data(pil_image, config=self.tesseract_config, output_type=pytesseract.Output.DICT)
            
            # Filter and combine text with confidence > threshold
            confidence_threshold = 30
            extracted_texts = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > confidence_threshold:
                    text = data['text'][i].strip()
                    if text:
                        extracted_texts.append({
                            'text': text,
                            'confidence': int(data['conf'][i]),
                            'bbox': {
                                'x': data['left'][i],
                                'y': data['top'][i],
                                'width': data['width'][i],
                                'height': data['height'][i]
                            }
                        })
            
            # Combine texts and find the most likely part number
            combined_text = ' '.join([item['text'] for item in extracted_texts])
            part_number = self._extract_part_number(combined_text)
            
            # Calculate average confidence
            avg_confidence = np.mean([item['confidence'] for item in extracted_texts]) if extracted_texts else 0
            
            return {
                'part_number': part_number,
                'raw_text': combined_text,
                'confidence': float(avg_confidence),
                'details': extracted_texts
            }
            
        except Exception as e:
            return {
                'part_number': '',
                'raw_text': '',
                'confidence': 0.0,
                'error': str(e),
                'details': []
            }

    def _preprocess_for_ocr(self, image):
        """Pra-pemrosesan khusus untuk OCR"""
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Resize image if too small (OCR works better on larger images)
        height, width = gray.shape
        if height < 50 or width < 100:
            scale_factor = max(2, 100 // min(height, width))
            gray = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
        
        # Apply Gaussian blur to reduce noise
        gray = cv2.GaussianBlur(gray, (1, 1), 0)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Apply threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up
        kernel = np.ones((1,1), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        return binary

    def _extract_part_number(self, text):
        """Ekstrak part number dari teks menggunakan pattern matching"""
        if not text:
            return ''
        
        # Clean the text
        text = text.strip().upper()
        
        # Common part number patterns
        patterns = [
            r'[A-Z0-9]{2,}-[A-Z0-9]{2,}',  # Pattern like ABC-123, XYZ-456
            r'[A-Z]{2,}[0-9]{2,}',         # Pattern like ABC123, XYZ456
            r'[0-9]{2,}[A-Z]{2,}',         # Pattern like 123ABC, 456XYZ
            r'[A-Z0-9]{4,}',               # Any alphanumeric string with 4+ chars
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Return the longest match (most likely to be a part number)
                return max(matches, key=len)
        
        # If no pattern matches, return the cleaned text if it looks like a part number
        if len(text) >= 3 and re.match(r'^[A-Z0-9\-_]+$', text):
            return text
        
        return ''

    def validate_part_number(self, part_number, valid_patterns=None):
        """Validasi part number berdasarkan pattern yang diizinkan"""
        if not part_number:
            return False, "Part number is empty"
        
        # Default validation rules
        if len(part_number) < 3:
            return False, "Part number too short"
        
        if len(part_number) > 50:
            return False, "Part number too long"
        
        # Check if contains only allowed characters
        if not re.match(r'^[A-Z0-9\-_]+$', part_number):
            return False, "Part number contains invalid characters"
        
        # Custom pattern validation if provided
        if valid_patterns:
            for pattern in valid_patterns:
                if re.match(pattern, part_number):
                    return True, "Valid part number"
            return False, "Part number doesn't match any valid pattern"
        
        return True, "Valid part number"

    def detect_and_extract_multiple_regions(self, image, max_regions=5):
        """Deteksi dan ekstrak teks dari multiple regions dalam gambar"""
        from src.services.camera_service import CameraService
        
        camera_service = CameraService()
        text_regions = camera_service.detect_text_regions(image)
        
        results = []
        for i, region in enumerate(text_regions[:max_regions]):
            ocr_result = self.extract_text_from_image(image, region)
            if ocr_result['part_number']:
                results.append({
                    'region': region,
                    'ocr_result': ocr_result,
                    'region_index': i
                })
        
        # Sort by confidence
        results.sort(key=lambda x: x['ocr_result']['confidence'], reverse=True)
        return results

    def extract_text_from_coordinates(self, image, x, y, width, height):
        """Ekstrak teks dari koordinat yang ditentukan secara manual"""
        region = {
            'x': int(x),
            'y': int(y), 
            'width': int(width),
            'height': int(height)
        }
        return self.extract_text_from_image(image, region)

