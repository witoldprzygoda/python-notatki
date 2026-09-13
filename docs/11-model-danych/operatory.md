# Przeciążanie operatorów

W rozdziale 10 poznaliśmy metody specjalne `__init__`, `__repr__` i `__str__`: Python wywołuje je sam, w określonych sytuacjach. Sytuacji takich jest znacznie więcej — każdy operator, wiele funkcji wbudowanych i kilka instrukcji języka działa przez wywołanie metody specjalnej obiektu. Zbiór tych metod i reguł ich wywoływania nazywamy **modelem danych** (ang. *data model*) Pythona. W tym podrozdziale definiujemy metody odpowiadające operatorom arytmetycznym i porównaniom, poznajemy wartość `NotImplemented` i operacje odbite, uczymy się, jak `__eq__` współpracuje z `__hash__`, a dla dociekliwych zostawiamy operator `@` i metody rozdzielane według typu argumentu.

## Operator jako metoda specjalna

Typy wbudowane nie są uprzywilejowane: dodawanie liczb całkowitych to wywołanie metody `__add__` obiektu `int`, a długość łańcucha — jego metody `__len__`. Metody specjalne można wywołać wprost, choć w zwykłym kodzie nigdy się tego nie robi:

```python title="operator-jako-metoda.py"
print(3 + 4, (3).__add__(4))
print(len("abc"), "abc".__len__())
print([10, 20, 30][1], [10, 20, 30].__getitem__(1))
print((3).__add__(4.5))
print(3 + 4.5)
print([nazwa for nazwa in dir(42) if nazwa.startswith("__")][:6])
```

```{ .text .no-copy }
7 7
3 3
20 20
NotImplemented
7.5
['__abs__', '__add__', '__and__', '__bool__', '__ceil__', '__class__']
```

Nawiasy w `(3).__add__(4)` są konieczne: zapis `3.__add__(4)` kończy się `SyntaxError: invalid decimal literal`, bo parser czyta `3.` jako początek liczby zmiennoprzecinkowej. Czwarty wiersz pokazuje coś istotnego: `int.__add__` nie umie dodać liczby zmiennoprzecinkowej i zwraca wartość `NotImplemented` — a mimo to `3 + 4.5` działa, bo Python próbuje wtedy drugiej strony, czyli metody obiektu `4.5`. Ten mechanizm omawiamy niżej. Funkcja `dir()` z rozdziału 2 wypisuje wszystkie atrybuty obiektu; warunkiem `startswith("__")` wybraliśmy nazwy specjalne — jest ich kilkadziesiąt, a wydruk skróciliśmy do sześciu pierwszych (`__class__` wśród nich jest atrybutem, nie metodą). Własna klasa część tych metod dziedziczy po `object`.

Definiowanie metod specjalnych we własnej klasie nazywamy **przeciążaniem operatorów** (ang. *operator overloading*): operator `+` zyskuje znaczenie dla nowego typu. Ogólna reguła jest prosta — dla operatora dwuargumentowego `x <op> y` Python wywołuje `type(x).__op__(x, y)`, dla funkcji wbudowanej `funkcja(x)` — metodę `x.__funkcja__()`. Tabela zbiera kategorie omawiane w tym rozdziale:

