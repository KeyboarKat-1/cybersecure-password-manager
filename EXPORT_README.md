# Password Manager Export Feature

This Flask password manager includes secure export functionality that allows you to download your saved passwords as encrypted CSV or JSON files.

## Exporting Passwords

1. **Log in** to your password manager dashboard
2. **Scroll down** to the "Export Passwords" section below the search/filter controls
3. **Enter an export password** (minimum 8 characters) - this will be used to encrypt your data
4. **Choose your format**:
   - **CSV**: Tabular format, easy to open in Excel or other spreadsheet applications
   - **JSON**: Structured format, better for programmatic access
5. **Click the export button** - your browser will download the encrypted file

## File Security

- **Encryption**: All exports are encrypted using AES-256 encryption with PBKDF2 key derivation
- **Password Protection**: You must provide a strong password to encrypt the export
- **Salt Embedding**: Each file includes a unique salt for additional security
- **No Plain Text**: Passwords are never stored in plain text in the export files

## Decrypting Exported Files

Use the included `decrypt_export.py` script to decrypt your exported files:

### Command Line Usage

```bash
python decrypt_export.py <encrypted_file> -p <password>
```

### Examples

```bash
# Decrypt a CSV export
python decrypt_export.py password_export_john_20231201_143022.csv.encrypted -p mystrongpassword

# Decrypt a JSON export with custom output file
python decrypt_export.py password_export_jane_20231201_143022.json.encrypted -p mypassword -o decrypted_passwords.json
```

### Interactive Mode

If you don't provide the password as an argument, the script will prompt you to enter it:

```bash
python decrypt_export.py password_export_john_20231201_143022.csv.encrypted
Enter decryption password:
```

## Export File Formats

### CSV Format
Contains columns: website, category, username, password, exported_at

### JSON Format
```json
{
  "export_info": {
    "user": "username",
    "exported_at": "2023-12-01T14:30:22",
    "total_entries": 5
  },
  "passwords": [
    {
      "website": "example.com",
      "category": "Work",
      "username": "user@example.com",
      "password": "actual_password_here",
      "exported_at": "2023-12-01T14:30:22"
    }
  ]
}
```

## Security Best Practices

1. **Use Strong Export Passwords**: Choose a different password than your login password
2. **Store Export Password Securely**: Remember or securely store the export password
3. **Delete Files After Use**: Remove decrypted files when no longer needed
4. **Use Encrypted Storage**: Store encrypted export files in encrypted locations
5. **Regular Exports**: Export regularly as a backup, but change export passwords periodically

## Troubleshooting

### "Decryption failed" Error
- Verify you're using the correct export password
- Check that the file wasn't corrupted during download
- Ensure you're using the correct decryptor script

### File Format Issues
- CSV files can be opened with Excel, Google Sheets, or any text editor
- JSON files can be viewed with any JSON viewer or text editor

### Large Exports
- The encryption process may take longer for large password databases
- Ensure you have sufficient disk space for the export file