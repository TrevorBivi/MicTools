import subprocess
import threading

si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

class Balcon(object):
    def __init__(self, path='..\\balcon\\balcon.exe', volume=100, speed=5, device=None):
        self.path = path
        self.volume = volume
        self.speed = speed
        self.device = device
        self.is_running = False
        
    def gen_cmd(self,text,cutoff=False):
        cmd_inp = self.path +' -s ' + str(self.speed) + ' -v ' + str(self.volume)
        if self.device:
            cmd_inp += ' -r ' + self.device
        if cutoff:
            cmd_inp += ' -k '
        cmd_inp += ' -t "' + text + '"'
        return cmd_inp

    def threadless_say(text,cutoff=False):
        subprocess.call( self.gen_cmd(text,cutoff), startupinfo=si )

    def say(self,text,cutoff=False):
        def thread_target():
            threadless_say(text,cutoff)
            self.is_running = False
        self.is_running = True
        thread = threading.Thread(target=thread_target)
        thread.start()
        
