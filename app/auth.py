from flask import Blueprint, request, render_template, url_for, redirect, session
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
from app.models import User
from app import app
"""
HERE are all the routes that require user authorization
"""
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'


auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': #si utiliza el metodo POST
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            # Cuando se encuentre el usuario en la base de datos
            return redirect(url_for('dashboard'))
        else:
            # Mostrar un error 
            error_message = 'Invalid username or password. Please try again.'
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')

@login_manager.user_loader
def load_user(user_id):
    from app.models import User  # Import the User model here to avoid circular import
    return User.query.get(int(user_id))


@auth.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))


