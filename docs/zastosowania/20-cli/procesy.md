# Procesy, pliki i konfiguracja

Narzędzie automatyzujące rzadko pracuje samo: wywołuje inne programy, kopiuje i pakuje pliki, czyta ustawienia z pliku i środowiska. Biblioteka standardowa ma do tego `subprocess`, `shutil` i `tomllib`; ten podrozdział pokazuje ich użycie w narzędziu.

## Procesy potomne

```python title="procesy.py"
import shutil
import subprocess
import sys

wynik = subprocess.run([sys.executable, "-c", "import sys; print('wersja', sys.version_info[:2]); print('uwaga', file=sys.stderr); sys.exit(3)"], capture_output=True, text=True, encoding="utf-8")
print(wynik.returncode, repr(wynik.stdout), repr(wynik.stderr))
try:
    subprocess.run([sys.executable, "-c", "raise SystemExit(4)"], check=True)
except subprocess.CalledProcessError as blad:
    print("CalledProcessError:", blad.returncode, blad.cmd[1:])
try:
    subprocess.run([sys.executable, "-c", "import time; time.sleep(5)"], timeout=0.5)
except subprocess.TimeoutExpired as blad:
    print("TimeoutExpired po", blad.timeout, "s")
wynik = subprocess.run([sys.executable, "-m", "json.tool", "--indent", "1"], input='{"a": [1, 2]}', capture_output=True, text=True, encoding="utf-8")
print(wynik.stdout.strip().splitlines())
print(shutil.which("python") is not None, shutil.which("nie-ma-takiego-programu"))
print(subprocess.run([sys.executable, "porzadek.py", "--version"], capture_output=True, text=True, encoding="utf-8").returncode)
```

```{ .text .no-copy }
3 'wersja (3, 14)\n' 'uwaga\n'
CalledProcessError: 4 ['-c', 'raise SystemExit(4)']
TimeoutExpired po 0.5 s
['{', ' "a": [', '  1,', '  2', ' ]', '}']
True None
2
```

`subprocess.run()` uruchamia program z listą argumentów — każdy argument osobno, bez powłoki, więc spacje i cudzysłowy w nazwach plików nie wymagają znaków ucieczki, a tekst od użytkownika nie może wstrzyknąć polecenia. Zwraca obiekt `CompletedProcess` z kodem wyjścia (`returncode`) oraz, przy `capture_output=True`, z `stdout` i `stderr` jako tekstem (`text=True` z jawnym `encoding`, jak przy plikach). `check=True` zamienia niezerowy kod w wyjątek `CalledProcessError`, `timeout` przerywa proces, który nie kończy się w czasie, a `input=` podaje tekst na jego `stdin` — tak narzędzie może użyć innego narzędzia jako filtra. Inny program Pythona uruchamiamy przez `sys.executable`, żeby użyć tego samego interpretera i środowiska wirtualnego; `shutil.which()` sprawdza przed startem, czy program zewnętrzny jest na ścieżce. Nieznana opcja `--version` daje kod `2` z parsera `porzadek` — narzędzia komunikują się kodami także wtedy, gdy jedno wywołuje drugie.

## Archiwa i narzędzia systemowe

```python title="archiwum.py"
import shutil
import tempfile
import zipfile
from pathlib import Path

zrodlo = Path("projekt-do-archiwum")
for sciezka in ("README.md", "src/app.py", "src/dane/przyklad.csv", "build/app.pyc"):
    (zrodlo / sciezka).parent.mkdir(parents=True, exist_ok=True)
    (zrodlo / sciezka).write_text(sciezka, encoding="utf-8")

with tempfile.TemporaryDirectory() as tymczasowy:
    kopia = Path(tymczasowy) / "kopia"
    shutil.copytree(zrodlo, kopia, ignore=shutil.ignore_patterns("build", "*.pyc"))
    print(sorted(str(p.relative_to(kopia)).replace("\\", "/") for p in kopia.rglob("*") if p.is_file()))
    archiwum = shutil.make_archive("projekt-2026-09-23", "zip", root_dir=kopia)
    with zipfile.ZipFile(archiwum) as plik_zip:
        print(Path(archiwum).name, plik_zip.namelist())
print(Path(tymczasowy).exists(), Path("projekt-2026-09-23.zip").stat().st_size > 0)
uzycie = shutil.disk_usage(".")
print(type(uzycie).__name__, uzycie.free < uzycie.total)
```

