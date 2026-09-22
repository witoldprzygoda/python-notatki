# Pakiet do instalacji

Pakiet to projekt z układem `src`, plikiem `pyproject.toml` i tym, czego rozdział 7 „Python Notatki” jeszcze nie wymagał: metadanymi, które zobaczy odbiorca, i **punktami wejścia** (ang. *entry point*), które zamieniają funkcje w polecenia dostępne z terminala. Budujemy go z logiki menedżera kontaktów z rozdziału 16.

## Od projektu do pakietu

```{ .text .no-copy }
projekt/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── kontakty/
│       ├── __init__.py
│       ├── logika.py
│       ├── cli.py
│       ├── okno.py
│       └── dane/
│           └── przyklad.csv
└── tests/
    ├── test_logika.py
    └── test_cli.py
```

```toml title="pyproject.toml"
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "kontakty"
dynamic = ["version"]
description = "Menedżer kontaktów: sprawdzanie, wyszukiwanie i eksport CSV"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
license-files = ["LICENSE"]
authors = [{ name = "Jan Kowalski", email = "jan.kowalski@example.com" }]
keywords = ["kontakty", "csv", "tkinter"]
classifiers = [
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
]
dependencies = []

[project.optional-dependencies]
test = ["pytest>=9"]

[project.urls]
Homepage = "https://example.com/kontakty"

[project.scripts]
kontakty-csv = "kontakty.cli:main"

[project.gui-scripts]
kontakty = "kontakty.okno:main"

[tool.hatch.version]
path = "src/kontakty/__init__.py"
```

Tabela `[project]` zawiera **metadane** pakietu: nazwę, pod którą odbiorca go zainstaluje, opis i plik README wyświetlane w indeksie pakietów, minimalną wersję Pythona, licencję jako identyfikator ze standardu SPDX (`MIT`) z plikiem, autorów, słowa kluczowe i klasyfikatory ułatwiające wyszukiwanie. `dependencies` to pakiety wymagane do działania — tu żadne, bo `kontakty` używa tylko biblioteki standardowej — a `[project.optional-dependencies]` to grupy dodatkowe, instalowane na życzenie: `pytest` potrzebują tylko programiści. `[project.scripts]` tworzy przy instalacji polecenie `kontakty-csv`, które wywołuje funkcję `main` z modułu `kontakty.cli`; `[project.gui-scripts]` robi to samo dla okna, ale na Windows bez okna konsoli w tle. Wersja jest **dynamiczna**: zamiast wpisywać ją w `pyproject.toml`, Hatchling odczytuje `__version__` z pliku wskazanego w `[tool.hatch.version]`, więc istnieje w jednym miejscu. Minimum `hatchling>=1.27` wynika z licencji: zapis `license-files` jako listy wzorców rozumie Hatchling od wersji 1.26, a od 1.27 domyślnie zapisuje metadane w wersji 2.4 — pierwszej, w której `License-Expression` i `License-File` (PEP 639) są polami standardowymi.

## Kod pakietu

```python title="src/kontakty/__init__.py"
"""Menedżer kontaktów: logika, polecenie kontakty-csv i okno."""

__version__ = "0.1.0"
```

```python title="src/kontakty/logika.py"
"""Logika menedżera kontaktów — bez okna, do testów."""

import csv
from dataclasses import asdict, dataclass, fields


@dataclass
class Kontakt:
    imie: str
    email: str
    telefon: str = ""


def sprawdz(kontakt):
    """Zwraca listę komunikatów o błędach; pusta lista oznacza poprawny kontakt."""
    bledy = []
    if not kontakt.imie.strip():
        bledy.append("imię jest wymagane")
    if "@" not in kontakt.email[1:-1]:
        bledy.append("adres e-mail musi zawierać znak @ między nazwą a domeną")
    if kontakt.telefon and not kontakt.telefon.replace(" ", "").replace("-", "").isdigit():
        bledy.append("telefon może zawierać tylko cyfry, spacje i myślniki")
    return bledy


def filtruj(kontakty, zapytanie):
    zapytanie = zapytanie.strip().lower()
    return [kontakt for kontakt in kontakty if zapytanie in kontakt.imie.lower() or zapytanie in kontakt.email.lower()]


def czytaj_kontakty(plik):
    """Czyta kontakty z otwartego pliku tekstowego CSV."""
    return [Kontakt(**wiersz) for wiersz in csv.DictReader(plik, delimiter=";")]


def wczytaj_csv(sciezka):
    with open(sciezka, newline="", encoding="utf-8-sig") as plik:
        return czytaj_kontakty(plik)


def zapisz_csv(kontakty, sciezka):
    with open(sciezka, "w", newline="", encoding="utf-8") as plik:
        pisarz = csv.DictWriter(plik, fieldnames=[pole.name for pole in fields(Kontakt)], delimiter=";")
        pisarz.writeheader()
        pisarz.writerows(asdict(kontakt) for kontakt in kontakty)
```

