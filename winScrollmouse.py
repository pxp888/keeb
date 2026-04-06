import ctypes
from ctypes import wintypes
import configparser
import os
import sys
import queue
import threading

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# --- Win32 Constants & Types ---
IS_64BIT = ctypes.sizeof(ctypes.c_void_p) == 8
LRESULT = ctypes.c_longlong if IS_64BIT else ctypes.c_long
WPARAM  = ctypes.c_ulonglong if IS_64BIT else wintypes.WPARAM
LPARAM  = ctypes.c_longlong if IS_64BIT else wintypes.LPARAM

# SendInput Constants
INPUT_MOUSE = 0
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000

# Raw Input Constants
RIDEV_INPUTSINK = 0x00000100
RID_INPUT = 0x10000003
WM_INPUT = 0x00FF

class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [
        ("dwType", wintypes.DWORD),
        ("dwSize", wintypes.DWORD),
        ("hDevice", wintypes.HANDLE),
        ("wParam", wintypes.WPARAM),
    ]

class RAWMOUSE(ctypes.Structure):
    class _U1(ctypes.Union):
        class _S2(ctypes.Structure):
            _fields_ = [
                ("usButtonFlags", wintypes.USHORT),
                ("usButtonData", wintypes.USHORT),
            ]
        _fields_ = [
            ("ulButtons", wintypes.ULONG),
            ("s", _S2),
        ]
    _fields_ = [
        ("usFlags", wintypes.USHORT),
        ("u1", _U1),
        ("ulRawButtons", wintypes.ULONG),
        ("lLastX", wintypes.LONG),
        ("lLastY", wintypes.LONG),
        ("ulExtraInformation", wintypes.ULONG),
    ]

class RAWINPUT(ctypes.Structure):
    _fields_ = [
        ("header", RAWINPUTHEADER),
        ("mouse", RAWMOUSE),
    ]

class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [
        ("usUsagePage", wintypes.USHORT),
        ("usUsage", wintypes.USHORT),
        ("dwFlags", wintypes.DWORD),
        ("hwndTarget", wintypes.HWND),
    ]

# Standard structures for hooks and input
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]

class _INPUTunion(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", _INPUTunion),
    ]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", wintypes.POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]

# Function Definitions
user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT

user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, WPARAM, LPARAM]
user32.CallNextHookEx.restype = LRESULT

user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]
user32.DefWindowProcW.restype = LRESULT

user32.GetRawInputData.argtypes = [wintypes.HANDLE, wintypes.UINT, ctypes.c_void_p, ctypes.POINTER(wintypes.UINT), wintypes.UINT]
user32.GetRawInputData.restype = wintypes.UINT

user32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID]
user32.CreateWindowExW.restype = wintypes.HWND

LowLevelMouseProc = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, WPARAM, LPARAM)
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, WPARAM, LPARAM)
PHANDLER_ROUTINE = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)

# --- Define API calls with proper types ---
kernel32.SetConsoleCtrlHandler.argtypes = [PHANDLER_ROUTINE, wintypes.BOOL]
kernel32.SetConsoleCtrlHandler.restype = wintypes.BOOL

# --- Global State ---
WH_MOUSE_LL = 14
WM_MOUSEMOVE = 0x0200
INI_PATH = './winScrollmode.ini'
hook_id = None
scroll_mode = False
scroll_queue = queue.Queue()

# Config defaults
TOGGLE_MESSAGE = 0x020B 
TOGGLE_MOUSEDATA = 1    
TOGGLE_UP_MESSAGE = 0x020C
V_SCALE = 40
H_SCALE = 20
handler_delegate = None
cb = None
wnd_proc_delegate = None

def scroll_worker():
    v_acc = 0
    h_acc = 0
    while True:
        try:
            task = scroll_queue.get()
            if task is None: break
            if task == "RESET":
                v_acc = 0
                h_acc = 0
                scroll_queue.task_done()
                continue
                
            dx, dy = task
            # Accumulate the movement scaled by our sensitivity
            v_acc += -dy * V_SCALE
            h_acc += dx * H_SCALE
            
            # Flush vertical pulses (120 units is one standard notch)
            while abs(v_acc) >= 120:
                pulse = 120 if v_acc > 0 else -120
                mouse_data = ctypes.c_ulong(pulse).value
                mi = MOUSEINPUT(0, 0, mouse_data, MOUSEEVENTF_WHEEL, 0, None)
                inp = INPUT(INPUT_MOUSE, _INPUTunion(mi=mi))
                user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
                v_acc -= pulse
                
            # Flush horizontal pulses
            while abs(h_acc) >= 120:
                pulse = 120 if h_acc > 0 else -120
                mouse_data_h = ctypes.c_ulong(pulse).value
                mi = MOUSEINPUT(0, 0, mouse_data_h, MOUSEEVENTF_HWHEEL, 0, None)
                inp = INPUT(INPUT_MOUSE, _INPUTunion(mi=mi))
                user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
                h_acc -= pulse
                
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
        
        global V_SCALE, H_SCALE
        V_SCALE = int(config['config'].get('VScale', 120))
        H_SCALE = int(config['config'].get('HScale', 120))
        
        print(f"Loaded config: MSG={hex(TOGGLE_MESSAGE)}, DATA={TOGGLE_MOUSEDATA}, VScale={V_SCALE}, HScale={H_SCALE}")
    except KeyError:
        print("Invalid config file.")
        sys.exit(1)

