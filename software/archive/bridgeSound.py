import numpy
from sounddevice import OutputStream, InputStream
import time
from threading import Condition, Event, Thread

from sound import *

class BridgeSound():
    def __init__(self, devices, input_device, sr=44100,chunk_size=1024):
        self.devices = devices
        self.input_device = input_device
        self.sr = sr
        self.chunk_size = chunk_size
        self.data = numpy.array([],'float32')
    
        def callback(indata, frames, time, status):#
            self.data = numpy.concatenate((self.data ,indata[:,0] ))
        self.in_stream = InputStream(device=self.input_device,blocksize=chunk_size,samplerate=sr,channels=1,dtype='float32', callback = callback) 
        self.in_stream.start()

    def _init_stretching():pass

    def _zero_padding():pass

    def next_chunk(self):
        ret = self.data[:self.chunk_size]
        self.data = self.data[self.chunk_size:]
        return ret
    
