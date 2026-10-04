"""Przechwytuje sesję nowego REPL przez pseudokonsolę (ConPTY) i zapisuje surowy strumień VT.

Użycie:
    python przechwyc.py <python-3.14> <wyjście.vt>

Skrypt uruchamia nowy REPL interpretera <python-3.14> w pseudokonsoli o wymiarach 12 × 56 znaków
(pakiet pywinpty), wpisuje znak po znaku krótką sesję z definicją funkcji, łańcuchem, liczbą
i komentarzami, a surowy strumień z sekwencjami sterującymi (kolory) zapisuje do <wyjście.vt>.
Zmienne, które wyłączają nowy REPL albo kolory (PYTHON_BASIC_REPL, NO_COLOR, PYTHONSTARTUP), są
pomijane, a historia poleceń trafia do pliku tymczasowego, nie do pliku historii użytkownika.
Obraz powstaje w drugim kroku, skryptem renderuj.py z tego katalogu.
"""
import os
import sys
import tempfile
import threading
import time

import winpty

PYTHON, WYJSCIE = sys.argv[1], sys.argv[2]
WIERSZE, KOLUMNY = 12, 56
WEJSCIE = [
    "def powitanie(imie):\r",
    'return f"Witaj, {imie}!"  # f-string\r',
    "\r",
    'powitanie("Ala") * 2  # łańcuch razy liczba\r',
]


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        env = {k: v for k, v in os.environ.items()
               if k not in ("PYTHON_BASIC_REPL", "NO_COLOR", "PYTHON_COLORS", "PYTHONSTARTUP")}
        env["PYTHON_HISTORY"] = os.path.join(tmp, "historia.txt")
        proces = winpty.PtyProcess.spawn([PYTHON, "-q"], dimensions=(WIERSZE, KOLUMNY), env=env)
        porcje = []

        def czytnik():
            while True:
                try:
                    porcja = proces.read(4096)
                except EOFError:
                    return
                if porcja:
                    porcje.append(porcja)

        threading.Thread(target=czytnik, daemon=True).start()
        time.sleep(2.0)
        for wiersz in WEJSCIE:
            for znak in wiersz:
                proces.write(znak)
                time.sleep(0.015)
            time.sleep(0.6)
        time.sleep(1.0)
        with open(WYJSCIE, "w", encoding="utf-8", newline="") as plik:
            plik.write("".join(porcje))
        proces.write("exit\r")
        time.sleep(1.0)
        if proces.isalive():
            proces.terminate(force=True)
    print(f"zapisano {WYJSCIE} ({len(''.join(porcje))} znaków)", flush=True)


if __name__ == "__main__":
    main()
    os._exit(0)  # wątek czytnika pseudokonsoli nie blokuje zakończenia
