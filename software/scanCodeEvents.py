import ctypes
import time

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (('dx', ctypes.c_long),
                ('dy', ctypes.c_long),
                ('mouseData', ctypes.c_ulong),
                ('dwFlags', ctypes.c_ulong),
                ('time', ctypes.c_ulong),
                ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong)))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (('wVk', ctypes.c_ushort),
                ('wScan', ctypes.c_ushort),
                ('dwFlags', ctypes.c_ulong),
                ('time', ctypes.c_ulong),
                ('dwExtraInfo', ctypes.POINTER(ctypes.c_ulong)))

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (('uMsg', ctypes.c_ulong),
                ('wParamL', ctypes.c_ushort),
                ('wParamH', ctypes.c_ushort))
    
class _INPUTunion(ctypes.Union):
    _fields_ = (('mi', MOUSEINPUT),
                ('ki', KEYBDINPUT),
                ('hi', HARDWAREINPUT))

class INPUT(ctypes.Structure):
    _fields_ = (('type', ctypes.c_ulong),
                ('union', _INPUTunion))

def send_input(*inputs):
    nInputs = len(inputs)
    LPINPUT = INPUT * nInputs
    pInputs = LPINPUT(*inputs)
    cbSize = ctypes.c_int(ctypes.sizeof(INPUT))
    return ctypes.windll.user32.SendInput(nInputs, pInputs, cbSize)

INPUT_KEYBOARD = 1

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

def key_input(code,flags):
    kbinp = KEYBDINPUT(0, code, flags, 0,None)
    inp = INPUT(
        INPUT_KEYBOARD,
        _INPUTunion(ki = kbinp)
        )

def key_up(scan_code,extra_flags):
    if not extra_flags: extra_flags = 0
    key_input(scan_code, KEYEVENTF_KEYUP | extra_flags) #KEYEVENTF_SCANCODE |

def key_down(scan_code,extra_flags):
    if not extra_flags: extra_flags = 0
    key_input(scan_code,extra_flags) #

def key_press(scan_code,press_time=0.01,extra_flags=KEYEVENTF_SCANCODE):
    key_down(scan_code,extra_flags)
    time.sleep(press_time)
    key_up(scan_code,extra_flags)
