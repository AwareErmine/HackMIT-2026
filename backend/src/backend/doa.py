"""
doa.py

Multi-source direction-of-arrival estimation: given one chunk of raw 4-mic
audio, finds the angle(s) sound is currently arriving from - possibly more
than one at once, unlike the chip's own onboard DOAANGLE reading (which only
ever reports a single current direction). This is what makes it possible to
tell two people talking over each other apart by direction, so each can get
their own beam in beamformer.py.

Uses SRP-PHAT (steered-response power with phase transform): scans a set of
candidate angles, and for each one, checks how well the 4 channels would line
up in phase if a source were actually there. Real sources show up as local
peaks in that response.

Known limitations, worth confirming once there's real hardware data to test
against: the array is small (6.4cm across), so inter-mic timing differences
are tiny - expect coarser angular accuracy than a larger array would give.
Peak-finding also doesn't handle the 0/360 wraparound boundary, so a source
sitting right near 0 degrees could occasionally get missed or double-counted.
"""

import numpy as np
from scipy.signal import find_peaks

from backend.mic_geometry import steering_delays_seconds

ANGLE_STEP_DEGREES = 5            # candidate angle resolution to scan
PEAK_HEIGHT_RATIO = 0.5           # a candidate angle counts as a source if its power is
                                   # at least this fraction of the strongest peak this chunk
MIN_PEAK_SEPARATION_DEGREES = 30  # two peaks closer than this are treated as one source


def _cross_spectrum_phat(sig_i: np.ndarray, sig_j: np.ndarray, n_fft: int) -> np.ndarray:
    # cross-power spectrum between two mic signals, phase-normalized (PHAT) so timing
    # alignment matters and raw loudness/spectral content doesn't
    Xi = np.fft.rfft(sig_i, n=n_fft)
    Xj = np.fft.rfft(sig_j, n=n_fft)
    cross = Xi * np.conj(Xj)
    return cross / np.maximum(np.abs(cross), 1e-12)


def find_directions(chunk: np.ndarray, sample_rate: int) -> list[float]:
    # chunk: (frames, 4) raw audio, one column per raw mic channel
    # returns estimated source angles in degrees - zero, one, or several, depending on
    # how many people are talking this chunk
    n_frames, n_mics = chunk.shape
    freqs = np.fft.rfftfreq(n_frames, d=1.0 / sample_rate)

    cross_phat = {}
    for i in range(n_mics):
        for j in range(i + 1, n_mics):
            cross_phat[(i, j)] = _cross_spectrum_phat(chunk[:, i], chunk[:, j], n_frames)

    angles = np.arange(0, 360, ANGLE_STEP_DEGREES)
    power = np.zeros(len(angles))

    # for each candidate angle, check how well the mics would line up in phase if a
    # source were actually there - real sources show up as local maxima
    for idx, angle in enumerate(angles):
        delays = steering_delays_seconds(angle)
        score = 0.0
        for (i, j), cross in cross_phat.items():
            tau = delays[i] - delays[j]
            steering = np.exp(1j * 2 * np.pi * freqs * tau)
            score += np.real(np.sum(cross * np.conj(steering)))
        power[idx] = score

    if power.max() <= 0:
        return []

    threshold = power.max() * PEAK_HEIGHT_RATIO
    min_distance = max(1, MIN_PEAK_SEPARATION_DEGREES // ANGLE_STEP_DEGREES)
    peak_indices, _ = find_peaks(power, height=threshold, distance=min_distance)

    return [float(angles[i]) for i in peak_indices]
