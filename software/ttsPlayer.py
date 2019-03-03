import subprocess
import threading

si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

class Narration():
    def __init__(self,text,skip):
        self.text = text
        self.skip = skip
        self.playing = False

class Balcon(object):
    def __init__(self, path='..\\balcon\\balcon.exe', volume=100, speed=5, device=None):
        self.path = path
        self.volume = volume
        self.speed = speed
        self.device = device
        self.is_running = False
        self.prev_narrations = []
        self.buff_narrations = []

    def gen_cmd(self,text,cutoff=False):
        cmd_inp = self.path +' -s ' + str(self.speed) + ' -v ' + str(self.volume)
        if self.device:
            cmd_inp += ' -r ' + self.device
        if cutoff:
            cmd_inp += ' -k '
        cmd_inp += ' -t "' + text + '"'
        return cmd_inp

    def say(self,text,cutoff=False):
        def thread_target():
            subprocess.call( self.gen_cmd(text,cuttoff), startupinfo=si )
            self.is_running = False
        self.is_running = True
        thread = threading.Thread(target=thread_target)
        thread.start()

    def narrate_buffer(self,narration,cutoff=False):
        def thread_target():
            subprocess.call( self.gen_cmd(narration.text,cutoff), startupinfo=si )
            index = self.buff_narrations.index(narration)
            if len(self.buff_narrations) > index + 1 and not self.buff_narrations[index+1].playing:
                self.narrate_buffer(self.buff_narrations[index+1],cutoff=False)
            self.buff_narrations.remove(narration)
        narration.playing = True
        thread = threading.Thread(target=thread_target)
        thread.start()

        
                
        

    def add_narration(self,text,skip=None):
        cutoff=False
        while len(self.buff_narrations) > 0 and \
            self.buff_narrations[-1].skip == skip != None and \
            not self.buff_narrations[-1].playing:
                del self.buff_narrations[-1]
        
        if len(self.buff_narrations) and self.buff_narrations[-1].playing and self.buff_narrations[-1].skip == skip != None:
                cutoff = True
        narration = Narration(text,skip)
        self.buff_narrations.append(narration)
        if cutoff or len(self.buff_narrations) == 1:
            self.narrate_buffer(narration,cutoff)
        
