from flask import Blueprint
from models import User

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route("/register")
def register():
    User(
        password="test",
        email="tests@mail.com",
        first_name="first_name",
        last_name="last_name",
    ).save()
    return "REGISTRATION PAGE"
