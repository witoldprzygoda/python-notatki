# Budowanie i publikacja

Instalacja edytowalna służy programiście. Odbiorca dostaje **pakiet dystrybucyjny**: plik, który pip potrafi zainstalować bez katalogu projektu — z lokalnego dysku, z własnego serwera albo z indeksu PyPI. Ten podrozdział buduje takie pliki, sprawdza ich zawartość, instaluje je w świeżym środowisku i omawia drogę do publikacji.

## Budowanie

```powershell title="Terminal"
python -m build
```

```{ .text .no-copy }
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - hatchling>=1.27
* Getting build dependencies for sdist...
* Installed build dependency versions:
  - hatchling==1.32.4
* Building sdist...
* Building wheel from sdist
* Creating isolated environment: venv+pip...
* Installing packages in isolated environment:
  - hatchling>=1.27
* Getting build dependencies for wheel...
* Installed build dependency versions:
  - hatchling==1.32.4
* Building wheel...
Successfully built kontakty-0.1.0.tar.gz and kontakty-0.1.0-py3-none-any.whl
```

Narzędzie `build` czyta `[build-system]`, dla każdego z dwóch plików tworzy tymczasowe, odizolowane środowisko z podanym backendem (dlatego pobiera Hatchling, nawet jeśli jest już zainstalowany) i zapisuje wynik w katalogu `dist`: **archiwum źródłowe** (ang. *source distribution*, sdist) `kontakty-0.1.0.tar.gz` oraz **koło** (ang. *wheel*) `kontakty-0.1.0-py3-none-any.whl` — gotowy do rozpakowania w `site-packages` plik zip z kodem i metadanymi, budowany z rozpakowanego archiwum, co sprawdza jego kompletność. Nazwa koła mówi, że pakiet działa na dowolnym Pythonie 3 (`py3`), nie zależy od binarnego interfejsu interpretera (`none`, ang. *ABI*) ani od systemu (`any`); pakiety z rozszerzeniami w C mają osobne koła dla każdej wersji Pythona i systemu, np. `cp314-cp314-win_amd64`. Pip preferuje koło, bo instaluje je bez uruchamiania backendu; sdist służy platformom, dla których koła nie ma, i jest źródłem dla dystrybucji systemowych.

## Zawartość koła

```python title="inspekcja.py"
import tarfile
import zipfile
from email import message_from_string
from pathlib import Path

kolo = next(Path("dist").glob("*.whl"))
archiwum = zipfile.ZipFile(kolo)
print(kolo.name)
print(*archiwum.namelist(), sep="\n")
metadane = message_from_string(archiwum.read("kontakty-0.1.0.dist-info/METADATA").decode("utf-8"))
print("---", metadane["Name"], metadane["Version"], metadane["Requires-Python"], metadane["License-Expression"])
print(metadane.get_all("Requires-Dist"), "|", metadane.get_all("Provides-Extra"))
print(archiwum.read("kontakty-0.1.0.dist-info/entry_points.txt").decode("utf-8").strip())
nazwy = tarfile.open(next(Path("dist").glob("*.tar.gz"))).getnames()
print("--- sdist:", sorted(nazwa.split("/")[1] for nazwa in nazwy if nazwa.count("/") == 1 and not nazwa.endswith(".py")), sum("/src/" in nazwa for nazwa in nazwy), sum("/tests/" in nazwa for nazwa in nazwy))
```

```{ .text .no-copy }
kontakty-0.1.0-py3-none-any.whl
kontakty/__init__.py
kontakty/cli.py
kontakty/logika.py
kontakty/okno.py
kontakty/dane/przyklad.csv
kontakty-0.1.0.dist-info/METADATA
kontakty-0.1.0.dist-info/WHEEL
kontakty-0.1.0.dist-info/entry_points.txt
kontakty-0.1.0.dist-info/licenses/LICENSE
kontakty-0.1.0.dist-info/RECORD
--- kontakty 0.1.0 >=3.12 MIT
["pytest>=9; extra == 'test'"] | ['test']
[console_scripts]
kontakty-csv = kontakty.cli:main

[gui_scripts]
kontakty = kontakty.okno:main
--- sdist: ['LICENSE', 'PKG-INFO', 'README.md', 'pyproject.toml'] 5 2
```

Koło zawiera pakiet z danymi (`dane/przyklad.csv` jest w środku, bo leży wewnątrz pakietu) oraz katalog `kontakty-0.1.0.dist-info`: `METADATA` w formacie nagłówków e-mail — stąd `email.message_from_string()` do jego odczytu — z polami odpowiadającymi `[project]`, `entry_points.txt` z poleceniami, `WHEEL` z wersją formatu, licencję i `RECORD` z listą plików i ich skrótami, którą pip uzupełnia przy instalacji o utworzone polecenia i według której odinstalowuje pakiet. Ostatni wiersz opisuje archiwum źródłowe: obok pięciu plików z `src` i dwóch testów zawiera README, licencję, `pyproject.toml` — z niego da się zbudować koło od nowa — i `PKG-INFO` z tymi samymi metadanymi. Hatchling pakuje do archiwum wszystkie pliki projektu nieignorowane przez Git, więc trafiają tam także skrypty pomocnicze z tego rozdziału (pominięte w wydruku); zbędne wykluczamy kluczem `exclude` w `[tool.hatch.build.targets.sdist]`.

