from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
from datetime import datetime, timedelta
import hashlib
import urllib.request
import urllib.error
import csv
import io
import json
import secrets
import pyotp
import qrcode
import io as StringIO

app = Flask(__name__)

app.secret_key = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

SESSION_TIMEOUT = timedelta(minutes=30)  # Inactivity timeout

db = SQLAlchemy(app)

# ---------------- ENCRYPTION SETUP ---------------- #

key = b'6V4m1m7V9z0WgY3M5oYt6z1V4n8m2K5jL0pQxR7sT8U='

cipher = Fernet(key)

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=5)
ADMIN_USERNAMES = ["admin"]


# ---------------- USER TABLE ---------------- #

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(300))

    failed_attempts = db.Column(db.Integer, default=0, nullable=False)

    lock_until = db.Column(db.DateTime, nullable=True)

    two_factor_secret = db.Column(db.String(32), nullable=True)

    two_factor_enabled = db.Column(db.Boolean, default=False)


# ---------------- PASSWORD TABLE ---------------- #

class PasswordEntry(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    website = db.Column(db.String(100))

    category = db.Column(db.String(50))

    account_username = db.Column(db.String(100))

    account_password = db.Column(db.String(500))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class LoginAttempt(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    username = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, nullable=False)
    source_ip = db.Column(db.String(45))
    method = db.Column(db.String(50))
    reason = db.Column(db.String(255))

    user = db.relationship("User", backref="login_attempts", lazy=True)


def get_table_columns(table_name):
    result = db.session.execute(text(f"PRAGMA table_info({table_name})"))
    return {row[1] for row in result.fetchall()}


def migrate_database():
    inspector = inspect(db.engine)
    existing_tables = inspector.get_table_names()

    if "user" in existing_tables:
        user_columns = get_table_columns("user")
        if "failed_attempts" not in user_columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN failed_attempts INTEGER DEFAULT 0 NOT NULL"))
        if "lock_until" not in user_columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN lock_until DATETIME"))
        if "two_factor_secret" not in user_columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN two_factor_secret VARCHAR(32)"))
        if "two_factor_enabled" not in user_columns:
            db.session.execute(text("ALTER TABLE user ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0"))
        db.session.commit()

    if "password_entry" in existing_tables:
        password_columns = get_table_columns("password_entry")
        if "category" not in password_columns:
            db.session.execute(text("ALTER TABLE password_entry ADD COLUMN category VARCHAR(50)"))
            db.session.commit()
        if "account_username" not in password_columns:
            db.session.execute(text("ALTER TABLE password_entry ADD COLUMN account_username VARCHAR(100)"))
            db.session.commit()
        if "account_password" not in password_columns:
            db.session.execute(text("ALTER TABLE password_entry ADD COLUMN account_password VARCHAR(500)"))
            db.session.commit()
        if "user_id" not in password_columns:
            db.session.execute(text("ALTER TABLE password_entry ADD COLUMN user_id INTEGER"))
            db.session.commit()


with app.app_context():
    db.create_all()
    migrate_database()


# ---------------- SESSION TIMEOUT CHECK ---------------- #

@app.before_request
def check_session_timeout():
    if 'user' in session:
        last_activity = session.get('last_activity')
        if last_activity:
            last_activity_time = datetime.fromisoformat(last_activity)
            if datetime.utcnow() - last_activity_time > SESSION_TIMEOUT:
                session.clear()
                flash("Session expired due to inactivity. Please log in again.", "info")
                return redirect(url_for('login'))
        session['last_activity'] = datetime.utcnow().isoformat()


def record_login_attempt(username, success, user_id=None, method='login', reason=''):
    attempt = LoginAttempt(
        username=username,
        user_id=user_id,
        success=success,
        source_ip=request.remote_addr or 'unknown',
        method=method,
        reason=reason
    )
    db.session.add(attempt)
    db.session.commit()


def is_admin_user():
    return session.get('user') in ADMIN_USERNAMES


# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    error_message = ""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # ---------- PASSWORD VALIDATION ---------- #
        if len(password) < 8:
            flash("Password must contain at least 8 characters", "error")

        elif not any(char.isupper() for char in password):
            flash("Password must contain at least one uppercase letter", "error")

        elif not any(char.isdigit() for char in password):
            flash("Password must contain at least one number", "error")

        elif not any(char in "!@#$%^&*" for char in password):
            flash("Password must contain at least one special character", "error")

        else:
            existing_user = User.query.filter_by(
                username=username
            ).first()

            if existing_user:
                flash("Username already exists", "error")

            else:
                hashed_password = generate_password_hash(password)
                new_user = User(
                    username=username,
                    password=hashed_password
                )
                db.session.add(new_user)
                db.session.commit()
                flash("Account created successfully. Please login.", "success")
                return redirect(url_for("login"))

    return render_template("register.html")
# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    # Check if user is in OTP verification step
    if session.get('login_step') == 'otp_required':
        return redirect(url_for('verify_otp'))

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.lock_until and user.lock_until > datetime.utcnow():
            remaining = int((user.lock_until - datetime.utcnow()).total_seconds() / 60) + 1
            record_login_attempt(username=username, success=False, user_id=user.id, method='login', reason='account locked')
            flash(f"Account locked due to failed login attempts. Try again in {remaining} minute(s).", "error")
            return redirect(url_for("login"))

        if user and check_password_hash(user.password, password):
            user.failed_attempts = 0
            user.lock_until = None
            db.session.commit()

            if user.two_factor_enabled and user.two_factor_secret:
                record_login_attempt(username=username, success=True, user_id=user.id, method='login', reason='password validated, awaiting OTP')
                session['pending_user_id'] = user.id
                session['pending_username'] = username
                session['login_step'] = 'otp_required'
                return redirect(url_for('verify_otp'))
            else:
                record_login_attempt(username=username, success=True, user_id=user.id, method='login', reason='successful login')
                session["user"] = username
                session["user_id"] = user.id
                session['last_activity'] = datetime.utcnow().isoformat()
                flash(f"Welcome back, {username}!", "success")
                return redirect(url_for("dashboard"))

        else:
            if user:
                user.failed_attempts = (user.failed_attempts or 0) + 1
                if user.failed_attempts >= MAX_LOGIN_ATTEMPTS:
                    user.lock_until = datetime.utcnow() + LOCKOUT_DURATION
                    record_login_attempt(username=username, success=False, user_id=user.id, method='login', reason='failed login - locked out')
                    flash(f"Account locked for {int(LOCKOUT_DURATION.total_seconds() / 60)} minutes after too many failed attempts.", "error")
                else:
                    remaining = MAX_LOGIN_ATTEMPTS - user.failed_attempts
                    record_login_attempt(username=username, success=False, user_id=user.id, method='login', reason='failed login - invalid credentials')
                    flash(f"Invalid username or password. {remaining} attempt(s) remaining.", "error")
                db.session.commit()
            else:
                record_login_attempt(username=username, success=False, method='login', reason='failed login - user not found')
                flash("Invalid username or password", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


# ---------------- OTP VERIFICATION ---------------- #

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if session.get('login_step') != 'otp_required':
        return redirect(url_for('login'))

    if request.method == "POST":
        otp_code = request.form.get("otp_code")

        user_id = session.get('pending_user_id')
        if not user_id:
            flash("Session expired. Please login again.", "error")
            session.clear()
            return redirect(url_for('login'))

        user = User.query.get(user_id)
        if not user or not user.two_factor_enabled or not user.two_factor_secret:
            flash("Two-factor authentication not properly configured.", "error")
            session.clear()
            return redirect(url_for('login'))

        # Verify OTP
        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(otp_code):
            record_login_attempt(username=session['pending_username'], success=True, user_id=user.id, method='otp', reason='OTP verified')
            session["user"] = session['pending_username']
            session["user_id"] = user.id
            session['last_activity'] = datetime.utcnow().isoformat()
            session.pop('login_step', None)
            session.pop('pending_user_id', None)
            session.pop('pending_username', None)
            flash(f"Welcome back, {session['user']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            record_login_attempt(username=session.get('pending_username', 'unknown'), success=False, user_id=user.id if user else None, method='otp', reason='invalid OTP')
            flash("Invalid OTP code. Please try again.", "error")
            return redirect(url_for('verify_otp'))

    return render_template("verify_otp.html")


# ---------------- 2FA SETUP ---------------- #

@app.route("/setup-2fa", methods=["GET", "POST"])
def setup_2fa():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if request.method == "POST":
        action = request.form.get("action")

        if action == "enable":
            # Generate new secret
            secret = pyotp.random_base32()
            user.two_factor_secret = secret
            user.two_factor_enabled = False  # Will be enabled after verification
            db.session.commit()

            # Generate QR code
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(name=user.username, issuer_name="Password Manager")

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            img_buffer = StringIO.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            session['temp_secret'] = secret
            return render_template("setup_2fa.html", qr_code=base64.b64encode(img_buffer.getvalue()).decode(), secret=secret, step="verify")

        elif action == "verify":
            otp_code = request.form.get("otp_code")
            temp_secret = session.get('temp_secret')

            if not temp_secret:
                flash("Session expired. Please start setup again.", "error")
                return redirect(url_for('setup_2fa'))

            totp = pyotp.TOTP(temp_secret)
            if totp.verify(otp_code):
                user.two_factor_enabled = True
                db.session.commit()
                session.pop('temp_secret', None)
                flash("Two-factor authentication has been enabled successfully!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid OTP code. Please try again.", "error")
                return redirect(url_for('setup_2fa'))

        elif action == "disable":
            user.two_factor_enabled = False
            user.two_factor_secret = None
            db.session.commit()
            flash("Two-factor authentication has been disabled.", "info")
            return redirect(url_for('dashboard'))

    return render_template("setup_2fa.html", user=user, step="setup")


# ---------------- QR CODE GENERATION ---------------- #

@app.route("/qr-code/<secret>")
def qr_code(secret):
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    if not user or user.two_factor_secret != secret:
        return "Unauthorized", 403

    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=user.username, issuer_name="Password Manager")

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = StringIO.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)

    return Response(img_buffer.getvalue(), mimetype='image/png')


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.pop("user", None)
    session.pop("user_id", None)
    session.pop("login_step", None)
    session.pop("pending_user_id", None)
    session.pop("pending_username", None)
    session.pop("temp_secret", None)
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("login"))


