from ibm_watson import DiscoveryV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from environment import discovery_api_key, discovery_url, \
    discovery_environment_id, discovery_collection_id
from transcribe import chunk_duration


def setup_discovery():
    authenticator = IAMAuthenticator(discovery_api_key)
    discovery = DiscoveryV1(
        version='2018-12-03',
        authenticator=authenticator
    )
    discovery.set_service_url(discovery_url)
    return discovery


def check_if_transcript_exists(discovery, filename):
    response = discovery.query(
        environment_id=discovery_environment_id,
        collection_id=discovery_collection_id
    ).get_result()
    for files in response["results"]:
        if files["extracted_metadata"]["filename"] == filename:
            return files["id"]
    return False


def upload_transcript(discovery, transcript_filename):
    transcript_path = "../transcripts/" + transcript_filename
    if check_if_transcript_exists(discovery, transcript_filename):
        delete_transcript(discovery, check_if_transcript_exists(discovery,
                                                                transcript_filename))
    with open(transcript_path) as fileinfo:
        add_doc = discovery.add_document(
            environment_id=discovery_environment_id,
            collection_id=discovery_collection_id,
            file=fileinfo,
            file_content_type="application/json"
        ).get_result()
        return add_doc["document_id"]


def query_transcript(discovery, document_id, user_query):
    result = discovery.query(
        environment_id=discovery_environment_id,
        collection_id=discovery_collection_id,
        # only returns results for specific document
        filter=f"id::{document_id}".format(document_id=document_id),
        natural_language_query=user_query,
        highlight=True,
        passages=True,
        passages_count=3  # number of passages to return
    ).get_result()

    # returns a dictionary where the key is passage text and the value is a dictionary of the score and timestamp
    return {matching_passage["passage_text"]: {
        "passage_score": matching_passage["passage_score"],
        "timestamp": int(matching_passage["field"]) * chunk_duration} for
        matching_passage in result["passages"]}


def delete_transcript(discovery, document_id):
    discovery.delete_document(
        environment_id=discovery_environment_id,
        collection_id=discovery_collection_id,
        document_id=document_id
    )
