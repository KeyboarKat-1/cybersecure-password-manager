# Git Commands for Render Deployment

This file contains the exact terminal commands needed to prepare your CyberSecure Password Manager for Render deployment.

## Command Reference

### 1. Check Current Status
```bash
git status
```
This shows all modified and new files that need to be staged.

### 2. Stage All Deployment Files
```bash
git add .
```
This stages all files including:
- Procfile (Render deployment configuration)
- runtime.txt (Python version)
- requirements.txt (updated with gunicorn)
- app.py (updated for production)
- .env.example (environment variables template)
- DEPLOYMENT.md (deployment guide)
- .gitignore (prevent accidental commits of sensitive files)

### 3. Commit Changes
```bash
git commit -m "Prepare CyberSecure for Render deployment: Add Procfile, production configuration, and deployment documentation"
```

### 4. Push to GitHub/GitLab
```bash
git push origin main
```
Or if your main branch is named differently:
```bash
git push origin master
```

## Full Sequence (Copy and Paste)

Run these commands in order:

```bash
# Navigate to project directory
cd "c:\Users\vatal\New folder (2)\fullstack-password-manager"

# Check what files have changed
git status

# Stage all deployment-related changes
git add .

# Verify staged files (optional)
git status

# Commit with deployment message
git commit -m "Prepare CyberSecure for Render deployment: Add Procfile, production configuration, and deployment documentation"

# Push to remote repository
git push origin main
```

## What Gets Committed

### New Files
- **Procfile** - Tells Render how to run the application
- **runtime.txt** - Specifies Python 3.11.11 version
- **DEPLOYMENT.md** - Complete deployment guide
- **.gitignore** - Prevents committing sensitive files (.env)
- **test_deployment.py** - Tests if app imports correctly
- **test_dependencies.py** - Tests if all dependencies are installed
- **.env.example** - Template for environment variables

### Modified Files
- **requirements.txt** - Updated with all dependencies and gunicorn
- **app.py** - Updated for production configuration and environment variables

### NOT Committed (Protected by .gitignore)
- **.env** - Local environment variables file (secrets)
- **instance/database.db** - Local SQLite database
- **__pycache__/** - Python cache files
- **.vscode/** - IDE configuration
- **venv/** or **env/** - Virtual environment

## Verification After Push

1. Go to your GitHub/GitLab repository
2. Verify that Procfile is in the root directory
3. Verify that runtime.txt is in the root directory
4. Confirm all changes appear in the latest commit

## Reverting if Needed

If you need to undo the commit (before pushing):
```bash
git reset HEAD~1
```

If you need to undo the staging (before committing):
```bash
git reset
```

## Next Steps After Git Push

Once you've pushed these files to GitHub:

1. Log into Render.com
2. Create new Web Service
3. Connect your GitHub repository
4. Configure environment variables (see DEPLOYMENT.md)
5. Deploy!

---

**You're ready to deploy!** After the git push, proceed with Render deployment following the steps in DEPLOYMENT.md.
