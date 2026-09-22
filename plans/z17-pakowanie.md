# Projekt rozdziału 17 części „Python Zastosowania” — Pakowanie i dystrybucja

Piąty rozdział ścieżki Aplikacje. Branch: `content/zastosowania-17` (z `dev` po `351c2a6`). Realizacja autonomiczna na polecenie autora z 23 IX 2026.

## Decyzje redakcyjne (23 IX 2026)

1. **Zakres:** pakiet do instalacji (układ `src` z rozdziału 7 „Python Notatki” rozwinięty o pełne metadane `[project]`: opis, README, `requires-python`, licencja z plikiem, autorzy, klasyfikatory, `dependencies`, zależności opcjonalne, adresy, punkty wejścia `[project.scripts]` i `[project.gui-scripts]`, wersja dynamiczna z `__init__.py` przez `[tool.hatch.version]`; dane w pakiecie i `importlib.resources`; polecenie `kontakty-csv` z `argparse` i podpoleceniami, okno `kontakty`; instalacja edytowalna z dodatkiem `[test]`, `pip show`, testy bez `sys.path`; `importlib.metadata`); budowanie i publikacja (`python -m build` → sdist i wheel, zawartość koła, instalacja z pliku w świeżym środowisku, `twine check`, TestPyPI i PyPI z tokenem — bez wykonania, `pipx run`/`pipx install`, wzmianka o uv); zależności i wersje (specyfikatory PEP 440, wersjonowanie semantyczne, `dependencies` a `requirements.txt` a plik blokady z `pip freeze`, `pip check`, `pip index versions`, zależności opcjonalne, `packaging.version`/`SpecifierSet`, wersja w jednym miejscu); aplikacja dla użytkownika (PyInstaller `--onefile --windowed --paths src --collect-data`, plik `.spec`, rozmiar i czas, brak konsoli — bez `print`, ostrzeżenia antywirusa, `--onedir`, ikona; `zipapp` dla narzędzia wiersza poleceń; tabela „co dostarczamy komu”; lista kontrolna). Cztery strony + index. Poza zakresem: publikacja wykonana naprawdę (wymaga konta), podpisywanie, kontenery (jedno zdanie), Nuitka/cx_Freeze (wzmianka), instalatory MSI/Inno Setup (wzmianka), `uv`/Poetry jako menedżery projektu (jedno zdanie), pakiety z rozszerzeniami w C.
2. **Biblioteki i wersje (sonda 23 IX 2026, Python 3.14.7):** build 1.6.1, hatchling 1.32.4, twine 7.0.0, pipx 1.17.5, PyInstaller 6.22.3 (buduje z Tk 9.0.4, ~10 s, `.exe` ~12 MB), packaging 26.3, pytest 9.1.1; setuptools 84.0.0 i uv 0.12.17 tylko jako wzmianki. Plik wymagań narzędzi: `build==1.6.1`, `hatchling==1.32.4`, `twine==7.0.0`, `pipx==1.17.5`, `pyinstaller==6.22.3`, `packaging==26.3` (+ pytest).
3. **Dane:** pakiet `kontakty` (logika z rozdziału 16 przeniesiona do `src/kontakty/logika.py` z rozbiciem na `czytaj_kontakty(plik)` i `wczytaj_csv(sciezka)`; `cli.py`, `okno.py`, `dane/przyklad.csv`), `README.md`, `LICENSE` (MIT), `tests/`. Harness: staging całego projektu z bloków stron (`extract_project.py`), instalacja edytowalna ze stagingu do `venv-ch17` przed weryfikacją (skrypty `metadane.py`, `wersje.py` czytają zainstalowany pakiet), koło zbudowane w stagingu (`inspekcja.py` czyta `dist/`), skrypty budujące `.pyz` i `.exe` przez `subprocess` (wynik deterministyczny: nazwy plików, kody wyjścia, rozmiar w MB zaokrąglony). Bloki terminalowe (`build`, `twine`, `pip`, `pipx`, PyInstaller) z rzeczywistych uruchomień, ścieżki skrócone. Okno `kontakty` przyjmuje `--zamknij-po MS` do testów automatycznych.
4. **Fakty sprawdzone 23 IX 2026:** hatchling znajduje `src/<nazwa>` bez konfiguracji; `dynamic = ["version"]` + `[tool.hatch.version] path`; `python -m build` buduje sdist i wheel w izolacji (pobiera backend); koło zawiera `kontakty/…`, `dane/przyklad.csv`, `kontakty-0.1.0.dist-info/{METADATA,WHEEL,entry_points.txt,licenses/LICENSE,RECORD}`; `twine check` → PASSED; `pip install dist/*.whl` w świeżym venv tworzy `Scripts/kontakty-csv.exe` i `Scripts/kontakty.exe`; `pipx run --spec koło polecenie` działa; `importlib.metadata`: `version()`, `entry_points(group="console_scripts")`, `requires()` zwraca `["pytest>=9; extra == 'test'"]`, `distribution().metadata["License-Expression"]`; `zipapp` z `-m pakiet.modul:funkcja` — `importlib.resources.files().open()` działa w archiwum (ścieżka `zipfile.Path`, nie `os.PathLike` — stąd `czytaj_kontakty(plik)`); PyInstaller: `--paths src --collect-data kontakty`, plik `.spec` z `collect_data_files`, `warn-*.txt`, w aplikacji `--windowed` `print()` z polskimi znakami na przechwyconym stdout → `UnicodeEncodeError` (cp1252) — w oknie nie drukować; exe uruchamia się i zamyka z `--zamknij-po`.
5. **Terminy:** „pakiet dystrybucyjny” (ang. *distribution package*), „koło” (ang. *wheel*), „archiwum źródłowe” (ang. *source distribution*, sdist), „backend budowania”, „punkt wejścia” (ang. *entry point*), „instalacja edytowalna”, „specyfikator wersji” (ang. *version specifier*), „wersjonowanie semantyczne” (ang. *semantic versioning*), „plik blokady” (ang. *lock file*), „zależności opcjonalne” (ang. *optional dependencies*, *extras*), „metadane”, „token API”.
6. Odsyłacze wstecz: „Python Notatki” 1 (pip, venv, plik wymagań), 7 (układ `src`, `pyproject.toml`, instalacja edytowalna, `__main__`), 9 (pathlib, csv), 16 (pytest, `pyproject.toml` narzędzi, `requirements-dev.txt`); „Python Zastosowania” 1 (środowisko projektu, `pip freeze`), 15 (uruchomienie serwera), 16 (menedżer kontaktów, `--zamknij-po` jak `after`). Zapowiedź: 18 (projekt aplikacji) — `TODO`.
7. Domknięcia: markery „pakowaniu i dystrybucji” w 15/testy-i-uruchomienie i 16/projekt-kontakty → `17-pakowanie/index.md`; marker „projekt aplikacji” zostaje.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i pliki |
|---|---|---|
| `index.md` | Wprowadzenie / „17. Pakowanie i dystrybucja” | cel; narzędzia i wersje; plik wymagań; ---; ## W tym rozdziale (4) |
| `pakiet.md` | Pakiet do instalacji | Od projektu do pakietu (drzewo, `pyproject.toml`); Kod pakietu (`src/kontakty/__init__.py`, `logika.py`, `cli.py`, `okno.py`, `dane/przyklad.csv`, `README.md`, `LICENSE`); Instalacja edytowalna i polecenia (terminal); Testy pakietu (`tests/test_logika.py`, `tests/test_cli.py`, pytest); Metadane z wnętrza (`metadane.py`) |
| `budowanie.md` | Budowanie i publikacja | Budowanie (`python -m build`); Zawartość koła (`inspekcja.py`); Instalacja z pliku (terminal, świeże środowisko); Kontrola i publikacja (`twine check`, TestPyPI, PyPI); Narzędzia z pipx |
| `zaleznosci.md` | Zależności i wersje | Specyfikatory wersji (tabela, `wersje.py`); Zależności pakietu a plik wymagań; Zależności opcjonalne; Wersja w jednym miejscu |
| `aplikacja-dla-uzytkownika.md` | Aplikacja dla użytkownika | Skrypt uruchamiający (`uruchom_okno.py`); PyInstaller (terminal, `zbuduj-exe.py`); Archiwum zipapp (`zbuduj-pyz.py`); Co dostarczamy komu (tabela); Lista kontrolna; Dalej (TODO 18) |

