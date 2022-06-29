from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, \
    SentimentOptions, ConceptsOptions
from environment import nlu_api_key, nlu_url
from watson_assistant import clean_string

import json


def get_full_transcript(transcript_filename):
    transcript_path = f"./transcripts/{transcript_filename}"
    # transcript_path = "../transcripts/old/5-second_overlap_transcript.json"
    with open(transcript_path) as f:
        transcript_dict = json.load(f)

    full_transcript = ""
    chunk = 0
    while transcript_dict.get(str(chunk)):
        full_transcript += transcript_dict[str(chunk)] + " "
        chunk += 1

    return full_transcript


def setup_nlu():
    authenticator = IAMAuthenticator(nlu_api_key)
    nlu = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator)
    nlu.set_service_url(nlu_url)
    return nlu


def analyse_text(transcript_filename):
    # get the concepts and sentiment of the video
    nlu = setup_nlu()
    text = get_full_transcript(transcript_filename)

    response = nlu.analyze(
        text=text,
        features=Features(
            sentiment=SentimentOptions(),
            concepts=ConceptsOptions(),
        ),
        language='en'
    ).get_result()

    results = {"sentiment": response["sentiment"]["document"],
               "concepts": response["concepts"]}
    return results

# print(analyse_text("1.json"))
