import os
import sys
import asyncio
import configparser
import evdev
import subprocess

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Header, Footer, OptionList, Label, Button, Input
from textual.screen import ModalScreen
from textual.binding import Binding
from textual import work

import scrollmouse

INI_PATH = './scrollmode.ini'

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
    #sudo-warning {
        color: $warning;
        margin-bottom: 1;
    }
    OptionList {
        height: 1fr;
        margin-bottom: 1;
        border: solid $accent;
    }
    #controls, #sensitivity-controls {
        height: 3;
        margin-bottom: 1;
        align-vertical: middle;
    }
    #trigger-label, #sensitivity-label {
        padding: 1;
        margin-right: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        self.trigger_code = 276
        self.sensitivity = "100"
        self.default_idx = None
        self.service_process = None

        if os.path.exists(INI_PATH):
            config = configparser.ConfigParser()
            config.read(INI_PATH)
            try:
                selected_name = config['server'].get('DeviceNames', '')
                for i, d in enumerate(self.devices):
                    if selected_name and selected_name in d.name:
                        self.default_idx = i
                        break
            except Exception: pass
            
            try:
                self.trigger_code = int(config['server'].get('ScrollToggleCode', '276'))
            except Exception: pass
            
            try:
                self.sensitivity = config['server'].get('Sensitivity', '100')
            except Exception: pass

    def on_mount(self) -> None:
        if self.default_idx is not None:
            self.query_one("#device-list", OptionList).highlighted = self.default_idx

    def on_unmount(self) -> None:
        if self.service_process is not None:
            try:
                self.service_process.terminate()
            except Exception:
                pass
            self.service_process = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main-container"):
            yield Label("Please select the target mouse device:")
            yield Label("⚠️ Note: You may need to run with 'sudo' to detect your mouse.", id="sudo-warning")
            yield OptionList(*[f"{d.name} ({d.path})" for d in self.devices], id="device-list")
            
            with Horizontal(id="controls"):
                yield Label(f"Trigger Key Code: {self.trigger_code} (Default: 276)", id="trigger-label")
                yield Button("Record Trigger", id="btn-record", variant="primary")
                
            with Horizontal(id="sensitivity-controls"):
                yield Label("Sensitivity (%):", id="sensitivity-label")
                yield Input(value=self.sensitivity, id="sensitivity-input")
                
            with Horizontal():
                yield Button("Start", id="btn-save", variant="success")
                yield Button("Start Daemon", id="btn-daemon", variant="primary")
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
            if self.service_process is None:
                if self.save_config_only():
                    if getattr(sys, 'frozen', False):
                        args = [sys.executable, "--service"]
                    else:
                        args = [sys.executable, sys.argv[0], "--service"]
                    self.service_process = subprocess.Popen(args, stdin=subprocess.DEVNULL)
                    btn = self.query_one("#btn-save", Button)
                    btn.label = "Stop"
                    btn.variant = "warning"
            else:
                self.service_process.terminate()
                self.service_process = None
                btn = self.query_one("#btn-save", Button)
                btn.label = "Start"
                btn.variant = "success"

        elif event.button.id == "btn-daemon":
            if self.service_process is not None:
                self.service_process.terminate()
                self.service_process = None
            if self.save_config_only():
                self.exit(result="daemon")

        elif event.button.id == "btn-cancel":
            if self.service_process is not None:
                self.service_process.terminate()
                self.service_process = None
            self.exit(result="cancel")

    def action_quit(self) -> None:
        if self.service_process is not None:
            try:
                self.service_process.terminate()
            except Exception:
                pass
            self.service_process = None
        self.exit(result="cancel")

    def save_config_only(self) -> bool:
        list_widget = self.query_one("#device-list", OptionList)
        if list_widget.highlighted is None:
            self.notify("Please select a device.", severity="warning")
            return False
            
        idx = list_widget.highlighted
        selected_name = self.devices[idx].name
        
        sensitivity_str = self.query_one("#sensitivity-input", Input).value
        sensitivity_str = sensitivity_str.replace('%', '').strip()
        try:
            float(sensitivity_str)
        except ValueError:
            sensitivity_str = "100"

        config = configparser.ConfigParser()
        config['server'] = {
            'DeviceNames': selected_name,
            'ScrollToggleCode': str(self.trigger_code),
            'Sensitivity': sensitivity_str
        }
        
        with open(INI_PATH, 'w') as configfile:
            config.write(configfile)
            
        return True

def show_device_selector():
    app = DeviceSelectorApp()
    return app.run()

def daemonize():
    """Double-fork to daemonize the process."""
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"Fork #1 failed: {e}\n")
        sys.exit(1)

    os.setsid()

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        sys.stderr.write(f"Fork #2 failed: {e}\n")
        sys.exit(1)

    sys.stdout.flush()
    sys.stderr.flush()
    try:
        with open('/dev/null', 'r') as f:
            os.dup2(f.fileno(), sys.stdin.fileno())
        with open('/dev/null', 'a+') as f:
            os.dup2(f.fileno(), sys.stdout.fileno())
            os.dup2(f.fileno(), sys.stderr.fileno())
    except Exception:
        pass

def main():
    if '--service' in sys.argv:
        try:
            asyncio.run(scrollmouse.mousemain())
        except KeyboardInterrupt:
            pass
        return

    run_daemon = False
    if '-d' in sys.argv:
        run_daemon = True
        sys.argv.remove('-d')

    if run_daemon:
        if not os.path.exists(INI_PATH):
            print(f"Error: '{INI_PATH}' not found. Please run without '-d' first to configure.", file=sys.stderr)
            sys.exit(1)
        
        print("Running in background (daemon mode)...")
        daemonize()
        try:
            asyncio.run(scrollmouse.mousemain())
        except KeyboardInterrupt:
            pass
        return

    try:
        action = show_device_selector()
    except Exception as e:
        print(f"Error launching TUI: {e}", file=sys.stderr)
        return

    if action == "daemon":
        print("Running in background (daemon mode)...")
        daemonize()
        try:
            asyncio.run(scrollmouse.mousemain())
        except KeyboardInterrupt:
            pass
    else:
        print("Exited without starting.")

if __name__ == '__main__':
    main()
