import sounddevice as sd
import numpy
assert numpy


class SoundHandler(object):

    @staticmethod
    def callback(indata, outdata, frames, time, status):
        if status:
            print(status)
        outdata[:] = indata
    
    def __init__(input_device,output_device,
            sample_rate=None,block_size=None,dtype=None,
            latency=None,channels=None,callback=SoundHandler.callback):

        self.inputDevice = inputDevice
        self.outputDevice = outputDevice
        self.stream = sd.Stream(


    self,voiceToMic=True, sfxToMic=True,
        ttsToSpeakers=True, voiceToSpeakers=True, sfxToSpeakers=True,
        micInputDevice='Microphone (Blue Snowball), Windows WASAPI',
        micOutputDevice='18 CABLE-A Output (VB-Audio Cable A), Windows WASAPI',
        speakerDevice='Speakers (High Definition Audio Device), Windows WASAPI'):

        self.        



def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    outdata[:] = indata

try:
    
    with sd.Stream(callback=callback):
        print('#' * 80)
        print('press Return to quit')
        print('#' * 80)
        input()
        
except KeyboardInterrupt:
    print('\nInterrupted by user')
except Exception as e:
    print(type(e).__name__ + ': ' + str(e))