# ---------------- DELETE PASSWORD ---------------- #

@app.route("/delete/<int:id>")
def delete(id):

    if "user" not in session:
        return redirect(url_for("login"))

    entry = PasswordEntry.query.get(id)

    if entry and entry.user_id == session["user_id"]:
        db.session.delete(entry)
        db.session.commit()
        flash("Password entry deleted.", "info")

    return redirect(url_for("dashboard"))

# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    strength_message = ""

    if request.method == "POST":

        website = request.form.get("website")
        category = request.form.get("category")
        account_username = request.form.get("account_username")
        account_password = request.form.get("account_password")

        # ---------- PASSWORD STRENGTH ---------- #
        if len(account_password) < 8:
            flash("Weak password saved. Consider a stronger one.", "warning")
        elif any(char.isdigit() for char in account_password) and any(char.isupper() for char in account_password):
            flash("Password saved successfully. Strength: strong.", "success")
        else:
            flash("Password saved successfully. Strength: medium.", "info")

        breach_count = query_pwned_password(account_password)
        if breach_count is None:
            flash("Unable to verify if the password was breached. Please check your network.", "warning")
        elif breach_count > 0:
            flash(f"Warning: this password was found in {breach_count} known breaches.", "error")

        # ---------- ENCRYPT PASSWORD ---------- #
        encrypted_password = cipher.encrypt(
            account_password.encode()
        ).decode()

        # ---------- SAVE ENTRY ---------- #
        new_entry = PasswordEntry(
            website=website,
            category=category,
            account_username=account_username,
            account_password=encrypted_password,
            user_id=session["user_id"]
        )
        db.session.add(new_entry)
        db.session.commit()



    # ---------- USER-SPECIFIC PASSWORDS ---------- #

    entries = PasswordEntry.query.filter_by(
        user_id=session["user_id"]
    ).all()


    # ---------- DECRYPT PASSWORDS ---------- #

    decrypted_entries = []

    for entry in entries:

        decrypted_password = cipher.decrypt(
            entry.account_password.encode()
        ).decode()

        breach_count = query_pwned_password(decrypted_password)
        decrypted_entries.append({
            "id": entry.id,
            "website": entry.website,
            "category": entry.category,
            "account_username": entry.account_username,
            "account_password": decrypted_password,
            "breach_count": breach_count
        })

    # Calculate risk scores for dashboard display
    risk_assessment = calculate_risk_scores(decrypted_entries)
    
    # Add risk scores to entries
    for entry in decrypted_entries:
        matching_risk = next((r for r in risk_assessment['entry_scores'] 
                            if r['website'] == entry['website'] and r['username'] == entry['account_username']), None)
        if matching_risk:
            entry['risk_score'] = matching_risk['risk_score']
            entry['risk_level'] = get_risk_level(matching_risk['risk_score'])
        else:
            entry['risk_score'] = 0
            entry['risk_level'] = 'excellent'


    return render_template(
        "dashboard.html",
        entries=decrypted_entries,
        username=session["user"],
        is_admin=is_admin_user()
    )


