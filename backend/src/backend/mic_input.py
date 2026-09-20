"""
mic_input.py

Opens the reSpeaker XVF3800 mic over USB and continuously reads channel 0
(the pre-cleaned, voice-focused channel it sends). Hands raw audio chunks to
server.py's processing loop via a thread-safe queue. First stage of the
audio path: mic -> [mic_input] -> speaker_detect / audio_boost -> audio_output.
"""

import queue

import sounddevice as sd

MIC_NAME_HINT = "ReSpeaker 4 Mic Array"  # matches the OS-reported device name (confirmed via
                                          # sd.query_devices(): "ReSpeaker 4 Mic Array (UAC1.0)");
                                          # the XVF3000 chip name doesn't appear in it at all
SAMPLE_RATE = 16000         # sample rate diart/pyannote expect
CHANNEL_INDEX = 0           # channel 0 = cleaned, voice-focused audio, per Seeed's documented
                             # layout for this device (6 channels total: 0=processed, 1-4=raw
                             # per-mic, 5=AEC playback reference) - confirmed the device exposes
                             # 6 input channels via sd.query_devices(), but channel 0's content
                             # itself hasn't been confirmed by ear yet
BLOCK_SIZE = 1024           # frames per chunk read from the stream


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
            if MIC_NAME_HINT.lower() in dev["name"].lower() and dev["max_input_channels"] > 0:
                return idx
        raise RuntimeError(f"Could not find mic containing '{MIC_NAME_HINT}'")

    def _callback(self, indata, frames, time_info, status):
        # sounddevice calls this on its own thread for every audio block
        if status:
            print(f"[mic_input] stream status: {status}")
        channel0 = indata[:, CHANNEL_INDEX].copy()
        self.audio_queue.put(channel0)

    def start(self):
        # opens and starts the input stream; audio starts flowing into the queue
        self.stream = sd.InputStream(
            device=self.device_index,
            channels=max(CHANNEL_INDEX + 1, 1),
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
        # blocks until the next audio chunk (numpy array) is available
        return self.audio_queue.get(timeout=timeout)
