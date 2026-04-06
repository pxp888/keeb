import ctypes
from ctypes import wintypes
import configparser
import os
import sys
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# --- Win32 Constants & Types ---
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

IS_64BIT = ctypes.sizeof(ctypes.c_void_p) == 8
LRESULT = ctypes.c_longlong if IS_64BIT else ctypes.c_long
WPARAM  = ctypes.c_ulonglong if IS_64BIT else wintypes.WPARAM
LPARAM  = ctypes.c_longlong if IS_64BIT else wintypes.LPARAM

INPUT_MOUSE = 0
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000
WH_MOUSE_LL = 14
WM_MOUSEMOVE = 0x0200
WM_XBUTTONDOWN = 0x020B
WM_XBUTTONUP = 0x020C
WM_INPUT = 0x00FF
RID_INPUT = 0x10000003
RIDEV_INPUTSINK = 0x00000100
WM_QUIT = 0x0012

# Standard Mouse Messages
WM_LBUTTONDOWN = 0x0201
WM_RBUTTONDOWN = 0x0204
WM_MBUTTONDOWN = 0x0207

class RAWINPUTHEADER(ctypes.Structure):
    _fields_ = [("dwType", wintypes.DWORD), ("dwSize", wintypes.DWORD),
                ("hDevice", wintypes.HANDLE), ("wParam", wintypes.WPARAM)]

class RAWMOUSE(ctypes.Structure):
    class _U1(ctypes.Union):
        class _S2(ctypes.Structure):
            _fields_ = [("usButtonFlags", wintypes.USHORT), ("usButtonData", wintypes.USHORT)]
        _fields_ = [("ulButtons", wintypes.ULONG), ("s", _S2)]
    _fields_ = [("usFlags", wintypes.USHORT), ("u1", _U1), ("ulRawButtons", wintypes.ULONG),
                ("lLastX", wintypes.LONG), ("lLastY", wintypes.LONG), ("ulExtraInformation", wintypes.ULONG)]

class RAWINPUT(ctypes.Structure):
    _fields_ = [("header", RAWINPUTHEADER), ("mouse", RAWMOUSE)]

class RAWINPUTDEVICE(ctypes.Structure):
    _fields_ = [("usUsagePage", wintypes.USHORT), ("usUsage", wintypes.USHORT),
                ("dwFlags", wintypes.DWORD), ("hwndTarget", wintypes.HWND)]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_void_p)]

class _INPUTunion(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", _INPUTunion)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", wintypes.POINT), ("mouseData", wintypes.DWORD), ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_void_p)]

# Function Signatures
user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.CallNextHookEx.argtypes = [ctypes.c_void_p, ctypes.c_int, WPARAM, LPARAM]
user32.GetRawInputData.argtypes = [wintypes.HANDLE, wintypes.UINT, ctypes.c_void_p, ctypes.POINTER(wintypes.UINT), wintypes.UINT]
user32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID]
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]
user32.SetWindowsHookExW.argtypes = [wintypes.INT, ctypes.c_void_p, wintypes.HINSTANCE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = wintypes.HANDLE

LowLevelMouseProc = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, WPARAM, LPARAM)
WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, WPARAM, LPARAM)

