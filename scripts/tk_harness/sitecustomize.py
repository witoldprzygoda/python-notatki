"""Harness rozdziału 16: mainloop() okien tkinter/CustomTkinter kończy się sam po ~0,9 s,
a przed zamknięciem zapisuje zrzut okien do katalogu z ZRZUTY_KATALOG (jeśli ustawiony).
Ładowany przez PYTHONPATH — skrypty książki pozostają nietknięte. Okna są podnoszone na
wierzch, a zrzut składa się z osobnych ujęć każdego okna na neutralnym tle (nic z pulpitu)."""
import ctypes
import ctypes.wintypes
import os
import sys
import time
from pathlib import Path

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

import tkinter as tk

CZAS = float(os.environ.get("TK_CZAS", "0.9"))
TLO = (243, 243, 243)


def _potomne(w):
    for dziecko in w.winfo_children():
        yield dziecko
        yield from _potomne(dziecko)


def _okna(root):
    okna = [root] + [w for w in _potomne(root) if isinstance(w, tk.Toplevel)]
    return [w for w in okna if w.winfo_viewable()]


def _ramka(w):
    w.update_idletasks()
    if w.wm_overrideredirect():
        return (w.winfo_rootx(), w.winfo_rooty(), w.winfo_rootx() + w.winfo_width(), w.winfo_rooty() + w.winfo_height())
    return (w.winfo_rootx(), w.winfo_y() + 1, w.winfo_rootx() + w.winfo_width(), w.winfo_rooty() + w.winfo_height())


def _na_wierzch(root):
    for w in _okna(root):
        try:
            w.attributes("-topmost", True)
            w.lift()
        except tk.TclError:
            pass
    root.update()


def _zrzut(root):
    katalog = os.environ.get("ZRZUTY_KATALOG")
    if not katalog:
        return
    from PIL import Image, ImageGrab
    kursor = ctypes.wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(kursor))
    ctypes.windll.user32.SetCursorPos(root.winfo_screenwidth() - 2, root.winfo_screenheight() - 2)
    okna = _okna(root)
    ramki = [_ramka(w) for w in okna]
    x0, y0 = min(r[0] for r in ramki), min(r[1] for r in ramki)
    x1, y1 = max(r[2] for r in ramki), max(r[3] for r in ramki)
    obraz = Image.new("RGB", (x1 - x0, y1 - y0), TLO)
    for w, r in zip(okna, ramki):
        w.lift()
        root.update()
        time.sleep(0.05)
        obraz.paste(ImageGrab.grab(bbox=r), (r[0] - x0, r[1] - y0))
    obraz.save(Path(katalog) / (Path(sys.argv[0]).stem + ".png"))
    ctypes.windll.user32.SetCursorPos(kursor.x, kursor.y)


def _mainloop(self, n=0):
    root = self.winfo_toplevel()
    koniec = time.monotonic() + CZAS
    try:
        root.update()
        _na_wierzch(root)
        while time.monotonic() < koniec:
            root.update()
            time.sleep(0.02)
        _na_wierzch(root)
        _zrzut(root)
    finally:
        try:
            root.destroy()
        except tk.TclError:
            pass


tk.Misc.mainloop = _mainloop
tk.Tk.mainloop = _mainloop