@app.route("/admin")
def admin_dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    if not is_admin_user():
        flash("Admin access required.", "error")
        return redirect(url_for("dashboard"))

    now = datetime.utcnow()
    last_24h = now - timedelta(days=1)

    total_users = User.query.count()
    total_passwords = PasswordEntry.query.count()
    active_lockouts = User.query.filter(User.lock_until != None, User.lock_until > now).count()
    total_failed_attempts = LoginAttempt.query.filter_by(success=False).count()
    total_successful_logins = LoginAttempt.query.filter_by(success=True).count()
    recent_attempts = LoginAttempt.query.order_by(LoginAttempt.timestamp.desc()).limit(20).all()
    suspicious_attempts = LoginAttempt.query.filter(LoginAttempt.success == False, LoginAttempt.timestamp >= last_24h).order_by(LoginAttempt.timestamp.desc()).limit(10).all()
    repeated_failure_users = db.session.query(User.username, db.func.count(LoginAttempt.id).label('failures'))\
        .join(LoginAttempt, User.id == LoginAttempt.user_id)\
        .filter(LoginAttempt.success == False, LoginAttempt.timestamp >= last_24h)\
        .group_by(User.username)\
        .order_by(db.desc('failures'))\
        .limit(5).all()

    # Password security statistics
    entries = PasswordEntry.query.all()
    decrypted_entries = []
    for entry in entries:
        try:
            decrypted_password = cipher.decrypt(entry.account_password.encode()).decode()
        except Exception:
            decrypted_password = ''

        decrypted_entries.append({
            'website': entry.website,
            'account_username': entry.account_username,
            'account_password': decrypted_password,
            'category': entry.category or 'other',
            'breach_count': None
        })

    risk_assessment = calculate_risk_scores(decrypted_entries)
    risk_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'excellent': 0}
    for item in risk_assessment['entry_scores']:
        level = get_risk_level(item['risk_score'])
        risk_counts[level] += 1

    top_risk_entries = sorted(risk_assessment['entry_scores'], key=lambda item: item['risk_score'], reverse=True)[:6]

    return render_template(
        "admin_dashboard.html",
        username=session['user'],
        total_users=total_users,
        total_passwords=total_passwords,
        active_lockouts=active_lockouts,
        total_failed_attempts=total_failed_attempts,
        total_successful_logins=total_successful_logins,
        recent_attempts=recent_attempts,
        suspicious_attempts=suspicious_attempts,
        repeated_failure_users=repeated_failure_users,
        risk_assessment=risk_assessment,
        risk_counts=risk_counts,
        top_risk_entries=top_risk_entries,
        get_risk_level=get_risk_level
    )


