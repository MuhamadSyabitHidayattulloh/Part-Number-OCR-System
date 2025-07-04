#!/usr/bin/env python3
"""
Script untuk menjalankan server Flask dengan logging yang lebih baik
"""

import os
import sys
import logging
from src.main import app

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    try:
        logger.info("Starting Part Number OCR System...")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Initialize database
        with app.app_context():
            from src.models.product import db
            db.create_all()
            logger.info("Database initialized successfully")
        
        logger.info("Server starting on http://0.0.0.0:5000")
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

