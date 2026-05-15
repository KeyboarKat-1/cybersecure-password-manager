#!/usr/bin/env python
"""
Verify all required dependencies are installed
This checks everything needed for CyberSecure Password Manager deployment
"""
import sys

dependencies = [
    # Core Framework
    ('flask', 'Flask'),
    ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
    ('werkzeug', 'Werkzeug'),
    
    # Database
    ('sqlalchemy', 'SQLAlchemy'),
    
    # Production Server
    ('gunicorn', 'Gunicorn'),
    
    # Security & Encryption
    ('cryptography', 'Cryptography'),
    ('pyotp', 'PyOTP'),
    
    # Image Processing
    ('qrcode', 'QRCode'),
    ('PIL', 'Pillow'),
    
    # Web Utilities
    ('requests', 'Requests'),
]

print("Checking deployment dependencies...\n")
missing = []

for module, name in dependencies:
    try:
        __import__(module)
        print(f"✓ {name}")
    except ImportError:
        print(f"✗ {name} - MISSING")
        missing.append(name)

print()
if missing:
    print(f"✗ Missing dependencies: {', '.join(missing)}")
    print("\nRun: pip install -r requirements.txt")
    sys.exit(1)
else:
    print("✓ All deployment dependencies installed successfully!")
    sys.exit(0)
