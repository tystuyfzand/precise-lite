import numpy as np
from os.path import join
from precise_lite_runner import PreciseRunner
from precise_lite_runner.runner import ListenerEngine
from prettyparse import Usage
from random import randint
from shutil import get_terminal_size
from threading import Event

from precise_lite.network_runner import Listener
from precise_lite.scripts.base_script import BaseScript
from precise_lite.util import save_audio, buffer_to_audio, activate_notify


class ReadWriteStream:
    """
    Class used to support writing binary audio data at any pace,
    optionally chopping when the buffer gets too large
    """
    def __init__(self, s=b'', chop_samples=-1):
        self.buffer = s
        self.write_event = Event()
        self.chop_samples = chop_samples

    def __len__(self):
        return len(self.buffer)

    def read(self, n=-1, timeout=None):
        if n == -1:
            n = len(self.buffer)
        if 0 < self.chop_samples < len(self.buffer):
            samples_left = len(self.buffer) % self.chop_samples
            self.buffer = self.buffer[-samples_left:]
        return_time = 1e10 if timeout is None else (
                timeout + time.time()
        )
        while len(self.buffer) < n:
            self.write_event.clear()
            if not self.write_event.wait(return_time - time.time()):
                return b''
        chunk = self.buffer[:n]
        self.buffer = self.buffer[n:]
        return chunk

    def write(self, s):
        self.buffer += s
        self.write_event.set()

    def flush(self):
        """Makes compatible with sys.stdout"""
        pass


class PreciseLiteListener:
    def __init__(self, model, chunk_size, trigger_level, sensitivity,
                 on_activation=None, on_prediction=None):
        on_activation = on_activation or self.on_activation
        on_prediction = on_prediction or self.on_prediction
        self.listener = Listener(model, chunk_size)
        self.audio_buffer = np.zeros(self.listener.pr.buffer_samples, dtype=float)
        self.engine = ListenerEngine(self.listener, chunk_size)
        self.engine.get_prediction = self.get_prediction
        self.runner = PreciseRunner(self.engine, trigger_level,
                                    sensitivity=sensitivity,
                                    on_activation=on_activation,
                                    on_prediction=on_prediction)

    def on_activation(self):
        print("     precise-lite activation!!!")

    def on_prediction(self, conf):
        pass

    def get_prediction(self, chunk):
        audio = buffer_to_audio(chunk)
        self.audio_buffer = np.concatenate((self.audio_buffer[len(audio):], audio))
        return self.listener.update(audio)

    def start(self):
        self.runner.start()
