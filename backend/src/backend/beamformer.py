"""
beamformer.py

Delay-and-sum beamforming: given raw 4-channel audio and a target direction
(from doa.py), produces one mono stream that reinforces sound from that
direction and partially suppresses sound from other directions. server.py
runs this once per currently-detected direction, so overlapping speakers
each get their own separated-ish stream to gain independently in
audio_boost.py before being mixed back down in audio_output.py.

Delay-and-sum is the simplest beamformer there is - it won't cleanly isolate
voices that are close together in angle (expect real leakage), but it's
cheap enough to run several in parallel every chunk, which is what matters
for a build like this.
"""

import numpy as np

from backend.mic_geometry import steering_delays_seconds


def beamform(chunk: np.ndarray, angle_degrees: float, sample_rate: int) -> np.ndarray:
    # chunk: (frames, 4) raw audio; returns one (frames,) mono stream steered at angle_degrees
    n_frames, n_mics = chunk.shape
    freqs = np.fft.rfftfreq(n_frames, d=1.0 / sample_rate)
    delays = steering_delays_seconds(angle_degrees)

    aligned_sum = np.zeros(len(freqs), dtype=np.complex128)
    for mic in range(n_mics):
        spectrum = np.fft.rfft(chunk[:, mic], n=n_frames)
        # shifts this mic's signal so it lines up in phase with the others,
        # assuming a source at angle_degrees
        phase_shift = np.exp(-1j * 2 * np.pi * freqs * delays[mic])
        aligned_sum += spectrum * phase_shift

    beam = np.fft.irfft(aligned_sum, n=n_frames) / n_mics
    return beam.astype(np.float32)
