from __future__ import division

import numpy
import librosa
from multiprocessing import Process, Pipe
from threading import Condition, Event, Thread
import time
from sounddevice import OutputStream

import sys
from sound import *

#from ThreadWithExc import ThreadWithExc, _async_raise

#from './ThreadWithExec.py' import ThreadWithExec
class WavSound(Sound):
    """ Sound object which can be read chunk by chunk. """

    def __init__(self, data, devices, sr=44100, chunk_size=1024, target_buffer = 6, name = 'unknown'):
        """
        :param array y: numpy array representing the audio data
        :param int sr: samplerate
        :param int chunk_size: size of each chunk (default 1024)

        You also have access two properties:
            * pitch_shift (real time pitch shifting)
            * time_stretch (real time time-scale without pitch modification)
            * volume (real time volume level)

        Both can be tweaked simultaneously.

        """
        
        self.devices = devices # ['Speakers / Headphones (IDT High, MME']#
        self.data = data
        self.playing = True
        self.index = 0
        self.name = name
        
        Sound.__init__(self,sr,chunk_size,target_buffer)

    def _zero_padding(self):
        padding = int(numpy.ceil(len(self.y) / self.speed + self._N) - len(self._sy))
        if padding > 0:
            self._sy = numpy.concatenate((self._sy,
                                          numpy.zeros(padding, dtype=self._sy.dtype)))

    def _init_stretching(self):
        # Resp. index of current audio chunk and computed phase
        self._i1, self._i2 = 0, 0
        self._N, self._H = self.chunk_size, int(self.chunk_size / 4)

        self._win = numpy.hanning(self._N)
        self._phi = numpy.zeros(self._N, dtype=self.y.dtype)
        self._sy = numpy.zeros(len(self.y), dtype=self.y.dtype)

        padding = int(numpy.ceil(len(self.y) / self.speed + self._N))
        self._sy = numpy.concatenate((self._sy,
                                          numpy.zeros(padding, dtype=self._sy.dtype)))

    def next_chunk(self):
        if not self.playing:
            raise StopIteration
        ret = self.speed_shift_chunk(self.speed)
        if self.pitch != 1.0:
            ret = self.pitch_shift_chunk(ret,int(self.pitch * 10) - 9)
        print('VOL',self.volume)
        return ret * self.volume

    def get_data_index(self):
        return self._i2

    def set_data_index(self, amount):
        self._i2 = amount

    def get_shifted_index(self):
        return self._i1

    def set_shifted_index(self,index):
        self._i1 = index
  
    @classmethod
    def from_file(cls, filename, devices=['Speakers (2- High Definition Au, MME'], sr=44100, orig_sr=None,chunk_size=1024):
        """ Loads an audiofile, uses sr=22050 by default. """
        orig_data, sr = librosa.load(filename, sr=orig_sr)
        print('len dat',orig_data)
        if orig_sr and orig_sr != sr:
            orig_data = librosa.core.resample(orig_data, orig_sr, sr, chunk_size)
            
        #y = t#librosa.effects.pitch_shift(t, 44100, -5, 24)
        return cls( orig_data, devices, sr, chunk_size, name = filename.split('/')[-1].split('\\')[-1].split('.')[0] )

    def out_of_chunks_action(self):
        raise StopIteration

    def play_self(self):
        def thread_target():
            streams = []
            for d in self.devices:
                streams.append(OutputStream(samplerate=self.sr, device=d, channels=1, blocksize=self.chunk_size, dtype='float32').__enter__())
            try:
                print('playing')
                while self.playing:
                    #print(streams)
                    chunk = self.next_chunk()
                    #print('pst',type(chunk))
                    [s.write(chunk) for s in streams]
            except Exception as err:
                print('playing error')
                [s.__exit__() for s in streams]
                raise err

        play_thread = Thread(target=thread_target)
        play_thread.daemon = True
        play_thread.start()

def generate_sound_library(path, devices):
    import os
    path = os.path.abspath(path)
    print(path)
    CD_list = []
    for CD in os.listdir(path):
        CD_list.append({'name':CD, 'files':[]})
        CD_path = path + '\\' + CD
        print('cd path', CD_path)
        for wav in os.listdir(CD_path):
            print('wav',wav)
            CD_list[-1]['files'].append(WavSound.from_file( CD_path + '\\' + wav, devices = devices))
        
    return CD_list

'''
if __name__ == '__main__':
    ws = WavSound.from_file() #fill in
    print(ws.speed)
    ws.play_self()
    time.sleep(0.5)
    #print('morph')
    for i in range(7):
        time.sleep(1)
    #    ws.pitch += 0.1
        ws.volume = 0.1
        time.sleep(1)
        ws.volume = 1.0'''

    
