import ctypes
from ctypes import wintypes
import configparser

user32 = ctypes.windll.user32

WH_MOUSE_LL = 14
WM_LBUTTONDOWN = 0x0201
WM_RBUTTONDOWN = 0x0204
WM_MBUTTONDOWN = 0x0207
WM_XBUTTONDOWN = 0x020B

INI_PATH = './winScrollmode.ini'

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("pt", wintypes.POINT),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]

LowLevelMouseProc = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, ctypes.POINTER(MSLLHOOKSTRUCT))
hook_id = None
recorded_button = None
recorded_mousedata = None

def hook_callback(nCode, wParam, lParam):
    global recorded_button, recorded_mousedata, hook_id

    if nCode < 0:
        return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

    event = lParam.contents
    
    # Ignore injected events
    if event.flags & 1: 
        return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

    # Exclude LBUTTON just in case someone clicks to start
    if wParam in (WM_RBUTTONDOWN, WM_MBUTTONDOWN, WM_XBUTTONDOWN): 
        recorded_button = wParam
        recorded_mousedata = event.mouseData >> 16
        
        button_name = "Unknown"
        if wParam == WM_RBUTTONDOWN: button_name = "Right Click"
        elif wParam == WM_MBUTTONDOWN: button_name = "Middle Click"
        elif wParam == WM_XBUTTONDOWN:
            button_name = f"Mouse {'4' if recorded_mousedata == 1 else '5'} (XBUTTON{recorded_mousedata})"
            
        print(f"\nRecorded button: {button_name}")
        
        # Stop message loop by sending WM_QUIT
        user32.PostQuitMessage(0)
        return 1 # Block this click so it doesn't do anything
        
    return user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

def main():
    global hook_id
    print("Press the desired mouse button now to use as a toggle (Right, Middle, or Side buttons)...")
    
    cb = LowLevelMouseProc(hook_callback)
    hook_id = user32.SetWindowsHookExW(WH_MOUSE_LL, cb, None, 0)
    
    if not hook_id:
        print("Failed to set hook")
        return
        
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))
        
    user32.UnhookWindowsHookEx(hook_id)
    
    if recorded_button is not None:
        config = configparser.ConfigParser()
        config['config'] = {
            'ButtonMessage': str(recorded_button),
            'MouseData': str(recorded_mousedata)
        }
        with open(INI_PATH, 'w') as f:
            config.write(f)
        print(f"Configuration saved to {INI_PATH}!")

if __name__ == "__main__":
    main()
