# Menedżery kontekstu i obiekty plikopodobne

Instrukcja `with` z rozdziału 8 współpracuje z każdym obiektem, który ma metody `__enter__` i `__exit__`; tam pisaliśmy własne menedżery kontekstu dekoratorem `contextlib.contextmanager`, odkładając wersję klasową do czasu poznania klas. W tym podrozdziale piszemy menedżer kontekstu jako klasę, uczymy się tłumić wyjątki w `__exit__`, porównujemy obie postacie, budujemy obiekt plikopodobny dla `print(file=)` — domykając zapowiedź z rozdziału 9 — i definiujemy `__format__`, ostatnią z metod reprezentacji zapowiedzianych w rozdziale 10.

## Metody `__enter__` i `__exit__`

Wykonanie `with wyrażenie as nazwa:` przebiega tak, jak opisaliśmy w rozdziale [8. Wyjątki i zarządzanie zasobami](../08-wyjatki/with-i-contextlib.md#protoko-menedzera-kontekstu): interpreter wywołuje `__enter__()` menedżera, wynik wiąże z nazwą po `as`, wykonuje blok, a na końcu — zawsze — wywołuje `__exit__()`. Metoda `__exit__` przyjmuje trzy argumenty opisujące wyjątek, który opuścił blok: jego typ, obiekt wyjątku i ślad wywołań; gdy blok zakończył się normalnie, wszystkie trzy są `None`. Stoper z rozdziału 8 jako klasa:

```python title="stoper-klasa.py"
import time


class Stoper:
    """Mierzy czas wykonania bloku with i zapamiętuje go w atrybucie czas."""

    def __init__(self, nazwa):
        self.nazwa = nazwa
        self.czas = None

    def __repr__(self):
        return f"Stoper({self.nazwa!r})"

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, typ, wartosc, slad):
        self.czas = time.perf_counter() - self._start
        print(f"{self.nazwa}: {self.czas:.3f} s (wyjątek: {typ})")
        return False


with Stoper("sortowanie") as stoper:
    posortowane = sorted(range(1_000_000, 0, -1))
print(posortowane[:3], stoper.czas is not None)
try:
    with Stoper("dzielenie"):
        1 / 0
except ZeroDivisionError as e:
    print("ZeroDivisionError:", e)
```

```{ .text .no-copy }
sortowanie: 0.031 s (wyjątek: None)
[1, 2, 3] True
dzielenie: 0.000 s (wyjątek: <class 'ZeroDivisionError'>)
ZeroDivisionError: division by zero
```

Zmierzone czasy zależą od komputera. Metoda `__enter__` zapamiętuje początek pomiaru i zwraca `self`, dzięki czemu obiekt stopera jest dostępny pod nazwą `stoper` — także po zakończeniu bloku, gdy atrybut `czas` ma już wartość. Metoda `__exit__` została wywołana również wtedy, gdy blok przerwał wyjątek: otrzymała jego typ, wypisała pomiar i zwróciła `False`, więc wyjątek propagował dalej, do klauzuli `except`. Zwracanie `False` (albo `None`, czyli brak `return`) jest zachowaniem domyślnym i właściwym dla większości menedżerów: sprzątają i nie ingerują w wyjątki.

## Tłumienie wyjątku — wartość zwracana przez `__exit__`

Jeśli `__exit__` zwróci wartość prawdziwą, wyjątek zostaje **stłumiony** — instrukcja `with` kończy się normalnie, a wykonanie programu jest kontynuowane za blokiem. Tak działa `pytest.raises()` z rozdziału 8, którego `__exit__` tłumi oczekiwany wyjątek. Własny menedżer ignorujący wybrane typy wyjątków:

```python title="ignoruj.py"
class Ignoruj:
    """Menedżer kontekstu tłumiący wyjątki podanych typów."""

    def __init__(self, *typy):
        self.typy = typy

    def __enter__(self):
        return None

    def __exit__(self, typ, wartosc, slad):
        return typ is not None and issubclass(typ, self.typy)


with Ignoruj(KeyError, IndexError):
    print({"a": 1}["b"])
    print("ten wiersz nie zostanie wykonany")
print("po pierwszym with")

try:
    with Ignoruj(KeyError):
        print([][0])
except IndexError as e:
    print("IndexError przepuszczony:", e)
```

```{ .text .no-copy }
po pierwszym with
IndexError przepuszczony: list index out of range
```

Metoda `__exit__` zwraca `True` tylko wtedy, gdy wyjątek wystąpił i należy do wskazanych typów — `issubclass()` z rozdziału 10 uwzględnia klasy pochodne, więc `Ignoruj(LookupError)` stłumiłby zarówno `KeyError`, jak i `IndexError`. Blok przerwany przez stłumiony wyjątek nie jest wznawiany: wiersz po `print({"a": 1}["b"])` się nie wykonał. Metoda `__enter__` zwraca tu `None`, bo menedżer nie ma czego udostępnić pod `as`. Tłumienie stosujemy wyłącznie do wyjątków, których wystąpienie jest przewidziane i nieszkodliwe; menedżer tłumiący wszystko ukrywałby błędy programu, dokładnie jak goła klauzula `except` z rozdziału 8. Biblioteka standardowa ma gotowy odpowiednik naszej klasy — `contextlib.suppress()`.

## Klasa a dekorator `contextlib.contextmanager`

Ten sam stoper w obu postaciach:

```python title="stoper-dwie-postacie.py"
import time
from contextlib import contextmanager


class Stoper:
    """Stoper klasowy z pomiarem dostępnym po bloku."""

    def __init__(self):
        self.czas = None

    def __repr__(self):
        return f"Stoper(czas={self.czas})"

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, typ, wartosc, slad):
        self.czas = time.perf_counter() - self._start
        return False


@contextmanager
def stoper(nazwa):
    """Stoper generatorowy wypisujący pomiar po bloku."""
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{nazwa}: {time.perf_counter() - start:.3f} s")


pomiar = Stoper()
with pomiar:
    suma = sum(range(1_000_000))
print(f"pierwszy pomiar: {pomiar.czas:.3f} s")
with pomiar:
    suma = sum(range(2_000_000))
print(f"drugi pomiar: {pomiar.czas:.3f} s")
with stoper("sumowanie"):
    suma = sum(range(1_000_000))
```

```{ .text .no-copy }
pierwszy pomiar: 0.018 s
drugi pomiar: 0.036 s
sumowanie: 0.018 s
```

Dekorator `@contextmanager` zamienia funkcję generatorową w menedżer: kod przed `yield` odpowiada `__enter__`, kod po nim — `__exit__`, a `finally` zapewnia wykonanie sprzątania także przy wyjątku. Jest krótszy i wystarcza, gdy menedżer wykonuje prosty przebieg „przygotuj — oddaj sterowanie — posprzątaj”. Klasę wybieramy, gdy menedżer ma stan, z którego korzystamy po bloku (`pomiar.czas`), gdy ten sam obiekt ma być używany wielokrotnie albo gdy oprócz `__enter__` i `__exit__` potrzebuje innych metod. Obie postacie realizują ten sam protokół — obiekt zwracany przez `stoper("sumowanie")` również ma metody `__enter__` i `__exit__` — zdefiniowane w klasie pomocniczej modułu `contextlib`, której instancję zwraca udekorowana funkcja.

## Obiekt plikopodobny — metoda `write()`

Argument `file` funkcji `print()` przyjmuje, jak ustaliliśmy w rozdziale 9, dowolny obiekt z metodą `write()` — nie tylko plik. **Obiekt plikopodobny** (ang. *file-like object*) to kolejny protokół: umowa, że obiekt ma `write()` przyjmującą łańcuch, a zwykle także `flush()`. Klasa `Pisarz` gromadzi wszystko, co do niej wypisano:

```python title="pisarz.py"
import io


class Pisarz:
    """Obiekt plikopodobny gromadzący wypisany tekst w pamięci."""

    def __init__(self):
        self._czesci = []

    def write(self, tekst):
        """Dopisuje tekst i zwraca liczbę zapisanych znaków."""
        self._czesci.append(tekst)
        return len(tekst)

    def flush(self):
        """Nic nie buforuje, więc nie ma czego opróżniać."""

    def getvalue(self):
        """Zwraca cały zgromadzony tekst."""
        return "".join(self._czesci)

    def __repr__(self):
        return f"Pisarz({self.getvalue()!r})"


pisarz = Pisarz()
print("Pierwsza porcja tekstu.", end=" ", file=pisarz)
print("Druga porcja.", file=pisarz)
print("Trzecia, z opróżnieniem.", file=pisarz, flush=True)
print(repr(pisarz.getvalue()))
print(pisarz._czesci[:4])

bufor = io.StringIO()
print("to samo przez StringIO", file=bufor)
print(repr(bufor.getvalue()))
try:
    print("tekst", file=object())
except AttributeError as e:
    print("AttributeError:", e)
```

```{ .text .no-copy }
'Pierwsza porcja tekstu. Druga porcja.\nTrzecia, z opróżnieniem.\n'
['Pierwsza porcja tekstu.', ' ', 'Druga porcja.', '\n']
'to samo przez StringIO\n'
AttributeError: 'object' object has no attribute 'write'
```

Lista części pokazuje, jak `print()` korzysta z `write()`: osobno przekazuje każdy argument, separator między argumentami oraz łańcuch `end` — w wydruku widać `' '` przekazane jako `end=" "` i `'\n'`. Metoda `flush()` jest potrzebna, bo `print(flush=True)` wywołuje ją na obiekcie docelowym — bez niej to wywołanie kończy się `AttributeError: 'Pisarz' object has no attribute 'flush'`; nasza wersja jest pusta, bo `Pisarz` niczego nie buforuje. Klasa `io.StringIO` z rozdziału [9. Wejście, wyjście i pliki](../09-wejscie-wyjscie/bytes-i-pliki-binarne.md#pliki-w-pamieci-iostringio-i-iobytesio-dla-dociekliwych) robi to samo i więcej — obsługuje odczyt, `seek()` i `with` — więc w praktyce sięgamy po nią; własny `Pisarz` przydaje się, gdy zapis ma wywoływać dodatkowe działania, na przykład wysyłać tekst do okna programu albo do dziennika `logging` z rozdziału 8. Obiekt plikopodobny nie musi dziedziczyć po żadnej klasie pliku — `print()` sprawdza jedynie, czy ma `write()`, co pokazuje ostatni wiersz.

## Metoda `__format__`

W rozdziale 10 ustaliliśmy, że f-string bez konwersji wywołuje `format()`, a więc metodę specjalną `__format__`, która w wersji odziedziczonej po `object` sprowadza się do `__str__`. Dotyczy to jednak wyłącznie pola bez specyfikacji formatu: `object.__format__` przyjmuje tylko pusty łańcuch, a każdą specyfikację odrzuca. Klasa, która ma współpracować z mini-językiem formatu z rozdziału [9. Wejście, wyjście i pliki](../09-wejscie-wyjscie/formatowanie.md#mini-jezyk-specyfikacji-formatu), definiuje `__format__` sama:

```python title="format-wektor.py"
class Wektor2D:
    """Wektor na płaszczyźnie z formatowaniem składowych."""

    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f"Wektor2D({self.x}, {self.y})"

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __format__(self, specyfikacja):
        if not specyfikacja:
            return str(self)
        return f"({format(self.x, specyfikacja)}, {format(self.y, specyfikacja)})"


class BezFormatu:
    def __str__(self):
        return "obiekt"


v = Wektor2D(3, 4.5)
print(f"{v} | {v!r} | {v:.2f} | {v:>8.1f} | {format(v, 'e')}")
b = BezFormatu()
print(f"{b} | {b!s}")
try:
    print(f"{b:>10}")
except TypeError as e:
    print("TypeError:", e)
```

```{ .text .no-copy }
(3.0, 4.5) | Wektor2D(3.0, 4.5) | (3.00, 4.50) | (     3.0,      4.5) | (3.000000e+00, 4.500000e+00)
obiekt | obiekt
TypeError: unsupported format string passed to BezFormatu.__format__
```

Metoda `__format__` otrzymuje specyfikację z pola f-stringa — to, co stoi po dwukropku — i sama decyduje, co ona znaczy; wektor deleguje ją do składowych `float`, więc `:.2f` zaokrągla obie współrzędne. Konwersje `!r` i `!s` omijają `__format__` obiektu: wywołują `__repr__` albo `__str__`, a specyfikację — jeśli jest — stosują już do otrzymanego łańcucha, więc `f"{b!s:>10}"` działa nawet dla klasy bez własnego `__format__`. Klasa `BezFormatu` działa w f-stringu bez specyfikacji, ale `{b:>10}` kończy się `TypeError` — tak zachowuje się każda klasa, która ani nie definiuje `__format__`, ani nie dziedziczy go po typie wbudowanym — w tym wszystkie klasy z rozdziału 10.

## Zapowiedź — blokady

Menedżery kontekstu spotkamy jeszcze w jednym ważnym miejscu: blokada w programie wielowątkowym jest menedżerem kontekstu, a `with blokada:` gwarantuje jej zwolnienie także przy wyjątku; wracamy do tego w podrozdziale [Synchronizacja](../15-wspolbieznosc/synchronizacja.md#blokada-lock-i-instrukcja-with) rozdziału 15.
