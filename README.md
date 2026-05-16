# CyberSecure Password Manager

[![Live Demo](https://img.shields.io/badge/Live-Demo-blue?style=for-the-badge&logo=render)](https://cybersecure-password-manager.onrender.com) [![Repo](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/KeyboarKat-1/cybersecure-password-manager)

## 🔐 Short Description

CyberSecure Password Manager is a full-stack cybersecurity web application built with Flask, Python, SQLite, HTML, CSS, and JavaScript. It delivers a modern, dark-themed vault experience with advanced security features, a responsive dashboard, and intelligent password insights.

## 🌐 Live Demo

Explore the deployed application here:

👉 [https://cybersecure-password-manager.onrender.com](https://cybersecure-password-manager.onrender.com)

> **Note:** The project is hosted on Render free tier, so the initial startup may take a few seconds after inactivity.
## 🚀 Features

- **Secure password vault** for storing encrypted credentials
- **AES-style encryption concept** to protect saved data
- **2FA authentication** for an extra layer of login security
- **Password strength analysis** with intelligent feedback
- **AI security assistant** for proactive digital safety recommendations
- **Password generator** for strong, unique credentials
- **Breach monitoring** awareness for compromised accounts
- **Export passwords** securely as encrypted CSV and JSON
- **Search and filter system** for quick vault navigation
- **Dark modern cybersecurity UI** with responsive design
- **Responsive dashboard** built for desktop and mobile workflows

## 🖼️ Screenshots

> _Add screenshots here once available. Use images to showcase the login page, dashboard, generator, export system, and AI assistant._

## 🧰 Technologies Used

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** SQLite
- **Security:** cryptography, pyotp, werkzeug.security
- **Frontend:** HTML, CSS, JavaScript
- **Deployment:** Render, Gunicorn
- **Utilities:** qrcode, requests

## 🛠️ Installation Steps

1. Clone the repository:
   ```bash
git clone https://github.com/KeyboarKat-1/cybersecure-password-manager.git
cd cybersecure-password-manager
```
2. Create and activate a virtual environment:
   ```bash
python -m venv venv
venv\Scripts\activate
```
3. Install dependencies:
   ```bash
pip install -r requirements.txt
```
4. Create an environment variables file from the example:
   ```bash
copy .env.example .env
```
5. Update `.env` with secure production values:
   - `FLASK_SECRET_KEY`
   - `ENCRYPTION_KEY`
   - `FLASK_ENV=production` for deployed environments
6. Run the app locally:
   ```bash
python app.py
```
7. Open the app in your browser:
   ```text
http://localhost:5000
```

## 📁 Project Structure

```text
fullstack-password-manager/
├── app.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── README.md
├── .env.example
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── demo_dashboard.html
│   ├── admin_dashboard.html
│   ├── ai-assistant.html
│   ├── setup_2fa.html
│   └── verify_otp.html
├── static/
│   ├── style.css
│   ├── script.js
│   └── landing.js
├── instance/
└── test_2fa.py
```

## ☁️ Deployment Information

This application is ready for production deployment on Render using Gunicorn.

- **Render start command:** `gunicorn app:app --workers 4 --worker-class sync --timeout 120 --bind 0.0.0.0:${PORT:-8000}`
- **Procfile:** `web: gunicorn app:app`
- **Python runtime:** `python-3.11.11` defined in `runtime.txt`

### Recommended Render environment variables

- `FLASK_ENV=production`
- `FLASK_SECRET_KEY=<secure-random-key>`
- `ENCRYPTION_KEY=<secure-fernet-key>`
- `SESSION_COOKIE_SECURE=True`
- `SESSION_COOKIE_HTTPONLY=True`
- `DATABASE_URL` (optional for PostgreSQL)

## 🌱 Future Improvements

- Add **PostgreSQL** production database support
- Add **email verification** and password reset flows
- Add **role-based access control** for admin features
- Add **activity logs** and security audit trails
- Improve **data export security** and encrypted file management
- Add **native mobile-friendly UI enhancements**
- Add **API endpoints** for secure integrations

## 👩‍💻 Author

**Anusha Vatala**

- GitHub: [https://github.com/KeyboarKat-1](https://github.com/KeyboarKat-1)
- Repository: [https://github.com/KeyboarKat-1/cybersecure-password-manager](https://github.com/KeyboarKat-1/cybersecure-password-manager)

---

Built for portfolio-level cybersecurity projects with secure design, responsive UI, and powerful vault functionality.  Keep your secrets safe with CyberSecure. 🔐