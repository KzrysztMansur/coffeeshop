'''
THIS MODULE CONTAINS THE DB INFORMATION
here are all the models and here you can change but remember you have to commit
for the databases to change
'''
from app import app
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    # Define the relationship between User and Coffee tables
    unroasted_coffees = db.relationship('UnroastedCoffee', backref='user', lazy=True)
    roasted_coffees = db.relationship('RoastedCoffee', backref='user', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class UnroastedCoffee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    arrival_date = db.Column(db.String(10), nullable=False)

    # Foreign key relationship to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, name, amount, arrival_date, user_id):
        self.name = name
        self.amount = amount
        self.arrival_date = arrival_date
        self.user_id = user_id


class RoastedCoffee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    roasting_date = db.Column(db.String(10), nullable=False)
    order_number = db.Column(db.String(20), nullable=False)
    amount_sold = db.Column(db.Integer, nullable=False)
    roasting_level = db.Column(db.String(20), nullable=False)

    # Foreign key relationship to User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, name, amount, roasting_date, order_number, roasting_level, user_id):
        self.name = name
        self.amount = amount
        self.roasting_date = roasting_date
        self.order_number = order_number
        self.amount_sold = 0
        self.roasting_level = roasting_level
        self.user_id = user_id
