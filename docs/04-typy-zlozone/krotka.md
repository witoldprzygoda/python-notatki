# Krotka (tuple)

Krotka (tuple) jest kontenerem sekwencyjnym, który jest **niemodyfikowalny**. Zatem obiekty tuple posiadają wyliczoną wartość hash i mogą być stosowane wszędzie tam, gdzie jest wymagany obiekt niemodyfikowalny — na przykład jako klucz w typie słownikowym (dict).

<!-- TODO: przykład z PDF (zrzut): pusta krotka i identyczny hash -->

Można by się zastanawiać, jaki jest sens obiektu pustego, którego nie można zmodyfikować. Jednak wszędzie tam, gdzie spodziewana jest krotka (np. w funkcji można zapisać sekwencję pozycyjnych argumentów za pomocą krotki), powinna również istnieć możliwość przekazania pustego obiektu — stąd istnienie pustej krotki ma jak najbardziej sens.

Krotka może zawierać, podobnie jak lista, obiekty różnych typów:

```python
krotka1 = (1, 1.23, 'stxt', 4+1j, True, None)
```

Można w tym zapisie opuścić nawiasy:

```python
krotka1 = 1, 2, 3, 4   # powstaje (1, 2, 3, 4)
```

!!! warning "Krotka jednoelementowa"
    Zapis `k1 = (1)` prowadzi do utworzenia obiektu typu **int**. Ażeby była to krotka
    jednoelementowa (singleton), trzeba zastosować niezbyt estetyczny przecinek na
    końcu: `k1 = 1,` albo `k1 = (1,)`.

Na tuplach można stosować dostęp za pomocą indeksów, również selekcję — tak samo jak na liście. Dla `krotka1 = 1, 2, 3, 4` zapis `krotka1[0:1]` da wynik `(1,)` — odwołując się przez indeks(y), również otrzymujemy krotkę (może być pusta). Wykonując slicing na krotce, otrzymujemy **nową** krotkę (pod innym adresem). Odwołanie się indeksem poza zakres powoduje zgłoszenie `IndexError: tuple index out of range`.

Za pomocą funkcji `k1.count(<obiekt>)` można odpytać, ile razy <obiekt> występuje w danej krotce.

Krotki mogą posiadać zagnieżdżone kolejne elementy, również krotki. Zapis `k1 = (1,),` spowoduje utworzenie `((1,),)`. Jeśli krotka składa się z elementów niemodyfikowalnych, np.:

```python
k1 = 'abc', (1, 1.23), (False, True)   # powstaje ('abc', (1, 1.23), (False, True))
```

to nadal pozostaje obiektem, dla którego wyliczony jest hash. Jeśli jednak uczynimy elementem krotki obiekt typu **modyfikowalnego** (np. listę), to dla takiej krotki nie można już wyliczyć hash (i tym samym nie można jej stosować tam, gdzie hash jest wymagany).

W przypadku jak wyżej nie możemy modyfikować elementów krotki (tuple nie ma operatora przypisania), ale można dostać się do zawartości obiektu modyfikowalnego (np. listy) i jego zawartość dowolnie zmienić.

<!-- TODO: przykłady z PDF (zrzuty): hash krotki z listą; modyfikacja listy w krotce -->

Niech nas nie zwiedzie, że możemy napisać np.:

```python
tuple1 = ()        # pierwsza krotka
tuple1 = (1,2,3)   # druga, zupełnie nowa krotka
```

bo to będzie zupełnie inny, nowy obiekt, a nie modyfikacja poprzedniej pustej krotki.

Krotkę (podobnie jak listę) utworzymy też przez rzutowanie:

```python
k1 = tuple("abcd")        # utworzy ('a', 'b', 'c', 'd')
k1 = tuple(range(0,10))   # utworzy (0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
```

Zatem jedną z możliwości „modyfikowania krotki” jest wykonanie rzutowania na listę, zrobienie modyfikacji i ponowne rzutowanie na tuple — finalnie dostaniemy całkowicie inną krotkę niż na początku.

Oprócz rzutowania, krotkę można też otrzymać poprzez rozpakowanie listy:

```python
l = list('abrakadabra')   # ['a', 'b', 'r', 'a', 'k', 'a', 'd', 'a', 'b', 'r', 'a']
t = (*l,)                 # ('a', 'b', 'r', 'a', 'k', 'a', 'd', 'a', 'b', 'r', 'a')
```

Natomiast aby z powrotem uzyskać string z krotki, można zapisać: `str = ''.join(t)`.

Iterowanie po elementach krotki jest podobne jak dla listy.

<!-- TODO: przykłady z PDF (zrzuty): lista z krotkami; rozpakowywanie w pętli -->
