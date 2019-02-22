import subprocess

si = subprocess.STARTUPINFO()
si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

class Balcon(object):
    def __init__(self, path='C:\\Users\\Trevor\\Documents\\MicTools\\balcon\\balcon.exe', volume=100, speed=5, device=''):
        self.path = path
        self.volume = volume
        self.speed = speed
        self.device = device

    def say(self,text,cutoff=False):
        cmd_inp = self.path +' -s ' + str(self.speed) + ' -v ' + str(self.volume) + ' -t "' + text + '"'
        subprocess.call(cmd_inp, startupinfo=si)
