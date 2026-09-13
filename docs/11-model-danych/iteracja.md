# Protokół iteracji

Pętla `for` z rozdziału 4 przechodzi po listach, łańcuchach, słownikach, plikach i generatorach. Łączy je protokół iteracji — para metod `__iter__` i `__next__` — który w tym podrozdziale poznajemy od strony klasy: rozpisujemy pętlę `for` na wywołania, piszemy iterator jako klasę, oddzielamy kolekcję od jej iteratora, korzystamy z `__iter__` jako funkcji generatorowej i przeglądamy typowe błędy.

## Obiekt iterowalny a iterator

Rozdział 4 wprowadził dwa pojęcia, które teraz możemy zdefiniować przez metody. **Obiekt iterowalny** (ang. *iterable*) to obiekt z metodą `__iter__`, która zwraca iterator; można po nim przechodzić wielokrotnie, bo każde wywołanie `__iter__` może dać nowy iterator. **Iterator** (ang. *iterator*) to obiekt z metodą `__next__`, która zwraca kolejny element albo zgłasza `StopIteration`, gdy elementów nie ma; iterator ma również `__iter__` zwracające jego samego, dzięki czemu może stać wszędzie tam, gdzie oczekiwany jest obiekt iterowalny. Funkcja wbudowana `iter()` wywołuje `__iter__`, a `next()` — `__next__`:

```python title="iterowalny-a-iterator.py"
lista = [10, 20, 30]
iterator = iter(lista)
print(type(iterator).__name__, iter(iterator) is iterator)
print(next(iterator), next(iterator), next(iterator))
try:
    next(iterator)
except StopIteration:
    print("StopIteration")
print(next(iterator, "koniec"))
print(hasattr(lista, "__next__"), hasattr(iterator, "__next__"))
```

```{ .text .no-copy }
list_iterator True
10 20 30
StopIteration
koniec
False True
```

Lista jest iterowalna, ale nie jest iteratorem — nie ma `__next__`; iterator listy jest osobnym obiektem, który pamięta pozycję. Po wyczerpaniu każde kolejne `next()` zgłasza `StopIteration`; dwuargumentowa forma `next(iterator, wartość)` zwraca zamiast tego wartość domyślną.

## Pętla `for` od środka

Instrukcja `for element in obiekt:` jest skrótem pętli `while`, która pobiera iterator i wywołuje `next()` aż do `StopIteration`:

```python title="for-od-srodka.py"
slowa = ["ala", "ma", "kota"]

iterator = iter(slowa)
while True:
    try:
        slowo = next(iterator)
    except StopIteration:
        break
    print(slowo.upper())
```

```{ .text .no-copy }
ALA
MA
KOTA
```

Ten sam mechanizm stoi za rozpakowaniem `a, b = para`, funkcjami `list()`, `sum()`, `max()`, `sorted()`, `zip()` i `enumerate()`, złożeniami list i wyrażeniami generatorowymi — wszystkie przyjmują dowolny obiekt iterowalny, bo wszystkie wywołują `iter()` i `next()`. Dlatego klasa, która zaimplementuje protokół, współpracuje z całym tym zestawem bez dodatkowej pracy.

## Iterator jako klasa — `Odliczanie`

Iterator napisany jako klasa przechowuje stan w atrybutach, zwraca kolejne wartości z `__next__` i kończy zgłoszeniem `StopIteration`:

```python title="odliczanie.py"
class Odliczanie:
    """Iterator odliczający od podanej liczby do 1."""

    def __init__(self, start):
        self.biezaca = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.biezaca <= 0:
            raise StopIteration
        wartosc = self.biezaca
        self.biezaca -= 1
        return wartosc


for liczba in Odliczanie(3):
    print(liczba)
odliczanie = Odliczanie(2)
print(list(odliczanie), list(odliczanie))
```

```{ .text .no-copy }
3
2
1
[2, 1] []
```

Metoda `__iter__` zwraca `self`, bo obiekt sam jest iteratorem — pętla `for` wywoła na nim `next()`. Ostatni wiersz pokazuje cenę tego rozwiązania: iterator jest jednorazowy. Drugie `list()` dostaje ten sam, już wyczerpany obiekt i zwraca pustą listę — tak samo jak generator z rozdziału 6 i jak `reversed()` w rozdziale 4.

## Oddzielenie kolekcji od iteratora

Kolekcja, po której chcemy przechodzić wielokrotnie — także w dwóch pętlach naraz — nie powinna być własnym iteratorem. Jej `__iter__` zwraca za każdym razem nowy obiekt iteratora z osobnym stanem:

```python title="talia.py"
class IteratorTalii:
    """Iterator przechodzący po kartach talii."""

    def __init__(self, karty):
        self._karty = karty
        self._pozycja = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._pozycja >= len(self._karty):
            raise StopIteration
        karta = self._karty[self._pozycja]
        self._pozycja += 1
        return karta


class Talia:
    """Talia kart, po której można przechodzić wielokrotnie."""

    def __init__(self, karty):
        self._karty = list(karty)

    def __iter__(self):
        return IteratorTalii(self._karty)


talia = Talia(["As", "Król", "Dama"])
print(list(talia), list(talia))
for pierwsza in talia:
    for druga in talia:
        if pierwsza != druga:
            print(pierwsza, "-", druga)
```

