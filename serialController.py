import serial

ser = serial.Serial('COM1',9600)

class Button():
    def __init__(self,downFunc=None,upFunc=None,isPressed=False):
        self.isPressed = isPressed
        self.downFunc = downFunc
        self.upFunc = upFunc

class Analog():
    def __init__(self, minVal, maxVal, changeFunc):
        self.maxVal = maxVal
        self.minVal = minVal
        self.changeFunc = changeFunc

class MultiPurposeAnalog(Analog):
    def __init__(self, minVal, MaxVal, changeFunc=None, funcChangeFunc=None,):
        Analog.__init__(minVal,maxVal,changeFunc)
        self.funcChangeFunc = funcChangeFunc

def selectSong(pos):
    newSong = selectedPlaylist[pos]
    if selectedSong != newSong:
        tts(newSong.name)

######

def changeSong(val,minVal,maxVal):
    global selectedSong
    vPerSong = (maxVal - minVal) / len(selectedPlaylist)
    song = (val - minVal) // vPerSong
    selectedSong = 

#####

mpAnalog = MultiPurposeAnalog()


buttons = [
    Button(
        downFunc = (lambda : )
        ),

    ]

analogs = [
    mpAnalog
    ]

while True:
    try:
        val = ser.read()
        if val[:5] == 'btUp:':
            print('button #' + val[5:] + ' released')
        elif val[:5] == 'btDn:':
            print('button #' + val[5:] + ' pressed')
            
    except (serial.SerialException, serial.SerialTimeoutException):
        continue
    
