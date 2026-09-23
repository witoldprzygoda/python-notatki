# Biblioteka standardowa i moduł collections

Instrukcja `import` otwiera dostęp nie tylko do modułów własnych, lecz przede wszystkim do **biblioteki standardowej** (ang. *standard library*) — zestawu modułów i pakietów dostarczanych razem z interpreterem. Korzystaliśmy z niej od pierwszego rozdziału: `sys`, `math`, `keyword`, `decimal`, a w tym rozdziale `argparse`; zawsze jednak przy okazji innego tematu. W tym podrozdziale biblioteka standardowa staje się tematem samym w sobie. Ustalamy, co do niej należy, jak czytać jej dokumentację i jak sprawdzić, czy nazwa jest w niej zajęta; wracamy do modułu `sys`, aby domknąć wątek limitu rekurencji z rozdziału 6; poznajemy cztery typy z modułu `collections`, które uzupełniają typy złożone z rozdziału 5. Dwa następne podrozdziały poświęcamy modułom `functools` i `itertools`.

## Moduły w zestawie

Biblioteka standardowa jest instalowana wraz z interpreterem, dlatego nie wymaga ani pip, ani środowiska wirtualnego, a jej zawartość odpowiada wersji interpretera — Python 3.14 ma dokładnie tę bibliotekę, którą opisuje dokumentacja 3.14. W sekcji [Ścieżka wyszukiwania modułów](moduly-i-import.md#sciezka-wyszukiwania-moduow) umieściliśmy ją w tabeli źródeł modułów obok pakietów zewnętrznych i modułów własnych. Rodzaje jej modułów — wbudowane w interpreter, zapisane w plikach `.py` w katalogu `Lib` instalacji oraz rozszerzenia skompilowane z języka C — omówiliśmy w sekcji [Moduł jako plik i jako obiekt](moduly-i-import.md#modu-jako-plik-i-jako-obiekt); dla programu różnica nie istnieje.

Pełną listę nazw udostępnia moduł `sys` w atrybucie `sys.stdlib_module_names`. Jest to zbiór niemodyfikowalny `frozenset` z rozdziału [5. Typy złożone](../05-typy-zlozone/zbiory.md#frozenset), jednakowy na wszystkich platformach, zawierający nazwy modułów i pakietów najwyższego poziomu (bez podmodułów i bez modułów testowych interpretera). Jego naturalnym zastosowaniem jest test kolizji nazw z sekcji [Pułapki importu](moduly-i-import.md#puapki-importu) — zanim nazwiemy własny plik, sprawdzamy, czy nazwa nie jest zajęta:

```{ .python .no-copy }
>>> import sys
>>> type(sys.stdlib_module_names)
<class 'frozenset'>
>>> "json" in sys.stdlib_module_names
True
>>> "random" in sys.stdlib_module_names
True
>>> "narzedzia" in sys.stdlib_module_names
False
>>> "sys" in sys.builtin_module_names, "collections" in sys.builtin_module_names
(True, False)
```

Osobna krotka `sys.builtin_module_names` wymienia węższą grupę: moduły wbudowane w interpreter, których — jak ustaliliśmy w sekcji o pułapkach — nie przesłania własny plik o tej samej nazwie; w ostatnim wierszu sesji sprawdziliśmy, że należy do niej `sys`, ale nie `collections`. Narzędzie pip, choć instalowane razem z interpreterem, nie jest modułem biblioteki standardowej: jest osobnym pakietem w katalogu `site-packages` i dlatego można je aktualizować niezależnie od interpretera, jak w podrozdziale [Pip — zarządzanie pakietami](../01-instalacja/pip.md).

Dokumentacją biblioteki jest spis *The Python Standard Library* pod adresem [docs.python.org/3/library/](https://docs.python.org/3/library/index.html), podzielony tematycznie: typy wbudowane, przetwarzanie tekstu, dane i obliczenia, pliki i katalogi, sieć i tak dalej. Strona każdego modułu ma stały układ: krótki opis przeznaczenia, listę funkcji i typów z sygnaturami, a przy wielu pozycjach noty *Added in version* i *Changed in version*, które mówią, od której wersji Pythona dana możliwość istnieje albo w której zmieniło się jej działanie. Noty te warto czytać: książka opisuje Pythona 3.14, ale program uruchamiany na starszym interpreterze nie znajdzie funkcji dodanej później. Z poziomu konsoli tę samą wiedzę, w skróconej formie, dają funkcje `help(modul)` i `dir(modul)` z podrozdziału [Konsola w praktyce](../02-konsola/konsola-w-praktyce.md#pomoc-wbudowana-help-i-dir).

Poniższe tabele zbierają moduły, które pojawiły się dotąd w książce, oraz te, które zapowiadamy na dalsze rozdziały. Nie jest to przegląd biblioteki — pełny spis liczy setki pozycji i nie należy go uczyć się na pamięć; wystarczy wiedzieć, że zanim napiszemy własne rozwiązanie typowego zadania, warto sprawdzić, czy biblioteka standardowa już go nie zawiera.

| Moduł | Zastosowanie | Gdzie w książce |
|---|---|---|
| `sys` | parametry interpretera: `sys.path`, `sys.argv`, `sys.modules`, `sys.exit()` | rozdz. 1, 3, 7 |
| `math` | funkcje i stałe matematyczne: `math.pi`, `math.sqrt()`, `math.isclose()` | rozdz. 2, 3, 7 |
| `keyword` | lista słów kluczowych języka | rozdz. 3 |
| `decimal`, `fractions` | arytmetyka dziesiętna i ułamki zwykłe | rozdz. 3, 7 |
| `ctypes` | odczyt obiektu spod adresu pamięci (demonstracja modelu pamięci) | rozdz. 3 |
| `copy` | kopie płytkie i głębokie | rozdz. 5 |
| `this` | Zen Pythona | rozdz. 2 |
| `calendar` | kalendarz; przykład uruchomienia modułu przez `python -m` | rozdz. 2, 7 |
| `venv` | tworzenie środowisk wirtualnych | rozdz. 1 |
| `random` | liczby pseudolosowe; przykład kolizji nazw | rozdz. 7 |
| `argparse` | argumenty wiersza poleceń | rozdz. 7 |
| `importlib` | mechanizm importu jako API; `reload()` | rozdz. 7 |
| `collections`, `functools`, `itertools` | typy kontenerowe, narzędzia funkcyjne, iteratory | rozdz. 7 |

| Moduł | Zastosowanie | Kiedy |
|---|---|---|
| `json` | zapis i odczyt danych w formacie JSON | dalsze rozdziały |
| `pathlib`, `os` | ścieżki, pliki i katalogi, informacje o systemie | dalsze rozdziały |
| `datetime`, `time` | daty i czas, pomiar czasu wykonania | dalsze rozdziały |
| `statistics` | średnia, mediana, odchylenie standardowe | dalsze rozdziały |
| `re` | wyrażenia regularne | część „Python Zastosowania”, [rozdział 19](../zastosowania/19-re/index.md) |

!!! note "Wyrażenia regularne"
    Moduł `re` implementuje **wyrażenia regularne** (ang. *regular expressions*)
    — język wzorców do wyszukiwania i przekształcania tekstu. Jest to osobna,
    obszerna umiejętność, niezależna od Pythona; w tej części moduł `re`
    pojawia się co najwyżej w gotowych fragmentach z objaśnieniem, a w całości
    omawia go [rozdział 19 części „Python Zastosowania”](../zastosowania/19-re/index.md).
    Punktem wyjścia do samodzielnej nauki jest też przewodnik
    *Regular Expression HOWTO* w dokumentacji Pythona.

## Moduł `sys`

Moduł `sys` towarzyszy nam od rozdziału 1 i jest wbudowany w interpreter — nie ma atrybutu `__file__`, co sprawdziliśmy w sekcji [Moduł jako plik i jako obiekt](moduly-i-import.md#modu-jako-plik-i-jako-obiekt). Dostarcza informacji o interpreterze i o sposobie uruchomienia programu oraz narzędzi do współpracy z nim. Dotychczas poznane atrybuty i funkcje zbiera poniższe zestawienie:

| Nazwa | Znaczenie | Gdzie w książce |
|---|---|---|
| `sys.executable` | ścieżka do pliku wykonywalnego bieżącego interpretera | [Wirtualne środowisko venv](../01-instalacja/venv.md#kontrola-aktywnego-srodowiska) |
| `sys.path` | ścieżka wyszukiwania modułów | [Ścieżka wyszukiwania modułów](moduly-i-import.md#sciezka-wyszukiwania-moduow) |
| `sys.modules` | pamięć podręczna zaimportowanych modułów | [Wykonywanie modułu podczas importu](moduly-i-import.md#wykonywanie-moduu-podczas-importu) |
| `sys.argv` | lista argumentów wiersza poleceń | [Lista `sys.argv`](argumenty-wiersza-polecen.md#lista-sysargv) |
| `sys.exit()` | zakończenie programu z kodem wyjścia | [Kody wyjścia i funkcja `sys.exit()`](argumenty-wiersza-polecen.md#kody-wyjscia-i-funkcja-sysexit) |
| `sys.stdlib_module_names`, `sys.builtin_module_names` | nazwy modułów biblioteki standardowej i modułów wbudowanych | sekcja wyżej |

Pozostała zapowiedź z podrozdziału [Rekurencja](../06-funkcje/rekurencja.md#limit-rekurencji): funkcje sterujące limitem głębokości rekurencji. Bieżącą wartość limitu zwraca `sys.getrecursionlimit()`:

```python title="limit.py"
import sys

print(sys.getrecursionlimit())
```

```{ .text .no-copy }
1000
```

Wartość `1000` jest domyślnym ustawieniem CPythona — szczegółem implementacyjnym, nie gwarancją języka — a rzeczywista głębokość dostępna dla programu jest mniejsza, bo do limitu liczą się wszystkie aktywne ramki, jak wyjaśniliśmy w rozdziale 6. Limit można zmienić funkcją `sys.setrecursionlimit(limit)`. Dokumentacja wymienia dwa zastrzeżenia: zbyt wysoki limit może doprowadzić do awarii interpretera (limit istnieje właśnie po to, by chronić stos języka C przed przepełnieniem), a limit niższy od bieżącej głębokości wywołań powoduje natychmiastowy `RecursionError`. W tej książce z funkcji tej nie korzystamy: rekurencja poprawna osiąga przypadek bazowy po liczbie kroków wynikającej z danych, a zadanie wymagające tysięcy poziomów zapisujemy iteracyjnie, jak ustaliliśmy w rozdziale 6.

## Kolejka dwustronna `deque`

W sekcji [Kolejka i stos](../05-typy-zlozone/lista.md#kolejka-i-stos) zbudowaliśmy kolejkę na liście i odnotowaliśmy jej wadę: metoda `pop(0)` musi przesunąć wszystkie pozostałe elementy, więc jej koszt rośnie wraz z długością listy. Zapowiedzianym wtedy rozwiązaniem jest typ `deque` z modułu `collections` — **kolejka dwustronna** (ang. *double-ended queue*, stąd nazwa). Dodawanie i zdejmowanie elementów z **obu** końców zajmuje w niej czas stały, niezależny od liczby elementów; ceną jest wolniejszy niż w liście dostęp przez indeks do elementów w głębi kolejki. Kolejkę zadań, w której nowe zadania dopisujemy na końcu, pilne wstawiamy na początek, a wykonujemy zawsze pierwsze, zapiszemy tak:

```python title="kolejka.py"
from collections import deque

zadania = deque(["a", "b", "c"])
zadania.append("d")
zadania.appendleft("pilne")
print(zadania)
print(zadania.popleft())
print(zadania.pop())
print(zadania)
zadania.rotate(1)
print(zadania)
```

```{ .text .no-copy }
deque(['pilne', 'a', 'b', 'c', 'd'])
pilne
d
deque(['a', 'b', 'c'])
deque(['c', 'a', 'b'])
```

Metody `append()` i `pop()` działają na prawym końcu tak jak w liście; `appendleft()` i `popleft()` są ich odpowiednikami dla lewego końca. Metoda `rotate(n)` przesuwa elementy o `n` miejsc w prawo — ostatni element trafia na początek — a dla ujemnego `n` w lewo. Poza tym `deque` zachowuje się jak lista: obsługuje `len()`, pętlę `for`, operator `in`, indeksowanie, metody `extend()`, `extendleft()` i `clear()`; nie obsługuje natomiast wycinków. Stos, w którym obie operacje dotyczą tego samego końca, nie potrzebuje `deque` — lista z `append()` i `pop()` pozostaje właściwym wyborem.

Drugie zastosowanie kolejki dwustronnej wynika z parametru `maxlen`. Kolejka o ograniczonej długości po zapełnieniu usuwa element z przeciwnego końca przy każdym dodaniu, jest więc gotowym **buforem ostatnich elementów** — na przykład ostatnich trzech pomiarów albo ostatnich wierszy dziennika:

```python title="ostatnie.py"
from collections import deque

ostatnie = deque(maxlen=3)
for numer in range(1, 6):
    ostatnie.append(numer)
    print(ostatnie)
```

```{ .text .no-copy }
deque([1], maxlen=3)
deque([1, 2], maxlen=3)
deque([1, 2, 3], maxlen=3)
deque([2, 3, 4], maxlen=3)
deque([3, 4, 5], maxlen=3)
```

Reprezentacja kolejki z ograniczeniem zawiera `maxlen`, więc odróżnia ją od kolejki bez ograniczenia. Lista wymagałaby po każdym dodaniu jawnego usunięcia najstarszego elementu.

## Licznik `Counter`

Zliczanie wystąpień jest jednym z najczęstszych zadań na słowniku. Z narzędzi rozdziału 5 — metody `get()` z wartością domyślną z sekcji [Metody słownika](../05-typy-zlozone/slownik.md#metody-sownika) — powstaje idiom: dla każdego elementu odczytujemy dotychczasową liczbę wystąpień (`0`, gdy elementu jeszcze nie było) i zapisujemy ją powiększoną o jeden. Trzy najczęstsze elementy wybiera funkcja `sorted()` z funkcją klucza z podrozdziału [Funkcje jako obiekty](../06-funkcje/funkcje-jako-obiekty.md#funkcja-klucza-w-sorted-min-i-max):

```python title="zliczanie.py"
tekst = "abracadabra"
licznik = {}
for znak in tekst:
    licznik[znak] = licznik.get(znak, 0) + 1
print(licznik)

najczestsze = sorted(licznik.items(), key=lambda para: para[1], reverse=True)
print(najczestsze[:3])
```

```{ .text .no-copy }
{'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1}
[('a', 5), ('b', 2), ('r', 2)]
```

Idiom jest poprawny i warto go znać, bo pokazuje mechanizm, który `Counter` jedynie opakowuje. Moduł `collections` dostarcza jednak typ `Counter`, który wykonuje to samo w jednym wywołaniu i dodaje operacje typowe dla zliczania:

```python title="counter.py"
from collections import Counter

litery = Counter("abracadabra")
print(litery)
print(litery.most_common(3))
print(litery["a"], litery["z"])
print(litery.total())

slowa = Counter("kot pies kot ryba kot pies".split())
print(slowa.most_common(1))
print(slowa + Counter(["ryba", "ryba"]))
print(slowa - Counter(["kot", "kot", "kot"]))
```

```{ .text .no-copy }
Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
[('a', 5), ('b', 2), ('r', 2)]
5 0
11
[('kot', 3)]
Counter({'kot': 3, 'ryba': 3, 'pies': 2})
Counter({'pies': 2, 'ryba': 1})
```

`Counter` przyjmuje dowolny obiekt iterowalny — łańcuch, listę słów, generator — i zlicza jego elementy, które, jak klucze słownika, muszą być haszowalne. Jest **podklasą** (ang. *subclass*) słownika: typem, który ma wszystkie możliwości słownika i dodaje własne; mechanizm tworzenia takich typów — dziedziczenie — omawiamy w podrozdziale [Dziedziczenie](../10-klasy/dziedziczenie.md#funkcje-isinstance-i-issubclass) rozdziału 10, a tu wystarczy wiedzieć, że wszystkie operacje słownika — `items()`, `keys()`, pętla `for`, operator `in`, konwersja `dict(licznik)` — działają również na liczniku. Różnica pojawia się przy brakującym kluczu: zamiast `KeyError` licznik zwraca `0` i nie tworzy przy tym nowego wpisu. Metoda `most_common(n)` zwraca listę `n` par (element, liczność) od najliczniejszej — dokładnie to, co obliczyliśmy wyżej funkcją `sorted()` — a bez argumentu wszystkie pary; metoda `total()`, dostępna od Pythona 3.10, sumuje liczności. W reprezentacji licznika elementy są wypisane od najliczniejszego. Operatory `+` i `-` łączą liczniki element po elemencie; wynik odejmowania zachowuje wyłącznie liczności dodatnie, dlatego `kot` zniknął z ostatniego wyniku. Liczności dopisuje też metoda `update()`, która — inaczej niż w zwykłym słowniku — dodaje wystąpienia zamiast zastępować wartości.

## Słownik z wartością domyślną `defaultdict`

Drugi częsty idiom słownikowy to grupowanie: każdemu kluczowi odpowiada lista elementów, a przy pierwszym elemencie danej grupy listę trzeba najpierw utworzyć. W rozdziale 5 służyła do tego metoda `setdefault(klucz, [])`, zwracająca istniejącą albo nowo wstawioną listę. Typ `defaultdict` z modułu `collections` wbudowuje ten krok w słownik: przy tworzeniu podajemy **fabrykę wartości domyślnej** (ang. *default factory*) — obiekt wywoływalny bez argumentów, którego wynik staje się wartością każdego klucza użytego po raz pierwszy:

```python title="grupowanie.py"
from collections import defaultdict

slowa = ["ala", "bartek", "adam", "basia", "celina"]
grupy = defaultdict(list)
for slowo in slowa:
    grupy[slowo[0]].append(slowo)
print(grupy)
print(dict(grupy))
print(grupy["z"])
print("z" in grupy, len(grupy))
```

```{ .text .no-copy }
defaultdict(<class 'list'>, {'a': ['ala', 'adam'], 'b': ['bartek', 'basia'], 'c': ['celina']})
{'a': ['ala', 'adam'], 'b': ['bartek', 'basia'], 'c': ['celina']}
[]
True 4
```

Fabryką jest tu typ `list` — jest obiektem wywoływalnym w rozumieniu sekcji [Obiekty wywoływalne](../06-funkcje/funkcje-jako-obiekty.md#obiekty-wywoywalne), a `list()` bez argumentów zwraca pustą listę. Równie dobrze sprawdzają się `int` (wartość `0`), `set` (pusty zbiór) i własna funkcja, także w postaci wyrażenia lambda, na przykład `lambda: "brak"`. Reprezentacja pokazuje fabrykę przed zawartością, a konwersja `dict(grupy)` daje zwykły słownik z tymi samymi parami. `defaultdict` jest, tak jak `Counter`, podklasą słownika.

Dwa ostatnie wiersze wyniku pokazują właściwość, o której trzeba pamiętać: wpis powstaje przy **każdym** odczycie nieistniejącego klucza składnią `slownik[klucz]`, także wtedy, gdy chcieliśmy tylko sprawdzić wartość. Po `grupy["z"]` słownik ma cztery klucze, choć żadne słowo nie zaczyna się na „z”. Metoda `get()` i operator `in` fabryki nie uruchamiają i wpisu nie tworzą — zachowują się jak w zwykłym słowniku:

```{ .python .no-copy }
>>> from collections import defaultdict
>>> licznik = defaultdict(int)
>>> for znak in "abracadabra":
...     licznik[znak] += 1
...
>>> licznik
defaultdict(<class 'int'>, {'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
>>> licznik.get("z")
>>> "z" in licznik
False
>>> licznik["z"]
0
>>> "z" in licznik
True
```

Zapis `licznik[znak] += 1` działa, bo odczyt `licznik[znak]` po prawej stronie dostaje `0` z fabryki `int`; jest to trzeci sposób zliczania, obok idiomu z `get()` i typu `Counter`. Wybór między trzema narzędziami zależy od sytuacji: `get()` z wartością domyślną wystarcza do jednorazowego odczytu, `setdefault()` do jednorazowego wstawienia, a `defaultdict` wtedy, gdy ten sam wzorzec powtarza się w całym programie; do samego zliczania najkrótszy i najczytelniejszy jest `Counter`.

## Krotka z nazwanymi polami `namedtuple`

Krotka z rozdziału [5. Typy złożone](../05-typy-zlozone/krotka.md) dobrze przechowuje rekord o ustalonej liczbie pól — punkt `(1, 2)`, wpis `("Ala", 21)` — ale znaczenie pola wynika wyłącznie z pozycji, a zapis `punkt[1]` nie mówi, czy chodzi o współrzędną `y`. Funkcja `namedtuple()` z modułu `collections` tworzy typ krotki, której pola mają nazwy. Jest to **funkcja fabryczna** (ang. *factory function*): przyjmuje nazwę nowego typu i listę nazw pól, a zwraca nowy typ, będący podklasą krotki; typ ten wiążemy z nazwą — z konwencji tą samą, którą podaliśmy jako pierwszy argument — i używamy jak `tuple` czy `int`:

```python title="punkt.py"
from collections import namedtuple

Punkt = namedtuple("Punkt", ["x", "y"])
p = Punkt(1, 2)
print(p)
print(p.x, p[0])
x, y = p
print(x + y)
print(isinstance(p, tuple))
p.x = 5
```

```{ .text .no-copy }
Punkt(x=1, y=2)
1 1
3
True
Traceback (most recent call last):
  File "punkt.py", line 10, in <module>
    p.x = 5
    ^^^
AttributeError: can't set attribute
```

Do pola sięgamy przez nazwę (`p.x`) albo, jak w zwykłej krotce, przez indeks (`p[0]`); rozpakowanie `x, y = p` działa tak samo jak w sekcji [Pakowanie i rozpakowywanie](../05-typy-zlozone/krotka.md#pakowanie-i-rozpakowywanie), a reprezentacja wypisuje nazwy pól. Wynik `isinstance(p, tuple)` potwierdza, że `Punkt` jest podklasą krotki: obiekt `p` jest krotką we wszystkich kontekstach, w których krotki są wymagane — jako klucz słownika, element zbioru czy argument funkcji przyjmującej sekwencję. Z krotki dziedziczy też niemodyfikowalność: próba przypisania `p.x = 5` kończy się błędem `AttributeError`, tak jak `p[0] = 5` zakończyłoby się błędem `TypeError` dla każdej krotki. Nazwy pól można podać także jednym łańcuchem rozdzielonym spacjami, `namedtuple("Punkt", "x y")`; obie formy są równoważne. Nowy typ ma ponadto kilka metod pomocniczych o nazwach z pojedynczym podkreśleniem, wśród nich `_replace()`, zwracającą nową krotkę ze zmienionym polem, i `_asdict()`, zwracającą słownik pól; opisuje je dokumentacja.

Krotka z nazwanymi polami jest najprostszym w Pythonie sposobem reprezentowania rekordu danych — niemodyfikowalnego, lekkiego, z czytelnym dostępem do pól. Język oferuje także inne mechanizmy, w szczególności **klasy danych** (ang. *data classes*) z pełną kontrolą nad polami, wartościami domyślnymi i modyfikowalnością; omawiamy je w podrozdziale [Klasy danych — dataclass, NamedTuple i Enum](../12-oop-zaawansowane/klasy-danych.md) rozdziału 12. Moduł `collections` zawiera również typ `OrderedDict` — słownik pamiętający kolejność wstawiania z czasów, gdy zwykły `dict` jej nie gwarantował — dziś potrzebny jedynie w wyspecjalizowanych zastosowaniach.

Cztery poznane typy — `deque`, `Counter`, `defaultdict` i `namedtuple` — są przykładem tego, jak biblioteka standardowa rozszerza typy wbudowane: nie zastępują listy, słownika ani krotki, lecz obsługują ich typowe zastosowania bez powtarzania tego samego kodu pomocniczego. W następnym podrozdziale tę samą rolę wobec funkcji z rozdziału 6 spełnia moduł `functools`.
