"""
mic_input.py

Opens the ReSpeaker 4-Mic Array over USB and continuously reads the 4 raw
per-mic channels (not the chip's single processed channel 0 - the DIY
beamforming pipeline in doa.py/beamformer.py needs all 4 independently to
compute directions and steer toward them itself). Hands raw audio chunks to
server.py's processing loop via a thread-safe queue.

First stage of the audio path: mic -> [mic_input] -> doa/beamformer/
audio_boost -> audio_output. Requires the 6-channel firmware to be flashed
on the array - the default firmware only exposes 2 real channels, which
would make channels 1-4 duplicates/silence rather than 4 distinct mics.
"""

import queue

import sounddevice as sd

MIC_NAME_HINT = "ReSpeaker 4 Mic Array"  # matches the OS-reported device name (confirmed via
                                          # sd.query_devices(): "ReSpeaker 4 Mic Array (UAC1.0)")
SAMPLE_RATE = 16000          # sample rate the DOA/beamforming math is tuned for
BLOCK_SIZE = 1024            # frames per chunk read from the stream

OPEN_CHANNEL_COUNT = 5       # open channels 0-4 (channel 0 is discarded below - the device
                              # doesn't let us request channels 1-4 without also opening 0)
RAW_CHANNEL_SLICE = slice(1, 5)  # the 4 raw per-mic channels within that opened range


class MicInput:
    def __init__(self, samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE):
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.audio_queue = queue.Queue()
        self.device_index = self._find_device()
        self.stream = None

    def _find_device(self):
        # scans available input devices and returns the one matching the mic name
        for idx, dev in enumerate(sd.query_devices()):
            if MIC_NAME_HINT.lower() in dev["name"].lower() and dev["max_input_channels"] >= OPEN_CHANNEL_COUNT:
                return idx
        raise RuntimeError(f"Could not find a {OPEN_CHANNEL_COUNT}-channel mic containing '{MIC_NAME_HINT}'")

    def _callback(self, indata, frames, time_info, status):
        # sounddevice calls this on its own thread for every audio block
        if status:
            print(f"[mic_input] stream status: {status}")
        raw_channels = indata[:, RAW_CHANNEL_SLICE].copy()  # shape (frames, 4)
        self.audio_queue.put(raw_channels)

    def start(self):
        # opens and starts the input stream; audio starts flowing into the queue
        self.stream = sd.InputStream(
            device=self.device_index,
            channels=OPEN_CHANNEL_COUNT,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            callback=self._callback,
        )
        self.stream.start()

    def stop(self):
        # stops and releases the stream
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def read_chunk(self, timeout=None):
        # blocks until the next (frames, 4) raw audio chunk is available
        return self.audio_queue.get(timeout=timeout)
