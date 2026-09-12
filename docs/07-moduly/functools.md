# Moduł functools

W rozdziale 6 napisaliśmy własne dekoratory: `zapamietuj` przechowujący wyniki w słowniku, `z_ramka` i `licz_wywolania`. Przy każdym z nich odnotowaliśmy ograniczenie, którego nie usuwaliśmy, bo nie korzystaliśmy jeszcze z modułów: pamięć podręczna obsługiwała tylko argumenty pozycyjne, a funkcja opakowująca zasłaniała nazwę i docstring funkcji pierwotnej. Moduł `functools` z biblioteki standardowej zbiera narzędzia do pracy z funkcjami jako obiektami — funkcje wyższego rzędu w rozumieniu sekcji [Funkcje pierwszej klasy](../06-funkcje/funkcje-jako-obiekty.md#funkcje-pierwszej-klasy) — i rozwiązuje oba problemy gotowymi dekoratorami. W tym podrozdziale poznajemy cztery jego elementy: dekoratory `cache` i `lru_cache`, dekorator `wraps`, funkcję `partial` oraz funkcję `reduce`. Od tej chwili memoizację i dekoratory zapisujemy wyłącznie z ich użyciem.

## Pamięć podręczna wyników: `cache` i `lru_cache`

Dekorator `zapamietuj` z sekcji [Memoizacja](../06-funkcje/dekoratory.md#memoizacja) przechowywał wyniki funkcji w słowniku w domknięciu, z krotką argumentów jako kluczem. Dekorator `functools.cache` robi to samo, ale włącza do klucza także argumenty nazwane, w CPythonie jest zaimplementowany w języku C i udostępnia statystyki. Zastosujmy go do funkcji `fib` z podrozdziału [Rekurencja](../06-funkcje/rekurencja.md#rekurencja-a-iteracja), która bez memoizacji wykonywała miliony wywołań:

```python title="fib-cache.py"
import functools


@functools.cache
def fib(n):
    """Zwraca n-ty wyraz ciągu Fibonacciego (fib(0) = 0, fib(1) = 1)."""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


print(fib(100))
print(fib.cache_info())
```

```{ .text .no-copy }
354224848179261915075
CacheInfo(hits=98, misses=101, maxsize=None, currsize=101)
```

Definicja `fib` pozostała bez zmian — memoizację dodaje sam wiersz `@functools.cache`. Metoda `cache_info()` zwraca krotkę z nazwanymi polami z poprzedniego podrozdziału: `misses` to liczba wywołań, które wymagały obliczenia (po jednym dla każdego argumentu od 0 do 100), `hits` — liczba wywołań obsłużonych z pamięci podręcznej, `currsize` — liczba przechowywanych wyników, a `maxsize=None` oznacza brak ograniczenia rozmiaru. Same liczby są szczegółem implementacji CPythona; istotny jest rząd wielkości — kilkaset wywołań zamiast wykładniczo rosnącej liczby. Metoda `cache_clear()` opróżnia pamięć podręczną. Wywołania `fib(10)` i `fib(n=10)` są zapamiętywane jako osobne wpisy, bo klucz obejmuje sposób przekazania argumentów.

Pamięcią podręczną pozostaje słownik, więc obowiązuje warunek znany z rozdziału 5: argumenty muszą być haszowalne. Funkcja przyjmująca listę nie nadaje się do memoizacji — wywołanie kończy się błędem `TypeError`, zanim ciało funkcji zostanie wykonane:

```{ .python .no-copy }
>>> import functools
>>> @functools.cache
... def dlugosc(dane):
...     return len(dane)
...
>>> dlugosc((1, 2, 3))
3
>>> dlugosc([1, 2, 3])
Traceback (most recent call last):
  File "<python-input-3>", line 1, in <module>
    dlugosc([1, 2, 3])
    ~~~~~~~^^^^^^^^^^^
TypeError: unhashable type: 'list'
```

Pamięć podręczna bez ograniczenia rośnie tak długo, jak długo działa program i jak wiele różnych argumentów otrzymuje funkcja. W skrypcie obliczającym kilkaset wyrazów ciągu nie ma to znaczenia, ale w programie działającym godzinami i wywołującym funkcję z wciąż nowymi argumentami pamięć podręczna stałaby się wyciekiem pamięci (ang. *memory leak*). Na taką sytuację moduł oferuje dekorator `functools.lru_cache(maxsize=128)`, który po zapełnieniu usuwa wpis **najdawniej używany** (ang. *least recently used*, stąd skrót LRU):

```python title="lru.py"
import functools


@functools.lru_cache(maxsize=32)
def kwadrat(n):
    """Zwraca kwadrat liczby."""
    return n * n


for n in range(40):
    kwadrat(n)
print(kwadrat.cache_info())
print(kwadrat(39), kwadrat(0))
print(kwadrat.cache_info())
```

```{ .text .no-copy }
CacheInfo(hits=0, misses=40, maxsize=32, currsize=32)
1521 0
CacheInfo(hits=1, misses=41, maxsize=32, currsize=32)
```

Po czterdziestu wywołaniach pamięć podręczna zawiera trzydzieści dwa ostatnie wyniki: `kwadrat(39)` zostaje odczytany z pamięci podręcznej, a `kwadrat(0)` — najdawniejszy, już usunięty — musi być obliczony ponownie. Dekorator `cache` jest równoważny `lru_cache(maxsize=None)`, ale bez mechanizmu usuwania jest mniejszy i szybszy, dlatego stosujemy go zawsze wtedy, gdy zbiór argumentów jest ograniczony, jak przy `fib`; `lru_cache` z limitem wybieramy dla funkcji o nieograniczonym zbiorze argumentów w długo działającym programie. Oba dekoratory zachowują metadane funkcji pierwotnej i udostępniają ją w atrybucie `__wrapped__` — korzystają z narzędzia opisanego w następnej sekcji.

## Zachowanie metadanych: `wraps`

W sekcji [Metadane funkcji](../06-funkcje/dekoratory.md#metadane-funkcji) pokazaliśmy koszt dekorowania: po zastosowaniu `z_ramka` atrybuty `__name__`, `__qualname__` i `__doc__` oraz funkcja `help()` opisywały funkcję `opakowana`, nie `powitanie`. Rozwiązaniem jest `functools.wraps` — dekorator z argumentem w rozumieniu sekcji [Dekoratory z argumentami i składanie dekoratorów](../06-funkcje/dekoratory.md#dekoratory-z-argumentami-i-skadanie-dekoratorow), stosowany **wewnątrz** dekoratora, nad funkcją opakowującą, z funkcją pierwotną jako argumentem:

```python title="metadane-wraps.py"
import functools


def z_ramka(funkcja):
    """Zwraca funkcję opakowującą, która wypisuje ramkę wokół wywołania."""
    @functools.wraps(funkcja)
    def opakowana(*args, **kwargs):
        print("---")
        wynik = funkcja(*args, **kwargs)
        print("---")
        return wynik

    return opakowana


@z_ramka
def powitanie(imie):
    """Zwraca powitanie dla podanego imienia."""
    return f"Witaj, {imie}!"


print(powitanie("Ola"))
print(powitanie.__name__)
print(powitanie.__qualname__)
print(powitanie.__doc__)
print(powitanie.__wrapped__("Ola"))
help(powitanie)
```

```{ .text .no-copy }
---
---
Witaj, Ola!
powitanie
powitanie
Zwraca powitanie dla podanego imienia.
Witaj, Ola!
Help on function powitanie in module __main__:

powitanie(imie)
    Zwraca powitanie dla podanego imienia.

```

Dekorator `@functools.wraps` zachowuje istotne metadane funkcji opakowywanej, między innymi jej nazwę, docstring i adnotacje, oraz udostępnia odwołanie `__wrapped__`. Funkcja `help()` pokazuje teraz nazwę, sygnaturę `(imie)` i docstring funkcji pierwotnej — sygnaturę odczytuje właśnie przez `__wrapped__`, bo funkcja opakowująca nadal ma parametry `(*args, **kwargs)`. Atrybut `__wrapped__` pozwala też wywołać funkcję pierwotną z pominięciem dekoratora, co widać w przedostatnim wierszu wyniku: powitanie bez ramki. Pełny zestaw kopiowanych atrybutów opisuje dokumentacja modułu; `wraps` jest wygodną formą funkcji `functools.update_wrapper()`, która wykonuje samo kopiowanie.

Od tej chwili każdy dekorator w książce ma tę postać. Wzorzec z sekcji [Stan w dekoratorze](../06-funkcje/dekoratory.md#stan-w-dekoratorze) — funkcja opakowująca z licznikiem w domknięciu — w wersji ostatecznej wygląda tak:

```python title="licz-wywolania-wraps.py"
import functools


def licz_wywolania(funkcja):
    """Zwraca funkcję opakowującą, która numeruje kolejne wywołania."""
    licznik = 0

    @functools.wraps(funkcja)
    def opakowana(*args, **kwargs):
        nonlocal licznik
        licznik += 1
        print(f"Wywołanie {licznik}: {funkcja.__name__}")
        return funkcja(*args, **kwargs)

    return opakowana


@licz_wywolania
def kwadrat(x):
    """Zwraca kwadrat liczby."""
    return x * x


print(kwadrat(3))
print(kwadrat(4))
print(kwadrat.__name__, kwadrat.__doc__)
```

```{ .text .no-copy }
Wywołanie 1: kwadrat
9
Wywołanie 2: kwadrat
16
kwadrat Zwraca kwadrat liczby.
```

Jedyną zmianą wobec rozdziału 6 jest wiersz `@functools.wraps(funkcja)`. Nie komplikuje on dekoratora, a zapewnia poprawne metadane w dokumentacji, introspekcji i narzędziach analizy kodu. Nie zmienia natomiast śladów wywołań: wyjątek zgłoszony wewnątrz udekorowanej funkcji nadal pokazuje ramkę `opakowana`, bo `wraps` kopiuje atrybuty obiektu funkcji, a nie jej kod.

## Częściowe zastosowanie: `partial`

W sekcji [Domknięcia](../06-funkcje/zasieg-nazw-i-domkniecia.md#domkniecia) fabryka `mnoznik(przez)` zwracała funkcję z ustalonym na stałe jednym z argumentów. Funkcja `functools.partial()` wykonuje tę operację bez pisania fabryki: przyjmuje funkcję oraz część jej argumentów, a zwraca obiekt wywoływalny, który przy wywołaniu dokłada pozostałe argumenty i wywołuje funkcję pierwotną. Operacja ta nosi nazwę **częściowego zastosowania** (ang. *partial application*):

```python title="czesciowe.py"
import functools

binarna = functools.partial(int, base=2)
print(binarna("101"), binarna("1111"))
print(binarna)

wypisz = functools.partial(print, sep=", ")
wypisz(1, 2, 3)
wypisz("a", "b", sep=" | ")

potega_dwojki = functools.partial(pow, 2)
print(potega_dwojki(10))
print(list(map(binarna, ["1", "10", "11"])))
```

```{ .text .no-copy }
5 15
functools.partial(<class 'int'>, base=2)
1, 2, 3
a | b
1024
[1, 2, 3]
```

Obiekt `binarna` wywołuje `int(napis, base=2)`; jego reprezentacja pokazuje funkcję pierwotną i ustalone argumenty, dostępne także w atrybutach `func`, `args` i `keywords`. Argumenty pozycyjne podane przy tworzeniu trafiają na początek listy argumentów — `potega_dwojki(10)` to `pow(2, 10)` — a argumenty nazwane można przy wywołaniu nadpisać, jak `sep=" | "` w czwartym wierszu. Częściowe zastosowanie jest wygodne wszędzie tam, gdzie funkcję trzeba przekazać dalej — do `map()`, jako funkcję klucza, jako funkcję wywoływaną po zdarzeniu w interfejsie graficznym — a istniejąca funkcja wymaga dodatkowego, stałego argumentu; zapis `partial(int, base=2)` jest przy tym czytelniejszy od `lambda napis: int(napis, base=2)`, bo nie wprowadza nowego parametru. Od Pythona 3.14 moduł udostępnia także obiekt `functools.Placeholder`, pozwalający zarezerwować miejsce na argument pozycyjny podawany dopiero przy wywołaniu; w książce z niego nie korzystamy.

## Funkcja `reduce`

Ostatnie narzędzie modułu, zapowiedziane w sekcji [Funkcje map() i filter()](../06-funkcje/funkcje-jako-obiekty.md#funkcje-map-i-filter), pochodzi z tej samej tradycji programowania funkcyjnego. Funkcja `functools.reduce(funkcja, iterowalny)` przyjmuje funkcję dwuargumentową i **redukuje** obiekt iterowalny do jednej wartości: stosuje funkcję do dwóch pierwszych elementów, potem do wyniku i trzeciego elementu, i tak do końca — dla listy `[1, 2, 3, 4]` i mnożenia oblicza `((1 * 2) * 3) * 4`. Trzeci, opcjonalny argument `initial` jest wartością początkową, od której zaczyna się redukcja; od Pythona 3.14 można go podać jako argument nazwany:

```{ .python .no-copy }
>>> import functools
>>> import math
>>> functools.reduce(lambda a, b: a * b, [1, 2, 3, 4])
24
>>> math.prod([1, 2, 3, 4])
24
>>> slowa = ["alfa", "beta", "gamma"]
>>> functools.reduce(lambda a, b: a + " " + b, slowa, initial="Słowa:")
'Słowa: alfa beta gamma'
>>> functools.reduce(lambda a, b: a * b, [])
Traceback (most recent call last):
  File "<python-input-6>", line 1, in <module>
    functools.reduce(lambda a, b: a * b, [])
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: reduce() of empty iterable with no initial value
```

Iterowalny o jednym elemencie daje ten element bez wywoływania funkcji, a pusty — błąd `TypeError`, chyba że podano `initial`, które wtedy staje się wynikiem. Funkcja `math.prod()`, użyta w drugim wywołaniu, oblicza iloczyn elementów tak, jak `sum()` oblicza sumę; nie potrzebowaliśmy jej wcześniej, bo iloczyny liczyliśmy pętlą. W praktyce `reduce` rzadko jest najlepszym wyborem: dla typowych redukcji istnieją funkcje wbudowane — `sum()`, `max()`, `min()`, `math.prod()`, metoda `join()` dla łańcuchów — a redukcję nietypową zwykle czytelniej zapisuje pętla `for` z nazwaną wartością bieżącą. Wyrażenie lambda w roli funkcji dwuargumentowej można zastąpić gotową funkcją z modułu `operator`, który udostępnia operatory języka w postaci funkcji — na przykład `operator.mul` zamiast `lambda a, b: a * b`. Wartość `reduce` polega na tym, że nazywa operację: gdy w kodzie pojawia się „złóż elementy jedną funkcją do jednej wartości”, zapis z `reduce` wyraża to wprost.

Moduł `functools` obejmuje jeszcze narzędzia wymagające pojęć z dalszych rozdziałów: `cached_property` i `total_ordering` (klasy) oraz `singledispatch` (wybór implementacji funkcji według typu argumentu). W następnym podrozdziale przechodzimy do modułu `itertools`, który wobec funkcji generatorowych z rozdziału 6 pełni tę samą rolę, jaką `functools` pełni wobec dekoratorów.
