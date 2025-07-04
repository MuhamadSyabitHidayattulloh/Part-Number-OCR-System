from flask import Blueprint, jsonify
from src.models.product import db
import cv2
import pytesseract
from datetime import datetime

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint untuk monitoring sistem"""
    try:
        # Check database connection
        db_status = "ok"
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db.session.commit()
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Check OpenCV
        opencv_version = cv2.__version__
        
        # Check Tesseract
        try:
            tesseract_version = pytesseract.get_tesseract_version()
        except Exception as e:
            tesseract_version = f"error: {str(e)}"
        
        # Check camera availability (basic check)
        camera_available = False
        try:
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                camera_available = True
                cap.release()
        except Exception:
            pass
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'database': db_status,
                'opencv': opencv_version,
                'tesseract': str(tesseract_version),
                'camera': 'available' if camera_available else 'not available'
            },
            'version': '1.0.0'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

