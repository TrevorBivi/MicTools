import serial
from functools import partial

from soundDeviceHandler import *
from morphVoxInteractor import *
from audioPlayer import *
from ttsPlayer import *

class Narration():
    def __init__(self,text,skip, repeat):
        self.text = text
        self.skip = skip
        self.repeat = repeat
        self.playing = False

class Analog():
    def __init__(self, min_volt=0, max_volt=1024):
        self.max_volt = max_volt
        self.min_volt = min_volt
        self.volt = -1
        self.min_val = None
        self.max_val = None
        self.change_func = None
        self.mode = None
        self.last_val = None
        self.change_alert_freq = None
        self.last_change_alert_val = None
        self.ser = None
        
    @property
    def val(self):
        float_val = ((self.volt - self.min_volt) / self.max_volt) * (self.max_val - self.min_val) + self.min_val
        if isinstance(self.max_val,int):
            return round(float_val)
        return float_val

    def set_volt(self,volt):
        self.volt = volt
        if self.change_func:
            new_val = self.val
            if new_val != self.last_val:
                self.last_val = new_val
                if self.change_alert_freq:
                    change_alert_val = new_val // self.change_alert_freq
                    alert_info = None
                    if self.last_change_alert_val and change_alert_val != self.last_change_alert_val:
                        alert_info = new_val
                    self.last_change_alert_val = change_alert_val
                    return self.change_func(new_val,alert_info)
                else:
                    return self.change_func(new_val)
                    

    def set_mode(self,mode=None, change_func=None, min_val = 0, max_val = 100,change_alert_freq=None):
        self.mode = mode
        self.change_func = change_func
        self.min_val = min_val
        self.max_val = max_val
        self.last_val = self.val
        self.change_alert_freq = change_alert_freq
        self.last_change_alert_val = None


def set_mode(mode,self):
    '''
    3  5    2    15 16
    1  4    0    12 14
    9  8   *6    10*13
     11           *7
    '''
    if self.button_states[0] and self.button_states[2] and self.button_states[6]:
        mode = 6
    elif self.button_states[0] and self.button_states[2]:
        mode = 3
    elif self.button_states[2] and self.button_states[6]:
        mode = 5
    elif self.button_states[0] and self.button_states[6]:
        mode = 4
        
    
    
    self.mode = mode
    group1,group2,name = self.modes[mode]

    if not name:
        return
    
    self.buttonFuncs = [
        partial(set_mode,0),#0
        group1[2],
        partial(set_mode,1),#2
        group1[0],
        group1[3],         #4
        group1[1],
        partial(set_mode,2),#6
        SerialController.repeat_narration,#self.repeat(),
        group1[5],  #8
        group1[4],
        group2[4],  #10
        None,
        group2[2],  #12
        group2[5],
        group2[3],  #14
        group2[0],
        group2[1]   #16
        ]
    return name + ' mode', 'mode'



