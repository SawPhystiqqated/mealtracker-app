from sqlalchemy.exc import IntegrityError
from flask import flash
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, Meal, User
import json, os, uuid
from datetime import datetime, timezone

import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

def require_login():
    if "user_id" not in session:
        flash("Please log in to access this page.", "warning")
        return False
    return True

# ---------- Routes ----------
@app.route("/")
def index():
    # send users straight to the form
    return redirect(url_for("add_meal"))

@app.route("/add", methods=["GET", "POST"])
def add_meal():
    if not require_login():
        return redirect(url_for("login"))

    if request.method == "POST":
        date = request.form.get("date").strip()
        meal_type = request.form.get("mealType").strip()
        meal_name = request.form.get("mealName").strip()
        serving_size = request.form.get("servingSize").strip()
        calories = float(request.form.get("calories"))
        dietary_flags = request.form.get("dietaryFlags", "")
        notes = request.form.get("notes", "")

        now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

        new_meal = Meal(
            user_id=session["user_id"],   # ✅ OWNERSHIP ENFORCED
            date=date,
            mealType=meal_type,
            mealName=meal_name,
            servingSize=serving_size,
            calories=calories,
            dietaryFlags=dietary_flags,
            notes=notes,
            createdAt=now_iso,
            updatedAt=now_iso
        )

        db.session.add(new_meal)
        db.session.commit()

        flash("Meal added successfully.", "success")
        return redirect(url_for("list_meals"))

    return render_template("add.html")

@app.route("/list")
def list_meals():
    if "user_id" not in session:
        return redirect(url_for("login"))

    meals = Meal.query.filter_by(user_id=session["user_id"]).all()

    return render_template(
        "items.html",
        meals=meals,
        meal_count=len(meals)
    )

@app.route("/delete/<int:meal_id>")
def delete_meal(meal_id):
    if not require_login():
        return redirect(url_for("login"))

    meal = Meal.query.get_or_404(meal_id)

    if meal.user_id != session["user_id"]:
        flash("You are not authorized to delete this item.")
        return redirect(url_for("list_meals"))

    db.session.delete(meal)
    db.session.commit()

    flash("Meal deleted successfully.", "success")
    return redirect(url_for("list_meals"))

@app.route("/edit/<int:meal_id>", methods=["GET", "POST"])
def edit_meal(meal_id):
    if not require_login():
        return redirect(url_for("login"))

    meal = Meal.query.get_or_404(meal_id)

    if meal.user_id != session["user_id"]:
        flash("You are not authorized to edit this item.")
        return redirect(url_for("list_meals"))

    if request.method == "POST":
        meal.date = request.form.get("date")
        meal.mealType = request.form.get("mealType")
        meal.mealName = request.form.get("mealName")
        meal.servingSize = request.form.get("servingSize")
        meal.calories = float(request.form.get("calories"))
        meal.dietaryFlags = request.form.get("dietaryFlags")
        meal.notes = request.form.get("notes")

        db.session.commit()
        flash("Meal updated successfully.")
        return redirect(url_for("list_meals"))

    return render_template("edit.html", meal=meal)

from sqlalchemy.exc import IntegrityError

@app.route("/register", methods=["GET", "POST"])
def register():
    
    if "user_id" in session:
        return redirect(url_for("list_meals"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User(username=username)
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()

            flash("Account created successfully. Please log in.", "success")
            return redirect(url_for("login"))

        except IntegrityError:
            db.session.rollback()
            return render_template(
                "register.html",
                error="Username already exists. Please choose another."
            )

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("list_meals"))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session["user_id"] = user.id

            meal_count = Meal.query.filter_by(user_id=user.id).count()

            if meal_count == 0:
                flash("Welcome! Login to continue")
                return redirect(url_for("add_meal"))

            flash("Logged in successfully!", "success")
            return redirect(url_for("list_meals"))

        flash("Invalid username or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "Logged out successful")
    return redirect(url_for("login"))

# --------- API Routes (Version 1) ---------

@app.route("/api/v1/meals", methods=["GET"])
def api_list_meals():
    # User must be logged in
    if "user_id" not in session:
        return jsonify({"error": "Authentication required"}), 401

    meals = Meal.query.filter_by(user_id=session["user_id"]).all()

    # Convert meals to a list of dictionaries
    meal_list = []
    for meal in meals:
        meal_list.append({
            "id": meal.id,
            "date": meal.date,
            "mealType": meal.mealType,
            "mealName": meal.mealName,
            "servingSize": meal.servingSize,
            "calories": meal.calories,
            "dietaryFlags": meal.dietaryFlags,
            "notes": meal.notes,
            "createdAt": meal.createdAt,
            "updatedAt": meal.updatedAt
        })

    return jsonify(meal_list), 200

@app.route("/api/v1/meals/<int:meal_id>", methods=["GET"])
def api_get_meal(meal_id):
    # User must be logged in
    if "user_id" not in session:
        return jsonify({"error": "Authentication required"}), 401

    meal = Meal.query.get(meal_id)

    # If meal does not exist
    if meal is None:
        return jsonify({"error": "Meal not found"}), 404

    # If meal does not belong to logged-in user
    if meal.user_id != session["user_id"]:
        return jsonify({"error": "Access denied"}), 403

    # Return the meal as JSON
    meal_data = {
        "id": meal.id,
        "date": meal.date,
        "mealType": meal.mealType,
        "mealName": meal.mealName,
        "servingSize": meal.servingSize,
        "calories": meal.calories,
        "dietaryFlags": meal.dietaryFlags,
        "notes": meal.notes,
        "createdAt": meal.createdAt,
        "updatedAt": meal.updatedAt
    }

    return jsonify(meal_data), 200

if __name__ == "__main__":
    app.run(debug=False)

# -------- App start ----------