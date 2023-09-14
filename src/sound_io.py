# -*- coding: utf-8-*-

import logging
import tempfile
import wave
import collections
import pyaudio
import numpy

class Mic:

    # Not used, reserved for future applications

    def __init__(self):

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        self._audio = pyaudio.PyAudio()
        self._rate = 16_000
        self._chunk = 1024

        self._logger.info('PyAudio initialized')

    def __del__(self):
        self._audio.terminate()
        self._logger.info('PyAudio terminated')

    def get_audio_stream(self):
        self._logger.info('Getting audio stream')
        return self._audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            input_device_index=3
        )

    def audio_seconds_duration(self, seconds):
        for index in range(0, self._rate / self._chunk * seconds):
            yield index

    def compute_audio_power(self, data):
        # root-mean-square measures the power in an audio signal `sqrt(sum(S_i^2)/n)`
        buffer = numpy.frombuffer(data, numpy.int16).astype(numpy.float)
        rms = numpy.sqrt( (buffer * buffer).sum() / len( buffer ) )
        return rms / 3

    def get_ambient_noise_threshold(self):

        circular_buffer = collections.deque(maxlen=20)
        stream = self.get_audio_stream()

        for _ in self.audio_seconds_duration( 1 ):
            circular_buffer.append(
                self.compute_audio_power(
                    stream.read( self._chunk )
                )
            )

        stream.stop_stream()
        stream.close()

        average = sum(circular_buffer) / len(circular_buffer)
        ambient_noise_threshold = average * 1.8 # gain of 1.8

        self._logger.info('get_ambient_noise_threshold() => %f' % ambient_noise_threshold)

        return ambient_noise_threshold

    def active_listen(self, time_out_seconds=12, ambient_noise_threshold=None, onstart=None, onend=None):
        '''
            Records until one second of silence or times out after `time_out_seconds`
            Return wavefile location or None
        '''

        # Get ambient noise
        if not ambient_noise_threshold:
            ambient_noise_threshold = self.get_ambient_noise_threshold()

        # Trigger onstart event (if setted)
        if callable(onstart):
            self._logger.info('Trigger onstart')
            onstart()

        # Start listening ...
        circular_buffer = collections.deque(
            [ambient_noise_threshold * 1.2] * 30,
            maxlen=30
        )
        frames = []
        stream = self.get_audio_stream()

        was_time_out = True

        for _ in self.audio_seconds_duration( time_out_seconds ):

            # Get audio frame
            frame = stream.read( self._chunk )

            # Keep frame
            frames.append( frame )

            # Check silence
            circular_buffer.append(
                self.compute_audio_power( frame )
            )
            audio_power_average = sum(circular_buffer) / len(circular_buffer)

            if audio_power_average < ambient_noise_threshold * 0.8:
                was_time_out = False
                break

        # Listening is over
        stream.stop_stream()
        stream.close()

        if was_time_out:
            self._logger.info('Active listening finished by timeout')
        else:
            self._logger.info('Active listening finished by silence detection')

        # Trigger onend event (if setted)
        if callable(onend):
            self._logger.info('Trigger end')
            onend(was_time_out)

        # Save file
        with tempfile.SpooledTemporaryFile(mode='w+b') as in_memory_file:

            # Save frames in-memory-file
            wav_file = wave.open(in_memory_file, 'wb')
            wav_file.setnchannels(1)
            wav_file.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wav_file.setframerate(self._rate)
            wav_file.writeframes(''.join(frames))
            wav_file.close()

            # Reset in-memory-file to be read
            in_memory_file.seek(0)

            self._logger.info('Wave file generated')

            return in_memory_file


class Speaker:

    def __init__(self):

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        self._audio = pyaudio.PyAudio()

        self._logger.info('PyAudio initialized')

    def __del__(self):
        self._audio.terminate()
        self._logger.info('PyAudio terminated')

    def play(self, filename, onstart=None, onend=None):

        # Trigger onstart event (if setted)
        if callable(onstart):
            self._logger.info('Trigger onstart')
            onstart()

        self._logger.info('Playing file')

        wav_file = wave.open(filename, 'rb')

        stream = self._audio.open(
            format = self._audio.get_format_from_width( wav_file.getsampwidth() ),
            channels = wav_file.getnchannels(),
            rate = wav_file.getframerate(),
            output = True
        )

        chunk = 1024
        frame = wav_file.readframes( chunk )

        while frame:
            stream.write( frame )
            frame = wav_file.readframes( chunk )

        wav_file.close()
        stream.close()

        # Trigger onend event (if setted)
        if callable(onend):
            self._logger.info('Trigger end')
            onend()