class SerialController():
    def __init__(self,ttsPath,ttsDevice,
                 audioPath,audioPlayerDevice,
                 micToSelfDevices,audioToSelfDevices,privateAudioToSelfDevices,
                 audioToOutputDevices,micToOutputDevices,
                 morphVoxPath="C:\\Program Files (x86)\\Screaming Bee\\MorphVOX Pro\\MorphVOXPro.exe",
                 self_audio_volume = 0.15,
                 self_mic_volume = 0.15,
                 self_private_volume = 0.33):
        
        self.analog = Analog()
        self.ser = None
        self.mode = None
        self.button_states = [False,] * 17

        self.audioPlayer = AudioPlayer(audioPath,device=audioPlayerDevice)
        self.ttsPlayer = Balcon(path=ttsPath,device=ttsDevice)
        self.morpher = MorphVox(path=morphVoxPath)

        self.self_audio_volume = self_audio_volume
        self.self_mic_volume = self_mic_volume
        self.self_mic_volume_mod = 1
        self.out_mic_vol = 1
        self.self_private_volume = self_private_volume
        self.micToSelf = SoundHandler(*micToSelfDevices,volume=self_mic_volume)
        self.audioToSelf = SoundHandler(*audioToSelfDevices,volume=self_audio_volume)
        self.privateAudioToSelf = SoundHandler(*privateAudioToSelfDevices,volume=self_private_volume)
        self.audioToOutput = SoundHandler(*audioToOutputDevices)
        self.micToOutput = SoundHandler(*micToOutputDevices)
        
        self.audioToSelf.start()
        self.privateAudioToSelf.start()
        self.audioToOutput.start()
        self.micToOutput.start()

        self.prev_narrations = []
        self.buff_narrations = []
        self.repeated_narrations = []

    def narrate_buffer(self,narration,cutoff=False):
        def thread_target():
            if not narration.repeat:
                for n in self.prev_narrations:
                    if n.skip == narration.skip:
                        self.prev_narrations.remove(n)
                self.prev_narrations.append(narration)
            
            self.ttsPlayer.threadless_say(narration.text,cutoff)
            index = self.buff_narrations.index(narration)
            if len(self.buff_narrations) > index + 1 and not self.buff_narrations[index+1].playing:
                self.narrate_buffer(self.buff_narrations[index+1],cutoff=False)
            self.buff_narrations.remove(narration)
            
        narration.playing = True
        thread = threading.Thread(target=thread_target)
        thread.start()

    def add_narration(self,text,skip=None,repeat=False):
        cutoff=False
        if not repeat:
            self.prev_narrations += self.repeated_narrations
            self.repeated_narrations = []
            self.prev_narrations = self.prev_narrations[-15:]
            #print('not repeat',self.prev_narrations)
            
        while len(self.buff_narrations) > 0 and \
            self.buff_narrations[-1].skip == skip != None and \
            not self.buff_narrations[-1].playing:
                del self.buff_narrations[-1]
        
        if len(self.buff_narrations) and self.buff_narrations[-1].playing and self.buff_narrations[-1].skip == skip != None:
            cutoff = True
        narration = Narration(text,skip,repeat)
        self.buff_narrations.append(narration)
        if cutoff or len(self.buff_narrations) == 1:
            self.narrate_buffer(narration,cutoff)

    def repeat_narration(self):
        if len(self.prev_narrations):
            self.to_repeat = self.prev_narrations[-1]
            del self.prev_narrations[-1]
            self.repeated_narrations.insert(0,self.to_repeat)
            self.add_narration('repeat ' + self.to_repeat.text + ' ' + str(self.prev_narrations), 'repeat', True)
        else:
            self.add_narration('repeat empty buffer', 'repeat', True)
            
    def start(self,modes,port,baud_rate):
        self.modes = modes     
        self.baud_rate = baud_rate
        self.port = port
        self.set_mode(0)

    def set_mode(self,mode):
        return set_mode(mode,self)

    def listen(self):
        while True:
            try:
                if not self.ser:
                    self.ser = serial.Serial(self.port,self.baud_rate)
                val = self.ser.readline()
                print(val)
                
                if val[:5] == b'btUp:':
                    buttonId = int(val[5:-1])
                    self.button_states[buttonId] = False

                elif val[:5] == b'btDn:':
                    #pass
                    buttonId = int(val[5:-1])

                    self.button_states[buttonId] = True
                    
                    if self.buttonFuncs[buttonId]:
                        ret_inf = self.buttonFuncs[buttonId](self)
                        print('tts:', ret_inf )
                        if ret_inf:
                            self.add_narration(*ret_inf)
                    
                elif val[:5] == b'AgCh:':
                    ret_inf = self.analog.set_volt(int(val[5:-1]))
                    if ret_inf:
                        self.add_narration(*ret_inf)
                    
                    
                    #print('analog val' + str(val[5:]))
            except (serial.SerialException, serial.SerialTimeoutException):
                print("DISCONNECT")
                self.ser = None