| Kategoria | Metody specjalne | Gdzie omawiane |
|---|---|---|
| tworzenie i reprezentacja | `__new__`, `__init__`, `__del__`, `__repr__`, `__str__`, `__format__` | rozdział 10; `__format__` — menedżery kontekstu |
| arytmetyka | `__add__`, `__sub__`, `__mul__`, `__truediv__`, `__floordiv__`, `__mod__`, `__pow__`, `__matmul__` | ten podrozdział |
| operacje odbite i złożone | `__radd__`, `__rsub__`, …; `__iadd__`, `__isub__`, … | ten podrozdział |
| jednoargumentowe i konwersje | `__neg__`, `__pos__`, `__abs__`, `__int__`, `__float__`, `__bool__` | ten podrozdział; `__bool__` — kolekcje |
| porównania i skrót | `__eq__`, `__ne__`, `__lt__`, `__le__`, `__gt__`, `__ge__`, `__hash__` | ten podrozdział |
| kolekcje i wywołanie | `__len__`, `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `__call__` | kolekcje i wywołania |
| iteracja | `__iter__`, `__next__` | iteracja |
| kontekst | `__enter__`, `__exit__` | menedżery kontekstu |
| dostęp do atrybutów | `__get__`, `__set__`, `__delete__`, `__set_name__`, `__getattr__` | deskryptory |

Przeciążanie operatorów nie jest przeciążaniem metod znanym z języków C++ czy Java, gdzie jedna nazwa może mieć kilka definicji różniących się typami parametrów. W Pythonie nazwa w klasie wskazuje jeden obiekt — druga definicja o tej samej nazwie zastępuje pierwszą:

```python title="dwie-definicje.py"
class Kalkulator:
    def dodaj(self, a):
        return a + 1

    def dodaj(self, a, b):
        return a + b


k = Kalkulator()
print(k.dodaj(2, 3))
print(k.dodaj(2))
```

```{ .text .no-copy }
5
Traceback (most recent call last):
  File "dwie-definicje.py", line 11, in <module>
    print(k.dodaj(2))
          ~~~~~~~^^^
TypeError: Kalkulator.dodaj() missing 1 required positional argument: 'b'
```

Różne zachowanie dla różnych argumentów uzyskujemy w Pythonie wartościami domyślnymi z rozdziału 6, sprawdzaniem typu argumentu wewnątrz metody (`isinstance()`) albo — dla dociekliwych — mechanizmem `singledispatchmethod` z końca tego podrozdziału.

## Arytmetyka — `__add__`, `__sub__` i `__mul__`

Klasa `Wektor2D` reprezentuje wektor na płaszczyźnie. Chcemy dodawać i odejmować wektory, mnożyć wektor przez liczbę, obliczać wektor przeciwny i długość — operatorami `+`, `-`, `*`, jednoargumentowym `-` i funkcją `abs()`:

```python title="wektor2d.py"
import math


class Wektor2D:
    """Wektor na płaszczyźnie o współrzędnych x i y."""

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f"Wektor2D({self.x}, {self.y})"

    def __add__(self, inny):
        return Wektor2D(self.x + inny.x, self.y + inny.y)

    def __sub__(self, inny):
        return Wektor2D(self.x - inny.x, self.y - inny.y)

    def __mul__(self, skalar):
        return Wektor2D(self.x * skalar, self.y * skalar)

    def __neg__(self):
        return Wektor2D(-self.x, -self.y)

    def __abs__(self):
        return math.hypot(self.x, self.y)


v = Wektor2D(3, 4)
w = Wektor2D(1, 2)
print(v + w, v - w)
print(v * 2, -v, abs(v))
print(v)
```

```{ .text .no-copy }
Wektor2D(4.0, 6.0) Wektor2D(2.0, 2.0)
Wektor2D(6.0, 8.0) Wektor2D(-3.0, -4.0) 5.0
Wektor2D(3.0, 4.0)
```

Metody dwuargumentowe otrzymują prawy operand jako drugi parametr i zwracają **nowy** obiekt — `v + w` nie zmienia ani `v`, ani `w`, tak jak dodawanie liczb. Metody jednoargumentowe `__neg__` i `__abs__` nie mają drugiego parametru. Tabela zestawia operatory z metodami; dla każdej metody dwuargumentowej istnieje wersja odbita z przedrostkiem `r`, a dla metod odpowiadających operatorom (nie dla `__divmod__`) — także złożona z przedrostkiem `i`; o obu mowa w dwóch następnych sekcjach:

| Wyrażenie | Metoda | Wyrażenie | Metoda |
|---|---|---|---|
| `x + y` | `__add__` | `x % y` | `__mod__` |
| `x - y` | `__sub__` | `x ** y`, `pow(x, y)` | `__pow__` |
| `x * y` | `__mul__` | `x @ y` | `__matmul__` |
| `x / y` | `__truediv__` | `-x`, `+x` | `__neg__`, `__pos__` |
| `x // y` | `__floordiv__` | `abs(x)` | `__abs__` |
| `divmod(x, y)` | `__divmod__` | `int(x)`, `float(x)` | `__int__`, `__float__` |

