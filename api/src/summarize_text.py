from watson_nlu import get_full_transcript
from environment import meaningcloud_license_key
import requests
import json


def summarize_text(user_id):
    parameters = {
        "key": meaningcloud_license_key,
        "txt": get_full_transcript(user_id),
        "sentences": 1
    }
    res = requests.post("https://api.meaningcloud.com/summarization-1.0",
                        data=parameters)
    summary = json.loads(res.text)["summary"]
    return summary


print(summarize_text(1))
