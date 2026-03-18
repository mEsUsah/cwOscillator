import tkinter as tk
import keyboard
from pynput import mouse as pynput_mouse
from typing import Callable

MOUSE_BUTTON_NAMES = {
    pynput_mouse.Button.left: "mouse-left",
    pynput_mouse.Button.right: "mouse-right",
    pynput_mouse.Button.middle: "mouse-middle",
}


class KeySelectorDialog:
    def __init__(self, parent: tk.Tk, current_key: str, on_select: Callable[[str], None]):
        self._on_select = on_select
        self._listening = False
        self._mouse_listener = None
        self._kb_hook = None

        self._dialog = tk.Toplevel(parent)
        self._dialog.title("Select Key")
        self._dialog.resizable(False, False)
        self._dialog.grab_set()

        self._key_var = tk.StringVar(value=current_key)

        tk.Label(self._dialog, text="Selected key:", font=("Segoe UI", 9)).pack(padx=24, pady=(16, 4))
        tk.Label(self._dialog, textvariable=self._key_var,
                 font=("Segoe UI", 13, "bold"), width=18).pack(padx=24)

        self._listen_btn = tk.Button(self._dialog, text="Detect key / mouse button",
                                     command=self._start_listening, font=("Segoe UI", 9))
        self._listen_btn.pack(padx=24, pady=12)

        btn_frame = tk.Frame(self._dialog)
        btn_frame.pack(padx=24, pady=(0, 16))
        tk.Button(btn_frame, text="OK", width=8, command=self._confirm).pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text="Cancel", width=8, command=self._cancel).pack(side=tk.LEFT, padx=4)

        self._dialog.protocol("WM_DELETE_WINDOW", self._cancel)

    def _start_listening(self):
        self._listen_btn.config(text="Listening — press a key or click a mouse button...")
        # Delay slightly so the button click that triggered this doesn't get captured
        self._dialog.after(80, self._begin_listening)

    def _begin_listening(self):
        self._listening = True

        def on_mouse_click(_x, _y, button, pressed):
            if pressed and self._listening:
                name = MOUSE_BUTTON_NAMES.get(button, str(button))
                self._dialog.after(0, lambda: self._set_key(name))
                return False  # stop listener

        self._mouse_listener = pynput_mouse.Listener(on_click=on_mouse_click, suppress=False)
        self._mouse_listener.start()

        def on_key(event):
            if self._listening and event.event_type == keyboard.KEY_DOWN:
                self._dialog.after(0, lambda: self._set_key(event.name))

        self._kb_hook = keyboard.hook(on_key, suppress=False)

    def _set_key(self, key: str):
        self._listening = False
        self._key_var.set(key)
        self._listen_btn.config(text="Detect key / mouse button")
        self._stop_listeners()

    def _stop_listeners(self):
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        if self._kb_hook:
            keyboard.unhook(self._kb_hook)
            self._kb_hook = None

    def _confirm(self):
        self._stop_listeners()
        self._on_select(self._key_var.get())
        self._dialog.destroy()

    def _cancel(self):
        self._stop_listeners()
        self._dialog.destroy()