class ScrollController:
    def __init__(self, root):
        self.root = root
        self.root.title("ScrollMode Control Panel")
        root.geometry("400x480")
        root.configure(bg="#1E1E2E")
        root.resizable(False, False)

        # State
        self.is_active = False
        self.scroll_mode = False
        self.hook_thread = None
        self.hook_thread_id = None
        self.scroll_queue = queue.Queue()
        self.ini_path = './winScrollmode.ini'
        
        # Internal configuration
        self.toggle_msg = 0x020B
        self.toggle_data = 1
        self.v_scale_val = 40
        self.h_scale_val = 20
        
        # TKinter vars
        self.v_scale_str = tk.StringVar(value="40")
        self.h_scale_str = tk.StringVar(value="20")
        self.recording_mode = False

        # Persistent delegates to prevent GC
        self.hook_proc_delegate = LowLevelMouseProc(self.hook_callback)
        self.wnd_proc_delegate = WNDPROC(self.wnd_proc)

        self.load_config()
        self.setup_ui()
        
        # Start injection thread
        threading.Thread(target=self.scroll_worker, daemon=True).start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_config(self):
        if not os.path.exists(self.ini_path): return
        config = configparser.ConfigParser()
        config.read(self.ini_path)
        try:
            if 'config' in config:
                self.toggle_msg = int(config['config'].get('ButtonMessage', 0x020B))
                self.toggle_data = int(config['config'].get('MouseData', 1))
                self.v_scale_val = int(config['config'].get('VScale', 40))
                self.h_scale_val = int(config['config'].get('HScale', 20))
                self.v_scale_str.set(str(self.v_scale_val))
                self.h_scale_str.set(str(self.h_scale_val))
                print(f"[Core] Config Loaded: Msg={hex(self.toggle_msg)}, Data={self.toggle_data}")
        except Exception as e:
            print(f"[Core] Error loading config: {e}")

    def save_config(self):
        try:
            self.v_scale_val = int(self.v_scale_str.get())
            self.h_scale_val = int(self.h_scale_str.get())
        except ValueError:
            messagebox.showwarning("Warning", "Invalid scale value. Please use integers.")
            return

        config = configparser.ConfigParser()
        config['config'] = {
            'ButtonMessage': str(self.toggle_msg),
            'MouseData': str(self.toggle_data),
            'VScale': str(self.v_scale_val),
            'HScale': str(self.h_scale_val)
        }
        with open(self.ini_path, 'w') as f:
            config.write(f)
        print("[Core] Settings Applied and Saved.")

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        colors = {"bg": "#1E1E2E", "card": "#24283B", "accent": "#7AA2F7", "text": "#C0CAF5", "success": "#9ECE6A", "error": "#F7768E", "input_bg": "#16161E"}
        
        style.configure("Main.TFrame", background=colors["bg"])
        style.configure("Card.TFrame", background=colors["card"])
        style.configure("Title.TLabel", background=colors["bg"], foreground=colors["accent"], font=("Segoe UI", 16, "bold"))
        style.configure("Status.TLabel", background=colors["card"], foreground=colors["text"], font=("Segoe UI", 10))
        style.configure("Info.TLabel", background=colors["bg"], foreground=colors["text"], font=("Segoe UI", 9))

        main_frame = ttk.Frame(self.root, style="Main.TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="SCROLL MODE", style="Title.TLabel").pack(pady=(0, 20))

        self.status_var = tk.StringVar(value="Status: Inactive")
        self.toggle_btn = tk.Button(
            main_frame, text="START ENGINE", command=self.toggle_engine,
            bg=colors["accent"], fg="#ffffff", font=("Segoe UI", 12, "bold"),
            relief=tk.FLAT, activebackground=colors["success"], cursor="hand2"
        )
        self.toggle_btn.pack(fill=tk.X, pady=(0, 20))

        card = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        card.pack(fill=tk.BOTH, expand=True)

        ttk.Label(card, text="Toggle Activation Button:", style="Status.TLabel").pack(anchor=tk.W)
        self.btn_name_var = tk.StringVar(value=self.get_button_name())
        self.record_btn = tk.Button(
            card, textvariable=self.btn_name_var, command=self.start_recording,
            bg=colors["input_bg"], fg=colors["text"], relief=tk.FLAT, pady=5, cursor="hand2"
        )
        self.record_btn.pack(fill=tk.X, pady=(5, 15))

        ttk.Label(card, text="Vertical Sensitivity:", style="Status.TLabel").pack(anchor=tk.W)
        tk.Entry(card, textvariable=self.v_scale_str, bg=colors["input_bg"], fg=colors["text"], insertbackground="white", relief=tk.FLAT, font=("Consolas", 11)).pack(fill=tk.X, pady=(5, 15))

        ttk.Label(card, text="Horizontal Sensitivity:", style="Status.TLabel").pack(anchor=tk.W)
        tk.Entry(card, textvariable=self.h_scale_str, bg=colors["input_bg"], fg=colors["text"], insertbackground="white", relief=tk.FLAT, font=("Consolas", 11)).pack(fill=tk.X, pady=(5, 15))

        ttk.Button(card, text="Apply & Save Settings", command=self.save_config).pack(fill=tk.X, pady=(10, 0))

    def get_button_name(self):
        if self.toggle_msg == WM_RBUTTONDOWN: return "Right Click"
        if self.toggle_msg == WM_MBUTTONDOWN: return "Middle Click"
        if self.toggle_msg == WM_XBUTTONDOWN: return f"Mouse {'4' if self.toggle_data == 1 else '5'}"
        return f"Btn {hex(self.toggle_msg)}"

    def start_recording(self):
        if self.recording_mode: return
        print("[Core] Recording starting... Press desired mouse button.")
        self.recording_mode = True
        self.btn_name_var.set("PRESS ANY MOUSE BUTTON...")
        self.record_btn.config(bg="#F7768E")
        if not self.is_active: self.start_hook_thread()

    def toggle_engine(self):
        if self.is_active:
            self.stop_hook_thread()
            self.toggle_btn.config(text="START ENGINE", bg="#7AA2F7")
        else:
            self.start_hook_thread()
            self.toggle_btn.config(text="STOP ENGINE", bg="#F7768E")

    def start_hook_thread(self):
        if self.hook_thread and self.hook_thread.is_alive(): return
        self.is_active = True
        self.hook_thread = threading.Thread(target=self._run_hook_loop, daemon=True)
        self.hook_thread.start()

    def stop_hook_thread(self):
        self.is_active = False
        if self.hook_thread_id:
            user32.PostThreadMessageW(self.hook_thread_id, WM_QUIT, 0, 0)
        self.hook_thread = None

    def _run_hook_loop(self):
        self.hook_thread_id = kernel32.GetCurrentThreadId()
        
        # Set Hook (Try None first as it worked in the crash version)
        h_hook = user32.SetWindowsHookExW(WH_MOUSE_LL, self.hook_proc_delegate, None, 0)
        if not h_hook:
            err = ctypes.get_last_error()
            print(f"[HookThread] Failed to set hook! Error Code: {err} ({ctypes.WinError(err)})")
            # If NULL fails, try with module handle
            h_hook = user32.SetWindowsHookExW(WH_MOUSE_LL, self.hook_proc_delegate, kernel32.GetModuleHandleW(None), 0)
            if not h_hook:
                err2 = ctypes.get_last_error()
                print(f"[HookThread] Retry with ModuleHandle failed too! Code: {err2}")
                return
        
        print(f"[HookThread] Hook set successfully (ID: {hex(h_hook)})")

        # Register window for Raw Input
        class_name = f"ScrollHook_{self.hook_thread_id}"
        wc = type("WNDCLASSEX", (ctypes.Structure,), {"_fields_": [("cbSize", wintypes.UINT), ("style", wintypes.UINT), ("lpfnWndProc", WNDPROC), ("cbClsExtra", ctypes.c_int), ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HANDLE), ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HANDLE), ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR), ("hIconSm", wintypes.HANDLE)]})()
        wc.cbSize, wc.lpfnWndProc, wc.hInstance, wc.lpszClassName = ctypes.sizeof(wc), self.wnd_proc_delegate, kernel32.GetModuleHandleW(None), class_name
        user32.RegisterClassExW(ctypes.byref(wc))
        hwnd = user32.CreateWindowExW(0, class_name, "Hidden", 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)
        
        rid = RAWINPUTDEVICE(0x01, 0x02, RIDEV_INPUTSINK, hwnd)
        user32.RegisterRawInputDevices(ctypes.byref(rid), 1, ctypes.sizeof(rid))

        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnhookWindowsHookEx(h_hook)
        user32.DestroyWindow(hwnd)
        print("[HookThread] Hook unhooked and thread exiting.")

    def hook_callback(self, nCode, wParam, lParam):
        if nCode == 0: # HC_ACTION
            event = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            if event.flags & 1: 
                return user32.CallNextHookEx(None, nCode, wParam, lParam)

            mouse_data = event.mouseData >> 16
            
            if self.recording_mode:
                if wParam in (WM_RBUTTONDOWN, WM_MBUTTONDOWN, WM_XBUTTONDOWN):
                    print(f"[Hook] Recorded: Msg={hex(wParam)}, Data={mouse_data}")
                    self.toggle_msg, self.toggle_data = wParam, mouse_data
                    self.recording_mode = False
                    self.root.after(0, self.update_ui_post_record)
                    return 1

            if self.is_active:
                if wParam == self.toggle_msg and (self.toggle_data == 0 or mouse_data == self.toggle_data):
                    self.scroll_mode = not self.scroll_mode
                    if self.scroll_mode: self.scroll_queue.put("RESET")
                    return 1
                
                # Check for release
                is_release = False
                if wParam == (self.toggle_msg + 1): is_release = True
                elif wParam == WM_XBUTTONUP and self.toggle_msg == WM_XBUTTONDOWN and mouse_data == self.toggle_data: is_release = True
                
                if is_release: return 1

                if self.scroll_mode and wParam == WM_MOUSEMOVE:
                    return 1

        return user32.CallNextHookEx(None, nCode, wParam, lParam)

    def wnd_proc(self, hwnd, msg, wParam, lParam):
        if msg == WM_INPUT:
            size = wintypes.UINT()
            user32.GetRawInputData(ctypes.cast(lParam, wintypes.HANDLE), RID_INPUT, None, ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER))
            if size.value > 0:
                raw_buffer = (ctypes.c_byte * size.value)()
                user32.GetRawInputData(ctypes.cast(lParam, wintypes.HANDLE), RID_INPUT, ctypes.byref(raw_buffer), ctypes.byref(size), ctypes.sizeof(RAWINPUTHEADER))
                raw = RAWINPUT.from_buffer(raw_buffer)
                if self.scroll_mode and raw.header.dwType == 0: 
                    dx, dy = raw.mouse.lLastX, raw.mouse.lLastY
                    if dx != 0 or dy != 0: self.scroll_queue.put((dx, dy))
        return user32.DefWindowProcW(hwnd, msg, wParam, lParam)

    def update_ui_post_record(self):
        self.btn_name_var.set(self.get_button_name())
        self.record_btn.config(bg="#16161E")
        self.save_config()

    def scroll_worker(self):
        v_acc, h_acc = 0, 0
        while True:
            task = self.scroll_queue.get()
            if task is None: break
            if task == "RESET":
                v_acc, h_acc = 0, 0
                continue
            dx, dy = task
            v_acc += -dy * self.v_scale_val
            h_acc += dx * self.h_scale_val
            
            while abs(v_acc) >= 120:
                pulse = 120 if v_acc > 0 else -120
                mi = MOUSEINPUT(0, 0, ctypes.c_ulong(pulse).value, MOUSEEVENTF_WHEEL, 0, None)
                inp = INPUT(INPUT_MOUSE, _INPUTunion(mi=mi))
                user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
                v_acc -= pulse
            while abs(h_acc) >= 120:
                pulse = 120 if h_acc > 0 else -120
                mi = MOUSEINPUT(0, 0, ctypes.c_ulong(pulse).value, MOUSEEVENTF_HWHEEL, 0, None)
                inp = INPUT(INPUT_MOUSE, _INPUTunion(mi=mi))
                user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
                h_acc -= pulse

    def on_close(self):
        self.stop_hook_thread()
        self.save_config()
        self.root.destroy()

if __name__ == "__main__":
    try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except: user32.SetProcessDPIAware()
    root = tk.Tk()
    app = ScrollController(root)
    root.mainloop()
