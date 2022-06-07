from ibm_watson import AssistantV2
from ibm_watson.assistant_v2 import MessageInputStateless
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from environment import assistant_api_key, assistant_url, assistant_id
import re

from watson_discovery import query_transcript, setup_discovery


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
        input=MessageInputStateless(text=text)
    ).get_result()
    watson_text_response = response["output"]["generic"][0]["text"]

    # extract query information from Watson assistant
    if process_quote(response):
        extracted_query = process_quote(response)
    elif process_concept(response):
        extracted_query = process_concept(response)
    else:
        extracted_query = False

    return {"extracted query": extracted_query,
            "user input": clean_string(text),
            "text response": watson_text_response}


def process_quote(response):
    # Check if the quote variable exists
    if "user_defined" in response["context"]["skills"]["main skill"]:
        quote = response["context"]["skills"]["main skill"]["user_defined"][
            "quote"]
        return clean_string(quote)
    else:
        return False


def process_concept(response):
    if len(response["output"]["intents"]) != 0:
        if response["output"]["intents"][0]["intent"] == "GetConcept":
            concept = response["output"]["entities"][0]["value"]
            return clean_string(concept)
    else:
        return False


def clean_string(string):
    return re.sub('\W+', ' ', string)


def watson_assistant_query(text, document_id):
    discovery = setup_discovery()

    # send query to watson assistant and receive response
    query_dict = send_stateless_message(text)

    # send watson assistant response as query to watson discovery
    results = {}
    if query_dict["extracted query"]:  # check watson extracted a query
        results = query_transcript(discovery, document_id,
                                   query_dict["extracted query"])

    # send user input as query to watson discovery
    user_input_results = query_transcript(discovery, document_id,
                                          query_dict["user input"])
    # combine both dictionaries
    results.update(user_input_results)

    # order the results by passage score
    ordered_results = []
    for result in sorted(results, key=lambda x: (results[x]['passage_score']),
                         reverse=True):
        ordered_results.append({'timestamp': results[result]['timestamp']})

    watson_results = {"top_results": ordered_results[0:2],
                      "text_response": query_dict[
                          "text response"], "extracted query": query_dict[
            "extracted query"]}  # return top 2 results

    return watson_results

# document_id = "b483a604-3736-4406-b88c-d3add2016b07" # ai video
# print(
#     watson_assistant_query('miners',
#                            document_id))

# print(send_stateless_message("hello"))
