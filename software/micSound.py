import librosa
import numpy
from sounddevice import OutputStream, InputStream
import time
from threading import Condition, Event, Thread

from sound import *

class MicSound(Sound):
    def __init__(self, devices, input_device, sr=44100,target_buffer=6, chunk_size=1024):
        self.target_buffer = target_buffer
        self.input_device = input_device
        self.data = numpy.array([],'float32')
        self.chunk_size = chunk_size
        self._speed = 0.5
        self.pitch_shift = 0
        self.orig_index = 0
        self.proc_index = 0
        self.devices = devices
        self.sr = sr
        
        def callback(indata, frames, time, status):#
            self.data = numpy.concatenate((self.data ,indata[:,0] ))
        self.in_stream = InputStream(device=self.input_device,blocksize=chunk_size,samplerate=sr,channels=1,dtype='float32', callback = callback) 
        self.in_stream.start()
        self._playing = False
        Sound.__init__(self,sr,chunk_size,target_buffer)
        self.playing = True

        self.buffering = False

    def play_self(self):
        def thread_target():
            streams = []
            for d in self.devices:
                streams.append(OutputStream(samplerate=self.sr, device=d, channels=1, blocksize=self.chunk_size, dtype='float32').__enter__())
            try:
                while self.playing:
                    #print(streams)
                    chunk = self.next_chunk()
                    if not chunk is None and chunk.size > 1:
                        [s.write(chunk) for s in streams]
            except Exception as err:
                print('playing error')
                [s.__exit__() for s in streams]
                raise err

        play_thread = Thread(target=thread_target)
        play_thread.daemon = True
        play_thread.start()

    def _init_stretching(self):
        # Resp. index of current audio chunk and computed phase
        self._i1, self._i2 = 0, 0
        self._N, self._H = self.chunk_size, int(self.chunk_size / 4)

        self._win = numpy.hanning(self._N)
        self._phi = numpy.zeros(self._N, dtype=self.data.dtype)
        self._sy = numpy.zeros(self.sr, dtype=self.data.dtype)

        self._zero_padding()

    def _zero_padding(self):
        if len(self._sy) < self.target_buffer * self.chunk_size:
            self._sy = numpy.concatenate((self._sy,
                                          numpy.zeros(self.sr, dtype=self._sy.dtype)))


    def get_data_index(self):
        return 0

    def set_data_index(self, index):
        #sprint('set ind',index)
        self._sy = self._sy[index:]
        self._zero_padding()
        #self.data[int(index * self.speed):]

    def get_shifted_index(self):
        return 0

    def set_shifted_index(self, index):
        #print('set sh ind', index)
        self.data = self.data[index:]

    def out_of_chunks_action(self):
        print('OUT OF CHUNKS')
        #self.speed = 1.0
        self.data = numpy.concatenate((numpy.zeros(self.chunk_size * 4, dtype=self._sy.dtype),
                                       self.data))
        

    def next_chunk(self):
        print('nxt ch' + str( len(self.data)) + ' sy:' + str(len(self._sy)))
        if self.buffering:
            return None
        
        if self._sy.size > ((self.chunk_size * 1.25) * self.speed):
            #self.data = self.data[self.chunk_size:]
            chunk = self.speed_shift_chunk(self.speed)
            if self.pitch != 1.0:
                print('PITCHJ SHITF')
                chunk = self.pitch_shift_chunk(chunk, int(self.pitch * 10) - 10)

            return chunk * self.volume

        print('_next_chunk empty')
        return None

if __name__ == '__main__':    
    ms = MicSound(('Speakers (2- High Definition Au, MME',),'Microphone (Blue Snowball), MME')
    #ms.pitch = 5.0
    print('self.speed',ms.speed)
    ms.speed = 0.4
    ms.pitch = 0.5
    ms.volume = 0.6
    ms.play_self()