sc = SerialController('..\\balcon\\balcon.exe','CABLE-B Input (VB-Audio Cable B)', 
                      "C:\\Users\\Trevor\\Music\\VR AUDIO",b'{49E2F089-8E24-44B0-BE20-3A45F25CC2FA}',
                      ('Microphone (Rift Audio), MME','Headphones (Rift Audio), MME'),
                      ('CABLE-A Output (VB-Audio Cable , MME','Headphones (Rift Audio), MME'),
                      ('CABLE-B Output (VB-Audio Cable , MME','Headphones (Rift Audio), MME'),
                      ('CABLE-A Output (VB-Audio Cable , MME','CABLE Input (VB-Audio Virtual , MME'),
                      ('Microphone (Rift Audio), MME','CABLE Input (VB-Audio Virtual , MME')
                      )
modes = []

def disable_mode(mode):
    def real_dec(func):
        def call(controller):
            print('check if ',controller,'mode is',mode)
            if controller.analog.mode == mode:
                controller.analog.set_mode()
            return func(controller)
        return call
    return real_dec


########
# mic

@disable_mode('vol')
def mute_vol(sc):
    sc.out_mic_vol = 0
    sc.micToOutput.volume = 0
    sc.micToSelf.volume = 0
    return 'mute vol','vol'

@disable_mode('vol')
def norm_vol(sc):
    sc.out_mic_vol = 1    
    sc.micToOutput.volume = 1
    sc.micToSelf.volume = sc.self_mic_volume_mod * sc.out_mic_vol * sc.self_mic_volume
    return 'norm vol','vol'

def sel_vol(sc):
    def changeVol(val,alert_info):
        sc.out_mic_vol = val
        sc.micToOutput.volume = val
        sc.micToSelf.volume = sc.self_mic_volume_mod * sc.out_mic_vol * sc.self_mic_volume
        if alert_info != None:
            return str(int(val*20)*5), 'vol'
    
    sc.analog.set_mode('vol',changeVol,change_alert_freq=0.3333,max_val=5.0)
    sc.out_mic_vol = sc.analog.val
    sc.micToOutput.volume = sc.out_mic_vol
    sc.micToSelf.volume = sc.self_mic_volume_mod * sc.out_mic_vol * sc.self_mic_volume
    return 'sel ' + str(int(sc.analog.val*20)*5) + ' vol', 'vol'


@disable_mode('pitch')
def norm_pitch(sc):
    sc.morpher.set_morphed(False)
    sc.micToSelf.stop()
    return 'norm morph', 'morph type'

class TogglePitch():
    def __init__(self):
        self.option = 'reg'

    
    def press_func(self,sc):
        if sc.analog.mode == 'pitch':
            sc.analog.set_mode()
            
        if self.option == 'norm':
            self.option = 'low'
            sc.morpher.set_morph_type(-3)
            sc.micToSelf.start()
            
        elif self.option == 'low':
            self.option = 'high'
            sc.morpher.set_morph_type(3)
            sc.micToSelf.start()

        else:
            self.option = 'norm'
            sc.morpher.set_morph_type(0)
            sc.micToSelf.stop()
            
        return str(self.option) + 'pitch', 'morph type'

toggle_pitch = TogglePitch().press_func

def sel_pitch(sc):
    def change_pitch(pitch):
        sc.morpher.set_morph_type(pitch)
        return str(pitch),'morph type'
    sc.micToSelf.start()
    sc.analog.set_mode('pitch',change_pitch,min_val = -3,max_val=3)
    sc.morpher.set_morph_type(sc.analog.val)
    return 'sel ' + str(sc.analog.val) + ' pitch','morph type'

@disable_mode('pitch')
def fem_morph(sc):
    sc.morpher.set_morph_type('female')
    return 'female morph', 'morph type'

@disable_mode('pitch')
def child_morph(sc):
    sc.morpher.set_morph_type('child')
    return 'child morph', 'morph type'

@disable_mode('pitch')
def demon_morph(sc):
    sc.morpher.set_morph_type('demon')
    return 'demon morph', 'morph type'

