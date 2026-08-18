# Zbiory: set i frozenset

## Set

Set to **nieuporządkowana, modyfikowalna** kolekcja niepowtarzających się obiektów — mogą to być obiekty różnych typów, także złożone. Utworzyć ją możemy za pomocą `set(<iter>)` lub `{ }`, gdzie <iter> to wielkość iterowalna.

Przykład z różnymi typami: `{1.23, 1, "a", 7+3j, True, (4,5)}`

Elementy obiektu set są niepowtarzalne, ale kolejność ich ułożenia jest **niegwarantowana**:

```python
set("AbrakadAbra")   # {'k', 'd', 'a', 'A', 'r', 'b'}
```

Oczywiście można posortować, np. używając funkcji [sorted()](https://docs.python.org/3/howto/sorting.html), działającej analogicznie do składowej listy sort():

```python
sorted(set("AbrakadAbra"))   # ['A', 'a', 'b', 'd', 'k', 'r']
```

ale — otrzymujemy w efekcie **listę**. Z definicji bowiem set jest zbiorem nieuporządkowanym. Jeśli więc uprzemy się i powyższe znowu zrzutujemy na set:

```python
set(sorted(set("AbrakadAbra")))   # {'d', 'k', 'a', 'A', 'r', 'b'}
```

otrzymany set ma elementy w innej kolejności — co jest bez znaczenia dla typu set. Inny ciekawy przykład:

```python
set(range(6))              # {0, 1, 2, 3, 4, 5}
list(enumerate(range(6)))  # [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
set(enumerate(range(6)))   # {(4, 4), (5, 5), (0, 0), (1, 1), (3, 3), (2, 2)}
```

Kilka prostych funkcji modyfikujących: `add(<element>)` — dodanie elementu, `clear()` — usunięcie wszystkich elementów, `remove(<element>)` — usunięcie wskazanego elementu, i ciekawostka: `pop()` — usunięcie **dowolnego, losowego** elementu; dla pustego setu zgłaszany jest `KeyError: 'pop from an empty set'`.

## Operacje na zbiorach

Na obiektach set można zastosować znane z matematyki operacje: **unię** (sumę), **część wspólną** (przecięcie), **różnicę** i **różnicę symetryczną**. Operacje te można wywołać za pomocą funkcji lub operatorów:

```python
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
    automatyczna konwersja. W przypadku operatorów oba argumenty muszą być typu set.

Operacje dla operatorów można połączyć z przypisaniem: `|=` (funkcja update), `&=` (intersection_update), `-=` (difference_update) oraz `^=` (symmetric_difference_update) — wtedy wynik będzie przypisany do nazwy s1. Operacja z przypisaniem jest **wydajniejsza** niż wykonana osobno z późniejszym przypisaniem wyniku.

Relacje pomiędzy elementami dwóch kontenerów set można sprawdzić za pomocą:

- `s1.isdisjoint(s2)` — jeśli brak elementów wspólnych, zwraca True
- `s1.issubset(s2)` — prawda, jeśli wszystkie elementy s1 są podzbiorem s2; można też zapisać relacją `<=`
- `s1.issuperset(s2)` — prawda, jeśli wszystkie elementy s2 są podzbiorem s1; relacja `>=`

```python
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

<!-- TODO: przykłady z PDF (zrzuty): utworzenie frozenset; f &= s i adresy -->
