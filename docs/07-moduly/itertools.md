# Moduł itertools

Ten podrozdział ma charakter uzupełniający: nie wprowadza pojęć, od których zależą dalsze rozdziały, i można do niego wrócić później — na przykład wtedy, gdy własne funkcje generatorowe zaczną powtarzać te same schematy. Warto jednak wiedzieć, że schematy te mają już gotowe, sprawdzone implementacje.

W podrozdziale [Funkcje generatorowe](../06-funkcje/funkcje-generatorowe.md) napisaliśmy funkcję generatorową `naturalne()` o nieskończonym ciągu wartości, funkcję `polacz()` łączącą kilka obiektów iterowalnych i potoki, w których każdy etap przetwarza elementy pojedynczo. Moduł `itertools` — wbudowany w interpreter i zaimplementowany w języku C — dostarcza gotowe odpowiedniki tych i wielu innych schematów. Wszystkie jego funkcje zwracają **iteratory**: produkują wartości na żądanie i są jednorazowe, jak obiekty generatorów z sekcji [Leniwość i jednorazowość](../06-funkcje/funkcje-generatorowe.md#leniwosc-i-jednorazowosc), dlatego w przykładach materializujemy je funkcją `list()`, a w programach łączymy z pętlą `for`, funkcjami `map()` i `filter()` oraz wyrażeniami generatorowymi. Nie omawiamy modułu w całości — wybieramy narzędzia najczęściej używane, pogrupowane według zadania, a pozostałe wymieniamy na końcu.

## Iteratory nieskończone: `count`, `cycle`, `repeat`

Trzy funkcje tworzą iteratory bez końca. `count(start, step)` odpowiada funkcji `naturalne()` z sekcji [Generatory nieskończone](../06-funkcje/funkcje-generatorowe.md#generatory-nieskonczone), z dodatkowym krokiem; `cycle(iterowalny)` powtarza elementy podanego obiektu cyklicznie, bez końca; `repeat(obiekt)` zwraca wciąż ten sam obiekt, a z drugim argumentem — określoną liczbę razy. Obowiązuje ostrzeżenie z rozdziału 6: iteratora nieskończonego nie wolno przekazać funkcji, która próbuje go wyczerpać, jak `list()` czy `sum()`. Bezpiecznym odbiorcą jest `islice()` z następnej sekcji, pobierająca tylko początkowy fragment:

```{ .python .no-copy }
>>> from itertools import count, cycle, repeat, islice
>>> licznik = count(1)
>>> next(licznik), next(licznik), next(licznik)
(1, 2, 3)
>>> list(islice(count(10, 2), 4))
[10, 12, 14, 16]
>>> list(islice(cycle("ab"), 5))
['a', 'b', 'a', 'b', 'a']
>>> list(repeat("x", 3))
['x', 'x', 'x']
>>> list(map(pow, range(5), repeat(2)))
[0, 1, 4, 9, 16]
```

Ostatni wiersz pokazuje typowe zastosowanie `repeat()` bez limitu: funkcja `map()` z sekcji [Funkcje map() i filter()](../06-funkcje/funkcje-jako-obiekty.md#funkcje-map-i-filter) przyjmuje kilka obiektów iterowalnych i kończy pracę wraz z najkrótszym z nich, więc nieskończony `repeat(2)` dostarcza drugi argument `pow()` dokładnie tyle razy, ile elementów ma `range(5)`.

## Wycinki i łączenie: `islice`, `chain`

Wycinek `sekwencja[start:stop:step]` z rozdziału 5 wymaga sekwencji — obiektu o znanej długości i dostępie przez indeks. Funkcja `islice()` wykonuje tę samą operację na dowolnym obiekcie iterowalnym, także na iteratorze nieskończonym albo generatorze, którego elementy dopiero powstaną: `islice(iterowalny, stop)` pobiera początkowe elementy, a `islice(iterowalny, start, stop, step)` pomija pierwsze `start` i pobiera dalsze. Indeksy ujemne nie są obsługiwane, bo długość nie jest znana z góry. Funkcja `chain()` odpowiada `polacz()` z sekcji [Delegowanie przez yield from](../06-funkcje/funkcje-generatorowe.md#delegowanie-przez-yield-from): produkuje kolejno elementy wszystkich przekazanych obiektów:

```{ .python .no-copy }
>>> from itertools import islice, chain, count
>>> list(islice("ABCDEFGH", 2, 6))
['C', 'D', 'E', 'F']
>>> list(islice(count(), 5, 10))
[5, 6, 7, 8, 9]
>>> list(chain("ab", [1, 2], range(3)))
['a', 'b', 1, 2, 0, 1, 2]
```

Obie funkcje nie budują żadnej listy pośredniej: `islice()` pobiera elementy ze źródła i przekazuje wybrane dalej, a `chain()` przechodzi do następnego obiektu dopiero po wyczerpaniu poprzedniego. Dzięki temu nadają się na etapy potoku z rozdziału 6 — na przykład `islice(potok, 5)` pobiera pięć pierwszych wyników potoku o nieskończonym źródle, którego nie wolno było materializować.

## Okna i porcje: `pairwise`, `batched`

Dwa nowsze narzędzia obsługują schematy, które wcześniej wymagały własnych funkcji generatorowych. `pairwise()`, dostępna od Pythona 3.10, zwraca kolejne pary sąsiednich elementów — okno o szerokości dwóch elementów przesuwane o jeden — co pozwala na przykład obliczyć różnice między kolejnymi pomiarami. `batched()`, dostępna od Pythona 3.12, dzieli obiekt iterowalny na krotki o zadanej długości; ostatnia porcja może być krótsza, chyba że argumentem `strict=True` (od Pythona 3.13) zażądamy porcji równych, analogicznie do `zip(strict=True)` z sekcji [Funkcja zip()](../05-typy-zlozone/krotka.md#funkcja-zip):

```{ .python .no-copy }
>>> from itertools import pairwise, batched
>>> list(pairwise([1, 2, 3, 4]))
[(1, 2), (2, 3), (3, 4)]
>>> pomiary = [10, 13, 17, 22]
>>> [b - a for a, b in pairwise(pomiary)]
[3, 4, 5]
>>> list(batched("ABCDEFG", 3))
[('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]
>>> list(batched("ABCDEFG", 3, strict=True))
Traceback (most recent call last):
  File "<python-input-5>", line 1, in <module>
    list(batched("ABCDEFG", 3, strict=True))
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: batched(): incomplete batch
```

Błąd pojawia się dopiero przy pobraniu ostatniej, niepełnej porcji — a nie przy wywołaniu `batched()` — bo iterator sprawdza dane w miarę ich przetwarzania. `batched()` jest naturalnym narzędziem do przetwarzania danych partiami: zapisu po sto rekordów, wysyłania po dziesięć zapytań, wypisywania tabeli po kilka pozycji w wierszu.

## Akumulacja i przekształcanie: `accumulate`, `starmap`

Funkcja `reduce()` z poprzedniego podrozdziału zwraca wyłącznie wynik końcowy redukcji. `accumulate()` produkuje wszystkie wyniki pośrednie — domyślnie **sumy bieżące** (ang. *running totals*), a z podaną funkcją dwuargumentową dowolną akumulację; argument `initial` działa jak w `reduce()` i pojawia się w wyniku jako pierwszy element. `starmap()` jest odmianą `map()` dla sytuacji, w której argumenty funkcji są już spakowane w krotki: każdy element rozpakowuje w wywołaniu, jak `funkcja(*element)` w sekcji [Rozpakowanie argumentów w wywołaniu](../06-funkcje/argumenty-i-parametry.md#rozpakowanie-argumentow-w-wywoaniu), podczas gdy `map()` oczekuje osobnego obiektu iterowalnego dla każdego argumentu:

```{ .python .no-copy }
>>> from itertools import accumulate, starmap
>>> list(accumulate([1, 2, 3, 4]))
[1, 3, 6, 10]
>>> list(accumulate([3, 1, 4, 1, 5], max))
[3, 3, 4, 4, 5]
>>> list(accumulate([1, 2, 3], initial=100))
[100, 101, 103, 106]
>>> list(starmap(pow, [(2, 3), (3, 2)]))
[8, 9]
>>> list(map(pow, [2, 3], [3, 2]))
[8, 9]
```

Drugie wywołanie `accumulate()` — z funkcją `max` — daje bieżące maksimum, przydatne na przykład do śledzenia rekordu w ciągu pomiarów. Trzecie pokazuje, że wynik z `initial` ma o jeden element więcej niż dane.

## Grupowanie: `groupby`

W poprzednim podrozdziale grupowaliśmy słowa według pierwszej litery za pomocą `defaultdict(list)`, otrzymując słownik grup. Funkcja `groupby()` grupuje inaczej: przechodzi przez dane raz i rozpoczyna nową grupę za każdym razem, gdy zmienia się wartość klucza — łączy więc wyłącznie elementy **sąsiadujące**. Wynika z tego warunek, o którym łatwo zapomnieć: dane muszą być posortowane według tej samej funkcji klucza, inaczej ta sama wartość klucza pojawi się w kilku grupach:

```python title="grupowanie-itertools.py"
from itertools import groupby

dane = [1, 1, 2, 1, 2, 2]
print([(klucz, list(grupa)) for klucz, grupa in groupby(dane)])
print([(klucz, list(grupa)) for klucz, grupa in groupby(sorted(dane))])

slowa = ["ala", "bartek", "adam", "basia"]
for litera, grupa in groupby(sorted(slowa), key=lambda slowo: slowo[0]):
    print(litera, list(grupa))
```

```{ .text .no-copy }
[(1, [1, 1]), (2, [2]), (1, [1]), (2, [2, 2])]
[(1, [1, 1, 1]), (2, [2, 2, 2])]
a ['adam', 'ala']
b ['bartek', 'basia']
```

`groupby()` zwraca pary (klucz, grupa), w których grupa jest iteratorem — jednorazowym i ważnym tylko do chwili pobrania następnej pary, bo obie strony czytają z tego samego źródła. Dlatego grupę materializujemy funkcją `list()` natychmiast, jak w przykładzie. Bez argumentu `key` kluczem jest sam element; funkcja klucza jest tą samą funkcją, którą podajemy `sorted()` — najprościej związać ją z nazwą i użyć w obu miejscach. Wybór między `groupby()` a `defaultdict(list)` zależy od danych: gdy są już posortowane albo napływają strumieniem posortowanym według klucza, `groupby()` nie potrzebuje pamięci na wszystkie grupy naraz; gdy porządek jest dowolny, `defaultdict` jest prostszy i nie wymaga sortowania.

## Kombinatoryka: `product`, `permutations`, `combinations`

Trzy funkcje generują układy elementów, które w rozdziale 4 zapisywalibyśmy zagnieżdżonymi pętlami. `product()` zwraca **iloczyn kartezjański** — wszystkie pary (ogólnie krotki) złożone z elementów kolejnych obiektów, a z argumentem `repeat=n` układy z powtórzeniami elementów jednego obiektu. `permutations(iterowalny, r)` zwraca **permutacje** — układy `r` elementów wybranych z różnych pozycji, w których kolejność ma znaczenie; `combinations(iterowalny, r)` — **kombinacje**, czyli takie same układy bez względu na kolejność:

```{ .python .no-copy }
>>> from itertools import product, permutations, combinations
>>> list(product("AB", [1, 2]))
[('A', 1), ('A', 2), ('B', 1), ('B', 2)]
>>> list(product("ab", repeat=2))
[('a', 'a'), ('a', 'b'), ('b', 'a'), ('b', 'b')]
>>> list(permutations("abc", 2))
[('a', 'b'), ('a', 'c'), ('b', 'a'), ('b', 'c'), ('c', 'a'), ('c', 'b')]
>>> list(combinations("abc", 2))
[('a', 'b'), ('a', 'c'), ('b', 'c')]
```

Wywołanie `product("AB", [1, 2])` zastępuje dwie zagnieżdżone pętle `for` jednym iteratorem, po którym iteruje jedna pętla z rozpakowaniem krotki. Wyniki są produkowane leniwie, ale ich liczba rośnie bardzo szybko wraz z liczbą elementów i długością układu — przed materializacją funkcją `list()` warto oszacować, ile układów powstanie.

**Dalsze narzędzia.** Moduł zawiera jeszcze kilka funkcji, które tylko wymieniamy. `zip_longest()` działa jak `zip()`, ale kończy pracę wraz z najdłuższym obiektem, uzupełniając brakujące elementy wartością `fillvalue`. `takewhile(warunek, iterowalny)` pobiera elementy, dopóki warunek jest prawdziwy, a `dropwhile()` pomija je aż do pierwszego, dla którego warunek jest fałszywy. `filterfalse()` jest dopełnieniem `filter()` — przepuszcza elementy, dla których funkcja zwraca fałsz. `compress(dane, selektory)` przepuszcza element, gdy odpowiadający mu selektor jest prawdziwy. `tee(iterowalny, n)` zwraca `n` niezależnych iteratorów czytających z jednego źródła — po jego użyciu z pierwotnego iteratora nie wolno już korzystać. Od Pythona 3.14 iteratorów `itertools` nie można kopiować funkcjami modułu `copy` z rozdziału 5; `tee()` jest właściwym narzędziem, gdy z jednego strumienia potrzebujemy dwóch, a danych nie chcemy materializować listą. Dokumentacja modułu kończy się sekcją *Itertools Recipes* z kilkudziesięcioma krótkimi funkcjami zbudowanymi z omówionych narzędzi — jak `flatten`, `unique_everseen` czy `sliding_window` — a ich gotowe implementacje udostępnia pakiet zewnętrzny more-itertools, instalowany w środowisku wirtualnym poleceniem `python -m pip install more-itertools`.

Na tym kończymy rozdział o modułach. Od jednego pliku przeszliśmy do projektu z pakietem, testami i instalacją w środowisku wirtualnym, a biblioteka standardowa — `sys`, `collections`, `functools` i `itertools` — okazała się tym samym mechanizmem importu, którym łączymy własne moduły. W następnym rozdziale zajmujemy się wyjątkami: błędami, które dotąd czytaliśmy wyłącznie ze śladów wywołań, a które od teraz będziemy obsługiwać.
