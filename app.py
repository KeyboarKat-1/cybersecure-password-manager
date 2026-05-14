from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(300))

class PasswordEntry(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    website = db.Column(db.String(100))

    account_username = db.Column(db.String(100))

    account_password = db.Column(db.String(200))

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        hashed_password = generate_password_hash(password)

        new_user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(new_user)

        db.session.commit()

        return "User Registered Successfully!"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(user.password, password):

            return redirect(url_for("dashboard"))

        else:
            return "Invalid Username or Password"
    return render_template("login.html")

@app.route("/delete/<int:id>")
def delete(id):

    entry = PasswordEntry.query.get(id)

    db.session.delete(entry)

    db.session.commit()

    return redirect(url_for("dashboard"))

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if request.method == "POST":

        website = request.form.get("website")

        account_username = request.form.get("account_username")

        account_password = request.form.get("account_password")

        new_entry = PasswordEntry(
            website=website,
            account_username=account_username,
            account_password=account_password
        )

        db.session.add(new_entry)

        db.session.commit()

    entries = PasswordEntry.query.all()

    return render_template(
        "dashboard.html",
        entries=entries
    )

    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)