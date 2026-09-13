# Statystyka i porządkowanie danych

Średnia i odchylenie z rozdziału 14 „Python Notatki” to początek; opis rozkładu wymaga kwantyli i histogramu, a praca z tabelą — sortowania po kolumnie, zliczania wartości i postępowania z brakami. Wszystko to NumPy wykonuje na całych tablicach, bez pętli.

## Kwantyle i rozkład

**Kwantyl** rzędu `q` to wartość, poniżej której leży ułamek `q` obserwacji; **percentyl** to kwantyl wyrażony w procentach, a mediana — kwantyl rzędu 0,5:

```python title="kwantyle.py"
import numpy as np

rng = np.random.default_rng(42)
czasy = rng.exponential(scale=2.0, size=1000).round(2)

print(czasy.mean().round(2), np.median(czasy), np.percentile(czasy, [25, 75]).round(2), np.quantile(czasy, 0.95).round(2))
licznosci, krawedzie = np.histogram(czasy, bins=5)
print(licznosci, krawedzie.round(1))
przedzialy = np.digitize(czasy, [1, 3, 6])
print(przedzialy[:8], np.bincount(przedzialy))
```

```{ .text .no-copy }
2.03 1.36 [0.58 2.82] 6.17
[772 173  45   7   3] [ 0.   3.   6.   9.  12.  14.9]
[2 2 2 0 0 1 1 3] [400 372 173  55]
```

Czasy obsługi z rozkładu wykładniczego (parametr `scale=2.0` jest jego średnią; rozkłady omawiamy w podrozdziale [Losowość i symulacje](losowosc-i-symulacje.md)) mają medianę wyraźnie poniżej średniej — rozkład jest skośny, czego średnia nie ujawnia, a kwantyle tak. `np.histogram()` zwraca liczności w przedziałach i ich krawędzie (o jedną więcej) — te same liczby, które `ax.hist()` z rozdziału 14 rysuje. `np.digitize()` przypisuje każdej obserwacji numer przedziału według podanych progów (`0` poniżej pierwszego, `3` od ostatniego progu wzwyż), a `np.bincount()` zlicza wystąpienia każdej nieujemnej liczby całkowitej — para przydatna do klasyfikowania wartości w kategorie — tu cztery: poniżej sekundy, od jednej do trzech, od trzech do sześciu i powyżej sześciu sekund.

## Sortowanie tabel

Tablicę dwuwymiarową sortujemy po kolumnie przez `argsort()` tej kolumny, a po kilku kluczach — przez `np.lexsort()`:

```python title="sortowanie.py"
import numpy as np

# kolumny: identyfikator, ocena, czas [s]
wyniki = np.array([[3, 4.5, 120], [1, 3.0, 95], [4, 4.5, 80], [2, 5.0, 110]])

print(wyniki[wyniki[:, 2].argsort()])
print(wyniki[wyniki[:, 1].argsort()[::-1]])
kolejnosc = np.lexsort((wyniki[:, 2], -wyniki[:, 1]))
print(wyniki[kolejnosc])

czasy = wyniki[:, 2]
print(czasy[np.argpartition(czasy, 2)[:2]])
print(np.searchsorted(np.sort(czasy), 100))
```

```{ .text .no-copy }
[[  4.    4.5  80. ]
 [  1.    3.   95. ]
 [  2.    5.  110. ]
 [  3.    4.5 120. ]]
[[  2.    5.  110. ]
 [  4.    4.5  80. ]
 [  3.    4.5 120. ]
 [  1.    3.   95. ]]
[[  2.    5.  110. ]
 [  4.    4.5  80. ]
 [  3.    4.5 120. ]
 [  1.    3.   95. ]]
[80. 95.]
2
```

`argsort()` zwraca indeksy, które ustawiają kolumnę rosnąco; indeksowanie nimi całej tablicy przestawia wiersze — odwrócenie `[::-1]` daje porządek malejący. `lexsort()` sortuje po wielu kluczach, przy czym **ostatni** klucz w krotce jest głównym: tu najpierw ocena malejąco (stąd minus), potem czas rosnąco. `argpartition()` znajduje `k` najmniejszych elementów bez sortowania całości — szybciej dla dużych tablic, ale w dowolnej kolejności, więc gdy kolejność ma znaczenie, wynik sortujemy osobno — a `searchsorted()` mówi, gdzie w posortowanej tablicy wstawić wartość, czyli ile elementów jest od niej mniejszych.

## Wartości unikatowe i zbiory

Zliczanie kategorii i proste grupowanie opierają się na `np.unique()`, a operacje na zbiorach mają odpowiedniki tablicowe:

```python title="unikatowe.py"
import numpy as np

kategorie = np.array(["b", "a", "c", "a", "b", "a"])
wartosci, indeksy, licznosci = np.unique(kategorie, return_inverse=True, return_counts=True)
print(wartosci, indeksy, licznosci)

kwoty = np.array([10, 20, 30, 40, 50, 60])
sumy = np.zeros(len(wartosci))
np.add.at(sumy, indeksy, kwoty)
print(dict(zip(wartosci.tolist(), sumy.tolist())))

a = np.array([1, 2, 3, 4])
b = np.array([3, 4, 5])
print(np.isin(a, b), np.intersect1d(a, b), np.setdiff1d(a, b), np.union1d(a, b))
```