```python title="src/kontakty/cli.py"
"""Polecenie kontakty-csv: sprawdzanie i przeszukiwanie plików CSV z kontaktami."""

import argparse
import sys
from importlib.resources import files

from . import __version__
from .logika import czytaj_kontakty, filtruj, sprawdz, wczytaj_csv


def przyklad():
    """Plik przykładowy dostarczany razem z pakietem."""
    return files("kontakty").joinpath("dane/przyklad.csv")


def wczytaj(sciezka):
    if sciezka:
        return wczytaj_csv(sciezka)
    with przyklad().open(encoding="utf-8-sig", newline="") as plik:
        return czytaj_kontakty(plik)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="kontakty-csv", description="Sprawdza i przeszukuje pliki CSV z kontaktami.")
    parser.add_argument("--wersja", action="version", version=f"%(prog)s {__version__}")
    polecenia = parser.add_subparsers(dest="polecenie", required=True)
    sprawdzanie = polecenia.add_parser("sprawdz", help="wypisuje kontakty z błędami")
    sprawdzanie.add_argument("plik", nargs="?", help="plik CSV (domyślnie przykład z pakietu)")
    szukanie = polecenia.add_parser("szukaj", help="wypisuje kontakty pasujące do frazy")
    szukanie.add_argument("fraza")
    szukanie.add_argument("plik", nargs="?", help="plik CSV (domyślnie przykład z pakietu)")
    argumenty = parser.parse_args(argv)
    kontakty = wczytaj(argumenty.plik)
    if argumenty.polecenie == "sprawdz":
        bledne = [(kontakt, sprawdz(kontakt)) for kontakt in kontakty if sprawdz(kontakt)]
        for kontakt, bledy in bledne:
            print(f"{kontakt.imie or '(bez imienia)'}: {'; '.join(bledy)}")
        print(f"kontaktów: {len(kontakty)}, z błędami: {len(bledne)}")
        return 1 if bledne else 0
    for kontakt in filtruj(kontakty, argumenty.fraza):
        print(f"{kontakt.imie:<16} {kontakt.email:<24} {kontakt.telefon}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

```python title="src/kontakty/okno.py"
"""Polecenie kontakty: okno z listą kontaktów z pliku CSV."""

import sys
import tkinter as tk
from tkinter import filedialog, ttk

from . import __version__
from .cli import wczytaj
from .logika import wczytaj_csv


class Okno(tk.Tk):
    def __init__(self, kontakty):
        super().__init__()
        self.title(f"Kontakty {__version__}")
        self.geometry("520x300")
        pasek = ttk.Frame(self, padding=6)
        pasek.pack(fill="x")
        ttk.Button(pasek, text="Otwórz CSV…", command=self.otworz).pack(side="left")
        self.stan = tk.StringVar()
        ttk.Label(pasek, textvariable=self.stan).pack(side="right")
        self.tabela = ttk.Treeview(self, columns=("imie", "email", "telefon"), show="headings")
        for kolumna, tytul in zip(("imie", "email", "telefon"), ("Imię", "E-mail", "Telefon")):
            self.tabela.heading(kolumna, text=tytul)
        self.tabela.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self.pokaz(kontakty)

    def pokaz(self, kontakty):
        self.tabela.delete(*self.tabela.get_children())
        for kontakt in kontakty:
            self.tabela.insert("", "end", values=(kontakt.imie, kontakt.email, kontakt.telefon))
        self.stan.set(f"Kontaktów: {len(kontakty)}")

    def otworz(self):
        sciezka = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if sciezka:
            self.pokaz(wczytaj_csv(sciezka))


