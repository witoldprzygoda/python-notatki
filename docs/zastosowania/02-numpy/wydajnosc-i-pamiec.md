# Wydajność i pamięć

NumPy jest szybki, gdy operacje przebiegają w C na całych tablicach; wystarczy jedna pętla w Pythonie albo jedna niepotrzebna kopia miliona elementów, aby zysk zniknął. Ten podrozdział pokazuje, na co uważać: typ elementów, kopie i tymczasowe tablice, pozorną wektoryzację, dane większe niż pamięć — oraz listę pułapek, które zbieramy z całego rozdziału.

## Typ elementów a pamięć

```python title="pamiec.py"
import numpy as np

n = 1_000_000
for dtype in (np.float64, np.float32, np.int32, np.int16, np.uint8):
    tablica = np.ones(n, dtype=dtype)
    print(f"{tablica.dtype.name:<8}{tablica.nbytes / 1e6:6.1f} MB")

print(np.finfo(np.float32).eps, np.finfo(np.float64).eps)
print(np.float32(16_777_216) + np.float32(1) == np.float32(16_777_216))
obraz = np.zeros((1080, 1920, 3), dtype=np.uint8)
print(obraz.nbytes / 1e6, "MB")
```

```{ .text .no-copy }
float64    8.0 MB
float32    4.0 MB
int32      4.0 MB
int16      2.0 MB
uint8      1.0 MB
1.1920929e-07 2.220446049250313e-16
True
6.2208 MB
```

Milion liczb `float64` zajmuje 8 MB, `float32` — połowę, a `uint8` — jedną ósmą; przy danych liczonych w setkach milionów elementów wybór typu decyduje, czy analiza zmieści się w pamięci. Ceną `float32` jest precyzja: `finfo().eps` — najmniejsza względna różnica, jaką typ rozróżnia — wynosi około 10⁻⁷ wobec 10⁻¹⁶ dla `float64`, czyli około siedmiu cyfr znaczących zamiast szesnastu, więc dodanie jedynki do 16 777 216 nic nie zmienia. Regułą jest `float64` do obliczeń i `float32` do przechowywania dużych zbiorów, gdy taka dokładność wystarcza; obrazy — kanały 0–255 — to naturalnie `uint8`. Konwersja `astype()` tworzy kopię, więc zmianę typu wykonujemy raz, przy wczytaniu.

## Operacje w miejscu i argument `out=`

```python title="w-miejscu.py"
import numpy as np

a = np.arange(5, dtype=np.float64)
przed = id(a)
a = a * 2
print(id(a) == przed)

a = np.arange(5, dtype=np.float64)
przed = id(a)
a *= 2
print(id(a) == przed, a)

x = np.linspace(0, 1, 5)
wynik = np.empty_like(x)
np.multiply(x, 10, out=wynik)
np.add(wynik, 1, out=wynik)
print(wynik)

calkowite = np.arange(5)
try:
    calkowite *= 1.5
except TypeError as e:
    print(type(e).__name__, "-", e)
```

```{ .text .no-copy }
False
True [0. 2. 4. 6. 8.]
[ 1.   3.5  6.   8.5 11. ]
UFuncTypeError - Cannot cast ufunc 'multiply' output from dtype('float64') to dtype('int64') with casting rule 'same_kind'
```

Wyrażenie `a = a * 2` tworzy nową tablicę i przypisuje ją nazwie; `a *= 2` zmienia tablicę w miejscu — bez przydzielania pamięci, co przy dużych danych liczy się bardziej niż samo mnożenie. Każda funkcja uniwersalna przyjmuje `out=`, do której zapisuje wynik zamiast tworzyć nową tablicę; wyrażenie `x * 10 + 1` tworzy po drodze tablicę tymczasową, a dwa wywołania z `out=` — nie. Operacja w miejscu nie może zmienić typu: mnożenie tablicy całkowitej przez ułamek w miejscu kończy się wyjątkiem `UFuncTypeError` (podklasą `TypeError`), bo wynik zmiennoprzecinkowy nie mieści się w tablicy całkowitej.

## Pętle, `np.vectorize` i prawdziwa wektoryzacja

```python title="wektoryzacja2.py"
import timeit

import numpy as np

x = np.linspace(0, 10, 200_000)


def petla(x):
    wynik = np.empty_like(x)
    for i in range(x.size):
        wynik[i] = x[i] ** 2 if x[i] < 5 else 10 * x[i]
    return wynik


def wektor_python(x):
    return np.vectorize(lambda v: v**2 if v < 5 else 10 * v)(x)


def wektor_numpy(x):
    return np.where(x < 5, x**2, 10 * x)


for funkcja in (petla, wektor_python, wektor_numpy):
    czas = min(timeit.repeat(lambda: funkcja(x), number=1, repeat=3))
    print(f"{funkcja.__name__:<14}{czas * 1000:8.2f} ms")
print(np.allclose(petla(x), wektor_numpy(x)))
```

```{ .text .no-copy }
petla            35.47 ms
wektor_python    22.53 ms
wektor_numpy      1.07 ms
True
```

`np.vectorize()` przyjmuje zwykłą funkcję i pozwala wywołać ją na tablicy, ale wykonuje ją w pętli w Pythonie — to wygoda zapisu, nie przyspieszenie, o czym dokumentacja mówi wprost. Prawdziwa wektoryzacja polega na przepisaniu warunku na operacje tablicowe: `np.where()` liczy obie gałęzie dla wszystkich elementów i wybiera właściwą — dziesiątki razy szybciej mimo nadmiarowych obliczeń. Inne wzorce zastępujące pętle: sumy narastające `cumsum()`, różnice sąsiednich elementów `np.diff()`, wyszukiwanie `searchsorted()` i grupowanie `np.add.at()` z poprzednich podrozdziałów. Gdy warunek zależy od poprzedniego elementu i nie da się go zapisać tablicowo, pozostaje kompilacja pętli w Numbie z rozdziału 13 „Python Notatki”.

