from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, \
    SummarizationOptions, SentimentOptions, KeywordsOptions, EntitiesOptions, \
    ConceptsOptions, EmotionOptions, CategoriesOptions
from environment import nlu_api_key, nlu_url
from watson_assistant import clean_string

import json


def get_full_transcript(user_id):
    transcript_path = f"../transcripts/{user_id}.json"
    # transcript_path = "../transcripts/old/5-second_overlap_transcript.json"
    with open(transcript_path) as f:
        transcript_dict = json.load(f)

    full_transcript = ""
    chunk = 0
    while transcript_dict.get(str(chunk)):
        full_transcript += transcript_dict[str(chunk)]
        chunk += 1

    return clean_string(full_transcript)


def setup_nlu():
    authenticator = IAMAuthenticator(nlu_api_key)
    nlu = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator)
    nlu.set_service_url(nlu_url)
    return nlu


# TODO: need to decide how exactly I want to deal with each feature
def summarize_text(user_id):
    # summarize text isnt working with watson
    nlu = setup_nlu()
    text = get_full_transcript(user_id)

    response = nlu.analyze(
        text=text,
        features=Features(
            sentiment=SentimentOptions(),
            # keywords=KeywordsOptions(emotion=True, sentiment=True),
            concepts=ConceptsOptions(),
            emotion=EmotionOptions(),
            # entities=EntitiesOptions()
            categories=CategoriesOptions(explanation=True)
        ),
        language='en'
    ).get_result()
    print(json.dumps(response, indent=2))
    return response


summarize_text(1)
