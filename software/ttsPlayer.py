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

    def say(self,text,cutoff=False):
        def thread_target():
            cmd_inp = self.path +' -s ' + str(self.speed) + ' -v ' + str(self.volume)
            if self.device:
                cmd_inp += ' -r ' + self.device
            if cutoff:
                cmd_inp += ' -k '
            cmd_inp += ' -t "' + text + '"'
            subprocess.call(cmd_inp, startupinfo=si)

        thread = threading.Thread(target=thread_target)
        thread.start()