@disable_mode('pitch')
def robot_morph(sc):
    sc.morpher.set_morph_type('robot')
    return 'robot morph', 'morph type'

@disable_mode('pitch')
def wtf_morph(sc):
    sc.morpher.set_morph_type('wtf')
    return 'wtf morph', 'morph type'

@disable_mode('pitch')
def echo_morph(sc):
    sc.morpher.set_morph_type('echo')
    return 'echo morph', 'morph type'

modes.append([
    [norm_vol,norm_pitch,
     mute_vol,toggle_pitch,
     sel_vol,sel_pitch],
    [fem_morph,child_morph,
     robot_morph,demon_morph,
     wtf_morph,echo_morph],
    'voice']
    )

#########
# audio mode

@disable_mode('CD')
def prevCD(sc):
    sc.audioPlayer.prevCD()
    return sc.audioPlayer.getSelectedCD().name + ' cd','cd'

@disable_mode('CD')
def nextCD(sc):
    sc.audioPlayer.nextCD()
    return sc.audioPlayer.getSelectedCD().name + ' cd','cd'

def selCD(sc):
    def changeCD(val):
        sc.audioPlayer.setCD(val)
        return sc.audioPlayer.getSelectedCD().name, 'cd'

    sc.analog.set_mode('CD',changeCD,max_val=sc.audioPlayer.getCDCount()-1)
    sc.audioPlayer.setCD(sc.analog.val)
    return "sel " + sc.audioPlayer.getSelectedCD().name + 'cd', 'cd'

@disable_mode('song')
def prevSong(sc):
    sc.audioPlayer.prevSong()
    song = sc.audioPlayer.getSelectedSong()
    if song:
        return song.name + ' Song','song'
    else:
        return 'no CD','song'

@disable_mode('song')
def nextSong(sc):
    sc.audioPlayer.nextSong()
    song = sc.audioPlayer.getSelectedSong()
    if song:
        return song.name + ' Song','song'
    else:
        return 'no CD','song'

def selSong(sc):
    def changeSong(val):
        sc.audioPlayer.setSong(val)
        return sc.audioPlayer.getSelectedSong().name,'song'
        
    if sc.audioPlayer.CDIndex != None:
        sc.analog.set_mode('song',changeSong,max_val = sc.audioPlayer.getSongCount()-1)
        sc.audioPlayer.setSong(sc.analog.val)
        song = sc.audioPlayer.getSelectedSong()
        if song:
            return 'sel ' + song.name + ' song','song'
    else:
        return 'no CD','song'

@disable_mode('amp')
def maxAmp(sc):       
    sc.audioPlayer.setVolume(100)
    return 'max amp', 'amp'

@disable_mode('amp')
def muteAmp(sc):
    sc.audioPlayer.setVolume(0)
    return 'mute amp', 'amp'

def selAmp(sc):
    def change_amp(val,alert_info):
        sc.audioPlayer.setVolume(val)
        if alert_info != None:
            return str(round(alert_info/10)*10), 'amp'
    
    sc.analog.set_mode('amp',change_amp,change_alert_freq=10)
    sc.audioPlayer.setVolume(sc.analog.val)
    return 'sel ' + str(sc.analog.val) + ' amp', 'amp'

def playSong(sc):
    sc.audioPlayer.playSong()
    return 'play', 'play state'

def pauseSong(sc):
    sc.audioPlayer.pauseSong()
    return 'pause', 'play state'

def stopSong(sc):
    sc.audioPlayer.stopSong()
    return 'stop', 'play state'


modes.append([
    [playSong,maxAmp,
     pauseSong,muteAmp,
     stopSong,selAmp],
    [nextSong,nextCD,
     prevSong,prevCD,
     selSong,selCD],
     'media']
    )

########
# sound_board

def sel_board(self,sc):
    def change_board(board_index):
        sc.audioPlayer.setBoard(board_index)
        return sc.audioPlayer.getSelectedBoard().name,'board'
    sc.analog.set_mode('board',change_board,max_val = len(sc.audioPlayer.boards)-1)
    'sel ' + sc.audioPlayer.getSelectedBoard().name + ' board', 'board'
    
