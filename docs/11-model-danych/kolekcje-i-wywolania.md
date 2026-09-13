# Protokoły kolekcji i wywołania

Funkcja `len()`, konwersja `bool()`, indeksowanie nawiasami kwadratowymi, operator `in` i wywołanie nawiasami okrągłymi działają z listami, słownikami i funkcjami, bo te typy udostępniają metody specjalne o ustalonych nazwach. Własna klasa, która zdefiniuje te same metody, zachowa się w tych miejscach jak kolekcja albo jak funkcja. W tym podrozdziale definiujemy `__len__` i `__bool__`, indeksowanie z wycinkami i indeksem krotkowym, `__contains__` oraz `__call__`, a na koniec zaglądamy do modułu `collections.abc`.

## Protokół jako umowa

W rozdziale 8 nazwaliśmy parę metod `__enter__` i `__exit__` protokołem menedżera kontekstu. Ogólnie **protokół** (ang. *protocol*) to umowa co do nazw i zachowania metod, których Python oczekuje od obiektu w określonej sytuacji: instrukcja `with` oczekuje `__enter__` i `__exit__`, funkcja `len()` — `__len__`, pętla `for` — `__iter__`. Umowa nie wymaga dziedziczenia po żadnej klasie ani deklaracji — wystarczy, że metody istnieją. Podejście to nazywa się **typowaniem kaczym** (ang. *duck typing*): interpreter nie pyta obiektu, czym jest, lecz czy potrafi wykonać żądaną operację. Klasa `Zamowienie` z poprzedniego podrozdziału stanie się w tym podrozdziale pełnoprawną kolekcją, choć nie dziedziczy po liście.

## Metody `__len__` i `__bool__`

Funkcja `len()` wywołuje `__len__`, która musi zwrócić nieujemną liczbę całkowitą. Konwersja `bool()` — także niejawna, w warunku `if` i `while` — wywołuje `__bool__`; gdy klasa jej nie definiuje, Python używa `__len__` i uznaje obiekt za fałszywy, gdy długość wynosi zero; gdy nie ma ani jednej, ani drugiej, każdy obiekt jest prawdziwy:

```python title="zamowienie-len.py"
class Zamowienie:
    """Zamówienie klienta z listą pozycji w koszyku."""

    def __init__(self, koszyk, klient):
        self.koszyk = list(koszyk)
        self.klient = klient

    def __repr__(self):
        return f"Zamowienie({self.koszyk!r}, {self.klient!r})"

    def __len__(self):
        return len(self.koszyk)


z = Zamowienie(["rower", "piłka", "arbuz"], "Jan")
puste = Zamowienie([], "Anna")
print(len(z), len(puste))
print(bool(z), bool(puste))
if not puste:
    print("koszyk jest pusty")
```

```{ .text .no-copy }
3 0
True False
koszyk jest pusty
```

Bez `__len__` wywołanie `len(z)` zgłosiłoby `TypeError: object of type 'Zamowienie' has no len()`, a `bool(puste)` dałoby `True`. Metodę `__bool__` definiujemy wtedy, gdy prawdziwość obiektu ma znaczyć coś innego niż „niepusty” — na przykład wektor jest fałszywy, gdy ma zerową długość — albo gdy obliczanie długości jest kosztowne. Wartość zwracana przez `__len__` jest sprawdzana:

```python title="bledy-len.py"
class ZlaDlugosc:
    def __len__(self):
        return "3"


class UjemnaDlugosc:
    def __len__(self):
        return -1


for klasa in [ZlaDlugosc, UjemnaDlugosc]:
    try:
        print(len(klasa()))
    except (TypeError, ValueError) as e:
        print(f"{type(e).__name__}: {e}")
```

```{ .text .no-copy }
TypeError: 'str' object cannot be interpreted as an integer
ValueError: __len__() should return >= 0
```

## Metody `__getitem__`, `__setitem__` i `__delitem__`

