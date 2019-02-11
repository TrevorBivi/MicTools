import vlc
import os

class song():
    def __init__(self,path):
        self.name = path.split('\\')[-1].split('.')[0]
        self.path = path

class CD():
    def __init__(self,path):
        self.name = path.split('\\')[-1]
        self.songs = []
        for songPath in os.listdir(path):#[p[0] for p in os.walk(path)][1:]:
            self.songs.append(song(path + '\\' + songPath))

class audioPlayer():
    def __init__(self,audioPath):
        self.CDs = []
        for CDPath in os.listdir(audioPath):#[p[0] for p in os.walk(audioPath)][1:]:
            self.CDs.append( CD(audioPath + '\\' + CDPath) )
        self.CDIndex = None
        self.songIndex = None
        self.volume = 100

    def nextCD():
        if self.CDIndex == None or self.CDIndex == len(self.CDs)-1:
            self.CDIndex = 0
        else:
            self.CDIndex += 1
        self.songIndex = None

    def prevCD():
        if self.CDIndex == None or self.CDIndex == 0:
            self.CDIndex = len(self.CDs)-1
        else:
            self.CDIndex -= 1
        self.songIndex = None

    def setCD(index)
        self.CDIndex = index

    def getCDCount():
        return len(self.CDs)

    def nextSong():
        songList = self.CDs[self.CDIndex]
        if self.songIndex == None or self.songIndex == len(songList)-1:
            self.songIndex = 0
        else:
            self.songIndex += 1

    def prevSong():
        if self.songIndex == None or self.songIndex == 0:
            songList = self.CDs[self.CDIndex]
            self.songIndex = len(songList)-1
        else:
            self.songIndex -= 1

    def setSong(index):
        self.songIndex = index

    def getSongCount():
        if self.CDIndex:
            return len(self.CDs[self.CDIndex])
        
            
    
ap = audioPlayer("C:\\Users\\Trevor\\Music\\VR CDS")

'''
        player = vlc.MediaPlayer("C:\\Users\\Trevor\\Dropbox\\Mic Spams\\white farts - chant.mp3")
        player.audio_set_volume(100)
        player.play()
        self.player = player

'''
