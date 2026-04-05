import os
import sys
import asyncio
import configparser
import evdev

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, OptionList, Label, Button
from textual.screen import ModalScreen
from textual.binding import Binding
from textual import work

import scrollmouse

INI_PATH = './mouse.ini'

class RecordModal(ModalScreen[tuple[int | None, Exception | None]]):
    """Modal to record button press."""
    CSS = """
    RecordModal {
        align: center middle;
    }
    #record-dialog {
        padding: 1 2;
        width: 40;
        height: 11;
        border: thick $background 80%;
        background: $surface;
    }
    #record-status {
        margin-bottom: 2;
        text-align: center;
    }
    """
    
    def __init__(self, device_path: str):
        super().__init__()
        self.device_path = device_path
        self.record_task = None
        self.dev = None

    def compose(self) -> ComposeResult:
        with Vertical(id="record-dialog"):
            yield Label("Grabbing device...", id="record-status")
            yield Button("Cancel", id="cancel-record", variant="error")

    async def on_mount(self) -> None:
        self.record_task = asyncio.create_task(self.poll_device())

    async def poll_device(self):
        try:
            self.dev = evdev.InputDevice(self.device_path)
            self.dev.grab()
            self.query_one("#record-status", Label).update("Press the desired mouse button now...")
            async for event in self.dev.async_read_loop():
                if event.type == evdev.ecodes.EV_KEY and event.value == 1:
                    try:
                        self.dev.ungrab()
                    except Exception:
                        pass
                    self.dev.close()
                    self.dismiss((event.code, None))
                    return
        except Exception as e:
            self.dismiss((None, e))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel-record":
            if self.record_task:
                self.record_task.cancel()
            if self.dev:
                try:
                    self.dev.ungrab()
                except Exception:
                    pass
                self.dev.close()
            self.dismiss((None, None))


class DeviceSelectorApp(App):
    """A Textual app to select target mouse."""
    
    CSS = """
    #main-container {
        padding: 1;
        height: 1fr;
    }
    OptionList {
        height: 1fr;
        margin-bottom: 1;
        border: solid $accent;
    }
    #controls {
        height: 3;
        margin-bottom: 1;
        align-vertical: middle;
    }
    #trigger-label {
        padding: 1;
        margin-right: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("enter", "submit", "Save & Exit", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        self.trigger_code = 276
        
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main-container"):
            yield Label("Please select the target mouse device:")
            yield OptionList(*[f"{d.name} ({d.path})" for d in self.devices], id="device-list")
            
            with Horizontal(id="controls"):
                yield Label(f"Trigger Key Code: {self.trigger_code} (Default: 276)", id="trigger-label")
                yield Button("Record Trigger", id="btn-record", variant="primary")
                
            with Horizontal():
                yield Button("Save & Exit", id="btn-save", variant="success")
                yield Button("Cancel", id="btn-cancel", variant="error")
                
        yield Footer()

    @work
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-record":
            list_widget = self.query_one("#device-list", OptionList)
            if list_widget.highlighted is None:
                self.notify("Please select a device first.", severity="warning")
                return
            idx = list_widget.highlighted
            device_path = self.devices[idx].path
            
            # Show modal
            result = await self.push_screen_wait(RecordModal(device_path))
            if result:
                code, err = result
                if err:
                    self.notify(f"Could not grab device: {err}", severity="error")
                elif code is not None:
                    self.trigger_code = code
                    self.query_one("#trigger-label", Label).update(f"Trigger Key Code: {self.trigger_code} (Default: 276)")
                    self.notify(f"Recorded key code {code}")
                    
        elif event.button.id == "btn-save":
            self.save_and_exit()
        elif event.button.id == "btn-cancel":
            self.exit()

    def action_submit(self) -> None:
        self.save_and_exit()
            
    def save_and_exit(self):
        list_widget = self.query_one("#device-list", OptionList)
        if list_widget.highlighted is None:
            self.notify("Please select a device.", severity="warning")
            return
            
        idx = list_widget.highlighted
        selected_name = self.devices[idx].name
        
        config = configparser.ConfigParser()
        config['server'] = {
            'DeviceNames': selected_name,
            'ScrollToggleCode': str(self.trigger_code)
        }
        
        with open(INI_PATH, 'w') as configfile:
            config.write(configfile)
            
        self.exit()

def show_device_selector():
    app = DeviceSelectorApp()
    app.run()

def main():
    if not os.path.exists(INI_PATH):
        print(f"'{INI_PATH}' not found. Launching device selector...")
        try:
            show_device_selector()
        except Exception as e:
            print(f"Error launching TUI: {e}", file=sys.stderr)
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
