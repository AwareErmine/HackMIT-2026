"""
audio_output.py

Sends the final, boosted audio out through the UNO Q's headphone jack.
Last stage of the audio path: mic_input -> speaker_detect -> audio_boost ->
[audio_output] -> headphones.
"""

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000


class AudioOutput:
    def __init__(self, samplerate=SAMPLE_RATE):
        self.samplerate = samplerate
        self.stream = None

    def start(self):
        # opens the output stream to the default playback device (the headphone jack)
        self.stream = sd.OutputStream(samplerate=self.samplerate, channels=1)
        self.stream.start()

    def stop(self):
        # stops and releases the output stream
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def play_chunk(self, audio_chunk: np.ndarray):
        # writes one chunk of processed audio out to the headphones
        self.stream.write(audio_chunk.astype(np.float32))