Operatory bitowe `&`, `|`, `^`, `<<`, `>>`, `~` mają metody `__and__`, `__or__`, `__xor__`, `__lshift__`, `__rshift__` i `__invert__`; funkcje `round()`, `math.floor()` i `math.ceil()` — `__round__`, `__floor__` i `__ceil__`. Definiujemy tylko te, które mają sens dla naszego typu.

## Wartość `NotImplemented` i operacje odbite — `__radd__`

Klasa `Wektor2D` zakłada, że prawy operand `+` jest wektorem, a prawy operand `*` liczbą. Dla innych typów metoda zgłosi mylący `AttributeError` albo zwróci wynik pozbawiony sensu. Poprawna metoda dwuargumentowa sprawdza typ drugiego operandu, a gdy go nie obsługuje, zwraca wartość specjalną **`NotImplemented`** — nie zgłasza wyjątku. Klasa `Liczba` opakowuje jedną wartość liczbową i dodaje się zarówno do innych obiektów `Liczba`, jak i do zwykłych liczb:

```python title="liczba.py"
class Liczba:
    """Opakowanie liczby, które dodaje się do liczb i do innych opakowań."""

    def __init__(self, wartosc):
        self.wartosc = wartosc

    def __repr__(self):
        return f"Liczba({self.wartosc})"

    def __add__(self, inny):
        if isinstance(inny, Liczba):
            return Liczba(self.wartosc + inny.wartosc)
        if isinstance(inny, (int, float)):
            return Liczba(self.wartosc + inny)
        return NotImplemented

    def __radd__(self, inny):
        return self.__add__(inny)


a = Liczba(3)
print(a + Liczba(4), a + 5, a + 0.5)
print(5 + a)
try:
    print(a + "tekst")
except TypeError as e:
    print("TypeError:", e)
try:
    print("tekst" + a)
except TypeError as e:
    print("TypeError:", e)
```

```{ .text .no-copy }
Liczba(7) Liczba(8) Liczba(3.5)
Liczba(8)
TypeError: unsupported operand type(s) for +: 'Liczba' and 'str'
TypeError: can only concatenate str (not "Liczba") to str
```

Wyrażenie `5 + a` nie może użyć `Liczba.__add__`, bo lewym operandem jest `int`, a `int.__add__(5, a)` zwraca `NotImplemented` — `int` nie zna naszej klasy. Python próbuje wtedy **operacji odbitej** (ang. *reflected operation*): metody `__radd__` prawego operandu, z zamienioną kolejnością argumentów. Dla dodawania przemiennego `__radd__` może wywołać `__add__`; dla odejmowania `__rsub__` musi obliczyć `inny - self`. Gdy obie strony zwrócą `NotImplemented`, interpreter zgłasza `TypeError` z komunikatem, który widzimy w dwóch ostatnich wierszach: dla `a + "tekst"` nasza klasa zwróciła `NotImplemented`, `str` nie ma `__radd__`, więc operacja jest niewykonalna; dla `"tekst" + a` typ `str` nie umie dołączyć obcego obiektu, nasz `__radd__` zwraca `NotImplemented`, a komunikat o konkatenacji formułuje sam `str`. Zwracanie `NotImplemented` zamiast zgłaszania wyjątku jest istotne: daje drugiemu operandowi szansę wykonania operacji i pozwala interpreterowi zbudować właściwy komunikat. Od opisanej kolejności jest jeden wyjątek: gdy prawy operand jest instancją klasy pochodnej od typu lewego operandu i ta klasa nadpisuje metodę odbitą, interpreter próbuje jej jako pierwszej — dzięki temu klasa pochodna może zmienić wynik operacji z klasą bazową niezależnie od strony, po której stoi.

