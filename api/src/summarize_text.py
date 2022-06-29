from watson_nlu import get_full_transcript
from environment import meaningcloud_license_key
import requests
import json


# def summarize_text(transcript_filename):
#     parameters = {
#         "key": meaningcloud_license_key,
#         "txt": get_full_transcript(transcript_filename),
#         "sentences": 1
#     }
#     res = requests.post("https://api.meaningcloud.com/summarization-1.0",
#                         data=parameters)
#     summary = json.loads(res.text)["summary"]
#     return summary

# need to pip install torch and transformers for this method
def summarize_text(transcript_filename):
    from transformers import pipeline
    summarization = pipeline("summarization", "sshleifer/distilbart-cnn-12-6")
    summarized_text = summarization(
        get_full_transcript(transcript_filename))
    return summarized_text[0]['summary_text']
