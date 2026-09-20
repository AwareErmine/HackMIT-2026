# HackMIT Backend

The backend runs on the UNO Q. It owns local audio processing and exposes a
small HTTP API for the React control interface; PCM audio never goes through
the browser.

## Install and run

```bash
uv sync
uv run backend
```

The API listens on port 5005:

- `GET /health` checks that the service is reachable.
- `GET /fishies` returns detected speaker controls.
- `PUT /fishies` accepts `{ "id": "Speaker 1", "volume": 20 }`.

Volumes are percentages from 0 through 100. A volume of 20 represents the
normal, unmodified gain.

## Test without audio hardware

Set `HACKMIT_MOCK_FISHIES=1` before starting the backend to seed four controls
when no matching microphone is connected.

Set `HACKMIT_API_ONLY=1` to skip audio-device initialization entirely while
testing the Arduino and frontend control path.

PowerShell:

```powershell
$env:HACKMIT_MOCK_FISHIES="1"
uv run backend
```

Linux:

```bash
HACKMIT_MOCK_FISHIES=1 uv run backend
```

Run the terminal client in another shell:

```bash
uv run python src/backend/test_client.py
```

To target a backend on the UNO Q, set `BACKEND_URL=http://joyce.local:5005`.
