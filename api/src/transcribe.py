from pytube import YouTube
from environment import stt_api_key, stt_url
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pydub import AudioSegment
from pydub.utils import make_chunks
import os
import json

chunk_duration = 5
overlap = 0.5  # 0.5 second overlap between each chunk


def download_video(video_url, filename):
    save_path = './static/video'
    YouTube(video_url).streams.filter(file_extension='mp4',
                                      progressive=True).first().download(
        output_path=save_path,
        filename=filename)
    return YouTube(video_url).title, f"{save_path}/{filename}"


def setup_stt():
    authenticator = IAMAuthenticator(stt_api_key)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(stt_url)
    return stt


def process_audio(video_filepath, user_id, country='us'):
    full_audio_clip = AudioSegment.from_file(video_filepath)
    stt = setup_stt()
    transcript_dict = {}
    transcript_path = "./transcripts/{uuid}.json".format(
        uuid=user_id)
    id_chunk_dict = {}

    language_model_dict = {'us': 'en-US_BroadbandModel',
                           'uk': 'en-GB_BroadbandModel'}

    chunks = make_chunks(full_audio_clip, chunk_duration * 1000)

    for chunk_number, chunk in enumerate(chunks):
        print("exporting chunk ", chunk_number)
        chunk_file_path = "./audio/{uuid}_{chunk_number}.mp3".format(
            uuid=user_id, chunk_number=chunk_number)
        chunk.export(chunk_file_path)

        # create a job in stt
        with open(chunk_file_path, 'rb') as f:
            job_id = stt.create_job(audio=f, content_type='audio/mp3',
                                    model=language_model_dict[country]
                                    ).get_result()["id"]
        # map id to a chunk number
        id_chunk_dict[job_id] = chunk_number

        # Delete the chunk file to save storage space
        os.remove(chunk_file_path)

        # make sure number of outstanding jobs is always less than 100
        if chunk_number % 100 == 0:
            transcript_dict = check_jobs(stt, transcript_dict, id_chunk_dict)

    # make sure all jobs are completed
    while len(stt.check_jobs().get_result()["recognitions"]) != 0:
        transcript_dict = check_jobs(stt, transcript_dict, id_chunk_dict)

    with open(transcript_path, "w") as outfile:
        json.dump(transcript_dict, outfile, indent=1)

    return transcript_dict


def check_jobs(stt, transcript_dict, id_chunk_dict):
    response = stt.check_jobs().get_result()

    for job in response["recognitions"]:
        # checking id is in dict means it won't interfere with jobs from other users
        if job["status"] == "completed" and job["id"] in id_chunk_dict:
            id = job["id"]
            job_result = stt.check_job(id).get_result()

            # retrieve text
            chunk_text = ""
            for section in job_result["results"]:
                if len(section["results"]) > 0:
                    chunk_text += section["results"][0]["alternatives"][0][
                        "transcript"]

            # update transcript dict
            chunk_number = id_chunk_dict[id]
            transcript_dict[chunk_number] = chunk_text

            # delete the job
            stt.delete_job(id)

    return transcript_dict


def delete_all_jobs():
    stt = setup_stt()
    response = stt.check_jobs().get_result()
    for job in response["recognitions"]:
        stt.delete_job(job["id"])
