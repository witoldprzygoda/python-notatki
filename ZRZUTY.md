# Checklista zrzutów ekranu

Plik roboczy (poza katalogiem `docs/` — nie trafia na stronę).
Znaczniki miejsc w źródłach: `<!-- TODO: screenshot ... -->`
Wyszukiwanie w Git Bash: `grep -rn "TODO: screenshot" docs/`

## Zasady wspólne

- Kadr: ciasno, tylko dialog / panel / fragment — nie całe okno.
- Motyw: stały (jasny), stały poziom powiększenia.
- Nazwy plików: od treści, bez numerów wersji; zapis do `docs/<rozdział>/img/`.
- Odświeżanie: tylko gdy zmieni się treść okna, nie jego oprawa; zrzuty odtwarzamy skryptami
  z `scripts/screenshots/` i `scripts/tk_harness/`, nie ręcznie.
- Treści terminalowe i listowe pokazujemy blokami tekstowymi (`CLAUDE.md`); zrzut tylko tam,
  gdzie obraz niesie informację niewyrażalną tekstem.

## Do wykonania

Brak (stan z 4 X 2026).

## Wykonane

- VS Code (motyw Light+, skala 1,5, interfejs angielski; Python 3.14.8; VS Code 1.140 z 4 X 2026,
  o ile pozycja nie podaje innej wersji) — generowane
  w Windows Sandbox skryptami `scripts/screenshots/vscode/` (`piaskownica.py` na komputerze,
  `vsc_zrzuty.py` w piaskownicy, pomocnicze `wsb/przygotuj.ps1` i `wsb/runner.ps1`); profil
  i rozszerzenia VS Code użytkownika pozostają nietknięte. Odświeżanie: `python
  scripts/screenshots/vscode/piaskownica.py --katalog <katalog-wymiany> wszystko`, przegląd obrazów,
  potem `kopiuj`. Wybrane zrzuty odświeża `wszystko <ID…>` (identyfikatory to klucze słownika
  `SCENARIUSZE` w `vsc_zrzuty.py`) w nowym katalogu wymiany, ponieważ `kopiuj` kopiuje do `docs/`
  wszystkie obrazy z jego podkatalogu `zrzuty`.
    - `01-instalacja/img/vsc-select-interpreter.png`, `vsc-environment-manager.png` — lista
      **Python: Select Interpreter** w projekcie `moj-projekt` ze środowiskami `.venv` i `.venv-t`
      z venv.md (zaznaczona pozycja `.venv`) oraz lista wyboru menedżera środowiska po pozycji
      **Create Virtual Environment...** (konfiguracja.md); scenariusze `interpreter` i `menedzer`,
      tryb rozszerzenia Python Environments (ustawienie `python.useEnvironmentsExtension`, decyzja
      autora z 12 X 2026), obrazy dotychczasowego trybu rozszerzenia Python w wariantach.
      Kompilację 3.14t instaluje managerem, a środowisko `.venv-t` tworzy poleceniem z venv.md skrypt
      `wsb/przygotuj.ps1`. Obrazy z 12 X 2026: VS Code 1.141.0, rozszerzenia Python 2026.8.0
      i Python Environments 1.38.0, Python 3.14.8 i 3.14t. Odświeżenie: `python
      scripts/screenshots/vscode/piaskownica.py --katalog <katalog-wymiany> wszystko interpreter
      menedzer`;
    - `01-instalacja/img/vsc-pylint-blad.png` — `print "hello wrong"` z podkreśleniem pylinta
      i dymkiem komunikatu E0001 (konfiguracja.md);
    - `03-nazwy-typy/img/vsc-pylance-inlay-hint.png` — podpowiedzi typów Pylance dla listingu
      `podpowiedzi.py` (konwersje-i-adnotacje.md);
    - `03-nazwy-typy/img/vsc-mypy-ostrzezenie.png` — błąd typu zgłoszony przez Mypy Type Checker
      dla `wiek: int = "25"` (konwersje-i-adnotacje.md);
    - `08-wyjatki/img/vsc-debugger-pulapka.png`, `vsc-debugger-stos-i-zmienne.png`,
      `vsc-debugger-pasek.png` — pułapka w `debug-silnia.py`, widok Run and Debug i pasek
      narzędzi debugowania (diagnostyka.md);
    - `16-warsztat/img/vsc-testing-panel.png` — widok Testing po uruchomieniu testów
      (testowanie.md);
    - `zastosowania/01-jupyter/img/vsc-notatnik-nowy.png`, `vsc-notatnik-jadro.png` — nowy
      notatnik z przyciskiem Select Kernel i lista wyboru środowiska z `.venv` projektu
      (notatnik-jupyter.md). Od 12 X 2026 piaskownica ma również kompilację 3.14t, którą
      czytelnik instaluje w rozdziale 1, więc scenariusz pokazuje na liście dodatkowy wiersz
      `pythoncore-3.14t-64`; obraz w książce (bez niego) i jego tekst alternatywny czekają
      na decyzję autora.
