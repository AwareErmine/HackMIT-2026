import argparse
import math
import subprocess
import wave
from pathlib import Path

import numpy as np

SAMPLE_RATE = 16000
CHANNELS = 6


def channel_stats(samples: np.ndarray) -> tuple[float, float, int]:
    normalized = samples.astype(np.float64) / 32768.0
    rms = float(np.sqrt(np.mean(normalized**2)))
    dbfs = 20 * math.log10(rms) if rms > 0 else float("-inf")
    return rms, dbfs, int(np.count_nonzero(samples))


def main() -> None:
    parser = argparse.ArgumentParser(description="Record the ReSpeaker's six ALSA channels.")
    parser.add_argument("output", nargs="?", type=Path, default=Path("respeaker_6ch_10s.wav"))
    parser.add_argument("--device", default="hw:0,0")
    parser.add_argument("--seconds", type=int, default=10)
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "arecord",
        "-q",
        "-D",
        args.device,
        "-f",
        "S16_LE",
        "-r",
        str(SAMPLE_RATE),
        "-c",
        str(CHANNELS),
        "-d",
        str(args.seconds),
        str(args.output),
    ]
    print(f"Recording {args.seconds}s from {args.device} to {args.output}")
    subprocess.run(command, check=True)

    with wave.open(str(args.output), "rb") as wav_file:
        if wav_file.getnchannels() != CHANNELS or wav_file.getsampwidth() != 2:
            raise RuntimeError("arecord did not produce six-channel 16-bit PCM")
        pcm = np.frombuffer(wav_file.readframes(wav_file.getnframes()), dtype="<i2")
        pcm = pcm.reshape(-1, CHANNELS)

    for channel in range(CHANNELS):
        rms, dbfs, nonzero = channel_stats(pcm[:, channel])
        print(
            f"channel {channel}: rms={rms:.6f}, {dbfs:.1f} dBFS, "
            f"nonzero={nonzero}/{len(pcm)}"
        )


if __name__ == "__main__":
    main()
