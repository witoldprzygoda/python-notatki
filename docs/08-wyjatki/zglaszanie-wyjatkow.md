# Zgłaszanie wyjątków

W poprzednim podrozdziale wyjątki zgłaszał interpreter i funkcje wbudowane, a my je przechwytywaliśmy. Własne funkcje sygnalizowały dotąd błędne argumenty inaczej: `silnia_bezpieczna()` z podrozdziału [Rekurencja](../06-funkcje/rekurencja.md#przypadek-bazowy-i-krok-rekurencyjny) zwracała `None`, co nazwaliśmy rozwiązaniem tymczasowym. Wartość `None` łatwo przeoczyć — wywołujący może jej nie sprawdzić i przekazać dalej — a informacja o przyczynie błędu ginie. Instrukcja `raise` oddaje własnym funkcjom ten sam mechanizm, którym posługuje się `int()`: funkcja zgłasza wyjątek z komunikatem, a wywołujący musi go obsłużyć albo program się zatrzyma. W tym podrozdziale poznajemy `raise`, hierarchię typów wyjątków, ponowne zgłaszanie i łączenie wyjątków w łańcuchy oraz miejsce instrukcji `assert` wobec wyjątków; na koniec piszemy funkcję z pełną walidacją argumentów.

## Instrukcja `raise`

Instrukcja `raise` przyjmuje obiekt wyjątku i zgłasza go w miejscu, w którym stoi. Obiekt tworzymy, wywołując typ wyjątku jak funkcję, z komunikatem jako argumentem — tak jak `int("12")` tworzy liczbę, `ValueError("opis")` tworzy wyjątek:

```python title="silnia-raise.py"
def silnia(n):
    """Zwraca n! dla nieujemnej liczby całkowitej n."""
    if not isinstance(n, int):
        raise TypeError(f"n musi być liczbą całkowitą, otrzymano {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n musi być nieujemne, otrzymano {n}")
    wynik = 1
    for k in range(2, n + 1):
        wynik *= k
    return wynik


print(silnia(5))
print(silnia(-3))
```

```{ .text .no-copy }
120
Traceback (most recent call last):
  File "silnia-raise.py", line 14, in <module>
    print(silnia(-3))
          ~~~~~~^^^^
  File "silnia-raise.py", line 6, in silnia
    raise ValueError(f"n musi być nieujemne, otrzymano {n}")
ValueError: n musi być nieujemne, otrzymano -3
```

Funkcja sprawdza argument, zanim zacznie liczyć, i dla argumentu niewłaściwego kończy się wyjątkiem, nie wynikiem. Wybór typu wynika z tabeli z poprzedniego podrozdziału: `TypeError` dla argumentu niewłaściwego typu, `ValueError` dla właściwego typu o niewłaściwej wartości — te same reguły stosują funkcje wbudowane, więc kod obsługujący `silnia()` może traktować ją tak jak `int()`. Komunikat powinien mówić, co było wymagane i co otrzymano; wartość wstawiamy w komunikat, bo w chwili czytania śladu nie ma już dostępu do argumentów. Ślad wywołań wskazuje wiersz z `raise` jako miejsce zgłoszenia — dla czytelnika śladu wyjątek zgłoszony instrukcją `raise` niczym nie różni się od wyjątku zgłoszonego przez `int()`. Dopuszczalny jest też zapis `raise ValueError` bez nawiasów: interpreter tworzy wtedy obiekt wyjątku bez komunikatu; w książce podajemy komunikat zawsze. Instrukcja `raise`, jak każda instrukcja, nie może wystąpić w wyrażeniu lambda z rozdziału 6, które dopuszcza wyłącznie wyrażenia.

W porównaniu ze zwracaniem `None` zmienia się jedno: wywołujący nie może błędu przeoczyć. Wyrażenie `silnia(-3) + 1` z wersją zwracającą `None` skończyłoby się `TypeError` przy dodawaniu, daleko od przyczyny; z `raise` program zatrzymuje się w funkcji, która błąd wykryła, z komunikatem opisującym przyczynę.

### Propagacja przez stos wywołań

Wyjątek zgłoszony w funkcji wędruje przez kolejne wywołania — ramki stosu, które poznaliśmy w podrozdziale [Rekurencja](../06-funkcje/rekurencja.md#limit-rekurencji) — aż natrafi na pasującą klauzulę `except` albo opuści kod modułu. Każda ramka, przez którą przeszedł, pojawia się w śladzie:

```python title="propagacja.py"
def silnia(n):
    """Zwraca n! dla nieujemnej liczby całkowitej n."""
    if not isinstance(n, int):
        raise TypeError(f"n musi być liczbą całkowitą, otrzymano {type(n).__name__}")
    if n < 0:
        raise ValueError(f"n musi być nieujemne, otrzymano {n}")
    wynik = 1
    for k in range(2, n + 1):
        wynik *= k
    return wynik


def srednia_silni(dane):
    """Zwraca średnią silni liczb z listy."""
    silnie = [silnia(n) for n in dane]
    return sum(silnie) / len(silnie)


def main():
    print(srednia_silni([1, 2, 3]))
    print(srednia_silni([1, -2, 3]))


main()
```

```{ .text .no-copy }
3.0
Traceback (most recent call last):
  File "propagacja.py", line 24, in <module>
    main()
    ~~~~^^
  File "propagacja.py", line 21, in main
    print(srednia_silni([1, -2, 3]))
          ~~~~~~~~~~~~~^^^^^^^^^^^^
  File "propagacja.py", line 15, in srednia_silni
    silnie = [silnia(n) for n in dane]
              ~~~~~~^^^
  File "propagacja.py", line 6, in silnia
    raise ValueError(f"n musi być nieujemne, otrzymano {n}")
ValueError: n musi być nieujemne, otrzymano -2
```

Funkcja `silnia()` jest tu bez zmian. Cztery ramki odpowiadają czterem aktywnym wywołaniom w chwili zgłoszenia. Ani `srednia_silni()`, ani `main()` nie zawierają instrukcji `try`, więc wyjątek przeszedł przez nie bez zatrzymania, przerywając każdą z nich. Obsługę można umieścić na dowolnym poziomie: gdyby `main()` objęła drugie wywołanie instrukcją `try` z klauzulą `except ValueError`, program wypisałby komunikat i działał dalej, a `silnia()` i `srednia_silni()` pozostałyby bez zmian. Obowiązuje zasada z poprzedniego podrozdziału: zgłasza `silnia()`, która wykryła problem, a obsługuje kod, który wie, co z nim zrobić — zwykle kod najbliższy użytkownikowi.

## Hierarchia wyjątków

Typy wyjątków tworzą drzewo: każdy typ jest odmianą typu ogólniejszego, a klauzula `except` z typem ogólniejszym przechwytuje także wyjątki wszystkich typów pod nim. Skrócone drzewo z typami, które spotykamy w książce, wygląda tak (pełne drzewo, z kilkudziesięcioma typami, zawiera dokumentacja *Built-in Exceptions* w sekcji [*Exception hierarchy*](https://docs.python.org/3/library/exceptions.html#exception-hierarchy)):

```{ .text .no-copy }
BaseException
 ├── BaseExceptionGroup
 ├── SystemExit
 ├── KeyboardInterrupt
 ├── GeneratorExit
 └── Exception
      ├── ArithmeticError
      │    └── ZeroDivisionError
      ├── AssertionError
      ├── AttributeError
      ├── ExceptionGroup [BaseExceptionGroup]
      ├── ImportError
      │    └── ModuleNotFoundError
      ├── LookupError
      │    ├── IndexError
      │    └── KeyError
      ├── NameError
      ├── OSError
      │    ├── FileNotFoundError
      │    └── PermissionError
      ├── RuntimeError
      │    └── RecursionError
      ├── StopIteration
      ├── SyntaxError
      ├── TypeError
      ├── ValueError
      └── Warning
```

Mechanizm, który buduje takie drzewo — typ pochodny przejmujący cechy typu bazowego — nazywa się dziedziczeniem; poznamy go w rozdziale o klasach, a tu wystarczy czytać drzewo od góry: `KeyError` jest odmianą `LookupError`, `LookupError` odmianą `Exception`, `Exception` odmianą `BaseException`. <!-- TODO: link po powstaniu rozdziału o klasach --> Klauzula `except LookupError` obsługuje więc zarówno brak klucza, jak i indeks poza zakresem:

```python title="lookup.py"
zapisy = {"ala": [90, 85]}


def ocena(imie, numer):
    """Zwraca ocenę o podanym numerze dla podanej osoby."""
    return zapisy[imie][numer]


for imie, numer in [("ala", 0), ("ola", 0), ("ala", 5)]:
    try:
        print(ocena(imie, numer))
    except LookupError as e:
        print("brak danych:", type(e).__name__, e)
```

```{ .text .no-copy }
90
brak danych: KeyError 'ola'
brak danych: IndexError list index out of range
```

Korzeniem drzewa jest `BaseException`, ale niemal wszystkie wyjątki, które program obsługuje, leżą pod `Exception`. Trzy z typów umieszczonych bezpośrednio pod korzeniem leżą poza `Exception` celowo, bo nie sygnalizują błędu, lecz żądanie zakończenia: `SystemExit` zgłasza funkcja `sys.exit()` z podrozdziału [Argumenty wiersza poleceń](../07-moduly/argumenty-wiersza-polecen.md#kody-wyjscia-i-funkcja-sysexit) — tak właśnie przerywa ona program, a kod wyjścia jest argumentem tego wyjątku; `KeyboardInterrupt` zgłasza interpreter po naciśnięciu ++ctrl+c++; `GeneratorExit` służy do zamykania generatorów. Klauzula `except Exception` żadnego z nich nie przechwytuje, co jest zachowaniem pożądanym:

```python title="wyjscie.py"
import sys

try:
    sys.exit(3)
except Exception:
    print("przechwycone przez Exception")
except SystemExit as e:
    print("kod wyjścia:", e.code)
print("program działa dalej")
```

```{ .text .no-copy }
kod wyjścia: 3
program działa dalej
```

Druga klauzula służy tu wyłącznie demonstracji — w programach nie przechwytujemy `SystemExit` ani `KeyboardInterrupt`, bo użytkownik, który nacisnął ++ctrl+c++, oczekuje, że program się zatrzyma. Z tego samego powodu klauzula `except` bez typu, przechwytująca wszystko włącznie z tymi wyjątkami, jest błędem, do którego wracamy w następnym podrozdziale. Gałąź `Warning` grupuje ostrzeżenia, jak `SyntaxWarning` z poprzedniego podrozdziału; są one wyjątkami, ale domyślnie interpreter je wypisuje, zamiast zgłaszać. Czwarty typ pod korzeniem, `BaseExceptionGroup`, wraz z odmianą `ExceptionGroup` (należącą zarazem do gałęzi `Exception`, co dokumentacja oznacza nawiasem kwadratowym) służy do zgłaszania wielu wyjątków naraz — wracamy do niego w następnym podrozdziale.

## Ponowne zgłoszenie i łańcuchy wyjątków

Przechwycenie wyjątku nie musi oznaczać zakończenia jego obsługi. Klauzula `except` może wykonać swoją część — wypisać komunikat, zanotować zdarzenie — i przekazać wyjątek dalej instrukcją `raise` bez argumentu, która zgłasza ponownie ten sam obiekt:

```python title="ponowne.py"
def wczytaj_liczby(teksty):
    """Zwraca listę liczb całkowitych z listy łańcuchów."""
    liczby = []
    for tekst in teksty:
        try:
            liczby.append(int(tekst))
        except ValueError:
            print(f"błędna wartość {tekst!r} w danych")
            raise
    return liczby


print(wczytaj_liczby(["1", "2"]))
print(wczytaj_liczby(["1", "x"]))
```

```{ .text .no-copy }
[1, 2]
błędna wartość 'x' w danych
Traceback (most recent call last):
  File "ponowne.py", line 14, in <module>
    print(wczytaj_liczby(["1", "x"]))
          ~~~~~~~~~~~~~~^^^^^^^^^^^^
  File "ponowne.py", line 6, in wczytaj_liczby
    liczby.append(int(tekst))
                  ~~~^^^^^^^
ValueError: invalid literal for int() with base 10: 'x'
```

Ślad wskazuje pierwotne miejsce zgłoszenia — wywołanie `int()` w wierszu 6, nie wiersz z `raise` — bo ponownie zgłoszony został ten sam obiekt wraz z zapisaną w nim drogą propagacji. Funkcja zdążyła wypisać komunikat, ale decyzję o obsłudze pozostawiła wywołującemu.

Częściej niż ten sam wyjątek chcemy zgłosić inny, lepiej opisujący sytuację z punktu widzenia wywołującego, nie tracąc informacji o przyczynie. Służy do tego forma `raise nowy from e`, która wiąże nowy wyjątek z pierwotnym:

```python title="lancuch.py"
def wczytaj_wiek(tekst):
    """Zwraca wiek jako liczbę całkowitą z łańcucha."""
    try:
        return int(tekst)
    except ValueError as e:
        raise ValueError(f"nieprawidłowy wiek: {tekst!r}") from e


print(wczytaj_wiek("42"))
print(wczytaj_wiek("dużo"))
```

```{ .text .no-copy }
42
Traceback (most recent call last):
  File "lancuch.py", line 4, in wczytaj_wiek
    return int(tekst)
ValueError: invalid literal for int() with base 10: 'dużo'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "lancuch.py", line 10, in <module>
    print(wczytaj_wiek("dużo"))
          ~~~~~~~~~~~~^^^^^^^^
  File "lancuch.py", line 6, in wczytaj_wiek
    raise ValueError(f"nieprawidłowy wiek: {tekst!r}") from e
ValueError: nieprawidłowy wiek: 'dużo'
```

Ślad składa się teraz z dwóch części rozdzielonych zdaniem *The above exception was the direct cause of the following exception*: najpierw wyjątek pierwotny, potem wyjątek zgłoszony przez nas. Jest to **łańcuch wyjątków** (ang. *exception chaining*) — czytelnik śladu widzi zarówno komunikat sformułowany w języku programu („nieprawidłowy wiek”), jak i techniczną przyczynę.

Łańcuch powstaje także bez `from`, gdy w trakcie obsługi jednego wyjątku zostanie zgłoszony drugi. Funkcja niżej próbuje w klauzuli `except` konwersji zapasowej — po usunięciu jednostki — która dla wpisu `"dużo"` również zawodzi:

```python title="lancuch-niejawny.py"
def wczytaj_wiek(tekst):
    """Zwraca wiek z łańcucha, dopuszczając zapis z jednostką „lat”."""
    try:
        return int(tekst)
    except ValueError:
        return int(tekst.replace(" lat", ""))


print(wczytaj_wiek("42"))
print(wczytaj_wiek("42 lat"))
print(wczytaj_wiek("dużo"))
```

```{ .text .no-copy }
42
42
Traceback (most recent call last):
  File "lancuch-niejawny.py", line 4, in wczytaj_wiek
    return int(tekst)
ValueError: invalid literal for int() with base 10: 'dużo'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "lancuch-niejawny.py", line 11, in <module>
    print(wczytaj_wiek("dużo"))
          ~~~~~~~~~~~~^^^^^^^^
  File "lancuch-niejawny.py", line 6, in wczytaj_wiek
    return int(tekst.replace(" lat", ""))
ValueError: invalid literal for int() with base 10: 'dużo'
```

Zdanie *During handling of the above exception, another exception occurred* odróżnia łańcuch niejawny od jawnego: interpreter nie wie, czy drugi wyjątek jest skutkiem pierwszego, czy niezależnym błędem w kodzie obsługi, więc pokazuje oba. Gdy przyczyna pierwotna nie ma znaczenia dla czytelnika — bo nowy komunikat mówi wszystko — łańcuch wyłącza forma `from None`:

```python title="lancuch-none.py"
def wczytaj_wiek(tekst):
    """Zwraca wiek jako liczbę całkowitą z łańcucha."""
    try:
        return int(tekst)
    except ValueError:
        raise ValueError(f"nieprawidłowy wiek: {tekst!r}") from None


print(wczytaj_wiek("dużo"))
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "lancuch-none.py", line 9, in <module>
    print(wczytaj_wiek("dużo"))
          ~~~~~~~~~~~~^^^^^^^^
  File "lancuch-none.py", line 6, in wczytaj_wiek
    raise ValueError(f"nieprawidłowy wiek: {tekst!r}") from None
ValueError: nieprawidłowy wiek: 'dużo'
```

Formę `from e` wybieramy, gdy przyczyna pierwotna pomaga zrozumieć błąd (typowo: błąd techniczny przetłumaczony na komunikat z języka programu); formę `from None` — gdy pierwotny wyjątek jest szczegółem implementacji, który tylko zaciemnia ślad.

### Notatki do wyjątku

Zamiast zgłaszać nowy wyjątek, można do istniejącego dopisać informację, której brakowało w miejscu zgłoszenia. Metoda `add_note()`, dostępna od Pythona 3.11, dołącza tekst wypisywany w śladzie pod komunikatem:

```python title="notatka.py"
def wczytaj_liczby(teksty):
    """Zwraca listę liczb; przy błędzie dopisuje do wyjątku numer wiersza."""
    liczby = []
    for numer, tekst in enumerate(teksty, start=1):
        try:
            liczby.append(int(tekst))
        except ValueError as e:
            e.add_note(f"wiersz {numer} danych wejściowych")
            raise
    return liczby


print(wczytaj_liczby(["7", "x", "9"]))
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "notatka.py", line 13, in <module>
    print(wczytaj_liczby(["7", "x", "9"]))
          ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "notatka.py", line 6, in wczytaj_liczby
    liczby.append(int(tekst))
                  ~~~^^^^^^^
ValueError: invalid literal for int() with base 10: 'x'
wiersz 2 danych wejściowych
```

Funkcja `int()` nie wie, z którego wiersza pochodzi łańcuch; wie to pętla, która go przekazała, i to ona dopisuje notatkę. Typ, komunikat i miejsce zgłoszenia pozostają nienaruszone, a wyjątek wędruje dalej z dodatkową informacją.

## Instrukcja `assert` a wyjątki

Instrukcję `assert` z podrozdziału [Struktura projektu i pierwsze testy](../07-moduly/struktura-projektu.md#instrukcja-assert) można teraz opisać w pełni: `assert warunek, komunikat` to skrócony zapis zgłoszenia wyjątku `AssertionError`, gdy warunek jest fałszywy. Różnica wobec `raise` polega na tym, że interpreter uruchomiony z opcją `-O` (od ang. *optimize*) pomija instrukcje `assert` całkowicie — tak jakby ich nie było w pliku. Ta sama opcja ustawia wbudowaną stałą `__debug__` na `False`; równoważna jest zmienna środowiskowa `PYTHONOPTIMIZE`:

```powershell title="Terminal"
python -c "print(__debug__)"
python -O -c "print(__debug__)"
```

```{ .text .no-copy }
True
False
```

Skutek dla instrukcji `assert` sprawdzamy na skrypcie uruchomionym na dwa sposoby:

```python title="zalozenie.py"
def procent(czesc, calosc):
    """Zwraca udział procentowy części w całości."""
    assert calosc > 0, "całość musi być dodatnia"
    return 100 * czesc / calosc


print(procent(1, 4))
print(procent(1, 0))
```

```{ .text .no-copy }
25.0
Traceback (most recent call last):
  File "zalozenie.py", line 8, in <module>
    print(procent(1, 0))
          ~~~~~~~^^^^^^
  File "zalozenie.py", line 3, in procent
    assert calosc > 0, "całość musi być dodatnia"
           ^^^^^^^^^^
AssertionError: całość musi być dodatnia
```

```powershell title="Terminal"
python -O zalozenie.py
```

```{ .text .no-copy }
25.0
Traceback (most recent call last):
  File "zalozenie.py", line 8, in <module>
    print(procent(1, 0))
          ~~~~~~~^^^^^^
  File "zalozenie.py", line 4, in procent
    return 100 * czesc / calosc
           ~~~~~~~~~~~~^~~~~~~~
ZeroDivisionError: division by zero
```

Z opcją `-O` założenie zniknęło, a błąd ujawnił się dopiero przy dzieleniu — z komunikatem, który nic nie mówi o przyczynie. Stąd reguła z rozdziału 7 w pełnym brzmieniu: `assert` sprawdza założenia programisty, które w poprawnym programie są zawsze spełnione, i wolno go pominąć bez zmiany działania programu; dane pochodzące z zewnątrz — od użytkownika, z pliku, z argumentów wywołania — sprawdzamy instrukcją `if` i zgłaszamy `ValueError` albo `TypeError`, bo ta kontrola musi działać zawsze. Testy pytest z rozdziału 7 nie stanowią odstępstwa od tej reguły: pytest przepisuje instrukcje `assert` w plikach testów na własny kod sprawdzający, więc opcja `-O` ich nie dotyczy, a w funkcjach testowych `assert` pozostaje istotą testu; w kodzie programu jest narzędziem diagnostycznym.

## Przykład: konwersja liczb rzymskich z walidacją

Funkcja `na_rzymskie()` łączy oba rodzaje kontroli: sprawdza typ i zakres argumentu, zgłaszając odpowiedni wyjątek, a `main()` obsługuje błędy dla listy danych, z których część jest celowo niepoprawna:

```python title="rzymskie.py"
WARTOSCI = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"),
    (100, "C"), (90, "XC"), (50, "L"), (40, "XL"),
    (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I"),
]


def na_rzymskie(liczba):
    """Zwraca zapis rzymski liczby całkowitej z zakresu 1–3999."""
    if not isinstance(liczba, int):
        raise TypeError(f"wymagana liczba całkowita, otrzymano {type(liczba).__name__}")
    if not 1 <= liczba <= 3999:
        raise ValueError(f"liczba {liczba} poza zakresem 1–3999")
    wynik = ""
    for wartosc, symbol in WARTOSCI:
        while liczba >= wartosc:
            wynik += symbol
            liczba -= wartosc
    return wynik


def main():
    for liczba in [1994, 3999, 4000, "X"]:
        try:
            print(liczba, "->", na_rzymskie(liczba))
        except (ValueError, TypeError) as e:
            print(liczba, "-> błąd:", e)


if __name__ == "__main__":
    main()
```

```{ .text .no-copy }
1994 -> MCMXCIV
3999 -> MMMCMXCIX
4000 -> błąd: liczba 4000 poza zakresem 1–3999
X -> błąd: wymagana liczba całkowita, otrzymano str
```

Kontrola argumentów stoi na początku funkcji, przed obliczeniami, dzięki czemu funkcja nigdy nie zwraca wyniku dla danych, których nie rozumie; obliczenie zaczyna się dopiero wtedy, gdy argument spełnia warunki. Wywołujący otrzymuje albo poprawny wynik, albo wyjątek z komunikatem, który może pokazać użytkownikowi — jak `main()` — albo przekazać dalej.

!!! note "Zapowiedź — własne typy wyjątków"
    Wyjątki wbudowane wystarczają, dopóki wywołujący odróżnia błędy po typie
    `ValueError` albo `TypeError`. Większe programy definiują własne typy
    wyjątków — na przykład `BladZakresu` jako odmianę `ValueError` — aby
    klauzula `except` mogła obsłużyć wyłącznie błędy danego programu, a nazwy
    kończące się na `Error` opisywały jego dziedzinę. Własny typ wyjątku jest
    klasą pochodną od `Exception` lub jego odmiany; definicję klas i zasady
    ich tworzenia poznamy w rozdziale o klasach, a do wyjątków wrócimy
    w nim jako do pierwszego zastosowania dziedziczenia.
    <!-- TODO: link po powstaniu rozdziału o klasach -->

Umiemy już wyjątki przechwytywać i zgłaszać. Pozostaje pytanie, kiedy z tego korzystać: czy sprawdzać warunki przed operacją, czy próbować i obsługiwać błąd, jak szeroki powinien być blok `try` i jak przetestować, że funkcja zgłasza wyjątek wtedy, gdy powinna. Tym zagadnieniom poświęcamy następny podrozdział.
