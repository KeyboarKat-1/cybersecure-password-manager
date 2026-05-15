#!/usr/bin/env python
"""
Quick test to verify app can be imported by Gunicorn
This is the same process Gunicorn uses when starting the app
"""
import sys

try:
    from app import app
    print("✓ Flask app imported successfully")
    print(f"✓ App name: {app.name}")
    print(f"✓ App debug: {app.debug}")
    print(f"✓ App database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print("✓ All deployment checks passed!")
    sys.exit(0)
except Exception as e:
    print(f"✗ Error importing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
