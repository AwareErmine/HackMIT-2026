"""
server.py

UDP bridge between the audio pipeline and the frontend, plus the main
mic -> DOA -> beamform -> boost -> output loop. WebSockets were dropped for
hackathon simplicity in favor of plain UDP datagrams: JSON speaker-list
updates go out to the frontend's address, and per-speaker gain commands (one
fish's height on the ocean UI = one speaker's volume) come back in on our
own listen port.

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
import uvicorn

import numpy as np

from backend.audio_boost import AudioBooster
from backend.audio_output import AudioOutput
from backend.beamformer import beamform
from backend.doa import find_directions
from backend.mic_input import MicInput
from backend.speaker_detect import SpeakerDetector
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import threading

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

DEFAULT_GAIN = 1.0
MAX_GAIN = 3.0  # keep in sync with audio_boost.py's MAX_GAIN

def gain_to_volume(gain: float) -> float:
    return (gain / MAX_GAIN) * 100

def volume_to_gain(volume: float) -> float:
    return (volume / 100) * MAX_GAIN

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

    mic = MicInput()
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