```{ .text .no-copy }
['a' 'b' 'c'] [1 0 2 0 1 0] [3 2 1]
{'a': 120.0, 'b': 60.0, 'c': 30.0}
[False False  True  True] [3 4] [1 2] [1 2 3 4 5]
```

`np.unique()` z `return_counts=True` — z tabeli w rozdziale 14 — zlicza kategorie, a `return_inverse=True` daje dla każdego elementu numer jego kategorii. Zwykłe `sumy[indeksy] += kwoty` nie zadziała: przy powtarzających się indeksach NumPy wykonuje przypisanie raz na indeks; metoda `at()` funkcji uniwersalnej `np.add` dodaje każde wystąpienie, więc sumuje kwoty w grupach bez pętli; metoda `tolist()` zamienia tablice na listy zwykłych wartości Pythona, czytelniejsze w słowniku. To najprostsze grupowanie w NumPy; przy wielu kolumnach i nazwanych grupach wygodniejsze jest [grupowanie w pandas](../05-pandas-analiza/grupowanie.md). Operacje zbiorowe `intersect1d()`, `setdiff1d()` i `union1d()` odpowiadają zbiorom z rozdziału 5, ale działają na tablicach i zwracają wynik posortowany rosnąco; `isin()` zwraca maskę — które elementy `a` należą do `b`.

## Warunki i przekształcenia

Wybór wartości według warunków i przekształcenia ciągów — przyrosty, sumy narastające, średnia ruchoma — również obywają się bez pętli:

```python title="warunki.py"
import numpy as np

temperatury = np.array([-3.0, 2.5, 8.0, 15.5, 24.0, 31.0])

print(np.where(temperatury < 0, "mróz", "dodatnia"))
print(np.select([temperatury < 0, temperatury < 15, temperatury < 25], ["zimno", "chłodno", "ciepło"], default="gorąco"))
print(np.clip(temperatury, 0, 25))
print(np.diff(temperatury), np.cumsum(temperatury))
sprzedaz = np.array([5, 3, 8, 2, 7, 6, 4])
print(np.convolve(sprzedaz, np.ones(3) / 3, mode="valid").round(2))
```

```{ .text .no-copy }
['mróz' 'dodatnia' 'dodatnia' 'dodatnia' 'dodatnia' 'dodatnia']
['zimno' 'chłodno' 'chłodno' 'ciepło' 'ciepło' 'gorąco']
[ 0.   2.5  8.  15.5 24.  25. ]
[5.5 5.5 7.5 8.5 7. ] [-3.  -0.5  7.5 23.  47.  78. ]
[5.33 4.33 5.67 5.   5.67]
```

`np.where()` i `np.clip()` znamy z rozdziału 14; `np.select()` uogólnia pierwszą z nich na wiele warunków sprawdzanych po kolei (rozstrzyga pierwszy spełniony, `default=` dla pozostałych). `np.diff()` liczy przyrosty między sąsiednimi elementami — operację odwrotną do `cumsum()` z rozdziału 14 — a **splot** (ang. *convolution*) `np.convolve()` z oknem jedynek podzielonych przez jego długość daje **średnią ruchomą** (ang. *moving average*) z trzech kolejnych wartości; `mode="valid"` zwraca tylko położenia, w których okno mieści się w całości w danych — stąd pięć wartości z siedmiu.

## Brakujące wartości

Brak pomiaru zapisujemy jako `np.nan` — specjalną wartość zmiennoprzecinkową „nie-liczbę” (ang. *not a number*) z rozdziału 3 „Python Notatki”, która nie jest równa niczemu, nawet sobie:

```python title="brakujace.py"
import numpy as np

pomiary = np.array([12.0, np.nan, 13.5, np.nan, 15.0, 16.0])

print(np.nan == np.nan, np.isnan(pomiary), np.isnan(pomiary).sum())
print(pomiary.mean(), np.nanmean(pomiary), np.nanpercentile(pomiary, 50))
print(np.nan_to_num(pomiary, nan=0.0))

indeksy = np.arange(len(pomiary))
znane = ~np.isnan(pomiary)
uzupelnione = np.interp(indeksy, indeksy[znane], pomiary[znane])
print(uzupelnione)
```

```{ .text .no-copy }
False [False  True False  True False False] 2
nan 14.125 14.25
[12.   0.  13.5  0.  15.  16. ]
[12.   12.75 13.5  14.25 15.   16.  ]
```

Zwykłe `mean()` zwraca `nan`, gdy w danych jest choć jeden brak — sygnał, że trzeba zdecydować, co z brakami zrobić. Trzy typowe decyzje: pominąć je (`np.nanmean()` i inne funkcje `nan*`), zastąpić stałą (`np.nan_to_num()`) albo uzupełnić przez interpolację liniową między sąsiednimi znanymi wartościami: `np.interp(x, xp, fp)` przyjmuje punkty, w których szukamy wartości, oraz znane punkty i ich wartości — tu indeksy pomiarów, a maska `znane` (negacja `~` z rozdziału 14) wybiera pozycje bez braków. Tablice całkowitoliczbowe nie mieszczą `nan` — brak w kolumnie liczb całkowitych wymusza typ `float64`, do czego wracamy przy [typach pandas](../04-pandas-tabele/typy-i-braki.md#typy-kolumn). Rozkłady, testy statystyczne i estymację przedziałów dostarcza pakiet SciPy (`scipy.stats`), poza zakresem tego rozdziału.
