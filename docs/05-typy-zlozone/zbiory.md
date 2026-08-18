# Zbiory (set, frozenset)

## Set

Set to **nieuporządkowana, modyfikowalna** kolekcja niepowtarzających się obiektów — mogą to być obiekty różnych typów (o ile da się dla nich wyliczyć hash), także złożone. Utworzyć ją możemy za pomocą `set(<iter>)` — gdzie `<iter>` to wielkość iterowalna — albo wymieniając elementy w nawiasach klamrowych, np. `{1.23, 1, "a", 7+3j, (4,5)}`.

!!! warning "Pusty zapis {} tworzy słownik"
    Pusty zbiór uzyskamy wyłącznie przez `set()` — zapis `{}` tworzy pusty
    **słownik** (opisany na stronie [Słownik](slownik.md)):

    ```{ .python .no-copy }
    >>> type({})       # uwaga: to pusty słownik!
    <class 'dict'>
    >>> type(set())    # pusty zbiór tworzymy wyłącznie tak
    <class 'set'>
    ```

Podobnie jak przy słowniku, w zbiorze nie znajdą się jednocześnie `1` i `True` — ponieważ `1 == True`, Python traktuje je jako ten sam element (pozostaje pierwszy dodany).

Elementy obiektu set są niepowtarzalne, ale kolejność ich ułożenia jest **niegwarantowana**:

```{ .python .no-copy }
set("AbrakadAbra")   # {'k', 'd', 'a', 'A', 'r', 'b'}
```

Kolejność elementów w wynikach jest przykładowa — u czytelnika będzie inna i zmienia się między uruchomieniami interpretera (randomizacja funkcji hash dla łańcuchów znakowych).