## Instalacja z pliku

```powershell title="Terminal"
python -m venv C:\tmp\proba
C:\tmp\proba\Scripts\python.exe -m pip install dist\kontakty-0.1.0-py3-none-any.whl
C:\tmp\proba\Scripts\kontakty-csv.exe szukaj ewa
```

```{ .text .no-copy }
Processing .\dist\kontakty-0.1.0-py3-none-any.whl
Installing collected packages: kontakty
Successfully installed kontakty-0.1.0
Ewa Lis          ewa.lis                  12 444 55 66
```

Nowe środowisko nie ma dostępu do katalogu projektu: pip rozpakowuje koło do `site-packages`, tworzy polecenia w `Scripts` i instaluje zależności z `METADATA` (tu żadnych). Tak samo zainstaluje pakiet odbiorca, któremu prześlemy plik koła, albo pip z opcjami `--no-index --find-links katalog`, które każą szukać plików w katalogu zamiast w indeksie (samo `--find-links` dodaje katalog do źródeł przeszukiwanych obok PyPI) — wystarczające dla pakietów wewnętrznych w firmie. Środowisko próbne warto usunąć po sprawdzeniu.

## Kontrola i publikacja

```powershell title="Terminal"
python -m twine check dist/*
```

```{ .text .no-copy }
Checking dist/kontakty-0.1.0-py3-none-any.whl: PASSED
Checking dist/kontakty-0.1.0.tar.gz: PASSED
```

Twine sprawdza, czy metadane i README (jako Markdown) wyświetlą się poprawnie w indeksie. Publikacja wymaga konta i **tokenu API** — ciągu wygenerowanego w ustawieniach konta, który zastępuje hasło; próbę wykonujemy na TestPyPI, osobnym indeksie do ćwiczeń z własnym kontem i tokenem:

```powershell title="Terminal"
python -m twine upload --repository testpypi dist/*
python -m pip install --index-url https://test.pypi.org/simple/ kontakty
```

Twine pyta tylko o token (nazwę użytkownika `__token__` ustawia sam) albo czyta go ze zmiennej środowiskowej `TWINE_PASSWORD`; tokenu nie zapisujemy w repozytorium, jak klucza API w rozdziale 14. Publikacja na właściwym PyPI to to samo polecenie bez `--repository`. Dwie zasady indeksu: nazwa musi być wolna (przed publikacją sprawdzamy `pypi.org/project/nazwa` albo `python -m pip index versions nazwa`), a raz opublikowanej wersji nie da się podmienić — poprawka to nowa wersja. Instalacja z TestPyPI wymaga `--index-url`, bo pip domyślnie korzysta tylko z PyPI. Nie publikujemy pakietu, którego nie zamierzamy utrzymywać; do przekazania jednej osobie wystarczy plik koła.

## Narzędzia z pipx

```powershell title="Terminal"
pipx run --spec dist\kontakty-0.1.0-py3-none-any.whl kontakty-csv --wersja
```

```{ .text .no-copy }
creating virtual environment...
determining package name from 'C:\\...\\projekt\\dist\\kontakty-0.1.0-py3-none-any.whl'...
creating virtual environment...
installing kontakty from spec 'C:\\...\\projekt\\dist\\kontakty-0.1.0-py3-none-any.whl'...
kontakty-csv 0.1.0
```

Narzędzie wiersza poleceń instalowane do środowiska projektu jest dostępne tylko po aktywacji tego środowiska. **pipx** instaluje każdy pakiet z poleceniami w osobnym środowisku wirtualnym i dodaje polecenia do katalogu `~\.local\bin`, który jednorazowe `pipx ensurepath` wpisuje do zmiennej `PATH`: `pipx install kontakty` (z PyPI) albo `pipx install dist\kontakty-0.1.0-py3-none-any.whl` (z pliku) daje `kontakty-csv` dostępne w każdym terminalu, `pipx run` uruchamia polecenie jednorazowo w środowisku tymczasowym, a `pipx upgrade` i `pipx uninstall` zarządzają narzędziem bez wpływu na inne. Tak instaluje się narzędzia takie jak `ruff` czy `mypy` z rozdziału 16 „Python Notatki”, gdy mają służyć wszystkim projektom. Narzędzie `uv` łączy w jednym programie szybszą instalację pakietów, środowiska i uruchamianie narzędzi; przy jego użyciu polecenia z tego rozdziału mają odpowiedniki (`uv build`, `uv publish`, `uvx`), a `pyproject.toml` pozostaje ten sam.
