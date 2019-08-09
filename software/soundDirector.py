from __future__ import division

import numpy
import librosa
from multiprocessing import Process, Pipe
from threading import Condition, Event, Thread
import time
from sounddevice import OutputStream

class OutputDevice():
    def __init__(self,name,volume=100, sr = 44100, chunk_size = 1024):
        self.name = name
        self.volume = volume
        self.stream = None
        self.sr = sr
        self.chunk_size = chunk_size

    def write(self,data):
        if not self.stream:
            self.stream = OutputStream(samplerate=self.sr, device=self.name, channels=1, blocksize=self.chunk_size, dtype='float32').__enter__()
        self.stream.write(data)

class SoundDirector():
    def __init__(self, devices, sr=44100, chunk_size = 1024):

        self.sr = sr
        self.chunk_size = chunk_size
        self.devices = devices
        self.sounds = []
        self.play_sounds()
        
    
    def add_sound(self, sound):
        self.sounds.append(sound)

    def remove_sound(self, sound):
        print('REMOVE SOUND')
        try:
            self.sounds.remove(sound)
            return True
        except ValueError:
            return False

    def play_sounds(self):
        def thread_target():
            while True:
                if len(self.sounds):
                    try:
                        sound_chunks = {}
                        sounds = self.sounds[:]

                        removed = 0
                        for i in range(len(sounds)):
                            s = sounds[i-removed]
                            try:
                                sound_chunks[s] = s.next_chunk()
                            except StopIteration:
                                sounds.remove(s)
                                self.remove_sound(s)
                                removed += 1
                                
                        for d in self.devices:
                            stream_chunks = []
                            for s in sounds:
                                #print(s)
                                if d.name in s.devices:
                                    new_chunk = sound_chunks[s]
                                    if type(new_chunk) != type(None):
                                        stream_chunks.append(new_chunk)

                            if len(stream_chunks):
                                d.write(numpy.mean(stream_chunks, axis=0))
                    except Exception as err:
                        print ('ERROR IN PLAY_SOUNDS: ',err)
                        
        play_thread = Thread(target=thread_target)
        play_thread.daemon = True
        play_thread.start()
        
                        
if __name__ == '__main__':
    from wavSound import *
    from micSound import *
    sd = SoundDirector(devices=[OutputDevice('CABLE Input (VB-Audio Virtual C, MME')]) #OutputDevice('Speakers (2- High Definition Au, MME')
    sound = WavSound.from_file("songFiles\\iconic\\seinfield.wav",devices=('CABLE Input (VB-Audio Virtual C, MME',))
    sound.speed = 40.0
    sd.add_sound( sound )
