'''
Play  | Mute/pause | reset

====
cds
===
files
====
vol
pitch
speed

====
====
====
vol
pitch
speed
buffer | release | reset
====
voices
====
playback audio



====




submodes
modes
'''

from wavSound import *
from micSound import *
from morphVoxPro import *

class smooth_trans_value():
    def __init__(self,target_value,trans_speed=0.75,trans_value=None):
        self.trans_value = trans_value
        if trans_value:
            self.trans_time = time.time()
        else:
            self.trans_time = None
        self.target_value = target_value

    def update_value(self, value):
        self.trans_value = self.current_value()
        self.trans_time = time.time()
        self.target_value = value

    def current_value(self):
        progress = (time.time() - self.trans_time) / trans_speed
        if progress >= 1.0:
            self.trans_value = None
            self.trans_time = None

        if not self.trans_value:
            return target_value
        
        change = self.target_value - self.trans_value
        return self.trans_value + progress * change

def default_state():
    return {
        'mode':1,
        'song':{
            'mode':1,
            'CDList':[]
            'CDIndex':None,
            'songIndex':None,
            'playing':False,
            'pitch':smooth_trans_value(1.0),
            'speed':smooth_trans_value(1.0),
            'currentVolume':smooth_trans_value(1.0)
            },
        'board':{
            'mode':1,
            'boardList':[]
            'boardIndex':None,
            'soundIndex':None,
            'playing':False,
            'pitch':smooth_trans_value(1.0),
            'speed':smooth_trans_value(1.0),
            'volume':smooth_trans_value(1.0)
            },
        'microphone':{
            'mode':1,
            'mute':False
            'aupyom':{
                'pitch':smooth_trans_value(1.0),
                'speed':smooth_trans_value(1.0),
                'volume':smooth_trans_value(1.0),
                'buffering':False
                },
            'vox':{
                'voice':None,
                'volume':smooth_trans_value(1.0),
            }
        }
    }

class controller():
    def __init__(self):
        self.state = default_state()

    def update_state(self,key,value):
        key_list = key.split('.')
        
        


        
