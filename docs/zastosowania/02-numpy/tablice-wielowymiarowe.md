# Tablice wielowymiarowe

Dane pomiarowe rzadko mieszczą się w dwóch wymiarach: kilka stacji, każda mierzy przez wiele dni kilka wielkości — to trzy osie. NumPy obsługuje dowolną liczbę osi tą samą składnią, co macierze z rozdziału 14 „Python Notatki”; trudność leży nie w zapisie, lecz w ustaleniu, co oznacza każda z osi. Ten podrozdział ćwiczy to myślenie na jednym zestawie danych.

## Osie i kształt

Zestaw danych generujemy z ziarnem, aby wyniki były powtarzalne: trzy stacje, siedem dni, dwie wielkości — temperatura i wilgotność:

```python title="osie.py"
import numpy as np

rng = np.random.default_rng(42)
temperatura = rng.normal(15, 5, size=(3, 7)).round(1)
wilgotnosc = rng.normal(60, 10, size=(3, 7)).round(0)
pomiary = np.stack([temperatura, wilgotnosc], axis=2)

print(pomiary.shape, pomiary.ndim)
print(pomiary[0])
print(pomiary[0, :, 0])
print(pomiary[..., 0].shape, pomiary[:, 0].shape, pomiary[1, 2])
```

```{ .text .no-copy }
(3, 7, 2) 3
[[16.5 53. ]
 [ 9.8 72. ]
 [18.8 58. ]
 [19.7 56. ]
 [ 5.2 56. ]
 [ 8.5 65. ]
 [15.6 64. ]]
[16.5  9.8 18.8 19.7  5.2  8.5 15.6]
(3, 7) (3, 2) [10.7 81. ]
```

Kształt `(3, 7, 2)` czytamy od zewnątrz: oś 0 to stacje, oś 1 — dni, oś 2 — wielkości. `pomiary[0]` to macierz jednej stacji (dni × wielkości), `pomiary[0, :, 0]` — temperatury tej stacji ze wszystkich dni, a `pomiary[:, 0]` — pomiary wszystkich stacji z pierwszego dnia. **Wielokropek** (ang. *ellipsis*) `...` zastępuje dowolną liczbę pełnych wycinków: `pomiary[..., 0]` znaczy „wszystko, ostatnia oś: temperatura” i daje macierz stacje × dni. Funkcja `np.stack()` złożyła dwie macierze `(3, 7)` w tablicę trójwymiarową, dokładając nową oś na końcu.

## Nowe osie i rozgłaszanie w trzech wymiarach

Rozgłaszanie z rozdziału 14 dopasowuje kształty od prawej; przy trzech osiach trzeba czasem dodać oś o rozmiarze 1 we właściwym miejscu. Służy do tego indeks `None` (synonim `np.newaxis`) albo argument `keepdims=True` w agregacji:

```python title="nowe-osie.py"
import numpy as np

rng = np.random.default_rng(42)
temperatura = rng.normal(15, 5, size=(3, 7)).round(1)
wilgotnosc = rng.normal(60, 10, size=(3, 7)).round(0)
pomiary = np.stack([temperatura, wilgotnosc], axis=2)

srednie = pomiary.mean(axis=1)
print(srednie.shape, srednie.round(1))
odchylenia = pomiary - srednie[:, None, :]
print(odchylenia.shape, odchylenia.mean(axis=1).round(6))

srednie_k = pomiary.mean(axis=1, keepdims=True)
print(srednie_k.shape, np.allclose(pomiary - srednie_k, odchylenia))
znormalizowane = (pomiary - srednie_k) / pomiary.std(axis=1, keepdims=True)
print(znormalizowane.std(axis=1).round(6))

wagi = np.array([1.0, 0.5])
print((pomiary * wagi).shape, (pomiary * wagi[None, None, :]).shape)
```

```{ .text .no-copy }
(3, 2) [[13.4 60.6]
 [16.2 62.6]
 [14.8 61.9]]
(3, 7, 2) [[0. 0.]
 [0. 0.]
 [0. 0.]]
(3, 1, 2) True
[[1. 1.]
 [1. 1.]
 [1. 1.]]
(3, 7, 2) (3, 7, 2)
```

Średnia po dniach (`axis=1`) ma kształt `(3, 2)` — stacje × wielkości — i nie da się jej odjąć od `(3, 7, 2)` wprost, bo osie nie pasują od prawej. `srednie[:, None, :]` wstawia oś dni o rozmiarze 1: kształt `(3, 1, 2)` rozgłasza się na `(3, 7, 2)` i każda stacja dostaje własną średnią. Średnie odchyleń są zerowe z dokładnością do błędów zaokrągleń — `-0.` w wydruku to ujemna liczba rzędu 10⁻¹⁶ zaokrąglona do zera, jak `np.sin(np.pi)` w rozdziale 14. `keepdims=True` daje ten sam wynik bez ręcznego wstawiania osi i jest czytelniejsze, gdy tę samą operację powtarzamy dla średniej i odchylenia — przy normalizacji danych, po której każda stacja i wielkość ma odchylenie równe jeden. Wektor `(2,)` rozgłasza się na ostatnią oś bez dodatkowych zabiegów, bo dopasowanie od prawej przypada na oś wielkości — zapis `wagi[None, None, :]` jest równoważny i zbędny.

## Agregacje wzdłuż wielu osi

