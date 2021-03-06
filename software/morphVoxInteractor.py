import os
import time

from memoryReader import *
from scanCodeEvents import *

#import win32gui

#morph_vox_hwnd = None

class MorphVox(object):
    def __init__(self,path="C:\\Program Files (x86)\\Screaming Bee\\MorphVOX Pro\\MorphVOXPro.exe"):
        #global more_vox_hwnd
        
        self.morph_keys={
            'tough':0x4f,
            'troll':0x50,
            'demon':0x53, #51

            'nerd':0x4b,
            'girl':0x4c,
            'child':0x4d,
            
            'alien':0x47,
            'radio':0x48,
            'echo':0x49,

            'robot':0x51,
            'shade':0x4A,
            #'cavern':0x53
            }

        self.toggle_mute_key = 0x35

        self.toggle_morph_key = 0x52

        os.system("taskkill /IM MorphVOXPro.exe")
        time.sleep(1)
        os.startfile("C:\\Program Files (x86)\\Screaming Bee\\MorphVOX Pro\\MorphVOXPro.exe")
        time.sleep(5)

        self.pid = get_pid('MorphVOXPro.exe')
        print('pid',self.pid)
        self.process_handle = windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, self.pid)
        print('proc handle',self.process_handle)
        self.morph_support_addr = get_module_addr(self.process_handle,"MorphSupport.dll")
        print('morph supp addr',self.morph_support_addr)

    def is_muted(self):
        val = get_val(self.process_handle,self.morph_support_addr + 0x79438,'l')
        if val == 0:
            return True
        elif val == 1:
            return False
        raise errorTypes.MemReadError()

    def set_muted(self,be_mute=False,reattempts=1):
        if self.is_muted() != be_mute:
            key_press(self.toggle_mute_key)
            if reattempts:
                time.sleep(0.025)
                self.set_muted(be_mute,reattempts-1)

    def is_morphed(self):
        val = get_val(self.process_handle,self.morph_support_addr + 0x82458,'l')
        if val == 0:
            return True
        elif val == 1:
            return False
        raise errorTypes.MemReadError()

    def set_morphed(self,be_morphed=False,reattempts=1):
        if self.is_morphed() != be_morphed:
            key_press(self.toggle_morph_key)
            if reattempts:
                print('reattempt morph')
                time.sleep(0.025)
                self.set_morphed(be_morphed,reattempts-1)
            
    def set_morph_type(self,morph_level):
        if morph_level in self.morph_keys.keys():
            key_press(self.morph_keys[morph_level])
            time.sleep(0.05)
            self.set_morphed(True)
        elif not morph_level:
            self.set_morphed(False)
