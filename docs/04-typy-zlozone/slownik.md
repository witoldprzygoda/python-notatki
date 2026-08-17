# Słownik (dict)

Typ słownikowy reprezentuje rodzaj **tablicy skojarzeniowej**. Każdy element to para: klucz–wartość. Klucz musi być typem niemodyfikowalnym (precyzyjniej: takim, dla którego możliwe jest wyliczenie wartości hash). Wartość (może to być złożony obiekt) jest modyfikowalna — stąd typ dict należy do typów modyfikowalnych.

## Tworzenie słownika

Obiekt dict tworzymy za pomocą pary nawiasów `{ }` lub za pomocą `dict()`:

```python
d1 = { }      # pusty
d1 = dict()
```

Obiekt wypełniamy parami klucz–wartość następująco:

```python
d1 = { 'a': 'alpha', 123: 1.435, True: 'prawda'}   # można mieszać typy
```

Można też utworzyć z listy krotek:

```python
d1 = dict([('a', 'AAA'), ('b','BBB')])   # powstaje {'a': 'AAA', 'b': 'BBB'}
```

Natomiast gdy klucze są prostymi stringami, można:

```python
d1 = dict(a='alpha', a123=1.435, klucz3='prawda')
# powstaje {'a': 'alpha', 'a123': 1.435, 'klucz3': 'prawda'}
```

Słownik można utworzyć też za pomocą składni **dictionary comprehension** (złożenie słownikowe), która jest sposobem na elegancki i zwięzły zapis. Minimalna składnia:

```{ .text .no-copy }
dictionary = {key: value for vars in iterable}
```

Za pomocą takiej składni można przeliczyć zawartość jednego słownika do drugiego; w składni można dodać warunki selekcji, również po stronie wielkości tworzących słownik (konstrukcja if… else).

<!-- TODO: przykłady z PDF (zrzuty): dictionary comprehension — 4 przykłady -->

## Dostęp i modyfikacja

Elementy (pary) obiektu dict wypełnione są w kolejności ich dodawania (co jest **gwarantowane od Python 3.7**) — nie są posortowane; ich identyfikacja odbywa się poprzez wyliczoną dla każdego klucza wartość hash. Klucz nie może się powtórzyć (jest unikatowy, jak element w typie set). Nie da się odwołać do danej pary poprzez indeks — z prostego powodu: indeks (typ int) również można zastosować jako klucz.

Najbardziej oczywistym sposobem odczytania wartości odpowiadającej danemu kluczowi jest składnia `d1[klucz1]`. W przypadku braku klucza zgłoszony zostaje wyjątek `KeyError`. Aby tego uniknąć, można odpytać za pomocą składni połączonej z odczytaniem poprzez operator and:

```python
klucz1 in d1 and d1[klucz1]   # jeśli klucza nie ma, d1[klucz1] nie będzie wywołane
```

Dodanie kolejnej pary: `d1[klucz1] = wartosc1`. Dla istniejącego wcześniej klucza taki zapis prowadzi do **aktualizacji** wartości. Kolejności elementów w słowniku nie można zmienić „in place” — gdybyśmy chcieli (np. posortować po kluczu), musielibyśmy usuwać parę (del) i dodawać ponownie (dodana ląduje na końcu), albo wykonać sortowanie poprzez uzyskanie dynamicznego widoku słownika.

## Metody słownika

**clear()** — usuwa zawartość (pusty słownik).

**get(&lt;klucz&gt;[, &lt;domyślny&gt;])** — bezpieczny sposób odpytania: jeśli klucza nie ma, zwrócone zostaje None (lub wartość &lt;domyślny&gt;, którą może być nawet wywołanie funkcji):

```python
print(d1.get('aa'))                            # None
print(d1.get('aa', "masakra".upper()))         # MASAKRA
print(d1.get('aa', print("masakra".upper())))  # MASAKRA None — bo print nic nie zwraca
```

**setdefault(&lt;klucz&gt;[, &lt;domyślny&gt;])** — zwraca wartość odpowiadającą kluczowi, a jeśli takiego w słowniku nie ma — umieszcza go z wartością &lt;domyślny&gt; i ją zwraca. Jeśli mamy słownik d1 bez klucza 123, a chcemy z tym kluczem związać pustą listę:

```python
d1.setdefault(123, [])
```

i co więcej — ponieważ takie wywołanie zwraca obiekt &lt;domyślny&gt; (tu: pustą listę), to od razu możemy na niej wywołać jakąś funkcję:

```python
d1.setdefault(123, []).extend(range(10,15))   # {123: [10, 11, 12, 13, 14]}
```

**items(), keys(), values()** — ważne z punktu widzenia pozyskiwania widoków oraz selekcji. `d1.items()` zwraca obiekt dict_items zawierający krotki (klucz, wartość), który łatwo rzutować na listę. `list(d1.keys())` daje listę wszystkich kluczy, `list(d1.values())` — wszystkich wartości. Prosta pętla po kluczach i wartościach — oraz wariant bez items(), gdzie w pętli dostajemy klucze:

<!-- TODO: przykłady z PDF (zrzuty): pętla z items(); pętla po kluczach -->

**pop(&lt;klucz&gt;[, &lt;domyślny&gt;])** — usuwa i zwraca element; jeśli klucza nie ma i nie zdefiniowano &lt;domyślny&gt;, zgłaszany jest `KeyError`.

**popitem()** — usuwa i zwraca krotkę z **ostatnią** parą w słowniku; dla pustego słownika zgłasza KeyError. Przed Python 3.6, gdy kolejność nie była gwarantowana, funkcja zwracała losową parę.

**update(&lt;obiekt&gt;)** — łączy (dodaje) do d1 elementy ze słownika &lt;obiekt&gt;. Dla kluczy już występujących wartość jest aktualizowana, dla nowych — para jest dodawana. Podobnie jak przy tworzeniu słownika, argumentem może być lista z krotkami lub argumenty w zapisie `kluczA=wartośćA, kluczB=wartośćB`.