# ---------------- EXPORT FUNCTIONALITY ---------------- #

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


def encrypt_data(data: str, password: str) -> bytes:
    """Encrypt data with user password and return encrypted data with embedded salt"""
    salt = secrets.token_bytes(16)
    key = derive_key(password, salt)
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data.encode())

    # Embed salt at the beginning of the encrypted data
    # Format: salt_length (4 bytes) + salt + encrypted_data
    salt_length = len(salt).to_bytes(4, byteorder='big')
    return salt_length + salt + encrypted_data


@app.route("/export/<format_type>", methods=["POST"])
def export_passwords(format_type):
    """Export passwords in encrypted CSV or JSON format"""
    if "user" not in session:
        return redirect(url_for("login"))

    export_password = request.form.get("export_password")
    if not export_password or len(export_password) < 8:
        flash("Export password must be at least 8 characters long.", "error")
        return redirect(url_for("dashboard"))

    # Get user's password entries
    entries = PasswordEntry.query.filter_by(user_id=session["user_id"]).all()

    # Decrypt passwords for export
    export_data = []
    for entry in entries:
        decrypted_password = cipher.decrypt(entry.account_password.encode()).decode()
        export_data.append({
            "website": entry.website,
            "category": entry.category or "Other",
            "username": entry.account_username,
            "password": decrypted_password,
            "exported_at": datetime.utcnow().isoformat()
        })

    # Generate export content based on format
    if format_type == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["website", "category", "username", "password", "exported_at"])
        writer.writeheader()
        writer.writerows(export_data)
        content = output.getvalue()
    elif format_type == "json":
        content = json.dumps({
            "export_info": {
                "user": session["user"],
                "exported_at": datetime.utcnow().isoformat(),
                "total_entries": len(export_data)
            },
            "passwords": export_data
        }, indent=2)
    else:
        flash("Invalid export format.", "error")
        return redirect(url_for("dashboard"))

    # Encrypt the export data
    encrypted_data = encrypt_data(content, export_password)

    # Create response with encrypted data
    response = make_response(encrypted_data)
    response.headers["Content-Type"] = "application/octet-stream"

    # Generate filename with timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"password_export_{session['user']}_{timestamp}.{format_type}.encrypted"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"

    flash(f"Passwords exported successfully as encrypted {format_type.upper()} file.", "success")
    return response


