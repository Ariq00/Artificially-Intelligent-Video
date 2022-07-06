from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
import mongoengine
from environment import secret_key, mongo_host, mail_server, mail_port, \
    mail_password, mail_username, mail_use_ssl, mail_use_tls

login_manager = LoginManager()
mail = Mail()
mongoengine.connect(host=mongo_host)


def create_app():
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

    register_extensions(app)
    register_blueprints(app)

    return app


def register_extensions(app):
    # Initialise the objects for the Flask app instance
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    mail.init_app(app)


def register_blueprints(app):
    from main.routes import main_bp
    app.register_blueprint(main_bp)

    from auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from user.routes import user_bp
    app.register_blueprint(user_bp)
