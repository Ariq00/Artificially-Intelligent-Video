from flask import session, render_template, request, jsonify, flash, \
    redirect, url_for, Blueprint
import uuid
from transcribe import download_video, process_audio
import watson_discovery
from werkzeug.utils import secure_filename
from watson_assistant import watson_assistant_query
from pytube.exceptions import PytubeError
from summarize_text import summarize_text
from watson_nlu import analyse_text
from main.utilities import check_if_video_saved

main_bp = Blueprint('main', __name__)


@main_bp.route("/", methods=["POST", "GET"])
def home():
    # generate uuid for session
    if not session.get("user_id"):
        session["user_id"] = str(uuid.uuid4())
    user_id = session.get("user_id")

    if request.method == "POST":
        file_ext = ".mp4"  # set default file extension

        if request.form["video"] == "youtube":
            youtube_url = request.form["youtubeUrl"]

            # check if no url is provided
            if len(youtube_url) == 0:
                flash("Please enter a YouTube link first!", "danger")
                return redirect(url_for("main.home"))

            # catch all other exceptions
            try:
                media_title = download_video(youtube_url, user_id)
            except PytubeError as e:
                flash(str(e), "danger")
                return redirect(url_for("main.home"))

        else:  # If video file was uploaded instead
            media_file = request.files["file"]

            # check if file has been uploaded
            if media_file.filename == "":
                flash("Please upload an MP3 or MP4 file first!", "danger")
                return redirect(url_for("main.home"))

            else:
                media_title = secure_filename(media_file.filename)
                file_ext = media_title[
                           -4:]  # check file extension of uploaded file

                # check file extension
                if file_ext not in [".mp3", ".mp4"]:
                    flash("Please upload a valid MP3 or MP4 file!", "danger")
                    return redirect(url_for("main.home"))

            media_file.save("./static/video/" + user_id + file_ext)

        # transcribe audio
        media_filepath = "/video/" + user_id + file_ext
        static_media_filepath = "./static" + media_filepath
        process_audio(static_media_filepath, user_id,
                      request.form['languageSubmit'])

        # upload to discovery
        transcript_filename = f"{user_id}.json"
        discovery = watson_discovery.setup_discovery()
        document_id = watson_discovery.upload_transcript(discovery,
                                                         transcript_filename)
        # retrieve text summary
        summary = summarize_text(transcript_filename)

        # sentiment analysis
        analysis_results = analyse_text(transcript_filename)
        score = int(abs(analysis_results["sentiment"]["score"] * 100))
        sentiment = analysis_results["sentiment"]["label"].title()

        # key concepts
        concepts = analysis_results["concepts"]

        video_is_saved = check_if_video_saved(document_id)

        return render_template("video.html",
                               video_filepath=media_filepath,
                               document_id=document_id,
                               video_title=media_title,
                               summary=summary,
                               sentiment=sentiment,
                               score=score,
                               concepts=concepts,
                               video_is_saved=video_is_saved)

    return render_template("index.html")


@main_bp.route("/watson_response", methods=["POST"])
def watson_response():
    text = request.get_json().get("message")
    document_id = request.get_json().get("document_id")
    watson_results = watson_assistant_query(text, document_id)
    timestamps = []
    for result in watson_results["top_results"]:
        timestamps.append(result["timestamp"])

    message = watson_results["text_response"]

    if len(timestamps) != 0 and not watson_results["extracted query"]:
        message = "I queried the video with your exact input."
    return jsonify({"timestamps": timestamps, "message": message})


# THIS ROUTE IS FOR TESTING
@main_bp.route('/video_test', methods=['GET'])
def video_testing_page():
    document_id = "66097691-d0f9-41db-b030-24fac3b0d813"
    video_is_saved = check_if_video_saved(document_id)
    # concepts = analyse_text("bitcoin.json")["concepts"]
    # summary = summarize_text("bitcoin.json")

    return render_template("video.html",
                           video_filepath="/video/Bitcoin Video.mp4",
                           document_id=document_id,
                           video_title="Bitcoin Video.mp4",
                           summary="This is a summary",
                           sentiment="negative".title(),
                           score=20,
                           concepts=["nakamoto", "bitcoin"],
                           video_is_saved=video_is_saved)
