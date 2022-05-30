from ibm_watson import AssistantV2
from ibm_watson.assistant_v2 import MessageInputStateless
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from environment import assistant_api_key, assistant_url, assistant_id
import json


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
    response = assistant.message_stateless(
        assistant_id=assistant_id,
        # can also just use a dict instead like the docs
        input=MessageInputStateless(text=text)
    ).get_result()

    print(json.dumps(response, indent=2))

    return response


send_stateless_message("Tell me about football")
