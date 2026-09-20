import wave
from pathlib import Path

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000
CHANNELS = 6
SECONDS = 10
DEVICE_HINT = "XVF3000"

def find_device():
    for idx, dev in enumerate(sd.query_devices()):
        if DEVICE_HINT.lower() in dev["name"].lower() and dev["max_input_channels"] >= CHANNELS:
            return idx
    raise RuntimeError("Could not find 6-channel XVF3000 input device")

device = 1
print(f"Recording from device {device}: {sd.query_devices()[device]['name']}")

audio = sd.rec(
    int(SAMPLE_RATE * SECONDS),
    samplerate=SAMPLE_RATE,
    channels=CHANNELS,
    dtype="float32",
    device=device,
)
sd.wait()

out = Path("respeaker_6ch_10s.wav")
pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype("<i2")

with wave.open(str(out), "wb") as f:
    f.setnchannels(CHANNELS)
    f.setsampwidth(2)
    f.setframerate(SAMPLE_RATE)
    f.writeframes(pcm.tobytes())

rms = np.sqrt(np.mean(audio**2, axis=0))
dbfs = 20 * np.log10(np.maximum(rms, 1e-12))

print(f"Wrote {out}")
for i, (r, db) in enumerate(zip(rms, dbfs)):
    print(f"channel {i}: rms={r:.6f}, {db:.1f} dBFS")