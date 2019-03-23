import librosa

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
        
class MicPlayer(ChunkPlayer):
    def __init__(self, devices, input_device, sr=48000, target_buffer=6, chunk_size=1024):
        ChunkPlayer.__init__(self,devices,sr)
        self.target_buffer = 6
        self.input_device = input_device
        self.orig_data = numpy.array([],'float32')
        self.proc_data = numpy.zeros(target_padding, dtype=self.orig_data.dtype)
        self.chunk_size = chunk_size
        self.jkl = int(chunk_size / 4)
        self._speed = 1.0
        self.pitch_shift = 0
        
        def callback(indata, frames, time, status):#
            self.orig_data = numpy.concatenate((self.orig_data ,indata[:,0] ))
        self.in_stream = InputStream(device=self.input_device,blocksize=chunk_size,samplerate=sr,channels=1,dtype='float32', callback = callback) 
        time.sleep(1)
        self.start_playint()
    
    def _init_stretching(self):
        self.orig_index = 0
        self.proc_index = 0
        
        self._taper_mod = numpy.hanning(chunk_size)
        self._angle = numpy.zeros(self.chunk_size, dtype=self.orig_data.dtype)
        self.proc_data = numpy.zeros(target_padding, dtype=self.orig_data.dtype)

        self._zero_padding()

    def _zero_padding(self):
        padding = int(numpy.ceil(self.chunk_size * target_buffer / self.speed + self.chunk_size) - len(self.chunk_size))
         if padding > 0:
            self.proc_data = numpy.concatenate((self.proc_data, numpy.zeros(padding, dtype=self._sy.dtype)))
        
    @property
    def speed(self):
        return self._speed

    @stretch_factor.setter
    def speed(self, value):
        self._speed = value
        self._zero_padding()

    @property
    def playing(self):
        """ Whether the sound is currently played. """
        return self._playing

    @playing.setter
    def playing(self, value):
        if not self._playing and value:
            start_playing(self)
        self._playing = value

    def start_playing(self):
        def thread_target():
            streams = []
            for d in self.devices:
                streams.append(self.OutputStream(samplerate=self.sr, device=d, channels=1, blocksize=self.chunk_size, dtype='float32').__enter__())
            try:
                while self.playing:
                     chunk = self._next_chunk()
                     [s.write(chunk) for s in streams]
            except:
                [s.__exit__() for s in streams]
            
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

    def _next_chunk(self):
        if self.orig_data.size >= self.chunk_size:
            chunk = self._time_stretcher(self.stretch_factor)

            if numpy.round(self.pitch_shift, 1) != 0:
                chunk = self.pitch_shifter(chunk, self.pitch_shift)

            return chunk

        print('_next_chunk empty')
        return numpy.array([],'float32')

    def _time_stretcher(self, stretch_factor):
        """ Real time time-scale without pitch modification.

            :param int i: index of the beginning of the chunk to stretch
            :param float stretch_factor: audio scale factor (if > 1 speed up the sound else slow it down)

            .. warning:: This method needs to store the phase computed from the previous chunk. Thus, it can only be called chunk by chunk.

        """
        #print('_time_stretcher')
        self.orig_data = self._chunks[self.orig_index + max(0,self.orig_index-self.chunk_size):]

        
        self.proc_data = self.proc_data[self.chunk_size:]
        sy_size_increase = int((self.chunk_size / self.speed * self.target_buffer - self.proc_data.size)
        if sy_size_increase > 0:
            self._sy = numpy.concatenate((self._sy, numpy.zeros(sy_size_increase+64, dtype=self.proc_data.dtype)))

        
        self.proc_index = 0
        self.orig_index = 0
        start = self.proc_index
        end = self.proc_index + self.chunk_size
                               
        if start >= end:
            raise StopIteration

        # The not so clean code below basically implements a phase vocoder
        out = numpy.zeros(self.chunk_size, dtype=numpy.complex)

        while self.proc_size < end:
            
            if (self.chunk_size + self.jkl)/max(self.speed,1) > self.orig_data.size:
                print('CUTOUT')
                return numpy.array([],'float32') 
            
            a, b = self.orig_data,self.orig_data+self.chunk_size
            #print(self._win.size,a,b)
            S1 = numpy.fft.fft(self._taper_mod * self.orig_data[a: b])
            S2 = numpy.fft.fft(self._taper_mod * self.orig_data[a + self.chunk_size: b + self.jkl])

            self._angle += (numpy.angle(S2) - numpy.angle(S1))
            self._angle = self._angle - 2.0 * numpy.pi * numpy.round(self._angle / (2.0 * numpy.pi))

            out.real, out.imag = numpy.cos(self._angle), numpy.sin(self._angle)
            self._sy[self.proc_index: self.proc_index + self.chunk_size] += self._taper_mod * numpy.fft.ifft(numpy.abs(S2) * out).real

            self._i1 += int(self.jkl * self.speed)
            self._i2 += self.jkl

        chunk = self.proc_data[start:end]
        
        return chunk

mp = MicPlayer(('CABLE-A Input (VB-Audio Cable A, MME','CABLE-B Input (VB-Audio Cable B, MME'),'Microphone (Blue Snowball), MME')

