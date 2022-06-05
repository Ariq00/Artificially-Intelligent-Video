from flask import Flask, session, render_template, request
import uuid
from transcribe import download_video, process_audio
import watson_discovery

app = Flask(__name__)
app.secret_key = "such_a_secret"


@app.route("/", methods=["POST", "GET"])
def home():
    # generate uuid for session
    if not session.get("user_id"):
        session["user_id"] = str(uuid.uuid4())
    user_id = session.get("uuid")

    if request.method == "POST":
        if request.form["video"] == "youtube":
            youtube_url = request.form["youtubeUrl"]
            video_title = download_video(youtube_url, user_id)

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


if __name__ == "__main__":
    app.run(debug=True)
