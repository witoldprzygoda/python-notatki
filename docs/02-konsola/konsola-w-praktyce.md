# Konsola w praktyce

## Konsola jako kalkulator

Najprostszym zastosowaniem konsoli jest kalkulator. Spróbujmy:

```{ .python .no-copy }
>>> 2 + 2
>>> 50 - 5*6
>>> (50 - 5*6) / 4
>>> 8 / 5      # float, dzielenie prawdziwe
>>> 17 // 3    # dzielenie bez reszty
>>> 17 % 3     # modulo, czyli reszta z dzielenia
>>> 5 * 3 + 2
>>> 5 ** 2     # 5^2
>>> 2 ** 7     # 2^7
>>> width = 20
>>> height = 5 * 9
>>> width * height
```

Ostatnia wyświetlona w konsoli wartość jest dostępna również pod nazwą `_` (znak podkreślenia):

```{ .python .no-copy }
>>> 5      # spróbujmy (Enter)
>>> _
>>> _ + _
```

## Funkcja print — pierwsze eksperymenty

Wyniki wypisuje na ekran funkcja `print`. Nawet ta prosta funkcja ma kilka opcji — np. w IDLE podczas pisania widoczna jest podpowiedź z jej pełną sygnaturą.

<!-- TODO: screenshot — podpowiedź sygnatury print() w IDLE -->

Spróbujmy:

```{ .python .no-copy }
>>> print("hello world"*2, ' ', 123, 'tez string', sep=",", end=" ||KONIEC\n")
hello worldhello world, ,123,tez string ||KONIEC

>>> print('hello world', end=', '); print("yeah")
hello world, yeah
```

Z powyższych przykładów widać, że argumenty funkcji mogą mieć postać **argumentów pozycyjnych** bez nazwy oraz **nazwanych** (`sep`, `end`) — te można pisać w dowolnej kolejności (warto wypróbować zamianę `end` z `sep`). Widoczne jest również, że dwie instrukcje w tej samej linii rozdziela separator `;`.

## Funkcja input — wczytywanie danych

Odpowiednikiem funkcji `print` po stronie wejścia jest funkcja **`input`**: wypisuje ona przekazany tekst zachęty, a następnie czeka na dane wprowadzone z klawiatury (zatwierdzone klawiszem ++enter++) i zwraca je jako wynik:

```{ .python .no-copy }
>>> imie = input("Podaj imie: ")
Podaj imie: Anna
>>> print("Witaj,", imie)
Witaj, Anna
```

Istotna właściwość: `input` **zawsze zwraca łańcuch znakowy** (typ `str`) — nawet jeżeli wprowadzone zostały cyfry. Aby otrzymać liczbę, wynik należy jawnie przekonwertować, np. `int(input("Podaj liczbe: "))`; konwersje typów omawia rozdział [3. Nazwy i typy](../03-nazwy-typy/typy-i-konwersje.md).

## Typ obiektu — funkcja type

Obiekty w Pythonie tworzy się dynamicznie, bez deklarowania typów — typ wynika z wartości inicjalizującej. W konsoli można go sprawdzić funkcją `type`:

```{ .python .no-copy }
>>> type(2)
<class 'int'>
>>> type("dwa")
<class 'str'>
>>> type(2.0)
<class 'float'>
```

Systematyczne omówienie typów danych — logicznych, liczbowych i łańcuchowych — zawiera rozdział [3. Nazwy i typy](../03-nazwy-typy/index.md).

## Funkcje matematyczne

Aby mieć dostęp do większej liczby funkcji matematycznych, trzeba skorzystać z dodatkowych modułów. Przed użyciem moduł należy zaimportować. W tym przypadku:

```{ .python .no-copy }
>>> import math
>>> math.sqrt(4)
2.0
```

Spis funkcji: [docs.python.org/3/library/math.html](https://docs.python.org/3/library/math.html) — w przypadku liczb zespolonych użyjemy [cmath](https://docs.python.org/3/library/cmath.html).

## Pomoc wbudowana: help i dir

Konsola jest też najszybszą drogą do dokumentacji. Funkcja `help` wyświetla opis wskazanego obiektu:

```{ .python .no-copy }
>>> help(print)
>>> help(math.sqrt)
```

a wywołana bez argumentu (`help()`) uruchamia interaktywną przeglądarkę pomocy — wpisujemy w niej nazwy funkcji czy modułów, a wychodzimy wpisując `q` (w nowej powłoce tę samą przeglądarkę otwiera klawisz ++f1++). Z kolei funkcja `dir` wypisuje dostępne atrybuty obiektu — np. wszystkie metody typu łańcuchowego:

```{ .python .no-copy }
>>> dir(str)
```

## Zen Pythona

Na zakończenie eksperymentów konsolowych warto wykonać jeszcze jedno polecenie:

```{ .python .no-copy }
>>> import this
The Zen of Python, by Tim Peters

Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
...
Readability counts.
...
```

Jest to **Zen of Python** — zbiór dziewiętnastu aforyzmów opisujących filozofię języka, opublikowany jako [PEP 20](https://peps.python.org/pep-0020/). Do najczęściej przywoływanych należą: „czytelność się liczy" (ang. *readability counts*) oraz „powinien istnieć jeden — i najlepiej tylko jeden — oczywisty sposób zrobienia danej rzeczy". Zasady te wyjaśniają wiele konwencji, które pojawią się w dalszych rozdziałach.
