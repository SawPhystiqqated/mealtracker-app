from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Meal
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_key")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()

def logged_in():
    return "user_id" in session


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
        user = User.query.filter_by(
            username=request.form["username"]
        ).first()

        if user and user.password == request.form["password"]:
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
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        # Convert form safely to a dict
        form = request.form.to_dict()

        try:
            meal = Meal(
                date=form.get("date"),
                meal_type=form.get("mealType"),
                meal_name=form.get("mealName"),

                serving_size=form.get("serving_size"),

                calories=int(form["calories"]) if form.get("calories") else None,
                protein=int(form["protein"]) if form.get("protein") else None,
                carbs=int(form["carbs"]) if form.get("carbs") else None,
                fats=int(form["fats"]) if form.get("fats") else None,

                user_id=session["user_id"]
            )

            db.session.add(meal)
            db.session.commit()
            return redirect(url_for("list_meals"))

        except Exception as e:
            print("ADD MEAL FAILED:", repr(e))
            print("FORM DATA:", form)
            return "Failed to save meal", 500

    return render_template("add.html")