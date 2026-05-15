# CyberSecure Password Manager - Deployment Guide for Render

This guide provides step-by-step instructions to deploy your CyberSecure password manager on Render.

## Table of Contents
1. [Pre-Deployment Preparation](#pre-deployment-preparation)
2. [Deployment Steps](#deployment-steps)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Preparation

### 1. Verify Project Structure
Ensure your project has all required files for Render deployment:

```
Procfile                      ← Instructions for Render on how to run the app
runtime.txt                   ← Python version specification
requirements.txt              ← Python dependencies
app.py                        ← Flask application (must have 'app' instance)
.env.example                  ← Environment variables template
static/                       ← CSS, JavaScript files
templates/                    ← HTML templates
instance/                     ← SQLite database (local dev only)
```

### 2. Install Local Dependencies
Before pushing to Render, install all dependencies locally:

```bash
pip install -r requirements.txt
```

### 3. Test Locally with Gunicorn
The production server uses Gunicorn, not Flask's development server:

```bash
# Install gunicorn if not in requirements.txt
pip install gunicorn

# Test with gunicorn (same as Render will use)
gunicorn app:app --workers 4 --worker-class sync --timeout 120 --bind 0.0.0.0:8000

# Application should be accessible at http://localhost:8000
```

### 4. Verify Environment Variables
Copy `.env.example` to `.env` and fill in your configuration:

```bash
cp .env.example .env
# Edit .env with your actual values
```

**Critical Environment Variables for Production:**
- `FLASK_SECRET_KEY`: Change to a strong secret key
- `FLASK_ENV`: Set to `production`
- `ENCRYPTION_KEY`: Your Fernet encryption key
- `DATABASE_URL`: PostgreSQL connection string (optional, for production DB)

### 5. Prepare Git Repository
Ensure your Git repository is clean and ready:

```bash
# Check status
git status

# Stage all changes (explained in detail below)
git add .

# Commit changes
git commit -m "Prepare project for Render deployment"

# Push to GitHub/GitLab
git push origin main
```

---

## Deployment Steps

### Step 1: Connect to Render

1. Go to [https://render.com](https://render.com)
2. Sign up for a free account or log in
3. Click **"New +"** button → Select **"Web Service"**

### Step 2: Connect Your Git Repository

1. Select your Git provider (GitHub/GitLab)
2. Authorize Render to access your repositories
3. Select the **fullstack-password-manager** repository
4. Choose the branch to deploy (usually **main** or **master**)

### Step 3: Configure the Web Service

Fill in the following information:

| Field | Value | Notes |
|-------|-------|-------|
| **Name** | cybersecure-pm | Give your service a memorable name |
| **Environment** | Python 3 | Select Python runtime |
| **Build Command** | `pip install -r requirements.txt` | Render uses this to install dependencies |
| **Start Command** | `gunicorn app:app --workers 4 --worker-class sync --timeout 120 --bind 0.0.0.0:${PORT:-8000}` | Render provides the PORT variable |
| **Region** | Select closest to your users | Example: US East |
| **Instance Type** | Free | Use free tier for testing/portfolio |

### Step 4: Set Environment Variables

In the Render dashboard, go to **Environment** section and add:

```
FLASK_ENV=production
FLASK_SECRET_KEY=<generate-a-strong-key>
ENCRYPTION_KEY=<your-fernet-key>
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

**How to generate FLASK_SECRET_KEY:**
```python
python -c 'import secrets; print(secrets.token_hex(32))'
```

**How to generate ENCRYPTION_KEY:**
```python
python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'
```

### Step 5: Database Setup (Optional)

For production, use PostgreSQL instead of SQLite:

1. In Render, create a **PostgreSQL Database** service
2. Copy the database connection string
3. Add to Environment Variables as `DATABASE_URL`

For development/portfolio use, SQLite works fine (stored in instance/database.db).

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Build the application
   - Start the Gunicorn server
3. Monitor the deployment logs
4. Once "Live" status appears, your app is deployed!

Your app will be accessible at: `https://cybersecure-pm.onrender.com`

---

## Configuration

### Static Files (CSS, JavaScript)

Flask automatically serves static files from the `static/` directory:
- `static/style.css` → `/static/style.css`
- `static/script.js` → `/static/script.js`

No additional configuration needed.

### Templates

HTML templates are served from the `templates/` directory:
- `templates/index.html` → `/` (home)
- `templates/login.html` → `/login`
- `templates/dashboard.html` → `/dashboard`

Flask automatically finds them with `render_template()`.

### Database

- **Development**: Uses SQLite (instance/database.db) ✓
- **Production**: Supports both SQLite and PostgreSQL
  - Set `DATABASE_URL` environment variable for PostgreSQL
  - app.py automatically detects and uses the correct database

---

## Verification

After deployment, verify everything works:

### 1. Check Application Status
```bash
# Visit your deployed app
https://cybersecure-pm.onrender.com

# You should see the landing page
```

### 2. Test Core Functionality

- [ ] Landing page loads
- [ ] Register new account
- [ ] Login with credentials
- [ ] Dashboard displays
- [ ] Can store/retrieve passwords
- [ ] AI assistant works
- [ ] Password generator works
- [ ] Export functionality works
- [ ] 2FA setup works (if enabled)

### 3. Check Logs

In Render dashboard → **Logs** section:
```
Check for any errors or warnings
Look for "Application started successfully" message
Verify no missing dependency errors
```

### 4. Test HTTPS

Your app should automatically use HTTPS:
```
https://cybersecure-pm.onrender.com ✓
http://cybersecure-pm.onrender.com  (redirects to HTTPS)
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. "No web process found in Procfile"
**Problem**: Render can't find Procfile
**Solution**: 
- Ensure Procfile exists in project root
- Procfile has no file extension (.txt, .md, etc.)
- File content is exactly: `web: gunicorn app:app --workers 4 --worker-class sync --timeout 120 --bind 0.0.0.0:${PORT:-8000}`

#### 2. "ModuleNotFoundError: No module named 'app'"
**Problem**: Flask app instance not found
**Solution**:
- Verify `app = Flask(__name__)` exists in app.py
- Check app.py is in project root directory
- Procfile command references correct module: `gunicorn app:app`

#### 3. "Static files not loading (404 errors)"
**Problem**: CSS/JavaScript files return 404
**Solution**:
```python
# In app.py, verify Flask is initialized correctly:
app = Flask(__name__)

# Static files should be in: static/
# Templates should be in: templates/

# Verify paths in HTML:
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
```

#### 4. "Database errors or data not persisting"
**Problem**: Database queries failing or data disappears
**Solution**:
- SQLite (instance/database.db) is file-based but not persistent on Render
- **For production**: Set `DATABASE_URL` to use PostgreSQL
- Create database migrations if needed
- Check `SQLALCHEMY_DATABASE_URI` configuration in app.py

#### 5. "Port binding error"
**Problem**: "Address already in use" or port conflicts
**Solution**:
- Render automatically sets `PORT` environment variable
- app.py respects this: `port = int(os.environ.get('PORT', 5000))`
- Procfile uses: `--bind 0.0.0.0:${PORT:-8000}`
- No manual port configuration needed

#### 6. "Module not found" (missing dependencies)
**Problem**: ImportError for packages like flask, gunicorn, etc.
**Solution**:
```bash
# Regenerate requirements.txt locally
pip freeze > requirements.txt

# Verify critical packages:
gunicorn
Flask
Flask-SQLAlchemy
cryptography
pyotp
qrcode
```

#### 7. "Service keeps restarting"
**Problem**: App crashes repeatedly
**Solution**:
- Check logs for errors: Render Dashboard → Logs
- Verify environment variables are set correctly
- Test locally: `gunicorn app:app`
- Check for syntax errors in app.py

---

## Performance Optimization

### Gunicorn Configuration

The Procfile uses optimized settings:
```
--workers 4              # Number of worker processes
--worker-class sync      # Synchronous worker (suitable for password manager)
--timeout 120            # 120 second timeout for long operations
```

For production, adjust based on your traffic:
- **Low traffic**: `--workers 2`
- **Medium traffic**: `--workers 4`
- **High traffic**: `--workers 8` (more expensive tier needed)

### Database Optimization

For production use:
1. **PostgreSQL** instead of SQLite
2. Add database indexes to frequently queried columns
3. Monitor slow queries in Render dashboard
4. Set appropriate connection pooling

---

## Security Considerations

✓ All critical security features are enabled:
- Session cookies are `Secure` and `HttpOnly`
- HTTPS is enforced
- CSRF protection via secret key
- Password hashing with werkzeug
- Encryption with cryptography library
- 2FA support with pyotp

⚠️ Before production deployment:
- [ ] Change `FLASK_SECRET_KEY` to a random value
- [ ] Change `ENCRYPTION_KEY` to your own value
- [ ] Set `FLASK_ENV=production`
- [ ] Enable 2FA for user accounts
- [ ] Use PostgreSQL for persistent storage
- [ ] Review security logs regularly

---

## Deployment Summary

| Step | Command | Notes |
|------|---------|-------|
| 1 | `pip install -r requirements.txt` | Install dependencies |
| 2 | `gunicorn app:app` | Test locally |
| 3 | `git add .` | Stage changes |
| 4 | `git commit -m "Ready for deployment"` | Commit |
| 5 | `git push origin main` | Push to GitHub |
| 6 | Connect Render dashboard | Point to repository |
| 7 | Set environment variables | FLASK_SECRET_KEY, ENCRYPTION_KEY, etc. |
| 8 | Deploy | Render auto-deploys on git push |

---

## Next Steps

After deployment:
1. Share your public URL with users
2. Add custom domain (optional)
3. Monitor logs and performance
4. Set up automated backups if using PostgreSQL
5. Monitor security logs for suspicious activity

---

## Support

For issues with Render:
- [Render Documentation](https://render.com/docs)
- Check Render Dashboard Logs
- Review Flask-SQLAlchemy docs for database issues
- Check Gunicorn documentation for server config

For issues with CyberSecure:
- Review app.py configuration
- Check environment variables
- Verify all dependencies installed
- Test locally with gunicorn

---

**Happy Deploying! Your CyberSecure Password Manager is now production-ready.** 🔐
