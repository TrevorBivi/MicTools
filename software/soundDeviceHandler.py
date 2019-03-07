'''
ABOUT:
Contains class for bridging audio from an input to output device and recording audio from an input or output device

IMPORTANT CLASSES:
SoundHandler -- handles connection from an input to output device
Recorder -- records and stores audio from an input device or WASAPI input device

IMPORT METHOS:
getDeviceIndex -- return the index of a device host api by name
getDeviceIndex -- return the index of a device by name

TODO:
 - make SoundHandler use Intxcc's pyaudio branch instead of sounddevice to decrease the required dependencies
'''

import sounddevice as sd

# Note: this requires Intxcc's pyaudio branch!
# it allows recording output audio from the soundcard
# https://github.com/intxcc/pyaudio_portaudio
import pyaudio
import time
from functools import partial
import threading
import numpy
assert numpy

p = pyaudio.PyAudio()

defaultframes = 512

def get_host_api(host_api_name):
    for i in range(p.get_host_api_count()):
        print('some host')
        info = p.get_host_api_info_by_index(i)
        if info['name'] == host_api_name:
            print('info name', info)
            return info

def get_device(device_name, host_api_name=None, host_api_index=None):
    if host_api_name:
        host_api_index = get_host_api(host_api_name)['index']
    elif not host_api_index:
       raise TypeError('host_api_name or host_api_index should be degined')
    
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['name'] == device_name and info['hostApi'] == host_api_index:
            return info['index']

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


class Recorder(object):
    def __init__(self,device_name='Speakers (High Definition Audio Device)',host_api_name='Windows WASAPI',
                 pre_rec_len=5):

        self.host_api_info = get_host_api(host_api_name)
        self.device_info = get_device(device_name,self.host_api_info['index'])
        self.pre_rec_len = pre_rec_len
        self.frames = []
        self.record()
        self.extend_record = True
        
    def record(self):
        def thread_target():
            stream = p.open(format = pyaudio.paInt16,
                channels = channelcount,
                rate = int(self.device_info["defaultSampleRate"]),
                input = True,
                frames_per_buffer = defaultframes,
                input_device_index = self.device_info["index"],
                as_loopback = useloopback)
            while True:            
                self.frames.append(stream.read(defaultframes))

                if not self.extend_record:
                    self.frames = self.frames[  -500:]
                
        thread = threading.Thread(target=thread_target)
        thread.start()

    def write_recorded(self):
        sd.play(data, fs, device='Speakers (High Definition Audio, MME')
        

        
    #def take_audio():
