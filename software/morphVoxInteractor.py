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
            -4:0x4f,
            -3:0x50,
            -2:0x51,
            -1:0x4b,
            1:0x4c,
            2:0x4d,
            3:0x47,
            4:0x48,
            }

        self.toggle_morph_key = 0x49
        self.toggle_mute_key = 0x52
        
        #time.sleep(4)
        #morph_vox_hwnd = win32gui.FindWindow(None,"MorphVOX Pro")

        os.system("taskkill /IM MorphVOXPro.exe")
        time.sleep(1)
        os.startfile("C:\\Program Files (x86)\\Screaming Bee\\MorphVOX Pro\\MorphVOXPro.exe")
        time.sleep(4)

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
                time.sleep(0.025)
                self.set_morphed(be_morphed,reattempts-1)
            
    def set_morph_type(self,morph_level):
        if morph_level in self.morph_keys.keys():
            key_press(self.morph_keys[morph_level])
            self.set_morphed(True)
        elif not morph_level:
            self.set_morphed(False)
