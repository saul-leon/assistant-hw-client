# -*- coding: utf-8-*-
from src.speech.snowboy_decoder import HotwordDetector
from src.speech.spinx_decoder import speech_to_text_offline
from src.services.speech_services import text_to_speech, speech_to_text, download_response
from src.audio.player import PlayerFactory
from src.utils.text_utils import TextUtils
from pynput.keyboard import Key, Listener
from threading import Timer
import logging
import glob
import os

if __name__ == '__main__':
    # on hotword detected, play beep_hi sound
    def on_hotword_detected():
        logger.info('Hotword detected, switching to active listening')
        player.play('resources/beep_hi.wav')        
        print(TextUtils.START_RECORDING_AUDIO)
    
    # on keypress detected, start recording if SPACE, stop listening keypress if ESC
    def on_keypress_detected(key):
        logger.info('{0} pressed.'.format(key))
        if key == Key.esc:
            print(TextUtils.STOP_LISTEN_KEYPRESS)
            return False
        elif key == Key.space:
            print(TextUtils.START_RECORDING_AUDIO)
            detector.can_start_recording = True
            return True

    # on active listening finished, play beep_lo sound, stop recording by keypress
    def on_listening_finished():
        logger.info('Active listening finished')
        detector.can_start_recording = False #restart listening keypress        
        player.play('resources/beep_lo.wav')        
        print(TextUtils.STOP_RECORDING_AUDIO)

    # on response generated, play response audio file
    def on_response_generated(assistant_response_ogg_file):        
        logger.info('Playing speech respond')
        print(TextUtils.START_ASSISTANT_ANSWER)
        player.play(assistant_response_ogg_file)

    # clear cache
    def clear_cache():
        # Clear cache directory
        for file in glob.glob('tmp/*'):
            os.remove(file)
        
    # generate new user session
    def generate_new_session():
        global user_id        
        user_id += 1 # increase user_id
        logger.info('New Session Generated')

    # process user request by using recorded speech file
    def process_user_request_speech(user_request_wav_file):
        global user_id        
        
        on_listening_finished()
        
        logger.info('Calling speech_to_text API')
        print(TextUtils.SEND_ASSISTANT_QUERY)
        user_response_file = speech_to_text( user_id, user_request_wav_file )        
        print(TextUtils.RECEIVE_ASSISTANT_RESPONSE)
        logger.info('Response file' + user_response_file)

        logger.info('Generating speech from assistant text')
        print(TextUtils.DOWNLOAD_ASSISTANT_RESPONSE)
        assistant_response_ogg_file = download_response( user_response_file )

        on_response_generated(assistant_response_ogg_file)        

        print(TextUtils.LISTEN_HOTWORD_KEYPRESS)
    
    # process user request by using recorded speech file by converting it offline
    def process_user_request_text(user_request_wav_file):
        global user_id

        on_listening_finished()

        logger.info('Getting text from user speech offline')        
        print(TextUtils.START_SPEECH_RECOGNITION)
        audio_as_text = speech_to_text_offline( user_request_wav_file )
        print(TextUtils.STOP_SPEECH_RECOGNITION.format(audio_as_text))
        logger.info('Speech recognized ' + audio_as_text)

        logger.info('Calling text_to_speech api')
        print(TextUtils.SEND_ASSISTANT_QUERY)
        user_response_file = text_to_speech( user_id, audio_as_text )
        print(TextUtils.RECEIVE_ASSISTANT_RESPONSE)
        logger.info('Response file' + user_response_file)

        logger.info('Generating speech from assistant text')
        print(TextUtils.DOWNLOAD_ASSISTANT_RESPONSE)
        assistant_response_ogg_file = download_response( user_response_file )

        on_response_generated(assistant_response_ogg_file)    

        print(TextUtils.LISTEN_HOTWORD_KEYPRESS)

    clear_cache()
        
    logging.basicConfig(filename='tmp/assistant.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    logger = logging.getLogger( 'main' )
    logger.setLevel(logging.INFO)
    
    detector = HotwordDetector('resources/computer.umdl', resource='resources/snowboy-common.res', sensitivity=0.5)
    player = PlayerFactory()
    user_id = 1
    
    session_timer = Timer(1800.0, generate_new_session)
    session_timer.start()

    logger.info('App started') 
    logger.info('Cache cleared')    
    logger.info('Main loop started, listening for keypress: SPACE')
    print(TextUtils.APP_STARTED)
    print(TextUtils.APP_QUIT)
    print(TextUtils.LISTEN_KEYPRESS_START)
    print(TextUtils.LISTEN_KEYPRESS_STOP)
    listener = Listener(
        on_release=on_keypress_detected)
    listener.start()

    logger.info('Main loop started, listening for hotword: COMPUTER')
    print(TextUtils.LISTEN_HOTWORD_START)
    detector.start(
        detected_callback=on_hotword_detected,
        audio_recorder_callback=process_user_request_speech
        #audio_recorder_callback=process_user_request_text
    )