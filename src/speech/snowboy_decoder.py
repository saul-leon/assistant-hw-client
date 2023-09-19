# -*- coding: utf-8-*-

from . import snowboydetect
from src.utils.audio_utils import save_wav_file

import collections
import pyaudio
import time
import os

import logging

class RingBuffer(object):
    def __init__(self, size=4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        self._buf.extend(data)

    def get(self):
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp


class HotwordDetector(object):
    """
    Snowboy decoder to detect whether a keyword specified by `decoder_model`
    exists in a microphone input stream.

    :param decoder_model: decoder model file path, a string or a list of strings
    :param resource: resource file path.
    :param sensitivity: decoder sensitivity, a float of a list of floats.
                              The bigger the value, the more senstive the
                              decoder. If an empty list is provided, then the
                              default sensitivity in the model will be used.
    :param audio_gain: multiply input volume by this factor.
    :param apply_frontend: applies the frontend processing algorithm if True.
    """

    def __init__(self,
                 decoder_model,
                 resource='resources/snowboy-common.res',
                 sensitivity=[],
                 audio_gain=1,
                 apply_frontend=False):

        if type(decoder_model) is not list:
            decoder_model = [decoder_model]

        if type(sensitivity) is not list:
            sensitivity = [sensitivity]

        model_str = ",".join(decoder_model)

        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=resource.encode(),
            model_str=model_str.encode()
        )

        self.detector.SetAudioGain(audio_gain)
        self.detector.ApplyFrontend(apply_frontend)

        self.num_hotwords = self.detector.NumHotwords()

        self.can_start_recording = False

        if len(decoder_model) > 1 and len(sensitivity) == 1:
            sensitivity = sensitivity * self.num_hotwords

        if len(sensitivity) != 0 and self.num_hotwords != len(sensitivity):
            raise Exception(
                "number of hotwords in decoder_model (%d) and sensitivity "
                "(%d) does not match" % (self.num_hotwords, len(sensitivity))
            )

        sensitivity_str = ",".join([str(t) for t in sensitivity])

        if len(sensitivity) != 0:
            self.detector.SetSensitivity(sensitivity_str.encode())

        self.ring_buffer = RingBuffer(
            self.detector.NumChannels() * self.detector.SampleRate() * 5
        )

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self._logger.info('HotwordDetector created')

    def start(self,
              detected_callback=None,
              interrupt_check=lambda: False,
              sleep_time=0.03,
              audio_recorder_callback=None,
              silent_count_threshold=15,
              recording_timeout=100):
        """
        Start the voice detector. For every `sleep_time` second it checks the
        audio buffer for triggering keywords. If detected, then call
        corresponding function in `detected_callback`, which can be a single
        function (single model) or a list of callback functions (multiple
        models). Every loop it also calls `interrupt_check` -- if it returns
        True, then breaks from the loop and return.

        :param detected_callback: a function or list of functions. The number of
                                  items must match the number of models in
                                  `decoder_model`.
        :param interrupt_check: a function that returns True if the main loop
                                needs to stop.
        :param float sleep_time: how much time in second every loop waits.
        :param audio_recorder_callback: if specified, this will be called after
                                        a keyword has been spoken and after the
                                        phrase immediately after the keyword has
                                        been recorded. The function will be
                                        passed the name of the file where the
                                        phrase was recorded.
        :param silent_count_threshold: indicates how long silence must be heard
                                       to mark the end of a phrase that is
                                       being recorded.
        :param recording_timeout: limits the maximum length of a recording.
        :return: None
        """

        self._running = True

        def audio_callback(in_data, frame_count, time_info, status):
            self.ring_buffer.extend(in_data)
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue

        self.audio = pyaudio.PyAudio()

        self.stream_in = self.audio.open(
            input=True,
            output=False,
            format=self.audio.get_format_from_width(
                self.detector.BitsPerSample() / 8
            ),
            channels=self.detector.NumChannels(),
            rate=self.detector.SampleRate(),
            frames_per_buffer=2048,
            stream_callback=audio_callback
        )

        if interrupt_check():
            self._logger.debug("detect voice return")
            return

        if type(detected_callback) is not list:
            detected_callback = [detected_callback]

        if len(detected_callback) == 1 and self.num_hotwords > 1:
            detected_callback *= self.num_hotwords

        if self.num_hotwords != len(detected_callback):
            raise Exception(
                "Error: hotwords in your models (%d) do not match the number of " \
                "callbacks (%d)" % (self.num_hotwords, len(detected_callback))
            )

        self._logger.debug("detecting...")

        state = "PASSIVE"

        while self._running is True:

            if interrupt_check():
                self._logger.debug("detect voice break")
                break

            data = self.ring_buffer.get()

            if len(data) == 0:
                time.sleep(sleep_time)
                continue

            status = self.detector.RunDetection(data)
    
            if status == -1:
                self._logger.warning("Error initializing streams or reading audio data")

            if state == "PASSIVE":

                if status > 0 or self.can_start_recording: # hotword detected

                    if self.can_start_recording:
                        status = 1
                    
                    self.recorded_data = []
                    self.recorded_data.append(data)

                    silent_count = 0
                    recording_count = 0

                    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    self._logger.info("Hotword detected at time: " + now)

                    callback = detected_callback[ status - 1 ]
                    if callback is not None:
                        callback()

                    if audio_recorder_callback is not None:
                        state = "ACTIVE"                    

            elif state == "ACTIVE":

                stop_recording = False

                if recording_count > recording_timeout:
                    stop_recording = True

                elif status == -2: # silence found
                    if silent_count > silent_count_threshold:
                        stop_recording = True
                    else:
                        silent_count = silent_count + 1

                elif status == 0: # voice found
                    silent_count = 0

                if stop_recording == True:
                    fname = save_wav_file(self.audio, self.recorded_data, 1, self.detector.BitsPerSample() / 8, self.detector.SampleRate())
                    self._logger.debug("wav file saved on: %s" % fname)
                    audio_recorder_callback(fname)
                    state = "PASSIVE"
                    continue

                recording_count = recording_count + 1
                self.recorded_data.append(data)

        logger.debug("finished.")

    def __del__(self):
        """
        Terminate audio stream. Users can call start() again to detect.
        :return: None
        """
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()
        self._running = False
