from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    part_number = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.part_number}>'

    def to_dict(self):
        return {
            'id': self.id,
            'part_number': self.part_number,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Inspection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    captured_image_path = db.Column(db.String(255))
    detected_part_number = db.Column(db.String(100))
    is_ok = db.Column(db.Boolean, default=False)
    inspection_mode = db.Column(db.String(20), nullable=False)  # 'auto' or 'manual'
    confidence_score = db.Column(db.Float)  # OCR confidence score
    detection_area = db.Column(db.Text)  # JSON string for detection area coordinates
    inspected_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref=db.backref('inspections', lazy=True))

    def __repr__(self):
        return f'<Inspection {self.id} - {self.detected_part_number}>'

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'captured_image_path': self.captured_image_path,
            'detected_part_number': self.detected_part_number,
            'is_ok': self.is_ok,
            'inspection_mode': self.inspection_mode,
            'confidence_score': self.confidence_score,
            'detection_area': self.detection_area,
            'inspected_at': self.inspected_at.isoformat() if self.inspected_at else None,
            'product': self.product.to_dict() if self.product else None
        }

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    index = db.Column(db.Integer, nullable=False)  # OpenCV camera index
    resolution_width = db.Column(db.Integer, default=640)
    resolution_height = db.Column(db.Integer, default=480)
    brightness = db.Column(db.Integer, default=50)
    contrast = db.Column(db.Integer, default=50)
    zoom = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Camera {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'index': self.index,
            'resolution_width': self.resolution_width,
            'resolution_height': self.resolution_height,
            'brightness': self.brightness,
            'contrast': self.contrast,
            'zoom': self.zoom,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ItemCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    rule_json = db.Column(db.Text)  # JSON string containing check rules
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ItemCheck {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'rule_json': self.rule_json,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

