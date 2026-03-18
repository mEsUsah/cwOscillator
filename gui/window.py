import tkinter as tk
from tkinter import ttk
from typing import Callable
from .key_selector import KeySelectorDialog
from .device_selector import DeviceSelectorFrame
from utils import APP_VERSION, check_updates, resource_path, set_icon


class GUI:
    def __init__(self, freq: int, current_device: int | None, current_key: str,
                 on_freq_change: Callable[[int], None],
                 on_key_change: Callable[[str], None],
                 on_device_change: Callable[[int | None], None],
                 on_destroy: Callable[[], None] | None = None):
        self._on_key_change = on_key_change

        self._root = tk.Tk()
        self._root.withdraw()
        self._root.title("CW Oscillator")
        self._root.resizable(False, False)

        self._freq_var = tk.IntVar(value=freq)
        self._freq_entry_var = tk.StringVar(value=str(freq))
        self._tx_var = tk.StringVar(value="")
        self._key_var = tk.StringVar(value=current_key)
        self._on_freq_change = on_freq_change

        # Frequency label
        tk.Label(self._root, text="Frequency (Hz):", font="TkDefaultFont 10 bold").pack(padx=10, pady=(16, 0), anchor="w")

        # Slider + spinbox on the same row
        freq_row = tk.Frame(self._root)
        freq_row.pack(padx=10, pady=(0, 8), fill="x")
        tk.Scale(freq_row, from_=200, to=1500, orient=tk.HORIZONTAL,
                 variable=self._freq_var, command=self._on_slider_change,
                 length=220, showvalue=False).pack(side=tk.LEFT)
        spinbox = ttk.Spinbox(freq_row, from_=200, to=1500, increment=1,
                              textvariable=self._freq_entry_var, width=6,
                              justify="right", command=self._on_spinbox_step)
        spinbox.pack(side=tk.LEFT, padx=(6, 0))
        spinbox.bind("<KeyRelease>", self._on_entry_type)
        spinbox.bind("<FocusOut>", self._on_entry_confirm)

        # Key selector
        tk.Label(self._root, text="Input Key:", font="TkDefaultFont 10 bold").pack(padx=10, pady=(0, 0), anchor="w")
        key_frame = tk.Frame(self._root, highlightbackground="#aaaaaa", highlightthickness=1)
        key_frame.pack(padx=10, pady=(0, 8), fill="x")
        tk.Label(key_frame, textvariable=self._key_var,
                 width=14, anchor="w").pack(side=tk.LEFT, padx=6, pady=4)
        tk.Button(key_frame, text="Change",
                  command=self._open_key_selector).pack(side=tk.RIGHT, padx=6, pady=4)

        # Output device
        DeviceSelectorFrame(self._root, current_device,
                            on_device_change).pack(padx=10, pady=(0, 8), fill="x")

        # TX indicator
        tk.Label(self._root, textvariable=self._tx_var,
                 font="TkDefaultFont 10 bold", fg="red", width=4).pack(pady=(0, 16))

        # Credits and version
        bottom_frame = ttk.Frame(self._root)
        bottom_frame.pack(side="bottom", fill="x")
        ttk.Label(bottom_frame, text="Created by Stanley Skarshaug - www.haxor.no").pack(side="left", padx=10, pady=10)
        ttk.Label(bottom_frame, text=APP_VERSION).pack(side="right", padx=10, pady=10)

        if on_destroy:
            self._root.protocol("WM_DELETE_WINDOW", on_destroy)

        set_icon(self._root, resource_path("logo.ico"))
        self._root.deiconify()
        self._root.after(500, check_updates)

    def _on_slider_change(self, val):
        self._freq_entry_var.set(val)
        self._on_freq_change(int(val))

    def _on_spinbox_step(self):
        try:
            val = max(200, min(1500, int(self._freq_entry_var.get())))
            self._freq_var.set(val)
            self._on_freq_change(val)
        except ValueError:
            pass

    def _on_entry_type(self, _event):
        try:
            val = max(200, min(1500, int(self._freq_entry_var.get())))
            self._freq_var.set(val)
            self._on_freq_change(val)
        except ValueError:
            pass  # ignore incomplete input while typing

    def _on_entry_confirm(self, _event):
        try:
            val = max(200, min(1500, int(self._freq_entry_var.get())))
        except ValueError:
            val = self._freq_var.get()
        self._freq_var.set(val)
        self._freq_entry_var.set(str(val))
        self._on_freq_change(val)

    def _open_key_selector(self):
        KeySelectorDialog(self._root, self._key_var.get(), self._on_key_selected)

    def _on_key_selected(self, key: str):
        self._key_var.set(key)
        self._on_key_change(key)

    def set_tx(self, val: bool):
        self._tx_var.set("TX" if val else "")

    def destroy(self):
        self._root.destroy()

    def mainloop(self):
        self._root.mainloop()
