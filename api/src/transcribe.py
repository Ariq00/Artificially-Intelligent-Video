from pytube import YouTube
from moviepy.editor import VideoFileClip

from environment import stt_api_key, stt_url
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

import os
import json


def download_video(video_url, user_id):
    """TODO:
        userID is obtained from cookies (needed in case multiple people use service at once)
        need to add error checking for invalid URL"""

    save_path = '../video'
    YouTube(video_url).streams.filter(file_extension='mp4',
                                      progressive=True).first().download(
        output_path=save_path, filename="video.mp4",
        filename_prefix="{uuid}_".format(uuid=user_id))


def setup_stt():
    authenticator = IAMAuthenticator(stt_api_key)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(stt_url)
    return stt


def process_audio(video_filepath, user_id):
    chunk_number = 0
    chunk_duration = 5
    full_audio_clip = VideoFileClip(video_filepath).audio
    total_duration = int(full_audio_clip.duration)
    current_duration = 0
    stt = setup_stt()
    transcript_dict = {}
    transcript_path = "../transcripts/{uuid}_transcript.json".format(
        uuid=user_id)

    for i in range(
            total_duration // chunk_duration + 1):  # loop for number of full clips (+1 for final shorter clip)

        chunk_file_path = "../audio/{uuid}_{chunk_number}.mp3".format(
            uuid=user_id, chunk_number=chunk_number)
        if i == (
                total_duration // chunk_duration):  # checking for last iteration
            clip = full_audio_clip.subclip(current_duration)

        else:
            # create subclip starting from the current duration
            clip = full_audio_clip.subclip(current_duration,
                                           current_duration + chunk_duration + 0.5)  # 0.5 second overlap between each chunk
        # save the subclip
        clip.write_audiofile(chunk_file_path)

        # transcribe the audio using stt
        chunk_text = transcribe_audio(stt, user_id, chunk_number)
        transcript_dict[chunk_number] = chunk_text

        # update the current duration and chunk number
        current_duration += chunk_duration
        chunk_number += 1

        # Delete the chunk file to save storage space
        os.remove(chunk_file_path)

    with open(transcript_path, "w") as outfile:
        json.dump(transcript_dict, outfile, indent=1)

    return transcript_dict


def transcribe_audio(stt, user_id, chunk_number):
    with open('../audio/{uuid}_{chunk_number}.mp3'.format(uuid=user_id,
                                                          chunk_number=chunk_number),
              'rb') as f:
        response = stt.recognize(audio=f, content_type='audio/mp3',
                                 model='en-GB_BroadbandModel').get_result()
        chunk_text = ""

        for section in response["results"]:
            chunk_text += section["alternatives"][0]["transcript"]

    return chunk_text