Argument `axis` przyjmuje krotkę osi — `axis=(0, 1)` uśrednia po stacjach i dniach naraz, zostawiając jedną wartość na wielkość — a funkcja `np.unravel_index()` zamienia indeks z `argmax()` na współrzędne w tablicy:

```python title="agregacje-3d.py"
import numpy as np

rng = np.random.default_rng(42)
temperatura = rng.normal(15, 5, size=(3, 7)).round(1)
wilgotnosc = rng.normal(60, 10, size=(3, 7)).round(0)
pomiary = np.stack([temperatura, wilgotnosc], axis=2)

print(pomiary.mean(axis=(0, 1)).round(1), pomiary.mean(axis=(0, 1)).shape)
print(pomiary[..., 0].max(axis=1))
najcieplej = tuple(int(i) for i in np.unravel_index(temperatura.argmax(), temperatura.shape))
print(temperatura.argmax(), najcieplej)
print(f"stacja {najcieplej[0]}, dzień {najcieplej[1]}: {temperatura[najcieplej]} °C")
print((temperatura > 20).sum(axis=1), (temperatura > 20).any(axis=0))
```

```{ .text .no-copy }
[14.8 61.7] (2,)
[19.7 20.6 19.4]
13 (1, 6)
stacja 1, dzień 6: 20.6 °C
[0 1 0] [False False False False False False  True]
```

`argmax()` bez osi zwraca indeks w spłaszczonej tablicy; `unravel_index()` przelicza go na krotkę współrzędnych (liczb NumPy, które `int()` zamienia na zwykłe), którą można od razu użyć do indeksowania. Maska `temperatura > 20` zsumowana wzdłuż osi dni liczy ciepłe dni każdej stacji, a `any(axis=0)` mówi, w które dni choć jedna stacja przekroczyła próg — typowe pytania o dane wielowymiarowe sprowadzają się do wyboru osi.

## Łączenie, dzielenie i przestawianie

Poza `concatenate()` z rozdziału 14 tablice składa `np.stack()`, dzieli `np.split()`, a osie przestawiają `moveaxis()` i `transpose()`:

```python title="ksztalty.py"
import numpy as np

a = np.arange(6).reshape(2, 3)
b = np.arange(6, 12).reshape(2, 3)

print(np.stack([a, b]).shape, np.stack([a, b], axis=-1).shape)
print(np.concatenate([a, b]).shape, np.concatenate([a, b], axis=1).shape)
lewa, prawa = np.split(np.concatenate([a, b], axis=1), 2, axis=1)
print(np.array_equal(lewa, a), np.array_equal(prawa, b))

pomiary = np.zeros((3, 7, 2))
print(np.moveaxis(pomiary, 2, 0).shape, pomiary.transpose(2, 0, 1).shape)
print(np.moveaxis(pomiary, 2, 0).base is pomiary)
```

```{ .text .no-copy }
(2, 2, 3) (2, 3, 2)
(4, 3) (2, 6)
True True
(2, 3, 7) (2, 3, 7)
True
```

`stack()` tworzy nową oś (domyślnie pierwszą), `concatenate()` z rozdziału 14 skleja wzdłuż osi istniejącej, a `split()` jest operacją odwrotną. `moveaxis()` i `transpose()` z krotką osi przestawiają osie bez kopiowania danych — wynik jest widokiem, jak `T` w rozdziale 14 — co przydaje się, gdy biblioteka oczekuje wielkości na pierwszej osi, a dane mają je na ostatniej.

## Indeksowanie tablicami indeksów

Indeksowanie listą z rozdziału 14 działa także w wielu wymiarach, ale dwie tablice indeksów są parowane element po elemencie, nie krzyżowane:

```python title="indeksy.py"
import numpy as np

m = np.arange(12).reshape(3, 4)
print(m)
print(m[[0, 2], [1, 3]])
print(m[np.ix_([0, 2], [1, 3])])

wiersze, kolumny = np.nonzero(m % 5 == 0)
print(np.column_stack([wiersze, kolumny]))

rng = np.random.default_rng(42)
oceny = rng.integers(1, 6, size=(3, 4))
print(oceny)
najlepsze = oceny.argmax(axis=1)
print(najlepsze, np.take_along_axis(oceny, najlepsze[:, None], axis=1).ravel())
```

```{ .text .no-copy }
[[ 0  1  2  3]
 [ 4  5  6  7]
 [ 8  9 10 11]]
[ 1 11]
[[ 1  3]
 [ 9 11]]
[[0 0]
 [1 1]
 [2 2]]
[[1 4 4 3]
 [3 5 1 4]
 [2 1 3 5]]
[1 1 3] [4 5 5]
```

`m[[0, 2], [1, 3]]` daje dwa elementy: `(0, 1)` i `(2, 3)`; podmacierz z wierszy 0 i 2 oraz kolumn 1 i 3 buduje `np.ix_()`. `np.nonzero()` zwraca współrzędne elementów spełniających warunek jako krotkę tablic — po jednej na oś — które `np.column_stack()` składa w wiersze par. `take_along_axis()` pobiera z każdego wiersza tablicy `oceny` element o indeksie z `argmax(axis=1)`: wzorzec „najlepszy w każdej grupie” bez pętli. Funkcja wymaga tablicy indeksów o tej samej liczbie osi, co dane — stąd `[:, None]` — i zwraca tablicę `(3, 1)`, którą `ravel()` spłaszcza. Wszystkie te operacje zwracają kopie, nie widoki — jak każde indeksowanie listą.
