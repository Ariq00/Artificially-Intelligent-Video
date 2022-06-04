from ibm_watson import AssistantV2
from ibm_watson.assistant_v2 import MessageInputStateless
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from environment import assistant_api_key, assistant_url, assistant_id
import json
import re

from watson_discovery import query_transcript


def setup_assistant():
    authenticator = IAMAuthenticator(assistant_api_key)
    assistant = AssistantV2(
        version='2021-11-27',
        authenticator=authenticator
    )
    assistant.set_service_url(assistant_url)
    return assistant


def send_stateless_message(text):
    assistant = setup_assistant()

    # send message to watson assistant
    response = assistant.message_stateless(
        assistant_id=assistant_id,
        # can also just use a dict instead like the docs
        input=MessageInputStateless(text=text)
    ).get_result()
    print(response)
    # extract query information from Watson assistant
    if process_quote(response):
        user_query = process_quote(response)
    elif process_concept(response):
        user_query = process_concept(response)
    else:
        user_query = text

    return user_query


def process_quote(response):
    if response["output"]["intents"][0]["intent"] == "GetQuote":
        quote = response["context"]["skills"]["main skill"]["user_defined"][
            "quote"]
        return clean_string(quote)
    else:
        return False


def process_concept(response):
    if response["output"]["intents"][0]["intent"] == "GetConcept":
        concept = response["output"]["entities"][0]["value"]
        return clean_string(concept)
    else:
        return False


def clean_string(string):
    return re.sub('\W+', ' ', string)


print(send_stateless_message('what is the future of self-driving cars'))
