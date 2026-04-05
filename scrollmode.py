import os
import sys
import asyncio
import configparser
import tkinter as tk
from tkinter import messagebox
import evdev

import scrollmouse

INI_PATH = './mouse.ini'

def show_device_selector():
    root = tk.Tk()
    root.title("Select Target Mouse")
    root.geometry("400x300")
    
    tk.Label(root, text="Please select the target mouse device:").pack(pady=(10, 5))
    
    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
    
    # We use a frame with a scrollbar
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, width=50, height=10)
    for device in devices:
        listbox.insert(tk.END, f"{device.name} ({device.path})")
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)
    
    def on_ok():
        selection = listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a device.")
            return
            
        selected_index = selection[0]
        selected_name = devices[selected_index].name
        
        config = configparser.ConfigParser()
        config['server'] = {'DeviceNames': selected_name}
        
        with open(INI_PATH, 'w') as configfile:
            config.write(configfile)
            
        root.destroy()

    def on_cancel():
        root.destroy()

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=(5, 10))
    
    tk.Button(btn_frame, text="OK", width=10, command=on_ok).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Cancel", width=10, command=on_cancel).pack(side=tk.LEFT, padx=10)
    
    root.mainloop()

def main():
    if not os.path.exists(INI_PATH):
        print(f"'{INI_PATH}' not found. Launching device selector...")
        try:
            show_device_selector()
        except Exception as e:
            print(f"Error launching GUI: {e}", file=sys.stderr)
            return

    if os.path.exists(INI_PATH):
        try:
            asyncio.run(scrollmouse.mousemain())
        except KeyboardInterrupt:
            pass
    else:
        print("mouse.ini was not created. Exiting.")

if __name__ == '__main__':
    main()
