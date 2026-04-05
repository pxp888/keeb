# ScrollMode

ScrollMode is a Linux utility that upgrades your mouse by adding a custom "scroll mode" feature. Instead of turning a mechanical scroll wheel, you can toggle a designated mouse button (e.g., a side thumb button), and any physical device movement will seamlessly translate into smooth vertical and horizontal scroll wheel events.

The program creates a virtual input device via Linux's `uinput` subsystem and `evdev` to intercept raw mouse inputs, intelligently route them based on the current mode, and emit them as standard OS-level events.

## Features

- **Custom Scroll Trigger**: Assign any mouse button to activate scroll mode.
- **Interactive Configuration TUI**: Includes a Textual-based UI to easily pick your mouse device and record your chosen trigger button.
- **High-Resolution Scrolling**: Supports high-res scroll events for butter-smooth scrolling, with a legacy fallback mechanism.
- **Background Daemon Mode**: Easily detach and run in the background.
- **System-Wide Support**: Works regardless of your display server (Wayland, X11, or console) since it operates directly via kernel evdev nodes.
- **Volume Control**: Use the scroll wheel to control system volume when **scrollmode** is active.

## Requirements

- Linux operating system
- Python 3.7+
- Dependencies: `evdev`, `textual`

_Note: Since the program grabs and emits raw device events directly through `/dev/input/_`devices, it typically requires`root`privileges (or membership in the`input` group).\*

## Quick Start (Pre-compiled Executable)

For most users, the easiest way to use ScrollMode without installing Python or any dependencies is to run the standalone executable.

1. Navigate to the `executable/` directory and download the compiled executable.
2. Make sure it has execute permissions (`chmod +x scrollmode`).
3. Run the executable with `root` privileges (required to interact with input devices):
   ```bash
   sudo ./scrollmode
   ```
4. If you want it to run silently in the background as a daemon, append the `-d` flag:
   ```bash
   sudo ./scrollmode -d
   ```

_Note: The first time you launch the executable, it will open an interactive configuration tool to help you select your mouse and trigger button._

## Running from Source (Python)

If you prefer to run the raw Python scripts instead, you will need to set up the environment.

1. Install the Python dependencies (via pip, a virtual environment, or your package manager):

   ```bash
   pip install evdev textual
   ```

2. Launch the script (with `sudo` if necessary) to begin the first-time setup:

   ```bash
   sudo python scrollmode.py
   ```

3. **Configuration UI**: Because no `scrollmode.ini` file exists yet, a Terminal UI will appear.
   - Use the arrow keys to select your mouse from the list of available input devices.
   - Focus "Record Trigger" and press it, then click the mouse button you want to use as your scroll toggle lock.
   - Select "Save & Exit" to save your choices locally.

## Usage

Once `scrollmode.ini` is generated, you can launch the application normally:

```bash
sudo python scrollmode.py
```

The script will actively capture your mouse. When the toggle button is pressed, dragging the mouse physically across your desk will send `REL_WHEEL` and `REL_HWHEEL` scroll inputs instead of moving the cursor.

### Daemon Mode (Background)

If you'd like to use this seamlessly without an open terminal, you can launch the tool as a background daemon:

```bash
sudo python scrollmode.py -d
```

### Re-configuring

To launch the setup wizard again to change your device or trigger key, simply delete the generated configuration file and run the script again:

```bash
rm scrollmode.ini
sudo python scrollmode.py
```

## Building the Executable

If you want to create your own standalone executable from the source, you can use PyInstaller:

```bash
pyinstaller --onefile --name "scrollmode" scrollmode.py
```