Wartości `NotImplemented` nie należy mylić z wyjątkiem `NotImplementedError`, którym metoda sygnalizuje, że nie została jeszcze napisana. `NotImplemented` jest zwykłym obiektem zwracanym z metody, przeznaczonym wyłącznie dla interpretera; nie wolno go używać jako wartości logicznej — od Pythona 3.14 zapis `if NotImplemented:` zgłasza `TypeError`.

Wektor również powinien odmawiać współpracy z obcymi typami i przyjmować liczbę po lewej stronie mnożenia:

```python title="wektor2d-odbicie.py"
import math


class Wektor2D:
    """Wektor na płaszczyźnie o współrzędnych x i y."""

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f"Wektor2D({self.x}, {self.y})"

    def __add__(self, inny):
        if not isinstance(inny, Wektor2D):
            return NotImplemented
        return Wektor2D(self.x + inny.x, self.y + inny.y)

    def __mul__(self, skalar):
        if not isinstance(skalar, (int, float)):
            return NotImplemented
        return Wektor2D(self.x * skalar, self.y * skalar)

    def __rmul__(self, skalar):
        return self.__mul__(skalar)

    def __abs__(self):
        return math.hypot(self.x, self.y)


v = Wektor2D(3, 4)
print(v * 2, 2 * v)
try:
    print(v * v)
except TypeError as e:
    print("TypeError:", e)
try:
    print(v + 1)
except TypeError as e:
    print("TypeError:", e)
```

```{ .text .no-copy }
Wektor2D(6.0, 8.0) Wektor2D(6.0, 8.0)
TypeError: unsupported operand type(s) for *: 'Wektor2D' and 'Wektor2D'
TypeError: unsupported operand type(s) for +: 'Wektor2D' and 'int'
```

## Operacje złożone — `__iadd__`

Operator `+=` ma własną metodę `__iadd__` (od ang. *in-place*, „w miejscu”), a pozostałe operatory złożone — odpowiednio `__isub__`, `__imul__` i tak dalej. Jeśli klasa jej nie definiuje, Python wykonuje `x = x + y` przez `__add__` i przypisanie, jak dla liczb i krotek. Dla obiektu modyfikowalnego `__iadd__` może zmienić obiekt bez tworzenia nowego — tak działa `+=` na listach. Klasa `Zamowienie` przechowuje koszyk i pozwala dodać pozycję na oba sposoby:

```python title="zamowienie-iadd.py"
class Zamowienie:
    """Zamówienie klienta z listą pozycji w koszyku."""

    def __init__(self, koszyk, klient):
        self.koszyk = list(koszyk)
        self.klient = klient

    def __repr__(self):
        return f"Zamowienie({self.koszyk!r}, {self.klient!r})"

    def __add__(self, pozycja):
        if not isinstance(pozycja, str):
            return NotImplemented
        return Zamowienie(self.koszyk + [pozycja], self.klient)

    def __iadd__(self, pozycja):
        if not isinstance(pozycja, str):
            return NotImplemented
        self.koszyk.append(pozycja)
        return self


z1 = Zamowienie(["rower", "piłka"], "Jan")
z2 = z1 + "kask"
print(z1, z2, z1 is z2)
z1 += "dzwonek"
print(z1)
z3 = z1
z1 += "lampka"
print(z3 is z1, z3.koszyk)
```

```{ .text .no-copy }
Zamowienie(['rower', 'piłka'], 'Jan') Zamowienie(['rower', 'piłka', 'kask'], 'Jan') False
Zamowienie(['rower', 'piłka', 'dzwonek'], 'Jan')
True ['rower', 'piłka', 'dzwonek', 'lampka']
```

Metoda `__add__` zwraca nowe zamówienie i zostawia stare bez zmian, a `__iadd__` dopisuje pozycję do istniejącego koszyka i zwraca `self` — dlatego `z3`, druga nazwa tego samego obiektu, widzi dopisaną lampkę. Zwrócenie `self` jest obowiązkowe: operator `+=` przypisuje wynik metody do nazwy po lewej stronie, więc `__iadd__` bez `return` zamienia obiekt na `None`:

