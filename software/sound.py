from abc import abstractmethod
import numpy

class Sound(object):
    def __init__(self, sr=44100, chunk_size=1024, target_buffer = 6):
        self.sr = sr
        self.chunk_size = chunk_size
        
        self.target_buffer = target_buffer
        self.speed_data = numpy.zeros(target_buffer, dtype=self.data.dtype)
        
        self._index = 0
        self._pitch = 1.0
        self._speed = 1.0
        self._volume = 1.0

        self.y = self.data

        self._init_stretching()
        
    
    @abstractmethod
    def next_chunk():
        pass

    @property
    def volume(self):
        return self._volume
    
    @volume.setter
    def volume(self,vol):
        self._volume = vol

    @property
    def speed(self):
        return self._speed
    
    @speed.setter
    def speed(self,speed):
        print('SPEED SET')
        self._speed = speed
        self._zero_padding()
        
    @property
    def pitch(self):
        return self._pitch
    
    @pitch.setter
    def pitch(self,pitch):
        self._pitch = pitch

    def pitch_shift_chunk(self, chunk, shift):
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


    def speed_shift_chunk(self, speed):
        """ Real time time-scale without pitch modification.
            :param int i: index of the beginning of the chunk to stretch
            :param float stretch_factor: audio scale factor (if > 1 speed up the sound else slow it down)
            .. warning:: This method needs to store the phase computed from the previous chunk. Thus, it can only be called chunk by chunk.
        """
        start = self.get_data_index()
        curr = start
        shift_index = self.get_shifted_index()
        
        end = min(curr + self._N, len(self._sy) - (self._N + self._H))

        #print('start',start,'shift ind',shift_index)

        if start >= end:
            self.out_of_chunks_action()

        # The not so clean code below basically implements a phase vocoder
        out = numpy.zeros(self._N, dtype=numpy.complex)

        while curr < end:
            #print('CUR > end')
            if shift_index + self._N + self._H > len(self.data):
                self.out_of_chunks_action()

            a, b = shift_index, shift_index + self._N
            S1 = numpy.fft.fft(self._win * self.data[a: b])
            S2 = numpy.fft.fft(self._win * self.data[a + self._H: b + self._H])

            self._phi += (numpy.angle(S2) - numpy.angle(S1))
            self._phi = self._phi - 2.0 * numpy.pi * numpy.round(self._phi / (2.0 * numpy.pi))

            out.real, out.imag = numpy.cos(self._phi), numpy.sin(self._phi)

            self._sy[curr: curr + self._N] += self._win * numpy.fft.ifft(numpy.abs(S2) * out).real

            shift_index += int(self._H * self.speed)
            curr += self._H



        if speed == 1.0:
            chunk = self.data[shift_index: min( shift_index + self._N, len(self.data) - self._N - self._H  ) ]
        else:
            chunk = self._sy[start:end]

        self.set_data_index(curr)
        self.set_shifted_index(shift_index)
        
        return chunk        
