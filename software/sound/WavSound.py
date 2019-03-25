from __future__ import division

import numpy
import librosa


class Sound(object):
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

        self.orig_index = 0
        self.proc_index = 0
        self.orig_data, self.sr = orig_data.astype(dtype='float32'), sr
        self.proc_data = orig_data[:]
        
        self._pitch = 0
        self._speed = 1.0
        self.vol = 100
        
    @classmethod
    def from_file(cls, filename, sr=48000, orig_sr=None):
        """ Loads an audiofile, uses sr=22050 by default. """
        orig_data, sr = librosa.load(filename, sr=orig_sr)

        if orig_sr and orig_sr != sr:
            orig_data = librosa.core.resample(orig_data, orig_sr, sr)
            
        #y = t#librosa.effects.pitch_shift(t, 48000, -5, 24)
        return cls(orig_data, sr)

    def set_morphing(self,pitch,speed):
        orig_index = self.orig_index
        proc_data = self.orig_data[orig_index:]
        if speed and speed != 1:
            if speed < 0.1: # assume the entire song won't be played while at a really low speed
                proc_data = librosa.effects.time_stretch(orig_data[:int(self.sr * 240 * speed)], speed)
            else:
                proc_data = librosa.effects.time_stretch(orig_data, speed)
            
        if pitch and pitch != 0:
            proc_data = librosa.effects.pitch_shift(t, 48000, pitch)

        orig_index_change = self.orig_index - orig_index
        self.proc_data = proc_data[orig_index_change:]
        
        if orig_index_change:
            print('this is maybe useful!')

    def next_chunk(self):
        self.orig_index += int(self.chunk_size * self.speed)
        chunk = self.proc_data[:self.chunk_size]
        self.proc_data = self.proc_data[self.chunk_size:]
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
        self_morphing(self.pitch,self.speed)

    @property
    def speed(self):
        return self._speed

    @stretch_factor.setter
    def speed(self, value):
        self._speed = value
        self_morphing(self.pitch,self.speed)

    