```{ .text .no-copy }
['As', 'Król', 'Dama'] ['As', 'Król', 'Dama']
As - Król
As - Dama
Król - As
Król - Dama
Dama - As
Dama - Król
```

Dwie zagnieżdżone pętle po tej samej talii działają, bo każda otrzymała własny iterator. Gdyby `Talia` była własnym iteratorem, jak `Odliczanie`, pętla wewnętrzna zużyłaby wspólny stan i pętla zewnętrzna skończyłaby się po pierwszym przebiegu. Tak są zbudowane typy wbudowane: lista ma `__iter__` zwracające nowy `list_iterator`, słownik — `dict_keyiterator`.

## Metoda `__iter__` jako funkcja generatorowa

Osobna klasa iteratora jest rozwlekła. Rozdział 6 dostarczył krótszej drogi: funkcja generatorowa zwraca obiekt generatora, a generator jest iteratorem — ma `__next__` i `__iter__`. Wystarczy więc napisać `__iter__` ze słowem `yield`:

```python title="talia-generator.py"
class Talia:
    """Talia kart z iteracją przez funkcję generatorową."""

    def __init__(self, karty):
        self._karty = list(karty)

    def __iter__(self):
        for karta in self._karty:
            yield karta

    def __reversed__(self):
        for karta in reversed(self._karty):
            yield karta


talia = Talia(["As", "Król", "Dama"])
print(type(iter(talia)).__name__)
print(list(talia), list(reversed(talia)))
print([karta for karta in talia if karta != "Król"])
```

```{ .text .no-copy }
generator
['As', 'Król', 'Dama'] ['Dama', 'Król', 'As']
['As', 'Dama']
```

Każde wywołanie `iter(talia)` uruchamia funkcję generatorową od nowa, więc po kolekcji nadal można przechodzić wielokrotnie, a stan iteracji — pozycję w pętli — przechowuje generator. To zalecany sposób implementacji `__iter__` dla własnych kolekcji; osobna klasa iteratora jest potrzebna tylko wtedy, gdy iterator ma udostępniać dodatkowe metody albo gdy stan iteracji musi być widoczny z zewnątrz. Metoda `__reversed__` w ten sam sposób obsługuje funkcję `reversed()`. W najprostszym przypadku — gdy klasa opakowuje jedną kolekcję — `__iter__` może zwrócić wprost jej iterator: `return iter(self._karty)`.

## Protokół sekwencji przez `__getitem__` (dla dociekliwych)

W poprzednim podrozdziale pętla `for` przeszła po obiekcie `Zamowienie`, który nie miał `__iter__`. Funkcja `iter()` ma bowiem drugi sposób budowania iteratora: gdy obiekt nie ma `__iter__`, ale ma `__getitem__`, powstaje iterator wywołujący `__getitem__(0)`, `__getitem__(1)` i tak dalej, aż metoda zgłosi `IndexError`:

```python title="sekwencja-getitem.py"
class Kwadraty:
    """Kwadraty liczb od 0 do n-1, dostępne przez indeks."""

    def __init__(self, n):
        self.n = n

    def __getitem__(self, indeks):
        if not 0 <= indeks < self.n:
            raise IndexError(indeks)
        return indeks * indeks


kwadraty = Kwadraty(4)
print(kwadraty[2], list(kwadraty), 9 in kwadraty, 10 in kwadraty)
print(type(iter(kwadraty)).__name__)
```

```{ .text .no-copy }
4 [0, 1, 4, 9] True False
iterator
```

Ten **protokół sekwencji** pochodzi z czasów przed wprowadzeniem `__iter__` i nadal działa, ale w nowym kodzie definiujemy `__iter__` jawnie: jest szybszy, działa dla kolekcji bez indeksów całkowitych i jest rozpoznawany przez `collections.abc.Iterable`.

## Typowe błędy

Trzy pomyłki wracają w kodzie z iteratorami regularnie:

```python title="bledy-iteracji.py"
import itertools


class ZlaTalia:
    def __init__(self, karty):
        self._karty = list(karty)

    def __iter__(self):
        return self._karty


try:
    for karta in ZlaTalia(["As"]):
        print(karta)
except TypeError as e:
    print("TypeError:", e)

kwadraty = (x * x for x in range(4))
print(sum(kwadraty), sum(kwadraty))

nieskonczony = itertools.count(1)
print(list(itertools.islice(nieskonczony, 5)))
```

```{ .text .no-copy }
TypeError: iter() returned non-iterator of type 'list'
14 0
[1, 2, 3, 4, 5]
```

Pierwszy błąd: `__iter__` musi zwrócić iterator, a lista nim nie jest — poprawnie byłoby `return iter(self._karty)`. Drugi: wyrażenie generatorowe jest iteratorem, więc po pierwszym `sum()` jest wyczerpane i drugie zwraca zero; gdy dane są potrzebne dwukrotnie, zapisujemy je w liście. Trzeci: funkcja `list()` na nieskończonym iteratorze, jak `itertools.count()` z rozdziału 7, nigdy się nie kończy — ograniczamy go funkcją `itertools.islice()` albo warunkiem w pętli. Wspólna zasada: przed przekazaniem obiektu dalej warto wiedzieć, czy jest kolekcją, po której można przejść wielokrotnie, czy jednorazowym iteratorem.
