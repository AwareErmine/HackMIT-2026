import wave
from pathlib import Path

import numpy as np

IN_PATH = Path("respeaker_6ch_10s.wav")

with wave.open(str(IN_PATH), "rb") as f:
    channels = f.getnchannels()
    samplerate = f.getframerate()
    sampwidth = f.getsampwidth()
    pcm_bytes = f.readframes(f.getnframes())

pcm = np.frombuffer(pcm_bytes, dtype="<i2").reshape(-1, channels)

for ch in range(channels):
    out_path = Path(f"channel_{ch}.wav")
    with wave.open(str(out_path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(sampwidth)
        out.setframerate(samplerate)
        out.writeframes(pcm[:, ch].tobytes())
    print(f"wrote {out_path}")
