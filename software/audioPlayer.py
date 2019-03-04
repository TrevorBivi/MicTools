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
    def __init__(self,audioPath, device=None):
        #store normal playlists
        self.CDs = []
        for CDPath in os.listdir(audioPath + '\\CDs'):
            self.CDs.append( CD(audioPath + '\\CDs\\' + CDPath) )
        
        self.boards = []
        for CDPath in os.listdir(audioPath + '\\SoundBoards'):
            self.boards.append( CD(audioPath + '\\SoundBoards\\' + CDPath) )
        
        self.CDIndex = None
        self.songIndex = None
        self.volume = 100
        self.Instance = vlc.Instance()
        self.player = self.Instance.media_player_new()

        self.board_index = None

        #self.player = vlc.MediaPlayer()
        #self.device=device
        if device:            
            
            devices = []
            mods = self.player.audio_output_device_enum()

            if mods:
                mod = mods
                while mod:
                    mod = mod.contents
                    devices.append(mod.device)
                    mod = mod.next

            vlc.libvlc_audio_output_device_list_release(mods)

            # this is the part I change on each run of the code.
            for d in devices:
                if bytes(d) == device:
                    
                    #print('aud device',bytes(devices[4]))
                    self.player.audio_output_device_set(None, d)

    def getSelectedBoard(self):
        if self.board_index != None:
            return self.boards[self.board_index]

    def nextBoard(self):
        if self.board_index == None or self.board_index >= len(self.boards)-1:
            self.setBoard(0)
        else:
             self.setBoard(self.board_index+1)
            
    def prevBoard(self):
        if not self.board_index:
            self.setBoard(len(self.boards)-1)
        else:
            self.setBoard(self.board_index-1)

    def setBoard(self,index):
        self.board_index = index
                    
    def getSelectedSong(self):
        if self.CDIndex == None or self.songIndex == None or \
           not 0 <= self.CDIndex < len(self.CDs) or not 0 <= self.songIndex < len(self.getSelectedCD().songs):
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
        if not self.CDIndex:
            self.setCD(len(self.CDs) - 1)
        else:
            self.setCD(self.CDIndex - 1)

    def setCDByName(self,name):
        for cd,index in enumerate(self.CDs):
            if name == cd.name:
                self.setCD(index)
                break

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
        if self.CDIndex != None:
            if not self.songIndex:
                songList = self.getSelectedCD().songs
                self.setSong(len(songList) - 1)
            else:
                self.setSong(self.songIndex - 1)

    def setSongByName(self,name):
        for song, index in enumerate(self.getSelectedCD()):
            if name == song.name:
                self.setSong(index)
                break

    def setSong(self,index):
        self.songIndex = index
        song = self.getSelectedSong()
        if song:
            print('set media',song.path)
            self.player.set_media( vlc.Media( song.path ) )

    def playBoardFile(self,index):
        song = self.getSelectedBoard().songs[index]
        self.player.set_media(vlc.Media(song.path))
        self.playSong()
        
    def getSongCount(self):
        if self.CDIndex != None:
            return len(self.CDs[self.CDIndex].songs)
        return None
        
            
#audioPlayer = AudioPlayer("C:\\Users\\Trevor\\Music\\VR CDS")

#ap = AudioPlayer("C:\\Users\\Trevor\\Music\\VR CDS")
