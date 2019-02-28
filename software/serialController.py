import serial
from soundDeviceHandler import *
from audioPlayer import *
from ttsPlayer import *

audioPlayer = AudioPlayer( "C:\\Users\\Trevor\\Music\\VR CDS",
                          device='CABLE-A Input (VB-Audio Cable A)')

ttsPlayer = Balcon(device='CABLE-B Input (VB-Audio Cable B)')

MicToHeadphones = SoundHandler(
                'Microphone (Rift Audio), MME',
                'Headphones (Rift Audio), MME')

audioToHeadphones = SoundHandler(
                'CABLE-A Output (VB-Audio Cable , MME',
                'Headphones (Rift Audio), MME')

privateAudioToHeadphones = SoundHandler(
                'CABLE-B Output (VB-Audio Cable , MME',
                'Headphones (Rift Audio), MME')

audioToOutput = SoundHandler(
                'CABLE-A Output (VB-Audio Cable , MME',
                'CABLE Input (VB-Audio Virtual , MME')

micToOutput = SoundHandler(
                'Microphone (Rift Audio), MME',
                'CABLE Input (VB-Audio Virtual , MME')

audioToHeadphones.start()
privateAudioToHeadphones.start()
audioToOutput.start()
micToOutput.start()

ser = None
### OBJECTS
class Button():
    def __init__(self,downFunc=None,upFunc=None,isPressed=False):
        global buttons
        self.isPressed = isPressed
        self.downFunc = downFunc
        self.upFunc = upFunc

buttons = []

class Analog():
    def __init__(self, minVolt=0, maxVolt=1024):
        global analogControllers
        self.maxVolt = maxVolt
        self.minVolt = minVolt
        self.volt = -1
        self.minVal = None
        self.maxVal = None
        self.changeFunc = None
        self.mode = None
        self.lastVal = None
        
    @property
    def val(self):
        floatVal = ((self.volt - self.minVolt) / self.maxVolt) * (self.maxVal - self.minVal) + self.minVal
        if isinstance(self.maxVal,int):
            return round(floatVal)
        return floatVal

    def setVolt(self,volt):
        self.volt = volt
        if self.changeFunc:
            newVal = self.val
            if newVal != self.lastVal:
                lastVal = newVal
                self.changeFunc(newVal)

    def setMode(self,mode, changeFunc=None, minVal = 0, maxVal = 100):
        self.mode = mode
        self.changeFunc = changeFunc
        self.minVal = minVal
        self.maxVal = maxVal
        self.lastVal = val

analog = Analog()

'''
class Mic():
    def __init__(self, device ,volume=1.0, pitchMod=None):
        self.volume = volume
        self.defVolume = volume
        self.pitchMod = pitchMod
        self.device = device

mic = Mic()

class Speaker():
    pass

speaker = Speaker()'''

### ACTIONS

class TogglePitch():
    def __init__(self):
        self.option = 'reg'

    def __call__(self):
        if analog.mode == 'micPitch':
            analog.mode = None
        
        if self.option == 'reg':
            self.option = 'low'
            mic.setPitch(0.5)
        elif self.option == 'low':
            self.option = 'high'
            mic.setPitch(1.5)
        else:
            self.option = 'reg'
            mic.setPitch(1)
            
        return 'pitch ' + str(self.option)[:3]

togglePitch = TogglePitch()

def selectPitch():
    togglePitch.option = None # will set to reg pitch if toggle pitch selected
    analog.mode = 'micPitch'
    analog.minVal = 0
    analog.maxVal = 2
    mic.setPitch(analog.val)
    analog.changeFunc = mic.setPitch
    return 'sel pitch ' + analog.val

def ToggleMicVol():
    def __init__(self):
        self.option = 'norm'

    def __call__(self):
        if analog.mode == 'micVol':
            analog.mode = None
        
        if self.option == 'norm':
            self.option = 'mute'
            mic.setVol(0)
        else:
            self.option = 'norm'
            mic.setVol(1)
        return 'vol ' + str(self.option)[:3]