```{ .text .no-copy }
['README.md', 'src/app.py', 'src/dane/przyklad.csv']
projekt-2026-09-23.zip ['src/', 'README.md', 'src/dane/', 'src/app.py', 'src/dane/przyklad.csv']
False True
usage True
```

`shutil.copytree()` kopiuje katalog z pominięciem wzorców podanych przez `ignore_patterns()`, `make_archive()` tworzy archiwum zip lub tar z katalogu bez otwierania modułu `zipfile` wprost, `disk_usage()` zwraca miejsce na dysku. Katalog tymczasowy z `tempfile` z rozdziału 9 „Python Notatki” znika po bloku `with`, więc kopia robocza nie zostaje na dysku, a archiwum — tak. Nazwa archiwum z datą i wzorce wykluczeń to dwa ustawienia, które narzędzie do kopii zapasowych powinno przyjmować z konfiguracji.

## Źródła konfiguracji

```toml title="ustawienia.toml"
[porzadek]
wg = "data"
limit = 100
```

```python title="konfiguracja.py"
"""Ustawienia narzędzia: wartości domyślne < plik TOML < zmienne środowiskowe < argumenty."""

import argparse
import os
import tomllib
from pathlib import Path

DOMYSLNE = {"wg": "rozszerzenie", "limit": None, "ukryte": False}


def z_pliku(sciezka):
    if sciezka is None or not Path(sciezka).is_file():
        return {}
    with open(sciezka, "rb") as plik:
        return tomllib.load(plik).get("porzadek", {})


def ze_srodowiska(prefiks="PORZADEK_"):
    ustawienia = {}
    for klucz in DOMYSLNE:
        wartosc = os.environ.get(prefiks + klucz.upper())
        if wartosc is not None:
            ustawienia[klucz] = {"limit": int, "ukryte": lambda w: w.lower() in ("1", "true", "tak")}.get(klucz, str)(wartosc)
    return ustawienia


def ustalenia(argv=None):
    parser = argparse.ArgumentParser(prog="porzadek")
    parser.add_argument("--config", type=Path, default=Path("ustawienia.toml"))
    parser.add_argument("--wg", choices=["rozszerzenie", "data"])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--ukryte", action=argparse.BooleanOptionalAction)
    argumenty = parser.parse_args(argv)
    z_argumentow = {k: v for k, v in vars(argumenty).items() if k != "config" and v is not None}
    return {**DOMYSLNE, **z_pliku(argumenty.config), **ze_srodowiska(), **z_argumentow}
```

```python title="uzycie-konfiguracja.py"
import os

from konfiguracja import ustalenia

print("domyślne i plik:  ", ustalenia([]))
print("bez pliku:        ", ustalenia(["--config", "brak.toml"]))
os.environ["PORZADEK_LIMIT"] = "5"
os.environ["PORZADEK_UKRYTE"] = "tak"
print("ze środowiskiem:  ", ustalenia([]))
print("z argumentami:    ", ustalenia(["--limit", "1", "--no-ukryte", "--wg", "rozszerzenie"]))
```

```{ .text .no-copy }
domyślne i plik:   {'wg': 'data', 'limit': 100, 'ukryte': False}
bez pliku:         {'wg': 'rozszerzenie', 'limit': None, 'ukryte': False}
ze środowiskiem:   {'wg': 'data', 'limit': 5, 'ukryte': True}
z argumentami:     {'wg': 'rozszerzenie', 'limit': 1, 'ukryte': False}
```

Narzędzie uruchamiane codziennie nie powinno wymagać tych samych opcji za każdym razem. Ustalona kolejność źródeł — wartości domyślne w kodzie, plik konfiguracyjny TOML z rozdziału 9 „Python Notatki”, zmienne środowiskowe z przedrostkiem nazwy narzędzia, na końcu argumenty wiersza poleceń — sprawia, że każde źródło może nadpisać poprzednie, a argument podany w terminalu ma zawsze pierwszeństwo. W kodzie to jedno złożenie słowników; istotne jest, by opcje bez wartości domyślnej w parserze (`None`) nie zasłaniały ustawień z pliku, dlatego `z_argumentow` pomija `None`. Zmienne środowiskowe są tekstem, więc wartości liczbowe i logiczne konwertujemy jawnie. Pliku ustawień szukamy w katalogu bieżącym — tak robi `konfiguracja.py` — albo w katalogu konfiguracji użytkownika (`%APPDATA%` na Windows, `~/.config` na Linuksie); inną ścieżkę wskazuje opcja `--config`.
