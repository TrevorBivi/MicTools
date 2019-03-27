from __future__ import division

import numpy
import librosa
from multiprocessing import Process
from threading import Condition, Event, Thread
import time
from sounddevice import OutputStream

import sys
sys.path.append('../other/')

from ThreadWithExc import ThreadWithExc, _async_raise

#from './ThreadWithExec.py' import ThreadWithExec

class EndResampleThread(Exception):
    pass

def resample_proc(self):
    orig_index = self.orig_index
    pitch_data = self.orig_data[orig_index:]
    
    if self.pitch == 1:
        pitch_data = self.orig_data[self.orig_index:]
    else:
        t1 = time.time()
        pitch_data = librosa.core.resample(self.orig_data[self.orig_index:],self.sr,self.sr / self._pitch)  #librosa.effects.pitch_shift(pitch_data, 48000, pitch)
        print('pitch time',time.time()-t1)

    self._resample_thread = None
    orig_index_change = self.orig_index - orig_index
    self.pitch_data = pitch_data[int(orig_index_change):]
    self.pitch_index = 0
    self._resampled_speed = self.speed / self.pitch
    print('CREATED RESAMPLED PITCH')
    
    if orig_index_change:
        print('this is maybe useful!')


class WavSound(object):
    """ Sound object which can be read chunk by chunk. """

    def __init__(self, orig_data, sr, chunk_size=1024):
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
        self.chunk_size = chunk_size
        self.jkl = int(chunk_size/4)
        self.sr = sr
        self.devices = ('CABLE-A Input (VB-Audio Cable A, MME','CABLE-B Input (VB-Audio Cable B, MME')
        self.orig_index = 0
        self.orig_data = orig_data
        self.pitch_data = orig_data[:]
        self._playing = True

        #the actual speed for the phase vocoder to playback audio at after adjusting for resampling to increase pitch
        #If None then program is using a fallback real time pitch adjustment using orig_data
        #A thread automatically generates the artifactless resampled pitch_data when the pitch is changed        
        self._resampled_speed = None
        self._resample_proc = None

        self.proc_index = 0
        self.orig_index = 0
        
        self._pitch = 1.0
        self._speed = 1.0 # desired speed by user
        self.vol = 100
        self._init_stretching()

    def _init_stretching(self):
        self.orig_index = 0
        self.played_count = 0
        
        self._window = numpy.hanning(self.chunk_size)
        self._angle = numpy.zeros(self.chunk_size, dtype=self.orig_data.dtype)
        self.proc_data = numpy.zeros(len(self.pitch_data), dtype=self.orig_data.dtype)

        self._zero_padding()

    def _zero_padding(self):
        padding = int(numpy.ceil(len(self.pitch_data) / self.speed + self.chunk_size) - len(self.proc_data))
        if padding > 0:
            self.proc_data = numpy.concatenate((self.proc_data,
                                          numpy.zeros(padding, dtype=self.proc_data.dtype)))

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
                    [s.write(chunk) for s in streams]
            except Exception as err:
                print('playing error')
                [s.__exit__() for s in streams]
                raise err

        play_thread = Thread(target=thread_target)
        play_thread.daemon = True
        play_thread.start()
        
    @classmethod
    def from_file(cls, filename, sr=48000, orig_sr=None,chunk_size=1024):
        """ Loads an audiofile, uses sr=22050 by default. """
        orig_data, sr = librosa.load(filename, sr=orig_sr)

        if orig_sr and orig_sr != sr:
            orig_data = librosa.core.resample(orig_data, orig_sr, sr, chunk_size)
            
        #y = t#librosa.effects.pitch_shift(t, 48000, -5, 24)
        return cls(orig_data, sr)

    def next_chunk(self):
        #self.orig_index += int(self.chunk_size * self.speed)
        chunk = self._time_stretcher()#self.proc_data[:self.chunk_size]
        if self._resampled_speed == None:
            print('live pitch mod')
            chunk = self.fallback_pitch_shifter(chunk,int(self.speed * 10))
        else: print('_time stretcher modified resampled data')
        return chunk

    def fallback_pitch_shifter(self, chunk, shift):
            """ Pitch-Shift the given chunk by shift semi-tones. """
            freq = numpy.fft.rfft(chunk)

            N = len(freq)
            shifted_freq = numpy.zeros(N, freq.dtype)

            S = numpy.round(shift if shift > 0 else N + shift, 0)
            s = N - S

            shifted_freq[:S] = freq[s:]
            shifted_freq[S:] = freq[:s]

            shifted_chunk = numpy.fft.irfft(shifted_freq)

            return shifted_chunk.astype(chunk.dtype)


    def _time_stretcher(self):
        """ Real time time-scale without pitch modification.

            :param int i: index of the beginning of the chunk to stretch
            :param float speed: audio scale factor (if > 1 speed up the sound else slow it down)

            .. warning:: This method needs to store the phase computed from the previous chunk. Thus, it can only be called chunk by chunk.

        """
        #print('_time_stretcher')
        #self.orig_data = self.orig_data[self.orig_index + max(0,self.orig_index-self.chunk_size):]
            
        #self.proc_index = 0
        #self.proc_data = self.proc_data[self.chunk_size:]
        
        #self.orig_index = 0

        if self._resampled_speed:
            used_data = self.pitch_data
            i1 = 0
            i2 = 0
            speed = self._resampled_speed
        else:
            used_data = self.orig_data
            i1 = self.orig_index
            i2 = self.proc_index
            speed = self.speed
        
        start = i1
        end = min(i1 + self.chunk_size, len(used_data) - self.chunk_size + self.jkl)
                               
        if start >= end:
            raise StopIteration

        # The not so clean code below basically implements a phase vocoder
        out = numpy.zeros(self.chunk_size, dtype=numpy.complex)
        
        while self.proc_index < end:    
            if (self.chunk_size + self.jkl)/max(self.speed,1) > used_data.size:
                print('CUTOUT')
                return numpy.array([],'float32') 
            
            a, b = i1, i1+self.chunk_size
            #print(self._win.size,a,b)
            S1 = numpy.fft.fft(self._window * used_data[a: b])
            S2 = numpy.fft.fft(self._window * used_data[a + self.jkl: b + self.jkl])

            self._angle += (numpy.angle(S2) - numpy.angle(S1))
            self._angle = self._angle - 2.0 * numpy.pi * numpy.round(self._angle / (2.0 * numpy.pi))

            out.real, out.imag = numpy.cos(self._angle), numpy.sin(self._angle)
            self.proc_data[i2: i2 + self.chunk_size] += self._window * numpy.fft.ifft(numpy.abs(S2) * out).real

            self.orig_index += int(self.jkl * speed)
            #self.i2 += int(self.jkl * speed)
            self.proc_index += self.jkl

        #self.orig_index += int(self.chunk_size * speed)
        if self._resampled_speed:
            return self.proc_data[start:end]
        else:
            return self.orig_data[start:end]
            #make use orig if not modifying
        return chunk
    
    # Chunk iterator
    @property
    def playing(self):
        """ Whether the sound is currently played. """
        return self._playing

    @playing.setter
    def playing(self, value):
        self._playing = value

    @property
    def pitch(self):
        return self._pitch

    @pitch.setter
    def pitch(self,value):
        self._pitch = value

        if self._resample_proc and self._resample_proc.is_alive():
            print('end resample_thread')
            self._resample_proc.terminate()
            #_async_raise(self._resample_thread._get_my_tid(), EndResampleThread())
        self._resample_proc = Process(target=resample_proc,args=(self,))
        self._resample_proc.daemon = True
        self._resample_proc.start()
    
        
    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value
        self._real_speed = self.speed / self.pitch
        self._zero_padding()
        #self.set_morphing(self.pitch,value)

ws = WavSound.from_file("C:\\Users\\Trevor\\Documents\\aupyom\\aupyom\\example_data\\Tom's Dinner.wav")
ws.play_self()
time.sleep(1)
print('morph')
for i in range(1):
    time.sleep(0.07)
    ws.pitch -= 0.1
    
