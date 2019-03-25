import librosa
import numpy
from sounddevice import OutputStream, InputStream
import time
from threading import Condition, Event, Thread


class ChunkPlayer(object):
    def __init__(self,devices,sr=48000):
        self.devices = devices
        self.sr = sr
        
class WavPlayer(ChunkPlayer):
    def __init__(self,devices,sr=48000,**kwargs):
        ChunkPlayer.__init__(self,devices,sr)
        if 'data' in kwargs:
            self.orig_data = kwargs['data']
        elif 'path' in kwargs:
            self.orig_data = librosa.load(kwargs['path'],sr)[0]
        self.proc_data = numpy.array([],'float32')
        
class MicSound(ChunkPlayer):
    def __init__(self, devices, input_device, sr=48000, target_buffer=6, chunk_size=1024):
        ChunkPlayer.__init__(self,devices,sr)
        self.target_buffer = target_buffer
        self.input_device = input_device
        self.orig_data = numpy.array([],'float32')
        self.proc_data = numpy.zeros(target_buffer, dtype=self.orig_data.dtype)
        self.chunk_size = chunk_size
        self.jkl = int(chunk_size / 4)
        self._speed = 1.0
        self.pitch_shift = 0
        self.orig_index = 0
        self.proc_index = 0
        
        def callback(indata, frames, time, status):#
            self.orig_data = numpy.concatenate((self.orig_data ,indata[:,0] ))
        self.in_stream = InputStream(device=self.input_device,blocksize=chunk_size,samplerate=sr,channels=1,dtype='float32', callback = callback) 
        self.in_stream.start()
        time.sleep(target_buffer * chunk_size / sr)
        self._playing = False
        self.playing = True
        
    
    def _init_stretching(self):
        self.orig_index = 0
        self.proc_index = 0
        
        self._window = numpy.hanning(self.chunk_size)
        self._angle = numpy.zeros(self.chunk_size, dtype=self.orig_data.dtype)
        self.proc_data = numpy.zeros(self.target_buffer, dtype=self.orig_data.dtype)

        self._zero_padding()

    def _zero_padding(self):
        padding = int(numpy.ceil(self.chunk_size * self.target_buffer / self.speed + self.chunk_size) - len( self.proc_data))
        if padding > 0:
            self.proc_data = numpy.concatenate((self.proc_data, numpy.zeros(padding, dtype=self.proc_data.dtype)))
        
    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value
        self._zero_padding()

    @property
    def playing(self):
        """ Whether the sound is currently played. """
        return self._playing

    @playing.setter
    def playing(self, value):
        old_val = self._playing
        self._playing = value
        if not old_val and value:
            self.start_playing()
        

    def start_playing(self):
        self._init_stretching()
        def thread_target():
            streams = []
            for d in self.devices:
                streams.append(OutputStream(samplerate=self.sr, device=d, channels=1, blocksize=self.chunk_size, dtype='float32').__enter__())
            try:
                while self.playing:
                    print(streams)
                    chunk = self.next_chunk()
                    [s.write(chunk) for s in streams]
            except Exception as err:
                print('playing error')
                [s.__exit__() for s in streams]
                raise err

        self.play_thread = Thread(target=thread_target)
        self.play_thread.daemon = True
        self.play_thread.start()
            
    def pitch_shifter(self, chunk, shift):
        """ Pitch-Shift the given chunk by shift semi-tones. """
        freq = numpy.fft.rfft(chunk,self.chunk_size)
        
        N = len(freq)
        shifted_freq = numpy.zeros(N, freq.dtype)

        S = numpy.round(shift if shift > 0 else N + shift, 0)
        s = N - S

        shifted_freq[:S] = freq[s:]
        shifted_freq[S:] = freq[:s]

        shifted_chunk = numpy.fft.irfft(shifted_freq)

        return shifted_chunk.astype(chunk.dtype)

    def next_chunk(self):
        if self.orig_data.size >= self.chunk_size:
            chunk = self._time_stretcher(self.speed)

            if numpy.round(self.pitch_shift, 1) != 0:
                chunk = self.pitch_shifter(chunk, self.pitch_shift)

            return chunk

        print('_next_chunk empty')
        return numpy.array([],'float32')

    def _time_stretcher(self, speed):
        """ Real time time-scale without pitch modification.

            :param int i: index of the beginning of the chunk to stretch
            :param float speed: audio scale factor (if > 1 speed up the sound else slow it down)

            .. warning:: This method needs to store the phase computed from the previous chunk. Thus, it can only be called chunk by chunk.

        """
        #print('_time_stretcher')
        self.orig_data = self.orig_data[self.orig_index + max(0,self.orig_index-self.chunk_size):]

        
        self.proc_data = self.proc_data[self.chunk_size:]
        if self.orig_data.size < self.target_buffer * self.chunk_size:
            self.speed = min(self.speed,1.0)
            
        sy_size_increase = int(self.chunk_size / self.speed * self.target_buffer - self.proc_data.size)
        if sy_size_increase > 0:
            self.proc_data = numpy.concatenate((self.proc_data, numpy.zeros(sy_size_increase+64*1024, dtype=self.proc_data.dtype)))

        
        self.proc_index = 0
        self.orig_index = 0
        start = self.proc_index
        end = self.proc_index + self.chunk_size
                               
        if start >= end:
            raise StopIteration

        # The not so clean code below basically implements a phase vocoder
        out = numpy.zeros(self.chunk_size, dtype=numpy.complex)

        while self.proc_index < end:
            
            if (self.chunk_size + self.jkl)/max(self.speed,1) > self.orig_data.size:
                print('CUTOUT')
                return numpy.array([],'float32') 
            
            a, b = self.orig_index, self.orig_index+self.chunk_size
            #print(self._win.size,a,b)
            S1 = numpy.fft.fft(self._window * self.orig_data[a: b])
            S2 = numpy.fft.fft(self._window * self.orig_data[a + self.jkl: b + self.jkl])

            self._angle += (numpy.angle(S2) - numpy.angle(S1))
            self._angle = self._angle - 2.0 * numpy.pi * numpy.round(self._angle / (2.0 * numpy.pi))

            out.real, out.imag = numpy.cos(self._angle), numpy.sin(self._angle)
            self.proc_data[self.proc_index: self.proc_index + self.chunk_size] += self._window * numpy.fft.ifft(numpy.abs(S2) * out).real

            self.orig_index += int(self.jkl * self.speed)
            self.proc_index += self.jkl

        chunk = self.proc_data[start:end]
        
        return chunk
    

ms = MicSound(('CABLE-A Input (VB-Audio Cable A, MME','CABLE-B Input (VB-Audio Cable B, MME'),'Microphone (Blue Snowball), MME')
ms.speed = 3
