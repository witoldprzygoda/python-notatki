# Operacje na tablicach

Siła NumPy leży nie w samej tablicy, lecz w operacjach na całych tablicach: funkcjach działających elementowo, dopasowywaniu kształtów, agregacjach wzdłuż osi i przekształceniach kształtu bez kopiowania danych. W tym podrozdziale poznajemy je po kolei, mierzymy zysk wektoryzacji zapowiedziany w rozdziale 13 i na koniec zaglądamy do algebry liniowej.

## Operacje elementowe i funkcje uniwersalne

Operatory arytmetyczne i porównania działają elementowo; tak samo **funkcje uniwersalne** (ang. *universal functions*, ufunc) — `np.sin()`, `np.sqrt()`, `np.exp()`, `np.log()`, `np.abs()` — które przyjmują tablicę i zwracają tablicę tego samego kształtu:

```python title="ufunc.py"
import numpy as np

a = np.array([1, 2, 3])
b = np.array([10, 20, 30])
print(a + b, a * b, b / a, b // a, a**2)

x = np.array([0, np.pi / 2, np.pi])
print(np.sin(x))
print(np.isclose(np.sin(x), [0, 1, 0]))
print(np.sqrt(a), np.exp(a).round(2))

print(a > 1, (a > 1).any(), (a > 1).all())
print(np.where(a > 1, a, 0))
print(np.where(a > 1, "duże", "małe"))
```

```{ .text .no-copy }
[11 22 33] [10 40 90] [10. 10. 10.] [10 10 10] [1 4 9]
[0.0000000e+00 1.0000000e+00 1.2246468e-16]
[ True  True  True]
[1.         1.41421356 1.73205081] [ 2.72  7.39 20.09]
[False  True  True] True False
[0 2 3]
['małe' 'duże' 'duże']
```

Funkcje z modułu `math` przyjmują tylko pojedyncze liczby; ich odpowiedniki w NumPy działają na całej tablicy i wykonują pętlę w C. Wynik `np.sin(np.pi)` to nie zero, lecz `1.22e-16` — liczba π jest w `float64` przybliżona, więc porównania z oczekiwaną wartością wykonujemy przez `np.isclose()`. Metody `any()` i `all()` sprowadzają tablicę logiczną do jednej wartości. Funkcja `np.where(warunek, gdy_prawda, gdy_fałsz)` to wektorowy odpowiednik wyrażenia warunkowego z rozdziału 4: wybiera elementowo z dwóch tablic lub wartości.

## Rozgłaszanie — broadcasting

Operacja na dwóch tablicach różnych kształtów nie musi kończyć się błędem. **Rozgłaszanie** (ang. *broadcasting*) dopasowuje kształty według dwóch reguł: wymiary porównujemy od prawej, a wymiar o rozmiarze 1 (albo brakujący) jest rozciągany do rozmiaru drugiej tablicy — bez kopiowania danych:

```python title="broadcasting.py"
import numpy as np

a = np.array([1, 2, 3])
print(a + 10, a * 2.5)

m = np.array([[1, 2, 3], [4, 5, 6]])
v = np.array([10, 20, 30])
print(m + v)

kolumna = np.array([[1], [2], [3]])
wiersz = np.array([10, 20, 30])
print(kolumna.shape, wiersz.shape)
print(kolumna + wiersz)
```

```{ .text .no-copy }
[11 12 13] [2.5 5.  7.5]
[[11 22 33]
 [14 25 36]]
(3, 1) (3,)
[[11 21 31]
 [12 22 32]
 [13 23 33]]
```

```{ .python .no-copy }
>>> np.array([1, 2, 3]) + np.array([1, 2])
Traceback (most recent call last):
  ...
ValueError: operands could not be broadcast together with shapes (3,) (2,)
```

Skalar jest rozgłaszany na całą tablicę; wektor o kształcie `(3,)` dodany do macierzy `(2, 3)` jest dodawany do każdego wiersza; kolumna `(3, 1)` i wiersz `(3,)` dają macierz `(3, 3)` — tabliczkę dodawania. Kształty `(3,)` i `(2,)` nie spełniają żadnej z reguł, stąd `ValueError`. Rozgłaszanie zastępuje większość pętli „dla każdego wiersza”: odjęcie od macierzy średniej każdej kolumny to jedno wyrażenie `m - m.mean(axis=0)` (argument `axis` omawiamy w następnej sekcji).