def hook_callback(nCode, wParam, lParam):
    global scroll_mode
    if nCode < 0:
        return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

    event = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
    if event.flags & 1: 
        return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

    mouseData = event.mouseData >> 16
    if wParam == TOGGLE_MESSAGE and (TOGGLE_MOUSEDATA == 0 or mouseData == TOGGLE_MOUSEDATA):
        scroll_mode = not scroll_mode
        if scroll_mode:
            scroll_queue.put("RESET")
            print("Scroll mode ON (Raw Input)")
        else:
            print("Scroll mode OFF")
        return 1

    if wParam == TOGGLE_UP_MESSAGE and (TOGGLE_MOUSEDATA == 0 or mouseData == TOGGLE_MOUSEDATA):
        return 1

    if scroll_mode and wParam == WM_MOUSEMOVE:
        # Suppress standard cursor movement
        return 1
        
    return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

def wnd_proc(hwnd, msg, wParam, lParam):
    if msg == WM_INPUT:
        size = wintypes.UINT()
        # Get required size
        user32.GetRawInputData(ctypes.cast(lParam, wintypes.HANDLE), RID_INPUT, None, ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER))
        
        if size.value > 0:
            raw_buffer = (ctypes.c_byte * size.value)()
            user32.GetRawInputData(ctypes.cast(lParam, wintypes.HANDLE), RID_INPUT, ctypes.byref(raw_buffer), ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER))
            
            raw = RAWINPUT.from_buffer(raw_buffer)
            if scroll_mode and raw.header.dwType == 0: # RIM_TYPEMOUSE
                dx = raw.mouse.lLastX
                dy = raw.mouse.lLastY
                if dx != 0 or dy != 0:
                    scroll_queue.put((dx, dy))
                    
    return user32.DefWindowProcW(hwnd, msg, wParam, lParam)

def ctrl_handler(ctrl_type):
    """
    Handles console control events (Ctrl+C, closing the window, logging off, etc.)
    Ensures that we post a quit message so GetMessage can exit and the hook can be removed.
    """
    if ctrl_type in (0, 2): # CTRL_C_EVENT or CTRL_CLOSE_EVENT
        print("\nShutdown signal received. Cleaning up...")
        user32.PostQuitMessage(0)
        return True # Handled
    return False

def main():
    global hook_id
    load_config()
    
    # Start the scroll event injection thread
    t = threading.Thread(target=scroll_worker, daemon=True)
    t.start()
    
    # Register a hidden window to receive WM_INPUT
    hinst = kernel32.GetModuleHandleW(None)
    
    WNDCLASSEX = type("WNDCLASSEX", (ctypes.Structure,), {
        "_fields_": [
            ("cbSize", wintypes.UINT),
            ("style", wintypes.UINT),
            ("lpfnWndProc", WNDPROC),
            ("cbClsExtra", ctypes.c_int),
            ("cbWndExtra", ctypes.c_int),
            ("hInstance", wintypes.HINSTANCE),
            ("hIcon", wintypes.HANDLE),
            ("hCursor", wintypes.HANDLE),
            ("hbrBackground", wintypes.HANDLE),
            ("lpszMenuName", wintypes.LPCWSTR),
            ("lpszClassName", wintypes.LPCWSTR),
            ("hIconSm", wintypes.HANDLE),
        ]
    })
    
    global wnd_proc_delegate
    wnd_proc_delegate = WNDPROC(wnd_proc) # Keep reference alive
    
    wc = WNDCLASSEX()
    wc.cbSize = ctypes.sizeof(WNDCLASSEX)
    wc.lpfnWndProc = wnd_proc_delegate
    wc.hInstance = hinst
    wc.lpszClassName = "RawInputReceiver"
    
    user32.RegisterClassExW(ctypes.byref(wc))
    
    hwnd = user32.CreateWindowExW(
        0, wc.lpszClassName, "RawInputMsgWindow", 0,
        0, 0, 0, 0,
        0, 0, hinst, None
    )
    
    if not hwnd:
        print("Failed to create hidden window for Raw Input")
        return

    # Register for Raw Input (Mouse)
    rid = RAWINPUTDEVICE()
    rid.usUsagePage = 0x01
    rid.usUsage = 0x02
    rid.dwFlags = RIDEV_INPUTSINK # Receive even when focus is lost
    rid.hwndTarget = hwnd
    if not user32.RegisterRawInputDevices(ctypes.byref(rid), 1, ctypes.sizeof(rid)):
        print("Failed to register Raw Input devices")
        return
    
    # Register console control handler to catch window 'X' close
    global handler_delegate
    handler_delegate = PHANDLER_ROUTINE(ctrl_handler)
    if not kernel32.SetConsoleCtrlHandler(handler_delegate, True):
        print("Failed to set console control handler")
        return

    # Set the global hook for cursor suppression
    global cb
    cb = LowLevelMouseProc(hook_callback)
    hook_id = user32.SetWindowsHookExW(WH_MOUSE_LL, cb, None, 0)
    
    if not hook_id:
        print("Failed to set suppression hook")
        return

    print("Scrollmode active using Raw Input. (Ctrl+C to stop)")
    msg = wintypes.MSG()
    try:
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
    except KeyboardInterrupt:
        pass
    finally:
        if hook_id:
            user32.UnhookWindowsHookEx(hook_id)
            print("Successfully unhooked mouse. Exit clean.")

if __name__ == "__main__":
    main()
