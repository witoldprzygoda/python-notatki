# Argumenty wiersza poleceń

Program z poprzedniego podrozdziału miał dane wpisane na stałe w funkcji `main()`. Dotychczas jedynym sposobem przekazania programowi danych z zewnątrz była funkcja `input()` z rozdziału [2. Konsola](../02-konsola/konsola-w-praktyce.md#funkcja-input-wczytywanie-danych), która wymaga dialogu w trakcie działania. Programy uruchamiane z terminala przyjmują dane inaczej — jako **argumenty wiersza poleceń** (ang. *command-line arguments*) podane za nazwą pliku lub modułu, tak jak `2026 9` za `python -m calendar`. W tym podrozdziale najpierw zobaczymy, czym te argumenty są w programie, potem poznamy narzędzie, które je porządkuje, a na końcu — jak program informuje powłokę o wyniku swojego działania.

## Lista `sys.argv`

Nazwa skryptu i wszystko, co wpisano w wierszu poleceń za nią, trafia do listy `sys.argv` modułu `sys`; opcje samego interpretera, podawane przed nazwą skryptu, do listy nie należą:

```python title="argumenty.py"
"""Wypisuje argumenty wiersza poleceń."""

import sys

print(sys.argv)
print(len(sys.argv))
```

```powershell title="Terminal"
python argumenty.py Ola 3
python argumenty.py
python argumenty.py "Anna Maria" 3
```

```{ .text .no-copy }
['argumenty.py', 'Ola', '3']
3
['argumenty.py']
1
['argumenty.py', 'Anna Maria', '3']
3
```

Lista `sys.argv` zawiera wyłącznie łańcuchy znaków: `3` jest tu tekstem `'3'`, nie liczbą, a argument ze spacją trzeba ująć w cudzysłowy, bo wiersz poleceń jest dzielony na słowa według spacji, zanim trafi do programu — robi to powłoka systemowa (PowerShell albo bash), w której wydajemy polecenie. Pierwszy element, `sys.argv[0]`, to nazwa skryptu; dokumentacja zastrzega, że jej postać zależy od systemu operacyjnego, a w CPythonie na Windows jest to zapis z polecenia: po uruchomieniu `python projekt\argumenty.py` będzie to `'projekt\\argumenty.py'`. Przy opcji `-c` pierwszym elementem jest łańcuch `'-c'`, przy opcji `-m` pełna ścieżka do pliku modułu, a w konsoli interaktywnej łańcuch pusty. Argumenty właściwe zaczynają się więc od `sys.argv[1]`. Nie należy mylić ich z argumentami funkcji z sekcji [Parametr a argument](../06-funkcje/argumenty-i-parametry.md#parametr-a-argument) rozdziału 6: argument wiersza poleceń to słowo przekazane programowi przez powłokę, które program dopiero interpretuje.

## Ręczna obsługa argumentów i jej granice

Skoro `sys.argv` jest zwykłą listą, program może odczytać z niej dane bezpośrednio. Zapiszmy w układzie z poprzedniego podrozdziału — funkcje u góry, `main()` na dole, warunek uruchomienia modułu na końcu — nowy program `powitanie.py`, którego `main()` pobiera imię i liczbę powtórzeń z wiersza poleceń, a na `--help` odpowiada docstringiem modułu. Docstring jest wewnątrz pliku dostępny jako nazwa globalna `__doc__`, na tej samej zasadzie, na której w poprzednim podrozdziale odczytywaliśmy `__name__`:

```python title="powitanie.py"
"""Wypisuje powitanie zadaną liczbę razy.

Użycie: python powitanie.py IMIE [LICZBA]
"""

import sys


def powitaj(imie, liczba):
    """Wypisuje powitanie dla imienia podaną liczbę razy."""
    for _ in range(liczba):
        print("Witaj,", imie)


def main():
    """Odczytuje argumenty wiersza poleceń i wypisuje powitanie."""
    if "--help" in sys.argv:
        print(__doc__)
        return
    imie = sys.argv[1]
    liczba = 1
    if len(sys.argv) > 2:
        liczba = int(sys.argv[2])
    powitaj(imie, liczba)


if __name__ == "__main__":
    main()
```

```powershell title="Terminal"
python powitanie.py Ola
python powitanie.py Ola 2
python powitanie.py --help
```

```{ .text .no-copy }
Witaj, Ola
Witaj, Ola
Witaj, Ola
Wypisuje powitanie zadaną liczbę razy.

Użycie: python powitanie.py IMIE [LICZBA]

```

W tekście pomocy przyjęliśmy zapis spotykany w dokumentacji poleceń: wielkie litery oznaczają wartość do podstawienia, a nawiasy kwadratowe — element nieobowiązkowy. Liczbę powtórzeń trzeba przekształcić funkcją `int()`, bo elementy listy są łańcuchami znaków; konwersja tekstu, który liczbą nie jest, kończy się `ValueError`, jak zapowiadał podrozdział [Konwersje i adnotacje typów](../03-nazwy-typy/konwersje-i-adnotacje.md#rzutowanie-jawna-konwersja). Program działa, dopóki użytkownik podaje argumenty poprawnie. Wystarczy pominąć imię albo podać zamiast liczby dowolny inny tekst, a program kończy się śladem wywołań:

```powershell title="Terminal"
python powitanie.py
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "powitanie.py", line 28, in <module>
    main()
    ~~~~^^
  File "powitanie.py", line 20, in main
    imie = sys.argv[1]
           ~~~~~~~~^^^
IndexError: list index out of range
```

```powershell title="Terminal"
python powitanie.py Ola abc
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "powitanie.py", line 28, in <module>
    main()
    ~~~~^^
  File "powitanie.py", line 23, in main
    liczba = int(sys.argv[2])
ValueError: invalid literal for int() with base 10: 'abc'
```

Brak elementu w liście zgłasza `IndexError`, a nieudana konwersja — `ValueError`; obsługę wyjątków omawia podrozdział [Obsługa wyjątków](../08-wyjatki/obsluga-wyjatkow.md). Nawet z obsługą wyjątków ręczne podejście ma jednak ograniczenia, które z każdym kolejnym argumentem stają się dotkliwsze: kolejność argumentów jest sztywna, opcję w rodzaju `--liczba 2` trzeba by samodzielnie odszukać w liście i usunąć, każdą pomyłkę użytkownika trzeba wykryć i opisać własnym komunikatem, a tekst pomocy w docstringu trzeba ręcznie utrzymywać w zgodzie z kodem. Wersja z `--help` jest demonstracją tych ograniczeń, nie wzorcem do naśladowania.

## Moduł `argparse`

Biblioteka standardowa zawiera moduł `argparse`, który przejmuje całą tę pracę: opisujemy, jakich argumentów program oczekuje, a moduł sam je rozpoznaje, konwertuje, sprawdza, generuje tekst pomocy i zgłasza błędy użycia.

### Parser, argument pozycyjny i opcja

Opis argumentów gromadzi obiekt **parsera** (ang. *parser*), tworzony przez `argparse.ArgumentParser()`. Metoda `add_argument()` dodaje do niego opis kolejnego argumentu wiersza poleceń, a `parse_args()` przetwarza wiersz poleceń według tego opisu:

```python title="przestrzen.py"
import argparse

parser = argparse.ArgumentParser(prog="powitanie")
parser.add_argument("imie")
parser.add_argument("-n", "--liczba", type=int, default=1)

print(parser.parse_args(["Ola", "-n", "2"]))
print(parser.parse_args(["Ola"]))
```

```{ .text .no-copy }
Namespace(imie='Ola', liczba=2)
Namespace(imie='Ola', liczba=1)
```

Parser rozróżnia dwa rodzaje argumentów. **Argument pozycyjny parsera**, jak `imie`, rozpoznawany jest po miejscu w wierszu poleceń i jest wymagany. **Opcja wiersza poleceń**, jak `-n`/`--liczba`, rozpoznawana jest po nazwie zaczynającej się od znaku `-` (jednego w postaci krótkiej, dwóch w długiej), może wystąpić w dowolnym miejscu i jest domyślnie nieobowiązkowa — jeśli jej nie podano, obowiązuje wartość `default`. Parametr `type=int` sprawia, że wartość opcji jest przekształcana na liczbę całkowitą. Opcja przypomina argument nazwany funkcji z sekcji [Parametr a argument](../06-funkcje/argumenty-i-parametry.md#parametr-a-argument) rozdziału 6, ale jest czym innym: to słowo w wierszu poleceń, które parser dopiero tłumaczy na wartość w programie.

Wynikiem `parse_args()` jest obiekt `Namespace` — prosty obiekt, którego atrybuty odpowiadają argumentom parsera; nazwa atrybutu pochodzi od nazwy argumentu (dla `--liczba` jest to `liczba`). W przykładzie przekazaliśmy `parse_args()` listę, by w jednym skrypcie pokazać dwa różne wywołania; w programie wywołujemy tę metodę bez listy, a parser przetwarza wtedy `sys.argv[1:]`. Nazwa `prog` podana parserowi pojawi się w tekstach pomocy i błędów — do czego wracamy w następnej sekcji. Program powitalny z parserem wygląda następująco:

```python title="powitanie.py"
"""Wypisuje powitanie zadaną liczbę razy."""

import argparse


def powitaj(imie, liczba):
    """Wypisuje powitanie dla imienia podaną liczbę razy."""
    for _ in range(liczba):
        print("Witaj,", imie)


def main():
    """Buduje parser, odczytuje argumenty i wypisuje powitanie."""
    parser = argparse.ArgumentParser(
        prog="powitanie",
        description="Wypisuje powitanie zadaną liczbę razy.",
    )
    parser.add_argument("imie", help="imię osoby do powitania")
    parser.add_argument("-n", "--liczba", type=int, default=1, help="liczba powtórzeń")
    argumenty = parser.parse_args()
    powitaj(argumenty.imie, argumenty.liczba)


if __name__ == "__main__":
    main()
```

```powershell title="Terminal"
python powitanie.py Ola
python powitanie.py Ola -n 2
python powitanie.py --liczba 2 Ola
```

```{ .text .no-copy }
Witaj, Ola
Witaj, Ola
Witaj, Ola
Witaj, Ola
Witaj, Ola
```

Opcja działa w obu postaciach — krótkiej `-n` i długiej `--liczba` — i w dowolnym miejscu wiersza poleceń. Parametry `description` i `help` nie wpływają na działanie programu; służą tekstowi pomocy. Wywołanie `ArgumentParser(...)` rozbiliśmy na kilka wierszy: wewnątrz nawiasów wiersz można łamać dowolnie, a przecinek po ostatnim argumencie jest dozwolony i ułatwia dopisywanie kolejnych.

### Automatyczna pomoc i komunikaty błędów

Parser sam dodaje opcję `-h`/`--help`, po której wypisuje tekst pomocy złożony z podanych opisów i kończy program kodem `0`, nie wykonując dalszej części `main()`:

```powershell title="Terminal"
python powitanie.py --help
```

```{ .text .no-copy }
usage: powitanie [-h] [-n LICZBA] imie

Wypisuje powitanie zadaną liczbę razy.

positional arguments:
  imie                 imię osoby do powitania

options:
  -h, --help           show this help message and exit
  -n, --liczba LICZBA  liczba powtórzeń
```

Wiersz `usage:` zaczyna się od nazwy podanej w `prog`; nawiasy kwadratowe oznaczają, jak w naszym docstringu, elementy nieobowiązkowe. Układ tekstu pomocy zależy od wersji interpretera — powyższy pochodzi z Pythona 3.14. Gdy użytkownik pomyli się w wywołaniu, parser wypisuje wiersz `usage:` i komunikat błędu (na osobny strumień błędów, ang. *standard error*, omówiony w podrozdziale [Funkcja print i strumienie](../09-wejscie-wyjscie/print-i-strumienie.md#strumienie-standardowe) rozdziału 9), a następnie kończy program — bez śladu wywołań i bez wykonywania `main()` do końca:

```powershell title="Terminal"
python powitanie.py
python powitanie.py Ola -n abc
python powitanie.py Ola --xyz
```

```{ .text .no-copy }
usage: powitanie [-h] [-n LICZBA] imie
powitanie: error: the following arguments are required: imie
usage: powitanie [-h] [-n LICZBA] imie
powitanie: error: argument -n/--liczba: invalid int value: 'abc'
usage: powitanie [-h] [-n LICZBA] imie
powitanie: error: unrecognized arguments: --xyz
```

Trzy sytuacje, które w wersji ręcznej kończyły się śladem wywołań, tu mają jednolite, zrozumiałe komunikaty. Długą nazwę opcji można skracać, dopóki skrót jest jednoznaczny — `--licz 2` działa jak `--liczba 2`. Więcej możliwości modułu — wybór spośród dozwolonych wartości, argumenty wielokrotne, podpolecenia — opisuje [samouczek argparse](https://docs.python.org/3/howto/argparse.html) w dokumentacji; w tej książce pozostajemy przy jednym argumencie pozycyjnym i jednej opcji.

!!! note "Nowości Pythona 3.14"
    W wersji 3.14 `argparse` koloruje tekst pomocy oraz wiersz `usage:`
    poprzedzający komunikat błędu, gdy wyjście jest terminalem obsługującym
    kolory; treść pozostaje taka sama, a kolorowanie wyłącza parametr
    `color=False` parsera albo zmienne środowiskowe, na przykład `NO_COLOR`.
    Parametr `suggest_on_error=True` włącza podpowiedzi przy błędnej wartości
    argumentu z listą dozwolonych wartości (`choices`) i przy błędnej nazwie
    podpolecenia — komunikat kończy się wtedy fragmentem w rodzaju
    `maybe you meant 'polski'?`; nie dotyczy on literówek w nazwach opcji,
    które nadal kończą się komunikatem `unrecognized arguments`. Zmieniła się
    też domyślna nazwa programu: bez `prog=` wiersz `usage:` odzwierciedla
    sposób uruchomienia — `powitanie.py` dla `python powitanie.py`, ale nazwa
    pliku interpretera z opcją `-m` (na Windows `python.exe -m powitanie`) dla
    `python -m powitanie`. Dlatego w przykładach ustawiamy `prog` jawnie.

## Kody wyjścia i funkcja `sys.exit()`

Program, który wypisał komunikat błędu i się zakończył, przekazał powłoce jeszcze jedną informację. Każdy uruchomiony program — w terminologii systemu operacyjnego: proces — kończy się liczbą całkowitą, **kodem wyjścia** (ang. *exit code*), którą powłoka i inne programy mogą odczytać, by ustalić, czy zadanie się powiodło. Umownie kod `0` oznacza powodzenie, a wartość niezerowa sygnalizuje problem; znaczenie poszczególnych wartości niezerowych ustala program.

Dotychczasowe programy kończyły się kodem `0`, gdy wykonały się do końca, a kodem `1`, gdy przerwał je **nieprzechwycony wyjątek**, czyli wyjątek, którego program nie obsłużył — na razie każdy, jak `IndexError` i `ValueError` wyżej; tak kończy program interpreter CPython, natomiast przerwanie klawiszami ++ctrl+c++ kończy go innym kodem, zależnym od systemu. Parser `argparse` po błędzie użycia kończy program kodem `2`. Kod można ustalić samodzielnie funkcją `sys.exit()`, która przerywa wykonywanie programu i ustala jego kod wyjścia:

```python title="koniec.py"
import sys

print("przed")
sys.exit(1)
print("po")
```

```{ .text .no-copy }
przed
```

Instrukcja `print("po")` nie została wykonana, a program zakończył się kodem `1`. Wywołanie `sys.exit(0)` kończy program z kodem `0`, a `sys.exit()` bez argumentu — również z kodem `0`, tak jak `sys.exit(None)`. Mechanizm, którym `sys.exit()` przerywa program — wyjątek `SystemExit` — opisuje sekcja [Hierarchia wyjątków](../08-wyjatki/zglaszanie-wyjatkow.md#hierarchia-wyjatkow); na razie wystarczy jego skutek.

Kod wyjścia łączy się naturalnie z konwencją `main()`: funkcja zwraca kod, a warunek uruchomienia modułu przekazuje go do `sys.exit()`. Dodajmy do programu sprawdzenie, którego parser w użytym tu zakresie nie wykona — liczba powtórzeń musi być dodatnia:

```python title="powitanie.py"
"""Wypisuje powitanie zadaną liczbę razy."""

import argparse
import sys


def powitaj(imie, liczba):
    """Wypisuje powitanie dla imienia podaną liczbę razy."""
    for _ in range(liczba):
        print("Witaj,", imie)


def main():
    """Buduje parser, sprawdza argumenty i wypisuje powitanie."""
    parser = argparse.ArgumentParser(
        prog="powitanie",
        description="Wypisuje powitanie zadaną liczbę razy.",
    )
    parser.add_argument("imie", help="imię osoby do powitania")
    parser.add_argument("-n", "--liczba", type=int, default=1, help="liczba powtórzeń")
    argumenty = parser.parse_args()
    if argumenty.liczba < 1:
        print("Liczba powtórzeń musi być dodatnia.")
        return 1
    powitaj(argumenty.imie, argumenty.liczba)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

```powershell title="Terminal"
python powitanie.py Ola -n 0
```

```{ .text .no-copy }
Liczba powtórzeń musi być dodatnia.
```

Program wypisał komunikat i zakończył się kodem `1`; poprawne wywołanie kończy się kodem `0`. Zapis `sys.exit(main())` jest tym brakującym elementem idiomatycznego układu pliku z poprzedniego podrozdziału. Funkcja `main()` pozostaje zwykłą funkcją zwracającą liczbę, a decyzja o zakończeniu procesu zapada dopiero w bloku warunku uruchomienia modułu. Funkcja `main()` bez instrukcji `return`, jak w poprzednim podrozdziale, zwraca `None`, więc `sys.exit(main())` kończy wtedy program kodem `0`.

| Zakończenie programu | Kod wyjścia |
|---|---|
| wykonanie do końca, `sys.exit()`, `sys.exit(0)`, `main()` zwracające `0` lub `None`, pomoc po `--help` | `0` |
| nieprzechwycony wyjątek (ślad wywołań) | `1` |
| `sys.exit(1)`, `main()` zwracające `1` | `1` |
| błąd użycia zgłoszony przez `argparse` | `2` |

!!! note "Odczyt kodu wyjścia"
    Kod ostatniego polecenia przechowuje w powłoce PowerShell zmienna
    `$LASTEXITCODE`, a w powłokach uniksowych `$?`; wypisuje go odpowiednio
    `echo $LASTEXITCODE` i `echo $?`. Z kodów korzystają przede wszystkim
    skrypty powłoki i narzędzia automatyzujące, które na ich podstawie
    decydują o dalszych krokach.

Program powitalny ma teraz podstawowe cechy programu narzędziowego: przyjmuje dane z wiersza poleceń, sam objaśnia użycie, zgłasza błędy zrozumiałymi komunikatami i informuje powłokę o wyniku. Gdy programów i modułów przybywa, jeden katalog przestaje wystarczać — następny podrozdział pokazuje, jak grupować moduły w pakiety.
