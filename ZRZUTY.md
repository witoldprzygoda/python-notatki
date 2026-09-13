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

7. `img/repl-kolorowanie.png` — nowy REPL (Python 3.14) w Windows Terminal
   z widocznym kolorowaniem składni; wpisać np. definicję krótkiej funkcji
   i wyrażenie z łańcuchem, liczbą i komentarzem. Jedyne miejsce, gdzie blok
   tekstowy nie odda treści (kolory).

### konsola-w-praktyce.md

## Do wykonania — rozdział 03

### konwersje-i-adnotacje.md

8. `img/vsc-pylance-inlay-hint.png` — podpowiedź typu (inlay hint) serwera Pylance
   w VSC przy zmiennej z wywnioskowanym typem; kadr: linia kodu + wyświetlony typ.
9. `img/vsc-mypy-ostrzezenie.png` — ostrzeżenie rozszerzenia Mypy Type Checker
    przy przypisaniu wartości o typie innym niż zadeklarowany; kadr: linia kodu
    + podkreślenie i treść ostrzeżenia.

## Do wykonania — rozdział 08

### diagnostyka.md

10. `img/vsc-debugger-pulapka.png` — edytor z plikiem `debug-silnia.py`, pułapka
    (czerwona kropka) w wierszu `return 1` i podświetlony wiersz po zatrzymaniu
    programu (++f5++, konfiguracja **Python File**); kadr: fragment edytora
    z numerami wierszy.
11. `img/vsc-debugger-stos-i-zmienne.png` — widok **Run and Debug** po zatrzymaniu
    na pułapce z punktu 11: panel **Variables** (`n` = 1) i panel **Call Stack**
    (cztery ramki `silnia` i `<module>`); kadr: sam widok boczny.
12. `img/vsc-debugger-pasek.png` — pasek narzędzi debugowania (Continue, Step Over,
    Step Into, Step Out, Restart, Stop) podczas wstrzymania; kadr: sam pasek.
13. `16-warsztat/img/vsc-testing-panel.png` — widok **Testing** w VSC z drzewem testów
    `test_fixtures.py` i `test_kolo.py` (w tym `test_pole_kola[zero]` itd.) po uruchomieniu,
    zielone znaczniki; kadr: sam pasek boczny (testowanie.md, sekcja „Panel Testing w VSC”).

## Wykonane

- `01-instalacja/img/vsc-select-interpreter.png` — lista wyboru interpretera (konfiguracja.md)
- `01-instalacja/img/vsc-environment-manager.png` — wybór menedżera środowiska (konfiguracja.md)