toggleMicVol = ToggleMicVol()

def selectMicVol():
    analog.mode = 'micVol'
    analog.minVal = 0
    analog.maxVal = 4
    mic.setVol(analog.val)
    toggleMicVol.option = None ## will set to default vol
    return 'sel vol ' + str(analog.val)[:3]

def prevCD():
    audioPlayer.prevCD()
    if analog.mode == 'CD':
        analog.setMode(None)
    return "CD " + audioPlayer.getSelectedCD().name

def nextCD():
    audioPlayer.nextCD()
    if analog.mode == 'CD':
        analog.setMode(None)
    return "CD " + audioPlayer.getSelectedCD().name

def selCD():
    def changeCD(val):
        audioPlayer.setCD(val)
        print(audioPlayer.getSelectedCD().name)

    analog.setMode('CD',changeCD,maxVal=audioPlayer.getCDCount()-1)
    audioPlayer.setCD(analog.val)
    return "sel CD " + audioPlayer.getSelectedCD().name

def prevSong():
    if analog.mode == 'song':
        analog.setMode(None)
        
    audioPlayer.prevSong()
    song = audioPlayer.getSelectedSong()
    if song:
        return 'Song ' + song.name
    else:
        return 'no CD'

def nextSong():
    if analog.mode == 'song':
        analog.setMode(None)
        
    audioPlayer.nextSong()
    song = audioPlayer.getSelectedSong()
    if song:
        return 'Song ' + song.name
    else:
        return 'no CD'

def selSong():
    def changeSong(val):
        audioPlayer.setSong(val)
        print(audioPlayer.getSelectedSong().name)
        
    if audioPlayer.CDIndex != None:
        analog.setMode('song',changeSong,maxVal = audioPlayer.getSongCount()-1)
        audioPlayer.setSong(analog.val)
        song = audioPlayer.getSelectedSong()
        if song:
            return 'sel song ' + song.name
    else:
        return 'no CD'
    
def maxVol():
    if analog.mode == 'amp':
        analog.setMode(None)
        
    audioPlayer.setSong(1)
    return 'amp max'

def selVol():
    def changeVol(val):
        audioPlayer.setVolume(val)
        print(str(val))
    
    analog.setMode('amp',changeVol)
    audioPlayer.setVolume(analog.val)
    return 'sel amp ' + str(analog.val)

def playSong():
    audioPlayer.playSong()
    return 'play'

def pauseSong():
    audioPlayer.pauseSong()
    return 'pause'

def stopSong():
    audioPlayer.stopSong()
    return 'stop'

buttons = [
    selSong, 
    None, #1
    selCD,
    None, #3
    None, 
    None, #5
    selVol,
    stopSong, #7
    None,
    None, #9
    playSong,
    None, #11
    nextSong, 
    pauseSong, #13
    prevSong, 
    prevCD, #15
    nextCD,
    ]

buttons = buttons + [None] * (17-len(buttons))

'''
3  5    2    15 16
1  4    0    12 14
9  8   *6    10*13
 11           *7
'''

while True:
    try:
        if not ser:
            ser = serial.Serial('COM6',9600)
        val = ser.readline()
        print(val)
        if val[:5] == b'btUp:':
            print('button #' + str(val[5:-1]) + ' released')
        elif val[:5] == b'btDn:':
            print('button #' + str(val[5:-1]) + ' pressed')
            buttonId = int(val[5:-1])
            if buttons[buttonId]:
                print('EXEC: ' + buttons[buttonId]())
        elif val[:5] == b'AgCh:':
            analog.setVolt(int(val[5:-1]))
            #print('analog val' + str(val[5:]))
            
    except (serial.SerialException, serial.SerialTimeoutException):
        print("DISCONNECT")
        ser = None
    
