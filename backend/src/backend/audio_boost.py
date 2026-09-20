"""
audio_boost.py

Scales one beamformed speaker stream by that speaker's gain - one
independent level per speaker, so each fish on the frontend can sit at its
own height (loud/normal/quiet). server.py calls apply() once per detected
direction each chunk (via beamformer.py's separated streams), so - unlike
the original single-active-speaker version - overlapping speakers each get
their own gain applied and are mixed together afterward, not just whichever
one is "active" this chunk.
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

    def apply(self, beam_audio: np.ndarray, speaker_label: str) -> np.ndarray:
        # scales one beamformed speaker's stream by their gain (1.0 if not yet adjusted),
        # then clips so a boosted signal doesn't distort/overflow
        gain = self.speaker_gains.get(speaker_label, DEFAULT_GAIN)
        boosted = beam_audio * gain
        return np.clip(boosted, -1.0, 1.0)
