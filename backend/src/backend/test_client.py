"""
test_client.py

Stand-in for the React frontend, for testing the HTTP API in server.py
without the real app or hardware. Polls GET /fishies in the background and
prints whenever the list changes, and lets you type a speaker id + volume
(simulating dragging that speaker's fish) to PUT a gain update - same idea
as the frontend's own poll-and-drag behavior, just from a terminal.

Uses only the standard library (urllib) rather than adding requests/httpx as
a dependency for what's just a manual test script.
"""

import json
import os
import threading
import time
import urllib.request
from urllib.error import URLError

BASE_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:5005").rstrip("/")
POLL_INTERVAL_SECONDS = 1


def get_fishies() -> dict:
    with urllib.request.urlopen(f"{BASE_URL}/fishies") as response:
        return json.loads(response.read())


def put_fishy(fish_id: str, volume: float) -> None:
    body = json.dumps({"id": fish_id, "volume": volume}).encode("utf-8")
    request = urllib.request.Request(
        f"{BASE_URL}/fishies",
        data=body,
        method="PUT",
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(request)


def _poll_loop():
    # background loop: prints the fishies list whenever it changes
    last_seen = None
    while True:
        try:
            fishies = get_fishies()
        except URLError as e:
            print(f"CLIENT: could not reach backend ({e}) - is server() running?")
            time.sleep(POLL_INTERVAL_SECONDS)
            continue
        if fishies != last_seen:
            print("CLIENT:", fishies)
            last_seen = fishies
        time.sleep(POLL_INTERVAL_SECONDS)


def test_client() -> None:
    threading.Thread(target=_poll_loop, daemon=True).start()

    # simulates dragging a speaker's fish to a new volume (0 = muted, 20 = normal, 100 = max boost)
    while True:
        fish_id = input("Speaker id to adjust: ").strip()
        volume = float(input("Volume (0-100): ").strip())
        put_fishy(fish_id, volume)


if __name__ == "__main__":
    test_client()
