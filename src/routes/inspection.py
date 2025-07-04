from flask import Blueprint, request, jsonify
from src.models.product import Product, Inspection, Camera, db
from src.services.camera_service import CameraService
from src.services.ocr_service import OCRService
from src.services.item_check_service import ItemCheckService
import cv2
import numpy as np
import base64
import os
import json
from datetime import datetime

inspection_bp = Blueprint('inspection', __name__)
camera_service = CameraService()
ocr_service = OCRService()
item_check_service = ItemCheckService()

@inspection_bp.route('/inspect/manual', methods=['POST'])
def manual_inspection():
    """Inspeksi manual dengan upload gambar atau capture dari kamera"""
    try:
        data = request.get_json()
        
        # Get image data
        if 'image_base64' in data:
            # Decode base64 image
            image_data = data['image_base64']
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
        elif 'camera_id' in data:
            # Capture from camera
            camera_id = data['camera_id']
            image = camera_service.capture_frame(camera_id)
            
        else:
            return jsonify({
                'success': False,
                'error': 'No image data or camera_id provided'
            }), 400
        
        # Get detection area if provided (for manual area selection)
        detection_area = data.get('detection_area')
        region = None
        if detection_area:
            region = {
                'x': int(detection_area['x']),
                'y': int(detection_area['y']),
                'width': int(detection_area['width']),
                'height': int(detection_area['height'])
            }
        
        # Use manual part number if provided, otherwise perform OCR
        if 'detected_part_number' in data and data['detected_part_number']:
            # Manual part number input
            part_number = data['detected_part_number']
            ocr_result = {
                'part_number': part_number,
                'raw_text': part_number,
                'confidence': 100.0,
                'details': []
            }
        else:
            # Perform OCR
            ocr_result = ocr_service.extract_text_from_image(image, region)
            part_number = ocr_result['part_number']
        
        # Validate part number
        is_valid, validation_message = ocr_service.validate_part_number(part_number)
        
        # Check if part number exists in database
        product = None
        if part_number:
            product = Product.query.filter_by(part_number=part_number).first()
        
        # Execute item checks
        item_check_results = item_check_service.execute_item_checks(image, part_number)
        
        # Overall inspection result
        inspection_passed = is_valid and product is not None and item_check_results['overall_pass']
        
        # Save image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"manual_inspection_{timestamp}.jpg"
        image_path = os.path.join('src', 'static', 'images', image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        cv2.imwrite(image_path, image)
        
        # Create inspection record
        inspection = Inspection(
            product_id=product.id if product else None,
            captured_image_path=image_path,
            detected_part_number=part_number,
            is_ok=inspection_passed,
            inspection_mode='manual',
            confidence_score=ocr_result['confidence'],
            detection_area=json.dumps(detection_area) if detection_area else None
        )
        
        db.session.add(inspection)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'inspection': inspection.to_dict(),
            'ocr_result': ocr_result,
            'validation': {
                'is_valid': is_valid,
                'message': validation_message
            },
            'product_exists': product is not None,
            'product': product.to_dict() if product else None,
            'item_check_results': item_check_results
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inspection_bp.route('/inspect/auto', methods=['POST'])
def auto_inspection():
    """Inspeksi otomatis dengan deteksi area teks otomatis"""
    try:
        data = request.get_json()
        camera_id = data.get('camera_id')
        
        if not camera_id:
            return jsonify({
                'success': False,
                'error': 'Camera ID is required'
            }), 400
        
        # Capture image from camera
        image = camera_service.capture_frame(camera_id)
        
        # Detect text regions automatically
        results = ocr_service.detect_and_extract_multiple_regions(image)
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'No text regions detected'
            }), 400
        
        # Use the best result (highest confidence)
        best_result = results[0]
        ocr_result = best_result['ocr_result']
        detection_area = best_result['region']
        part_number = ocr_result['part_number']
        
        # Validate part number
        is_valid, validation_message = ocr_service.validate_part_number(part_number)
        
        # Check if part number exists in database
        product = None
        if part_number:
            product = Product.query.filter_by(part_number=part_number).first()
        
        # Execute item checks
        item_check_results = item_check_service.execute_item_checks(image, part_number)
        
        # Overall inspection result
        inspection_passed = is_valid and product is not None and item_check_results['overall_pass']
        
        # Save image
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_filename = f"auto_inspection_{timestamp}.jpg"
        image_path = os.path.join('src', 'static', 'images', image_filename)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        cv2.imwrite(image_path, image)
        
        # Create inspection record
        inspection = Inspection(
            product_id=product.id if product else None,
            captured_image_path=image_path,
            detected_part_number=part_number,
            is_ok=inspection_passed,
            inspection_mode='auto',
            confidence_score=ocr_result['confidence'],
            detection_area=json.dumps(detection_area)
        )
        
        db.session.add(inspection)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'inspection': inspection.to_dict(),
            'ocr_result': ocr_result,
            'detection_area': detection_area,
            'all_results': results,
            'validation': {
                'is_valid': is_valid,
                'message': validation_message
            },
            'product_exists': product is not None,
            'product': product.to_dict() if product else None,
            'item_check_results': item_check_results
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inspection_bp.route('/inspect/area', methods=['POST'])
def inspect_specific_area():
    """Inspeksi area spesifik yang ditentukan dengan koordinat"""
    try:
        data = request.get_json()
        
        # Get image
        if 'image_base64' in data:
            image_data = data['image_base64']
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
        elif 'camera_id' in data:
            camera_id = data['camera_id']
            image = camera_service.capture_frame(camera_id)
        else:
            return jsonify({
                'success': False,
                'error': 'No image source provided'
            }), 400
        
        # Get coordinates
        x = data.get('x')
        y = data.get('y')
        width = data.get('width')
        height = data.get('height')
        
        if None in [x, y, width, height]:
            return jsonify({
                'success': False,
                'error': 'Missing coordinates (x, y, width, height)'
            }), 400
        
        # Perform OCR on specific area
        ocr_result = ocr_service.extract_text_from_coordinates(image, x, y, width, height)
        
        # Validate part number
        is_valid, validation_message = ocr_service.validate_part_number(ocr_result['part_number'])
        
        # Execute item checks if part number is detected
        item_check_results = None
        if ocr_result['part_number']:
            item_check_results = item_check_service.execute_item_checks(image, ocr_result['part_number'])
        
        return jsonify({
            'success': True,
            'ocr_result': ocr_result,
            'validation': {
                'is_valid': is_valid,
                'message': validation_message
            },
            'coordinates': {
                'x': x,
                'y': y,
                'width': width,
                'height': height
            },
            'item_check_results': item_check_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inspection_bp.route('/inspections', methods=['GET'])
def get_inspections():
    """Mendapatkan daftar inspeksi dengan pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        mode = request.args.get('mode')  # 'auto' or 'manual'
        
        query = Inspection.query
        
        if mode:
            query = query.filter_by(inspection_mode=mode)
        
        inspections = query.order_by(Inspection.inspected_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'inspections': [inspection.to_dict() for inspection in inspections.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': inspections.total,
                'pages': inspections.pages,
                'has_next': inspections.has_next,
                'has_prev': inspections.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inspection_bp.route('/inspections/stats', methods=['GET'])
def get_inspection_stats():
    """Mendapatkan statistik inspeksi"""
    try:
        # Get date range from query params
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        query = Inspection.query
        
        if from_date:
            query = query.filter(Inspection.inspected_at >= from_date)
        if to_date:
            query = query.filter(Inspection.inspected_at <= to_date)
        
        total_inspections = query.count()
        ok_inspections = query.filter_by(is_ok=True).count()
        ng_inspections = query.filter_by(is_ok=False).count()
        auto_inspections = query.filter_by(inspection_mode='auto').count()
        manual_inspections = query.filter_by(inspection_mode='manual').count()
        
        # Get current running part number (most recent inspection)
        latest_inspection = Inspection.query.order_by(Inspection.inspected_at.desc()).first()
        current_part_number = latest_inspection.detected_part_number if latest_inspection else None
        
        return jsonify({
            'success': True,
            'stats': {
                'total_inspections': total_inspections,
                'ok_count': ok_inspections,
                'ng_count': ng_inspections,
                'auto_count': auto_inspections,
                'manual_count': manual_inspections,
                'ok_percentage': (ok_inspections / total_inspections * 100) if total_inspections > 0 else 0,
                'ng_percentage': (ng_inspections / total_inspections * 100) if total_inspections > 0 else 0,
                'current_part_number': current_part_number
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@inspection_bp.route('/inspect/test-item-checks', methods=['POST'])
def test_item_checks():
    """Test endpoint untuk menguji item checks"""
    try:
        data = request.get_json()
        part_number = data.get('part_number', 'TEST-123')
        
        # Create a dummy image for testing
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Execute item checks
        results = item_check_service.execute_item_checks(test_image, part_number)
        
        return jsonify({
            'success': True,
            'part_number': part_number,
            'item_check_results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

