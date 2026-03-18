import argparse
import numpy as np
import sounddevice as sd
import keyboard
from pynput import mouse as pynput_mouse
from gui import GUI

SAMPLE_RATE = 44100
BLOCKSIZE = 256
RAMP_MS = 4  # attack/release time in milliseconds

_playing = False
_phase = 0
_amplitude = 0.0
_ramp_rate = 1.0 / (SAMPLE_RATE * RAMP_MS / 1000)
FREQ = 650

MOUSE_BUTTONS = {
    "mouse-left":   pynput_mouse.Button.left,
    "mouse-right":  pynput_mouse.Button.right,
    "mouse-middle": pynput_mouse.Button.middle,
}


def _audio_callback(outdata, frames, time, status):
    global _phase, _amplitude
    target = 1.0 if _playing else 0.0
    env = np.empty(frames)
    for i in range(frames):
        _amplitude += _ramp_rate if _amplitude < target else -_ramp_rate
        _amplitude = max(0.0, min(1.0, _amplitude))
        env[i] = _amplitude

    t = (_phase + np.arange(frames)) / SAMPLE_RATE
    outdata[:, 0] = np.sin(2 * np.pi * FREQ * t) * 0.5 * env
    _phase = (_phase + frames) if _amplitude > 0 else 0


parser = argparse.ArgumentParser(description="CW Oscillator for morse code practice")
parser.add_argument("--key", default="i", help="Key to use as the morse key (default: i). Use 'mouse-left', 'mouse-right', or 'mouse-middle' for mouse buttons.")
parser.add_argument("--freq", type=int, default=650, help="Tone frequency in Hz (default: 650)")
parser.add_argument("--device", default=None, help="Output audio device name or index (partial name match supported)")
parser.add_argument("--list-devices", action="store_true", help="List available output devices and exit")
parser.add_argument("--cli", action="store_true", help="Run without GUI")
args = parser.parse_args()

if args.list_devices:
    devices = sd.query_devices()
    print("Available output devices:")
    for i, d in enumerate(devices):
        if d["max_output_channels"] > 0:
            print(f"  [{i}] {d['name']}")
    raise SystemExit(0)

FREQ = args.freq

device = args.device
if device is not None and not device.isdigit():
    matches = [i for i, d in enumerate(sd.query_devices())
               if device.lower() in d["name"].lower() and d["max_output_channels"] > 0]
    if not matches:
        print(f"No output device matching '{device}'. Run with --list-devices to see options.")
        raise SystemExit(1)
    device = matches[0]
elif device is not None:
    device = int(device)

_gui: GUI | None = None
_press_hook = None
_release_hook = None
_mouse_listener: pynput_mouse.Listener | None = None
_stream: sd.OutputStream | None = None


def start_stream(dev: int | None):
    global _stream
    set_playing(False)
    if _stream:
        _stream.stop()
        _stream.close()
    _stream = sd.OutputStream(samplerate=SAMPLE_RATE, channels=1, blocksize=BLOCKSIZE,
                               device=dev, latency="low", callback=_audio_callback)
    _stream.start()


def on_device_change(dev: int | None):
    global device
    device = dev
    start_stream(dev)


def set_playing(val: bool):
    global _playing
    _playing = val
    if _gui is not None:
        _gui.set_tx(val)


def setup_input_hooks(key: str):
    global _press_hook, _release_hook, _mouse_listener

    set_playing(False)

    if _press_hook:
        try:
            keyboard.unhook(_press_hook)
        except KeyError:
            pass
        _press_hook = None
    if _release_hook:
        try:
            keyboard.unhook(_release_hook)
        except KeyError:
            pass
        _release_hook = None
    if _mouse_listener:
        _mouse_listener.stop()
        _mouse_listener = None

    if key in MOUSE_BUTTONS:
        target_button = MOUSE_BUTTONS[key]

        def on_click(_x, _y, button, pressed):
            if button == target_button:
                set_playing(pressed)

        _mouse_listener = pynput_mouse.Listener(on_click=on_click, suppress=False)
        _mouse_listener.start()
    else:
        _press_hook = keyboard.on_press_key(key, lambda _: set_playing(True), suppress=True)
        _release_hook = keyboard.on_release_key(key, lambda _: set_playing(False), suppress=True)


# --- Run ---

setup_input_hooks(args.key)
start_stream(device)

try:
    if args.cli:
        device_name = (sd.query_devices(device)["name"] if device is not None
                       else f"System Default ({sd.query_devices(sd.default.device['output'])['name']})")
        quit_key = "esc" if args.key in ("left ctrl", "right ctrl", "ctrl") else None
        quit_hint = f"[{quit_key}]" if quit_key else "Ctrl+C"
        print(f"CW Oscillator — Hold [{args.key}] to transmit at {FREQ} Hz on [{device_name}]. {quit_hint} to quit.")
        try:
            if quit_key:
                keyboard.wait(quit_key)
            else:
                keyboard.wait()
        except KeyboardInterrupt:
            pass
        print("\nQuit.")
    else:
        def on_freq_change(val: int):
            global FREQ
            FREQ = val

        _gui = GUI(FREQ, current_device=device, current_key=args.key,
                   on_freq_change=on_freq_change,
                   on_key_change=setup_input_hooks,
                   on_device_change=on_device_change)

        _gui.mainloop()
finally:
    if _stream:
        _stream.stop()
        _stream.close()
