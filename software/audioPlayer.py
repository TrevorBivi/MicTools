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
        for songPath in os.listdir(path):
           self.songs.append(song(path + '\\' + songPath))
            
class AudioPlayer():
    def __init__(self,audioPath):
        self.CDs = []
        for CDPath in os.listdir(audioPath):
            self.CDs.append( CD(audioPath + '\\' + CDPath) )
        self.CDIndex = None
        self.songIndex = None
        self.volume = 100
        self.player = vlc.MediaPlayer()

    def getSelectedSong(self):
        if self.CDIndex == None or self.songIndex == None:
            return None
        CD = self.CDs[self.CDIndex]
        song = CD.songs[self.songIndex]
        return song

    def playSong(self):
        self.player.play()

    def pauseSong(self):
        self.player.pause()

    def stopSong(self):
        self.player.stop()

    def setVolume(self, volume):
        self.volume = volume
        self.player.audio_set_volume(self.volume)

    def nextCD(self):
        if self.CDIndex == None or self.CDIndex == len(self.CDs)-1:
            self.setCD(0)
        else:
            self.setCD(self.CDIndex + 1)

    def prevCD(self):
        if self.CDIndex == None or self.CDIndex == 0:
            self.setCD(len(self.CDs) - 1)
        else:
            self.setCD(self.CDIndex - 1)

    def setCD(self,index):
        self.CDIndex = index
        self.songIndex = None
        self.player.set_media(None)

    def getCDCount(self):
        return len(self.CDs)

    def getSelectedCD(self):
        return self.CDs[self.CDIndex]

    def nextSong(self):
        if self.CDIndex != None:
            songList = self.CDs[self.CDIndex].songs
            if self.songIndex == None or self.songIndex == len(songList)-1:
                self.setSong(0)
            else:
                self.setSong(self.songIndex + 1)

    def prevSong(self):
        if self.songIndex == None or self.songIndex == 0:
            songList = self.CDs[self.CDIndex].songs
            self.setSong(len(songList) - 1)
        else:
            self.setSong(self.songIndex - 1)

    def setSong(self,index):
        self.songIndex = index
        song = self.getSelectedSong()
        if song:
            print('set media',song.path)
            self.player.set_media( vlc.Media( song.path ) )

    def getSongCount(self):
        if self.CDIndex != None:
            return len(self.CDs[self.CDIndex].songs)
        return None
        
            
#audioPlayer = AudioPlayer("C:\\Users\\Trevor\\Music\\VR CDS")

ap = AudioPlayer("C:\\Users\\Trevor\\Music\\VR CDS")
