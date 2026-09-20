"""
server.py

HTTP API between the audio pipeline and the frontend, plus the main
mic -> DOA -> beamform -> boost -> output loop. UDP was dropped because a
browser can't open raw UDP sockets at all - GET /fishies reports each
speaker's current volume (0-100, mapped from their internal gain), and
PUT /fishies sets it (one fish's height on the ocean UI = one speaker's
volume). Runs via uvicorn on a background thread alongside the audio loop.
If no mic is connected, the HTTP API still comes up on its own (useful for
frontend/API development without hardware) - only the audio path is skipped.

Unlike the original single-active-speaker design, this runs DOA + one
beamformer per detected direction + gain on every chunk (not periodically) -
overlapping speakers need their own separated stream applied continuously,
not just an occasional identity check. This is real DSP work happening every
~64ms (at the default blocksize); untested for real-time performance on the
UNO Q itself.

server() is the entry point called by backend/__init__.py:main(), which in
turn is what arduino/python/main.py runs once deployed on the UNO Q via App Lab.
"""

import threading

import numpy as np
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.audio_boost import DEFAULT_GAIN, MAX_GAIN, AudioBooster
from backend.audio_output import AudioOutput
from backend.beamformer import beamform
from backend.doa import find_directions
from backend.mic_input import MicInput
from backend.speaker_detect import SpeakerDetector

SPAWN_VOLUME = 20    # the frontend's default fish spawn position
SPAWN_GAIN = DEFAULT_GAIN  # what that position means: normal, unmodified volume

def volume_to_gain(volume: float) -> float:
    # piecewise: 0-20% maps to 0.0-SPAWN_GAIN (muted -> normal), 20-100% maps to
    # SPAWN_GAIN-MAX_GAIN (normal -> max boost) - spawning at 20% has to mean
    # "normal volume", not quieter or louder than an unmodified voice
    if volume <= SPAWN_VOLUME:
        return (volume / SPAWN_VOLUME) * SPAWN_GAIN
    return SPAWN_GAIN + ((volume - SPAWN_VOLUME) / (100 - SPAWN_VOLUME)) * (MAX_GAIN - SPAWN_GAIN)

def gain_to_volume(gain: float) -> float:
    # inverse of volume_to_gain, for reporting a speaker's current gain back as a volume
    if gain <= SPAWN_GAIN:
        return (gain / SPAWN_GAIN) * SPAWN_VOLUME
    return SPAWN_VOLUME + ((gain - SPAWN_GAIN) / (MAX_GAIN - SPAWN_GAIN)) * (100 - SPAWN_VOLUME)

def build_app(detector: SpeakerDetector, speaker_gains: dict[str, float]) -> FastAPI:
    # bundles the HTTP routes with the state they need (detector, speaker_gains),
    # same idea as UDPBridge bundling state + behavior together
    app = FastAPI()
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.get("/fishies")
    def get_fishies():
        return {
            "fishies": [
                {"id": label, "volume": gain_to_volume(speaker_gains.get(label, DEFAULT_GAIN))}
                for label in detector.get_known_speakers()
            ]
        }

    @app.put("/fishies")
    def put_fishy(fish: dict):
        speaker_gains[fish["id"]] = volume_to_gain(fish["volume"])
        return {"ok": True}

    return app

def server() -> None:
    speaker_gains: dict[str, float] = {}
    detector = SpeakerDetector()
    app = build_app(detector, speaker_gains)
    threading.Thread(
        target=lambda: uvicorn.run(app, host="0.0.0.0", port=5005),
        daemon=True,
    ).start()

    try:
        mic = MicInput()
    except RuntimeError as e:
        # no mic connected - keep the HTTP API up anyway so it can still be tested/developed
        # against, just without any audio path
        print(f"[server] {e} - running HTTP API only, no audio")
        threading.Event().wait()
        return

    booster = AudioBooster()
    booster.speaker_gains = speaker_gains  # same sharing pattern as before
    output = AudioOutput(samplerate=mic.samplerate)

    mic.start()
    output.start()

    try:
        while True:
            chunk = mic.read_chunk()
            directions = find_directions(chunk, mic.samplerate)
            labels = detector.label_for_angles(directions)

            mixed = np.zeros(chunk.shape[0], dtype=np.float32)
            for angle, label in zip(directions, labels):
                beam = beamform(chunk, angle, mic.samplerate)
                mixed += booster.apply(beam, label)
            output.play_chunk(np.clip(mixed, -1.0, 1.0))
    finally:
        mic.stop()
        output.stop()
