'''
ABOUT:
reads memory values relating to MorphVOX Pro to verify the program is in the desired state

IMPORTANT METHODS:
is_muted - whether the user's mic is muted
is_morphing - whether the user's voice is being morphed

REQUIREMENTS:
- must be running morph vox pro version 

TODO:
add is_listening - whether the user's voice is being played back to them
'''

#Used to get pid by process name
from subprocess import check_output

#Used to read memory values
from ctypes import *
from ctypes.wintypes import *

#Used to convert memory values
import struct

#Used to get address of dll within process
import win32process

import errorTypes

import math as m


###### get the process id of the Minecraft process
def get_pid(proc_name):
    '''
    get pid by process name
    '''
    cmd_output = check_output('tasklist /fi "Imagename eq '+ proc_name +'"')
    return int(cmd_output.split()[14])

###### find the handle of the Minecraft process

PROCESS_ALL_ACCESS = 0x1F0FFF
#PROCESS_VM_READ = 0x0010

###### find the memory address of the desired MorphVox process module (MorphSupport.dll for information on whether is muted & morphing)

Psapi = ctypes.WinDLL('Psapi.dll')
LIST_MODULES_ALL = 0x03

def EnumProcessModulesEx(hProcess):
    buf_count = 256
    while True:
        buf = (HMODULE * buf_count)()
        buf_size = sizeof(buf)
        needed = DWORD()
        if not Psapi.EnumProcessModulesEx(hProcess, byref(buf), buf_size,
                                          byref(needed), LIST_MODULES_ALL):
            raise OSError('EnumProcessModulesEx failed')
        if buf_size < needed.value:
            buf_count = needed.value // (buf_size // buf_count)
            continue
        count = needed.value // (buf_size // buf_count)
        return map(HMODULE, buf[:count])

def GetModuleFileNameEx(hProcess, hModule):
    buf = create_unicode_buffer(MAX_PATH)
    nSize = DWORD()
    if not Psapi.GetModuleFileNameExW(hProcess, hModule,
                                      byref(buf), byref(nSize)):
        raise OSError('GetModuleFileNameEx failed')
    return buf.value

def print_module_names(process,sep='\n'):
    '''
    just to help find names
    '''
    print( *[hex(int.from_bytes(bytes(a),'little')) + '\t- ' + str(GetModuleFileNameEx(processHandle,a)) + sep for a in list(EnumProcessModulesEx(processHandle))])
    
    
def get_module_addr(process,name):
    '''
    get address of module by name that is a member of process
    '''
    modules = list(EnumProcessModulesEx(process))
    for m in modules:
        if name in str(GetModuleFileNameEx(process,m)):
            return int.from_bytes(bytes(m),'little')

###### find player position x and camera rotation y relative to desired modules
ReadProcessMemory = windll.kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [HANDLE,LPCVOID,LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
ReadProcessMemory.rettype = BOOL

type_sizes = {'f':4, 'l':4, 'q':8} #idk if q would behave
def get_val(process,addr,typ):
    '''
    get value from processHandler starting at address of type
    '''
    buffer = c_void_p()
    bufferSize = type_sizes[typ]
    bytesRead = c_size_t()
    while not ReadProcessMemory(process, addr, byref(buffer), bufferSize, byref(bytesRead)):
        print ("Failed to read",process,hex(addr),typ)
    if buffer.value == None:
        return 0
    return struct.unpack(typ, struct.pack("I", buffer.value)   )[0]

class THREADENTRY32(Structure):
    _fields_ = [
        ('dwSize' , c_long ),
        ('cntUsage' , c_long),
        ('th32ThreadID' , c_long),
        ('th32OwnerProcessID' , c_long),
        ('tpBasePri' , c_long),
        ('tpDeltaPri' , c_long),
        ('dwFlags' , c_long) ]

def get_tid(proc_id):
    '''
    get the ids of processes's threads
    (This function is only the first step of reading a base pointer relative to a threadstack)
    haven't needed to do but steps are as follows https://stackoverflow.com/questions/48237813/
    
    - Get the id of each thread (wew)
    - Get a Handle to the thread: Use OpenThread() 
    - import NtQueryInformationThread which is an undocumented function exported by ntdll.dll
    - call NtQueryInformationThread() with the thread handle in the first argument and ThreadBasicInformation as the second. The result is a THREAD_BASIC_INFORMATION structure with member variable StackBase.
    - StackBase is the address of THREADSTACK, just match it with the correct id. 
    
    '''
    hSnapshot = c_void_p(0)
    te32 = THREADENTRY32 ()
    te32.dwSize = sizeof(THREADENTRY32 )

    hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD,0)
        
    thr_ids = []
    
    ret = Thread32First(hSnapshot, pointer(te32))
    if ret == 0:
        CloseHandle(hSnapshot)
        return false
    
    while ret :
        if te32.th32OwnerProcessID == proc_id:
            #print('thr_id',te32.th32ThreadID, '  tpBasePri',te32.tpBasePri,'  tpDeltaPri',te32.tpDeltaPri, '  cntUsage',te32.cntUsage,'  dwSize',te32.dwSize  )
            thr_ids.append( te32.th32ThreadID)
        ret = Thread32Next(hSnapshot, pointer(te32))
    return thr_ids
