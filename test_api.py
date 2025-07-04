#!/usr/bin/env python3
"""
Script untuk testing API endpoints sistem Part Number OCR
"""

import requests
import json
import base64
import cv2
import numpy as np
from datetime import datetime

# Base URL untuk API
BASE_URL = "http://localhost:5000/api"

def create_test_image():
    """Membuat gambar test sederhana dengan teks"""
    # Buat gambar putih
    img = np.ones((200, 400, 3), dtype=np.uint8) * 255
    
    # Tambahkan teks
    cv2.putText(img, "ABC-123", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    
    # Encode ke base64
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return f"data:image/jpeg;base64,{img_base64}"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test generic endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        if response.status_code == expected_status:
            print(f"✅ {method} {endpoint} - Status: {response.status_code}")
            return True
        else:
            print(f"❌ {method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Connection Error (Server not running?)")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {str(e)}")
        return False

def test_cameras():
    """Test camera endpoints"""
    print("\n🔍 Testing Camera Endpoints...")
    
    # Test get cameras
    test_endpoint('GET', '/cameras')
    
    # Test add camera
    camera_data = {
        "name": "Test Camera",
        "device_index": 0,
        "resolution_width": 640,
        "resolution_height": 480
    }
    test_endpoint('POST', '/cameras', camera_data)
    
    # Test camera detection
    test_endpoint('GET', '/cameras/detect')

def test_products():
    """Test product endpoints"""
    print("\n📦 Testing Product Endpoints...")
    
    # Test get products
    test_endpoint('GET', '/products')
    
    # Test add product
    product_data = {
        "part_number": "TEST-123",
        "description": "Test Product"
    }
    test_endpoint('POST', '/products', product_data)

def test_item_checks():
    """Test item check endpoints"""
    print("\n✅ Testing Item Check Endpoints...")
    
    # Test get item checks
    test_endpoint('GET', '/item-checks')
    
    # Test add item check
    item_check_data = {
        "name": "Test Validation",
        "description": "Test validation rule",
        "rule_json": json.dumps({
            "type": "part_number_validation",
            "min_length": 3,
            "max_length": 20
        }),
        "is_active": True
    }
    test_endpoint('POST', '/item-checks', item_check_data)

def test_inspections():
    """Test inspection endpoints"""
    print("\n🔍 Testing Inspection Endpoints...")
    
    # Test get inspections
    test_endpoint('GET', '/inspections')
    
    # Test get inspection stats
    test_endpoint('GET', '/inspections/stats')
    
    # Test manual inspection with image
    test_image = create_test_image()
    manual_inspection_data = {
        "image_base64": test_image,
        "detected_part_number": "TEST-123"
    }
    test_endpoint('POST', '/inspect/manual', manual_inspection_data)
    
    # Test item check testing endpoint
    test_endpoint('POST', '/inspect/test-item-checks', {"part_number": "TEST-123"})

def test_health():
    """Test health endpoint"""
    print("\n❤️ Testing Health Endpoint...")
    test_endpoint('GET', '/health')

def main():
    """Main testing function"""
    print("🚀 Starting API Testing...")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test all endpoints
    test_health()
    test_cameras()
    test_products()
    test_item_checks()
    test_inspections()
    
    print("\n✨ API Testing Completed!")

if __name__ == "__main__":
    main()