## Agregacje i oś `axis`

**Agregacja** sprowadza tablicę do jednej liczby — albo do jednej liczby na wiersz lub kolumnę, gdy podamy oś:

```python title="agregacje.py"
import numpy as np

a = np.array([3, 1, 4, 1, 5, 9])
print(a.sum(), a.mean(), a.std().round(3), a.min(), a.max())
print(a.argmin(), a.argmax(), a.cumsum())

m = np.array([[1, 2, 3], [4, 5, 6]])
print(m.sum())
print(m.sum(axis=0))
print(m.sum(axis=1))
print(m.mean(axis=0), m.max(axis=1))
```

```{ .text .no-copy }
23 3.8333333333333335 2.734 1 9
1 5 [ 3  4  8  9 14 23]
21
[5 7 9]
[ 6 15]
[2.5 3.5 4.5] [3 6]
```

Argument `axis` wskazuje oś, **wzdłuż której** agregacja przebiega — i która znika z wyniku. Dla macierzy `axis=0` sumuje w dół, przez wiersze, zostawiając jedną wartość na kolumnę; `axis=1` sumuje w prawo, przez kolumny, zostawiając jedną wartość na wiersz:

```{ .text .no-copy }
          axis=1 →
axis=0  [[1 2 3]  → 6
  ↓      [4 5 6]] → 15
          ↓ ↓ ↓
          5 7 9
```

`argmin()` i `argmax()` zwracają indeks elementu, nie jego wartość; `cumsum()` — sumy narastające. Te same funkcje istnieją w postaci `np.sum(m, axis=0)`; obie formy są równoważne.

## Przekształcanie kształtu

Ta sama pamięć może być widziana jako tablica innego kształtu:

```python title="ksztalt.py"
import numpy as np

a = np.arange(12)
b = a.reshape(3, 4)
print(b)
print(a.reshape(2, -1).shape, b.T.shape)
print(b.ravel().base is a, b.flatten().base is None)

m = np.arange(6).reshape(2, 3)
print(np.vstack([m, m]).shape, np.hstack([m, m]).shape)
print(np.concatenate([m, m], axis=1))
```

```{ .text .no-copy }
[[ 0  1  2  3]
 [ 4  5  6  7]
 [ 8  9 10 11]]
(2, 6) (4, 3)
True True
(4, 3) (2, 6)
[[0 1 2 0 1 2]
 [3 4 5 3 4 5]]
```

`reshape()` zwraca widok o nowym kształcie, gdy układ pamięci na to pozwala (dla tablicy ciągłej — zawsze), w przeciwnym razie kopię; wartość `-1` w jednym wymiarze oznacza „oblicz z pozostałych”. `T` transponuje macierz. `ravel()` spłaszcza do jednego wymiaru jako widok (gdy dane są ciągłe w pamięci), `flatten()` — zawsze jako kopia. `vstack()` łączy tablice w pionie, `hstack()` w poziomie, a `concatenate()` wzdłuż wskazanej osi.

## Liczby losowe — `default_rng()`

Generator liczb losowych tworzymy funkcją `np.random.default_rng()`; z zadanym **ziarnem** (ang. *seed*) daje powtarzalne ciągi, co pozwala sprawdzać wyniki:

```python title="losowe.py"
import numpy as np

rng = np.random.default_rng(42)
print(rng.random(3))
print(rng.integers(0, 10, size=5))
print(rng.normal(0, 1, size=3).round(3))
print(rng.choice(["a", "b", "c"], size=5))

talia = np.arange(5)
rng.shuffle(talia)
print(talia)
```

```{ .text .no-copy }
[0.77395605 0.43887844 0.85859792]
[0 6 2 0 5]
[ 0.128 -0.316 -0.017]
['c' 'c' 'b' 'b' 'b']
[0 3 4 2 1]
```

`random()` losuje z przedziału [0, 1), `integers()` — liczby całkowite z przedziału prawostronnie otwartego jak `range()`, `normal()` — z rozkładu normalnego o podanej średniej i odchyleniu, `choice()` — elementy sekwencji, a `shuffle()` tasuje tablicę w miejscu. W starszym kodzie i w wielu samouczkach spotkamy funkcje `np.random.seed()`, `np.random.rand()` i `np.random.randn()` — działają, ale korzystają ze wspólnego stanu globalnego; w nowym kodzie używamy generatora.

## Wektoryzacja — pomiar

