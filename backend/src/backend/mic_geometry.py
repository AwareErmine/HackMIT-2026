"""
mic_geometry.py

Shared physical constants for the 4-mic array: each mic's fixed position and
the speed of sound. Used by both doa.py (finding which directions sound is
coming from) and beamformer.py (steering toward those directions), so the
two stay consistent with each other.
"""

import numpy as np

SPEED_OF_SOUND = 343.0  # m/s, in air at room temperature

# (x, y, z) in meters, array center at the origin, all 4 mics on a horizontal
# plane (assumes the array is mounted flat, per the current headphone-top
# mounting plan). Taken from the array's published ODAS reference config.
# Order assumed to match raw channels 1-4, in that order - unverified on our
# actual hardware; confirm by covering one mic at a time and checking which
# channel's amplitude drops.
MIC_POSITIONS = np.array([
    [-0.032, 0.000, 0.0],
    [0.000, -0.032, 0.0],
    [0.032, 0.000, 0.0],
    [0.000, 0.032, 0.0],
])


def steering_delays_seconds(angle_degrees: float) -> np.ndarray:
    # each mic's expected extra travel time (seconds) for a far-field source at this
    # angle, relative to the array center - negative means "reaches this mic sooner"
    theta = np.radians(angle_degrees)
    direction = np.array([np.cos(theta), np.sin(theta), 0.0])
    return -(MIC_POSITIONS @ direction) / SPEED_OF_SOUND
