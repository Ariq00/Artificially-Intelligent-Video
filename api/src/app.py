from flask import Flask, session, render_template, request, jsonify
import uuid
from transcribe import download_video, process_audio
import watson_discovery
from werkzeug.utils import secure_filename
from environment import secret_key
from watson_assistant import watson_assistant_query

app = Flask(__name__)
app.secret_key = secret_key
app.config["UPLOAD_FOLDER"] = "./static/video/"


@app.route("/", methods=["POST", "GET"])
def home():
    # generate uuid for session
    if not session.get("user_id"):
        session["user_id"] = str(uuid.uuid4())
    user_id = session.get("user_id")
    if request.method == "POST":
        if request.form["video"] == "youtube":
            youtube_url = request.form["youtubeUrl"]
            video_title = download_video(youtube_url, user_id)

        else:
            video_file = request.files["file"]
            # TODO: Do some error checking on valid file format
            #        also allow mp3 files
            #        limit max file size
            if video_file.filename != "":
                video_title = secure_filename(video_file.filename)
                video_file.save(app.config["UPLOAD_FOLDER"] + user_id + ".mp4")

        # transcribe audio
        video_filepath = "/video/" + user_id + ".mp4"
        static_video_filepath = "./static" + video_filepath
        process_audio(static_video_filepath, user_id)

        # upload to discovery
        transcript_filename = f"{user_id}.json"
        discovery = watson_discovery.setup_discovery()
        session["document_id"] = watson_discovery.upload_transcript(discovery,
                                                                    transcript_filename)

        return render_template("video.html",
                               video_filepath=video_filepath,
                               video_title=video_title)

    return render_template("index.html")


@app.route('/video', methods=['GET'])
def video_page():
    return render_template("video.html")


@app.route("/watson_response", methods=["POST"])
def watson_response():
    text = request.get_json().get("message")
    watson_results = watson_assistant_query(text, session["document_id"])

    timestamps = []
    for result in watson_results["top_results"]:
        timestamps.append(result["timestamp"])

    message = watson_results["text_response"]

    if len(timestamps) != 0 and not watson_results["extracted query"]:
        message = "I queried the video with your exact input."

    return jsonify({"timestamps": timestamps, "message": message})


# THIS ROUTE IS FOR TESTING
@app.route('/video_test', methods=['GET'])
def video_testing_page():
    session["document_id"] = "66097691-d0f9-41db-b030-24fac3b0d813"
    return render_template("video.html",
                           video_filepath="/video/Bitcoin Video.mp4",
                           video_title="Bitcoin Video.mp4")


if __name__ == "__main__":
    app.run(debug=True)
