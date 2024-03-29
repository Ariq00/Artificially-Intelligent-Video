from watson_nlu import get_full_transcript
from environment import meaningcloud_license_key
import requests
import json


def summarize_text(transcript_filename):
    parameters = {
        "key": meaningcloud_license_key,
        "txt": get_full_transcript(transcript_filename),
        "limit": 20
    }
    res = requests.post("https://api.meaningcloud.com/summarization-1.0",
                        data=parameters)
    try:
        summary = json.loads(res.text)["summary"]
    except KeyError:
        summary = "Could not generate summary for video."

    return summary
