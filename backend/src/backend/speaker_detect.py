"""
speaker_detect.py

Runs diart (built on pyannote-audio) over the live audio stream to figure out
who is currently talking, assigning temporary labels (Speaker 1, Speaker 2, ...)
with no voice-enrollment step. server.py feeds it audio chunks every ~1-2s and
reads back the current speaker(s) to push to the frontend over UDP.

Note: diart's real-time pipeline API may need small adjustments once tested
directly on the UNO Q - this wraps it behind a simple
process_chunk()/get_current_speakers() interface so the rest of the backend
doesn't need to know diart's internals.
"""

import numpy as np
from diart import SpeakerDiarization


class SpeakerDetector:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.pipeline = SpeakerDiarization()
        self.current_speakers = []  # most recent list of active speaker labels
        self._label_map = {}        # maps diart's raw internal ids to friendly "Speaker N" names

    def _friendly_label(self, raw_id):
        # converts diart's internal speaker id into a stable "Speaker N" label,
        # assigning the next number the first time a given id is seen
        if raw_id not in self._label_map:
            self._label_map[raw_id] = f"Speaker {len(self._label_map) + 1}"
        return self._label_map[raw_id]

    def process_chunk(self, audio_chunk: np.ndarray):
        # feeds one chunk of audio into diart and updates self.current_speakers
        # with whoever diart currently thinks is talking
        annotation = self.pipeline(audio_chunk, self.sample_rate)
        speakers = set()
        for _segment, _track, raw_id in annotation.itertracks(yield_label=True):
            speakers.add(self._friendly_label(raw_id))
        self.current_speakers = sorted(speakers)
        return self.current_speakers

    def get_current_speakers(self):
        # returns the last computed list of active speaker labels without recomputing
        return self.current_speakers
