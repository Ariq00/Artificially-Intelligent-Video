from flask import render_template, request, Blueprint, flash, redirect, \
    url_for, session
from models import Video
from flask_login import current_user, login_required
from watson_assistant import watson_assistant_query
from datetime import datetime
import json
import os
from main.utilities import process_upload, \
    summarise_and_analyse, send_email
from transcribe import process_audio
from ibm_cloud_sdk_core.api_exception import ApiException
import watson_discovery
from pydub.exceptions import CouldntDecodeError

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


@user_bp.route("/delete_saved_videos", methods=["POST"])
@login_required
def delete_saved_videos():
    video_ids = json.loads(request.form["video_ids_json"])
    for id_active in video_ids:
        video = Video.objects(id=id_active.replace("_active", "")).first()
        try:
            os.remove(f"./static{video.filepath}")
        except FileNotFoundError:
            print("Could not delete video file. File does not exist")
        watson_discovery.delete_transcript(watson_discovery.setup_discovery(),
                                           video.document_id)
        video.delete()
    flash("Videos successfully deleted", "info")
    return redirect(url_for("user.saved_videos"))


@user_bp.route("/upload_multiple_videos", methods=["POST"])
@login_required
def upload_multiple_videos():
    user_id = session.get("user_id")

    if request.form["video"] == "youtube":
        # format urls
        video_list = [url.replace("\r", "").strip() for url in
                      request.form['youtubeUrls'].split("\n")]
    else:
        video_list = request.files.getlist("multipleFile[]")

    video_status_dict = {}

    for index, video in enumerate(video_list, 1):
        request_array = [request.form["video"], video]
        upload_result = process_upload(request_array, user_id)

        if upload_result["status"] == "failed":
            if upload_result.get("media_title"):
                title = upload_result["media_title"]

                if title == "Video Not Available":
                    title = f"Video {index}"
            else:
                title = f"Video {index}"
            video_status_dict[title] = upload_result["message"]

            continue

        media_title, static_media_filepath = \
            upload_result["media_title"], upload_result[
                "static_media_filepath"]

        # transcribe audio
        try:
            process_audio(static_media_filepath, user_id,
                          request.form['languageSubmit'])
        except CouldntDecodeError:
            video_status_dict[media_title] = "Couldn't decode file"
            continue

        transcript_filename = f"{user_id}.json"

        try:
            summary, score, sentiment, concepts = summarise_and_analyse(
                transcript_filename)

        except ApiException:
            video_status_dict[
                media_title] = "Could not analyse video. Video has no audio content!"
            continue

        # upload to discovery
        discovery = watson_discovery.setup_discovery()
        document_id = watson_discovery.upload_transcript(discovery,
                                                         transcript_filename)
        # delete transcript
        os.remove(f"./transcripts/{transcript_filename}")

        Video(
            filepath=static_media_filepath.replace(
                "./static", ""),
            document_id=document_id,
            title=media_title,
            summary=summary,
            sentiment=sentiment,
            score=score,
            concepts=concepts,
            user=current_user
        ).save()

        video_status_dict[media_title] = "Success"

    # send email
    msg_body = f"Hi {current_user.first_name},\n\nThe status of your submitted videos is shown below:\n\n"
    for video_title in video_status_dict:
        msg_body += f"{video_title}: {video_status_dict[video_title]}\n"
    msg_body += f"\nYou can find these videos in your Saved Videos section at:\n\n" \
                f"{url_for('user.saved_videos', _external=True)}\n"
    send_email("Your videos have been saved to your account.", msg_body,
               current_user.email)

    return video_status_dict