@disable_mode('board')
def next_board(sc):
    if sc.button_states[1]:
        return sel_board(sc)
    else:
        sc.audioPlayer.nextBoard()
        return sc.audioPlayer.getSelectedBoard().name + ' board', 'board'

@disable_mode('board')     
def prev_board(sc):
    if sc.button_states[3]:
        return sel_board(sc)
    else:
        sc.audioPlayer.prevBoard()
        sc.audioPlayer.getSelectedBoard().name + ' board', 'board'

class PreviewHandler(object):
    def __init__(self):
        self.is_previewing = True

    def toggle_preview(self,sc):
        self.is_previewing = not self.is_previewing
        if self.is_previewing:
            sc.audioPlayer.stopSong()
            return 'preview board','board toggle'
        else:
            return 'live board','board toggle'

    def play_board_button(self,index,sc):
        board = sc.audioPlayer.getSelectedBoard()
        if not board:
            return 'no board','board play'
        if len(board.songs) <= index:
            return 'no index','board play'
        song = board.songs[index]
        if self.is_previewing:
            return song.name,'board play'
        elif song:
            sc.audioPlayer.playBoardFile(index)

ph = PreviewHandler()

modes.append([
    [next_board, partial(ph.play_board_button,0),
     prev_board, partial(ph.play_board_button,1),
     ph.toggle_preview, partial(ph.play_board_button,2) ],
    [partial(ph.play_board_button,3),partial(ph.play_board_button,6),
     partial(ph.play_board_button,4),partial(ph.play_board_button,7),
     partial(ph.play_board_button,5),partial(ph.play_board_button,8)],
    'board'
    ]
    )

modes.append([[],[],None]) # TODO: recorder tab

modes.append([[],[],None]) #TODO: splice tab

########
# settings
'''
self.self_audio_volume = self_audio_volume
        self.self_mic_volume = self_mic_volume
        self.self_private_volume = self_private_volume
        self.micToSelf = SoundHandler(*micToSelfDevices,volume=self_mic_volume)
        self.audioToSelf = SoundHandler(*audioToSelfDevices,volume=self_audio_volume)
        self.privateAudioToSelf = SoundHandler(*privateAudioToSelfDevices,volume=self_private_volume)
        
'''
@disable_mode('audio vol')
def norm_audio_vol(sc):
    sc.audioToSelf.volume = sc.self_mic_volume
    return 'norm audio vol', 'audio vol'
        
@disable_mode('audio vol')
def low_audio_vol(sc):
    sc.audioToSelf.volume = sc.self_mic_volume * 0.33
    return 'low audio vol', 'audio vol'

def sel_audio_vol(sc):
    def change_audio_vol(change_vol,alert_info):
        sc.audioToSelf.volume = change_vol
        if alert_info:
            return str(int(alert_info*10)*10) + ' audio vol', 'audio vol'
    sc.analog.set_mode('audio vol ',change_audio_vol,change_alert_freq=0.20,max_val=2.0)
    sc.audioToSelf.volume = sc.self_audio_volume * sc.analog.val
    return 'sel ' + str(int(sc.analog.val*10)*10) + ' audio vol', 'audio vol'

@disable_mode('private vol')
def norm_private_vol(sc):
    sc.privateAudioToSelf.volume = sc.self_private_volume
    return 'norm private vol', 'private vol'

@disable_mode('private vol')
def low_private_vol(sc):
    sc.privateAudioToSelf.volume = sc.self_private_volume * 0.33
    return 'low private vol', 'private vol'
    
def sel_private_vol(sc):
    def change_tts_vol(tts_vol,alert_info):
        sc.privateAudioToSelf.volume = sc.self_private_volume * tts_vol
        if alert_info:
            return str(int(alert_info*10)*10) + ' private vol', 'private vol'

    sc.analog.set_mode('private vol', change_tts_vol, change_alert_freq=0.20, max_val = 2.0)
    sc.privateAudioToSelf.volume = sc.analog.val
    return 'sel ' + str(int(sc.analog.val*10)*10) + ' private vol','private vol'

