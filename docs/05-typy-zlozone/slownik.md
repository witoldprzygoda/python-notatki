# Słownik (dict)

Typ słownikowy reprezentuje rodzaj **tablicy skojarzeniowej**. Każdy element to para: klucz–wartość. Klucz musi być typem niemodyfikowalnym (precyzyjniej: takim, dla którego możliwe jest wyliczenie wartości hash — pojęcie wprowadzone przy [krotce](krotka.md)). Wartość (może to być złożony obiekt) jest modyfikowalna — stąd typ dict należy do typów modyfikowalnych.

## Tworzenie słownika

Obiekt dict tworzymy za pomocą pary nawiasów `{ }` lub za pomocą `dict()`:

```{ .python .no-copy }
d1 = { }      # pusty
d1 = dict()
```

Obiekt wypełniamy parami klucz–wartość następująco:

```{ .python .no-copy }
d1 = { 'a': 'alpha', 123: 1.435, True: 'prawda'}   # można mieszać typy
```

!!! note "True czy 1?"
    Ponieważ `True == 1` i `hash(True) == hash(1)` (bool jest podtypem int —
    rozdział [3. Nazwy i typy](../03-nazwy-typy/typy-proste.md)), klucze `True`
    i `1` są dla słownika **tym samym kluczem**. W powyższym przykładzie `d1[1]`
    zwróci `'prawda'`, a literał z oboma kluczami zachowa tylko jeden wpis:

    ```{ .python .no-copy }
    >>> d = {True: "prawda", 1: "jeden"}
    >>> d               # klucz zachowuje pierwszą postać, wartość — ostatnią
    {True: 'jeden'}
    >>> len(d)
    1
    ```

Można też utworzyć z listy krotek:

```{ .python .no-copy }
d1 = dict([('a', 'AAA'), ('b','BBB')])   # powstaje {'a': 'AAA', 'b': 'BBB'}
```

Parę równoległych sekwencji łatwo skleić w takie krotki funkcją `zip()` (opisaną przy [krotce](krotka.md)):

```{ .python .no-copy }
>>> imiona = ["Ala", "Bartek", "Celina"]
>>> wiek = [21, 23, 22]
>>> dict(zip(imiona, wiek))
{'Ala': 21, 'Bartek': 23, 'Celina': 22}
```

Natomiast gdy klucze są prostymi stringami, można:

```{ .python .no-copy }
d1 = dict(a='alpha', a123=1.435, klucz3='prawda')
# powstaje {'a': 'alpha', 'a123': 1.435, 'klucz3': 'prawda'}
```

