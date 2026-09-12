# Obsługa wyjątków

Od rozdziału 2 spotykamy błędy wykonania: `ValueError` przy `int(input())`, `KeyError` i `IndexError` przy kontenerach, `RecursionError` w rozdziale 6, `ModuleNotFoundError` i `AssertionError` w rozdziale 7. Za każdym razem czytaliśmy je wyłącznie ze **śladu wywołań** (ang. *traceback*), a program kończył się kodem wyjścia `1`, jak ustaliliśmy w sekcji [Kody wyjścia i funkcja `sys.exit()`](../07-moduly/argumenty-wiersza-polecen.md#kody-wyjscia-i-funkcja-sysexit). W tym podrozdziale błąd staje się obiektem, z którym program może coś zrobić: **wyjątek** (ang. *exception*) zgłoszony w jednym miejscu można przechwycić w innym i zdecydować, co dalej — na tym polega **obsługa wyjątków** (ang. *exception handling*). Ustalamy, jak wyjątek wędruje przez wywołania, jak czytać ślad w brzmieniu Pythona 3.14, które wyjątki spotykamy najczęściej i jak działa instrukcja `try` z klauzulami `except`, `else` i `finally`. Na koniec piszemy funkcję, która wczytuje liczbę od użytkownika i poprawnie reaguje na błędny wpis.

## Program bez obsługi i z obsługą

Funkcja `srednia()` oblicza średnią wartości podanych jako łańcuchy znaków — tak trafiają do programu dane z klawiatury lub z pliku. Konwersja `int()` jest tu miejscem, w którym program może zawieść:

```python title="srednia.py"
def srednia(dane):
    """Zwraca średnią arytmetyczną wartości podanych jako łańcuchy."""
    liczby = [int(tekst) for tekst in dane]
    return sum(liczby) / len(liczby)


print(srednia(["4", "5", "6"]))
print(srednia(["4", "pięć", "6"]))
print("koniec programu")
```

```{ .text .no-copy }
5.0
Traceback (most recent call last):
  File "srednia.py", line 8, in <module>
    print(srednia(["4", "pięć", "6"]))
          ~~~~~~~^^^^^^^^^^^^^^^^^^^^
  File "srednia.py", line 3, in srednia
    liczby = [int(tekst) for tekst in dane]
              ~~~^^^^^^^
ValueError: invalid literal for int() with base 10: 'pięć'
```

Drugie wywołanie nie zwróciło wyniku, a wiersz `koniec programu` nigdy się nie wykonał. Funkcja `int()` napotkała łańcuch, którego nie umie zamienić na liczbę, i **zgłosiła** (ang. *raise*) wyjątek `ValueError`. Wyjątek jest obiektem — ma typ i komunikat — i nie jest zwykłą wartością zwracaną: przerywa wykonanie w miejscu zgłoszenia i wędruje w górę przez wywołania; tę wędrówkę nazywamy **propagacją** (ang. *propagation*). Funkcja `srednia()` nie miała dla niego obsługi, więc jej wykonanie zostało przerwane i wyjątek trafił do kodu modułu; tam również nie został przechwycony, więc interpreter wypisał ślad wywołań na **strumień błędów** (ang. *standard error*, `stderr`) i zakończył program. Strumień błędów jest kanałem wyjścia odrębnym od **standardowego wyjścia** (ang. *standard output*, `stdout`), na które trafia `print()`: w konsoli widzimy oba razem, ale przekierowanie wyjścia programu do pliku poleceniem `python program.py > wynik.txt` zapisuje w pliku tylko standardowe wyjście, a ślad nadal pojawia się w konsoli. Taki wyjątek nazywamy **nieprzechwyconym** (ang. *unhandled*).

Instrukcja `try` pozwala wskazać fragment kodu, w którym spodziewamy się wyjątku, i podać, co zrobić, gdy wystąpi:

```python title="srednia-obsluga.py"
def srednia(dane):
    """Zwraca średnią arytmetyczną wartości podanych jako łańcuchy."""
    liczby = [int(tekst) for tekst in dane]
    return sum(liczby) / len(liczby)


for dane in (["4", "5", "6"], ["4", "pięć", "6"]):
    try:
        print(srednia(dane))
    except ValueError:
        print("dane zawierają wartość, która nie jest liczbą")
print("koniec programu")
```

```{ .text .no-copy }
5.0
dane zawierają wartość, która nie jest liczbą
koniec programu
```

Wyjątek powstał w tym samym miejscu co poprzednio — wewnątrz `int()` wywołanej w `srednia()` — ale tym razem, wędrując w górę, natrafił na blok `try` z klauzulą `except ValueError` i został **przechwycony** (ang. *caught*). Wykonanie bloku `try` zostało przerwane w chwili zgłoszenia (wywołanie `print()` z pierwszego wiersza pętli nie doszło do skutku), wykonała się klauzula `except`, a program kontynuował od instrukcji następującej po całej instrukcji `try`. Sama funkcja `srednia()` pozostała bez zmian: o tym, co zrobić z błędem, zdecydował kod, który ją wywołał. To rozdzielenie — wyjątek zgłasza ten, kto wykrył problem, a obsługuje ten, kto wie, co z nim zrobić — jest istotą całego mechanizmu.

## Anatomia śladu wywołań

Ślad wywołań czyta się od dołu. Ostatni wiersz podaje typ wyjątku i komunikat — to on odpowiada na pytanie, co się stało. Wyżej znajdują się **ramki** (ang. *frame*), po jednej dla każdego aktywnego wywołania w chwili zgłoszenia, wypisane w kolejności od najstarszego do najnowszego, o czym przypomina nagłówek `most recent call last`: ostatnia ramka to miejsce zgłoszenia, a każda wyżej to wywołanie, które do niego doprowadziło. Ramka zawiera nazwę pliku, numer wiersza i nazwę funkcji — `<module>` oznacza kod na poziomie modułu, jak w podrozdziale [Skrypt jako program](../07-moduly/skrypt-jako-program.md) — a pod nią wiersz kodu. Od Pythona 3.11 interpreter dodaje pod wierszem znaczniki wskazujące fragment, który był obliczany w chwili błędu; od Pythona 3.13 przy wywołaniu funkcji `~~~` obejmuje nazwę wywoływanej funkcji, a `^^^` nawiasy z argumentami. W śladzie wyżej `~~~^^^^^^^` pod `int(tekst)` mówi więc, że zawiodło wywołanie `int()`, a nie na przykład odczyt nazwy `tekst`. W śladach przytaczanych w książce ścieżkę do pliku skracamy do nazwy, zgodnie z regułą z podrozdziału [Definiowanie funkcji](../06-funkcje/definiowanie-funkcji.md#anatomia-definicji-i-wywoania); interpreter wypisuje ścieżkę pełną. W terminalu obsługującym kolory Python 3.13 i nowszy wyróżnia barwami nazwy plików, numery wierszy i komunikat; kolorowanie wyłącza zmienna środowiskowa `NO_COLOR` (albo `PYTHON_COLORS=0`), a w tekście książki go nie odtwarzamy.

### Podpowiedzi interpretera

Od Pythona 3.10 ślad zawiera przy niektórych błędach podpowiedź, na przykład przy literówce w nazwie:

```python title="podpowiedz.py"
import math

print(mth.sqrt(2))
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "podpowiedz.py", line 3, in <module>
    print(mth.sqrt(2))
          ^^^
NameError: name 'mth' is not defined. Did you mean: 'math'?
```

Dopisek `Did you mean: 'math'?` powstaje dopiero podczas wypisywania śladu: interpreter porównuje błędną nazwę z nazwami dostępnymi w danym miejscu i proponuje najbliższą. Sam obiekt wyjątku tej podpowiedzi nie zawiera, co sprawdzimy w sekcji o obiekcie wyjątku. Podpowiedzi pojawiają się też przy `AttributeError` (literówka w nazwie atrybutu), `ImportError` i błędach składni; są pomocą diagnostyczną, której brzmienie zmienia się z wersji na wersję, i nie należy na nich polegać w kodzie.

## Najczęstsze wyjątki

Typy wyjątków są typami jak `int` czy `list` — zgłoszony wyjątek jest obiektem takiego typu — i noszą nazwy zakończone zwykle na `Error`. Poniższa tabela zbiera te, które pojawiły się dotąd w książce lub pojawią się w tym rozdziale, wraz z komunikatami w brzmieniu Pythona 3.14; komunikaty należą do implementacji i mogą się zmieniać, dlatego programy rozpoznają wyjątki po typie, nie po treści komunikatu.

| Wyjątek | Sytuacja | Przykład | Komunikat |
|---|---|---|---|
| `ValueError` | argument właściwego typu, ale o niewłaściwej wartości | `int("abc")` | `invalid literal for int() with base 10: 'abc'` |
| `TypeError` | operacja na obiekcie niewłaściwego typu | `"a" + 1` | `can only concatenate str (not "int") to str` |
| `IndexError` | indeks poza zakresem sekwencji | `[][0]` | `list index out of range` |
| `KeyError` | brak klucza w słowniku | `{}["klucz"]` | `'klucz'` |
| `ZeroDivisionError` | dzielenie przez zero | `1 / 0` | `division by zero` |
| `AttributeError` | brak atrybutu w obiekcie | `None.x` | `'NoneType' object has no attribute 'x'` |
| `NameError` | nieznana nazwa | `print(xyz)` | `name 'xyz' is not defined` |
| `FileNotFoundError` | brak pliku | `open("brak.txt", encoding="utf-8")` | `[Errno 2] No such file or directory: 'brak.txt'` |
| `ModuleNotFoundError` | brak modułu na ścieżce wyszukiwania | `import brak` | `No module named 'brak'` |
| `RecursionError` | przekroczony limit rekurencji | `def f(): f()` | `maximum recursion depth exceeded` |
| `AssertionError` | niespełnione założenie | `assert 1 == 2` | pusty albo tekst po przecinku |
| `StopIteration` | wyczerpany iterator | `next(iter([]))` | pusty |

Trzy z nich znamy z wcześniejszych rozdziałów jako sygnały końca albo błędu programisty: `StopIteration` z podrozdziału [Pętle i iteratory](../04-sterowanie/petle-i-iteratory.md#iteratory), `RecursionError` z podrozdziału [Rekurencja](../06-funkcje/rekurencja.md#limit-rekurencji) i `AssertionError` z podrozdziału [Struktura projektu i pierwsze testy](../07-moduly/struktura-projektu.md#instrukcja-assert). `FileNotFoundError` pochodzi z funkcji `open()`, która otwiera plik do odczytu; jej pełne omówienie należy do rozdziału o wejściu i wyjściu, a w tym rozdziale korzystamy z niej wyłącznie jako ze źródła tego wyjątku i jako z przykładu zasobu, który trzeba zamknąć. <!-- TODO: link po powstaniu rozdziału o wejściu i wyjściu --> Niektóre nazwy w tabeli tworzą rodziny — `IndexError` i `KeyError` są odmianami ogólniejszego `LookupError`, a `FileNotFoundError` należy do rodziny `OSError` — do czego wracamy w następnym podrozdziale przy hierarchii wyjątków.

## Instrukcja `try` i klauzula `except`

Instrukcja `try` składa się z bloku `try` oraz co najmniej jednej klauzuli `except`, każda z nazwą typu wyjątku. Gdy w bloku `try` — także wewnątrz wywołanych z niego funkcji — zostanie zgłoszony wyjątek, interpreter przegląda klauzule po kolei i wykonuje pierwszą, której typ pasuje; pozostałe pomija. Gdy żadna nie pasuje, wyjątek wędruje dalej, tak jakby instrukcji `try` nie było:

```python title="dzielenie.py"
pary = [(1, 2), (1, 0), ("1", 2)]
for a, b in pary:
    try:
        print(a / b)
    except ZeroDivisionError:
        print("dzielenie przez zero")
    except TypeError:
        print("argumenty muszą być liczbami")
```

```{ .text .no-copy }
0.5
dzielenie przez zero
argumenty muszą być liczbami
```

Klauzula `except` obsługuje wyłącznie wymieniony typ. Jest to celowe: przechwytujemy te wyjątki, które potrafimy sensownie obsłużyć, a pozostałe pozwalamy przejść wyżej — do kodu, który wie o programie więcej, albo do interpretera, który zakończy program ze śladem. Kod obsługi jest zwykle krótki: komunikat dla użytkownika, wartość zastępcza, powtórzenie próby.

### Obiekt wyjątku

Dopisek `as nazwa` w klauzuli wiąże obiekt wyjątku z nazwą, dzięki czemu obsługa ma dostęp do jego typu i komunikatu:

```python title="obiekt-wyjatku.py"
for tekst in ["12", "dwanaście"]:
    try:
        print(int(tekst))
    except ValueError as e:
        print("typ:", type(e).__name__)
        print("komunikat:", e)
        print("argumenty:", e.args)
        print("repr:", repr(e))
```

```{ .text .no-copy }
12
typ: ValueError
komunikat: invalid literal for int() with base 10: 'dwanaście'
argumenty: ("invalid literal for int() with base 10: 'dwanaście'",)
repr: ValueError("invalid literal for int() with base 10: 'dwanaście'")
```

Nazwa `e` jest zwyczajowa. Konwersja `str(e)` — tę wykonuje `print()` — daje komunikat, ten sam, który widzimy w ostatnim wierszu śladu; krotka `e.args` przechowuje argumenty, z jakimi wyjątek utworzono (zwykle jeden komunikat), a `repr(e)` pokazuje typ i argumenty w postaci wywołania. Nazwa związana przez `as` istnieje tylko wewnątrz klauzuli: po jej zakończeniu interpreter usuwa ją, aby obiekt wyjątku wraz ze śladem nie pozostawał w pamięci.

Niektóre typy udostępniają dodatkowe atrybuty. `FileNotFoundError` przechowuje nazwę brakującego pliku w `e.filename`, a `StopIteration` zgłaszany po zakończeniu funkcji generatorowej instrukcją `return wartość` — zapowiedziany w podrozdziale [Funkcje generatorowe](../06-funkcje/funkcje-generatorowe.md#delegowanie-przez-yield-from) — niesie tę wartość w `e.value`. W sesji sprawdzamy oba, a przy okazji to, że komunikat `NameError` nie zawiera podpowiedzi ze śladu:

```{ .python .no-copy }
>>> try:
...     open("brak.txt", encoding="utf-8")
... except FileNotFoundError as e:
...     print(e.filename, "|", e)
...
brak.txt | [Errno 2] No such file or directory: 'brak.txt'
>>> def gen():
...     yield 1
...     return "koniec"
...
>>> g = gen()
>>> next(g)
1
>>> try:
...     next(g)
... except StopIteration as e:
...     print(repr(e.value))
...
'koniec'
>>> import math
>>> try:
...     mth.sqrt(2)
... except NameError as e:
...     print(e)
...
name 'mth' is not defined
```

### Kilka typów w jednej klauzuli

Gdy kilka typów wyjątków ma tę samą obsługę, podajemy je w krotce:

```python title="krotka-typow.py"
pary = [(1, 0), ("1", 2)]
for a, b in pary:
    try:
        print(a / b)
    except (ZeroDivisionError, TypeError) as e:
        print("nieudane dzielenie:", e)
```

```{ .text .no-copy }
nieudane dzielenie: division by zero
nieudane dzielenie: unsupported operand type(s) for /: 'str' and 'int'
```

Python 3.14 dopuszcza pominięcie nawiasów, gdy klauzula nie używa `as` — zapis `except ZeroDivisionError, TypeError:` jest od tej wersji poprawny. W książce pozostajemy przy nawiasach: działają w każdej wersji Pythona, są jedyną formą dopuszczalną z `as`, a próba połączenia zapisu bez nawiasów z `as` kończy się błędem składni jeszcze przed uruchomieniem programu:

```python title="bez-nawiasow.py"
try:
    print(1 / 0)
except ZeroDivisionError, TypeError as e:
    print("nieudane dzielenie:", e)
```

```{ .text .no-copy }
  File "bez-nawiasow.py", line 3
    except ZeroDivisionError, TypeError as e:
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SyntaxError: multiple exception types must be parenthesized when using 'as'
```

### Kolejność klauzul `except`

Klauzule są sprawdzane od góry i wykonuje się pierwsza pasująca. Ma to znaczenie, gdy typy są ze sobą spokrewnione: typ ogólniejszy pasuje także do wyjątków typów szczegółowych, więc umieszczony wyżej przesłania klauzule pod sobą:

```python title="kolejnosc.py"
try:
    int("abc")
except Exception:
    print("obsługa ogólna")
except ValueError:
    print("obsługa ValueError")
```

```{ .text .no-copy }
obsługa ogólna
```

`Exception` jest typem ogólnym, do którego pasują niemal wszystkie wyjątki, więc druga klauzula nigdy się nie wykona; Pylint z rozdziału 1 zgłasza taki układ jako `bad-except-order`. Regułą jest kolejność od typu najbardziej szczegółowego do najogólniejszego; które typy są ogólniejsze od których, opisuje hierarchia wyjątków w następnym podrozdziale.

## Klauzule `else` i `finally`

Instrukcja `try` ma dwie klauzule opcjonalne. Klauzula `else` wykonuje się wtedy, gdy blok `try` zakończył się bez wyjątku; klauzula `finally` — zawsze, jako ostatnia, niezależnie od tego, czy wyjątek wystąpił i czy został obsłużony:

```python title="else-finally.py"
def wczytaj(tekst):
    """Wypisuje liczbę z tekstu i informuje o przebiegu próby."""
    try:
        liczba = int(tekst)
    except ValueError:
        print(f"{tekst!r} nie jest liczbą")
    else:
        print(f"wczytano {liczba}")
    finally:
        print("koniec próby")


wczytaj("42")
wczytaj("abc")
```

```{ .text .no-copy }
wczytano 42
koniec próby
'abc' nie jest liczbą
koniec próby
```

W komunikacie użyliśmy zapisu `{tekst!r}`, który wstawia do f-stringu wynik `repr(tekst)` zamiast `str(tekst)`, dzięki czemu łańcuch pojawia się w cudzysłowach. Instrukcję `print(f"wczytano {liczba}")` można by umieścić w bloku `try` tuż po konwersji, ale wtedy `except ValueError` obejmowałby także ją — a `ValueError` zgłoszony przypadkiem w kodzie, który miał tylko wypisać wynik, zostałby mylnie potraktowany jako błąd konwersji. Klauzula `else` pozwala utrzymać blok `try` możliwie wąski: obejmuje wyłącznie instrukcję, po której spodziewamy się wyjątku. Do tej zasady wracamy w podrozdziale o stylu obsługi błędów.

Klauzula `finally` służy do czynności porządkowych — zwalniania zasobów, które program zajął w bloku `try` — i wykonuje się nawet wtedy, gdy blok `try` kończy funkcję instrukcją `return` albo gdy wyjątek nie został obsłużony i wędruje dalej:

```python title="finally-return.py"
def sprawdz():
    """Zwraca wynik z bloku try; klauzula finally wykonuje się mimo return."""
    try:
        return "wynik z try"
    finally:
        print("sprzątanie")


print(sprawdz())
```

```{ .text .no-copy }
sprzątanie
wynik z try
```

Wartość została obliczona w `return`, potem wykonała się klauzula `finally`, a dopiero potem funkcja zwróciła wynik. Instrukcje `return`, `break` i `continue` wewnątrz samej klauzuli `finally` są natomiast źródłem trudnych do wykrycia błędów: przerywają wychodzenie z instrukcji `try`, więc `return` w `finally` zastępuje wynik z bloku `try`, a nieobsłużony wyjątek zostaje porzucony bez żadnego komunikatu. Od Pythona 3.14 kompilator ostrzega o takim zapisie:

```python title="finally-blad.py"
def wynik():
    try:
        return "z try"
    finally:
        return "z finally"


print(wynik())
```

```{ .text .no-copy }
finally-blad.py:5: SyntaxWarning: 'return' in a 'finally' block
  return "z finally"
z finally
```

Ostrzeżenie trafia na strumień błędów podczas kompilacji pliku, przed uruchomieniem programu — tak samo jak ostrzeżenie o `assert` z krotką w podrozdziale [Struktura projektu i pierwsze testy](../07-moduly/struktura-projektu.md#instrukcja-assert) — a program wykonuje się dalej i zwraca `z finally`. Klauzula `finally` powinna zwalniać zasoby, nie sterować przepływem. Najczęstszy przypadek sprzątania — zamknięcie pliku lub innego zasobu — ma w Pythonie osobną, wygodniejszą składnię, instrukcję `with`, której poświęcamy dalszy podrozdział.

## Walidacja danych wejściowych

Typowym zastosowaniem obsługi wyjątków jest wczytywanie danych od użytkownika. Funkcja `input()` z rozdziału 2 zwraca łańcuch, a konwersja `int()` zgłasza `ValueError` dla każdego wpisu, który nie jest liczbą całkowitą. Pętla `while True` z podrozdziału [Pętle i iteratory](../04-sterowanie/petle-i-iteratory.md#petla-while) powtarza pytanie, dopóki konwersja się nie powiedzie, a instrukcja `return` w bloku `try` kończy zarówno pętlę, jak i funkcję:

```python title="wczytaj-liczbe.py"
def wczytaj_liczbe(komunikat):
    """Zwraca liczbę całkowitą wczytaną od użytkownika; pyta aż do skutku."""
    while True:
        tekst = input(komunikat)
        try:
            return int(tekst)
        except ValueError:
            print(f"{tekst!r} nie jest liczbą całkowitą, spróbuj ponownie")


wiek = wczytaj_liczbe("Podaj wiek: ")
print(f"Za 10 lat: {wiek + 10}")
```

```{ .text .no-copy }
Podaj wiek: dwanaście
'dwanaście' nie jest liczbą całkowitą, spróbuj ponownie
Podaj wiek: 12
Za 10 lat: 22
```

Blok `try` obejmuje wyłącznie konwersję; wywołanie `input()` stoi przed nim, bo nie jest źródłem `ValueError`, a komunikat dla użytkownika powtarza błędny wpis w cudzysłowach dzięki `{tekst!r}`. Ten sam wzorzec obsługuje wczytywanie ciągu wartości zakończonego słowem umownym; operator `:=` z podrozdziału [Wyrażenia warunkowe](../04-sterowanie/wyrazenia-warunkowe.md#operator-przypisania-w-wyrazeniu) pozwala wczytać i sprawdzić wpis w warunku pętli, a błędne wpisy są pomijane zamiast przerywać program:

```python title="suma-liczb.py"
suma = 0
while (tekst := input("Liczba (albo koniec): ")) != "koniec":
    try:
        suma += int(tekst)
    except ValueError:
        print(f"{tekst!r} pominięte")
print("suma:", suma)
```

```{ .text .no-copy }
Liczba (albo koniec): 5
Liczba (albo koniec): x
'x' pominięte
Liczba (albo koniec): 7
Liczba (albo koniec): koniec
suma: 12
```

Nasuwa się pytanie, czy zamiast próbować konwersji nie lepiej sprawdzić wpis wcześniej — metoda `str.isdigit()` z podrozdziału [Funkcje jako obiekty](../06-funkcje/funkcje-jako-obiekty.md#funkcje-map-i-filter) zwraca `True`, gdy łańcuch składa się wyłącznie z cyfr. Sprawdzenie takie jest jednak węższe niż reguły funkcji `int()`:

```{ .python .no-copy }
>>> "42".isdigit(), "dwanaście".isdigit()
(True, False)
>>> "-5".isdigit(), int("-5")
(False, -5)
>>> " 7 ".isdigit(), int(" 7 ")
(False, 7)
>>> "1_000".isdigit(), int("1_000")
(False, 1000)
```

Liczby ujemne, wpisy ze spacjami i zapis z podkreśleniami `int()` przyjmuje, a `isdigit()` odrzuca; odtworzenie pełnych reguł konwersji własnym warunkiem jest trudne i zbędne, skoro `int()` zna je najlepiej i zgłasza wyjątek, gdy nie są spełnione. Oba podejścia — sprawdzenie przed operacją i próba z obsługą wyjątku — mają swoje miejsce; porównujemy je w podrozdziale o stylu obsługi błędów. Wcześniej jednak trzeba nauczyć się drugiej strony mechanizmu: dotąd wyjątki zgłaszał za nas interpreter i funkcje wbudowane, a w następnym podrozdziale zaczniemy zgłaszać je sami.