@disable_mode('mic vol')    
def norm_mic_vol(sc):
    sc.self_mic_volume_mod = 1
    sc.micToSelf.volume = sc.self_mic_volume_mod * sc.out_mic_vol * sc.self_mic_volume
    return 'norm vol', 'mic vol'

@disable_mode('mic vol')
def low_mic_vol(sc):
    sc.self_mic_volume_mod = 0.33
    sc.micToSelf.volume = sc.self_mic_volume_mod * sc.out_mic_vol * sc.self_mic_volume
    return 'low vol','mic vol'

def sel_mic_vol(sc):
    def change_mic(mic_val, alert_info):
        sc.self_mic_volume_mod = mic_val
        sc.micToSelf.volume = sc.self_mic_volume_mod * sc.out_mic_vol * sc.self_mic_volume
        if alert_info:
            return str(int(alert_info*10)*10) + ' mic vol', 'mic vol'
    
    sc.analog.set_mode('mic vol', change_mic, change_alert_freq = 0.20, max_val = 2.0)
    sc.analog.self_mic_volume_mod = sc.analog.val
    sc.micToSelf.volume = sc.self_mic_volume_mod * sc.out_mic_vol * sc.self_mic_volume
    return 'sel ' + str(int(sc.analog.val*10)*10) + ' mic vol', 'mic vol'

@disable_mode('all vol')
def norm_all_vol(sc):
    norm_audio_vol(sc)
    norm_private_vol(sc)
    norm_mic_vol(sc)
    return 'norm all vol', 'all vol'

@disable_mode('all vol')
def low_all_vol(sc):
    low_audio_vol(sc)
    low_private_vol(sc)
    low_mic_vol(sc)
    'low all vol', 'all vol'

def sel_all_vol(sc):
    def change_all_val(mic_val,alert_info):
        sc.self_mic_volume_mod = mic_val
        sc.micToSelf.volume = sc.self_mic_volume_mod * sc.out_mic_vol * sc.self_mic_volume
        sc.audioToSelf.volume = mic_val * sc.self_private_volume
        sc.privateAudioToSelf.volume = mic_val * sc.self_private_volume
        sc.micToSelf.volume = mic_val * sc.self_mic_volume_mod * sc.out_mic_vol
        if alert_info:
            return str(int(alert_info*10)*10) + ' all vol', 'all vol'

    sc.analog.set_mode('all vol',change_all_val, change_alert_freq=0.20, max_val = 2.0)
    sc.self_mic_volume_mod = sc.analog.val
    sc.audioToSelf.volume = sc.self_mic_volume_mod * sc.self_private_volume
    sc.privateAudioToSelf.volume = sc.self_mic_volume_mod * sc.self_private_volume
    sc.micToSelf.volume = sc.self_mic_volume_mod * sc.out_mic_vol * sc.self_mic_volume
    return 'sel ' + str(int(sc.self_mic_volume_mod*10)*10) + ' all vol', 'all vol'
    
modes.append([
    [norm_private_vol, norm_mic_vol,
     low_private_vol, low_mic_vol,
     sel_private_vol, sel_mic_vol],
    [norm_audio_vol, norm_all_vol,
     low_audio_vol, low_all_vol,
     sel_audio_vol, sel_all_vol],
    'settings'
    ])
    


#def prev_board(sc):

#def toggle_preview(sc):

    
#@disable_
#def normVol():
    
#
#def selectMicVol():
#    analog.mode = 'micVol'
#    analog.minVal = 0
#    analog.maxVal = 4
#    mic.setVol(analog.val)
#    toggleMicVol.option = None ## will set to default vol
#    return 'sel vol ' + str(analog.val)[:3]


sc.start( modes,'COM6',9600)
sc.listen()
