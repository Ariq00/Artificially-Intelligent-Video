from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, \
    SentimentOptions, ConceptsOptions
from environment import nlu_api_key, nlu_url
from watson_assistant import watson_assistant_query

import json


def get_full_transcript(transcript_filename):
    transcript_path = f"./transcripts/{transcript_filename}"
    with open(transcript_path) as f:
        transcript_dict = json.load(f)

    full_transcript = ""
    chunk = 0
    while transcript_dict.get(str(chunk)):
        full_transcript += transcript_dict[str(chunk)] + ". "
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


def get_concept_timestamps(document_id, results):
    concept_timestamps = []
    # run query for each concept and get timestamp
    for concept in results["concepts"]:
        query_results = watson_assistant_query(concept["text"], document_id)
        # only keep concepts for which a timestamp is found
        if len(query_results["top_results"]) > 0 and concept[
            "relevance"] > 0.8:
            concept_timestamps.append({"concept": concept["text"],
                                       "timestamp": query_results[
                                           "top_results"][0]["timestamp"]})

    return sorted(concept_timestamps, key=lambda d: d['timestamp'])
