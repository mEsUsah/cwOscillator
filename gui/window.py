import tkinter as tk
from typing import Callable
from .key_selector import KeySelectorDialog


class GUI:
    def __init__(self, freq: int, device_name: str, current_key: str,
                 on_freq_change: Callable[[int], None],
                 on_key_change: Callable[[str], None],
                 on_destroy: Callable[[], None] | None = None):
        self._on_key_change = on_key_change

        self._root = tk.Tk()
        self._root.title(f"CW Oscillator — {device_name}")
        self._root.resizable(False, False)

        self._freq_var = tk.IntVar(value=freq)
        self._tx_var = tk.StringVar(value="")
        self._key_var = tk.StringVar(value=current_key)

        # Frequency
        tk.Label(self._root, text="Frequency (Hz)", font=("Segoe UI", 9)).pack(padx=20, pady=(16, 0))
        tk.Scale(self._root, from_=200, to=1500, orient=tk.HORIZONTAL,
                 variable=self._freq_var, command=lambda val: on_freq_change(int(val)),
                 length=280, showvalue=True, font=("Segoe UI", 9)).pack(padx=20, pady=(0, 8))

        # Key selector
        key_frame = tk.Frame(self._root)
        key_frame.pack(padx=20, pady=(0, 8))
        tk.Label(key_frame, text="Key:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(key_frame, textvariable=self._key_var,
                 font=("Segoe UI", 9, "bold"), width=14, anchor="w").pack(side=tk.LEFT)
        tk.Button(key_frame, text="Change", font=("Segoe UI", 9),
                  command=self._open_key_selector).pack(side=tk.LEFT, padx=(6, 0))

        # TX indicator
        tk.Label(self._root, textvariable=self._tx_var,
                 font=("Segoe UI", 11, "bold"), fg="red", width=4).pack(pady=(0, 16))

        if on_destroy:
            self._root.protocol("WM_DELETE_WINDOW", on_destroy)

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