Szacunek: 700–850 linii; bez wykresów i zrzutów.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 16)

```yaml
      - 17. Pakowanie i dystrybucja:
          - Wprowadzenie: zastosowania/17-pakowanie/index.md
          - Pakiet do instalacji: zastosowania/17-pakowanie/pakiet.md
          - Budowanie i publikacja: zastosowania/17-pakowanie/budowanie.md
          - Zależności i wersje: zastosowania/17-pakowanie/zaleznosci.md
          - Aplikacja dla użytkownika: zastosowania/17-pakowanie/aplikacja-dla-uzytkownika.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `aplikacja-dla-uzytkownika.md` | projekt aplikacji | rozdział 18 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/15-fastapi/testy-i-uruchomienie.md` (marker pakowanie) | `17-pakowanie/index.md` |
| `zastosowania/16-tkinter/projekt-kontakty.md` (marker pakowanie) | `17-pakowanie/index.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/`; rozdział 7 „Python Notatki” (struktura-projektu.md) wprowadza układ `src`, minimalny `pyproject.toml` z Hatchling i instalację edytowalną — rozdział 17 buduje na tym bez powtarzania.

## Listy kontrolne

- Przed commitem: staging z bloków; `pip install -e stage17[test]` do `venv-ch17`; `python -m build` w stagingu; `refresh_outputs.py`; bloki terminalowe z rzeczywistych uruchomień; `verify_page.py` dwa przebiegi (`--skip` dla testów); pytest w stagingu; oba buildy `--strict`; cudzysłowy; kolokwializmy; recenzje z weryfikacją uwag.
- Po commicie: domknięcia w rozdziałach 15 i 16, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