```python title="iadd-bez-return.py"
class Akumulator:
    def __init__(self, wartosc):
        self.wartosc = wartosc

    def __iadd__(self, inny):
        self.wartosc += inny


akumulator = Akumulator(10)
akumulator += 5
print(akumulator)
```

```{ .text .no-copy }
None
```

## Porównania — `__eq__`, `__lt__` i `functools.total_ordering`

Sześciu operatorom porównania odpowiada sześć **metod porównań** (w dokumentacji: *rich comparison methods*): `x == y` wywołuje `x.__eq__(y)`, `x != y` — `__ne__`, `x < y` — `__lt__`, `x <= y` — `__le__`, `x > y` — `__gt__`, `x >= y` — `__ge__`. Klasa `object` dostarcza wszystkie sześć: `__eq__` zwraca `True` dla tego samego obiektu, a `NotImplemented` dla różnych — stąd domyślne porównanie według tożsamości, zapowiedziane w rozdziale 10; `__ne__` odwraca wynik `__eq__`; `__lt__`, `__le__`, `__gt__` i `__ge__` zwracają `NotImplemented` dla każdego argumentu, więc `<` na instancjach własnej klasy zgłasza `TypeError`. Porównania podlegają tym samym regułom co arytmetyka: zwracają `NotImplemented` dla obcego typu, a interpreter próbuje wtedy metody odbitej drugiego operandu — dla `<` jest nią `>`, dla `<=` — `>=`, dla `==` — `==`:

```python title="student-porownania.py"
class Student:
    """Student z nazwiskiem i średnią ocen."""

    def __init__(self, nazwisko, srednia):
        self.nazwisko = nazwisko
        self.srednia = srednia

    def __repr__(self):
        return f"Student({self.nazwisko!r}, {self.srednia})"

    def __eq__(self, inny):
        if not isinstance(inny, Student):
            return NotImplemented
        return self.srednia == inny.srednia

    def __lt__(self, inny):
        if not isinstance(inny, Student):
            return NotImplemented
        return self.srednia < inny.srednia


a = Student("Kowalski", 4.5)
b = Student("Nowak", 3.8)
print(a == b, a != b, a == Student("Lis", 4.5))
print(a < b, a > b, b < a)
print(a == 4.5)
print(sorted([a, b]))
try:
    print(a <= b)
except TypeError as e:
    print("TypeError:", e)
```

```{ .text .no-copy }
False True True
False True True
False
[Student('Nowak', 3.8), Student('Kowalski', 4.5)]
TypeError: '<=' not supported between instances of 'Student' and 'Student'
```

Zdefiniowaliśmy tylko `__eq__` i `__lt__`, a działają także `!=` (Python odwraca `__eq__`) i `>` (dla `a > b` interpreter wywołuje odbite `b.__lt__(a)`). Porównanie `a == 4.5` daje `False` bez wyjątku: obie strony zwróciły `NotImplemented`, a dla równości interpreter wykonuje wtedy jeszcze jeden, ostatni krok — porównanie tożsamości, które daje `False`. Funkcja `sorted()` z rozdziału 5 potrzebuje wyłącznie `__lt__`. Operator `<=` nie ma jednak z czego skorzystać: odziedziczone `__le__` zwraca `NotImplemented`, odbite `__ge__` również, a dla porządkowania — inaczej niż dla równości — nie ma zapasowego porównania tożsamości. Zamiast pisać cztery metody porządkujące, korzystamy z dekoratora klasy `functools.total_ordering`, który na podstawie `__eq__` i jednej metody porządkującej dopisuje pozostałe:

```python title="student-total-ordering.py"
from functools import total_ordering


@total_ordering
class Student:
    """Student z nazwiskiem i średnią ocen."""

    def __init__(self, nazwisko, srednia):
        self.nazwisko = nazwisko
        self.srednia = srednia

    def __repr__(self):
        return f"Student({self.nazwisko!r}, {self.srednia})"

    def __eq__(self, inny):
        if not isinstance(inny, Student):
            return NotImplemented
        return self.srednia == inny.srednia

    def __lt__(self, inny):
        if not isinstance(inny, Student):
            return NotImplemented
        return self.srednia < inny.srednia


a = Student("Kowalski", 4.5)
b = Student("Nowak", 3.8)
print(a <= b, a >= b, b <= a, a >= Student("Lis", 4.5))
print(max(a, b), min([a, b]))
```

