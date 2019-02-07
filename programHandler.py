from pynput import keyboard
import win32api# as win32api
import win32gui# as win32gui
import win32com
import win32con
import win32process
import subprocess
import time
import os

controller = keyboard.Controller()

in_search_menu = False #in foobars search input
in_tts = False #in text to speech program input box

foob_hwnd = None
tts_hwnd = None
voice_meeter_hwnd = None
morph_vox_hwnd = None
all_hwnd = {}
mode = None

def enumHandler(hwnd, lParam):
    
    global foob_hwnd, tts_hwnd,morph_vox_hwnd,voice_meeter_hwnd, all_hwnd
    if win32gui.IsWindowVisible(hwnd):
        win_txt = win32gui.GetWindowText(hwnd)
        all_hwnd[win_txt] = hwnd
        if 'foobar2000 v1.4' in win_txt or '  [foobar2000]' in win_txt:
            foob_hwnd = hwnd
        elif 'Balabolka - [' in win_txt:# - [
            tts_hwnd = hwnd
        elif 'MorphVOX Pro' in win_txt:
            morph_vox_hwnd = hwnd
        elif 'VoiceMeeter' in win_txt:
            voice_meeter_hwnd = hwnd

def key_down_event(key):
    win32api.keybd_event(key, 0,0,0)

def key_up_event(key):
    win32api.keybd_event(key, 0,win32con.KEYEVENTF_KEYUP ,0)

def press_key(vk,delay=0.01):
    key_down_event(vk)
    time.sleep(delay)
    key_up_event(vk);

last_hwnd = None
def send_to_front(hwnd,require_restore=False):
    '''
    send a window to front

    Keyword Arguments:
    hwnd -- The handle of the window
    require_resore -- whether or not the window needs to be restored too
    '''
    global last_hwnd
    last_hwnd = win32gui.GetForegroundWindow()
    if require_restore:
        win32gui.ShowWindow(hwnd,9)
    win32gui.ShowWindow(hwnd,5)
    win32gui.SetForegroundWindow(hwnd)
    '''
    win32gui.SystemParametersInfo(win32con.SPI_SETFOREGROUNDLOCKTIMEOUT, 0, win32con.SPIF_SENDWININICHANGE | win32con.SPIF_UPDATEINIFILE)
    last_hwnd = win32gui.GetForegroundWindow()    #print('sending',hwnd,'to front')#print('fgwin',fgwin)
    fg = win32process.GetWindowThreadProcessId(last_hwnd)[0]
    current = win32api.GetCurrentThreadId()
    if current != fg:
        win32process.AttachThreadInput(fg, current, True)
        if require_restore:
            win32gui.ShowWindow(hwnd,9)#restore
        win32gui.SetForegroundWindow(hwnd)
        win32process.AttachThreadInput(fg, win32api.GetCurrentThreadId(), False)
        '''
    
def perform_search_shortcut():
    '''
    presses ctrl+f
    '''
    key_down_event(VK_CODE['ctrl'])
    time.sleep(0.01)
    key_down_event(VK_CODE['f'])
    time.sleep(0.01)
    key_up_event(VK_CODE['f'])
    time.sleep(0.01)
    key_up_event(VK_CODE['ctrl'])

def perform_switch_to_last(backDepth=1):
    '''
    presses alt+tab
    '''
    key_down_event(VK_CODE['alt'])
    for i in range(backDepth):
        key_down_event(VK_CODE['tab'])
        time.sleep(0.025)
        key_up_event(VK_CODE['tab'])
        time.sleep(0.025)
    key_up_event(VK_CODE['alt'])

def search_foob_act():
    '''
    allows the user to type the audio they want to play
    '''
    global in_search_menu
    send_to_front(foob_hwnd,False)
    time.sleep(0.1)
    perform_search_shortcut()
    in_search_menu = True

def finish_search_foob_act():
    '''
    readys the audio to be played and brings the user back to their application
    '''
    global in_search_menu
    press_key(VK_CODE['esc'])
    time.sleep(0.1)
    press_key(VK_CODE['stop_media'])
    time.sleep(0.1)
    send_to_front(last_hwnd,True)
    in_search_menu = False

def input_tts_act():
    '''
    allows the user to type the text they want to be spoken
    '''
    global in_tts
    send_to_front(tts_hwnd,True)
    in_tts = True

def finish_tts_act():
    '''
    brings the user back to their application
    '''
    global in_tts
    in_tts = False
    press_key(VK_CODE['backspace'])
    press_key(VK_CODE['page_up'])
    press_key(VK_CODE['home'])
    send_to_front(last_hwnd,True)
            
def boot_programs(use_balabolka=True):
    '''
    boots the mic enhancement programs
    '''
    if use_balabolka:
        print("Starting 'Balabolka' text to speech...")
        os.startfile("C:\\Program Files (x86)\\Balabolka\\balabolka.exe")
    
    print("Starting 'Voice Meeter' audio mixer...")
    os.startfile("C:\\Program Files (x86)\\VB\\Voicemeeter\\voicemeeterpro.exe")

    print("Starting 'morph vox pro' voice effects...")
    os.startfile("C:\\Program Files (x86)\\Screaming Bee\\MorphVOX Pro\\MorphVOXPro.exe")

    print("Starting 'Foobar2000' audio player...")
    os.startfile("C:\\Program Files (x86)\\foobar2000\\foobar2000.exe")

def close_programs(use_balabolka=True):
    '''
    closes the mic enhancement programs
    '''
    if use_balabolka:
        print("Closing 'Balabolka' text to speech...")
        os.system("taskkill /T /F /IM balabolka.exe")
    
    print("Closing 'Voice Meeter' audio mixer...")
    os.system("taskkill /IM voicemeeterpro.exe")
    
    print("Closing 'morph vox pro' voice effects...")
    os.system("taskkill /IM MorphVOXPro.exe")
    
    print("Closing 'Foobar2000' audio player...")
    os.system("taskkill /IM foobar2000.exe")

import ctypes, sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run(use_balabolka=True):
    '''
    initialises programs

    Keyword Argument:
    use_balabolka -- whether or not to launch balabolka
    '''
    close_programs(use_balabolka)
    time.sleep(3.5)
    boot_programs(use_balabolka)
    print('\nGathering hwnds...\n--------------------')
    time.sleep(3)

    for i in range(20):
        win32gui.EnumWindows(enumHandler, None)    
        print('foob:',foob_hwnd)
        print('tts:',tts_hwnd)
        print('voice meeter:',voice_meeter_hwnd)
        print('morph vox:',morph_vox_hwnd)
        print('--------------------')	
        if (foob_hwnd and (tts_hwnd or not use_balabolka) and voice_meeter_hwnd and morph_vox_hwnd):
            #win32gui.MoveWindow(foob_hwnd,2515, 279, 570, 1014, 1)
            #win32gui.MoveWindow(tts_hwnd,1678, 261, 2467-1625, 602-270,1)
            #win32gui.MoveWindow(voice_meeter_hwnd,-261, 811, 955, 1751, 1)
            #win32gui.MoveWindow(morph_vox_hwnd,1681-70, 800, 6, 6, 1)
            #win32gui.ShowWindow(tts_hwnd,5)
            #win32gui.ShowWindow(foob_hwnd,5)
            
            break
        time.sleep(1)	
    else:
        print('DID NOT DETECT ALL PROGRAMS!!!')

####################################
'''
run()
send_to_front(morph_vox_hwnd)
send_to_front(tts_hwnd)
send_to_front(foob_hwnd)
'''