## Duże dane — porcje i `memmap`

Tablica większa niż pamięć nie musi być wczytywana w całości. Plik `.npy` można **zmapować w pamięci** (ang. *memory mapping*): system operacyjny wczytuje z dysku tylko te fragmenty, do których program sięga:

```python title="memmap.py"
import numpy as np

ksztalt = (20_000, 1_000)
plik = np.lib.format.open_memmap("duze.npy", mode="w+", dtype=np.float32, shape=ksztalt)
rng = np.random.default_rng(42)
for start in range(0, ksztalt[0], 5_000):
    plik[start : start + 5_000] = rng.normal(size=(5_000, ksztalt[1]))
plik.flush()
del plik

dane = np.load("duze.npy", mmap_mode="r")
print(type(dane).__name__, dane.shape, dane.dtype, f"{dane.nbytes / 1e6:.0f} MB w pliku")
srednie_wierszy = np.empty(ksztalt[0], dtype=np.float32)
for start in range(0, ksztalt[0], 5_000):
    srednie_wierszy[start : start + 5_000] = dane[start : start + 5_000].mean(axis=1)
print(srednie_wierszy.mean().round(4), srednie_wierszy.std().round(4))
```

```{ .text .no-copy }
memmap (20000, 1000) float32 80 MB w pliku
-1e-04 0.0316
```

`open_memmap()` tworzy plik `.npy` o zadanym kształcie bez trzymania go w pamięci; zapisujemy go porcjami po pięć tysięcy wierszy, a `np.load()` z `mmap_mode="r"` otwiera go w trybie tylko do odczytu jako obiekt `memmap`, który zachowuje się jak tablica. Obliczenia prowadzimy porcjami — każda porcja to widok na fragment pliku, którego dane system wczytuje dopiero przy obliczeniu — a wyniki zbieramy w małej tablicy. `flush()` zapisuje bufory na dysk, a `del` zamyka mapowanie przed ponownym otwarciem pliku. Odchylenie średnich wierszy, 0,0316, to 1/√1000 — zgodnie z tym, co pokazało błądzenie losowe w poprzednim podrozdziale. Osiemdziesiąt megabajtów mieści się w pamięci bez trudu; ten sam kod działa jednak dla osiemdziesięciu gigabajtów. Przy danych tabelarycznych tej wielkości wygodniejsze są narzędzia z dalszej części ścieżki, które porcjowanie wykonują same. <!-- TODO: link po powstaniu rozdziału o pandas -->

## Typowe pułapki

```python title="pulapki.py"
import numpy as np

print(np.array([250], dtype=np.uint8) + 10, np.array([250], dtype=np.uint8) + np.int64(10))
print((np.array([1, 2, 3]) / 2).dtype, (np.array([1, 2, 3]) // 2).dtype)
print(np.array([0.1 + 0.2]) == 0.3, np.isclose(np.array([0.1 + 0.2]), 0.3))

a = np.arange(6)
a[a > 3][0] = 100
print(a)
a[a > 3] = 100
print(a)

wyniki = []
for i in range(5):
    wyniki.append(i**2)
print(np.array(wyniki))
```

```{ .text .no-copy }
[4] [260]
float64 int64
[False] [ True]
[0 1 2 3 4 5]
[  0   1   2   3 100 100]
[ 0  1  4  9 16]
```

- **Przepełnienie typów o stałej szerokości** — `uint8` zawija 260 do 4; dodanie skalara `int64` przenosi obliczenie do szerszego typu, ale to szczegół reguł promocji, nie zabezpieczenie: typ dobieramy do zakresu danych.
- **Dzielenie** `/` zawsze daje typ zmiennoprzecinkowy — dla tablic całkowitych `float64`; dzielenie całkowite to `//`.
- **Porównanie liczb zmiennoprzecinkowych** — `==` zawodzi jak w rozdziale 3 „Python Notatki”; `np.isclose()` i `np.allclose()` porównują z tolerancją.
- **Przypisanie do wyniku indeksowania maską** — `a[a > 3][0] = 100` zmienia kopię, a zmiana przepada; poprawne jest `a[a > 3] = 100`, bo wtedy przypisanie trafia wprost do `a`.
- **Rozbudowywanie tablicy w pętli** — `np.append()` kopiuje całość przy każdym wywołaniu; wyniki zbieramy w liście i zamieniamy na tablicę raz, na końcu.
- **Pomylone osie** — `axis=0` agreguje w dół (przez wiersze), `axis=1` w prawo; przy wątpliwościach sprawdzamy kształt wyniku, a nie wartości.
- **`and`/`or` na tablicach** — zamiast nich `&`, `|` i nawiasy wokół porównań, jak w rozdziale 14.

## Kiedy sięgnąć dalej

NumPy wystarcza, gdy dane są tablicą liczb jednego typu, a operacje dają się zapisać na całych tablicach. Trzy sygnały, że potrzebne jest inne narzędzie: kolumny różnych typów z nazwami i brakami — pandas z dalszej części ścieżki; pętla, której nie da się zwektoryzować — Numba z rozdziału 13; algorytmy numeryczne spoza `np.linalg` — całkowanie, optymalizacja, statystyka, przetwarzanie sygnałów — SciPy, zbudowane na tablicach NumPy i używające ich w taki sam sposób.
