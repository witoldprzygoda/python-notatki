# Checklista zrzutów ekranu

Plik roboczy (poza katalogiem `docs/` — nie trafia na stronę).
Znaczniki miejsc w źródłach: `<!-- TODO: screenshot ... -->`
Wyszukiwanie w Git Bash: `grep -rn "TODO: screenshot" docs/`

## Zasady wspólne

- Kadr: ciasno, tylko dialog / panel / fragment — nie całe okno.
- Motyw: stały (jasny), stały poziom powiększenia.
- Nazwy plików: od treści, bez numerów wersji; zapis do `docs/<rozdział>/img/`.
- Odświeżanie: tylko gdy zmieni się treść okna, nie jego oprawa.

## Do wykonania — rozdział 01

### konfiguracja.md

1. `img/vsc-pylint-blad.png` — plik `main.py` z treścią `print "hello wrong"`;
   kadr: linia kodu z podkreśleniem błędu + dymek podpowiedzi pylint.
2. `img/vsc-problems.png` — panel **Problems** (++ctrl+shift+m++) z widocznym
   wpisem błędu z punktu 1.
3. `img/vsc-settings-json.png` — paleta poleceń z wpisanym
   **Preferences: Open User Settings (JSON)** (przed zatwierdzeniem).
4. `img/vsc-code-runner.png` — terminal VSC z wynikiem uruchomienia
   `print("pierwszy program")` przez Code Runner (++ctrl+alt+n++).

### notebook.md

5. `img/jupyter-interfejs.png` — strona główna Jupyter Notebook w przeglądarce
   (po `jupyter notebook`); kadr: pasek narzędzi + lista plików.
6. `img/jupyter-new-notebook.png` — rozwinięte menu **New → Notebook**.

## Do wykonania — rozdział 02

### index.md (Konsola)

7. `img/idle-print-podpowiedz.png` — IDLE, dymek z sygnaturą podczas wpisywania
   `print(`; kadr: linia edycji + dymek.
8. `img/repl-kolorowanie.png` — nowy REPL (Python 3.14) w Windows Terminal
   z widocznym kolorowaniem składni; wpisać np. definicję krótkiej funkcji
   i wyrażenie z łańcuchem, liczbą i komentarzem. Jedyne miejsce, gdzie blok
   tekstowy nie odda treści (kolory).

## Wykonane

- `01-instalacja/img/vsc-select-interpreter.png` — lista wyboru interpretera (venv.md)
- `01-instalacja/img/vsc-environment-manager.png` — wybór menedżera środowiska (venv.md)