Oczywiście można posortować, np. używając funkcji [sorted()](https://docs.python.org/3/howto/sorting.html), opisanej przy [liście](lista.md):

```{ .python .no-copy }
sorted(set("AbrakadAbra"))   # ['A', 'a', 'b', 'd', 'k', 'r']
```

ale — otrzymujemy w efekcie **listę**. Z definicji bowiem set jest zbiorem nieuporządkowanym. Jeśli więc uprzemy się i powyższe znowu zrzutujemy na set:

```{ .python .no-copy }
set(sorted(set("AbrakadAbra")))   # {'d', 'k', 'a', 'A', 'r', 'b'}
```

otrzymany set ma elementy w innej kolejności — co jest bez znaczenia dla typu set. Połączenie `sorted(set(...))` to zarazem najkrótszy idiom **usuwania duplikatów** z kolekcji z jednoczesnym uporządkowaniem wyniku: `sorted(set([1, 2, 2, 3, 3, 3]))` daje `[1, 2, 3]`. Inny ciekawy przykład (funkcja `enumerate()` — rozdział [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md)):

```{ .python .no-copy }
set(range(6))              # {0, 1, 2, 3, 4, 5}
list(enumerate(range(6)))  # [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
set(enumerate(range(6)))   # {(4, 4), (5, 5), (0, 0), (1, 1), (3, 3), (2, 2)}
```

Kilka prostych funkcji modyfikujących: `add(<element>)` — dodanie elementu, `clear()` — usunięcie wszystkich elementów, `remove(<element>)` — usunięcie wskazanego elementu (gdy elementu nie ma, zgłaszany jest `KeyError`; wariant `discard(<element>)` usuwa bez zgłaszania wyjątku), i ciekawostka: `pop()` — usunięcie **dowolnego (arbitralnego, choć nie losowego)** elementu; dla pustego setu zgłaszany jest `KeyError: 'pop from an empty set'`.

Zbiory można również budować **złożeniem zbiorowym** (ang. *set comprehension*) — analogicznym do złożeń listowych (opis w podrozdziale [Złożenia](zlozenia.md)):

```{ .python .no-copy }
>>> {x % 3 for x in range(10)}
{0, 1, 2}
>>> {x for x in range(20) if x % 2 == 0}
{0, 2, 4, 6, 8, 10, 12, 14, 16, 18}
```

## Operacje na zbiorach

Na obiektach set można zastosować znane z matematyki operacje: **unię** (sumę), **część wspólną** (przecięcie), **różnicę** i **różnicę symetryczną**. Operacje te można wywołać za pomocą funkcji lub operatorów:

```{ .python .no-copy }
s1 = {'a','A','z','Z','G','g'}
s2 = {'b','B','z','Z','G','k'}
s1.union(s2)                  # {'g', 'k', 'G', 'a', 'A', 'B', 'Z', 'z', 'b'}
s1 | s2                       # j.w.
s1.intersection(s2)           # {'z', 'G', 'Z'}
s1 & s2                       # j.w.
s1.difference(s2)             # {'g', 'A', 'a'}
s1 - s2                       # j.w.
s1.symmetric_difference(s2)   # {'g', 'k', 'A', 'b', 'B', 'a'}
s1 ^ s2                       # j.w.
```

!!! note "Funkcje vs operatory"
    Pomiędzy użyciem funkcji a operatorów jest subtelna różnica: w przypadku funkcji
    możemy jako argument podać wielkości iterowalne niebędące typu set — nastąpi
    automatyczna konwersja. W przypadku operatorów oba argumenty muszą być zbiorami
    (set lub frozenset).

Operacje dla operatorów można połączyć z przypisaniem: `|=` (funkcja update), `&=` (intersection_update), `-=` (difference_update) oraz `^=` (symmetric_difference_update) — wtedy wynik będzie przypisany do nazwy s1. Operacja z przypisaniem jest **wydajniejsza** niż wykonana osobno z późniejszym przypisaniem wyniku, ponieważ modyfikuje istniejący zbiór w miejscu (ang. *in-place*), bez tworzenia pośredniego obiektu z wynikiem — dotyczy to jednak tylko modyfikowalnego typu set (o frozenset — niżej). Analogiczne operatory `|` i `|=` dla słowników opisuje strona [Słownik](slownik.md).

Relacje pomiędzy elementami dwóch kontenerów set można sprawdzić za pomocą:

- `s1.isdisjoint(s2)` — jeśli brak elementów wspólnych, zwraca True
- `s1.issubset(s2)` — prawda, jeśli wszystkie elementy s1 są podzbiorem s2; można też zapisać relacją `<=`
- `s1.issuperset(s2)` — prawda, jeśli wszystkie elementy s2 są podzbiorem s1; relacja `>=`

```{ .python .no-copy }
s1 = {2,1}
s2 = {1,2,3,4}
s1 <= s2   # True
s1 >= s2   # False
s2 >= s1   # True
```

## Frozenset

Typ frozenset odpowiada typowi set, ale jest **niemodyfikowalny**. Funkcje modyfikujące (add, pop, clear…) są w typie frozenset nieobecne.

!!! warning "Pozorna modyfikacja"
    Nie dajmy się zwieść zapisowi typu `f &= s` — nie modyfikuje on obiektu f,
    tylko tworzy **nowy**.

```{ .python .no-copy }
>>> f = frozenset(["a", "b", "c", "d"])
>>> f
frozenset({'b', 'c', 'd', 'a'})
>>> f.add("e")
Traceback (most recent call last):
  File "<python-input-2>", line 1, in <module>
    f.add("e")
    ^^^^^
AttributeError: 'frozenset' object has no attribute 'add'
>>> s = {"b", "c", "x"}
>>> id(f)
2333498599776
>>> f &= s
>>> f
frozenset({'b', 'c'})
>>> id(f)                # inny adres — powstał nowy obiekt
2333494279104
```

Kolejność wypisywanych elementów zbioru oraz wartości `id()` zależą od konkretnej sesji interpretera — przy ponownym uruchomieniu będą inne.
