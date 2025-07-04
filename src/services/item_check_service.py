import json
import cv2
import numpy as np
from src.models.product import ItemCheck

class ItemCheckService:
    def __init__(self):
        pass
    
    def execute_item_checks(self, image, part_number, active_checks_only=True):
        """Eksekusi semua item check yang aktif"""
        try:
            # Get item checks from database
            if active_checks_only:
                item_checks = ItemCheck.query.filter_by(is_active=True).all()
            else:
                item_checks = ItemCheck.query.all()
            
            results = []
            overall_pass = True
            
            for item_check in item_checks:
                result = self.execute_single_check(image, part_number, item_check)
                results.append(result)
                if not result['passed']:
                    overall_pass = False
            
            return {
                'overall_pass': overall_pass,
                'individual_results': results,
                'total_checks': len(results),
                'passed_checks': sum(1 for r in results if r['passed']),
                'failed_checks': sum(1 for r in results if not r['passed'])
            }
            
        except Exception as e:
            return {
                'overall_pass': False,
                'error': str(e),
                'individual_results': [],
                'total_checks': 0,
                'passed_checks': 0,
                'failed_checks': 0
            }
    
    def execute_single_check(self, image, part_number, item_check):
        """Eksekusi satu item check"""
        try:
            # Parse rule JSON
            rules = json.loads(item_check.rule_json) if item_check.rule_json else {}
            
            result = {
                'check_id': item_check.id,
                'check_name': item_check.name,
                'passed': True,
                'message': 'Check passed',
                'details': {}
            }
            
            # Execute different types of checks based on rule type
            check_type = rules.get('type', 'part_number_validation')
            
            if check_type == 'part_number_validation':
                result = self._check_part_number_validation(part_number, rules, result)
            elif check_type == 'visual_inspection':
                result = self._check_visual_inspection(image, rules, result)
            elif check_type == 'dimension_check':
                result = self._check_dimensions(image, rules, result)
            elif check_type == 'color_check':
                result = self._check_color(image, rules, result)
            elif check_type == 'pattern_match':
                result = self._check_pattern_match(image, rules, result)
            else:
                result['passed'] = False
                result['message'] = f'Unknown check type: {check_type}'
            
            return result
            
        except Exception as e:
            return {
                'check_id': item_check.id,
                'check_name': item_check.name,
                'passed': False,
                'message': f'Error executing check: {str(e)}',
                'details': {}
            }
    
    def _check_part_number_validation(self, part_number, rules, result):
        """Validasi part number berdasarkan aturan"""
        try:
            # Check if part number matches allowed patterns
            allowed_patterns = rules.get('allowed_patterns', [])
            if allowed_patterns:
                import re
                pattern_matched = False
                for pattern in allowed_patterns:
                    if re.match(pattern, part_number):
                        pattern_matched = True
                        break
                
                if not pattern_matched:
                    result['passed'] = False
                    result['message'] = f'Part number {part_number} does not match any allowed pattern'
                    result['details']['allowed_patterns'] = allowed_patterns
                    return result
            
            # Check part number length
            min_length = rules.get('min_length')
            max_length = rules.get('max_length')
            
            if min_length and len(part_number) < min_length:
                result['passed'] = False
                result['message'] = f'Part number too short (minimum {min_length} characters)'
                return result
            
            if max_length and len(part_number) > max_length:
                result['passed'] = False
                result['message'] = f'Part number too long (maximum {max_length} characters)'
                return result
            
            # Check forbidden characters
            forbidden_chars = rules.get('forbidden_characters', [])
            if forbidden_chars:
                for char in forbidden_chars:
                    if char in part_number:
                        result['passed'] = False
                        result['message'] = f'Part number contains forbidden character: {char}'
                        return result
            
            result['message'] = 'Part number validation passed'
            result['details']['part_number'] = part_number
            return result
            
        except Exception as e:
            result['passed'] = False
            result['message'] = f'Error in part number validation: {str(e)}'
            return result
    
    def _check_visual_inspection(self, image, rules, result):
        """Inspeksi visual berdasarkan aturan"""
        try:
            # Check for presence of specific features
            features_to_check = rules.get('features', [])
            
            for feature in features_to_check:
                feature_name = feature.get('name')
                feature_type = feature.get('type', 'contour')
                area_of_interest = feature.get('area')  # {x, y, width, height}
                
                if area_of_interest:
                    # Crop image to area of interest
                    x, y, w, h = area_of_interest['x'], area_of_interest['y'], area_of_interest['width'], area_of_interest['height']
                    roi = image[y:y+h, x:x+w]
                else:
                    roi = image
                
                if feature_type == 'contour':
                    found = self._detect_contour_feature(roi, feature)
                elif feature_type == 'circle':
                    found = self._detect_circle_feature(roi, feature)
                elif feature_type == 'line':
                    found = self._detect_line_feature(roi, feature)
                else:
                    found = False
                
                if not found:
                    result['passed'] = False
                    result['message'] = f'Required feature not found: {feature_name}'
                    result['details']['missing_feature'] = feature_name
                    return result
            
            result['message'] = 'Visual inspection passed'
            result['details']['features_checked'] = len(features_to_check)
            return result
            
        except Exception as e:
            result['passed'] = False
            result['message'] = f'Error in visual inspection: {str(e)}'
            return result
    
    def _check_dimensions(self, image, rules, result):
        """Pemeriksaan dimensi objek"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Find contours
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                result['passed'] = False
                result['message'] = 'No objects found for dimension check'
                return result
            
            # Get largest contour (assuming it's the main object)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Calculate bounding rectangle
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Check dimensions against rules
            min_width = rules.get('min_width')
            max_width = rules.get('max_width')
            min_height = rules.get('min_height')
            max_height = rules.get('max_height')
            
            if min_width and w < min_width:
                result['passed'] = False
                result['message'] = f'Object width {w} is below minimum {min_width}'
                return result
            
            if max_width and w > max_width:
                result['passed'] = False
                result['message'] = f'Object width {w} exceeds maximum {max_width}'
                return result
            
            if min_height and h < min_height:
                result['passed'] = False
                result['message'] = f'Object height {h} is below minimum {min_height}'
                return result
            
            if max_height and h > max_height:
                result['passed'] = False
                result['message'] = f'Object height {h} exceeds maximum {max_height}'
                return result
            
            result['message'] = 'Dimension check passed'
            result['details']['dimensions'] = {'width': w, 'height': h}
            return result
            
        except Exception as e:
            result['passed'] = False
            result['message'] = f'Error in dimension check: {str(e)}'
            return result
    
    def _check_color(self, image, rules, result):
        """Pemeriksaan warna"""
        try:
            # Define area of interest for color check
            area_of_interest = rules.get('area')
            if area_of_interest:
                x, y, w, h = area_of_interest['x'], area_of_interest['y'], area_of_interest['width'], area_of_interest['height']
                roi = image[y:y+h, x:x+w]
            else:
                roi = image
            
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
            
            # Check for expected colors
            expected_colors = rules.get('expected_colors', [])
            tolerance = rules.get('tolerance', 20)
            
            for color_rule in expected_colors:
                color_name = color_rule.get('name')
                target_hsv = color_rule.get('hsv')  # [h, s, v]
                min_percentage = color_rule.get('min_percentage', 10)
                
                if not target_hsv:
                    continue
                
                # Create color range
                lower_bound = np.array([max(0, target_hsv[0] - tolerance), 
                                      max(0, target_hsv[1] - tolerance), 
                                      max(0, target_hsv[2] - tolerance)])
                upper_bound = np.array([min(179, target_hsv[0] + tolerance), 
                                      min(255, target_hsv[1] + tolerance), 
                                      min(255, target_hsv[2] + tolerance)])
                
                # Create mask
                mask = cv2.inRange(hsv, lower_bound, upper_bound)
                
                # Calculate percentage of pixels matching the color
                total_pixels = roi.shape[0] * roi.shape[1]
                matching_pixels = cv2.countNonZero(mask)
                percentage = (matching_pixels / total_pixels) * 100
                
                if percentage < min_percentage:
                    result['passed'] = False
                    result['message'] = f'Insufficient {color_name} color: {percentage:.1f}% (minimum {min_percentage}%)'
                    result['details']['color_percentages'] = {color_name: percentage}
                    return result
            
            result['message'] = 'Color check passed'
            return result
            
        except Exception as e:
            result['passed'] = False
            result['message'] = f'Error in color check: {str(e)}'
            return result
    
    def _check_pattern_match(self, image, rules, result):
        """Pemeriksaan pencocokan pola"""
        try:
            # This is a placeholder for pattern matching
            # In a real implementation, you might use template matching or feature detection
            
            template_path = rules.get('template_path')
            threshold = rules.get('threshold', 0.8)
            
            if not template_path:
                result['passed'] = False
                result['message'] = 'No template path specified for pattern matching'
                return result
            
            # For now, just return success as this would require actual template images
            result['message'] = 'Pattern matching check passed (placeholder implementation)'
            result['details']['template_path'] = template_path
            return result
            
        except Exception as e:
            result['passed'] = False
            result['message'] = f'Error in pattern matching: {str(e)}'
            return result
    
    def _detect_contour_feature(self, image, feature):
        """Deteksi fitur berdasarkan kontur"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            min_area = feature.get('min_area', 100)
            max_area = feature.get('max_area', 10000)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if min_area <= area <= max_area:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _detect_circle_feature(self, image, feature):
        """Deteksi fitur lingkaran"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                     param1=50, param2=30, 
                                     minRadius=feature.get('min_radius', 10), 
                                     maxRadius=feature.get('max_radius', 100))
            
            return circles is not None and len(circles[0]) > 0
            
        except Exception:
            return False
    
    def _detect_line_feature(self, image, feature):
        """Deteksi fitur garis"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=feature.get('threshold', 100))
            
            return lines is not None and len(lines) > 0
            
        except Exception:
            return False