def main(argv=None):
    argumenty = sys.argv[1:] if argv is None else argv
    okno = Okno(wczytaj(None))
    if "--zamknij-po" in argumenty:
        okno.after(int(argumenty[argumenty.index("--zamknij-po") + 1]), okno.destroy)
    okno.mainloop()


if __name__ == "__main__":
    main()
```

```text title="src/kontakty/dane/przyklad.csv"
imie;email;telefon
Anna Nowak;anna@example.com;600 100 200
Jan Kowalski;jan@example.com;
Ewa Lis;ewa.lis;12 444 55 66
```

```markdown title="README.md"
# kontakty

Menedżer kontaktów: sprawdzanie, wyszukiwanie i eksport plików CSV.

- `kontakty-csv sprawdz [plik]` — wypisuje kontakty z błędami,
- `kontakty-csv szukaj FRAZA [plik]` — wypisuje kontakty pasujące do frazy,
- `kontakty` — okno z listą kontaktów.
```

```text title="LICENSE"
MIT License

Copyright (c) 2026 Jan Kowalski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, subject to the following condition: the
above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED
"AS IS", WITHOUT WARRANTY OF ANY KIND.
```

Logika z rozdziału 16 zmieniła się w jednym miejscu: odczyt rozdzielono na `czytaj_kontakty()`, które przyjmuje otwarty plik, i `wczytaj_csv()` ze ścieżką — bo plik przykładowy leży wewnątrz pakietu i otwiera go `importlib.resources`, nie `open()`. `files("kontakty").joinpath(…)` zwraca obiekt, który działa jak ścieżka niezależnie od tego, czy pakiet leży w katalogu, w archiwum zip czy w pliku wykonywalnym; dane w pakiecie muszą być w nim fizycznie, stąd katalog `dane`. Moduł `cli.py` używa `argparse` z rozdziału 7 „Python Notatki”, rozszerzonego o **podpolecenia** (`sprawdz`, `szukaj`) tworzone przez `add_subparsers()` — każde z własnymi argumentami — których tamten rozdział nie omawiał i zwraca kod wyjścia — `main()` przyjmuje listę argumentów, żeby testy mogły ją wywołać bez procesu. Okno korzysta z tej samej logiki i przyjmuje przełącznik `--zamknij-po` do testów automatycznych, jak zegar z `after()` w rozdziale 16. Plik `LICENSE` (tu skrócony) trafia do pakietu przez `license-files`; identyfikator `MIT` mówi odbiorcy, na jakich zasadach może z kodu korzystać, a pełny tekst dołączamy, bo sama licencja MIT wymaga go w każdej kopii kodu.

## Instalacja edytowalna i polecenia

```powershell title="Terminal"
python -m pip install -e ".[test]"
kontakty-csv --wersja
kontakty-csv sprawdz
kontakty-csv szukaj an
python -m pip show kontakty
```

```{ .text .no-copy }
...
Successfully built kontakty
Installing collected packages: kontakty
Successfully installed kontakty-0.1.0
kontakty-csv 0.1.0
Ewa Lis: adres e-mail musi zawierać znak @ między nazwą a domeną
kontaktów: 3, z błędami: 1
Anna Nowak       anna@example.com         600 100 200
Jan Kowalski     jan@example.com
Name: kontakty
Version: 0.1.0
Summary: Menedżer kontaktów: sprawdzanie, wyszukiwanie i eksport CSV
Home-page: https://example.com/kontakty
Author:
Author-email: Jan Kowalski <jan.kowalski@example.com>
License-Expression: MIT
Location: C:\...\projekt\.venv\Lib\site-packages
Editable project location: C:\...\projekt
Requires:
Required-by:
```

Instalacja edytowalna z rozdziału 7 dostaje dopisek `[test]` — nazwę grupy zależności opcjonalnych, więc pip instaluje także pytest. Od tej chwili polecenia `kontakty-csv` i `kontakty` są dostępne w środowisku z każdego katalogu: pip utworzył w katalogu `Scripts` środowiska pliki `kontakty-csv.exe` i `kontakty.exe`, które importują pakiet i wywołują wskazane funkcje. Kod pozostaje w `src`, a zmiany widać bez ponownej instalacji — ale metadane pip zapisał przy instalacji, więc zmiana `pyproject.toml` (nowe polecenie, zależność) albo numeru `__version__` wymaga ponownego `pip install -e`. `pip show` wyświetla metadane z `pyproject.toml`; autor z adresem e-mail trafia w całości do `Author-email`, a `Requires` i `Required-by` są puste, bo pakiet nie ma zależności i nic od niego nie zależy.

## Testy pakietu

```python title="tests/test_logika.py"
from kontakty.logika import Kontakt, filtruj, sprawdz, wczytaj_csv, zapisz_csv

