# Series i DataFrame

pandas ma dwie struktury: **serię** (`Series`) — jednowymiarową tablicę z etykietami — i **ramkę danych** (ang. *DataFrame*), czyli tabelę złożoną z serii o wspólnym indeksie wierszy. Kolumny liczbowe obu struktur to tablice NumPy z rozdziału 14 „Python Notatki”, więc operacje wektorowe, maski i funkcje uniwersalne działają na nich tak samo; nowe są etykiety, które pandas zachowuje i dopasowuje przy każdej operacji.

## Series — dane z etykietami

```python title="series.py"
import pandas as pd

temperatura = pd.Series([12.5, 7.0, 9.2], index=["Kraków", "Tarnów", "Nowy Sącz"], name="temperatura")
print(temperatura)
print(temperatura.dtype, temperatura.index.tolist())
print(temperatura["Tarnów"], temperatura.iloc[0], temperatura.max())
print((temperatura * 9 / 5 + 32).round(1).tolist())
wczoraj = pd.Series({"Tarnów": 6.1, "Kraków": 11.0, "Rzeszów": 8.4})
print(temperatura - wczoraj)
```

```{ .text .no-copy }
Kraków       12.5
Tarnów        7.0
Nowy Sącz     9.2
Name: temperatura, dtype: float64
float64 ['Kraków', 'Tarnów', 'Nowy Sącz']
7.0 12.5 12.5
[54.5, 44.6, 48.6]
Kraków       1.5
Nowy Sącz    NaN
Rzeszów      NaN
Tarnów       0.9
dtype: float64
```

Seria to tablica wartości — dla liczb tablica NumPy, dla napisów w pandas 3 tablica pyarrow — plus **indeks**, ciąg etykiet, tu nazw miast, i opcjonalna nazwa; wydruk pokazuje etykiety, wartości i typ. Element wybieramy etykietą (`temperatura["Tarnów"]`) albo pozycją przez `iloc`; arytmetyka jest wektorowa jak w NumPy. Najważniejsza różnica ujawnia się przy odejmowaniu dwóch serii: pandas dopasowuje je **po etykietach**, nie po pozycji — Kraków do Krakowa, Tarnów do Tarnowa — a etykiety obecne tylko w jednej z serii dostają `NaN`. To wyrównanie po indeksie chroni przed odjęciem temperatury jednego miasta od temperatury drugiego, gdy pliki mają inną kolejność wierszy.

## DataFrame — tabela kolumn

```python title="dataframe.py"
import numpy as np
import pandas as pd

miasta = pd.DataFrame({"miasto": ["Kraków", "Tarnów", "Nowy Sącz"], "ludnosc": [800_000, 108_000, 83_000], "temperatura": [12.5, 7.0, 9.2]})
print(miasta)
print(miasta.dtypes)
print(miasta.shape, miasta.columns.tolist())
print(type(miasta["ludnosc"]).__name__, miasta["ludnosc"].max())
print(miasta.loc[1])
print(pd.DataFrame([{"miasto": "Kraków", "ludnosc": 800_000}, {"miasto": "Tarnów"}]))
print(pd.DataFrame(np.arange(6).reshape(2, 3), columns=["a", "b", "c"]))
```

```{ .text .no-copy }
      miasto  ludnosc  temperatura
0     Kraków   800000         12.5
1     Tarnów   108000          7.0
2  Nowy Sącz    83000          9.2
miasto             str
ludnosc          int64
temperatura    float64
dtype: object
(3, 3) ['miasto', 'ludnosc', 'temperatura']
Series 800000
miasto         Tarnów
ludnosc        108000
temperatura       7.0
Name: 1, dtype: object
   miasto   ludnosc
0  Kraków  800000.0
1  Tarnów       NaN
   a  b  c
0  0  1  2
1  3  4  5
```

`DataFrame` ze słownika list ma kolumny w kolejności kluczy; każda kolumna jest serią własnego typu — `dtypes` pokazuje `str` dla napisów, `int64` i `float64` dla liczb — a wszystkie dzielą jeden indeks wierszy, domyślnie liczby od zera. `miasta["ludnosc"]` zwraca kolumnę jako `Series` ze wszystkimi jej metodami, a `miasta.loc[1]` — wiersz, także jako `Series`, tym razem o typie `object`, bo miesza napis z liczbami. Tabelę tworzy też lista słowników (brakujące klucze dają `NaN`, a kolumna z brakiem staje się `float64`) oraz tablica NumPy z nazwami kolumn.

## Indeks — etykiety wierszy

```python title="indeks.py"
import pandas as pd

miasta = pd.DataFrame({"miasto": ["Kraków", "Tarnów", "Nowy Sącz"], "ludnosc": [800_000, 108_000, 83_000], "temperatura": [12.5, 7.0, 9.2]})
print(miasta.index)
po_nazwie = miasta.set_index("miasto")
print(po_nazwie)
print(po_nazwie.loc["Tarnów", "ludnosc"], po_nazwie.iloc[1, 0])
print(po_nazwie.index.is_unique, po_nazwie.loc["Tarnów":"Nowy Sącz"].shape)
print(po_nazwie.reset_index().columns.tolist())
gestosc = pd.Series({"Tarnów": 1500, "Kraków": 2450})
po_nazwie["gestosc"] = gestosc
print(po_nazwie)
```

