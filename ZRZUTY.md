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

- VS Code (motyw Light+, skala 1,5 jak w dwóch pierwszych zrzutach z rozdziału 1, interfejs angielski;
  VS Code 1.140, Python 3.14.8) — generowane w Windows Sandbox skryptami
  `scripts/screenshots/vscode/` (`piaskownica.py` na komputerze, `vsc_zrzuty.py` w piaskownicy,
  pomocnicze `wsb/przygotuj.ps1` i `wsb/runner.ps1`); profil i rozszerzenia VS Code użytkownika
  pozostają nietknięte. Odświeżanie: `python scripts/screenshots/vscode/piaskownica.py
  --katalog <katalog-wymiany> wszystko`, przegląd obrazów, potem `kopiuj`.
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
      (notatnik-jupyter.md).
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
- `01-instalacja/img/vsc-select-interpreter.png` — lista wyboru interpretera (konfiguracja.md)
- `01-instalacja/img/vsc-environment-manager.png` — wybór menedżera środowiska (konfiguracja.md)

## Zrezygnowano (decyzja autora z 2 X 2026)

- panel Problems i otwieranie `settings.json` (konfiguracja.md), menu New → Notebook
  (notebook.md), arkusz w Excelu i dokument w Wordzie (rozdział 22 części „Python Zastosowania”);
- wynik Code Runnera (konfiguracja.md) — zamiast zrzutu blok tekstowy z zawartością panelu
  Output, zgodnie z zasadą bloków tekstowych z `CLAUDE.md` (4 X 2026).