Zapis `obiekt[klucz]` wywołuje `__getitem__(klucz)`, przypisanie `obiekt[klucz] = wartość` — `__setitem__`, a `del obiekt[klucz]` — `__delitem__`. Nazwa parametru jest umowna: dla sekwencji jest to indeks całkowity albo obiekt `slice`, dla odwzorowań — klucz dowolnego haszowalnego typu. Klasa `Zamowienie` deleguje indeksowanie do listy i dzięki temu bez dodatkowej pracy otrzymuje indeksy ujemne, wycinki i właściwe wyjątki:

```python title="zamowienie-indeksy.py"
class Zamowienie:
    """Zamówienie klienta z listą pozycji w koszyku."""

    def __init__(self, koszyk, klient):
        self.koszyk = list(koszyk)
        self.klient = klient

    def __repr__(self):
        return f"Zamowienie({self.koszyk!r}, {self.klient!r})"

    def __len__(self):
        return len(self.koszyk)

    def __getitem__(self, indeks):
        return self.koszyk[indeks]

    def __setitem__(self, indeks, pozycja):
        self.koszyk[indeks] = pozycja

    def __delitem__(self, indeks):
        del self.koszyk[indeks]


z = Zamowienie(["rower", "piłka", "arbuz"], "Jan")
print(z[0], z[-1], z[1:], z[::-1])
z[1] = "kask"
del z[0]
print(z)
for pozycja in z:
    print("-", pozycja)
print("kask" in z, "rower" in z)
try:
    z["x"]
except TypeError as e:
    print("TypeError:", e)
try:
    z[5]
except IndexError as e:
    print("IndexError:", e)
```

```{ .text .no-copy }
rower arbuz ['piłka', 'arbuz'] ['arbuz', 'piłka', 'rower']
Zamowienie(['kask', 'arbuz'], 'Jan')
- kask
- arbuz
True False
TypeError: list indices must be integers or slices, not str
IndexError: list index out of range
```

Wycinek `z[1:]` dociera do `__getitem__` jako obiekt `slice(1, None, None)`, który lista rozumie — dlatego delegowanie do listy jest najprostszą drogą do pełnego indeksowania. Dokumentacja określa też, jakie wyjątki `__getitem__` powinno zgłaszać: `TypeError` dla niewłaściwego typu indeksu i `IndexError` (sekwencje) albo `KeyError` (odwzorowania) dla niewłaściwej wartości; lista robi to za nas. Pętla `for` i operator `in` działają, choć klasa nie definiuje `__iter__` ani `__contains__` — Python korzysta wtedy z `__getitem__`, wywołując je dla kolejnych indeksów od zera aż do `IndexError`. Ten mechanizm, zwany protokołem sekwencji, jest starszy od `__iter__` i wracamy do niego w następnym podrozdziale; w nowym kodzie iterację definiujemy jawnie.

### Indeks krotkowy

Zapis `plansza[1, 2]` to wywołanie `__getitem__` z jednym argumentem — krotką `(1, 2)`. Tak indeksuje się tablice dwuwymiarowe, a plansza do gry w kółko i krzyżyk jest naturalnym przykładem:

```python title="plansza.py"
class Plansza:
    """Plansza 3×3 do gry w kółko i krzyżyk."""

    def __init__(self):
        self._pola = [["." for _ in range(3)] for _ in range(3)]

    def __getitem__(self, pozycja):
        wiersz, kolumna = pozycja
        return self._pola[wiersz][kolumna]

    def __setitem__(self, pozycja, znak):
        wiersz, kolumna = pozycja
        self._pola[wiersz][kolumna] = znak

    def __str__(self):
        return "\n".join(" ".join(wiersz) for wiersz in self._pola)


plansza = Plansza()
plansza[0, 0] = "X"
plansza[1, 1] = "O"
plansza[2, 2] = "X"
print(plansza[1, 1], plansza[0, 1])
print(plansza)
```

