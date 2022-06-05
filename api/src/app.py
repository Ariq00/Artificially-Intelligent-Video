from flask import Flask, session, render_template
import uuid

app = Flask(__name__)
app.secret_key = "such_a_secret"


@app.route("/", methods=["POST", "GET"])
def home():
    session["uuid"] = str(uuid.uuid4())
    print(session)
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
