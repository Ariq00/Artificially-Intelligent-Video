from flask import render_template, request, Blueprint
from models import Video
from flask_login import current_user, login_required

user_bp = Blueprint('user', __name__)


@user_bp.route("/save_video", methods=["POST"])
@login_required
def save_video():
    video_dict = request.get_json()
    Video(**video_dict, user=current_user).save()
    return video_dict


@user_bp.route("/saved_videos", methods=["GET"])
@login_required
def saved_videos():
    if request.args.get("videoID"):
        video_id = request.args.get("videoID")
        video = Video.objects(id=video_id).first()
        return render_template("video.html", **video.to_dict(),
                               video_is_saved=True)
    else:
        videos = Video.objects(user=current_user)
        return render_template("saved_videos.html", videos=videos)


@user_bp.route("/search_saved_videos", methods=["GET"])
@login_required
def search_saved_videos():
    search_query = request.args.get("searchQuery")

    # get all videos first
    # loop through each video and send search query to watson response endpoint
    # if timestamp exists: save video.to_dict() and add timestamp to dict with key as "timestamp"
    # pass a list of dictionaries to render template
    return search_query
