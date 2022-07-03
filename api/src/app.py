from flask import Flask, flash, redirect, url_for
import mongoengine
from environment import secret_key, mongo_host
from flask_login import LoginManager
from models import User
from auth.routes import auth_bp
from main.routes import main_bp

mongoengine.connect(host=mongo_host)

app = Flask(__name__)
app.secret_key = secret_key
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # max upload size is 50mb

# register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

# login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    """ Takes a user ID and returns a user object or None if the user does
    not exist """
    if user_id is not None:
        return User.objects(id=user_id).first()
    return None


@login_manager.unauthorized_handler
def unauthorised():
    """Redirect unauthorised users to Login page."""
    flash('You must be logged in to view this page.', 'warning')
    return redirect(url_for('auth.login'))


if __name__ == "__main__":
    app.run(debug=True)
