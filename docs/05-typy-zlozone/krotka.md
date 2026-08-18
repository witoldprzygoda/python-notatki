# Krotka (tuple)

Krotka (tuple) jest kontenerem sekwencyjnym, który jest **niemodyfikowalny**. Zatem dla obiektów tuple — o ile ich elementy również są niemodyfikowalne, o czym dalej — można wyliczyć wartość skrótu (ang. *hash*): liczbę identyfikującą zawartość obiektu, obliczaną funkcją wbudowaną `hash()` i wymaganą m.in. od kluczy słownika oraz elementów zbioru. Krotki mogą więc być stosowane wszędzie tam, gdzie jest wymagany obiekt niemodyfikowalny — na przykład jako klucz w typie słownikowym (dict):

```{ .python .no-copy }
>>> t1 = ()
>>> type(t1)
<class 'tuple'>
>>> t2 = tuple()
>>> t1 == t2
True
>>> hash(t1)
5740354900026072187
>>> hash(t2)
5740354900026072187
```

Konkretna liczba zależy od platformy, ale dla wszystkich pustych krotek jest identyczna — to właśnie czyni je wymiennymi wszędzie tam, gdzie wymagany jest hash.

Można by się zastanawiać, jaki jest sens obiektu pustego, którego nie można zmodyfikować. Jednak wszędzie tam, gdzie spodziewana jest krotka (np. sekwencja pozycyjnych argumentów funkcji trafia do krotki — mechanizm `*args`, który omówimy w rozdziale o funkcjach), powinna również istnieć możliwość przekazania pustego obiektu — stąd istnienie pustej krotki ma jak najbardziej sens. <!-- TODO: link po powstaniu rozdziału o funkcjach -->

Krotka może zawierać, podobnie jak lista, obiekty różnych typów:

```{ .python .no-copy }
krotka1 = (1, 1.23, 'stxt', 4+1j, True, None)
```

Można w tym zapisie opuścić nawiasy:

```{ .python .no-copy }
krotka1 = 1, 2, 3, 4   # powstaje (1, 2, 3, 4)
```

!!! warning "Krotka jednoelementowa"
    Zapis `k1 = (1)` prowadzi do utworzenia obiektu typu **int**. Ażeby była to krotka
    jednoelementowa (singleton), trzeba zastosować niezbyt estetyczny przecinek na
    końcu: `k1 = 1,` albo `k1 = (1,)`.

Na tuplach można stosować dostęp za pomocą indeksów, również selekcję (slicing, opisany w rozdziale [3. Nazwy i typy](../03-nazwy-typy/typy-proste.md)) — tak samo jak na liście. Dla `krotka1 = 1, 2, 3, 4` zapis `krotka1[0:1]` da wynik `(1,)` — odwołując się przez indeks(y), również otrzymujemy krotkę (może być pusta). Wycinek częściowy krotki to nowy obiekt; pełny wycinek `krotka1[:]` zwraca natomiast **ten sam** obiekt — skoro krotki nie można zmodyfikować, kopiowanie jest zbędne (inaczej niż przy listach). Odwołanie się indeksem poza zakres powoduje zgłoszenie `IndexError: tuple index out of range`.

Za pomocą funkcji `k1.count(<obiekt>)` można odpytać, ile razy `<obiekt>` występuje w danej krotce.

Krotki mogą posiadać zagnieżdżone kolejne elementy, również krotki. Zapis `k1 = (1,),` spowoduje utworzenie `((1,),)`. Jeśli krotka składa się z elementów niemodyfikowalnych, np.:

```{ .python .no-copy }
k1 = 'abc', (1, 1.23), (False, True)   # powstaje ('abc', (1, 1.23), (False, True))
```

to nadal pozostaje obiektem, dla którego można wyliczyć hash. Jeśli jednak uczynimy elementem krotki obiekt typu **modyfikowalnego** (np. listę), to dla takiej krotki nie można już wyliczyć hash (i tym samym nie można jej stosować tam, gdzie hash jest wymagany).

W przypadku jak wyżej nie możemy modyfikować elementów krotki (tuple nie ma operatora przypisania), ale można dostać się do zawartości obiektu modyfikowalnego (np. listy) i jego zawartość dowolnie zmienić:

```{ .python .no-copy }
>>> k1 = 'abc', (1, 1.23), (False, True)
>>> hash(k1)
-1447288345422647273
>>> k2 = ('abc', [1, 1.23], (False, True))
>>> hash(k2)
Traceback (most recent call last):
  File "<python-input-3>", line 1, in <module>
    hash(k2)
    ~~~~^^^^
TypeError: unhashable type: 'list'
>>> k2[1] = [9, 9]
Traceback (most recent call last):
  File "<python-input-4>", line 1, in <module>
    k2[1] = [9, 9]
    ~~^^^
TypeError: 'tuple' object does not support item assignment
>>> k2[1][0] = 999
>>> k2[1].append("nowy")
>>> k2
('abc', [999, 1.23, 'nowy'], (False, True))
```

Konkretna wartość hash jest w każdej sesji interpretera inna — dla obiektów zawierających łańcuchy znakowe jest ona losowana przy każdym uruchomieniu.

Niech nas nie zwiedzie, że możemy napisać np.:

```{ .python .no-copy }
tuple1 = ()        # pierwsza krotka
tuple1 = (1,2,3)   # druga, zupełnie nowa krotka
```