- `01-instalacja/img/jupyter-interfejs.png` — strona główna Jupyter Notebook (notebook.md);
  `scripts/screenshots/jupyter_interfejs.py`, przeglądarka Edge bez okna.
- `02-konsola/img/repl-kolorowanie.png` — kolorowy nowy REPL (index.md); przechwycenie przez
  pseudokonsolę i render xterm.js w schemacie One Half Light: `scripts/screenshots/repl/`
  (`przechwyc.py`, `renderuj.py`; przygotowanie opisane w `renderuj.py`).
- `zastosowania/15-fastapi/img/fastapi-docs.png` — strona `/docs` (Swagger UI)
  (pierwsza-aplikacja.md); `scripts/screenshots/fastapi_docs.py`, środowisko z wersjami
  FastAPI i uvicorn z rozdziału.
- `zastosowania/16-tkinter/img/*.png` (32 zrzuty okien tkinter i CustomTkinter) — generowane automatycznie
  z listingów rozdziału: harness `scripts/tk_harness/sitecustomize.py` (ładowany przez `PYTHONPATH=scripts/tk_harness`)
  podmienia `mainloop()`, podnosi okna na wierzch i składa ujęcia na neutralnym tle; proces świadomy DPI,
  motyw jasny (ciemny tylko tam, gdzie pokazuje tryb ciemny CustomTkinter). Odświeżanie: ponowne
  uruchomienie harnessu (`ZRZUTY_KATALOG=docs/zastosowania/16-tkinter/img`), nie ręcznie.
- `zastosowania/22-office-obrazy/img/{oryginal,znak-wodny,wykres}.png` — obrazy generowane przez skrypty
  rozdziału (`przeksztalcenia.py`, `rysowanie.py`, `wykres-slupkowy.py`) w stagingu; odświeżanie: ponowne
  uruchomienie skryptów i skopiowanie plików, nie ręcznie.
- `01-instalacja/img/python-cykl-wydan.svg` — wykres okresów wsparcia wersji Pythona ze strony
  devguide.python.org/versions, wycięty bez zmian (instalacja.md); `python scripts/release_cycle_chart.py
  <wynik.svg>` pobiera stronę i zapisuje wykres (istniejącego pliku nie nadpisuje bez `--nadpisz`;
  zapisaną kopię strony czyta opcja `--html=`). Pionowa linia oznacza dzień, w którym devguide wygenerował
  stronę (nagłówek Last-Modified, wypisywany przez skrypt), w rysunku książki — 9 X 2026. Rysunek
  odświeżamy przy zmianie statusu którejś wersji, nie przy samym przesunięciu linii dnia; potem
  sprawdzamy tekst alternatywny i opis faz w instalacja.md.

## Zrezygnowano (decyzja autora z 2 X 2026)

- panel Problems i otwieranie `settings.json` (konfiguracja.md), menu New → Notebook
  (notebook.md), arkusz w Excelu i dokument w Wordzie (rozdział 22 części „Python Zastosowania”);
- wynik Code Runnera (konfiguracja.md) — zamiast zrzutu blok tekstowy z zawartością panelu
  Output, zgodnie z zasadą bloków tekstowych z `CLAUDE.md` (4 X 2026); scenariusz 4 zapisuje
  obrazy panelu wyłącznie do wariantów, jako kontrolę treści bloku.
