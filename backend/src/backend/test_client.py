"""
test_client.py

Stand-in for the React frontend, for testing the UDP protocol in server.py
without the real app or hardware. Registers itself with the backend (so the
backend knows where to push speaker updates), prints incoming speaker-list
updates, and lets you type a speaker name + gain (simulating dragging that
speaker's fish) to send a gain-update command back.
"""

import json
import socket
import threading

BACKEND_ADDR = ("127.0.0.1", 5005)  # matches server.LISTEN_PORT
LISTEN_PORT = 5006                  # matches server.FRONTEND_ADDR's default port


def _listen(sock: socket.socket):
    # background loop: prints every speaker-list update pushed by the backend
    while True:
        data, _addr = sock.recvfrom(4096)
        print("CLIENT:", json.loads(data))


def test_client() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", LISTEN_PORT))

    # tells the backend where we are, so it starts pushing speaker updates here
    sock.sendto(json.dumps({"type": "register"}).encode("utf-8"), BACKEND_ADDR)

    threading.Thread(target=_listen, args=(sock,), daemon=True).start()

    # simulates dragging a speaker's fish to a new height (0.0 = muted, 1.0 = normal, 3.0 = max boost)
    while True:
        speaker = input("Speaker to adjust: ").strip()
        gain = float(input("Gain (0.0-3.0): ").strip())
        msg = json.dumps({"type": "set_speaker_gain", "speaker": speaker, "gain": gain}).encode("utf-8")
        sock.sendto(msg, BACKEND_ADDR)


if __name__ == "__main__":
    test_client()
