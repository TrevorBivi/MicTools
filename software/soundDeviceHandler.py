import sounddevice as sd
import time
from functools import partial
import threading
import numpy
assert numpy


def unbound_callback(sh, indata, outdata, frames, time, status):
    if status:
        print(status)
    outdata[:] = indata * sh.volume

class SoundHandler(object):
    def start(self,doRestart = False):
        def thread_target():
            with sd.Stream(device=(self.input_device, self.output_device), samplerate=self.sample_rate,
                      blocksize=self.block_size, dtype=self.dtype, latency=self.latency,
                      channels=self.channels, callback=self.callback):
                while self.streaming:
                    time.sleep(0.66)
        if doRestart and self.streaming:
            self.stop()
            self.time.sleep(0.75)
            self.start()
        elif not self.streaming:
            self.streaming = True
            thread = threading.Thread(target=thread_target)
            thread.start()

    def stop(self):
        self.streaming = False

    def __init__(self,input_device=None, output_device=None, sample_rate=None,
                      block_size=None, dtype=None, latency=None,
                      channels=None, callback=None,volume=1):
        self.streaming = False
        self.volume = volume
    
        self.input_device = input_device
        self.output_device = output_device

        self.sample_rate = sample_rate
        self.block_size = block_size
        self.dtype = dtype
        
        self.latency = latency
        self.channels = channels
        self.callback = unbound_callback if callback else partial(unbound_callback,self)
    
