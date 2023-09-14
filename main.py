# -*- coding: utf-8-*-

from src.sound_io import Speaker
from src.snowboy_decoder import HotwordDetector
from src.speech_services import text_to_speech, speech_to_text

import logging
import glob
import os

if __name__ == '__main__':

    # Clear cache directory
    for file in glob.glob('tmp/*'):
        os.remove(file)

    print('\n\nBooting assistant-hw-client ... (Ignore Alsa messages)\n\n')

    logging.basicConfig(filename='tmp/assistant.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

    logger = logging.getLogger( 'main' )
    logger.setLevel(logging.INFO)

    speaker = Speaker()
    detector = HotwordDetector('resources/computer.umdl', resource='resources/snowboy-common.res', sensitivity=0.5)

    def on_hotword_detected():
        speaker.play('resources/beep_hi.wav')
        logger.info('Hotword detected, switching to active listening')
        print('\nHotword detected, switching to active listening')

    def process_user_request(user_request_wave_file):
        speaker.play('resources/beep_lo.wav')
        logger.info('Active listening finished')
        print('Active listening finished')

        # For Debug: This does "echo"
        print('Debug: Echo input sound from user')
        speaker.play( user_request_wave_file )

        logger.info('Getting text from user speech')
        user_text = speech_to_text( user_request_wave_file )
        print('User request: %s' % user_text)

        logger.info('Calling brain service')
        # TODO: Connect to Brain service
        assistant_text = 'Hi, your request is "%s"' % user_text
        print('Assistant response: %s' % assistant_text)

        logger.info('Generating speech from assitant text')
        assistant_response_wave_file = text_to_speech( assistant_text )

        print('Playing assistant response as voice')
        logger.info('Playing speech respond')
        speaker.play( assistant_response_wave_file )

        print('\nListening for hotword')


    logger.info('Main loop started, press control + c to stop it')
    print('\n\nMain loop started\n\nListening for hotword')
    detector.start(
        detected_callback=on_hotword_detected,
        audio_recorder_callback=process_user_request
    )

