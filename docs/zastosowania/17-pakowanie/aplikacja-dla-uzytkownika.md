# Aplikacja dla użytkownika

Koło i `pip` zakładają, że odbiorca ma Pythona i wie, czym jest środowisko wirtualne. Użytkownik aplikacji okienkowej oczekuje pliku, który uruchomi podwójnym kliknięciem. Ten podrozdział buduje z okna `kontakty` plik `.exe` narzędziem **PyInstaller**, a z polecenia `kontakty-csv` — archiwum `.pyz` modułem `zipapp` z biblioteki standardowej, i porównuje, co komu dostarczać.

## Skrypt uruchamiający

```python title="uruchom_okno.py"
from kontakty.okno import main

if __name__ == "__main__":
    main()
```

PyInstaller zaczyna od skryptu, nie od punktu wejścia z `pyproject.toml`, więc w katalogu projektu tworzymy plik, który importuje pakiet i wywołuje `main()`. Analizując importy skryptu, PyInstaller zbiera moduły pakietu, biblioteki standardowej i Tcl/Tk.

## PyInstaller

```powershell title="Terminal"
python -m PyInstaller --onefile --windowed --name Kontakty --paths src --collect-data kontakty uruchom_okno.py
dist\Kontakty.exe
```

```{ .text .no-copy }
146 INFO: PyInstaller: 6.22.3, contrib hooks: 2026.7
146 INFO: Python: 3.14.7
178 INFO: Platform: Windows-11-10.0.26200-SP0
...
7614 INFO: Appending PKG archive to EXE
7658 INFO: Fixing EXE headers
7874 INFO: Building EXE from EXE-00.toc completed successfully.
7876 INFO: Build complete! The results are available in: C:\...\projekt\dist
```

```python title="zbuduj-exe.py"
import subprocess
import sys
from pathlib import Path

polecenie = [sys.executable, "-m", "PyInstaller", "--onefile", "--windowed", "--name", "Kontakty", "--paths", "src", "--collect-data", "kontakty", "--noconfirm", "--log-level", "WARN", "uruchom_okno.py"]
budowanie = subprocess.run(polecenie, capture_output=True, text=True, encoding="utf-8")
print("PyInstaller:", budowanie.returncode, "| pliki:", sorted(sciezka.name for sciezka in Path("dist").iterdir()))
plik = Path("dist/Kontakty.exe")
print(f"{plik.name}: {plik.stat().st_size / 1e6:.0f} MB")
print("uruchomienie:", subprocess.run([str(plik), "--zamknij-po", "1500"]).returncode)
```

```{ .text .no-copy }
PyInstaller: 0 | pliki: ['Kontakty.exe', 'kontakty-0.1.0-py3-none-any.whl', 'kontakty-0.1.0.tar.gz']
Kontakty.exe: 12 MB
uruchomienie: 0
```

Opcje: `--onefile` pakuje wszystko w jeden plik, który przy starcie rozpakowuje się do katalogu tymczasowego (wolniejszy start, jeden plik do wysłania); bez niej powstaje katalog `dist/Kontakty` z plikiem `.exe` i podkatalogiem `_internal` z bibliotekami (szybszy start, wiele plików). `--windowed` wyłącza okno konsoli — właściwe dla aplikacji okienkowej, ale wtedy `sys.stdout` to `None`: `print()` nie wypisuje nic, zapis do `sys.stdout` wprost kończy program wyjątkiem, a gdy wyjście przechwytuje inny proces, wydruk polskich znaków zgłasza `UnicodeEncodeError` — komunikaty aplikacji okienkowej kierujemy do pliku modułem `logging` z rozdziału 8 „Python Notatki”. `--paths src` wskazuje, gdzie szukać pakietu, `--collect-data kontakty` dołącza pliki danych pakietu (`przyklad.csv`), które nie są modułami i bez tej opcji zostałyby pominięte; `--name` nadaje nazwę, `--icon plik.ico` ikonę. Każde uruchomienie ze skryptem zapisuje na nowo plik `Kontakty.spec` — opis budowania w Pythonie, który można edytować i odtąd podawać zamiast skryptu i opcji (`python -m PyInstaller Kontakty.spec`) — oraz katalog `build/Kontakty` z plikiem `warn-Kontakty.txt`: listą modułów, których nie udało się znaleźć; większość dotyczy importów warunkowych dla innych systemów. Plik ma kilkanaście megabajtów, bo zawiera interpreter i Tcl/Tk; czas budowania to kilka sekund. Skrypt `zbuduj-exe.py` robi to samo z poziomu Pythona i sprawdza, że plik uruchamia się i zamyka — tak można włączyć budowanie do automatycznej kontroli.

