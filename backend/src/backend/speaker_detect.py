"""
speaker_detect.py

Assigns stable "Speaker N" labels to the directions found by doa.py, so the
same physical person keeps the same label - and the same fish on the
frontend - as the conversation continues.

This replaces the original diart-based approach: diart's voice-embedding
labels don't have a natural way to apply to N separately-beamformed streams
without running diart once per beam per chunk, which is too heavy to do in
real time on top of SRP-PHAT + N beamformers already. Identity here is
purely angle-based instead - simpler, and naturally more stable than
embeddings (no more diart relabeling mid-conversation), but a new person
standing at the same angle as an existing speaker will be (mis)treated as
that same speaker.
"""

ANGLE_MATCH_TOLERANCE_DEGREES = 20  # a detected direction within this many degrees of a
                                     # known speaker's angle is treated as the same person
ANGLE_SMOOTHING = 0.3                # how much a new reading nudges a speaker's tracked angle
                                      # (0 = never update, 1 = jump straight to the new reading)
CONFIRM_HITS = 5  # a direction must be detected at least this many times before it shows up
                   # as a fish on the frontend - filters one-off spurious blips (echoes, a
                   # passing background voice) without muting anyone: audio still applies gain
                   # to every detected direction immediately regardless of this count, since
                   # detection runs every ~64ms this only delays a real ongoing voice's fish
                   # by a few hundred ms, not enough to notice


class SpeakerDetector:
    def __init__(self):
        self._speakers: dict[str, float] = {}  # label -> tracked angle in degrees
        self._hit_counts: dict[str, int] = {}  # label -> number of times detected

    def _closest_speaker(self, angle_degrees: float):
        # finds the known speaker whose tracked angle is nearest this reading,
        # accounting for wraparound at the 0/360 boundary
        best_label, best_diff = None, None
        for label, known_angle in self._speakers.items():
            diff = abs(angle_degrees - known_angle) % 360
            diff = min(diff, 360 - diff)
            if best_diff is None or diff < best_diff:
                best_label, best_diff = label, diff
        return best_label, best_diff

    def label_for_angle(self, angle_degrees: float) -> str:
        # returns the stable speaker label for this angle, creating a new one if this
        # direction doesn't match any speaker seen before
        label, diff = self._closest_speaker(angle_degrees)
        if label is not None and diff <= ANGLE_MATCH_TOLERANCE_DEGREES:
            old_angle = self._speakers[label]
            signed_diff = ((angle_degrees - old_angle + 180) % 360) - 180
            self._speakers[label] = old_angle + ANGLE_SMOOTHING * signed_diff
            self._hit_counts[label] += 1
            return label

        new_label = f"Speaker {len(self._speakers) + 1}"
        self._speakers[new_label] = angle_degrees
        self._hit_counts[new_label] = 1
        return new_label

    def label_for_angles(self, angles_degrees: list[float]) -> list[str]:
        # convenience: label a whole chunk's worth of detected directions at once
        return [self.label_for_angle(a) for a in angles_degrees]

    def get_known_speakers(self) -> list[str]:
        # only speakers detected repeatedly enough to be confident it's a real, ongoing voice
        # nearby - not every label that's ever been created, which would include one-off blips
        return [label for label, count in self._hit_counts.items() if count >= CONFIRM_HITS]
