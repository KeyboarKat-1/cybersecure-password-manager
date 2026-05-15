# Two-Factor Authentication (2FA) Setup Guide

This password manager now includes two-factor authentication (2FA) using Time-based One-Time Passwords (TOTP) for enhanced security.

## How 2FA Works

Two-factor authentication adds an extra layer of security to your account. In addition to your password, you'll need a time-based code from an authenticator app to log in.

### Supported Authenticator Apps
- **Google Authenticator** (Android/iOS)
- **Authy** (Android/iOS/Desktop)
- **Microsoft Authenticator** (Android/iOS)
- **1Password** (with TOTP support)
- **LastPass** (with TOTP support)
- Any TOTP-compatible authenticator app

## Setting Up 2FA

### Step 1: Access 2FA Settings
1. Log in to your password manager
2. Click the **"🔐 2FA Settings"** button in the dashboard header

### Step 2: Enable 2FA
1. On the 2FA settings page, click **"Enable 2FA"**
2. You'll see a QR code and a secret key

### Step 3: Add to Authenticator App
**Option A: Scan QR Code (Recommended)**
1. Open your authenticator app
2. Use the app's scanner to scan the QR code displayed
3. The app will automatically add your password manager account

**Option B: Manual Entry**
1. Open your authenticator app
2. Choose "Add account" or "Enter key manually"
3. Enter the secret key displayed on the page
4. Set the account name to "Password Manager" or your username

### Step 4: Verify Setup
1. Enter the 6-digit code from your authenticator app
2. Click **"Verify & Enable 2FA"**
3. You'll see a success message confirming 2FA is enabled

## Logging In with 2FA

After enabling 2FA, the login process changes:

1. **Enter your username and password** as usual
2. **Enter the 6-digit code** from your authenticator app
3. **Complete login** - you're now securely logged in

### What Happens During Login
- First, your username/password are verified
- If 2FA is enabled, you're redirected to the OTP verification page
- Enter the current 6-digit code from your authenticator app
- The code is valid for 30 seconds and changes automatically

## Managing 2FA

### Check 2FA Status
- Visit the 2FA settings page to see if 2FA is enabled or disabled

### Disable 2FA
- Go to 2FA settings
- Click **"Disable 2FA"**
- Confirm the action (this reduces your account security)

### Recovery Options
⚠️ **Important**: If you lose access to your authenticator app, you may be locked out of your account. Consider these backup options:

1. **Multiple Devices**: Set up the same account on multiple authenticator apps
2. **Backup Codes**: Some authenticator apps offer backup codes
3. **Device Backup**: Ensure your authenticator app data is backed up

## Security Benefits

### Enhanced Protection
- **Brute Force Protection**: Even if someone guesses your password, they need the OTP code
- **Phishing Resistance**: OTP codes are time-based and expire quickly
- **Account Recovery**: Adds protection against unauthorized password resets

### Best Practices
1. **Use a strong password** in combination with 2FA
2. **Keep your authenticator app updated**
3. **Back up your authenticator app data**
4. **Don't share OTP codes** with anyone
5. **Set up 2FA on all your important accounts**

## Troubleshooting

### "Invalid OTP code" Error
- Ensure your device time is synchronized
- Check that you're entering the code from the correct account
- Try generating a new code (wait 30 seconds for it to refresh)

### QR Code Won't Scan
- Ensure good lighting and camera focus
- Try zooming in/out of the QR code
- Use manual entry with the secret key instead

### Lost Authenticator Access
- If you have backup codes from your authenticator app, use them
- Contact support if available (this feature doesn't include backup codes yet)
- As a last resort, you may need to reset your account security

## Technical Details

### Implementation
- **TOTP Standard**: RFC 6238 compliant
- **HMAC-SHA1**: Industry standard hashing algorithm
- **30-Second Windows**: Codes are valid for 30 seconds
- **6-Digit Codes**: Standard 6-digit OTP format

### Security Features
- **Server-Side Verification**: OTP codes are verified on the server
- **No Code Reuse**: Each code can only be used once
- **Time Synchronization**: Accounts for minor time differences
- **Secure Storage**: Secrets are encrypted in the database

## Migration for Existing Users

Existing users can enable 2FA at any time:
1. Log in with your existing credentials
2. Go to 2FA settings
3. Follow the setup process above
4. Once enabled, 2FA becomes required for all future logins

## Future Enhancements

Planned improvements:
- **Backup Codes**: One-time use codes for account recovery
- **SMS 2FA**: Alternative to authenticator apps
- **Hardware Keys**: Support for FIDO U2F/WebAuthn
- **Account Recovery**: Secure process for regaining access

---

**Remember**: 2FA significantly improves your account security, but it's not infallible. Always use strong, unique passwords and keep your recovery options up to date.