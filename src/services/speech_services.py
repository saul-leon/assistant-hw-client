# -*- coding: utf-8-*-
from src.utils.audio_utils import convert_to_wav, convert_to_ogg, read_ogg_data_base64
import requests
import time

API_ENDPOINT = "https://ek.app-on.cloud/api/voice/robot"
AUDIO_TYPE = "audio"
TEXT_TYPE = "text"

# sends text data which was being converted from the recorded audio file offline to the robot API
def text_to_speech(user_id, audio_text):
    headers = {'Content-Type': 'application/json'}
    data = {'from': 'id_from_' + str(user_id),
        'type': TEXT_TYPE,
        'text': {'body': audio_text}}
    response = requests.post(url = API_ENDPOINT, json=data, headers=headers)
    json_data = response.json()
    # put some error handling
    # there is no audio generated on this api, need to discuss with Juan Diego
    if "data" in json_data and "voice" in json_data['data'] and json_data['data']['voice'] != None:
        return json_data['data']['voice']    
    return ""

# sends recorded audio file from wav to ogg and send it to the robot API
def speech_to_text(user_id, wav_file):    
    ogg_file = convert_to_ogg(wav_file) # discuss with Juan Diego to send directly wav
    base64_encoded_audio = read_ogg_data_base64(ogg_file)
    headers = {'Content-Type': 'application/json'}
    data = {'from': 'id_from_' + str(user_id),
        'type': AUDIO_TYPE,
        'audio': {'base64': base64_encoded_audio}}
    response = requests.post(url = API_ENDPOINT, json=data, headers=headers)
    json_data = response.json()
    # put some error handling
    if "data" in json_data and "voice" in json_data['data'] and json_data['data']['voice'] != None:
        return json_data['data']['voice']    
    return ""

# download the audio file that comes with the response
def download_response(response_file):
    if (response_file != ""):
        ogg_file = 'tmp/user-response-%s.ogg' % str(int(time.time()))
        ogg_file_online = requests.get(response_file)
        with open(ogg_file, 'wb') as f:
            f.write(ogg_file_online.content)
        return ogg_file
    return 'resources/error.wav' # return some voice that says please try again
