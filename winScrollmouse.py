import ctypes
from ctypes import wintypes
import configparser
import os
import sys
import queue
import threading

user32 = ctypes.windll.user32

# --- 64-bit Compatibility Fixes ---
IS_64BIT = ctypes.sizeof(ctypes.c_void_p) == 8
LRESULT = ctypes.c_longlong if IS_64BIT else ctypes.c_long
WPARAM  = ctypes.c_ulonglong if IS_64BIT else wintypes.WPARAM
LPARAM  = ctypes.c_longlong if IS_64BIT else wintypes.LPARAM

# Constants for SendInput
INPUT_MOUSE = 0
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]

# We need the union to represent the C/C++ union in INPUT perfectly
class _INPUTunion(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", _INPUTunion),
    ]

# Define exact types for SendInput
user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT

# Define types for CallNextHookEx to prevent stack corruption
user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, WPARAM, LPARAM]
user32.CallNextHookEx.restype = LRESULT

WH_MOUSE_LL = 14
WM_MOUSEMOVE = 0x0200
INI_PATH = './winScrollmode.ini'

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", wintypes.POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]

# The callback signature MUST use LRESULT, WPARAM, and LPARAM correctly for 64-bit
LowLevelMouseProc = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, WPARAM, LPARAM)
hook_id = None

# Config defaults
TOGGLE_MESSAGE = 0x020B 
TOGGLE_MOUSEDATA = 1    
TOGGLE_UP_MESSAGE = 0x020C

scroll_mode = False
last_x, last_y = 0, 0
scroll_queue = queue.Queue()

def scroll_worker():
    vScroll = 0.0
    hScroll = 0.0
    while True:
        try:
            task = scroll_queue.get()
            if task is None: break
            if task == "RESET":
                vScroll, hScroll = 0.0, 0.0
                scroll_queue.task_done()
                continue
                
            dx, dy = task
            vScroll += dy 
            hScroll += dx         
            
            if dy != 0:
                ticks_y = int(vScroll)
                signed_delta = -ticks_y * 120
                mouse_data = ctypes.c_ulong(signed_delta).value
                mi = MOUSEINPUT(0, 0, mouse_data, MOUSEEVENTF_WHEEL, 0, None)
                inp = INPUT(INPUT_MOUSE, _INPUTunion(mi=mi))
                user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
                
            scroll_queue.task_done()
        except Exception as e:
            print(f"Worker Loop Error: {e}")

def load_config():
    global TOGGLE_MESSAGE, TOGGLE_MOUSEDATA, TOGGLE_UP_MESSAGE
    if not os.path.exists(INI_PATH):
        print(f"Config '{INI_PATH}' not found.")
        sys.exit(1)
        
    config = configparser.ConfigParser()
    config.read(INI_PATH)
    try:
        TOGGLE_MESSAGE = int(config['config']['ButtonMessage'])
        TOGGLE_MOUSEDATA = int(config['config']['MouseData'])
        TOGGLE_UP_MESSAGE = TOGGLE_MESSAGE + 1
        print(f"Loaded config: MSG={hex(TOGGLE_MESSAGE)}, DATA={TOGGLE_MOUSEDATA}")
    except KeyError:
        print("Invalid config file.")
        sys.exit(1)

def hook_callback(nCode, wParam, lParam):
    global scroll_mode, last_x, last_y
    
    if nCode < 0:
        return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

    # Cast lParam to the structure pointer
    event = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
    
    # Ignore injected events from ourselves
    if event.flags & 1:
        return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

    mouseData = event.mouseData >> 16

    # Toggle switch
    if wParam == TOGGLE_MESSAGE and (TOGGLE_MOUSEDATA == 0 or mouseData == TOGGLE_MOUSEDATA):
        scroll_mode = not scroll_mode
        if scroll_mode:
            # Use current cursor position as the anchor
            last_x, last_y = event.pt.x, event.pt.y
            scroll_queue.put("RESET")
            print("Scroll mode ON")
        else:
            print("Scroll mode OFF")
        return 1

    if wParam == TOGGLE_UP_MESSAGE and (TOGGLE_MOUSEDATA == 0 or mouseData == TOGGLE_MOUSEDATA):
        return 1

    # Mouse movement in scroll mode
    if scroll_mode and wParam == WM_MOUSEMOVE:
        dx = event.pt.x - last_x
        dy = event.pt.y - last_y
        
        # Always update anchor so deltas stay small (one-pixel steps)
        last_x, last_y = event.pt.x, event.pt.y
        
        if dx != 0 or dy != 0:
            scroll_queue.put((dx, dy))
            
        return 1
        
    return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

def main():
    global hook_id
    load_config()
    
    t = threading.Thread(target=scroll_worker, daemon=True)
    t.start()
    
    print("Starting... (Ctrl+C to quit)")
    cb = LowLevelMouseProc(hook_callback)
    
    # Passing hook_id=0 because it is ignored by CallNextHookEx on modern Windows, 
    # but we will store the real handle for unhooking.
    hook_id = user32.SetWindowsHookExW(WH_MOUSE_LL, cb, None, 0)
    
    if not hook_id:
        print("Failed to set hook")
        return

    msg = wintypes.MSG()
    try:
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    except KeyboardInterrupt:
        pass
    finally:
        user32.UnhookWindowsHookEx(hook_id)

if __name__ == "__main__":
    main()