Dwie pułapki dystrybucji plików `.exe`: programy antywirusowe często oznaczają jako podejrzane nieznane pliki rozpakowujące się w katalogu tymczasowym — pomaga wariant katalogowy i podpis cyfrowy — a plik zbudowany na jednej wersji Windows nie musi działać na dużo starszej; budujemy na najstarszym systemie, który wspieramy. PyInstaller nie buduje krzyżowo: plik dla macOS lub Linuksa powstaje na tym systemie. Alternatywy: Nuitka kompiluje kod do C (szybsze wykonanie, dłuższe budowanie i wymagany kompilator C), a narzędzie takie jak Inno Setup tworzy z katalogu `dist` instalator ze skrótem w menu Start i wpisem na liście zainstalowanych aplikacji.

## Archiwum zipapp

```python title="zbuduj-pyz.py"
import os
import subprocess
import sys
import zipapp
from pathlib import Path

zipapp.create_archive("src", target="kontakty-csv.pyz", main="kontakty.cli:main", interpreter="/usr/bin/env python3", filter=lambda sciezka: "__pycache__" not in sciezka.parts)
print(f"kontakty-csv.pyz: {Path('kontakty-csv.pyz').stat().st_size / 1000:.0f} kB")
srodowisko = {**os.environ, "PYTHONUTF8": "1"}
for argumenty in (["--wersja"], ["szukaj", "ewa"], ["sprawdz"]):
    wynik = subprocess.run([sys.executable, "kontakty-csv.pyz", *argumenty], capture_output=True, text=True, encoding="utf-8", env=srodowisko)
    print(wynik.returncode, "|", wynik.stdout.strip().replace("\n", " / "))
```

```{ .text .no-copy }
kontakty-csv.pyz: 6 kB
0 | kontakty-csv 0.1.0
0 | Ewa Lis          ewa.lis                  12 444 55 66
0 | Ewa Lis: adres e-mail musi zawierać znak @ między nazwą a domeną / kontaktów: 3, z błędami: 1
```

Moduł `zipapp` z biblioteki standardowej pakuje katalog `src` w jeden plik zip z nagłówkiem, który Python uruchamia jak skrypt: `python kontakty-csv.pyz szukaj ewa` (na Linuksie i macOS wystarczy `./kontakty-csv.pyz` dzięki wierszowi `interpreter`). Argument `main` wskazuje funkcję, jak punkt wejścia w `pyproject.toml`, ale wygenerowany `__main__.py` wywołuje ją bez `sys.exit()` — stąd kod 0 po `sprawdz` mimo błędów, gdy `kontakty-csv sprawdz` kończy się kodem 1; dane w pakiecie działają, bo `importlib.resources` czyta je z archiwum — to powód, dla którego `cli.py` otwiera plik przykładowy przez `files().open()`, a nie przez ścieżkę. Odbiorca potrzebuje Pythona, nie potrzebuje pip ani instalacji; zależności trzeba wcześniej skopiować do pakowanego katalogu (`python -m pip install --target src nazwa`) i nie mogą zawierać rozszerzeń w C, bo Python nie importuje ich z archiwum, a `importlib.metadata` nie znajdzie w archiwum metadanych — stąd wersja w `__init__.py`. Zmienna `PYTHONUTF8=1` w uruchomieniu podrzędnym wymusza UTF-8 na wyjściu, bo gdy wyjście przechwytuje inny proces, Python na Windows używa strony kodowej systemu (tu cp1252) i polskie znaki w wydruku zgłosiłyby `UnicodeEncodeError`; w oknie konsoli wydruk działa — ten sam problem rozwiązuje `python -X utf8`.

## Co dostarczamy komu

| Odbiorca | Postać | Narzędzie |
|---|---|---|
| programista używający kodu w swoim projekcie | koło w indeksie PyPI albo plik `.whl` | `build`, `twine` |
| użytkownik narzędzia wiersza poleceń z Pythonem | pakiet z `[project.scripts]` przez `pipx` albo archiwum `.pyz` | `pipx`, `zipapp` |
| użytkownik aplikacji okienkowej bez Pythona | plik `.exe` albo katalog, opcjonalnie z instalatorem | PyInstaller, Inno Setup |
| serwer (aplikacja FastAPI z rozdziału 15) | kod z plikiem blokady w środowisku wirtualnym albo obraz kontenera | `pip`, Docker |

## Lista kontrolna

- **`pyproject.toml`** z pełnymi metadanymi, licencją, `requires-python` i punktami wejścia; wersja w jednym miejscu.
- **Zależności** jako zakresy w `dependencies`; narzędzia w `requirements.txt`; plik blokady dla wdrożeń.
- **Dane pakietu** w jego katalogu, czytane przez `importlib.resources`.
- **`python -m build`** i `twine check` przed każdą publikacją; wersja opublikowana jest ostateczna.
- **Testy** przez instalację edytowalną, bez `sys.path`; polecenia testowane przez `main(argv)`.
- **Aplikacja okienkowa** bez `print()`; budowanie pliku sprawdzone uruchomieniem.

## Dalej: projekt

Ścieżka aplikacji ma wszystkie elementy: bazę danych, API, okno i sposób dostarczenia. Projekt ścieżki połączy je w jeden program — sklep z warstwą danych, usługą FastAPI i oknem klienta — spakowany tak, jak opisano tutaj — [rozdział 18](../18-projekt-aplikacja/index.md).
