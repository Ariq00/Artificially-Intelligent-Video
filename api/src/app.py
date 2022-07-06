from flask import Flask, flash, redirect, url_for
import mongoengine
from environment import secret_key, mongo_host, mail_server, mail_port, \
    mail_password, mail_username, mail_use_ssl, mail_use_tls
from flask_login import LoginManager
from models import User
from auth.routes import auth_bp
from main.routes import main_bp
from user.routes import user_bp
from flask_mail import Mail, Message

mongoengine.connect(host=mongo_host)

app = Flask(__name__)
app.secret_key = secret_key
app.config[
    'MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # max payload size is 500mb
app.config['MAIL_SERVER'] = mail_server
app.config['MAIL_PORT'] = mail_port
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password
app.config['MAIL_USE_TLS'] = mail_use_tls
app.config['MAIL_USE_SSL'] = mail_use_ssl

# register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(user_bp)

# login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.objects(id=user_id).first()
    return None


@login_manager.unauthorized_handler
def unauthorised():
    flash('You must be logged in to view this page.', 'warning')
    return redirect(url_for('auth.login'))


def send_email():
    msg = Message('Hello from the other side!',
                  sender='smart.video.project@gmail.com',
                  recipients=['smart.video.project@gmail.com'])
    msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works"
    mail.send(msg)
    return "Message sent!"


if __name__ == "__main__":
    app.run(debug=True)
