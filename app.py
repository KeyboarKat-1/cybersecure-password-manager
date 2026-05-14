from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet

app = Flask(__name__)

app.secret_key = "supersecretkey"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"


db = SQLAlchemy(app)

# ---------------- ENCRYPTION SETUP ---------------- #

key = b'6V4m1m7V9z0WgY3M5oYt6z1V4n8m2K5jL0pQxR7sT8U='

cipher = Fernet(key)


# ---------------- USER TABLE ---------------- #

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(300))


# ---------------- PASSWORD TABLE ---------------- #

class PasswordEntry(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    website = db.Column(db.String(100))

    account_username = db.Column(db.String(100))

    account_password = db.Column(db.String(500))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

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
            error_message = "Password must contain at least 8 characters"

        elif not any(char.isupper() for char in password):
            error_message = "Password must contain at least one uppercase letter"

        elif not any(char.isdigit() for char in password):
            error_message = "Password must contain at least one number"

        elif not any(char in "!@#$%^&*" for char in password):
            error_message = "Password must contain at least one special character"

        else:

            existing_user = User.query.filter_by(
                username=username
            ).first()

            if existing_user:
                error_message = "Username already exists"

            else:

                hashed_password = generate_password_hash(password)

                new_user = User(
                    username=username,
                    password=hashed_password
                )

                db.session.add(new_user)

                db.session.commit()

                return redirect(url_for("login"))


    return render_template(
        "register.html",
        error_message=error_message
    )
# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")

        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):

            session["user"] = username

            session["user_id"] = user.id

            return redirect(url_for("dashboard"))

        else:
            return "Invalid Username or Password"

    return render_template("login.html")

# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.pop("user", None)

    session.pop("user_id", None)

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

    return redirect(url_for("dashboard"))

# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    strength_message = ""

    if request.method == "POST":

        website = request.form.get("website")

        account_username = request.form.get("account_username")

        account_password = request.form.get("account_password")
 # ---------- PASSWORD STRENGTH ---------- #

        if len(account_password) < 8:
            strength_message = "Weak Password"

        elif any(char.isdigit() for char in account_password) and any(char.isupper() for char in account_password):
            strength_message = "Strong Password"

        else:
            strength_message = "Medium Password"


        # ---------- ENCRYPT PASSWORD ---------- #

        encrypted_password = cipher.encrypt(
            account_password.encode()
        ).decode()



        # ---------- SAVE ENTRY ---------- #

        new_entry = PasswordEntry(
            website=website,
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

        decrypted_entries.append({
            "id": entry.id,
            "website": entry.website,
            "account_username": entry.account_username,
            "account_password": decrypted_password
        })


    return render_template(
        "dashboard.html",
        entries=decrypted_entries,
        strength_message=strength_message,
        username=session["user"]
    )

# ---------------- DATABASE CREATE ---------------- #

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)