import tkinter as tk
from typing import Callable


class GUI:
    def __init__(self, freq: int, device_name: str,
                 on_freq_change: Callable[[int], None],
                 on_destroy: Callable[[], None] | None = None):
        self._root = tk.Tk()
        self._root.title(f"CW Oscillator — {device_name}")
        self._root.resizable(False, False)

        self._freq_var = tk.IntVar(value=freq)
        self._tx_var = tk.StringVar(value="")

        tk.Label(self._root, text="Frequency (Hz)", font=("Segoe UI", 9)).pack(padx=20, pady=(16, 0))

        tk.Scale(self._root, from_=200, to=1500, orient=tk.HORIZONTAL,
                 variable=self._freq_var, command=lambda val: on_freq_change(int(val)),
                 length=280, showvalue=True, font=("Segoe UI", 9)).pack(padx=20, pady=(0, 4))

        tk.Label(self._root, textvariable=self._tx_var,
                 font=("Segoe UI", 11, "bold"), fg="red", width=4).pack(pady=(0, 16))

        if on_destroy:
            self._root.protocol("WM_DELETE_WINDOW", on_destroy)

    def set_tx(self, val: bool):
        self._tx_var.set("TX" if val else "")

    def destroy(self):
        self._root.destroy()

    def mainloop(self):
        self._root.mainloop()
