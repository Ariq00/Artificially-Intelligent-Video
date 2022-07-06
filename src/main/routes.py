from flask import session, render_template, request, jsonify, Blueprint, flash, \
    redirect, url_for
import uuid
from transcribe import process_audio
import watson_discovery
from watson_assistant import watson_assistant_query
from main.utilities import process_upload, \
    summarise_and_analyse
from ibm_cloud_sdk_core.api_exception import ApiException
from main.utilities import send_email

main_bp = Blueprint('main', __name__)


@main_bp.route("/", methods=["POST", "GET"])
def home():
    # generate uuid for session
    if not session.get("user_id"):
        session["user_id"] = str(uuid.uuid4())
    user_id = session.get("user_id")

    if request.method == "POST":
        # upload file
        if request.form["video"] == "file":
            request_array = [request.form["video"], request.files["file"]]
        else:
            request_array = [request.form["video"], request.form["youtubeUrl"]]

        upload_result = process_upload(request_array, user_id)
        if upload_result["status"] == "failed":
            flash(upload_result["message"], "danger")
            return redirect(url_for("main.home"))
        else:
            media_title, static_media_filepath = upload_result["media_title"], \
                                                 upload_result[
                                                     "static_media_filepath"]
        # transcribe audio
        process_audio(static_media_filepath, user_id,
                      request.form['languageSubmit'])

        # upload to discovery
        discovery = watson_discovery.setup_discovery()
        transcript_filename = f"{user_id}.json"
        document_id = watson_discovery.upload_transcript(discovery,
                                                         transcript_filename)

        try:
            summary, score, sentiment, concepts = summarise_and_analyse(
                transcript_filename)

            return render_template("video.html",
                                   filepath=static_media_filepath.replace(
                                       "./static", ""),
                                   document_id=document_id,
                                   title=media_title,
                                   summary=summary,
                                   sentiment=sentiment,
                                   score=score,
                                   concepts=concepts,
                                   video_is_saved=False)

        except ApiException:
            flash("Could not analyse video. Video has no audio content!",
                  "danger")
            return redirect(url_for("main.home"))

    return render_template("index.html")


@main_bp.route("/watson_response", methods=["POST"])
def watson_response():
    text = request.get_json().get("message")
    document_id = request.get_json().get("document_id")
    return jsonify(watson_assistant_query(text, document_id))


# THIS ROUTE IS FOR TESTING
@main_bp.route('/video_test', methods=['GET'])
def video_testing_page():
    document_id = "66097691-d0f9-41db-b030-24fac3b0d813"
    # concepts = analyse_text("bitcoin.json")["concepts"]
    # summary = summarize_text("bitcoin.json")

    print(send_email())

    return render_template("video.html",
                           filepath="/video/Bitcoin Video.mp4",
                           document_id=document_id,
                           title="Bitcoin Video.mp4",
                           summary="This is a summary",
                           sentiment="negative".title(),
                           score=20,
                           concepts=["nakamoto", "bitcoin"],
                           video_is_saved=True)
