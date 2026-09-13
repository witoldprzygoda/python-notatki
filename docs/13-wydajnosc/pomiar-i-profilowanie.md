# Pomiar czasu i profilowanie

Zanim przyspieszymy program, musimy wiedzieć, co w nim jest wolne — a intuicja odpowiada na to pytanie często błędnie. W tym podrozdziale poznajemy narzędzia pomiaru z biblioteki standardowej: `time.perf_counter()` i dekorator mierzący czas, moduł `timeit` do mikropomiarów, profiler `cProfile` z modułem `pstats` oraz `tracemalloc` do pomiaru pamięci. Na koniec porównujemy trzy wersje funkcji Fibonacciego z rozdziałów 6 i 7. Wszystkie czasy w tym rozdziale pochodzą z jednego uruchomienia na komputerze autora (Python 3.14.7, 64-bitowy) — na innym komputerze będą inne, ale proporcje między nimi pozostają podobne.

## Zasada: najpierw pomiar

Wydajność programu rzadko zależy od tego, co wygląda na skomplikowane. Typowy program spędza większość czasu w kilku procentach kodu — w **wąskim gardle** (ang. *bottleneck*) — a poprawianie całej reszty nie daje nic poza gorszą czytelnością. Dlatego obowiązuje kolejność: najpierw program poprawny i czytelny, potem pomiar, potem poprawa jednego miejsca, potem ponowny pomiar. Bez pomiaru po zmianie nie wiadomo, czy zmiana w ogóle pomogła; zdarza się, że „optymalizacja” spowalnia kod.

## `time.perf_counter()` i dekorator mierzący czas