def get_risk_level(score):
    """Convert risk score to risk level string"""
    if score >= 80:
        return 'critical'
    elif score >= 60:
        return 'high'
    elif score >= 40:
        return 'medium'
    elif score >= 20:
        return 'low'
    else:
        return 'excellent'


# ---------------- AI CYBERSECURITY ASSISTANT ---------------- #

def analyze_passwords(entries):
    recommendations = []
    weak_passwords = []
    reused_passwords = []
    passwords = [entry['account_password'] for entry in entries]
    categories = {}
    
    # Group passwords by category
    for entry in entries:
        cat = entry.get('category', 'other')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(entry)
    
    # Calculate risk scores for each entry
    risk_assessment = calculate_risk_scores(entries)
    
    # Check for weak passwords
    common_weak = ['password', '123456', 'password123', 'qwerty', 'abc123', 'letmein', 'admin', 'welcome']
    
    for entry in entries:
        pwd = entry['account_password']
        issues = []
        
        if len(pwd) < 8:
            issues.append("Too short (less than 8 characters)")
        if not any(c.isupper() for c in pwd):
            issues.append("Missing uppercase letters")
        if not any(c.islower() for c in pwd):
            issues.append("Missing lowercase letters")
        if not any(c.isdigit() for c in pwd):
            issues.append("Missing numbers")
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?`~' for c in pwd):
            issues.append("Missing special characters")
        if pwd.lower() in common_weak:
            issues.append("Commonly used weak password")
        if pwd in [p for p in passwords if p != pwd]:
            issues.append("Password reused across multiple accounts")
        
        if issues:
            weak_passwords.append({
                'website': entry['website'],
                'username': entry['account_username'],
                'issues': issues
            })
    
    # Category-specific recommendations
    category_tips = {
        'banking': 'Banking accounts should use very strong passwords (16+ characters) and enable 2FA.',
        'social': 'Social media accounts are high-risk for breaches. Use unique passwords and monitor account activity.',
        'email': 'Email accounts are critical - they can be used to reset other passwords. Use maximum security.',
        'shopping': 'Shopping accounts may contain payment information. Use strong, unique passwords.',
        'work': 'Work accounts often contain sensitive company data. Follow corporate security policies.',
        'government': 'Government accounts require maximum security. Use the strongest available passwords.',
        'health': 'Health accounts contain sensitive personal information. Use HIPAA-compliant password practices.',
        'education': 'Educational accounts may contain personal academic records. Use strong passwords.'
    }
    
    for cat, cat_entries in categories.items():
        if cat in category_tips:
            recommendations.append({
                'type': 'info',
                'title': f'{cat.title()} Account Security',
                'message': category_tips[cat],
                'details': []
            })
    
    # General recommendations
    if weak_passwords:
        recommendations.insert(0, {
            'type': 'critical',
            'title': 'Weak Passwords Detected',
            'message': f'Found {len(weak_passwords)} passwords that need improvement.',
            'details': weak_passwords
        })
    
    # Password variety
    total_passwords = len(passwords)
    unique_passwords = len(set(passwords))
    if unique_passwords < total_passwords:
        recommendations.append({
            'type': 'warning',
            'title': 'Password Reuse',
            'message': f'You have {total_passwords - unique_passwords} duplicate passwords. Use unique passwords for each account.',
            'details': []
        })
    
    # General security tips
    recommendations.extend([
        {
            'type': 'info',
            'title': 'Use Smart Password Generation',
            'message': 'Try our new category-based password generator for memorable yet secure passwords.',
            'details': []
        },
        {
            'type': 'info',
            'title': 'Enable Two-Factor Authentication',
            'message': 'Add 2FA to your important accounts for extra security.',
            'details': []
        },
        {
            'type': 'info',
            'title': 'Regular Password Updates',
            'message': 'Change passwords every 3-6 months, especially for critical accounts.',
            'details': []
        }
    ])
    
    return recommendations, risk_assessment


def calculate_risk_scores(entries):
    """
    Calculate comprehensive risk scores for password security assessment.
    
    Returns a dictionary with:
    - overall_score: Overall risk score (0-100, higher = more risk)
    - risk_level: 'Critical', 'High', 'Medium', 'Low', 'Excellent'
    - category_scores: Risk scores by category
    - entry_scores: Individual entry risk assessments
    - risk_factors: Breakdown of risk contributors
    """
    
    if not entries:
        return {
            'overall_score': 0,
            'risk_level': 'Excellent',
            'category_scores': {},
            'entry_scores': [],
            'risk_factors': {}
        }
    
    passwords = [entry['account_password'] for entry in entries]
    total_entries = len(entries)
    
    # Risk factor weights
    WEIGHTS = {
        'password_reuse': 25,
        'weak_patterns': 20,
        'breach_history': 20,
        'password_strength': 15,
        'category_criticality': 10,
        'account_age': 5,
        'uniqueness': 5
    }
    
    # Category criticality scores (higher = more critical)
    category_criticality = {
        'banking': 100,
        'government': 95,
        'health': 90,
        'work': 85,
        'email': 80,
        'shopping': 60,
        'social': 50,
        'education': 40,
        'entertainment': 30,
        'other': 20
    }
    
    # Common weak patterns
    common_patterns = [
        r'123456', r'password', r'qwerty', r'abc123', r'letmein', r'admin', r'welcome',
        r'111111', r'123123', r'abcabc', r'password123', r'admin123', r'root123'
    ]
    
    # Sequential patterns
    sequential_patterns = [
        r'12345', r'23456', r'34567', r'45678', r'56789', r'67890',
        r'abcdef', r'bcdefg', r'cdefgh', r'defghi', r'efghij', r'fghijk'
    ]
    
    entry_scores = []
    category_scores = {}
    risk_factors = {
        'password_reuse': 0,
        'weak_patterns': 0,
        'breach_history': 0,
        'password_strength': 0,
        'category_criticality': 0,
        'account_age': 0,
        'uniqueness': 0
    }
    
    # Analyze each entry
    for entry in entries:
        pwd = entry['account_password']
        category = entry.get('category', 'other')
        breach_count = entry.get('breach_count', 0)
        
        entry_risk = {
            'website': entry['website'],
            'username': entry['account_username'],
            'category': category,
            'risk_score': 0,
            'risk_factors': {}
        }
        
        # 1. Password Reuse Risk
        reuse_count = passwords.count(pwd) - 1  # Subtract 1 for self
        reuse_risk = min(reuse_count * 20, 100)  # Max 100 for 5+ reuses
        entry_risk['risk_factors']['password_reuse'] = reuse_risk
        risk_factors['password_reuse'] += reuse_risk
        
        # 2. Weak Patterns Risk
        pattern_risk = 0
        if len(pwd) < 8:
            pattern_risk += 30
        if pwd.lower() in [p.lower() for p in common_patterns]:
            pattern_risk += 40
        if any(seq in pwd.lower() for seq in sequential_patterns):
            pattern_risk += 20
        if not any(c.isupper() for c in pwd):
            pattern_risk += 10
        if not any(c.islower() for c in pwd):
            pattern_risk += 10
        if not any(c.isdigit() for c in pwd):
            pattern_risk += 10
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?`~' for c in pwd):
            pattern_risk += 10
        
        entry_risk['risk_factors']['weak_patterns'] = min(pattern_risk, 100)
        risk_factors['weak_patterns'] += pattern_risk
        
        # 3. Breach History Risk
        breach_risk = 0
        if breach_count is None:
            breach_risk = 20  # Unknown breach status
        elif breach_count > 0:
            breach_risk = min(breach_count * 5, 100)  # 5 points per breach
        
        entry_risk['risk_factors']['breach_history'] = breach_risk
        risk_factors['breach_history'] += breach_risk
        
        # 4. Password Strength Risk (inverse of strength)
        entropy = estimate_entropy(pwd)
        strength_score = min(max(entropy * 1.1, 0), 100)
        strength_risk = 100 - strength_score
        entry_risk['risk_factors']['password_strength'] = strength_risk
        risk_factors['password_strength'] += strength_risk
        
        # 5. Category Criticality Risk
        cat_risk = category_criticality.get(category, 20)
        entry_risk['risk_factors']['category_criticality'] = cat_risk
        risk_factors['category_criticality'] += cat_risk
        
        # 6. Account Age Risk (simplified - could be enhanced with actual dates)
        age_risk = 10  # Base risk for older accounts
        entry_risk['risk_factors']['account_age'] = age_risk
        risk_factors['account_age'] += age_risk
        
        # 7. Uniqueness Risk (how unique is this password in the set)
        unique_chars = len(set(pwd))
        uniqueness_score = (unique_chars / len(pwd)) * 100 if pwd else 0
        uniqueness_risk = 100 - uniqueness_score
        entry_risk['risk_factors']['uniqueness'] = uniqueness_risk
        risk_factors['uniqueness'] += uniqueness_risk
        
        # Calculate total entry risk score
        total_risk = sum(entry_risk['risk_factors'].values()) / len(entry_risk['risk_factors'])
        entry_risk['risk_score'] = min(total_risk, 100)
        
        entry_scores.append(entry_risk)
        
        # Update category scores
        if category not in category_scores:
            category_scores[category] = {'total_risk': 0, 'count': 0, 'entries': []}
        category_scores[category]['total_risk'] += entry_risk['risk_score']
        category_scores[category]['count'] += 1
        category_scores[category]['entries'].append(entry_risk)
    
    # Calculate average category scores
    for cat in category_scores:
        category_scores[cat]['average_risk'] = category_scores[cat]['total_risk'] / category_scores[cat]['count']
    
    # Calculate overall risk score (weighted average of all factors)
    total_weighted_risk = 0
    total_weight = 0
    
    for factor, weight in WEIGHTS.items():
        factor_avg = risk_factors[factor] / total_entries if total_entries > 0 else 0
        total_weighted_risk += factor_avg * (weight / 100)
        total_weight += weight
    
    overall_score = (total_weighted_risk / total_weight) * 100 if total_weight > 0 else 0
    overall_score = min(max(overall_score, 0), 100)
    
    # Determine risk level
    if overall_score >= 80:
        risk_level = 'Critical'
    elif overall_score >= 60:
        risk_level = 'High'
    elif overall_score >= 40:
        risk_level = 'Medium'
    elif overall_score >= 20:
        risk_level = 'Low'
    else:
        risk_level = 'Excellent'
    
    # Normalize risk factors
    for factor in risk_factors:
        risk_factors[factor] = risk_factors[factor] / total_entries if total_entries > 0 else 0
    
    return {
        'overall_score': round(overall_score, 1),
        'risk_level': risk_level,
        'category_scores': category_scores,
        'entry_scores': entry_scores,
        'risk_factors': risk_factors
    }


