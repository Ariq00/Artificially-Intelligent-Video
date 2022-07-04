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


@user_bp.route("/saved_videos", methods=["GET", "POST"])
def saved_videos():
    if request.args.get("videoID"):
        video_id = request.args.get("videoID")
        video = Video.objects(id=video_id).first()
        return render_template("video.html",
                               video_filepath=video.filepath,
                               document_id=video.document_id,
                               video_title=video.title,
                               summary=video.summary,
                               sentiment=video.sentiment,
                               score=video.score,
                               concepts=video.concepts,
                               video_is_saved=True)

    else:
        videos = Video.objects(user=current_user)
        return render_template("saved_videos.html", videos=videos)