W rozdziale [13. Wydajność i optymalizacja](../13-wydajnosc/przyspieszanie-pythona.md#wektoryzacja-numpy) porównaliśmy trzy zapisy sumy kwadratów; teraz mierzymy je w środowisku kursu i dodajemy czwarty — iloczyn skalarny operatorem `@`, do którego wracamy w ostatniej sekcji tego podrozdziału:

```python title="wektoryzacja.py"
import time

import numpy as np

n = 1_000_000
dane = list(range(n))
tablica = np.arange(n)


def mierz(etykieta, funkcja):
    start = time.perf_counter()
    wynik = funkcja()
    czas = time.perf_counter() - start
    print(f"{etykieta:<22}{czas * 1000:7.2f} ms  wynik: {wynik}")


def petla():
    suma = 0
    for x in dane:
        suma += x * x
    return suma


mierz("pętla", petla)
mierz("sum() z generatorem", lambda: sum(x * x for x in dane))
mierz("NumPy", lambda: int(np.sum(tablica * tablica)))
mierz("NumPy, iloczyn @", lambda: int(tablica @ tablica))
```

```{ .text .no-copy }
pętla                   33.09 ms  wynik: 333332833333500000
sum() z generatorem     43.83 ms  wynik: 333332833333500000
NumPy                    2.31 ms  wynik: 333332833333500000
NumPy, iloczyn @         0.46 ms  wynik: 333332833333500000
```

Pomiar potwierdza szacunek z rozdziału 13: wersja NumPy jest kilkanaście razy szybsza od pętli mimo pośredniej tablicy miliona kwadratów, którą tworzy `tablica * tablica`; iloczyn skalarny `tablica @ tablica` liczy to samo bez tablicy pośredniej i jest jeszcze kilkakrotnie szybszy. Cały zysk bierze się z tego, co opisaliśmy w rozdziale 13: pętla przebiega w C na liczbach w ciągłym bloku pamięci, bez obiektów Pythona i sprawdzania typów. Wynik jest poprawny, bo `int64` mieści liczby do ok. 9,2·10¹⁸ — przy większych sumach trzeba pamiętać o przepełnieniu z poprzedniego podrozdziału.

## Przydatne funkcje

| Funkcja | Działanie |
|---|---|
| `np.sort(a)`, `a.argsort()` | posortowana kopia; indeksy, które sortują tablicę |
| `np.unique(a, return_counts=True)` | wartości bez powtórzeń i ich liczności |
| `np.clip(a, dolna, górna)` | ogranicza wartości do przedziału |
| `np.round(a, 2)`, `a.round(2)` | zaokrąglenie elementowe |
| `np.nanmean(a)`, `np.nansum(a)` | agregacje pomijające `np.nan` (zwykłe `mean()` zwraca `nan`) |
| `np.isclose(a, b)`, `np.allclose(a, b)` | porównanie zmiennoprzecinkowe elementowe i zbiorcze |
| `np.meshgrid(x, y)` | siatki współrzędnych do wykresów funkcji dwóch zmiennych |

Pełną listę funkcji zawiera dokumentacja NumPy; przed napisaniem własnej pętli warto sprawdzić, czy operacja nie ma już gotowej, wektorowej postaci.

## Algebra liniowa (dla dociekliwych)

Operator `@` — metoda `__matmul__` z rozdziału [11. Model danych](../11-model-danych/operatory.md#operator-i-metoda-rozdzielana-wedug-typu-dla-dociekliwych) — mnoży macierze; gwiazdka mnoży elementowo. Moduł `np.linalg` dostarcza wyznacznik, macierz odwrotną i rozwiązywanie układów równań:

```python title="algebra.py"
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
print(A @ B)
print(A * B)
print(np.linalg.det(A).round(6))
print(np.linalg.inv(A).round(6))

b = np.array([5, 11])
x = np.linalg.solve(A, b)
print(x, np.allclose(A @ x, b))
```

```{ .text .no-copy }
[[19 22]
 [43 50]]
[[ 5 12]
 [21 32]]
-2.0
[[-2.   1. ]
 [ 1.5 -0.5]]
[1. 2.] True
```

Układ równań `A @ x = b` rozwiązujemy funkcją `solve()`, nie przez `inv(A) @ b` — jest szybsza i dokładniejsza numerycznie. Zaokrąglenie w wydruku ukrywa błędy rzędu 10⁻¹⁶, które zobaczymy, wypisując `det(A)` wprost.
