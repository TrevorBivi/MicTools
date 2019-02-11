from pynput import keyboard
import win32api# as win32api
import win32gui# as win32gui
import win32com
import win32con
import win32process
import subprocess
import time
import os

VK_CODE = {'backspace':0x08,
           'tab':0x09,
           'clear':0x0C,
           'enter':0x0D,
           'shift':0x10,
           'ctrl':0x11,
           'alt':0x12,
           'pause':0x13,
           'caps_lock':0x14,
           'esc':0x1B,
           ' ':0x20,
           'page_up':0x21,
           'page_down':0x22,
           'end':0x23,
           'home':0x24,
           'left_arrow':0x25,'up_arrow':0x26,'right_arrow':0x27,'down_arrow':0x28,
           'select':0x29,
           'print':0x2A,
           'execute':0x2B,
           'print_screen':0x2C,
           'ins':0x2D,
           'del':0x2E,
           'help':0x2F,
           '0':0x30,'1':0x31,'2':0x32,'3':0x33,'4':0x34,'5':0x35,'6':0x36,'7':0x37,'8':0x38,'9':0x39,
           'a':0x41,'b':0x42,'c':0x43,'d':0x44,'e':0x45,'f':0x46,'g':0x47,'h':0x48,'i':0x49,'j':0x4A,'k':0x4B,'l':0x4C,'m':0x4D,
           'n':0x4E,'o':0x4F,'p':0x50,'q':0x51,'r':0x52,'s':0x53,'t':0x54,'u':0x55,'v':0x56,'w':0x57,'x':0x58,'y':0x59,'z':0x5A,
           'numpad_0':0x60,'numpad_1':0x61,'numpad_2':0x62,'numpad_3':0x63,'numpad_4':0x64,
           'numpad_5':0x65,'numpad_6':0x66,'numpad_7':0x67,'numpad_8':0x68,'numpad_9':0x69,
           'multiply_key':0x6A,
           'add_key':0x6B,
           'separator_key':0x6C,
           'subtract_key':0x6D,
           'decimal_key':0x6E,
           'divide_key':0x6F,
           'F1':0x70,'F2':0x71,'F3':0x72,'F4':0x73,'F5':0x74,'F6':0x75,'F7':0x76,'F8':0x77,'F9':0x78,'F10':0x79,'F11':0x7A,'F12':0x7B,
           'F13':0x7C,'F14':0x7D,'F15':0x7E,'F16':0x7F,'F17':0x80,'F18':0x81,'F19':0x82,'F20':0x83,'F21':0x84,'F22':0x85,'F23':0x86,'F24':0x87,
           'num_lock':0x90,
           'scroll_lock':0x91,
           'left_shift':0xA0,'right_shift ':0xA1,
           'left_control':0xA2,'right_control':0xA3,
           'left_menu':0xA4,'right_menu':0xA5,
           'browser_back':0xA6,'browser_forward':0xA7,'browser_refresh':0xA8,'browser_stop':0xA9,'browser_search':0xAA,'browser_favorites':0xAB,'browser_start_and_home':0xAC,
           'volume_mute':0xAD,'volume_Down':0xAE,'volume_up':0xAF,
           'next_track':0xB0,'previous_track':0xB1,
           'stop_media':0xB2,'play/pause_media':0xB3,
           'start_mail':0xB4,
           'select_media':0xB5,
           'start_application_1':0xB6,
           'start_application_2':0xB7,
           'attn_key':0xF6,
           'crsel_key':0xF7,
           'exsel_key':0xF8,
           'play_key':0xFA,
           'zoom_key':0xFB,
           'clear_key':0xFE,
           '=':0xBB,
           ',':0xBC,
           '-':0xBD,
           '.':0xBE,
           '/':0xBF,
           '`':0xC0,
           ';':0xBA,
           '[':0xDB,
           '\\':0xDC,
           ']':0xDD,
           "'":0xDE,
}

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
    #os.startfile("C:\\Program Files (x86)\\Screaming Bee\\MorphVOX Pro\\MorphVOXPro.exe")

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
    #os.system("taskkill /IM voicemeeterpro.exe")
    
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

def runPrograms(use_balabolka=True):
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
