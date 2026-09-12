# Diagnostyka — ślad wywołań (traceback) i debugger

Wyjątek, którego nikt nie przechwycił, kończy program śladem wywołań. Ślad jest najdokładniejszym opisem tego, co się stało, jaki daje interpreter, i warto umieć z niego korzystać. Ten podrozdział dotyczy warsztatu: jak czytać ślad systematycznie, jak zapisać go z programu bez przerywania pracy oraz jak zatrzymać program w wybranym miejscu i obejrzeć jego stan — pod debuggerem Visual Studio Code, zapowiedzianym w rozdziale 1, i w terminalu za pomocą funkcji `breakpoint()`.

## Czytanie śladu wywołań

Anatomię śladu opisaliśmy w podrozdziale [Obsługa wyjątków](obsluga-wyjatkow.md#anatomia-sladu-wywoan); tu zbieramy ją w procedurę. Program poniżej ma błąd, który ujawnia się dopiero dla pewnych danych:

```python title="czytanie.py"
def srednia(dane):
    """Zwraca średnią arytmetyczną listy liczb."""
    return sum(dane) / len(dane)


def srednia_grupy(oceny, grupa):
    """Zwraca średnią ocen podanej grupy."""
    return srednia(oceny[grupa])


def raport(oceny):
    """Wypisuje średnią każdej grupy."""
    for grupa in oceny:
        print(grupa, srednia_grupy(oceny, grupa))


raport({"A": [4, 5], "B": []})
```

```{ .text .no-copy }
A 4.5
Traceback (most recent call last):
  File "czytanie.py", line 17, in <module>
    raport({"A": [4, 5], "B": []})
    ~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "czytanie.py", line 14, in raport
    print(grupa, srednia_grupy(oceny, grupa))
                 ~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "czytanie.py", line 8, in srednia_grupy
    return srednia(oceny[grupa])
  File "czytanie.py", line 3, in srednia
    return sum(dane) / len(dane)
           ~~~~~~~~~~^~~~~~~~~~~
ZeroDivisionError: division by zero
```

Ślad czytamy w trzech krokach. Krok pierwszy: ostatni wiersz — **co** się stało. `ZeroDivisionError` przy dzieleniu oznacza, że `len(dane)` wyniosło zero, czyli funkcja otrzymała pustą listę. Krok drugi: ostatnia ramka — **gdzie** wyjątek został zgłoszony: wiersz 3, funkcja `srednia()`; znaczniki pod wierszem wskazują dzielenie. Krok trzeci: ramki wyżej, od dołu ku górze — **skąd** przyszły dane: `srednia_grupy()` przekazała `oceny[grupa]`, a `raport()` iterowała po grupach; wiersz `A 4.5` wypisany przed śladem mówi, że grupa `A` została przetworzona poprawnie, więc pustą listą jest grupa `B`. Dopiero teraz podejmujemy decyzję, gdzie leży błąd i gdzie go naprawić: nie w `srednia()`, która dla pustej listy nie ma sensownego wyniku i słusznie zawodzi, lecz w `raport()`, który powinien grupy bez ocen pominąć albo opisać — w duchu podrozdziału o zgłaszaniu wyjątków `srednia()` mogłaby też zgłaszać `ValueError` z czytelnym komunikatem zamiast pozwolić na `ZeroDivisionError`.

Dwie uwagi o ramkach spoza własnego kodu. Program uruchomiony przez `python -m` — jak testy w podrozdziale [Struktura projektu i pierwsze testy](../07-moduly/struktura-projektu.md#katalog-tests), gdzie pominęliśmy je wierszem `...` — ma na początku śladu dwie ramki `<frozen runpy>` mechanizmu uruchamiającego:

```powershell title="Terminal"
python -m czytanie
```

```{ .text .no-copy }
A 4.5
Traceback (most recent call last):
  File "<frozen runpy>", line 203, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\...\projekt\czytanie.py", line 17, in <module>
    raport({"A": [4, 5], "B": []})
    ~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
...
```

Ramki te pomijamy; numery wierszy w nich zależą od wersji interpretera. Gdy błąd powstaje wewnątrz funkcji bibliotecznej wywołanej z naszego kodu, ślad zawiera ramki z plików biblioteki (ścieżki z katalogu `Lib` instalacji albo `site-packages`); przyczyna leży wtedy niemal zawsze w najniższej ramce **własnej** — w argumentach, które przekazaliśmy — i od niej zaczynamy czytanie. Łańcuchy wyjątków z podrozdziału [Zgłaszanie wyjątków](zglaszanie-wyjatkow.md#ponowne-zgoszenie-i-ancuchy-wyjatkow) czytamy od góry: pierwszy ślad opisuje przyczynę, ostatni — wyjątek, który zatrzymał program.

## Moduł `traceback`

Czasem program ma pracować dalej mimo błędu, ale ślad nie powinien przepaść — na przykład przy przetwarzaniu wielu wpisów chcemy pominąć błędny, zapisując jednak pełną informację o nim. Moduł `traceback` z biblioteki standardowej udostępnia to, co interpreter robi przy nieprzechwyconym wyjątku, jako funkcje do wywołania z klauzuli `except`: `print_exc()` wypisuje ślad bieżącego wyjątku na strumień błędów, a `format_exc()` zwraca ten sam tekst jako łańcuch:

```python title="przetwarzanie.py"
import traceback


def przetworz(wpisy):
    """Sumuje poprawne wpisy, a dla błędnych wypisuje ślad i pracuje dalej."""
    suma = 0
    for wpis in wpisy:
        try:
            suma += int(wpis)
        except ValueError:
            traceback.print_exc()
    return suma


print(przetworz(["1", "x", "3"]))
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "przetwarzanie.py", line 9, in przetworz
    suma += int(wpis)
            ~~~^^^^^^
ValueError: invalid literal for int() with base 10: 'x'
4
```

Ślad ma tę samą postać, co przy nieprzechwyconym wyjątku, ale program dokończył pętlę i zwrócił sumę poprawnych wpisów. Wersja z `format_exc()` pozwala ślad zapisać — do pliku dziennika albo do przesłania — zamiast wypisywać; w następnym podrozdziale zobaczymy, że moduł `logging` robi to jednym wywołaniem. Wypisywanie śladów w klauzuli `except` jest właściwe w kodzie na najwyższym poziomie programu, który decyduje o kontynuowaniu pracy; funkcje pomocnicze, zgodnie z zasadą z podrozdziału o stylu, przekazują wyjątek dalej.

## Debugger w Visual Studio Code

Ślad opisuje stan programu w chwili błędu, ale nie mówi, jak do niego doszło — jakie wartości miały nazwy kilka kroków wcześniej. Wstawianie `print()` w kolejnych miejscach jest metodą pracochłonną i pozostawia w kodzie instrukcje, które trzeba potem usunąć. **Debugger** pozwala zatrzymać program w dowolnym wierszu, obejrzeć wartości wszystkich nazw i stos wywołań, po czym wykonywać program wiersz po wierszu. W podrozdziale [Konfigurowanie narzędzi](../01-instalacja/konfiguracja.md#uruchamianie-kodu-code-runner) wspomnieliśmy o uruchamianiu klawiszem ++f5++; teraz opisujemy tę pracę w całości na przykładzie rekurencyjnej silni z rozdziału 6:

```python title="debug-silnia.py"
def silnia(n):
    """Zwraca silnię nieujemnej liczby całkowitej n."""
    if n <= 1:
        return 1
    return n * silnia(n - 1)


print(silnia(4))
```

### Pułapki i uruchomienie

Debugowanie w VSC obsługuje rozszerzenie **Python Debugger** (identyfikator `ms-python.debugpy`), instalowane automatycznie wraz z rozszerzeniem Python z rozdziału 1; nie wymaga osobnej instalacji ani konfiguracji. **Pułapka** (ang. *breakpoint*) to miejsce, w którym debugger ma zatrzymać program: ustawiamy ją, klikając margines na lewo od numeru wiersza (pojawia się czerwona kropka) albo naciskając ++f9++ w wybranym wierszu. Ustawmy pułapkę w wierszu `return 1`, a następnie naciśnijmy ++f5++. Przy pierwszym uruchomieniu VSC pyta o rodzaj konfiguracji — wybieramy **Python File** — i uruchamia bieżący plik pod kontrolą debuggera w terminalu zintegrowanym. Program zatrzymuje się na pułapce: wiersz jest podświetlony, a wykonanie wstrzymane **przed** jego wykonaniem.

<!-- TODO: screenshot — edytor z pułapką (czerwona kropka) w wierszu return 1 i podświetlonym wierszem po zatrzymaniu; kadr: fragment edytora z numerami wierszy -->

### Wykonanie krokowe i podgląd zmiennych

Po zatrzymaniu widok **Run and Debug** (ikona trójkąta z sylwetką owada na pasku bocznym, skrót ++ctrl+shift+d++) pokazuje stan programu w kilku panelach. **Variables** wypisuje nazwy lokalne bieżącej ramki i ich wartości — tu `n` równe `1` — oraz nazwy globalne modułu. **Call Stack** pokazuje stos wywołań: cztery ramki `silnia` (dla `n` równego 1, 2, 3 i 4) i ramkę `<module>`, dokładnie jak ramki w śladzie wywołań, tyle że dla programu, który jeszcze się nie zakończył; kliknięcie innej ramki przełącza panel Variables na jej nazwy, więc można obejrzeć `n` w każdym poziomie rekurencji. **Watch** pozwala wpisać własne wyrażenie, na przykład `n * 2`, obliczane ponownie po każdym kroku, a **Debug Console** na dole okna przyjmuje dowolne wyrażenia Pythona obliczane w kontekście wstrzymanej ramki — tak jak konsola interaktywna, ale z dostępem do bieżących nazw programu. Panel **Breakpoints** zbiera pułapki całego projektu i pozwala je wyłączać bez usuwania.

<!-- TODO: screenshot — panele Variables (n = 1) i Call Stack (cztery ramki silnia i <module>) po zatrzymaniu na pułapce; kadr: sam widok Run and Debug -->

Pasek narzędzi debugowania u góry okna steruje dalszym wykonaniem. **Continue** (++f5++) wznawia program do następnej pułapki albo do końca; **Step Over** (++f10++) wykonuje bieżący wiersz w całości, traktując wywołanie funkcji jako jeden krok; **Step Into** (++f11++) wchodzi do wywoływanej funkcji; **Step Out** (++shift+f11++) kończy bieżącą funkcję i zatrzymuje się po powrocie z niej; **Restart** i **Stop** uruchamiają program od nowa albo przerywają. W naszym programie ++shift+f11++ naciśnięte kilka razy pokazuje, jak kolejne wywołania `silnia()` zwracają `1`, `2`, `6` i `24` — wartość zwracana jest po powrocie z funkcji widoczna w panelu Variables jako osobna pozycja oznaczona słowem *return*.

<!-- TODO: screenshot — pasek narzędzi debugowania (Continue, Step Over, Step Into, Step Out, Restart, Stop); kadr: sam pasek -->

### Pułapki warunkowe i plik `launch.json`

Pułapka może zatrzymywać program tylko wtedy, gdy spełniony jest warunek: kliknięcie prawym przyciskiem na kropce i wybór **Edit Breakpoint** pozwala wpisać wyrażenie, na przykład `n == 3`, albo liczbę trafień, po której debugger ma się zatrzymać. Jest to szczególnie przydatne w pętlach o tysiącach obrotów, gdy błąd występuje dla jednej wartości. Podobnym narzędziem jest **pułapka rejestrująca** (ang. *logpoint*) — pułapka, która nie zatrzymuje programu, lecz wypisuje komunikat z wartościami wyrażeń w nawiasach klamrowych; zastępuje tymczasowe `print()` bez zmiany kodu.

Uruchomienie klawiszem ++f5++ z wyborem **Python File** wystarcza do plików uruchamianych bez argumentów. Gdy program przyjmuje argumenty wiersza poleceń z rozdziału 7 albo ma być uruchamiany w innym katalogu, konfigurację zapisujemy w pliku `launch.json` w katalogu `.vscode` projektu; VSC tworzy go po wybraniu w widoku Run and Debug pozycji **create a launch.json file**:

```json title=".vscode/launch.json"
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: bieżący plik",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "args": [],
            "justMyCode": true
        }
    ]
}
```

Pole `"type"` musi mieć wartość `"debugpy"` — dawna wartość `"python"` jest przestarzała i VSC proponuje jej zamianę. `"program": "${file}"` oznacza bieżący plik edytora; `"console"` wskazuje terminal zintegrowany, w którym działa `input()`; do listy `"args"` wpisujemy argumenty wiersza poleceń, każdy jako osobny łańcuch, a `"justMyCode": true` sprawia, że wykonanie krokowe nie wchodzi do kodu biblioteki standardowej ani zainstalowanych pakietów. Pozostałe pola — katalog roboczy `"cwd"`, zatrzymanie w pierwszym wierszu `"stopOnEntry"` — opisuje dokumentacja VSC *Python debugging in VS Code*.

## Funkcja `breakpoint()` i pdb

Debugger istnieje także poza VSC. Funkcja wbudowana `breakpoint()` wstawiona w kod zatrzymuje program w tym miejscu i uruchamia **pdb** — debugger z biblioteki standardowej działający w terminalu, w którym program został uruchomiony. Wstawmy ją do silni przed `return 1`:

```python title="debug-pdb.py"
def silnia(n):
    """Zwraca silnię nieujemnej liczby całkowitej n."""
    if n <= 1:
        breakpoint()
        return 1
    return n * silnia(n - 1)


print(silnia(4))
```

```powershell title="Terminal"
python debug-pdb.py
```

Program zatrzymuje się i wyświetla znak zachęty `(Pdb)`, przy którym wpisujemy polecenia. Sesja z pięcioma poleceniami — `w` (ang. *where*, stos wywołań), `p n` (ang. *print*, wartość wyrażenia), `u` (ang. *up*, przejście do ramki wyżej), ponownie `p n` i `c` (ang. *continue*, wznowienie) — wygląda tak:

```{ .text .no-copy }
> C:\...\projekt\debug-pdb.py(4)silnia()
-> breakpoint()
(Pdb) w
  C:\...\projekt\debug-pdb.py(9)<module>()
-> print(silnia(4))
  C:\...\projekt\debug-pdb.py(6)silnia()
-> return n * silnia(n - 1)
  C:\...\projekt\debug-pdb.py(6)silnia()
-> return n * silnia(n - 1)
  C:\...\projekt\debug-pdb.py(6)silnia()
-> return n * silnia(n - 1)
> C:\...\projekt\debug-pdb.py(4)silnia()
-> breakpoint()
(Pdb) p n
1
(Pdb) u
> C:\...\projekt\debug-pdb.py(6)silnia()
-> return n * silnia(n - 1)
(Pdb) p n
2
(Pdb) c
24
```

Polecenie `w` wypisuje ten sam stos, który VSC pokazuje w panelu Call Stack — znak `>` oznacza ramkę bieżącą — a `u` i `d` (ang. *down*) przechodzą między ramkami, jak kliknięcie ramki w panelu. Pozostałe podstawowe polecenia to `n` (ang. *next*, odpowiednik Step Over), `s` (ang. *step*, Step Into), `l` (ang. *list*, wypisanie kodu wokół bieżącego wiersza), `q` (ang. *quit*, przerwanie programu — pdb uruchomiony przez `breakpoint()` prosi w Pythonie 3.14 o potwierdzenie pytaniem `Quitting pdb will kill the process. Quit anyway? [y/n]`) i `h` (ang. *help*, lista poleceń). Wywołanie `breakpoint()` nie powinno trafić do wersji oddawanej użytkownikom; zmienna środowiskowa `PYTHONBREAKPOINT=0` wyłącza wszystkie takie wywołania bez zmiany kodu, co chroni przed zapomnianą pułapką. Pdb przydaje się tam, gdzie nie ma VSC — na serwerze, w terminalu zdalnym — i do szybkiego sprawdzenia stanu programu bez konfigurowania czegokolwiek; do dłuższej pracy wygodniejszy jest debugger graficzny.

!!! note "Nowości Pythona 3.14"
    Python 3.14 pozwala podłączyć debugger do już działającego procesu bez
    jego zatrzymywania i ponownego uruchamiania: polecenie `python -m pdb -p PID`
    łączy się z procesem o podanym identyfikatorze, a funkcja `sys.remote_exec()`
    wykonuje w nim wskazany plik ze skryptem. Mechanizm ten, opisany w PEP 768, jest
    przeznaczony dla narzędzi diagnostycznych i długo działających programów;
    w książce z niego nie korzystamy.

Ślad wywołań, debugger i `traceback.print_exc()` pomagają zrozumieć błąd, który już wystąpił. W ostatnim podrozdziale rozdziału zajmujemy się rejestrowaniem tego, co program robi na bieżąco — tak, by po błędzie zgłoszonym przez użytkownika dało się odtworzyć, co działo się wcześniej.
