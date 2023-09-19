from src.audio.sound_io import Speaker
from pygame import mixer
import logging

AUDIO_FORMAT_WAV = "wav"
AUDIO_FORMAT_OGG = "ogg"

'''
base Player class 
which can be initialized with frequency, size, channels and buffer
which should be valid for most of the players
'''
class Player(object):
    _player = None

    def __init__(self, frequency=44100, size=-16, channels=2, buffer=2048):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        self._frequency = frequency
        self._size = size
        self._channels = channels
        self._buffer = buffer

        self._logger.info('Player initialized')

    # play method to start playing the audio file passed to it using the _player object that should be instantiated on child classes 
    # it is also possible to override play method if it is not possible to instantiate _player object before
    def play(self, audio_file):
        self._player.play(audio_file)
        self._logger.info('Audio data played')

    
    # stop method to stop playing of the audio file
    # child classes need to override this method, template pattern
    def stop(self):
        self._logger.info('Child class need to implement stop method')

'''
OggPlayer class
which is extended from Player super class
play method is overriden because of the pygame library
'''
class OggPlayer(Player):
    def __init__(self, frequency=44100, size=-16, channels=2, buffer=2048):
        super().__init__(frequency, size, channels, buffer)        
        mixer.pre_init(frequency, size, channels, buffer) # may need to validate these with Juan Diego        

    def play(self, audio_file):  
        mixer.init()
        sound = mixer.Sound(audio_file)
        sound.play()        

    def stop(self):
        mixer.quit()

'''
WavPlayer class
which is extended from Player super class
'''
class WavPlayer(Player):
    def __init__(self):
        super().__init__()
        self._player = Speaker()

'''
Player Factory class to decide which player to use and select player accordingly
'''
class PlayerFactory(object):
    '''
    play method to decide which player to select first and then to play
    '''
    def play(self, audio_file):
        file_format = self._get_format(audio_file)
        player = self._get_player(file_format)
        if player != None:
            player.play(audio_file)

    '''
    find format of the audio_file, not required to have a library to do it as we are creating the audio files
    we only need to get the extension from file name
    '''
    def _get_format(self, audio_file):
        # no need to have any complex library implementation as we are creating the audio files
        # just find the extension from name and return it as format
        return audio_file.split(".")[-1]

    '''
    based on the format of audio file, create a player
    '''
    def _get_player(self, file_format):
        if file_format == AUDIO_FORMAT_WAV:
            return WavPlayer()
        elif file_format == AUDIO_FORMAT_OGG:
            return OggPlayer()                    
        return None