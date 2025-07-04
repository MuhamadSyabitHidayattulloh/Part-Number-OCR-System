from flask import Blueprint, request, jsonify
from src.models.product import Product, db

product_bp = Blueprint('product', __name__)

@product_bp.route('/products', methods=['GET'])
def get_products():
    """Mendapatkan daftar semua produk"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = Product.query
        
        if search:
            query = query.filter(Product.part_number.contains(search))
        
        products = query.order_by(Product.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'products': [product.to_dict() for product in products.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': products.total,
                'pages': products.pages,
                'has_next': products.has_next,
                'has_prev': products.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@product_bp.route('/products', methods=['POST'])
def create_product():
    """Menambahkan produk baru"""
    try:
        data = request.get_json()
        
        # Validasi input
        if 'part_number' not in data:
            return jsonify({
                'success': False,
                'error': 'Part number is required'
            }), 400
        
        # Cek apakah part number sudah ada
        existing_product = Product.query.filter_by(part_number=data['part_number']).first()
        if existing_product:
            return jsonify({
                'success': False,
                'error': 'Part number already exists'
            }), 400
        
        # Buat produk baru
        product = Product(
            part_number=data['part_number'],
            description=data.get('description', '')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'product': product.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Mendapatkan detail produk"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            'success': True,
            'product': product.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@product_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update produk"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Update fields
        if 'part_number' in data:
            # Cek apakah part number baru sudah ada
            existing_product = Product.query.filter_by(part_number=data['part_number']).first()
            if existing_product and existing_product.id != product_id:
                return jsonify({
                    'success': False,
                    'error': 'Part number already exists'
                }), 400
            product.part_number = data['part_number']
        
        if 'description' in data:
            product.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'product': product.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Hapus produk"""
    try:
        product = Product.query.get_or_404(product_id)
        
        db.session.delete(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@product_bp.route('/products/search', methods=['GET'])
def search_products():
    """Pencarian produk berdasarkan part number"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({
                'success': True,
                'products': []
            })
        
        products = Product.query.filter(
            Product.part_number.contains(query)
        ).limit(limit).all()
        
        return jsonify({
            'success': True,
            'products': [product.to_dict() for product in products]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@product_bp.route('/products/validate', methods=['POST'])
def validate_part_number():
    """Validasi part number"""
    try:
        data = request.get_json()
        part_number = data.get('part_number')
        
        if not part_number:
            return jsonify({
                'success': False,
                'error': 'Part number is required'
            }), 400
        
        # Cek apakah part number ada di database
        product = Product.query.filter_by(part_number=part_number).first()
        
        return jsonify({
            'success': True,
            'exists': product is not None,
            'product': product.to_dict() if product else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