```{ .text .no-copy }
O .
X . .
. O .
. . X
```

Rozpakowanie `wiersz, kolumna = pozycja` z rozdziału 5 rozkłada krotkę na dwa indeksy. Biblioteki numeryczne rozbudowują ten zapis o wycinki w każdym wymiarze, na przykład `tablica[0, :]` dla całego wiersza — wracamy do tego w podrozdziale [Tablice ndarray](../14-numpy-matplotlib/ndarray.md#indeksowanie-i-wycinki) rozdziału 14.

## Metoda `__contains__`

Operator `in` wywołuje `__contains__`. Gdy klasa jej nie definiuje, Python przegląda obiekt elementem po elemencie — przez `__iter__`, a w jego braku przez `__getitem__` — i porównuje każdy element z szukanym. Własna implementacja pozwala odpowiedzieć szybciej albo inaczej niż „czy element jest wśród elementów”:

```python title="zakres.py"
class Zakres:
    """Przedział liczb od dolnej do górnej granicy włącznie."""

    def __init__(self, dolna, gorna):
        self.dolna = dolna
        self.gorna = gorna

    def __repr__(self):
        return f"Zakres({self.dolna}, {self.gorna})"

    def __contains__(self, wartosc):
        return self.dolna <= wartosc <= self.gorna


dozwolone = Zakres(0, 150)
print(30 in dozwolone, 200 in dozwolone, 149.5 in dozwolone, -1 not in dozwolone)
```

```{ .text .no-copy }
True False True True
```

Zakres nie przechowuje żadnych elementów, a mimo to odpowiada na `in` — dla liczb zmiennoprzecinkowych, których nie dałoby się wyliczyć. Tak samo działa `in` dla `range()` z rozdziału 4: `10**9 in range(10**10)` nie przegląda miliarda liczb, lecz sprawdza nierówności.

## Metoda `__call__`

Wywołanie `obiekt(argumenty)` uruchamia `__call__(self, argumenty)`. Instancja z tą metodą jest obiektem wywoływalnym w sensie z rozdziału [6. Funkcje](../06-funkcje/funkcje-jako-obiekty.md#obiekty-wywoywalne) — `callable()` zwraca dla niej `True`, można ją przekazać jako argument do `map()` albo `sorted(key=)`. W przeciwieństwie do funkcji taki obiekt ma jawny stan w atrybutach:

```python title="mnoznik.py"
class Mnoznik:
    """Obiekt wywoływalny mnożący argument przez ustalony czynnik."""

    def __init__(self, czynnik):
        self.czynnik = czynnik

    def __call__(self, wartosc):
        return self.czynnik * wartosc


podwoj = Mnoznik(2)
potroj = Mnoznik(3)
print(podwoj(10), potroj(10), callable(podwoj))
print(list(map(podwoj, [1, 2, 3])))
podwoj.czynnik = 5
print(podwoj(10))
```

```{ .text .no-copy }
20 30 True
[2, 4, 6]
50
```

To samo zadanie wykonałoby domknięcie z rozdziału 6 — funkcja zwracająca funkcję, która pamięta `czynnik`. Klasa z `__call__` jest lepszym wyborem, gdy stan ma być widoczny i modyfikowalny z zewnątrz (`podwoj.czynnik = 5`), gdy operacji jest kilka albo gdy obiekt potrzebuje `__repr__`. Obiekt wywoływalny z licznikiem domyka wątek dwuargumentowej funkcji `iter()` z sekcji o obiektach wywoływalnych w rozdziale 6 oraz zapowiedź wywoływalnych instancji z rozdziału 10:

```python title="licznik-call.py"
class Licznik:
    """Obiekt wywoływalny zwracający kolejne liczby od 1."""

    def __init__(self):
        self.stan = 0

    def __call__(self):
        self.stan += 1
        return self.stan


licznik = Licznik()
for numer in iter(licznik, 4):
    print(numer)
print("stan po pętli:", licznik.stan)
```

```{ .text .no-copy }
1
2
3
stan po pętli: 4
```

Funkcja `iter(licznik, 4)` wywołuje obiekt bez argumentów, dopóki wynik nie będzie równy wartownikowi `4`; wartownik nie trafia do pętli, ale wywołanie, które go zwróciło, już się odbyło — stąd stan `4`. Obiekty wywoływalne są też naturalną postacią dekoratorów z rozdziału 6 wtedy, gdy dekorator ma przechowywać dane, na przykład liczbę wywołań:

```python title="dekorator-klasa.py"
class Zliczaj:
    """Dekorator zliczający wywołania funkcji."""

    def __init__(self, funkcja):
        self.funkcja = funkcja
        self.wywolania = 0

    def __call__(self, *args, **kwargs):
        self.wywolania += 1
        return self.funkcja(*args, **kwargs)


@Zliczaj
def kwadrat(x):
    return x * x


print(kwadrat(3), kwadrat(4))
print(kwadrat.wywolania, type(kwadrat).__name__)
```

```{ .text .no-copy }
9 16
2 Zliczaj
```

Składnia `@Zliczaj` oznacza `kwadrat = Zliczaj(kwadrat)`: nazwa `kwadrat` wskazuje odtąd instancję klasy, a każde wywołanie `kwadrat(3)` przechodzi przez `__call__`. Dekorator zapisany jako klasa nie zachowuje jednak metadanych funkcji — `kwadrat.__name__` nie istnieje — czemu w dekoratorach zapisanych jako funkcje zaradzał `functools.wraps` z rozdziału 7; w klasie potrzebne byłoby `functools.update_wrapper(self, funkcja)` w `__init__`.

## Klasy abstrakcyjne kolekcji — `collections.abc` (dla dociekliwych)

Moduł `collections.abc` definiuje klasy opisujące protokoły kolekcji: `Sized` (obiekty z `__len__`), `Container` (`__contains__`), `Iterable` (`__iter__`), `Sequence`, `Mapping` i inne. Dla klas opisujących pojedynczą metodę — `Sized`, `Container`, `Iterable` — funkcja `isinstance()` sprawdza samą obecność metody, bez dziedziczenia; klasy złożone, jak `Sequence` i `Mapping`, rozpoznają wyłącznie klasy pochodne albo jawnie zarejestrowane:

```python title="abc-kolekcje.py"
from collections.abc import Container, Iterable, Sized


class Zamowienie:
    def __init__(self, koszyk, klient):
        self.koszyk = list(koszyk)
        self.klient = klient

    def __len__(self):
        return len(self.koszyk)

    def __getitem__(self, indeks):
        return self.koszyk[indeks]


z = Zamowienie(["rower"], "Jan")
print(isinstance(z, Sized), isinstance(z, Iterable), isinstance(z, Container))
print(isinstance([], Sized), isinstance(42, Sized))
```

```{ .text .no-copy }
True False False
True False
```

Klasa z samym `__getitem__` jest iterowalna i obsługuje `in` dzięki protokołowi sekwencji, ale `Iterable` i `Container` sprawdzają obecność metod `__iter__` i `__contains__`, więc odpowiadają `False`. Dziedziczenie po klasach z `collections.abc` daje więcej: klasa pochodna po `Sequence` musi zdefiniować tylko `__getitem__` i `__len__`, a `__contains__`, `__iter__`, `index()` i `count()` otrzymuje gotowe. Mechanizm klas abstrakcyjnych omawiamy w podrozdziale [Mixiny, kompozycja i klasy abstrakcyjne](../12-oop-zaawansowane/mixiny-i-abstrakcja.md#klasy-abstrakcyjne-abcabc-i-abstractmethod) rozdziału 12.
