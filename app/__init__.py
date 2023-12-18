
"""
HERE are all the main components of the app
and all the critical information is saved or edited like the 
"""
from flask import Flask
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://coffeenventory_user:YlwgdNEoYahJzpTpmk3GFNZn2SFDKWeO@dpg-clvrh2la73kc73bsj4pg-a.oregon-postgres.render.com/coffeenventory"
#postgresql://coffeenventory_user:YlwgdNEoYahJzpTpmk3GFNZn2SFDKWeO@dpg-clvrh2la73kc73bsj4pg-a.oregon-postgres.render.com/coffeenventory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'WEBVBWEUC93CB2EOCIQNC9823'
app.config['ENV'] = 'production'


from .models import db, User, UnroastedCoffee, RoastedCoffee
from .views import app
from .auth import auth

db.init_app(app)  # Initialize db with the app


"""
with app.app_context():
    try:
        # Begin a transaction
        db.session.begin()

        # Your database operations here
        new_user = User(username='Cecilia1795', password='CR1795!')
        db.session.add(new_user)
        # Commit the transaction
        db.session.commit()
    except Exception as e:
        # Rollback the transaction in case of an error
        db.session.rollback()
        print(f"Error: {str(e)}")
    finally:
        # Close the transaction
        db.session.close()
"""

"""
with app.app_context():
    # Create the database and tables
    db.create_all()
"""