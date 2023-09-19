from pydub import AudioSegment
import base64
import time
import wave

'''
utility method to convert ogg file passed to the method to wav file
pydub library is being used to convert the file which needs ffpmeg to be installed on client 
!TODO need to check because when ogg file is converted to wav, the sound is not understandable
'''
def convert_to_wav(ogg_file):
    wav_file = 'tmp/user-response-%s.wav' % str(int(time.time()))
    song = AudioSegment.from_ogg(ogg_file)
    song.export(wav_file, format="wav")
    return wav_file

'''
utility method to convert wav file passed to the method to ogg file
pydub library is being used to convert the file which needs ffpmeg to be installed on client 
'''
def convert_to_ogg(wav_file):
    ogg_file = 'tmp/user-request-%s.ogg' % str(int(time.time()))
    song = AudioSegment.from_wav(wav_file)
    song.export(ogg_file, format="ogg")
    return ogg_file

'''
reads an ogg file into base64 encoded string
'''
def read_ogg_data_base64(ogg_file):    
    with open(ogg_file, "rb") as audio_file:
        audio_binary_data = audio_file.read()

    return base64.b64encode(audio_binary_data).decode('utf-8')

'''
saves a new wav file using the chunks passed to the method as recorded_data
'''
def save_wav_file(audio, recorded_data, channels, bits_per_sample, sample_rate):
    filename = 'tmp/user-request-%s.wav' % str(int(time.time()))

    wave_file = wave.open(filename, 'wb')
    wave_file.setnchannels(channels)
    wave_file.setsampwidth(
        audio.get_sample_size(
            audio.get_format_from_width(
                bits_per_sample                
            )
        )
    )
    wave_file.setframerate(
        sample_rate
    )
    wave_file.writeframes(
        b''.join(recorded_data)
    )
    wave_file.close()

    return filename