KONTAKTY = [Kontakt("Anna Nowak", "anna@example.com", "600 100 200"), Kontakt("Jan Kowalski", "jan@example.com"), Kontakt("Ewa Lis", "ewa@firma.pl")]


def test_poprawny_kontakt_bez_bledow():
    assert sprawdz(KONTAKTY[0]) == []


def test_bledy_sa_zbierane_razem():
    bledy = sprawdz(Kontakt("  ", "brak-malpy", "abc"))
    assert len(bledy) == 3


def test_filtrowanie_po_imieniu_i_adresie():
    assert [kontakt.imie for kontakt in filtruj(KONTAKTY, "an")] == ["Anna Nowak", "Jan Kowalski"]


def test_zapis_i_odczyt_csv(tmp_path):
    sciezka = tmp_path / "kontakty.csv"
    zapisz_csv(KONTAKTY, sciezka)
    assert wczytaj_csv(sciezka) == KONTAKTY
```

```python title="tests/test_cli.py"
import pytest

from kontakty import __version__
from kontakty.cli import main


def test_szukaj_wypisuje_pasujace(capsys):
    assert main(["szukaj", "an"]) == 0
    wiersze = capsys.readouterr().out.splitlines()
    assert [wiersz.split()[0] for wiersz in wiersze] == ["Anna", "Jan"]


def test_sprawdz_zglasza_bledny_adres(capsys):
    assert main(["sprawdz"]) == 1
    assert "Ewa Lis" in capsys.readouterr().out


def test_wersja(capsys):
    with pytest.raises(SystemExit) as wyjscie:
        main(["--wersja"])
    assert wyjscie.value.code == 0
    assert capsys.readouterr().out.strip() == f"kontakty-csv {__version__}"
```

```powershell title="Terminal"
python -m pytest -q
```

```{ .text .no-copy }
.......                                                                  [100%]
7 passed in 0.06s
```

Testy importują `kontakty` jak każdy inny zainstalowany pakiet — bez `sys.path.insert()`, którym w rozdziałach 13–16 docieraliśmy do modułów obok testów; to jedna z korzyści instalacji edytowalnej. Test polecenia wywołuje `main()` z listą argumentów i czyta wydruk przez `capsys` z rozdziału 16 „Python Notatki”; `--wersja` kończy program przez `SystemExit`, którego oczekujemy jawnie.

## Metadane z wnętrza

```python title="metadane.py"
from importlib.metadata import distribution, entry_points, requires, version

import kontakty

print(version("kontakty"), kontakty.__version__)
print(requires("kontakty"))
pakiet = distribution("kontakty")
print(pakiet.metadata["Summary"], "|", pakiet.metadata["License-Expression"], "|", pakiet.metadata["Requires-Python"])
print(sorted((punkt.name, punkt.value, punkt.group) for punkt in entry_points(group="console_scripts") if punkt.value.startswith("kontakty")))
print([(punkt.name, punkt.value) for punkt in entry_points(group="gui_scripts")])
```

```{ .text .no-copy }
0.1.0 0.1.0
["pytest>=9; extra == 'test'"]
Menedżer kontaktów: sprawdzanie, wyszukiwanie i eksport CSV | MIT | >=3.12
[('kontakty-csv', 'kontakty.cli:main', 'console_scripts')]
[('kontakty', 'kontakty.okno:main')]
```

Zainstalowany pakiet opisuje katalog `kontakty-0.1.0.dist-info` w `site-packages`, a moduł `importlib.metadata` z biblioteki standardowej udostępnia go bez importowania pakietu: wersję, zależności (z zaznaczeniem grupy `extra`), pola metadanych i zarejestrowane punkty wejścia. To ten sam mechanizm, którym `pip show` znajduje pakiet — a dla programu sposób, by wypisać własną wersję albo odkryć wtyczki innych pakietów.
