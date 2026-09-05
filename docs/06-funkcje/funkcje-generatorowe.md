# Funkcje generatorowe

W rozdziale [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md#iteratory) poznaliśmy iteratory: obiekty jednorazowe, z których funkcja `next()` pobiera kolejne elementy, aż zgłoszą wyjątek `StopIteration`. W rozdziale [5. Typy złożone](../05-typy-zlozone/zlozenia.md#wyrazenie-generatorowe) zapisaliśmy własny iterator wyrażeniem generatorowym, a na stronie [Funkcje jako obiekty](funkcje-jako-obiekty.md#funkcje-map-i-filter) poznaliśmy funkcje `map()` i `filter()`, zwracające iteratory klas `map` i `filter`. Ta strona domyka ten wątek: wprowadza funkcje generatorowe ze słowem kluczowym `yield`, wymienionym w katalogu słów kluczowych w rozdziale [3. Nazwy i typy](../03-nazwy-typy/nazwy-i-slowa-kluczowe.md#sowa-kluczowe), i porządkuje pojęcia — zwykła funkcja, funkcja generatorowa, obiekt generatora, iterator, wyrażenie generatorowe oraz `map()` i `filter()`.

## Funkcja generatorowa i obiekt generatora

Słowo kluczowe `yield` może wystąpić wyłącznie w ciele funkcji. Jego obecność zmienia znaczenie całej definicji: instrukcja `def` tworzy wtedy **funkcję generatorową** (ang. *generator function*) zamiast zwykłej funkcji. Wywołanie funkcji generatorowej nie wykonuje jej ciała — zwraca **obiekt generatora** (ang. *generator object*), nazywany w dokumentacji także iteratorem generatorowym (ang. *generator iterator*). Dokumentacja używa słowa **generator** potocznie w obu znaczeniach; w tej książce „generator” oznacza — jak w rozdziałach 4 i 5 — obiekt generatora, tworzony funkcją generatorową albo wyrażeniem generatorowym, a funkcję nazywamy zawsze funkcją generatorową.

```python title="odliczanie.py"
def odliczanie():
    print("start")
    yield 3
    yield 2
    yield 1
    print("koniec")


print(type(odliczanie))
generator = odliczanie()
print(type(generator))
print("obiekt generatora utworzony")
print(next(generator))
```

```{ .text .no-copy }
<class 'function'>
<class 'generator'>
obiekt generatora utworzony
start
3
```

Funkcja `odliczanie` jest obiektem klasy `function`, tak jak każda funkcja ze strony [Definiowanie funkcji](definiowanie-funkcji.md#funkcja-jako-obiekt). Jej wywołanie zwraca obiekt klasy `generator` i niczego nie wypisuje — komunikat „start” pojawia się dopiero po wywołaniu `next(generator)`. Wtedy ciało funkcji wykonuje się od początku do pierwszej instrukcji `yield`, wartość `3` trafia do wywołującego, a wykonanie zostaje **zawieszone** (ang. *suspended*), czyli wstrzymane do następnego wywołania `next()`. Reprezentacja obiektu generatora w konsoli zawiera nazwę funkcji, z której obiekt powstał; adres po `at` jest, jak poprzednio, szczegółem implementacyjnym:

```{ .python .no-copy }
>>> generator = odliczanie()
>>> generator
<generator object odliczanie at 0x...>
>>> generator.__name__
'odliczanie'
```

Postać tej reprezentacji i nazwa klasy `generator` są szczegółem CPythona; dokumentacja gwarantuje atrybut `__name__` z nazwą funkcji generatorowej.

## Wstrzymanie i wznowienie wykonania

Kolejne wywołania `next()` wznawiają wykonanie od miejsca zawieszenia — od instrukcji następującej po ostatnim `yield`:

```{ .python .no-copy }
>>> generator = odliczanie()
>>> next(generator)
start
3
>>> next(generator)
2
>>> next(generator)
1
>>> next(generator)
koniec
Traceback (most recent call last):
  File "<python-input-4>", line 1, in <module>
    next(generator)
    ~~~~^^^^^^^^^^^
StopIteration
>>> next(generator, "wyczerpany")
'wyczerpany'
```

Czwarte wywołanie wznawia wykonanie za instrukcją `yield 1`: wypisuje „koniec”, dochodzi do końca ciała i wtedy obiekt generatora zgłasza `StopIteration` — dokładnie tak, jak iteratory z rozdziału 4. Każde następne `next()` zgłasza ten wyjątek ponownie; forma `next(generator, wartość_domyślna)`, poznana w rozdziale [5. Typy złożone](../05-typy-zlozone/lista.md#elementy-listy), zwraca wtedy wartość domyślną. Instrukcja `return` w ciele funkcji generatorowej kończy generator tak samo jak dojście do końca ciała. Cały model wygląda następująco:

```{ .text .no-copy }
def z yield           →  funkcja generatorowa
wywołanie funkcji     →  obiekt generatora (ciało jeszcze nie wykonane)
pierwsze next()       →  wykonanie do pierwszego yield → wartość → zawieszenie
kolejne next()        →  wznowienie za yield → następny yield → zawieszenie
koniec ciała / return →  StopIteration
```

Instrukcja `yield` nie jest wielokrotnym `return`. Instrukcja `return` kończy wykonanie funkcji: jej ramka wywołania, poznana na stronie [Rekurencja](rekurencja.md#przypadek-bazowy-i-krok-rekurencyjny), znika wraz z nazwami lokalnymi. Instrukcja `yield` tylko zawiesza wykonanie: ramka pozostaje, a wraz z nią — jak ujmuje to dokumentacja języka — cały stan lokalny, w tym bieżące wiązania nazw lokalnych i miejsce, od którego wykonanie ma być wznowione. Obiekt generatora jest iteratorem w rozumieniu rozdziału 4. Każdy iterator — także te z rozdziału 4 — zwraca z `iter()` samego siebie; dzięki temu pętla `for`, która zawsze zaczyna od `iter()`, przyjmuje zarówno obiekty iterowalne, jak i iteratory, i sama przechwytuje `StopIteration`. Sprawdzamy to dla obiektu generatora:

```{ .python .no-copy }
>>> generator = odliczanie()
>>> iter(generator) is generator
True
>>> for wartosc in generator:
...     print(wartosc)
...
start
3
2
1
koniec
```

Zachowanie stanu lokalnego między kolejnymi `yield` pozwala zapisać `yield` wewnątrz pętli. Funkcja `licznik()` zwraca generator kolejnych liczb z zadanego przedziału:

```python title="licznik.py"
def licznik(start, koniec):
    """Zwraca generator kolejnych liczb całkowitych od start do koniec."""
    n = start
    while n <= koniec:
        yield n
        n += 1


for wartosc in licznik(1, 3):
    print(wartosc)
print(list(licznik(5, 8)))
```

```{ .text .no-copy }
1
2
3
[5, 6, 7, 8]
```

Pierwsze `next()` wiąże `n` z wartością `start`, sprawdza warunek pętli i zawiesza wykonanie na `yield n`. Kolejne wznawia je za tą instrukcją: `n += 1`, ponowne sprawdzenie warunku, kolejne zawieszenie. Gdy warunek przestaje być spełniony, ciało kończy się i generator zgłasza `StopIteration`. Nazwa `n` jest lokalna dla tego obiektu generatora — dwa obiekty utworzone z tej samej funkcji mają niezależne stany:

```{ .python .no-copy }
>>> a = licznik(1, 3)
>>> b = licznik(1, 3)
>>> next(a), next(a), next(b)
(1, 2, 1)
>>> list(a), list(b)
([3], [2, 3])
```

Na stronie [Zasięg nazw i domknięcia](zasieg-nazw-i-domkniecia.md#przestrzenie-nazw-i-zasiegi) ustaliliśmy, że przestrzeń lokalna istnieje tak długo, jak wywołanie. Domknięcie przechowuje stan w zachowanych wiązaniach zmiennych wolnych, już po usunięciu przestrzeni lokalnej funkcji otaczającej; obiekt generatora przechowuje go we własnej, zawieszonej ramce, w której przestrzeń lokalna nadal istnieje. Funkcja generatorowa jest więc najprostszym sposobem zapisania obliczenia, które ma zachowywać stan między kolejnymi pobraniami wyniku — prostszym niż domknięcie z `nonlocal` opakowane w `iter(obiekt_wywoływalny, wartownik)` ze strony [Funkcje jako obiekty](funkcje-jako-obiekty.md#obiekty-wywoywalne).

## Leniwość i jednorazowość

Obiekt generatora oblicza wartości dopiero wtedy, gdy są pobierane — jest **leniwy** (ang. *lazy*), tak jak sekwencja `range` z rozdziału [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md#leniwa-sekwencja-range), w odróżnieniu od niej jest jednak iteratorem. Widać to, porównując funkcję budującą całą listę z funkcją generatorową o tej samej treści, gdy obie wypisują komunikat przy każdym obliczeniu:

```python title="leniwe.py"
def kwadraty_lista(n):
    """Zwraca listę kwadratów liczb od 0 do n - 1."""
    wynik = []
    for i in range(n):
        print(f"obliczam {i}")
        wynik.append(i * i)
    return wynik


def kwadraty(n):
    """Zwraca generator kwadratów liczb od 0 do n - 1."""
    for i in range(n):
        print(f"obliczam {i}")
        yield i * i


lista = kwadraty_lista(3)
print("lista gotowa:", lista)
generator = kwadraty(3)
print("generator utworzony")
print(next(generator))
print(next(generator))
```

```{ .text .no-copy }
obliczam 0
obliczam 1
obliczam 2
lista gotowa: [0, 1, 4]
generator utworzony
obliczam 0
0
obliczam 1
1
```

Wywołanie `kwadraty_lista(3)` wykonuje wszystkie obliczenia, zanim zwróci wynik. Wywołanie `kwadraty(3)` nie oblicza niczego; każde `next()` oblicza dokładnie jeden element, a trzeci kwadrat nie zostaje obliczony nigdy, bo program go nie pobiera. Leniwość ma dwie praktyczne konsekwencje: można pobrać tylko część wyników — np. zakończyć przeglądanie po znalezieniu pierwszego pasującego elementu — i można pracować z ciągiem, którego pełne zbudowanie w pamięci byłoby niepotrzebne albo, jak w następnej sekcji, niemożliwe.

Drugą cechą, wspólną ze wszystkimi iteratorami i znaną z rozdziału [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md#iteratory) oraz z wyrażenia generatorowego w rozdziale 5, jest **jednorazowość**. Wyczerpany generator pozostaje wyczerpany; aby przejść po wartościach ponownie, tworzymy nowy obiekt kolejnym wywołaniem funkcji generatorowej. Generator nie ma też określonej długości — `len()` zgłasza `TypeError`, bo ustalenie liczby elementów wymagałoby wykonania wszystkich obliczeń:

```{ .python .no-copy }
>>> generator = kwadraty(3)
>>> sum(generator)
obliczam 0
obliczam 1
obliczam 2
5
>>> list(generator)
[]
>>> len(kwadraty(3))
Traceback (most recent call last):
  File "<python-input-3>", line 1, in <module>
    len(kwadraty(3))
    ~~~^^^^^^^^^^^^^
TypeError: object of type 'generator' has no len()
```

Gdy potrzebna jest długość, indeksowanie albo wielokrotne przejście, wynik generatora przekazujemy funkcji `list()`, rezygnując z leniwości. Wyrażenie generatorowe z rozdziału 5 tworzy obiekt tej samej klasy — różni się tylko sposobem powstania i, w CPythonie, nazwą `<genexpr>` w atrybucie `__name__`; iteratory zwracane przez `map()` i `filter()` należą natomiast do własnych klas:

```{ .python .no-copy }
>>> wyrazenie = (i * i for i in range(3))
>>> type(wyrazenie), type(kwadraty(3))
(<class 'generator'>, <class 'generator'>)
>>> wyrazenie.__name__
'<genexpr>'
>>> type(map(str, [1])), type(filter(None, [1]))
(<class 'map'>, <class 'filter'>)
```

Zestawienie pojęć używanych na tej i na poprzednich stronach:

| Pojęcie | Czym jest | Jak powstaje |
|---|---|---|
| zwykła funkcja | funkcja wykonująca całe ciało przy wywołaniu i kończąca je instrukcją `return` albo dojściem do końca ciała (wynik `None`) | `def` bez `yield` w ciele |
| funkcja generatorowa | funkcja, której wywołanie zwraca obiekt generatora zamiast wykonać ciało | `def` z `yield` w ciele |
| obiekt generatora (iterator generatorowy) | iterator wykonujący fragmentami, po jednym elemencie, ciało funkcji generatorowej (od jednego `yield` do następnego) albo pętlę wyrażenia generatorowego | wywołanie funkcji generatorowej albo wyrażenie generatorowe |
| wyrażenie generatorowe | wyrażenie tworzące obiekt generatora z jednego wyrażenia i pętli `for`; nie jest funkcją | `(i * i for i in range(3))` |
| iterator | obiekt obsługujący `next()` i kończący się wyjątkiem `StopIteration`, dla którego `iter()` zwraca ten sam obiekt; obiekt generatora jest jednym z rodzajów iteratora | `iter(lista)`, `enumerate()`, `zip()`, `reversed()`, obiekt generatora |
| `map()`, `filter()` | funkcje zwracające iteratory klas `map` i `filter`: `map` przekształca elementy funkcją, `filter` przepuszcza elementy, dla których funkcja zwraca wartość prawdziwą; nie są generatorami | `map(funkcja, dane)`, `filter(funkcja, dane)` |

## Generatory nieskończone

Skoro wartości powstają na żądanie, ciało funkcji generatorowej nie musi się nigdy kończyć. Pętla `while` z warunkiem zawsze prawdziwym — `while True`, pokazana w rozdziale [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md#break-continue-pass) przy instrukcji `pass` — daje generator kolejnych liczb naturalnych:

```python title="naturalne.py"
def naturalne(start=0):
    """Zwraca generator kolejnych liczb całkowitych od start, bez końca."""
    n = start
    while True:
        yield n
        n += 1


generator = naturalne()
for liczba in generator:
    if liczba > 4:
        break
    print(liczba)
print(next(generator))
print(next(naturalne(10)))
```

```{ .text .no-copy }
0
1
2
3
4
6
10
```

Generator nieskończony jest wykonalny wyłącznie dlatego, że wartości powstają na żądanie — w każdej chwili istnieje tylko bieżąca wartość lokalnej nazwy `n`. O zakończeniu decyduje odbiorca: pętla `for` przerwana instrukcją `break` z rozdziału [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md#break-continue-pass) albo pojedyncze wywołania `next()`. Po przerwaniu pętli generator pozostaje zawieszony: pętla pobrała już `5`, więc następne `next()` zwraca `6`. Takiego generatora nie wolno przekazać funkcjom, które próbują wyczerpać iterator: program albo będzie działał bez końca (`sum()`, `max()`, pętla `for` bez `break`), albo — gromadząc elementy — wyczerpie pamięć (`list()`, `sorted()`, metoda `join()`); w obu przypadkach trzeba go przerwać z klawiatury (++ctrl+c++). Gotowe narzędzia do pobierania początkowego fragmentu ciągu i do tworzenia ciągów nieskończonych oferuje moduł `itertools` z biblioteki standardowej, który poznamy w następnym rozdziale. <!-- TODO: link po powstaniu rozdziału o modułach -->

## Potoki generatorów

Funkcja generatorowa może przyjmować obiekt iterowalny i przetwarzać jego elementy pojedynczo. Kilka takich funkcji połączonych w łańcuch tworzy **potok** (ang. *pipeline*): źródło, filtr, przekształcenie i odbiorca, a każdy element przechodzi przez kolejne etapy — o ile filtr go przepuści — zanim źródło wyprodukuje następny:

```python title="potok.py"
def naturalne(start=0):
    """Zwraca generator kolejnych liczb całkowitych od start, bez końca."""
    n = start
    while True:
        yield n
        n += 1


def parzyste(liczby):
    """Zwraca generator przepuszczający tylko liczby parzyste."""
    for liczba in liczby:
        if liczba % 2 == 0:
            yield liczba


def kwadraty(liczby):
    """Zwraca generator kwadratów kolejnych liczb."""
    for liczba in liczby:
        yield liczba * liczba


potok = kwadraty(parzyste(naturalne()))
for wynik in potok:
    if wynik > 100:
        break
    print(wynik)
```

```{ .text .no-copy }
0
4
16
36
64
100
```

Źródło jest nieskończone, a mimo to potok działa: pętla odbiorcy pobiera element z obiektu generatora utworzonego przez `kwadraty()`, ten — z obiektu utworzonego przez `parzyste()`, a tamten pobiera z obiektu `naturalne()` tyle liczb, ile jest potrzebne do znalezienia parzystej. Samo utworzenie potoku niczego nie oblicza — wyrażenie `kwadraty(parzyste(naturalne()))` tworzy jedynie trzy obiekty generatorów, a obliczenia zaczynają się przy pierwszym pobraniu elementu przez odbiorcę. Przepływ elementów przez etapy pokazuje wersja z komunikatami:

```python title="potok-slad.py"
def zrodlo():
    for n in (1, 2, 3):
        print(f"  źródło: {n}")
        yield n


def podwoj(liczby):
    for n in liczby:
        print(f"  podwajam: {n}")
        yield 2 * n


for wynik in podwoj(zrodlo()):
    print(f"odbiorca: {wynik}")
```

```{ .text .no-copy }
  źródło: 1
  podwajam: 1
odbiorca: 2
  źródło: 2
  podwajam: 2
odbiorca: 4
  źródło: 3
  podwajam: 3
odbiorca: 6
```

Element `1` przechodzi przez źródło, przekształcenie i odbiorcę, zanim źródło wyprodukuje `2`; żaden etap nie buduje listy pośredniej. Etapy potoku można też zapisać wyrażeniami generatorowymi z rozdziału 5 — wynik jest identyczny:

```python title="potok-wyrazenia.py"
def naturalne(start=0):
    """Zwraca generator kolejnych liczb całkowitych od start, bez końca."""
    n = start
    while True:
        yield n
        n += 1


parzyste = (n for n in naturalne() if n % 2 == 0)
kwadraty = (n * n for n in parzyste)
for wynik in kwadraty:
    if wynik > 100:
        break
    print(wynik)
```

```{ .text .no-copy }
0
4
16
36
64
100
```

Żadna z form nie jest zawsze lepsza. Wyrażenie generatorowe jest naturalne dla prostego przekształcenia albo selekcji zapisanej jednym wyrażeniem. Funkcja generatorowa jest właściwa, gdy etap wymaga kilku instrukcji, zachowania stanu między elementami, rozgałęzień albo kilku instrukcji `yield` — jak źródło `naturalne()`, które nie ma naturalnego zapisu wyrażeniem — wyrażenie generatorowe iteruje po istniejącym obiekcie iterowalnym, a nie tworzy ciągu od zera. Obie formy łączą się swobodnie w jednym potoku. Potoku o nieskończonym źródle nie wolno niezależnie od formy zapisu przekazywać funkcji `list()` — „materializować”, jak nazwaliśmy to w rozdziale [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md#leniwa-sekwencja-range): zapis `list(kwadraty)[:5]` próbowałby najpierw zbudować całą listę, a przy dużym, lecz skończonym źródle obliczyłby wszystkie elementy, aby wykorzystać pięć.

## Delegowanie przez yield from

Etap potoku, który ma przekazać dalej wszystkie elementy innego obiektu iterowalnego, wymagałby pętli `for` z instrukcją `yield` w ciele. Instrukcja `yield from` zapisuje to jednym wierszem — jest to **delegowanie** (ang. *delegation*): produkowanie wartości zostaje przekazane podanemu obiektowi iterowalnemu, a jego kolejne elementy trafiają bezpośrednio do odbiorcy. Funkcja `polacz()` łączy dowolną liczbę obiektów iterowalnych, przekazanych przez parametr `*iterowalne` ze strony [Argumenty i parametry](argumenty-i-parametry.md#parametr-args), w jeden ciąg:

```python title="polacz.py"
def polacz(*iterowalne):
    """Zwraca generator kolejnych elementów wszystkich podanych obiektów."""
    for iterowalny in iterowalne:
        yield from iterowalny


print(list(polacz([1, 2], "ab", range(3))))
```

```{ .text .no-copy }
[1, 2, 'a', 'b', 0, 1, 2]
```

W tym podstawowym zastosowaniu `yield from iterowalny` działa tak samo jak pętla `for element in iterowalny: yield element`. Delegować można także do innego obiektu generatora — również takiego, który powstał z tej samej funkcji generatorowej. Spłaszczanie listy zagnieżdżonej ze strony [Rekurencja](rekurencja.md#rekurencja-na-strukturach-zagniezdzonych) przyjmuje wtedy postać rekurencyjnej funkcji generatorowej, która zamiast budować listę wynikową, zwraca generator produkujący wartości pojedynczo:

```python title="splaszcz-generator.py"
def splaszcz(lista):
    """Zwraca generator wszystkich wartości z listy zagnieżdżonej."""
    for element in lista:
        if isinstance(element, list):
            yield from splaszcz(element)
        else:
            yield element


zagniezdzona = [1, [2, 3], [[4], 5]]
generator = splaszcz(zagniezdzona)
print(next(generator), next(generator))
print(list(generator))
print(list(splaszcz([[[[7]]]])))
```

```{ .text .no-copy }
1 2
[3, 4, 5]
[7]
```

Dla elementu będącego listą powstaje zagnieżdżony obiekt generatora, a `yield from` przekazuje jego wartości w górę, przez wszystkie poziomy, aż do odbiorcy; odbiorca widzi jeden płaski ciąg i może pobrać z niego tylko część wartości. W porównaniu z wersją z poprzedniej strony ubyło listy `wynik` oraz wywołań `append()` i `extend()`. Instrukcja `yield from` przekazuje między odbiorcą a generatorem zagnieżdżonym również bardziej zaawansowany protokół sterowania — obiekty generatorów mają metody `send()`, `throw()` i `close()` — który nie jest potrzebny do podstawowego korzystania z generatorów i do którego wrócimy przy korutynach. <!-- TODO: link po powstaniu rozdziału o korutynach -->

Mechanizm generatorów rozwijał się etapami: funkcje generatorowe wprowadził [PEP 255](https://peps.python.org/pep-0255/) (Python 2.2), wyrażenia generatorowe — [PEP 289](https://peps.python.org/pep-0289/) (2.4), protokół sterowania generatorem z zewnątrz — [PEP 342](https://peps.python.org/pep-0342/) (2.5), a instrukcję `yield from` — [PEP 380](https://peps.python.org/pep-0380/) (3.3). Dokumenty te opisują genezę mechanizmu; jego bieżące zachowanie definiuje dokumentacja języka w sekcji o wyrażeniach `yield`.

!!! note "Dla dociekliwych — return z wartością"
    Instrukcja `return wartość` w funkcji generatorowej kończy generator, a podana
    wartość zostaje dołączona do zgłaszanego wyjątku `StopIteration` — widać ją
    w komunikacie śladu wywołań; jak odczytać ją z obiektu wyjątku, pokażemy
    w rozdziale o wyjątkach. Pętla `for` i funkcja `list()` tę wartość pomijają,
    więc nie jest ona sposobem przekazania wyniku odbiorcy; korzysta z niej
    instrukcja `yield from`, dla której staje się wartością wyrażenia —
    w zastosowaniach poza zakresem tej strony. Instrukcje po `return` nigdy się
    nie wykonują:
    <!-- TODO: link po powstaniu rozdziału o wyjątkach -->

    ```{ .python .no-copy }
    >>> def dwa():
    ...     yield 1
    ...     return "gotowe"
    ...     yield 2
    ...
    >>> generator = dwa()
    >>> next(generator)
    1
    >>> next(generator)
    Traceback (most recent call last):
      File "<python-input-3>", line 1, in <module>
        next(generator)
        ~~~~^^^^^^^^^^^
    StopIteration: gotowe
    >>> list(dwa())
    [1]
    ```
