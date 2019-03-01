import serial
from functools import partial

from soundDeviceHandler import *
from morphVoxInteractor import *
from audioPlayer import *
from ttsPlayer import *
'''
class Button():
    def __init__(self,down_func=None,upFunc=None,isPressed=False):
        global buttons
        self.isPressed = isPressed
        self.downFunc = downFunc
        self.upFunc = upFunc
'''
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
                self.change_func(new_val)

    def set_mode(self,mode=None, change_func=None, min_val = 0, max_val = 100):
        self.mode = mode
        self.change_func = change_func
        self.min_val = min_val
        self.max_val = max_val
        self.last_val = self.val

class SerialController():
    def __init__(self,ttsPath,ttsDevice,
                 audioPath,audioPlayerDevice,
                 micToSelfDevices,audioToSelfDevices,privateAudioToSelfDevices,
                 audioToOutputDevices,micToOutputDevices):
        
        self.analog = Analog()
        self.ser = None
        self.mode = None

        self.audioPlayer = AudioPlayer(audioPath,device=audioPlayerDevice)
        self.ttsPlayer = Balcon(path=ttsPath,device=ttsDevice)

        self.micToSelf = SoundHandler(*micToSelfDevices)
        self.audioToSelf = SoundHandler(*audioToSelfDevices)
        self.privateAudioToSelf = SoundHandler(*privateAudioToSelfDevices)
        self.audioToOutput = SoundHandler(*audioToOutputDevices)
        self.micToOutput = SoundHandler(*micToOutputDevices)
    
    def start(self,modes,port,baud_rate):
        self.modes = modes     
        self.baud_rate = baud_rate
        self.port = port
        self.set_mode(0)

        
    def set_mode(self,mode):
        '''
        3  5    2    15 16
        1  4    0    12 14
        9  8   *6    10*13
         11           *7
        '''
        self.mode = mode
        group1,group2 = self.modes[mode]

        self.buttonFuncs = [
            partial(self.set_mode,1),#0
            group1[2],
            partial(self.set_mode,0),#2
            group1[0],
            group1[3],         #4
            group1[1],
            partial(self.set_mode,2),#6
            None,#self.repeat(),
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
        return 'mode ' + str(mode)

    def listen(self):
        while True:
            try:
                if not self.ser:
                    self.ser = serial.Serial(self.port,self.baud_rate)
                val = self.ser.readline()
                print(val)
                
                if val[:5] == b'btUp:':
                    pass

                elif val[:5] == b'btDn:':
                    #pass
                    buttonId = int(val[5:-1])
                    print('tts:',self.buttonFuncs[buttonId](self) )
                    
                elif val[:5] == b'AgCh:':
                    self.analog.set_volt(int(val[5:-1]))

                    
                    
                    #print('analog val' + str(val[5:]))
            except (serial.SerialException, serial.SerialTimeoutException):
                print("DISCONNECT")
                self.ser = None


def disable_mode(mode):
    def real_dec(func):
        def call(controller):
            print('check if ',controller,'mode is',mode)
            if controller.analog.mode == mode:
                controller.analog.set_mode()
            return func(controller)
        return call
    return real_dec


sc = SerialController('..\\balcon\\balcon.exe','CABLE-B Input (VB-Audio Cable B)', 
                      "C:\\Users\\Trevor\\Music\\VR CDS",b'{49E2F089-8E24-44B0-BE20-3A45F25CC2FA}',
                      ('Microphone (Rift Audio), MME','Headphones (Rift Audio), MME'),
                      ('CABLE-A Output (VB-Audio Cable , MME','Headphones (Rift Audio), MME'),
                      ('CABLE-B Output (VB-Audio Cable , MME','Headphones (Rift Audio), MME'),
                      ('CABLE-A Output (VB-Audio Cable , MME','CABLE Input (VB-Audio Virtual , MME'),
                      ('Microphone (Rift Audio), MME','CABLE Input (VB-Audio Virtual , MME')
                      )


modes = []

#########
# Sound mode

@disable_mode('CD')
def prevCD(sc):
    sc.audioPlayer.prevCD()
    return "CD " + sc.audioPlayer.getSelectedCD().name

@disable_mode('CD')
def nextCD(sc):
    sc.audioPlayer.nextCD()
    return "CD " + sc.audioPlayer.getSelectedCD().name

def selCD(sc):
    def changeCD(val):
        sc.audioPlayer.setCD(val)
        print('new cd',sc.audioPlayer.getSelectedCD().name)

    sc.analog.set_mode('CD',changeCD,max_val=sc.audioPlayer.getCDCount()-1)
    sc.audioPlayer.setCD(sc.analog.val)
    return "sel CD " + sc.audioPlayer.getSelectedCD().name

@disable_mode('song')
def prevSong(sc):
    sc.audioPlayer.prevSong()
    song = sc.audioPlayer.getSelectedSong()
    if song:
        return 'Song ' + song.name
    else:
        return 'no CD'

@disable_mode('song')
def nextSong(sc):
    sc.audioPlayer.nextSong()
    song = sc.audioPlayer.getSelectedSong()
    if song:
        return 'Song ' + song.name
    else:
        return 'no CD'

def selSong(sc):
    def changeSong(val):
        sc.audioPlayer.setSong(val)
        print('song',sc.audioPlayer.getSelectedSong().name)
        
    if sc.audioPlayer.CDIndex != None:
        sc.analog.set_mode('song',changeSong,max_val = sc.audioPlayer.getSongCount()-1)
        sc.audioPlayer.setSong(sc.analog.val)
        song = sc.audioPlayer.getSelectedSong()
        if song:
            return 'sel song ' + song.name
    else:
        return 'no CD'

@disable_mode('amp')
def maxAmp(sc):       
    sc.audioPlayer.setVolume(100)
    return 'amp max'

@disable_mode('amp')
def muteAmp(sc):
    sc.audioPlayer.setVolume(0)
    return 'amp mute'

def selAmp(sc):
    def changeVol(val):
        sc.audioPlayer.setVolume(val)
        print(str(val))
    
    sc.analog.set_mode('amp',changeVol)
    sc.audioPlayer.setVolume(sc.analog.val)
    return 'sel amp ' + str(sc.analog.val)

def playSong(sc):
    sc.audioPlayer.playSong()
    return 'play'

def pauseSong(sc):
    sc.audioPlayer.pauseSong()
    return 'pause'

def stopSong(sc):
    sc.audioPlayer.stopSong()
    return 'stop'

modes.append([
    [playSong,maxAmp,
     pauseSong,muteAmp,
     stopSong,selAmp],
    [nextSong,nextCD,
     prevSong,prevCD,
     selSong,selCD]]
    )

########
# mic

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
