# Tablice ndarray

Podstawowym typem NumPy jest **tablica** `ndarray` (ang. *n-dimensional array*): ciąg liczb jednego typu, ułożony w jednym ciągłym bloku pamięci, o dowolnej liczbie wymiarów. Lista z rozdziału 5 przechowuje referencje do dowolnych obiektów; tablica przechowuje same liczby, a wszystkie operacje na niej wykonuje kod w C — stąd oszczędność pamięci oraz szybkość, którą zmierzyliśmy w rozdziale [13. Wydajność i optymalizacja](../13-wydajnosc/przyspieszanie-pythona.md#wektoryzacja-numpy). W tym podrozdziale poznajemy tworzenie tablic, ich atrybuty, indeksowanie z maskami, różnicę między widokiem a kopią oraz zapis i odczyt z plików.

## Od listy do tablicy

Funkcja `np.array()` buduje tablicę z listy — także zagnieżdżonej, co daje tablicę dwuwymiarową. Różnicę w zachowaniu widać przy pierwszym operatorze arytmetycznym:

```python title="lista-a-tablica.py"
import numpy as np

lista = [1, 2, 3, 4]
tablica = np.array(lista)

print(type(tablica), tablica)
print(lista * 2)
print(tablica * 2)
print(tablica + tablica)
print([x * 2 for x in lista])
print(np.array([[1, 2, 3], [4, 5, 6]]))
```

```{ .text .no-copy }
<class 'numpy.ndarray'> [1 2 3 4]
[1, 2, 3, 4, 1, 2, 3, 4]
[2 4 6 8]
[2 4 6 8]
[2, 4, 6, 8]
[[1 2 3]
 [4 5 6]]
```

Mnożenie listy przez liczbę powtarza elementy (rozdział 5); mnożenie tablicy mnoży każdy element. Tę własność — operator działa na całej tablicy, element po elemencie, bez pętli w kodzie Pythona — nazywamy **wektoryzacją** (ang. *vectorization*), a złożenie listowe z przedostatniego wiersza listingu jest jej ręcznym odpowiednikiem. Wydruk tablicy różni się od wydruku listy brakiem przecinków; `repr()` pokazuje pełny zapis `array([1, 2, 3, 4])`.

Tablica ma jeden typ elementów. Jeśli lista miesza typy, NumPy dobiera wspólny — liczby całkowite z ułamkami dają `float64`, a liczby z napisami dają tablicę napisów, nie liczb (`<U21` to napisy Unicode o długości do 21 znaków):

```{ .python .no-copy }
>>> import numpy as np
>>> np.array([1, 2.5]).dtype
dtype('float64')
>>> np.array([1, "a"])
array(['1', 'a'], dtype='<U21')
```

## Tworzenie tablic

Poza `np.array()` tablice tworzą funkcje wypełniające i funkcje generujące zakresy:

```python title="tworzenie.py"
import numpy as np

print(np.zeros(3))
print(np.ones((2, 3)))
print(np.full((2, 2), 7))
print(np.eye(3))
print(np.arange(0, 1, 0.25))
print(np.linspace(0, 1, 5))
print(np.arange(0, 1, 0.1).size, np.linspace(0, 1, 11).size)
```

```{ .text .no-copy }
[0. 0. 0.]
[[1. 1. 1.]
 [1. 1. 1.]]
[[7 7]
 [7 7]]
[[1. 0. 0.]
 [0. 1. 0.]
 [0. 0. 1.]]
[0.   0.25 0.5  0.75]
[0.   0.25 0.5  0.75 1.  ]
10 11
```

Kształt podajemy krotką: `(2, 3)` to dwa wiersze i trzy kolumny. `np.zeros()` i `np.ones()` tworzą tablice liczb zmiennoprzecinkowych (kropka po zerze w wydruku), `np.full()` przyjmuje typ od podanej wartości, a `np.eye()` daje macierz jednostkową. Funkcja `np.arange()` działa jak `range()` z rozdziału 4, ale przyjmuje krok ułamkowy i nie obejmuje końca przedziału; `np.linspace()` dzieli przedział domknięty na zadaną liczbę punktów — stąd ostatni wiersz wydruku: dziesięć elementów i jedenaście punktów. Dla kroków ułamkowych dokumentacja NumPy zaleca `linspace()`: błędy zaokrągleń w `arange()` mogą zmienić liczbę elementów o jeden, a przy `linspace()` liczba punktów jest zadana wprost.

## Atrybuty i typy elementów

Każda tablica zna swój kształt i typ elementów:

```python title="atrybuty.py"
import numpy as np

m = np.array([[1, 2, 3], [4, 5, 6]])
print(m.ndim, m.shape, m.size)
print(m.dtype, m.itemsize, m.nbytes)
print(np.array([1.5, 2]).dtype, np.array([True, False]).dtype)

male = np.array([100, 120], dtype=np.int8)
print(male * 2)
print(male.astype(np.int64) * 2)
print(np.array([1.7, 2.2]).astype(int))
```

```{ .text .no-copy }
2 (2, 3) 6
int64 8 48
float64 bool
[-56 -16]
[200 240]
[1 2]
```

Atrybut `ndim` to liczba wymiarów, `shape` — krotka z rozmiarem każdego wymiaru, `size` — liczba wszystkich elementów; `dtype` opisuje typ elementów, `itemsize` — jego rozmiar w bajtach, a `nbytes` — rozmiar całej tablicy. Sześć liczb całkowitych zajmuje 48 bajtów; lista sześciu liczb potrzebowałaby osobnego obiektu `int` na każdą z nich — po 28 bajtów, jak zmierzyliśmy w rozdziale [3. Nazwy i typy](../03-nazwy-typy/obiekty-i-pamiec.md#rozmiar-obiektow-i-zarzadzanie-pamiecia).

Domyślny typ całkowity to `int64` (na Windows od NumPy 2.0 — wcześniej `int32`), zmiennoprzecinkowy — `float64`, czyli ten sam format, którego używa typ `float` z rozdziału [3. Nazwy i typy](../03-nazwy-typy/typy-proste.md#typ-float). Typ można zadać argumentem `dtype=` albo zmienić metodą `astype()`, która domyślnie tworzy nową tablicę; konwersja z ułamka na liczbę całkowitą obcina część ułamkową. Typy o stałej szerokości mają ograniczony zakres: `int8` mieści liczby od −128 do 127, więc podwojenie wartości 100 i 120 daje −56 i −16 — NumPy nie zgłasza błędu przy operacjach na tablicach, tylko „zawija” wynik, jak procesor — to **przepełnienie** (ang. *overflow*); dla pojedynczych liczb, jak `np.int8(100) * 2`, wypisuje ostrzeżenie `RuntimeWarning`. To pierwsza różnica wobec Pythona, w którym `int` rośnie bez ograniczeń.

| Typ | Zakres lub precyzja | Typowe użycie |
|---|---|---|
| `np.int8`, `np.int16`, `np.int32`, `np.int64` | liczby całkowite ze znakiem, od 1 do 8 bajtów | liczniki, indeksy, dane całkowite |
| `np.uint8` | 0–255 | obrazy (jeden bajt na kanał piksela) |
| `np.float32`, `np.float64` | ok. 7 i ok. 15–16 cyfr znaczących | pomiary, obliczenia; `float32` oszczędza połowę pamięci |
| `np.complex128` | dwie liczby `float64` | liczby zespolone |
| `np.bool` (starsza nazwa `np.bool_` nadal działa) | `True`/`False` | maski logiczne |

Różnicę precyzji między `float32` a `float64` pokazuje eksperyment z laboratorium 3, rozwijający porównania z rozdziału [7. Moduły, pakiety i biblioteka standardowa](../07-moduly/struktura-projektu.md#porownania-liczb-zmiennoprzecinkowych) — sumowanie liczb `0.1`, `0.2` i `0.3` wczytanych jako napisy, czterema typami:

```python title="float32-float64.py"
from decimal import Decimal

import numpy as np

napisy = "0.1 0.2 0.3".split()

suma_float = sum(float(s) for s in napisy)
suma_decimal = sum(Decimal(s) for s in napisy)
suma_f32 = sum(np.float32(s) for s in napisy)
suma_f64 = sum(np.float64(s) for s in napisy)

print(f"float:   {suma_float!r}")
print(f"Decimal: {suma_decimal!r}")
print(f"float32: {suma_f32!r}")
print(f"float64: {suma_f64!r}")
print(f"wprost:  {0.1 + 0.2 + 0.3!r}")
print(suma_f32 == np.float32(0.6), suma_f64 == 0.6, np.isclose(suma_f64, 0.6))
```

```{ .text .no-copy }
float:   0.6
Decimal: Decimal('0.6')
float32: np.float32(0.6)
float64: np.float64(0.6000000000000001)
wprost:  0.6000000000000001
True False True
```

Wyniki `float` i `float64` różnią się, choć to ten sam format binarny, a `np.float64` jest podklasą `float`. Różnica bierze się z funkcji `sum()`: od Pythona 3.12 sumuje ona zwykłe liczby `float` z kompensacją błędów zaokrągleń (algorytm Neumaiera), lecz obiekty `np.float64` — jako podklasę — dodaje zwyczajnie, tak samo jak wyrażenie `0.1 + 0.2 + 0.3` wpisane wprost. `Decimal` z rozdziału 7 liczy dokładnie. Ciekawy jest przypadek `float32`: suma wychodzi „dokładnie” `0.6`, ale nie dlatego, że typ jest lepszy — jest mniej precyzyjny, więc błąd reprezentacji ginie w zaokrągleniu do siedmiu cyfr. Ostatni wiersz wydruku pokazuje, że `suma_f64 == 0.6` jest fałszem; porównania liczb zmiennoprzecinkowych nadal wykonujemy przez bliskość: `math.isclose()` z rozdziału 7 dla pojedynczych liczb, `np.isclose()` i `np.allclose()` dla tablic.

## Indeksowanie i wycinki

Indeksy i wycinki jednowymiarowe działają jak w listach; tablice dwuwymiarowe indeksujemy krotką `[wiersz, kolumna]`, w której każdy element może być wycinkiem. Dochodzą dwa mechanizmy nieznane listom — indeksowanie listą indeksów i maską logiczną:

```python title="indeksowanie.py"
import numpy as np

a = np.array([10, 20, 30, 40, 50])
print(a[0], a[-1], a[1:4], a[::2], a[::-1])
print(a[[0, 2, 4]])
print(a[a > 25])
print((a > 15) & (a < 45), a[(a > 15) & (a < 45)])
print(a[~(a > 25)])

m = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print(m[0, 1], m[1], m[:, 0])
print(m[0:2, 1:])
print(m[m % 2 == 0])
```

```{ .text .no-copy }
10 50 [20 30 40] [10 30 50] [50 40 30 20 10]
[10 30 50]
[30 40 50]
[False  True  True  True False] [20 30 40]
[10 20]
2 [4 5 6] [1 4 7]
[[2 3]
 [5 6]]
[2 4 6 8]
```

Zapis `m[0, 1]` to wywołanie `__getitem__` z krotką `(0, 1)` — mechanizm z rozdziału [11. Model danych](../11-model-danych/kolekcje-i-wywolania.md#metody-__getitem__-__setitem__-i-__delitem__); `m[1]` daje cały wiersz, `m[:, 0]` — całą kolumnę, a `m[0:2, 1:]` — podmacierz. **Indeksowanie listą** (ang. *fancy indexing*) wybiera elementy o podanych indeksach w podanej kolejności. **Maska logiczna** (ang. *boolean mask*) to tablica wartości `True`/`False` tego samego kształtu; porównanie `a > 25` tworzy ją elementowo, a `a[maska]` zwraca elementy, dla których maska jest prawdziwa — zawsze jako tablicę jednowymiarową, także dla macierzy `m`. Maski łączymy operatorami `&`, `|` i `~` — bitowymi z rozdziału 3, które NumPy przeciąża do działania elementowego. Porównania ujmujemy w nawiasy, bo operatory bitowe wiążą silniej niż porównania. Słowa `and`, `or` i `not` nie działają:

```{ .python .no-copy }
>>> a[(a > 15) and (a < 45)]
Traceback (most recent call last):
  ...
ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
```

Operator `and` wywołuje `bool()` na tablicy (rozdział 11), a wartość logiczna tablicy wieloelementowej nie jest określona — stąd błąd i podpowiedź o `any()` i `all()`. Maski przydają się też do przypisań: `a[a < 0] = 0` zeruje wszystkie elementy ujemne bez pętli.

## Widok a kopia

Wycinek listy jest kopią (rozdział [5. Typy złożone](../05-typy-zlozone/referencje-i-kopiowanie.md#kopiowanie-pytkie-i-gebokie)); wycinek tablicy jest **widokiem** (ang. *view*) — nową tablicą odwołującą się do tego samego bloku pamięci. Zmiana widoku zmienia oryginał:

```python title="widok-a-kopia.py"
import numpy as np

a = np.array([1, 2, 3, 4, 5])
b = a[1:4]
b[0] = 99
print(a, b.base is a)

c = a[1:4].copy()
c[0] = -1
print(a, c.base is None)

d = a[[0, 2, 4]]
d[0] = 0
print(a, d.base is None)

lista = [1, 2, 3, 4, 5]
wycinek = lista[1:4]
wycinek[0] = 99
print(lista)
```

```{ .text .no-copy }
[ 1 99  3  4  5] True
[ 1 99  3  4  5] True
[ 1 99  3  4  5] True
[1, 2, 3, 4, 5]
```

Atrybut `base` wskazuje tablicę, której pamięć widok współdzieli; dla kopii jest równy `None`. Widoki są zamierzoną cechą biblioteki — pozwalają pracować na fragmencie dużej tablicy bez kopiowania — ale bywają źródłem trudnych błędów, gdy funkcja modyfikuje otrzymany wycinek. Gdy potrzebna jest niezależna tablica, wywołujemy `copy()`. Funkcje kształtu z tabeli — `reshape()`, `T`, `ravel()`, `flatten()` — omawiamy w następnym podrozdziale.

| Widok (wspólna pamięć) | Kopia (osobna pamięć) |
|---|---|
| wycinek `a[1:4]`, `a[:, 0]` | indeksowanie listą `a[[0, 2]]` i maską `a[a > 0]` |
| `reshape()` (dla tablic ciągłych w pamięci), `T` | `copy()`, `flatten()`, `astype()` |
| `ravel()` — dla tablic ciągłych w pamięci | operacje arytmetyczne `a * 2`, `a + b` |

## Zapis i odczyt

Tablice zapisujemy w binarnym formacie NumPy (`.npy`, jedna tablica; `.npz`, kilka tablic pod nazwami) albo tekstowo. Do plików CSV z samymi liczbami wystarczy `np.loadtxt()`; plik w formacie CSV z rozdziału [9. Wejście, wyjście i pliki](../09-wejscie-wyjscie/csv-i-json.md#format-csv-i-modu-csv) wczytujemy z pominięciem nagłówka:

```text title="pomiary.csv"
czas,temperatura
0,20.5
1,21.0
2,21.4
3,22.1
```

```python title="zapis-odczyt.py"
from pathlib import Path

import numpy as np

dane = np.loadtxt("pomiary.csv", delimiter=",", skiprows=1)
print(dane.shape, dane.dtype)
print(f"średnia temperatura: {dane[:, 1].mean():.2f}")

np.save("dane.npy", dane)
print(np.load("dane.npy")[-1])

np.savez("zestaw.npz", czas=dane[:, 0], temperatura=dane[:, 1])
with np.load("zestaw.npz") as zestaw:
    print(zestaw["temperatura"].max())

np.savetxt("odchylenia.txt", dane[:, 1] - dane[:, 1].mean(), fmt="%.2f")
print(Path("odchylenia.txt").read_text(encoding="utf-8"))
```

```{ .text .no-copy }
(4, 2) float64
średnia temperatura: 21.25
[ 3.  22.1]
22.1
-0.75
-0.25
0.15
0.85
```

`np.loadtxt()` domyślnie oczekuje pliku w pełni liczbowego; kolumny tekstowe, brakujące wartości i nazwy kolumn to zadanie dla modułu `csv` z rozdziału 9 albo — wygodniej — dla biblioteki pandas, która buduje na tablicach NumPy tabele z nazwanymi kolumnami; omawiamy ją w części II książki. <!-- TODO: link po powstaniu rozdziału o pandas --> Format `.npy` zachowuje typ i kształt tablicy bez strat i wczytuje się wielokrotnie szybciej niż tekst, ale czytają go tylko programy z NumPy; `savetxt()` z argumentem `fmt=` daje plik czytelny dla arkusza kalkulacyjnego.