```{ .text .no-copy }
False True True True
Student('Kowalski', 4.5) Student('Nowak', 3.8)
```

Dekorator `@total_ordering` jest pierwszym w książce dekoratorem klasy — przyjmuje klasę, dopisuje jej brakujące metody i zwraca ją pod tą samą nazwą, dokładnie według mechanizmu z rozdziału 6. Dopisane metody są nieco wolniejsze od napisanych ręcznie, co ma znaczenie tylko przy bardzo wielu porównaniach.

Liczba zespolona z własnym dodawaniem i porównaniem równości łączy elementy tego podrozdziału w jednej klasie:

```python title="zespolona.py"
import math


class Zespolona:
    """Liczba zespolona o części rzeczywistej re i urojonej im."""

    def __init__(self, re=0.0, im=0.0):
        self.re = float(re)
        self.im = float(im)

    def __repr__(self):
        return f"Zespolona({self.re}, {self.im})"

    def __str__(self):
        znak = "+" if self.im >= 0 else "-"
        return f"{self.re} {znak} {abs(self.im)}i"

    def __add__(self, inna):
        if not isinstance(inna, Zespolona):
            return NotImplemented
        return Zespolona(self.re + inna.re, self.im + inna.im)

    def __sub__(self, inna):
        if not isinstance(inna, Zespolona):
            return NotImplemented
        return Zespolona(self.re - inna.re, self.im - inna.im)

    def __eq__(self, inna):
        if not isinstance(inna, Zespolona):
            return NotImplemented
        return self.re == inna.re and self.im == inna.im

    def __abs__(self):
        return math.hypot(self.re, self.im)

    def sprzezenie(self):
        """Zwraca liczbę sprzężoną."""
        return Zespolona(self.re, -self.im)


a = Zespolona(1, 2)
b = Zespolona(3, -1)
print(a + b, "|", a - b, "|", abs(Zespolona(3, 4)))
print(a == Zespolona(1, 2), a == b, a != b, a == (1, 2))
print(repr(a.sprzezenie()), a.sprzezenie())
```

```{ .text .no-copy }
4.0 + 1.0i | -2.0 + 3.0i | 5.0
True False True False
Zespolona(1.0, -2.0) 1.0 - 2.0i
```

## Metoda `__hash__`

W rozdziale 5 ustaliliśmy, że kluczem słownika i elementem zbioru może być tylko obiekt haszowalny — taki, dla którego `hash()` zwraca liczbę identyfikującą zawartość. Instancje własnych klas są domyślnie haszowalne: `object.__hash__` wylicza skrót z tożsamości, spójnie z domyślnym `__eq__`. Zdefiniowanie własnego `__eq__` psuje tę spójność — dwa obiekty równe według wartości miałyby różne skróty — dlatego Python w takiej klasie ustawia `__hash__` na `None`:

```python title="hash-demo.py"
class Punkt:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Punkt({self.x}, {self.y})"

    def __eq__(self, inny):
        if not isinstance(inny, Punkt):
            return NotImplemented
        return (self.x, self.y) == (inny.x, inny.y)


print(Punkt(1, 2) == Punkt(1, 2), Punkt.__hash__)
try:
    print({Punkt(1, 2)})
except TypeError as e:
    print("TypeError:", e)


class PunktHaszowalny(Punkt):
    def __hash__(self):
        return hash((self.x, self.y))


punkty = {PunktHaszowalny(1, 2), PunktHaszowalny(1, 2), PunktHaszowalny(0, 0)}
print(len(punkty), PunktHaszowalny(0, 0) in punkty)
print(hash(PunktHaszowalny(1, 2)) == hash((1, 2)))
```

```{ .text .no-copy }
True None
TypeError: cannot use 'Punkt' as a set element (unhashable type: 'Punkt')
2 True
True
```