bo to będzie zupełnie inny, nowy obiekt, a nie modyfikacja poprzedniej pustej krotki.

Krotkę (podobnie jak listę) utworzymy też przez rzutowanie:

```{ .python .no-copy }
k1 = tuple("abcd")        # utworzy ('a', 'b', 'c', 'd')
k1 = tuple(range(0,10))   # utworzy (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
```

Zatem jedną z możliwości „modyfikowania krotki” jest wykonanie rzutowania na listę, zrobienie modyfikacji i ponowne rzutowanie na tuple — finalnie dostaniemy całkowicie inną krotkę niż na początku.

## Pakowanie i rozpakowywanie

Zapis `krotka1 = 1, 2, 3, 4` to **pakowanie** (ang. *packing*) wartości w krotkę. Operacja odwrotna — **rozpakowanie** (ang. *unpacking*) — przypisuje elementy do osobnych nazw; ich liczba musi odpowiadać liczbie elementów:

```{ .python .no-copy }
>>> t = 1, 2, 3
>>> a, b, c = t
>>> a, c
(1, 3)
```

Tak właśnie działa poznana w rozdziale [3. Nazwy i typy](../03-nazwy-typy/nazwy-i-slowa-kluczowe.md) zamiana wartości `a, b = b, a` — po prawej stronie powstaje krotka, natychmiast rozpakowywana po lewej. Jeśli nazw jest mniej niż elementów, jedną z nich można poprzedzić gwiazdką — to **rozszerzone rozpakowanie** (ang. *extended unpacking*); nazwa z gwiazdką zbiera pozostałe elementy zawsze do **listy**, niezależnie od typu źródła:

```{ .python .no-copy }
>>> pierwszy, *reszta = [1, 2, 3, 4, 5]
>>> pierwszy, reszta
(1, [2, 3, 4, 5])
>>> *poczatek, ostatni = [1, 2, 3, 4, 5]
>>> poczatek, ostatni
([1, 2, 3, 4], 5)
>>> a, *srodek, z = (10, 20, 30, 40)
>>> srodek
[20, 30]
```

Ten sam symbol `*` użyty w wyrażeniu rozpakowuje sekwencję na osobne elementy — dzięki temu krotkę można otrzymać poprzez rozpakowanie listy:

```{ .python .no-copy }
l = list('abrakadabra')   # ['a', 'b', 'r', 'a', 'k', 'a', 'd', 'a', 'b', 'r', 'a']
t = (*l,)                 # ('a', 'b', 'r', 'a', 'k', 'a', 'd', 'a', 'b', 'r', 'a')
```

Natomiast aby z powrotem uzyskać string z krotki, można zapisać: `napis = ''.join(t)`. Gwiazdka w wywołaniu funkcji rozpakowuje sekwencję na osobne argumenty — mechanizm ten, wraz z parametrami `*args`, omówimy w rozdziale o funkcjach. <!-- TODO: link po powstaniu rozdziału o funkcjach -->

Iterowanie po elementach krotki jest podobne jak dla listy; pary (i dłuższe krotki) można rozpakowywać bezpośrednio w nagłówku pętli for — dokładnie tak, jak przy `enumerate()` w rozdziale [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md):

```{ .python .no-copy }
>>> pary = [(1, 'jeden'), (2, 'dwa'), (3, 'trzy')]
>>> for para in pary:
...     print(para)
...
(1, 'jeden')
(2, 'dwa')
(3, 'trzy')
>>> for liczba, slowo in pary:
...     print(liczba, '->', slowo)
...
1 -> jeden
2 -> dwa
3 -> trzy
```

## Funkcja zip()

Zapowiedziana przy pętlach (rozdział [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md)) funkcja `zip()` łączy elementy kilku sekwencji w krotki — i-ta krotka zawiera i-te elementy argumentów, a łączenie kończy się wraz z najkrótszą sekwencją:

```{ .python .no-copy }
>>> imiona = ["Ala", "Bartek", "Celina"]
>>> wiek = [21, 23, 22]
>>> for imie, lata in zip(imiona, wiek):
...     print(f"{imie}: {lata}")
...
Ala: 21
Bartek: 23
Celina: 22
>>> list(zip([1, 2, 3], "ab"))   # ucina do krótszej sekwencji
[(1, 'a'), (2, 'b')]
>>> pary = [(1, 'a'), (2, 'b'), (3, 'c')]
>>> liczby, litery = zip(*pary)  # operacja odwrotna: rozdzielenie par
>>> liczby
(1, 2, 3)
```

Wynikiem `zip()` jest jednorazowy **iterator** (tak jak przy `enumerate()`), dlatego w pętli for pary zwykle od razu rozpakowujemy. Od Pythona 3.10 wywołanie `zip(a, b, strict=True)` zgłasza wyjątek `ValueError`, gdy sekwencje mają różne długości — przydatne, gdy ucinanie do najkrótszej maskowałoby błąd w danych.

!!! note "Ciekawostka: transpozycja macierzy"
    Połączenie zip() z rozpakowaniem `*` transponuje „macierz” zbudowaną z list
    (zamienia wiersze z kolumnami): `list(zip(*[[1, 2], [3, 4], [5, 6]]))` daje
    `[(1, 3, 5), (2, 4, 6)]`. Tablice wielowymiarowe omawia strona
    [Referencje i kopiowanie](referencje-i-kopiowanie.md).
