from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# ===============================
# App Setup
# ===============================

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ===============================
# Models
# ===============================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), nullable=False)
    mealType = db.Column(db.String(50), nullable=False)
    mealName = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


with app.app_context():
    db.create_all()

# ===============================
# Helper
# ===============================

def user_is_logged_in():
    return "user_id" in session   

# ===============================
# Routes
# ===============================

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")
            return redirect(url_for("register"))

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session["user_id"] = user.id
            return redirect(url_for("list_meals"))

        flash("Invalid login.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/list")
def list_meals():
    if not logged_in():
        return redirect(url_for("login"))

    meals = Meal.query.filter_by(user_id=session["user_id"]).all()
    return render_template("items.html", meals=meals)

@app.route("/add", methods=["GET", "POST"])
def add_meal():
    if not logged_in():
        return redirect(url_for("login"))

    if request.method == "POST":
        meal = Meal(
        date=request.form["date"],
            mealType=request.form["mealType"],
            mealName=request.form["mealName"],
            user_id=session["user_id"]
        )
        db.session.add(meal)
        db.session.commit()

        flash("Meal added successfully.", "success")
        return redirect(url_for("list_meals"))
    