from pytube import YouTube
from moviepy.editor import VideoFileClip

from environment import stt_api_key, stt_url
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

import json


def download_video(video_url, user_id):
    """TODO:
        userID is obtained from cookies (needed in case multiple people use service at once)
        need to add error checking for invalid URL"""

    save_path = '../videos'
    YouTube(video_url).streams.filter(file_extension='mp4',
                                      progressive=True).first().download(
        output_path=save_path, filename="video.mp4",
        filename_prefix="{uuid}_".format(uuid=user_id))


def extract_audio(video_filepath, user_id):
    audio_clip = VideoFileClip(video_filepath)
    audio_clip.audio.write_audiofile(
        "../videos/{uuid}_audio.mp3".format(uuid=user_id))


def setup_stt():
    authenticator = IAMAuthenticator(stt_api_key)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(stt_url)
    return stt


def transcribe_audio(user_id):
    """TODO:
        make sure audio file is less than 100mb"""
    stt = setup_stt()
    with open('../videos/{uuid}_audio.mp3'.format(uuid=user_id), 'rb') as f:
        response = stt.recognize(audio=f, content_type='audio/mp3',
                                 model='en-GB_BroadbandModel',
                                 timestamps=True).get_result()
    return response


def process_response():
    data = json.load(open("transcript.json"))

    text = [result['alternatives'][0]['transcript'].rstrip() + '.\n' for result
            in data['results']]
    text = [para[0].title() + para[1:] for para in text]
    transcript = ''.join(text)
    print(transcript)


process_response()
