import serial

ser = serial.Serial('COM1',9600)


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
        self.label = label
        self.maxVolt = maxVolt
        self.minVolt = minVolt
        self.volt = -1
        self.minVal = None
        self.maxVal = None
        self.changeFunc = None

    @property
    def val(self):
        return ((self.volt - self.minVolt) / self.maxVolt) * (self.maxVal - self.minVal) + self.minVal

    def setVolt(volt):
        self.volt = volt
        if changeFunc: changeFunc(val)

analog = Analog()

class Mic():
    def __init__(self, device ,volume=1.0, pitchMod=None):
        self.volume = volume
        self.defVolume = volume
        self.pitchMod = pitchMod
        self.device = device

mic = Mic()

class AudioPlayer():
    pass

audioPlayer = AudioPlayer()

class Speaker():
    pass

speaker = Speaker()



### ACTIONS

class TogglePitch():
    def __init__(self):
        self.option = 'reg'

    def __call__(self):
        if analog.selected == 'micPitch':
            analog.selected = None
        
        if self.option = 'reg':
            self.option = 'low'
            mic.setPitch(0.5)
        elif self.option = 'low':
            self.option = 'high'
            mic.setPitch(1.5)
        else:
            self.option = 'reg'
            mic.setPitch(1)
            
        return 'pitch ' + str(self.option)[:3]

togglePitch = togglePitch()

def selectPitch():
    togglePitch.option = None # will set to reg pitch if toggle pitch selected
    analog.selected = 'micPitch'
    analog.minVal = 0
    analog.maxVal = 2
    mic.setPitch(analog.val)
    analog.changeFunc = mic.setPitch
    return 'sel pitch ' + analog.val

def ToggleMicVol():
    def __init__(self):
        self.option = 'norm'

    def __call__(self):
        if analog.selected = 'micVol':
            analog.selected = None
        
        if self.option == 'norm':
            self.option = 'mute'
            mic.setVol(0)
        else:
            self.option = 'norm'
            mic.setVol(1)
        return 'vol ' + str(self.option)[:3]

toggleMicVol = ToggleMicVol()

def selectMicVol():
    analog.selected = 'micVol'
    analog.minVal = 0
    analog.maxVal = 4
    mic.setVol(analog.val)
    toggleMicVol.option = None ## will set to default vol
    return 'sel vol ' + str(analog.val)[:3]

def prevCD():
    audioPlayer.prevCD()
    return "CD " + audioPlayer.getCDName()

def nextCD():
    audioPlayer.nextCD()
    return "CD " + audioPlayer.getCDName()

def selCD():
    analog.selected = 'CD'
    analog.minVal = 0
    analog.maxVal = len(audioPlayer.CDList)-1
    audioPlayer.setCD(analog.val)
    return "sel CD " + audioPlayer.getCDName()

def prevSong():
    audioPlayer.prevSong()
    return "song " + audioPlayer.getSongName()

def nextCD():
    audioPlayer.nextCD()
    return "song " + audioPlayer.getSongName()

def selSong():
    analog.selected = 'song'
    analog.minVal = 0
    analog.maxVal = len(audioPlayer.songList)-1
    audioPlayer.setSong(analog.val)
    return "sel Song " + audioPlayer.getSongName()

def maxVol():
    if analog.selected = 'songVol':
        analog.selected = None
    audioPlayer.setSong(1)
    return 'amp max'

def selVol():
    analog.selected = 'songVol'
    analog.minVal = 0
    analog.maxVal = 1
    audioPlayer.setSong(analog.val)
    return 'sel amp ' + str(analog.val)[:3]

def playSong():
    audioPlayer.playSong()
    return 'play'
    
def stopSong():
    audioPlayer.stopSong()


while True:
    try:
        val = ser.read()
        if val[:5] == 'btUp:':
            print('button #' + val[5:] + ' released')
        elif val[:5] == 'btDn:':
            print('button #' + val[5:] + ' pressed')
            
    except (serial.SerialException, serial.SerialTimeoutException):
        continue
    