def estimate_entropy(password):
    """Estimate password entropy for strength calculation"""
    if not password:
        return 0
    
    has_upper = bool(any(c.isupper() for c in password))
    has_lower = bool(any(c.islower() for c in password))
    has_number = bool(any(c.isdigit() for c in password))
    has_symbol = bool(any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?`~' for c in password))
    
    alphabet_size = 0
    if has_upper: alphabet_size += 26
    if has_lower: alphabet_size += 26
    if has_number: alphabet_size += 10
    if has_symbol: alphabet_size += 32
    if ' ' in password: alphabet_size += 1
    
    if alphabet_size == 0:
        return 0
    
    return len(password) * (alphabet_size ** 0.5)  # Simplified entropy calculation


@app.route("/ai-assistant")
def ai_assistant():
    if "user" not in session:
        return redirect(url_for("login"))
    
    entries = PasswordEntry.query.filter_by(user_id=session["user_id"]).all()
    
    decrypted_entries = []
    for entry in entries:
        decrypted_password = cipher.decrypt(entry.account_password.encode()).decode()
        breach_count = query_pwned_password(decrypted_password)
        decrypted_entries.append({
            "id": entry.id,
            "website": entry.website,
            "category": entry.category,
            "account_username": entry.account_username,
            "account_password": decrypted_password,
            "breach_count": breach_count
        })
    
    recommendations, risk_assessment = analyze_passwords(decrypted_entries)
    
    return render_template("ai-assistant.html", 
                         recommendations=recommendations, 
                         risk_assessment=risk_assessment,
                         username=session["user"])


def query_pwned_password(password):
    try:
        sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'FullStackPasswordManager/1.0'
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
        for line in body.splitlines():
            hash_suffix, count = line.split(':')
            if hash_suffix == suffix:
                return int(count)
        return 0
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError):
        return None

# ---------------- DATABASE CREATE ---------------- #

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)