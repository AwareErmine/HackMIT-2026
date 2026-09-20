# HackMIT UNO Q App

This Arduino App starts the Python backend on the UNO Q and exposes its control
API on port 5005. Audio capture, processing, and playback remain local to the
UNO Q; the browser exchanges only JSON control data.

The App Lab launcher starts the real ReSpeaker audio pipeline by default.
Detected directions become fish in the frontend, and fish volume changes are
applied to the corresponding audio streams on the UNO Q.

## Build for App Lab

From the repository root in Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\arduino\build_app.ps1
```

Import `arduino/dist/HackMIT.zip` into Arduino App Lab. The archive contains
`app.yaml` at its root together with the backend package and Python
requirements.

## Run from an SSH checkout

If the full repository is already at `~/project` on the UNO Q:

```bash
cd ~/project
python3 arduino/python/main.py
```

Set `HACKMIT_BACKEND_SRC` when the backend source is stored elsewhere.
