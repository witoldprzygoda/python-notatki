# Funkcja print i strumienie

Funkcję `print()` poznaliśmy w podrozdziale [Konsola w praktyce](../02-konsola/konsola-w-praktyce.md#funkcja-print-pierwsze-eksperymenty) rozdziału 2 wraz z argumentami `sep` i `end`, a w rozdziale 8 dowiedzieliśmy się, że ślady wywołań i dziennik trafiają na inny strumień niż wyniki programu. W tym podrozdziale składamy te wątki w całość: pełna sygnatura `print()`, znaki sterujące, trzy strumienie standardowe i ich przekierowania w PowerShell, buforowanie, kierowanie wyjścia do pliku oraz zachowanie `input()`, gdy wejście się kończy. Wszystko to jest podstawą dla animacji w następnym podrozdziale i dla plików w dalszych.

## Pełna sygnatura `print()`

```{ .text .no-copy }
print(*objects, sep=" ", end="\n", file=None, flush=False)
```

Parametr `*objects` z podrozdziału [Argumenty i parametry](../06-funkcje/argumenty-i-parametry.md#parametr-args) zbiera dowolną liczbę argumentów pozycyjnych; każdy jest zamieniany na tekst tak, jak robi to `str()`. Cztery pozostałe parametry są tylko nazwane: `sep` rozdziela argumenty, `end` kończy wypisany tekst, `file` wskazuje strumień docelowy (domyślnie standardowe wyjście), a `flush` wymusza natychmiastowe opróżnienie bufora strumienia. Wywołanie bez argumentów wypisuje sam `end`, czyli pusty wiersz:

```python title="sygnatura.py"
print("a", "b", "c")
print("a", "b", "c", sep="")
print("a", "b", "c", sep=" | ")
print("bez nowego wiersza", end="")
print(" — ciąg dalszy")
print()
print(1, 2.5, None, [1, 2], sep=", ")
```

```{ .text .no-copy }
a b c
abc
a | b | c
bez nowego wiersza — ciąg dalszy

1, 2.5, None, [1, 2]
```

## Znaki sterujące w `sep` i `end`

Argumenty `sep` i `end` przyjmują dowolne łańcuchy, także zawierające **znaki sterujące** (ang. *control characters*) — sekwencje ucieczki z podrozdziału [Typy proste](../03-nazwy-typy/typy-proste.md#typ-str), które terminal interpretuje jako polecenia zamiast wypisywać: `\n` przechodzi do nowego wiersza, `\t` przesuwa kursor do następnej pozycji tabulacji (co osiem znaków), `\r` cofa kursor na początek bieżącego wiersza, `\b` cofa go o jeden znak, a `\a` wydaje sygnał dźwiękowy, o ile terminal go obsługuje. Tabulacja daje najprostsze kolumny:

```python title="tabulacja.py"
print("imię", "wiek", "miasto", sep="\t")
print("Ala", 30, "Kraków", sep="\t")
print("Bartłomiej", 25, "Gdańsk", sep="\t")
```

```{ .text .no-copy }
imię	wiek	miasto
Ala	30	Kraków
Bartłomiej	25	Gdańsk
```

Kolumny zbudowane tabulacją przestają być wyrównane, gdy tekst przekracza szerokość pozycji, jak `Bartłomiej` w trzecim wierszu — dlatego do tabel służy formatowanie z poprzedniego podrozdziału, a `\t` przydaje się do danych, które mają być rozdzielone tabulatorem, na przykład do wklejenia w arkuszu kalkulacyjnym. Znak `\r` pozwala nadpisać wiersz: wypisany tekst pozostaje na ekranie, ale kursor wraca na początek, więc następne `print()` zastępuje go od lewej:

```python title="powrot-karetki.py"
print("ładowanie 50%", end="\r")
print("ładowanie 100%")
```

W terminalu widzimy tylko `ładowanie 100%` — drugi napis całkowicie zakrył pierwszy; gdy nowy tekst jest krótszy od poprzedniego, końcówka starego pozostaje widoczna i trzeba ją nadpisać spacjami. Na tym mechanizmie opierają się animacje z następnego podrozdziału. Efekt znaków `\b` i `\a` zależy od terminala: Windows Terminal cofa kursor bez kasowania znaku, a dźwięk bywa wyłączony.

## Strumienie standardowe

Każdy program uruchomiony w terminalu ma trzy **strumienie standardowe** (ang. *standard streams*): **standardowe wejście** (ang. *standard input*, `stdin`), z którego czyta `input()`, **standardowe wyjście** (`stdout`), na które pisze `print()`, i **strumień błędów** (`stderr`), na który trafiają ślady wywołań, ostrzeżenia i dziennik `logging` — te dwa ostatnie poznaliśmy w podrozdziale [Obsługa wyjątków](../08-wyjatki/obsluga-wyjatkow.md#program-bez-obsugi-i-z-obsuga). W Pythonie są to obiekty `sys.stdin`, `sys.stdout` i `sys.stderr` — obiekty plików tekstowych, takie same jak te, które zwraca `open()` — i można je podać jako argument `file`:

```python title="strumienie.py"
import sys

print("suma: 42")
print("UWAGA: plik nie istnieje", file=sys.stderr)
print("koniec")
```

```{ .text .no-copy }
suma: 42
UWAGA: plik nie istnieje
koniec
```

W konsoli oba strumienie wyjściowe trafiają na ekran i wynik wygląda tak samo, jak przy trzech zwykłych `print()`. Różnica ujawnia się poza konsolą.

### Przekierowanie i potok w PowerShell

Powłoka może **przekierować** (ang. *redirect*) strumienie programu: `>` zapisuje standardowe wyjście do pliku (nadpisując go), `>>` dopisuje na końcu, a `2>` przekierowuje strumień błędów; wyjście nieprzekierowane nadal trafia na ekran:

```powershell title="Terminal"
python strumienie.py > wynik.txt
Get-Content wynik.txt
```

```{ .text .no-copy }
UWAGA: plik nie istnieje
suma: 42
koniec
```

Komunikat ostrzeżenia pojawił się na ekranie w trakcie pierwszego polecenia, a plik `wynik.txt` — wypisany poleceniem `Get-Content` — zawiera tylko dwa wiersze ze standardowego wyjścia. Przekierowanie `2> bledy.txt` działa odwrotnie: na ekranie zostają wyniki, a do pliku trafia ostrzeżenie. Dlatego komunikaty diagnostyczne piszemy na `stderr`: użytkownik, który zapisuje wynik programu do pliku, nie dostaje w nim ostrzeżeń, a ostrzeżenia nie są tracone. **Potok** (ang. *pipe*), zapisywany znakiem `|`, łączy standardowe wyjście jednego programu ze standardowym wejściem drugiego; ostrzeżenie, jako że idzie osobnym strumieniem, nie trafia do potoku:

```powershell title="Terminal"
python strumienie.py | python -c "import sys; print(len(sys.stdin.read().splitlines()), 'wierszy')"
```

```{ .text .no-copy }
UWAGA: plik nie istnieje
2 wierszy
```

Drugi program policzył wiersze, które otrzymał na standardowym wejściu (metoda `splitlines()` dzieli tekst na listę wierszy) — dwa, bo ostrzeżenie do potoku nie weszło. Ten sam zapis w Git Bash i w terminalach uniksowych działa identycznie; różnica dotyczy tylko sposobu wyświetlania pliku (`cat` zamiast `Get-Content`).

### Kodowanie strumieni — konsola a przekierowanie

Strumień tekstowy zamienia znaki na bajty według **kodowania** (ang. *encoding*), a kodowanie strumieni standardowych zależy od tego, dokąd prowadzą. W konsoli Windows Python zapisuje tekst przez interfejs konsoli w Unicode, więc polskie znaki wyświetlają się poprawnie niezależnie od ustawień systemu. Strumień przekierowany do pliku lub potoku jest natomiast kodowany **stroną kodową** (ang. *code page*) systemu — w polskim Windows zwykle cp1250, w angielskim cp1252 — która nie obejmuje wszystkich znaków Unicode:

```python title="polskie.py"
print("zażółć gęślą jaźń")
```

```powershell title="Terminal"
python polskie.py
python polskie.py > polskie.txt
```

```{ .text .no-copy }
zażółć gęślą jaźń
Traceback (most recent call last):
  File "C:\...\projekt\polskie.py", line 1, in <module>
    print("zażółć gęślą jaźń")
    ~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "C:\...\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u017c' in position 2: character maps to <undefined>
```

Na komputerze ze stroną kodową cp1252 (jak w tym przykładzie) litera `ż` nie ma odpowiednika i przekierowanie kończy się wyjątkiem `UnicodeEncodeError`; ze stroną cp1250 zapis się powiedzie, ale plik nie będzie w UTF-8 i program czytający go w UTF-8 zobaczy zniekształcone znaki. Rozwiązaniem jest **tryb UTF-8** interpretera, w którym strumienie standardowe i pliki otwierane bez podanego kodowania używają UTF-8: włącza go opcja `-X utf8` albo zmienna środowiskowa `PYTHONUTF8=1`, ustawiana w PowerShell na czas sesji poleceniem `$env:PYTHONUTF8 = "1"`:

```powershell title="Terminal"
python -X utf8 polskie.py > polskie.txt
Get-Content polskie.txt
```

```{ .text .no-copy }
zażółć gęślą jaźń
```

!!! note "Wersja PowerShell"
    Opisane zachowanie dotyczy PowerShell 7.4 i nowszego, gdzie przekierowanie `>` i potok `|` przekazują bajty dokładnie tak, jak wypisał je program. Wbudowany w system Windows PowerShell 5.1 oraz wersje 7.0–7.3 dekodują wyjście programu według ustawień konsoli i zapisują je ponownie we własnym kodowaniu, więc zawartość pliku może się różnić od pokazanej. Wersję powłoki sprawdzamy poleceniem `$PSVersionTable.PSVersion`.

Od Pythona 3.15 tryb UTF-8 ma być włączony domyślnie ([PEP 686](https://peps.python.org/pep-0686/)); w Pythonie 3.14 trzeba o nim pamiętać przy przekierowaniach — samo kodowanie strumieni standardowych, bez wpływu na pliki, ustala też zmienna środowiskowa `PYTHONIOENCODING` — a przy zapisie do plików z poziomu programu zawsze podawać kodowanie, o czym mowa w podrozdziale o plikach tekstowych.

## Buforowanie i argument `flush`

Tekst przekazany do `print()` nie zawsze trafia na ekran natychmiast. Strumień gromadzi go w **buforze** (ang. *buffer*) i przekazuje dalej porcjami, bo pojedyncze zapisy są kosztowne. Reguła zależy od miejsca docelowego: standardowe wyjście prowadzące do terminala jest **buforowane wierszowo** (ang. *line-buffered*) — tekst pojawia się przy każdym znaku nowego wiersza — a przekierowane do pliku lub potoku jest **buforowane blokowo** (ang. *block-buffered*) i opróżnia się dopiero po zapełnieniu bufora albo przy zakończeniu programu; strumień błędów jest buforowany wierszowo zawsze, dlatego komunikaty diagnostyczne docierają na czas. Wartość `sys.stdout.line_buffering` mówi, który tryb obowiązuje: `True` w terminalu, `False` po przekierowaniu. Program, który wypisuje postęp bez znaku nowego wiersza, w terminalu pokaże więc wszystkie liczby naraz, na końcu:

```python title="bufor.py"
import time

for i in range(5):
    print(i, end=" ")
    time.sleep(0.2)
print()

for i in range(5):
    print(i, end=" ", flush=True)
    time.sleep(0.2)
print()
```

```{ .text .no-copy }
0 1 2 3 4 
0 1 2 3 4 
```

Funkcja `time.sleep()` z modułu `time` wstrzymuje program na podaną liczbę sekund. Wynik obu pętli jest identyczny, ale w terminalu pierwsza wypisuje pięć liczb dopiero po sekundzie, jednocześnie, a druga — co 0,2 sekundy, jedną po drugiej, bo `flush=True` opróżnia bufor (ang. *flush*) po każdym wywołaniu. Ten sam efekt dla całego programu daje opcja interpretera `-u` (ang. *unbuffered*) albo zmienna środowiskowa `PYTHONUNBUFFERED` o dowolnej niepustej wartości. Zachowanie buforowania sprawdzamy, uruchamiając skrypt w terminalu: okno IDLE, panel OUTPUT w Visual Studio Code, do którego pisze rozszerzenie Code Runner z rozdziału 1 (uruchamia ono program z opcją `-u`), oraz przekierowanie do pliku dają inny obraz.

## Argument `file` — wyjście do pliku i `redirect_stdout()`

Argument `file` przyjmuje dowolny obiekt pliku tekstowego, więc `print()` może pisać do pliku otwartego funkcją `open()` z podrozdziału [Instrukcja with i menedżery kontekstu](../08-wyjatki/with-i-contextlib.md#instrukcja-with) — z tymi samymi `sep` i `end`, co na ekranie. Gdy do pliku ma trafić wyjście większego fragmentu kodu, który wywołuje `print()` bez argumentu `file`, używamy menedżera kontekstu `contextlib.redirect_stdout()`: na czas bloku podstawia on wskazany obiekt jako `sys.stdout`, a po bloku przywraca poprzedni:

```python title="do-pliku.py"
from contextlib import redirect_stdout

with open("raport.txt", "w", encoding="utf-8") as plik:
    print("Raport", file=plik)
    print("suma:", 42, file=plik)

with open("przechwycone.txt", "w", encoding="utf-8") as plik:
    with redirect_stdout(plik):
        print("to trafia do pliku")
        print("to również")
print("to trafia na konsolę")

for nazwa in ["raport.txt", "przechwycone.txt"]:
    with open(nazwa, encoding="utf-8") as plik:
        print(f"--- {nazwa}")
        print(plik.read(), end="")
```

```{ .text .no-copy }
to trafia na konsolę
--- raport.txt
Raport
suma: 42
--- przechwycone.txt
to trafia do pliku
to również
```

W starszym kodzie spotyka się ręczne przypisanie `sys.stdout = plik` i przywracanie `sys.stdout = sys.__stdout__`; `redirect_stdout()` robi to samo bezpiecznie, także gdy blok zgłosi wyjątek. Argument `file` nie wymaga zresztą prawdziwego pliku — wystarczy obiekt z metodą `write()`; taki obiekt, gromadzący tekst w pamięci, piszemy jako własną klasę w podrozdziale [Menedżery kontekstu i obiekty plikopodobne](../11-model-danych/menedzery-kontekstu.md#obiekt-plikopodobny-metoda-write) rozdziału 11, a gotowy — `io.StringIO` — poznamy przy plikach binarnych.

## Funkcja `input()` i koniec wejścia

Funkcja `input(zachęta)` wypisuje zachętę na standardowe wyjście bez znaku nowego wiersza, po czym czyta jeden wiersz ze standardowego wejścia i zwraca go bez końcowego `\n`. Gdy wejście się skończy — użytkownik nacisnął ++ctrl+z++ i ++enter++ w konsoli Windows (++ctrl+d++ w terminalach uniksowych) albo wyczerpał się plik podany potokiem — `input()` zgłasza `EOFError` (od skrótu EOF, ang. *end of file*), który obsługujemy jak każdy wyjątek:

```python title="wejscie.py"
suma = 0
while True:
    try:
        wiersz = input("liczba: ")
    except EOFError:
        break
    suma += int(wiersz)
print()
print("suma:", suma)
```

```text title="liczby.txt"
3
4
5
```

```powershell title="Terminal"
Get-Content liczby.txt | python wejscie.py
```

```{ .text .no-copy }
liczba: liczba: liczba: liczba: 
suma: 12
```

Program wczytał trzy liczby z pliku podanego potokiem i zakończył pętlę przy czwartym `input()`. Zachęty pojawiły się cztery razy w jednym wierszu: przy wejściu z potoku nikt nie wpisuje tekstu, więc nie ma echa ani znaków nowego wiersza, które w konsoli wprowadza użytkownik klawiszem ++enter++; stąd dodatkowe `print()` przed wynikiem. Zapis `Get-Content plik | program` jest w PowerShell odpowiednikiem uniksowego `program < plik`, które działa także w Git Bash. Program czytający wiersze z wejścia do wyczerpania można zapisać krócej — bez `input()` i bez zachęt — iterując po `sys.stdin` jak po pliku:

```python title="numeruj.py"
import sys

for numer, wiersz in enumerate(sys.stdin, start=1):
    print(f"{numer:3}: {wiersz}", end="")
```

```powershell title="Terminal"
Get-Content liczby.txt | python numeruj.py
```

```{ .text .no-copy }
  1: 3
  2: 4
  3: 5
```

Wiersz odczytany z `sys.stdin` zachowuje końcowy `\n`, dlatego `print()` otrzymał `end=""`. Taki program jest **filtrem** (ang. *filter*): przetwarza wejście na wyjście i daje się łączyć potokami z innymi programami. Oba sposoby czytania — `input()` w pętli z `EOFError` oraz iteracja po `sys.stdin` — opierają się na tym samym strumieniu; pierwszy jest właściwy dla dialogu z użytkownikiem, drugi dla danych podawanych z zewnątrz.
