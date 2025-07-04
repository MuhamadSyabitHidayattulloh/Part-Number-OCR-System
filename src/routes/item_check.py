from flask import Blueprint, request, jsonify
from src.models.product import ItemCheck, db
import json

item_check_bp = Blueprint('item_check', __name__)

@item_check_bp.route('/item-checks', methods=['GET'])
def get_item_checks():
    """Mendapatkan daftar semua item check"""
    try:
        item_checks = ItemCheck.query.order_by(ItemCheck.created_at.desc()).all()
        return jsonify({
            'success': True,
            'item_checks': [item_check.to_dict() for item_check in item_checks]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@item_check_bp.route('/item-checks', methods=['POST'])
def create_item_check():
    """Menambahkan item check baru"""
    try:
        data = request.get_json()
        
        # Validasi input
        required_fields = ['name', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validasi rule_json jika ada
        rule_json = data.get('rule_json', '{}')
        try:
            json.loads(rule_json)  # Validasi JSON
        except json.JSONDecodeError:
            return jsonify({
                'success': False,
                'error': 'Invalid JSON format in rule_json'
            }), 400
        
        # Buat item check baru
        item_check = ItemCheck(
            name=data['name'],
            description=data['description'],
            rule_json=rule_json,
            is_active=data.get('is_active', True)
        )
        
        db.session.add(item_check)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item_check': item_check.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@item_check_bp.route('/item-checks/<int:item_check_id>', methods=['GET'])
def get_item_check(item_check_id):
    """Mendapatkan detail item check"""
    try:
        item_check = ItemCheck.query.get_or_404(item_check_id)
        return jsonify({
            'success': True,
            'item_check': item_check.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@item_check_bp.route('/item-checks/<int:item_check_id>', methods=['PUT'])
def update_item_check(item_check_id):
    """Update item check"""
    try:
        item_check = ItemCheck.query.get_or_404(item_check_id)
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            item_check.name = data['name']
        if 'description' in data:
            item_check.description = data['description']
        if 'rule_json' in data:
            # Validasi JSON
            try:
                json.loads(data['rule_json'])
                item_check.rule_json = data['rule_json']
            except json.JSONDecodeError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON format in rule_json'
                }), 400
        if 'is_active' in data:
            item_check.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item_check': item_check.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@item_check_bp.route('/item-checks/<int:item_check_id>', methods=['DELETE'])
def delete_item_check(item_check_id):
    """Hapus item check"""
    try:
        item_check = ItemCheck.query.get_or_404(item_check_id)
        
        db.session.delete(item_check)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item check deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@item_check_bp.route('/item-checks/<int:item_check_id>/toggle', methods=['POST'])
def toggle_item_check(item_check_id):
    """Toggle status aktif/non-aktif item check"""
    try:
        item_check = ItemCheck.query.get_or_404(item_check_id)
        item_check.is_active = not item_check.is_active
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item_check': item_check.to_dict(),
            'message': f'Item check {"activated" if item_check.is_active else "deactivated"}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@item_check_bp.route('/item-checks/active', methods=['GET'])
def get_active_item_checks():
    """Mendapatkan daftar item check yang aktif"""
    try:
        item_checks = ItemCheck.query.filter_by(is_active=True).order_by(ItemCheck.name).all()
        return jsonify({
            'success': True,
            'item_checks': [item_check.to_dict() for item_check in item_checks]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