Zapis `a='alpha'` to argumenty nazwane (ang. *keyword arguments*) — konstruktor `dict()` pakuje je w słownik; dlatego właśnie klucze muszą tu być poprawnymi nazwami. Ten sam mechanizm (`**kwargs`), tym razem od strony definiowania własnych funkcji, omawiamy w rozdziale [6. Funkcje](../06-funkcje/argumenty-i-parametry.md#parametr-kwargs).

Słownik można utworzyć też za pomocą **złożenia słownikowego** (ang. *dictionary comprehension*), analogicznego do złożeń listowych (opis w podrozdziale [Złożenia](zlozenia.md)). Minimalna składnia:

```{ .text .no-copy }
dictionary = {klucz: wartość for zmienna in iterowalne}
```

```{ .python .no-copy }
>>> kwadraty = {x: x**2 for x in range(6)}
>>> kwadraty
{0: 0, 1: 1, 2: 4, 3: 9, 4: 16, 5: 25}
```

Za pomocą takiej składni można przeliczyć zawartość jednego słownika do drugiego (pary klucz–wartość zwraca metoda `items()`, omawiana niżej):

```{ .python .no-copy }
>>> ceny_netto = {"kawa": 10.0, "herbata": 8.0}
>>> {t: round(c * 1.23, 2) for t, c in ceny_netto.items()}
{'kawa': 12.3, 'herbata': 9.84}
```

W składni można dodać warunki selekcji:

```{ .python .no-copy }
>>> oceny = {"Ala": 5, "Bartek": 2, "Celina": 4}
>>> {k: v for k, v in oceny.items() if v >= 3}
{'Ala': 5, 'Celina': 4}
```

również po stronie wielkości tworzących słownik (konstrukcja if… else):

```{ .python .no-copy }
>>> {k: ("zdał" if v >= 3 else "nie zdał") for k, v in oceny.items()}
{'Ala': 'zdał', 'Bartek': 'nie zdał', 'Celina': 'zdał'}
```

## Dostęp i modyfikacja

Elementy (pary) obiektu dict wypełnione są w kolejności ich dodawania (co jest **gwarantowane od Python 3.7**) — nie są posortowane; ich identyfikacja odbywa się poprzez wyliczoną dla każdego klucza wartość hash. Klucz nie może się powtórzyć (jest unikatowy, jak element w typie set). Nie da się odwołać do danej pary poprzez indeks — z prostego powodu: indeks (typ int) również można zastosować jako klucz.

Najbardziej oczywistym sposobem odczytania wartości odpowiadającej danemu kluczowi jest składnia `d1[klucz1]`. W przypadku braku klucza zgłoszony zostaje wyjątek `KeyError`. Warto wiedzieć, że operator `in` sprawdza w słowniku **klucze**, nie wartości:

```{ .python .no-copy }
>>> d = {"imie": "Ala", "wiek": 21}
>>> "imie" in d           # in sprawdza klucze…
True
>>> "Ala" in d            # …a nie wartości
False
>>> "Ala" in d.values()   # wartości — poprzez widok values()
True
```

Aby uniknąć wyjątku KeyError, można odpytać za pomocą składni połączonej z odczytaniem poprzez operator and:

```{ .python .no-copy }
klucz1 in d1 and d1[klucz1]   # jeśli klucza nie ma, d1[klucz1] nie będzie wywołane
```

Gdy klucza nie ma, wartością całego wyrażenia jest `False` (a nie wartość ze słownika); trzeba też pamiętać, że dla wartości o logicznej wartości False (0, pusty napis, pusta lista) wynik jest nieodróżnialny od braku klucza — bezpieczniejszą alternatywą jest metoda `get()`, opisana niżej.

Dodanie kolejnej pary: `d1[klucz1] = wartosc1`. Dla istniejącego wcześniej klucza taki zapis prowadzi do **aktualizacji** wartości. Kolejności elementów w słowniku nie można zmienić w miejscu (ang. *in-place*) — gdybyśmy chcieli (np. posortować po kluczu), musielibyśmy usuwać parę (del) i dodawać ponownie (dodana ląduje na końcu), albo wykonać sortowanie poprzez uzyskanie dynamicznego widoku słownika.

## Metody słownika

**clear()** — usuwa zawartość (pusty słownik).

**get(&lt;klucz&gt;[, &lt;domyślny&gt;])** — bezpieczny sposób odpytania: jeśli klucza nie ma, zwrócone zostaje None (lub wartość &lt;domyślny&gt;, którą może być nawet wywołanie funkcji):

```{ .python .no-copy }
print(d1.get('aa'))                            # None
print(d1.get('aa', "masakra".upper()))         # MASAKRA
print(d1.get('aa', print("masakra".upper())))  # wypisze MASAKRA, potem None —
                                               # bo wewnętrzny print zwraca None
```

Uwaga: wyrażenie podane jako wartość domyślna jest ewaluowane **zawsze** — również wtedy, gdy klucz istnieje w słowniku.

**setdefault(&lt;klucz&gt;[, &lt;domyślny&gt;])** — zwraca wartość odpowiadającą kluczowi, a jeśli takiego w słowniku nie ma — umieszcza go z wartością &lt;domyślny&gt; i ją zwraca. Jeśli mamy słownik d1 bez klucza 123, a chcemy z tym kluczem związać pustą listę:

```{ .python .no-copy }
d1.setdefault(123, [])
```

i co więcej — ponieważ takie wywołanie zwraca obiekt &lt;domyślny&gt; (tu: pustą listę), to od razu możemy na niej wywołać jakąś funkcję:

```{ .python .no-copy }
d1.setdefault(123, []).extend(range(10,15))   # {123: [10, 11, 12, 13, 14]}
```

**items(), keys(), values()** — zwracają **widoki** słownika (ang. *view objects*: dict_items, dict_keys, dict_values). Widok jest **dynamiczny** — odzwierciedla późniejsze zmiany słownika; chcąc utrwalić jego zawartość, rzutujemy go na listę: `list(d1.items())` daje listę krotek (klucz, wartość), `list(d1.keys())` — listę wszystkich kluczy, `list(d1.values())` — wszystkich wartości. Prosta pętla po kluczach i wartościach — oraz wariant bez items(), gdzie w pętli dostajemy klucze:

```{ .python .no-copy }
>>> d1 = {'a': 'alpha', 'b': 'beta', 'g': 'gamma'}
>>> for klucz, wartosc in d1.items():
...     print(klucz, '->', wartosc)
...
a -> alpha
b -> beta
g -> gamma
>>> for klucz in d1:
...     print(klucz, '->', d1[klucz])
...
a -> alpha
b -> beta
g -> gamma
```

**pop(&lt;klucz&gt;[, &lt;domyślny&gt;])** — usuwa i zwraca element; jeśli klucza nie ma i nie zdefiniowano &lt;domyślny&gt;, zgłaszany jest `KeyError`.

**popitem()** — usuwa i zwraca krotkę z **ostatnią** parą w słowniku (kolejność LIFO, gwarantowana od Python 3.7); dla pustego słownika zgłasza KeyError. We wcześniejszych wersjach, gdy kolejność nie była gwarantowana, funkcja zwracała dowolną (arbitralną) parę.

**update(&lt;obiekt&gt;)** — łączy (dodaje) do d1 elementy ze słownika &lt;obiekt&gt;. Dla kluczy już występujących wartość jest aktualizowana, dla nowych — para jest dodawana. Podobnie jak przy tworzeniu słownika, argumentem może być lista z krotkami lub argumenty w zapisie `kluczA=wartośćA, kluczB=wartośćB`.

Od Pythona 3.9 łączenie słowników umożliwiają również operatory: `|` tworzy **nowy** słownik z połączenia dwóch, a `|=` działa jak update() — modyfikuje słownik po lewej stronie. Przy powtórzonym kluczu wygrywa wartość z prawego operandu:

```{ .python .no-copy }
>>> a = {'x': 1, 'y': 2}
>>> b = {'y': 3, 'z': 4}
>>> a | b        # nowy słownik
{'x': 1, 'y': 3, 'z': 4}
>>> a |= b       # aktualizacja a „w miejscu”, jak a.update(b)
>>> a
{'x': 1, 'y': 3, 'z': 4}
```

Symetryczne operatory `|` i `|=` dla zbiorów opisuje strona [Zbiory](zbiory.md).
