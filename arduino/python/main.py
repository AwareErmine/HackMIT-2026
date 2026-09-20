"""
arduino/python/main.py

Entry point App Lab actually runs on the UNO Q's Linux side. This is a thin
launcher: the real audio pipeline (mic capture, speaker detection, boosting,
HTTP API for the frontend) lives in the backend/ uv package so it can be
developed, tested, and dependency-managed independently of App Lab. This
just imports and runs it once deployed on the board.

NOTE: the backend package needs to be importable from wherever App Lab runs
this file - e.g. installing it (`uv pip install -e ../../backend`) into
whatever environment App Lab uses, or adding backend/src to PYTHONPATH.
Not yet confirmed how App Lab wants dependencies declared in app.yaml.
"""

from backend import main

if __name__ == "__main__":
    main()
