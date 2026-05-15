#!/usr/bin/env python3
"""
2FA Test Script
Test the two-factor authentication functionality
"""

import pyotp
import time
import sys

def test_totp_generation():
    """Test TOTP generation and verification"""
    print("🔐 Testing TOTP Generation and Verification")

    # Generate a secret
    secret = pyotp.random_base32()
    print(f"Generated secret: {secret}")

    # Create TOTP instance
    totp = pyotp.TOTP(secret)

    # Generate current code
    current_code = totp.now()
    print(f"Current TOTP code: {current_code}")

    # Verify the code
    is_valid = totp.verify(current_code)
    print(f"Code verification: {'✅ Valid' if is_valid else '❌ Invalid'}")

    # Test with wrong code
    wrong_code = "000000"
    is_invalid = totp.verify(wrong_code)
    print(f"Wrong code verification: {'❌ Valid (unexpected)' if is_invalid else '✅ Invalid (expected)'}")

    return is_valid and not is_invalid

def test_qr_generation():
    """Test QR code generation"""
    print("\n📱 Testing QR Code Generation")

    try:
        import qrcode
        from io import BytesIO
        import base64

        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(name="Test User", issuer_name="Password Manager")

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64 (simulating what the app does)
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        qr_base64 = base64.b64encode(img_buffer.getvalue()).decode()

        print(f"✅ QR code generated successfully (size: {len(qr_base64)} characters)")
        return True

    except ImportError as e:
        print(f"❌ QR code generation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ QR code generation error: {e}")
        return False

def test_time_sync():
    """Test time synchronization"""
    print("\n⏰ Testing Time Synchronization")

    secret = pyotp.random_base32()
    totp1 = pyotp.TOTP(secret)
    totp2 = pyotp.TOTP(secret)

    # Generate codes at the same time
    code1 = totp1.now()
    code2 = totp2.now()

    if code1 == code2:
        print("✅ Time synchronization working correctly")
        return True
    else:
        print(f"❌ Time sync issue: {code1} != {code2}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting 2FA Functionality Tests\n")

    tests = [
        ("TOTP Generation", test_totp_generation),
        ("QR Code Generation", test_qr_generation),
        ("Time Synchronization", test_time_sync),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All 2FA tests passed! The implementation should work correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())