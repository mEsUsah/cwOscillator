import argparse
import numpy as np
import sounddevice as sd
import keyboard
from pynput import mouse as pynput_mouse

SAMPLE_RATE = 44100
BLOCKSIZE = 256
RAMP_MS = 4  # attack/release time in milliseconds

_playing = False
_phase = 0
_amplitude = 0.0
_ramp_rate = 1.0 / (SAMPLE_RATE * RAMP_MS / 1000)


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


MOUSE_BUTTONS = {
    "mouse-left": pynput_mouse.Button.left,
    "mouse-right": pynput_mouse.Button.right,
}

parser = argparse.ArgumentParser(description="CW Oscillator for morse code practice")
parser.add_argument("--key", default="i", help="Key to use as the morse key (default: i). Use 'mouse-left' or 'mouse-right' for mouse buttons.")
parser.add_argument("--freq", type=int, default=650, help="Tone frequency in Hz (default: 650)")
args = parser.parse_args()

FREQ = args.freq

quit_key = "esc" if args.key in ("left ctrl", "right ctrl", "ctrl") else None
quit_hint = f"[{quit_key}]" if quit_key else "Ctrl+C"
print(f"CW Oscillator — Hold [{args.key}] to transmit at {FREQ} Hz. {quit_hint} to quit.")

with sd.OutputStream(samplerate=SAMPLE_RATE, channels=1, blocksize=BLOCKSIZE,
                     latency="low", callback=_audio_callback):
    if args.key in MOUSE_BUTTONS:
        target_button = MOUSE_BUTTONS[args.key]

        def on_click(x, y, button, pressed):
            if button == target_button:
                globals().update(_playing=pressed)

        listener = pynput_mouse.Listener(on_click=on_click, suppress=True)
        listener.start()
    else:
        keyboard.on_press_key(args.key, lambda _: globals().update(_playing=True), suppress=True)
        keyboard.on_release_key(args.key, lambda _: globals().update(_playing=False), suppress=True)

    try:
        if quit_key:
            keyboard.wait(quit_key)
        else:
            keyboard.wait()
    except KeyboardInterrupt:
        pass
    print("\nQuit.")
