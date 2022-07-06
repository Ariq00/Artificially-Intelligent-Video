from flask_login import current_user
from models import Video
from pytube.exceptions import PytubeError
from werkzeug.utils import secure_filename
from summarize_text import summarize_text
from transcribe import download_video
from datetime import datetime
from watson_nlu import analyse_text
import os
from flask_mail import Message
from setup_app import mail


def process_upload(request_array, user_id):
    # request array is ["file"/"video", video file or youtube url]
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    if request_array[0] == "file":
        media_file = request_array[1]

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
        youtube_url = request_array[1]

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


def summarise_and_analyse(transcript_filename):
    summary = summarize_text(transcript_filename)
    analysis_results = analyse_text(transcript_filename)
    score = int(abs(analysis_results["sentiment"]["score"] * 100))
    sentiment = analysis_results["sentiment"]["label"].title()

    # key concepts
    concepts = analysis_results["concepts"]
    # delete transcript
    os.remove(f"./transcripts/{transcript_filename}")

    return summary, score, sentiment, concepts


def send_email(subject, msg_content):
    msg = Message(subject,
                  sender='smart.video.project@gmail.com',
                  recipients=[current_user.email])
    msg.body = msg_content
    mail.send(msg)
    print("Email sent", msg.body)
