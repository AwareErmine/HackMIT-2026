"""
server.py

UDP bridge between the audio pipeline and the frontend, plus the main
mic -> detect -> boost -> output loop. WebSockets were dropped for hackathon
simplicity in favor of plain UDP datagrams: JSON speaker-list updates go out
to the frontend's address, and per-speaker gain commands (one fish's height
on the ocean UI = one speaker's volume) come back in on our own listen port.

server() is the entry point called by backend/__init__.py:main(), which in
turn is what arduino/python/main.py runs once deployed on the UNO Q via App Lab.
"""

import json
import socket
import threading

from backend.audio_boost import AudioBooster
from backend.audio_output import AudioOutput
from backend.mic_input import MicInput
from backend.speaker_detect import SpeakerDetector

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 5005                    # backend listens here for messages from the frontend
FRONTEND_ADDR = ("127.0.0.1", 5006)   # default frontend (host, port) for local testing; overwritten
                                       # as soon as the frontend sends us anything (see _listen_loop)
DETECTION_INTERVAL_CHUNKS = 20        # how often (in chunks) to re-run speaker detection


class UDPBridge:
    def __init__(self, listen_host=LISTEN_HOST, listen_port=LISTEN_PORT, frontend_addr=FRONTEND_ADDR):
        self.frontend_addr = frontend_addr
        self.speaker_gains: dict[str, float] = {}  # speaker label -> gain, updated as fish get dragged
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((listen_host, listen_port))

    def send_speakers(self, speakers: list[str]):
        # pushes the current speaker list to the frontend as JSON
        payload = json.dumps({"type": "speakers", "speakers": speakers}).encode("utf-8")
        self.sock.sendto(payload, self.frontend_addr)

    def _listen_loop(self):
        # background loop: reads commands sent by the frontend (fish-drag gain updates, registration pings)
        while True:
            data, addr = self.sock.recvfrom(4096)
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                continue
            self.frontend_addr = addr  # learn/refresh where the frontend actually is
            if msg.get("type") == "set_speaker_gain":
                speaker = msg.get("speaker")
                gain = msg.get("gain")
                if speaker is not None and gain is not None:
                    self.speaker_gains[speaker] = gain

    def start_listening(self):
        # runs _listen_loop on a background thread so it doesn't block the audio loop
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def close(self):
        self.sock.close()


def server() -> None:
    # wires the mic -> detect -> boost -> output loop together and bridges it to the frontend over UDP
    bridge = UDPBridge()
    bridge.start_listening()

    mic = MicInput()
    detector = SpeakerDetector(sample_rate=mic.samplerate)
    booster = AudioBooster()
    booster.speaker_gains = bridge.speaker_gains  # share the dict so fish-drag updates apply immediately
    output = AudioOutput(samplerate=mic.samplerate)

    mic.start()
    output.start()

    chunk_count = 0
    active_speaker = None
    try:
        while True:
            chunk = mic.read_chunk()

            # only re-run the heavier speaker-detection step every N chunks
            if chunk_count % DETECTION_INTERVAL_CHUNKS == 0:
                speakers = detector.process_chunk(chunk)
                active_speaker = speakers[0] if speakers else None
                bridge.send_speakers(speakers)

            boosted = booster.apply(chunk, active_speaker)
            output.play_chunk(boosted)

            chunk_count += 1
    finally:
        mic.stop()
        output.stop()
        bridge.close()