Funkcja `time.perf_counter()` z rozdziału 8 zwraca odczyt zegara o wysokiej rozdzielczości; różnica dwóch odczytów to czas w sekundach. Stoper zapisaliśmy już jako menedżer kontekstu — za pomocą dekoratora `@contextmanager` w rozdziale [8. Wyjątki i zarządzanie zasobami](../08-wyjatki/with-i-contextlib.md#dekorator-contextlibcontextmanager) i jako klasę w rozdziale [11. Model danych](../11-model-danych/menedzery-kontekstu.md#metody-__enter__-i-__exit__). Trzecia postać, dekorator funkcji, mierzy każde wywołanie udekorowanej funkcji; korzysta z `functools.wraps` z rozdziału 7, aby zachować nazwę i docstring:

```python title="mierz-czas.py"
import functools
import time


def mierz_czas(funkcja):
    """Wypisuje czas każdego wywołania udekorowanej funkcji."""

    @functools.wraps(funkcja)
    def opakowana(*args, **kwargs):
        start = time.perf_counter()
        wynik = funkcja(*args, **kwargs)
        czas = time.perf_counter() - start
        print(f"{funkcja.__name__}({', '.join(map(repr, args))}): {czas:.4f} s")
        return wynik

    return opakowana


@mierz_czas
def fib(n):
    """Zwraca n-ty wyraz ciągu Fibonacciego rekurencyjnie."""
    if n < 2:
        return n
    return fib.__wrapped__(n - 1) + fib.__wrapped__(n - 2)


@mierz_czas
def fib_iter(n):
    """Zwraca n-ty wyraz ciągu Fibonacciego pętlą."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


print(fib(30))
print(fib_iter(30))
print(fib_iter(300))
```

```{ .text .no-copy }
fib(30): 0.1203 s
832040
fib_iter(30): 0.0000 s
832040
fib_iter(300): 0.0000 s
222232244629420445529739893461909967206666939096499764990979600
```

Dekorator mierzy całe wywołanie zewnętrzne. Wewnątrz `fib()` wywołania rekurencyjne przechodzą przez `fib.__wrapped__` — oryginalną funkcję zachowaną przez `functools.wraps` — inaczej dekorator wypisałby czas każdego z prawie trzech milionów wywołań rekurencyjnych. Wynik jest wymowny: rekurencyjne `fib(30)` liczy się ponad sto milisekund (odczyt `fib.__wrapped__` przy każdym wywołaniu dokłada nieco kosztu do samej rekurencji, którą mierzymy w ostatniej sekcji), a pętla z rozdziału [6. Funkcje](../06-funkcje/rekurencja.md#rekurencja-a-iteracja) daje odpowiedź w czasie poniżej rozdzielczości wydruku, nawet dla `n = 300`. Pomiar pojedynczego wywołania ma jednak ograniczenie: krótkie operacje giną w szumie — inne procesy, pamięć podręczna procesora, sam koszt wywołania `perf_counter()` — dlatego dla operacji trwających mikrosekundy potrzebne jest inne narzędzie.

## Moduł `timeit` — mikropomiary

**Mikropomiar** (ang. *micro-benchmark*) mierzy pojedynczą krótką operację, powtarzając ją wiele razy i dzieląc łączny czas przez liczbę powtórzeń. Moduł `timeit` robi to poprawnie: wyłącza na czas pomiaru odśmiecacz z rozdziału 10, używa najdokładniejszego zegara i przyjmuje kod do zmierzenia jako łańcuch albo jako obiekt wywoływalny:

```python title="timeit-demo.py"
import timeit


def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


czas = timeit.timeit("sum(range(1000))", number=10_000)
print(f"sum(range(1000)) × 10 000: {czas:.3f} s, {czas / 10_000 * 1e6:.1f} µs na wywołanie")

czas = timeit.timeit("fib(20)", globals=globals(), number=100)
print(f"fib(20) × 100: {czas:.3f} s")
print(f"fib(20) przez lambda: {timeit.timeit(lambda: fib(20), number=100):.3f} s")

lista = list(range(100_000))
zbior = set(lista)
print(f"in lista: {timeit.timeit('99_999 in lista', globals=globals(), number=1000):.4f} s")
print(f"in zbior: {timeit.timeit('99_999 in zbior', globals=globals(), number=1000):.6f} s")

powtorzenia = timeit.repeat("sum(range(1000))", number=10_000, repeat=5)
print("repeat:", [f"{t:.4f}" for t in powtorzenia], "minimum:", f"{min(powtorzenia):.4f}")
```

```{ .text .no-copy }
sum(range(1000)) × 10 000: 0.055 s, 5.5 µs na wywołanie
fib(20) × 100: 0.064 s
fib(20) przez lambda: 0.062 s
in lista: 0.4846 s
in zbior: 0.000019 s
repeat: ['0.0581', '0.0565', '0.0542', '0.0510', '0.0512'] minimum: 0.0510
```

Argument `number` określa liczbę powtórzeń — łączny czas powinien wynosić od dziesiątych części sekundy do kilku sekund, aby szum nie dominował. Kod w łańcuchu wykonuje się w osobnej przestrzeni nazw, więc własne funkcje i dane przekazujemy przez `globals=globals()` (albo argumentem `setup=`); obiekt wywoływalny, jak `lambda: fib(20)`, unika tego problemu. Funkcja `repeat()` powtarza cały pomiar kilka razy; miarodajne jest **minimum**, bo każde zakłócenie tylko wydłuża czas — średnia zawiera szum, minimum jest najbliżej prawdziwego kosztu. Pomiar operatora `in` zapowiada następny podrozdział: na liście o stu tysiącach elementów trwa pół milisekundy, na zbiorze — dwadzieścia nanosekund.

Ten sam moduł jest dostępny z wiersza poleceń; opcja `-s` podaje kod przygotowawczy, a liczbę powtórzeń dobiera sam:

```powershell title="Terminal"
python -m timeit "sum(range(1000))"
python -m timeit -s "s = set(range(100_000))" "99_999 in s"
python -m timeit -s "l = list(range(100_000))" "99_999 in l"
```

```{ .text .no-copy }
50000 loops, best of 5: 5.06 usec per loop
20000000 loops, best of 5: 18.4 nsec per loop
500 loops, best of 5: 469 usec per loop
```

Wydruk podaje najlepszy z pięciu przebiegów, przeliczony na jedno wykonanie. To najszybsza droga do odpowiedzi na pytanie „która z dwóch wersji jest szybsza?” — bez pisania skryptu.

## Profilowanie — `cProfile` i `pstats`

Pomiar całości mówi, że program jest wolny; **profilowanie** (ang. *profiling*) mówi, **gdzie**. **Profiler** rejestruje każde wywołanie funkcji z czasem jego trwania, a zestawienie pokazuje, które funkcje zajmują najwięcej czasu i ile razy były wywołane. W bibliotece standardowej służy do tego moduł `cProfile`, a do prezentacji wyników — `pstats`:

```python title="profil-fib.py"
import cProfile
import pstats


def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def fib_iter(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def program():
    for n in range(15, 23):
        fib(n)
    for _ in range(1000):
        fib_iter(30)


profiler = cProfile.Profile()
profiler.enable()
program()
profiler.disable()
pstats.Stats(profiler).strip_dirs().sort_stats("cumulative").print_stats(4)
```

```{ .text .no-copy }
         147850 function calls (1010 primitive calls) in 0.026 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.026    0.026 profil-fib.py:16(program)
 146848/8    0.025    0.000    0.025    0.003 profil-fib.py:5(fib)
     1000    0.001    0.000    0.001    0.000 profil-fib.py:9(fib_iter)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```

Kolumny zestawienia: `ncalls` — liczba wywołań (zapis `146848/8` oznacza 146 848 wywołań, z których 8 to wywołania z zewnątrz, a reszta to rekurencja), `tottime` — czas spędzony w samej funkcji bez funkcji przez nią wywołanych, `cumtime` — czas łączny wraz z wywołaniami podrzędnymi, `percall` — czas na jedno wywołanie: pierwsza kolumna to `tottime` podzielone przez wszystkie wywołania, druga — `cumtime` podzielone przez wywołania pierwotne (stąd dla `fib` druga wartość `percall` to `cumtime` podzielone przez 8). Metoda `strip_dirs()` usuwa z nazw plików ścieżki katalogów, `sort_stats()` sortuje zestawienie, a `print_stats(4)` wypisuje cztery pierwsze wiersze. Sortowanie po `cumulative` pokazuje, które gałęzie programu kosztują najwięcej; sortowanie po `tottime` wskazuje funkcje, które same wykonują pracę. Wniosek z zestawienia jest jednoznaczny: osiem wywołań `fib()` kosztuje kilkadziesiąt razy więcej niż tysiąc wywołań `fib_iter()`, a przyczyną jest liczba wywołań rekurencyjnych, nie koszt pojedynczego. Profiler spowalnia mierzony program, zwykle kilkakrotnie, więc czasy bezwzględne z profilu porównujemy tylko między sobą.

Cały skrypt profilujemy bez zmian w kodzie, z wiersza poleceń. Skrypt `fib25.py` wypisuje `fib(25)`:

```python title="fib25.py"
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


print(fib(25))
```

Opcja `-s` sortuje zestawienie, a `-o` zapisuje wynik do pliku, który później wczytuje `pstats.Stats("plik.prof")`:

```powershell title="Terminal"
python -m cProfile -s cumulative fib25.py
python -m cProfile -o fib.prof fib25.py
```

```{ .text .no-copy }
75025
         242789 function calls (5 primitive calls) in 0.040 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.040    0.040 {built-in method builtins.exec}
        1    0.000    0.000    0.040    0.040 fib25.py:1(<module>)
 242785/1    0.040    0.000    0.040    0.040 fib25.py:1(fib)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
        1    0.000    0.000    0.000    0.000 {built-in method builtins.print}
```

Profil pokazuje 242 785 wywołań rekurencyjnych; pozostałe wiersze to wywołania pomocnicze interpretera. Dla większych programów zestawienie tekstowe ma setki wierszy; wtedy przydaje się narzędzie zewnętrzne `snakeviz` (instalowane poleceniem `python -m pip install snakeviz`), które wczytuje plik zapisany opcją `-o` i pokazuje profil w przeglądarce jako interaktywny wykres. Od Pythona 3.15 narzędzia profilowania trafiają do wspólnego pakietu `profiling`, o czym mowa w ostatnim podrozdziale.

## Pomiar pamięci — `sys.getsizeof()` i `tracemalloc`

Funkcja `sys.getsizeof()` z rozdziału [3. Nazwy i typy](../03-nazwy-typy/obiekty-i-pamiec.md#rozmiar-obiektow-i-zarzadzanie-pamiecia) zwraca rozmiar pojedynczego obiektu — ale tylko jego samego, bez obiektów, które on wskazuje. Rozmiar listy nie obejmuje jej elementów, a rozmiar instancji klasy nie obejmuje słownika atrybutów. Łączne zużycie pamięci przez fragment programu mierzy moduł `tracemalloc`, który śledzi każdą alokację od wywołania `start()`:

```python title="pamiec.py"
import sys
import tracemalloc

lista = list(range(1_000_000))
generator = (x * x for x in range(1_000_000))
print(f"getsizeof listy: {sys.getsizeof(lista) / 1e6:.1f} MB, generatora: {sys.getsizeof(generator)} B")

tracemalloc.start()
kwadraty = [x * x for x in range(1_000_000)]
biezace, szczyt = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"lista miliona kwadratów: {biezace / 1e6:.1f} MB (szczyt {szczyt / 1e6:.1f} MB)")

tracemalloc.start()
suma = sum(x * x for x in range(1_000_000))
biezace, szczyt = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"suma przez generator: szczyt {szczyt / 1e3:.1f} kB")
```

```{ .text .no-copy }
getsizeof listy: 8.0 MB, generatora: 208 B
lista miliona kwadratów: 40.4 MB (szczyt 40.4 MB)
suma przez generator: szczyt 0.5 kB
```

`getsizeof()` listy miliona liczb podaje osiem megabajtów — to tablica referencji, po osiem bajtów każda, bez samych liczb. `tracemalloc` pokazuje pełny koszt: lista kwadratów zajmuje czterdzieści megabajtów, bo obok tablicy referencji powstaje milion obiektów `int`. Ta sama suma obliczona przez wyrażenie generatorowe potrzebuje kilkuset bajtów: w każdej chwili istnieje jeden kwadrat. Funkcja `get_traced_memory()` zwraca parę: zużycie bieżące i szczytowe; funkcja `take_snapshot()` pozwala ponadto sprawdzić, które wiersze programu przydzieliły najwięcej pamięci. Pomiar pamięci wraca w następnym podrozdziale przy `__slots__`.

## Porównanie wersji funkcji Fibonacciego

Trzy wersje tej samej funkcji z rozdziałów 6 i 7 — rekurencja, pętla i rekurencja z pamięcią podręczną `functools.cache` — zestawione jednym pomiarem:

```python title="fibonacci-porownanie.py"
import functools
import time


def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


def fib_iter(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@functools.cache
def fib_cache(n):
    return n if n < 2 else fib_cache(n - 1) + fib_cache(n - 2)


for funkcja in (fib, fib_iter, fib_cache):
    start = time.perf_counter()
    wynik = funkcja(30)
    czas = time.perf_counter() - start
    print(f"{funkcja.__name__:10}{wynik:>8}  {czas * 1000:8.3f} ms")
print(fib_cache.cache_info())
```

```{ .text .no-copy }
fib         832040    77.452 ms
fib_iter    832040     0.004 ms
fib_cache   832040     0.042 ms
CacheInfo(hits=28, misses=31, maxsize=None, currsize=31)
```

| Wersja | Wywołań dla `n = 30` | Czas | Uwagi |
|---|---|---|---|
| `fib` (rekurencja) | 2 692 537 | ok. 78 ms | każdy wyraz liczony wielokrotnie |
| `fib_iter` (pętla) | 1 | ok. 2 µs | 30 obrotów pętli |
| `fib_cache` (memoizacja) | 31 obliczeń (59 wywołań, 28 z pamięci podręcznej) | ok. 40 µs | każdy wyraz liczony raz, wyniki w słowniku |

Różnica czterech rzędów wielkości nie wynika z „wolnego Pythona”, lecz z algorytmu: rekurencja bez pamięci podręcznej liczy `fib(28)` dwa razy, `fib(27)` trzy razy i tak dalej. Memoizacja z rozdziału [7. Moduły, pakiety i biblioteka standardowa](../07-moduly/functools.md#pamiec-podreczna-wynikow-cache-i-lru_cache) usuwa powtórzenia jednym wierszem, a pętla usuwa wywołania w ogóle. To najważniejsza lekcja tego rozdziału: zanim sięgniemy po narzędzia z następnych podrozdziałów, sprawdzamy algorytm.
