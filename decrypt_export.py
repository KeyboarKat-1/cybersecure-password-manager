#!/usr/bin/env python3
"""
Password Manager Export Decryptor
Decrypts encrypted CSV/JSON exports from the Flask password manager.
"""

import base64
import json
import csv
import sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import argparse


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive encryption key from password using PBKDF2"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def decrypt_export(encrypted_file: str, password: str, output_file: str = None):
    """Decrypt an exported password file"""
    try:
        # Read the encrypted file
        with open(encrypted_file, 'rb') as f:
            file_data = f.read()

        # Extract salt from embedded data
        # Format: salt_length (4 bytes) + salt + encrypted_data
        if len(file_data) < 4:
            print("❌ Error: Invalid encrypted file format.")
            return False

        salt_length = int.from_bytes(file_data[:4], byteorder='big')
        if len(file_data) < 4 + salt_length:
            print("❌ Error: Invalid encrypted file format.")
            return False

        salt = file_data[4:4 + salt_length]
        encrypted_data = file_data[4 + salt_length:]

        # Derive key and decrypt
        key = derive_key(password, salt)
        cipher = Fernet(key)

        try:
            decrypted_data = cipher.decrypt(encrypted_data).decode()
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            print("This could be due to:")
            print("1. Incorrect password")
            print("2. Corrupted file")
            return False

        # Determine output format and save
        if output_file:
            output_path = output_file
        else:
            # Generate output filename
            base_name = encrypted_file.replace('.encrypted', '')
            if '.csv' in base_name:
                output_path = base_name.replace('.csv', '_decrypted.csv')
            elif '.json' in base_name:
                output_path = base_name.replace('.json', '_decrypted.json')
            else:
                output_path = base_name + '_decrypted.txt'

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(decrypted_data)

        print(f"✅ Successfully decrypted file to: {output_path}")

        # Try to parse and show summary
        try:
            if '.json' in output_path:
                data = json.loads(decrypted_data)
                if 'passwords' in data:
                    print(f"📊 Export contains {len(data['passwords'])} password entries")
                    print(f"👤 Exported by: {data.get('export_info', {}).get('user', 'Unknown')}")
                else:
                    print("📄 JSON file decrypted successfully")
            elif '.csv' in output_path:
                # Count CSV rows
                lines = decrypted_data.strip().split('\n')
                if len(lines) > 1:
                    print(f"📊 CSV file contains {len(lines) - 1} password entries (plus header)")
                else:
                    print("📄 CSV file decrypted successfully")
        except:
            print("📄 File decrypted successfully (could not parse for summary)")

        return True

    except FileNotFoundError:
        print(f"❌ Error: File '{encrypted_file}' not found.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Decrypt password manager exports')
    parser.add_argument('encrypted_file', help='Path to the encrypted export file')
    parser.add_argument('-p', '--password', help='Decryption password')
    parser.add_argument('-o', '--output', help='Output file path (optional)')

    args = parser.parse_args()

    if not args.password:
        args.password = input("Enter decryption password: ")

    success = decrypt_export(args.encrypted_file, args.password, args.output)

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()