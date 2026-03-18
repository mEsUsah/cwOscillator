import tkinter as tk
from tkinter import ttk
import sounddevice as sd
from typing import Callable

REFRESH_INTERVAL_MS = 3000


class DeviceSelectorFrame(tk.Frame):
    def __init__(self, parent, current_device: int | None,
                 on_device_change: Callable[[int | None], None]):
        super().__init__(parent)
        self._on_device_change = on_device_change
        self._devices: list[tuple[int | None, str]] = []

        tk.Label(self, text="Output Device:", font="TkDefaultFont 10 bold").pack(anchor="w")

        self._combo = ttk.Combobox(self, state="readonly", width=38)
        self._combo.pack(fill="x")
        self._combo.bind("<<ComboboxSelected>>", self._on_select)

        self._refresh(initial_device=current_device)
        self._schedule_refresh()

    def _get_output_devices(self) -> list[tuple[int | None, str]]:
        default_idx = sd.default.device["output"]
        default_name = sd.query_devices(default_idx)["name"]
        devices = [(None, f"System Default ({default_name})")]
        for i, d in enumerate(sd.query_devices()):
            if d["max_output_channels"] > 0:
                devices.append((i, d["name"]))
        return devices

    def _refresh(self, initial_device: int | None = None):
        try:
            new_devices = self._get_output_devices()
        except Exception:
            return

        if new_devices == self._devices:
            return

        current_selection = self._devices[self._combo.current()][0] if self._combo.current() >= 0 and self._devices else initial_device
        self._devices = new_devices
        self._combo["values"] = [name for _, name in self._devices]

        # Re-select the previously selected device (or initial)
        select = current_selection if initial_device is None else initial_device
        for idx, (dev, _) in enumerate(self._devices):
            if dev == select:
                self._combo.current(idx)
                return
        self._combo.current(0)  # fallback to system default

    def _schedule_refresh(self):
        self._refresh()
        self.after(REFRESH_INTERVAL_MS, self._schedule_refresh)

    def _on_select(self, _event):
        idx = self._combo.current()
        if idx >= 0:
            dev, _ = self._devices[idx]
            self._on_device_change(dev)
