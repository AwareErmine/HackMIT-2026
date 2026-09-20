"""
audio_boost.py

Takes incoming audio and the speaker currently talking, and scales the
volume by that speaker's gain - one independent level per speaker, so each
fish on the frontend can sit at its own height (loud/normal/quiet) rather
than a single on/off boost target. Sits between speaker_detect.py (who's
talking) and audio_output.py (final playback).

Limitation: the mic gives one mixed-down audio channel, and diart reports
only one "active" speaker per chunk (no true overlapping-voice separation),
so only one speaker's gain is actually applied per chunk - whichever one is
active. Two people talking over each other won't be heard at two different
volumes.
"""

import numpy as np

DEFAULT_GAIN = 1.0  # gain for any speaker whose fish hasn't been moved yet (no change)
MIN_GAIN = 0.0       # fish dragged to the very bottom = fully muted
MAX_GAIN = 3.0        # fish dragged to the very top = loudest allowed boost


class AudioBooster:
    def __init__(self):
        self.speaker_gains: dict[str, float] = {}  # speaker label -> gain, set from the frontend via server.py

    def set_speaker_gain(self, speaker_label: str, gain: float):
        # updates one speaker's gain (e.g. from that speaker's fish being dragged), clamped to a safe range
        self.speaker_gains[speaker_label] = max(MIN_GAIN, min(MAX_GAIN, gain))

    def apply(self, audio_chunk: np.ndarray, active_speaker: str) -> np.ndarray:
        # scales the chunk's volume by the active speaker's gain (1.0 if they haven't been adjusted),
        # then clips so a boosted signal doesn't distort/overflow
        gain = self.speaker_gains.get(active_speaker, DEFAULT_GAIN) if active_speaker else DEFAULT_GAIN
        boosted = audio_chunk * gain
        return np.clip(boosted, -1.0, 1.0)
