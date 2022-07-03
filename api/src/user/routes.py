from flask import session, render_template, request, jsonify, flash, \
    redirect, url_for, Blueprint
from models import User, Video
from flask_login import current_user

user_bp = Blueprint('user', __name__)


@user_bp.route("/save_video", methods=["POST"])
def save_video():
    video_dict = request.get_json()
    Video(**video_dict, user=current_user).save()
    return video_dict