Reguła jest następująca: klasa z własnym `__eq__` powinna albo zdefiniować `__hash__` zgodny z `__eq__` — obiekty równe muszą mieć równe skróty, co najprościej osiągnąć, haszując krotkę tych samych atrybutów, które biorą udział w porównaniu — albo pozostać niehaszowalna. Klasy pochodne dziedziczą tę decyzję: `PunktHaszowalny` przejmuje `__eq__` i dodaje `__hash__`. Obiekt modyfikowalny, którego atrybuty biorą udział w `__eq__`, nie powinien definiować `__hash__`: zmiana atrybutu po umieszczeniu obiektu w zbiorze zmieniłaby skrót, a zbiór nie potrafiłby go już odnaleźć. Właśnie dlatego listy są niehaszowalne, a krotki — tylko wtedy, gdy ich elementy są haszowalne. Klasy `Punkt` i `Wektor2D` nie chronią atrybutów przed zmianą — traktujemy je jako niemodyfikowalne umownie i po utworzeniu obiektu nie przypisujemy do `x` ani `y`; gwarancję dałyby właściwości tylko do odczytu z rozdziału 10. Klasę `Wektor2D`, której współrzędnych umownie nie zmieniamy po utworzeniu, można więc wyposażyć w parę `__eq__` i `__hash__` z krotki `(self.x, self.y)`.

## Operator `@` i metoda rozdzielana według typu (dla dociekliwych)

Operator `@` (metoda `__matmul__`, od ang. *matrix multiplication*) istnieje od Pythona 3.5 wyłącznie po to, aby biblioteki numeryczne mogły zapisać mnożenie macierzy bez nadużywania `*`; żaden typ wbudowany go nie obsługuje. Dla wektorów naturalnym znaczeniem jest iloczyn skalarny:

```python title="matmul.py"
class Wektor2D:
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __matmul__(self, inny):
        if not isinstance(inny, Wektor2D):
            return NotImplemented
        return self.x * inny.x + self.y * inny.y


print(Wektor2D(1, 2) @ Wektor2D(3, 4))
```

```{ .text .no-copy }
11.0
```

W bibliotece NumPy `@` mnoży macierze; wracamy do niego w rozdziale o NumPy. <!-- TODO: link po powstaniu rozdziału o NumPy --> Ten sam znak `@` w składni dekoratorów z rozdziału 6 nie ma z operatorem nic wspólnego.

Brak przeciążania metod po typach argumentów można obejść dekoratorem `functools.singledispatchmethod`: metoda bazowa obsługuje przypadek ogólny, a warianty zarejestrowane przez `@nazwa.register` są wybierane według typu pierwszego argumentu po `self`, odczytanego z adnotacji parametru:

```python title="dispatch.py"
from functools import singledispatchmethod


class Opisywacz:
    """Opisuje wartość zależnie od jej typu."""

    @singledispatchmethod
    def opisz(self, wartosc):
        return f"wartość typu {type(wartosc).__name__}"

    @opisz.register
    def _(self, wartosc: int):
        return f"liczba całkowita {wartosc}"

    @opisz.register
    def _(self, wartosc: str):
        return f"tekst o długości {len(wartosc)}"

    @opisz.register
    def _(self, wartosc: list):
        return f"lista {len(wartosc)} elementów"


o = Opisywacz()
print(o.opisz(42))
print(o.opisz("Python"))
print(o.opisz([1, 2, 3]))
print(o.opisz(3.14))
```

```{ .text .no-copy }
liczba całkowita 42
tekst o długości 6
lista 3 elementów
wartość typu float
```

Warianty noszą nazwę `_`, bo ich nazwa nie ma znaczenia — dostęp odbywa się zawsze przez `opisz`. Adnotacje typów, w rozdziale 6 opisane jako informacja bez wpływu na wykonanie, tu wyjątkowo sterują wyborem wariantu; o narzędziach, które korzystają z adnotacji na większą skalę, mowa w rozdziale o narzędziach analizy typów. <!-- TODO: link po powstaniu rozdziału o narzędziach analizy typów -->
