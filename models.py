from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Meal(db.Model):
    __tablename__ = "meals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    date = db.Column(db.String(20))
    mealType = db.Column(db.String(50))
    mealName = db.Column(db.String(200))
    servingSize = db.Column(db.String(100))
    calories = db.Column(db.Float)
    dietaryFlags = db.Column(db.String(200))
    notes = db.Column(db.Text)
    createdAt = db.Column(db.String(50))
    updatedAt = db.Column(db.String(50))


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    meals = db.relationship("Meal", backref="user", lazy=True)
