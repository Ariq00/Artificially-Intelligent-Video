from flask import render_template, request, Blueprint, jsonify
from models import Video
from flask_login import current_user, login_required
from watson_assistant import watson_assistant_query
from datetime import timedelta, datetime

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
    videos = Video.objects(user=current_user)
    results = []

    # loop through each video and send search query to watson response endpoint
    for video in videos:
        video_result = watson_assistant_query(search_query, video.document_id)
        if len(video_result["timestamps"]) > 0:
            video_dict = video.to_dict()
            video_dict["timestamps"] = video_result["timestamps"]

            video_dict["formatted_timestamps"] = [
                datetime.fromtimestamp(timestamp).strftime("%-M:%S")
                for timestamp in video_result["timestamps"]]

            results.append(video_dict)

    return render_template("search_results.html", results=results,
                           search_query=search_query)
