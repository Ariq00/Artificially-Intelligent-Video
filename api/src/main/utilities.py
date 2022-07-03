from flask_login import current_user
from models import Video
from pytube.exceptions import PytubeError
from werkzeug.utils import secure_filename
from transcribe import download_video
from datetime import datetime


def check_if_video_saved(document_id):
    if current_user and Video.objects(user=current_user,
                                      document_id=document_id):
        video_is_saved = True
    else:
        video_is_saved = False

    return video_is_saved


def process_upload(request, user_id):
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    if request.form["video"] == "file":
        media_file = request.files["file"]

        # check if file has been uploaded
        if media_file.filename == "":
            return {"status": "failed",
                    "message": "Please upload an MP3 or MP4 file first!"}

        else:
            media_title = secure_filename(media_file.filename)
            file_ext = media_title[
                       -4:]  # check file extension of uploaded file

            # check file extension
            if file_ext not in [".mp3", ".mp4"]:
                return {"status": "failed",
                        "message": "Please upload an MP3 or MP4 file!"}

        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        static_media_filepath = f"./static/video/{user_id}_{current_time}{file_ext}"
        media_file.save(static_media_filepath)

    else:  # If video file was uploaded instead
        youtube_url = request.form["youtubeUrl"]

        # check if no url is provided
        if len(youtube_url) == 0:
            return {"status": "failed",
                    "message": "Please enter a YouTube link first!"}

        # catch all other exceptions
        try:
            media_title, static_media_filepath = download_video(youtube_url,
                                                                f"{user_id}_{current_time}.mp4")
        except PytubeError as e:
            return {"status": "failed", "message": str(e)}

    return {"status": "success", "media_title": media_title,
            "static_media_filepath": static_media_filepath}
