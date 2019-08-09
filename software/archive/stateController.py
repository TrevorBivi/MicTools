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

import serial
from soundDirector import *
from wavSound import *
from micSound import *
from bridgeSound import *
from morphVoxInteractor import *

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
        'mode':'song',
        'song':{
            'mode':1,
            'CDList':[
                [

                    ],
                ],
            'playingSong':None,
            'CDIndex':0,#None,
            'songIndex':0,#None,
            'playing':False,
            'pitch':1.0,
            'speed':1.0,
            'volume':1.0
            },
        'board':{
            'mode':1,
            'boardList':[
                [
                    ]


                ],
            'boardIndex':None,
            'soundIndex':None,
            'playing':False,
            'pitch':1.0
            ,
            'speed':1.0,
            'volume':1.0
            },
        'mic':{
            'mode':1,
            'playingMic':None,
            'mute':False,
            'aupyom':{
                'pitch':1.0,
                'speed':1.0,
                'volume':1.0,
                'buffering':False
                },
            'vox':{
                'voice':None,
                'volume':1.0,
            }
        }
    }

class controller():
    def __init__(self, sound_director):
        self.sound_director = sound_director
        self.state = default_state()
        self.ser = serial.Serial('COM3',9600)

    def update_state(self,key,value):
        key_list = key.split('.')

        orig_val = self.state
        for k in key_list[:-1]:
            orig_val = orig_val[k]

        if key == 'song.playingSong':
            if self.state['song']['playingSong']:
                if self.state['song']['playingSong'] != value:
                    value.index = 0
                    value._init_stretching()
                    try:
                        self.sound_director.remove_sound(self.state['song']['playingSong'])
                    except ValueError:
                        print("REMOVE AAA: failed")
  
        elif key == 'song.playing':
            if self.state['song']['CDIndex'] != None:
                if self.state['song']['songIndex'] != None:
                    song = self.state['song']['CDList'][
                        self.state['song']['CDIndex']
                        ][
                            self.state['song']['songIndex']
                            ]
                    if value:
                        print('STARTING NEW SONG')
                        if self.state['song']['playingSong'] != song:
                            self.update_state('song.playingSong', song)
                        if song not in self.sound_director.sounds:
                            song.speed = self.state['song']['speed']
                            song.volume = self.state['song']['volume']
                            song.pitch = self.state['song']['pitch']
                            self.sound_director.add_sound( song )
                    elif not value:
                        print('REMOVEING SOUND')
                        try:
                            self.sound_director.remove_sound( song )
                        except ValueError:
                            print ('REMOVE BBB FAILED')
        elif key == 'song.songIndex':
            if self.state['song']['CDIndex'] != None and not self.state['song']['playing']:
                if self.state['song']['songIndex'] == value:
                    print('RESETING SONG')
                    self.state['song']['playingSong'].index = 0
                    self.state['song']['playingSong']._init_stretching()

        elif key == 'song.speed':
            if self.state['song']['playingSong']:
                self.state['song']['playingSong'].speed = value
        elif key == 'song.volume':
            if self.state['song']['playingSong']:
                value = max(value, 0.05)
                self.state['song']['playingSong'].volume = value
        elif key == 'song.pitch':
            if self.state['song']['playingSong']:            
                self.state['song']['playingSong'].pitch = value

        elif key == 'mic.playingMic':
            if self.state['mic']['playingMic']:
                self.sound_director.remove_sound( self.state['mic']['playingMic'] )
            if type(value) == MicSound:
                value.speed = self.state['mic']['aupyom']['speed']
                value.pitch = self.state['mic']['aupyom']['pitch']
                value.volume = self.state['mic']['aupyom']['volume']
            self.sound_director.add_sound(value)
            
        elif key == 'mic.playing':
            playing_mic = self.state['mic']['playingMic']
            if self.state['mic']['mode'] == 0:
                if type(self.state['mic']['playingMic']) != MicSound:
                    self.update_state('mic.playingMic',
                                 MicSound(('Speakers (2- High Definition Au, MME',),'Microphone (Blue Snowball), MME')
                                 )
            elif self.state['mic']['mode'] == 1:
                if type(self.state['mic']['playingMic']) != BridgeSound:
                    self.update_state('mic.playingMic',
                                 BridgeSound(('Speakers (2- High Definition Au, MME',),'Microphone (Screaming Bee Audio, MME')
                                 )
                        
        elif key in ['mic.aupyom.speed', 'mic.aupyom.speed', 'mic.aupyom.speed']:
            playing_mic = self.state['mic']['playingMic']
            if type(playing_mic) == MicSound:
                setattr(playing_mic,key_list[-1],value)            
                
        
        orig_val[key_list[-1]] = value

        print('update state\n' + str(self.state))
            

    def handle_button_press(self,button_ID):
        print('PRESS',button_ID)
        if button_ID == 20:
            self.update_state('mode','mic')
        elif button_ID == 19:
            self.update_state('mode','board')
        elif button_ID == 18:
            self.update_state('mode','song')
        elif 14 < button_ID < 18:
            self.update_state(self.state['mode'] + '.mode', button_ID - 15)
        elif button_ID == 0:
            if self.state['mode'] == 'song':
                self.update_state('song.playing',True)
            if self.state['mode'] == 'mic':
                self.update_state('mic.playing',True)
                
                            
        elif button_ID == 1:
            if self.state['mode'] == 'song':
                self.update_state('song.playing',False)
            
        elif button_ID == 2:
            pass
        else:
            if self.state['mode'] == 'song':
                if self.state['song']['mode'] == 0:
                    print('SEL CD')
                    self.update_state('song.CDIndex', button_ID - 3)
                elif self.state['song']['mode'] == 1:
                    self.update_state('song.songIndex', button_ID - 3)
                elif self.state['song']['mode'] == 2:
                    row = (button_ID - 3) // 3
                    col = (button_ID - 3) % 3
                        
                    if row <= 2:
                        var = ['volume','pitch','speed'][row]
                        if col == 0:
                            self.update_state('song.' + var, max(0.01,
                                self.state['song'][var] - 0.125))
                        elif col == 1:
                            self.update_state('song.'+var, min(4,
                                self.state['song'][var] + 0.125))
                        elif col == 2:
                            self.update_state('song.'+var, 1.0)
            if self.state['mode'] == 'mic':
                if self.state['mic']['mode'] == 0:
                    row = (button_ID - 3) // 3
                    col = (button_ID - 3) % 3
                        
                    if row == 3:
                        if col <= 1:
                            mic_sound = self.state['mic']['playingMic']
                            if type(mic_sound) == MicSound:
                                mic_sound.buffering = bool(col - 1)
                        else:
                            mic_sound = self.state['mic']['playingMic']
                            if type(mic_sound) == MicSound:
                                mic_sound.data = mic_sound.data[mic_sound.data.size - mic_sound.target_buffer * mic_sound.chunk_size:]
                                mic_sound._sy = numpy.zeros(mic_sound.sr, dtype=mic_sound._sy.dtype)
                                

                    else:
                        var = ['volume','pitch','speed'][row]
                        if col == 0:
                            self.update_state('mic.aupyom.' + var, max(0.01,
                                self.state['mic']['aupyom'][var] - 0.125))
                        elif col == 1:
                            self.update_state('mic.aupyom.'+var, min(4,
                                self.state['mic']['aupyom'][var] + 0.125))
                        elif col == 2:
                            self.update_state('mic.aupyom.'+var, 1.0)
                if self.state['mic']['mode'] == 1:

                    voice = ('tough','troll','demon','nerd','girl','child','alien','radio','echo','demon','shade',None)[button_ID-3]
                    
                    self.update_state('mic.vox.voice', voice):
                        
                        
                            
                            
                        
                    

    def listen(self):
        while True:
            try:
                if not self.ser:
                    self.ser = serial.Serial('COM3',9600)
                val = self.ser.readline()[:-2]
                if val != b'x':
                    button = int(val)

                    self.handle_button_press(button)

                        
                    
            except (serial.SerialException, serial.SerialTimeoutException):
                print("DISCONNECT")
                self.ser = None

morph_vox = MorphVox()
time.sleep(1)
morph_vox.set_muted(True)
morph_vox.set_morph_type(False)

c = controller(SoundDirector([ OutputDevice('Speakers (2- High Definition Au, MME') ]))
c.listen()

        


        