```{ .text .no-copy }
RangeIndex(start=0, stop=3, step=1)
           ludnosc  temperatura
miasto                         
Kraków      800000         12.5
Tarnów      108000          7.0
Nowy Sącz    83000          9.2
108000 108000
True (2, 2)
['miasto', 'ludnosc', 'temperatura']
           ludnosc  temperatura  gestosc
miasto                                  
Kraków      800000         12.5   2450.0
Tarnów      108000          7.0   1500.0
Nowy Sącz    83000          9.2      NaN
```

Domyślny `RangeIndex` numeruje wiersze; `set_index()` czyni indeksem kolumnę — odtąd `loc` wybiera wiersz po nazwie miasta, a `iloc` nadal po pozycji — i `reset_index()` przywraca ją do kolumn. Wycinek po etykietach `loc["Tarnów":"Nowy Sącz"]` obejmuje **oba końce**, inaczej niż wycinki list i tablic. Przypisanie serii do nowej kolumny wyrównuje ją po indeksie: Nowy Sącz, którego w serii nie ma, dostaje `NaN`, a kolumna liczb całkowitych z brakiem staje się `float64` — do tej konsekwencji wracamy w podrozdziale o typach. Indeks nie musi być unikalny (`is_unique`), ale wtedy `loc` z etykietą zwraca wszystkie pasujące wiersze.

## pandas a NumPy

```python title="pandas-numpy.py"
import numpy as np
import pandas as pd

miasta = pd.DataFrame({"miasto": ["Kraków", "Tarnów", "Nowy Sącz"], "ludnosc": [800_000, 108_000, 83_000], "temperatura": [12.5, 7.0, 9.2]})
tablica = miasta[["ludnosc", "temperatura"]].to_numpy()
print(type(tablica).__name__, tablica.dtype, tablica.shape)
print(miasta.to_numpy().dtype)
print(np.log10(miasta["ludnosc"]).round(2))
print(miasta["temperatura"].mean(), np.mean(miasta["temperatura"]))
print(pd.Series(np.linspace(0, 1, 3)))
```

```{ .text .no-copy }
ndarray float64 (3, 2)
object
0    5.90
1    5.03
2    4.92
Name: ludnosc, dtype: float64
9.566666666666666 9.566666666666666
0    0.0
1    0.5
2    1.0
dtype: float64
```

`to_numpy()` zwraca tablicę NumPy: dla kolumn liczbowych — o typie wspólnym dla wszystkich, tu `float64`, do którego awansuje kolumna `int64`; dla całej tabeli z napisami — tablicę `object`, na której obliczenia są wolne. Funkcje uniwersalne NumPy przyjmują serie i zwracają serie z zachowanym indeksem, a metody statystyczne (`mean()`, `sum()`, `std()`) mają odpowiedniki po obu stronach. Zasada: dane trzymamy w pandas, dopóki potrzebne są nazwy kolumn, typy mieszane i braki; do algebry liniowej z rozdziału 2 albo do funkcji, które wymagają tablicy, przekazujemy `to_numpy()`.

## Wyświetlanie

```python title="wyswietlanie.py"
import numpy as np
import pandas as pd

duza = pd.DataFrame(np.arange(1_000).reshape(100, 10), columns=[f"k{i}" for i in range(10)])
print(duza)
print(pd.get_option("display.max_rows"), pd.get_option("display.width"))
print(duza.head(3).to_string())
with pd.option_context("display.max_rows", 4):
    print(duza)
```

```{ .text .no-copy }
     k0   k1   k2   k3   k4   k5   k6   k7   k8   k9
0     0    1    2    3    4    5    6    7    8    9
1    10   11   12   13   14   15   16   17   18   19
2    20   21   22   23   24   25   26   27   28   29
3    30   31   32   33   34   35   36   37   38   39
4    40   41   42   43   44   45   46   47   48   49
..  ...  ...  ...  ...  ...  ...  ...  ...  ...  ...
95  950  951  952  953  954  955  956  957  958  959
96  960  961  962  963  964  965  966  967  968  969
97  970  971  972  973  974  975  976  977  978  979
98  980  981  982  983  984  985  986  987  988  989
99  990  991  992  993  994  995  996  997  998  999

[100 rows x 10 columns]
60 80
   k0  k1  k2  k3  k4  k5  k6  k7  k8  k9
0   0   1   2   3   4   5   6   7   8   9
1  10  11  12  13  14  15  16  17  18  19
2  20  21  22  23  24  25  26  27  28  29
     k0   k1   k2   k3   k4   k5   k6   k7   k8   k9
0     0    1    2    3    4    5    6    7    8    9
1    10   11   12   13   14   15   16   17   18   19
..  ...  ...  ...  ...  ...  ...  ...  ...  ...  ...
98  980  981  982  983  984  985  986  987  988  989
99  990  991  992  993  994  995  996  997  998  999

[100 rows x 10 columns]
```

Wydruk dużej tabeli jest skracany: powyżej 60 wierszy pandas pokazuje początek i koniec, a kolumny, które nie mieszczą się w 80 znakach, zastępuje wielokropkiem. `head()` i `tail()` pokazują wybraną liczbę wierszy, `to_string()` wypisuje wszystko bez skracania, a `option_context()` — menedżer kontekstu z rozdziału 8 „Python Notatki” — zmienia ustawienia wyświetlania tylko wewnątrz bloku. W notatniku z rozdziału 1 ramka wyświetla się jako tabela HTML z tą samą granicą 60 wierszy; kolumny skraca dopiero powyżej 20 (`display.max_columns`), bo szerokość wiersza nie ma tam znaczenia.
