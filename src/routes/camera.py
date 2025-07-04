from flask import Blueprint, request, jsonify
from src.models.product import Camera, db
from src.services.camera_service import CameraService
import json

camera_bp = Blueprint('camera', __name__)
camera_service = CameraService()

@camera_bp.route('/cameras', methods=['GET'])
def get_cameras():
    """Mendapatkan daftar semua kamera yang terkonfigurasi"""
    try:
        cameras = Camera.query.all()
        return jsonify({
            'success': True,
            'cameras': [camera.to_dict() for camera in cameras]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@camera_bp.route('/cameras/available', methods=['GET'])
def get_available_cameras():
    """Mendeteksi kamera yang tersedia di sistem"""
    try:
        available_cameras = camera_service.get_available_cameras()
        return jsonify({
            'success': True,
            'available_cameras': available_cameras
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@camera_bp.route('/cameras', methods=['POST'])
def create_camera():
    """Menambahkan konfigurasi kamera baru"""
    try:
        data = request.get_json()
        
        # Validasi input
        required_fields = ['name', 'index']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Cek apakah nama kamera sudah ada
        existing_camera = Camera.query.filter_by(name=data['name']).first()
        if existing_camera:
            return jsonify({
                'success': False,
                'error': 'Camera name already exists'
            }), 400
        
        # Buat kamera baru
        camera = Camera(
            name=data['name'],
            index=data['index'],
            resolution_width=data.get('resolution_width', 640),
            resolution_height=data.get('resolution_height', 480),
            brightness=data.get('brightness', 50),
            contrast=data.get('contrast', 50),
            zoom=data.get('zoom', 100),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(camera)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'camera': camera.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@camera_bp.route('/cameras/<int:camera_id>', methods=['PUT'])
def update_camera(camera_id):
    """Update konfigurasi kamera"""
    try:
        camera = Camera.query.get_or_404(camera_id)
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            camera.name = data['name']
        if 'index' in data:
            camera.index = data['index']
        if 'resolution_width' in data:
            camera.resolution_width = data['resolution_width']
        if 'resolution_height' in data:
            camera.resolution_height = data['resolution_height']
        if 'brightness' in data:
            camera.brightness = data['brightness']
        if 'contrast' in data:
            camera.contrast = data['contrast']
        if 'zoom' in data:
            camera.zoom = data['zoom']
        if 'is_active' in data:
            camera.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'camera': camera.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@camera_bp.route('/cameras/<int:camera_id>', methods=['DELETE'])
def delete_camera(camera_id):
    """Hapus konfigurasi kamera"""
    try:
        camera = Camera.query.get_or_404(camera_id)
        
        # Release camera if it's currently in use
        camera_service.release_camera(camera_id)
        
        db.session.delete(camera)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Camera deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@camera_bp.route('/cameras/<int:camera_id>/initialize', methods=['POST'])
def initialize_camera(camera_id):
    """Inisialisasi kamera untuk digunakan"""
    try:
        camera = Camera.query.get_or_404(camera_id)
        
        # Initialize camera with current configuration
        camera_service.initialize_camera(camera.to_dict())
        
        return jsonify({
            'success': True,
            'message': 'Camera initialized successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@camera_bp.route('/cameras/<int:camera_id>/capture', methods=['POST'])
def capture_frame(camera_id):
    """Mengambil frame dari kamera"""
    try:
        camera = Camera.query.get_or_404(camera_id)
        
        # Capture frame
        frame = camera_service.capture_frame(camera_id)
        
        # Convert to base64 for frontend
        frame_base64 = camera_service.frame_to_base64(frame)
        
        return jsonify({
            'success': True,
            'image': frame_base64,
            'camera_name': camera.name
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@camera_bp.route('/cameras/<int:camera_id>/preview', methods=['GET'])
def get_camera_preview(camera_id):
    """Mendapatkan preview dari kamera (untuk live feed)"""
    try:
        camera = Camera.query.get_or_404(camera_id)
        
        # Initialize camera if not already initialized
        if camera_id not in camera_service.cameras:
            camera_service.initialize_camera(camera.to_dict())
        
        # Capture frame
        frame = camera_service.capture_frame(camera_id)
        
        # Convert to base64
        frame_base64 = camera_service.frame_to_base64(frame)
        
        return jsonify({
            'success': True,
            'image': frame_base64,
            'timestamp': camera_service.cameras[camera_id].get(cv2.CAP_PROP_POS_MSEC) if camera_id in camera_service.cameras else 0
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@camera_bp.route('/cameras/<int:camera_id>/release', methods=['POST'])
def release_camera(camera_id):
    """Release kamera"""
    try:
        camera_service.release_camera(camera_id)
        
        return jsonify({
            'success': True,
            'message': 'Camera released successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

