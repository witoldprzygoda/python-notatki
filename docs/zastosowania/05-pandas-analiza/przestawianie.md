# Tabele przestawne i kształt danych

Wynik grupowania po dwóch kluczach to długa lista wierszy; do odczytu wygodniejsza jest tabela z jednym kluczem w wierszach, drugim w kolumnach i sumami na brzegach — **tabelę przestawną** (ang. *pivot table*) znaną z arkuszy. pandas buduje ją jedną funkcją, a między postacią długą (do obliczeń) i szeroką (do czytania) przechodzi w obie strony.

## `pivot_table()`

```python title="pivot.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
zamowienia["miesiac"] = zamowienia["data"].dt.month
tabela = pd.pivot_table(zamowienia, values="wartosc", index="kategoria", columns="miesiac", aggfunc="sum", fill_value=0).round(0)
print(tabela)
print(tabela.index.name, tabela.columns.name, tabela.shape)
print(pd.pivot_table(zamowienia, values="wartosc", index="kategoria", aggfunc=["sum", "mean"], margins=True, margins_name="razem").round(0))
print(pd.pivot_table(zamowienia, values=["wartosc", "ilosc"], index="kategoria", columns="rabat", aggfunc="sum", fill_value=0).round(0).loc[["sport"]])
```

```{ .text .no-copy }
miesiac           1        2        3        4        5        6
kategoria                                                       
elektronika  8763.0  14462.0  15710.0  13048.0  11960.0  21186.0
książki       464.0    696.0   1527.0   2955.0   2796.0   3661.0
sport        2801.0   2492.0   5643.0   6138.0   1654.0   4680.0
zabawki      1207.0   2646.0   3210.0   4092.0   2218.0   3652.0
kategoria miesiac (4, 6)
                  sum    mean
              wartosc wartosc
kategoria                    
elektronika   85128.0  1851.0
książki       12099.0   129.0
sport         23409.0   669.0
zabawki       17025.0   262.0
razem        137661.0   574.0
          ilosc              wartosc                        
rabat        0   5   10  20       0       5       10      20
kategoria                                                   
sport        51  18  10  15  14420.0  3905.0  2066.0  3018.0
```

`pivot_table()` to `groupby()` po dwóch kluczach z `unstack()` w jednym wywołaniu: `index=` trafia do wierszy, `columns=` do kolumn, `values=` z `aggfunc=` wypełnia komórki, a `fill_value=` zastępuje puste kombinacje. `margins=True` dodaje wiersz podsumowania (przy `columns=` także kolumnę) liczony tą samą funkcją — przy średniej jest to średnia z całości, nie średnia średnich. Lista funkcji lub kolumn daje kolumny dwupoziomowe, jak w `agg()`; wynik jest zwykłą ramką, więc działają na nim `loc`, sortowanie i zapis.

## `crosstab()`

```python title="crosstab.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
print(pd.crosstab(zamowienia["kategoria"], zamowienia["rabat"]))
print(pd.crosstab(zamowienia["kategoria"], zamowienia["rabat"], normalize="index").round(2))
print(pd.crosstab(zamowienia["kategoria"], zamowienia["rabat"], values=zamowienia["wartosc"], aggfunc="sum").round(0).fillna(0).astype(int))
print(pd.crosstab(zamowienia["klient"], zamowienia["kategoria"], margins=True).tail(2))
```

```{ .text .no-copy }
rabat        0   5   10  20
kategoria                  
elektronika  21   9   8   8
książki      41  17  19  17
sport        20   7   4   4
zabawki      39   7  12   7
rabat          0     5     10    20
kategoria                          
elektronika  0.46  0.20  0.17  0.17
książki      0.44  0.18  0.20  0.18
sport        0.57  0.20  0.11  0.11
zabawki      0.60  0.11  0.18  0.11
rabat           0      5      10     20
kategoria                              
elektronika  34432  21728  15196  13772
książki       5709   2058   2448   1884
sport        14420   3905   2066   3018
zabawki      10886   1854   3134   1150
kategoria  elektronika  książki  sport  zabawki  All
klient                                              
Zielińska            7       20      4        7   38
All                 46       94     35       65  240
```

`crosstab()` zlicza kombinacje dwóch kolumn — tabela kontyngencji — bez `values=`; z `normalize="index"` (albo `"columns"`, `"all"`) zamienia liczności na udziały, a z `values=` i `aggfunc=` działa jak `pivot_table()` na seriach zamiast ramki, tylko bez `fill_value=` — puste kombinacje uzupełnia `fillna()`. Z tabeli udziałów widać od razu, że w kategorii sport i zabawki większość zamówień jest bez rabatu, a w książkach i elektronice rabaty są częstsze.

## Postać długa i szeroka — `melt()` i `pivot()`

```python title="melt.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
szeroka = pd.pivot_table(zamowienia, values="wartosc", index="kategoria", columns=zamowienia["data"].dt.month, aggfunc="sum", fill_value=0).reset_index().rename_axis(columns=None)
print(szeroka.round(0))
dluga = szeroka.melt(id_vars="kategoria", var_name="miesiac", value_name="wartosc")
print(dluga.head(3).round(0), dluga.shape)
print(dluga.pivot(index="kategoria", columns="miesiac", values="wartosc").round(0).iloc[:2, :3])
print(dluga.groupby("miesiac")["wartosc"].sum().round(0).head(3).to_dict())
```

```{ .text .no-copy }
     kategoria       1        2        3        4        5        6
0  elektronika  8763.0  14462.0  15710.0  13048.0  11960.0  21186.0
1      książki   464.0    696.0   1527.0   2955.0   2796.0   3661.0
2        sport  2801.0   2492.0   5643.0   6138.0   1654.0   4680.0
3      zabawki  1207.0   2646.0   3210.0   4092.0   2218.0   3652.0
     kategoria miesiac  wartosc
0  elektronika       1   8763.0
1      książki       1    464.0
2        sport       1   2801.0 (24, 3)
miesiac           1        2        3
kategoria                            
elektronika  8763.0  14462.0  15710.0
książki       464.0    696.0   1527.0
{1: 13235.0, 2: 20297.0, 3: 26090.0}
```

Ta sama informacja ma dwie postaci. **Postać szeroka** (ang. *wide*) — kategoria w wierszu, miesiąc w kolumnie — jest czytelna dla ludzi i typowa dla arkuszy; **postać długa** (ang. *long*) — jeden wiersz na parę (kategoria, miesiąc) — jest wygodna dla `groupby()`, `merge()` i wykresów z podziałem na serie. `melt()` przekształca szeroką w długą (`rename_axis(columns=None)` usuwa wcześniej nazwę osi kolumn odziedziczoną z serii miesięcy): `id_vars=` to kolumny do zachowania, pozostałe nagłówki trafiają do kolumny `var_name=`, a wartości do `value_name=`. `pivot()` wraca do szerokiej bez agregacji — wymaga, aby każda para (wiersz, kolumna) wystąpiła raz; gdy się powtarza, potrzebna jest `pivot_table()` z funkcją agregującą.

## `stack()` i `unstack()`

```python title="stack.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
tabela = pd.pivot_table(zamowienia, values="wartosc", index="kategoria", columns="rabat", aggfunc="sum", fill_value=0).round(0)
print(tabela)
ulozona = tabela.stack()
print(ulozona.head(3))
print(type(ulozona.index).__name__, ulozona.index.names)
print(ulozona.unstack("kategoria").iloc[:2])
print(tabela.T.iloc[:2])
print(zamowienia.groupby(["kategoria", "rabat"]).size().unstack(fill_value=0).equals(pd.crosstab(zamowienia["kategoria"], zamowienia["rabat"])))
```

```{ .text .no-copy }
rabat             0        5        10       20
kategoria                                      
elektronika  34432.0  21728.0  15196.0  13772.0
książki       5709.0   2058.0   2448.0   1884.0
sport        14420.0   3905.0   2066.0   3018.0
zabawki      10886.0   1854.0   3134.0   1150.0
kategoria    rabat
elektronika  0        34432.0
             5        21728.0
             10       15196.0
dtype: float64
MultiIndex ['kategoria', 'rabat']
kategoria  elektronika  książki    sport  zabawki
rabat                                            
0              34432.0   5709.0  14420.0  10886.0
5              21728.0   2058.0   3905.0   1854.0
kategoria  elektronika  książki    sport  zabawki
rabat                                            
0              34432.0   5709.0  14420.0  10886.0
5              21728.0   2058.0   3905.0   1854.0
True
```

`stack()` przenosi kolumny do wewnętrznego poziomu indeksu — z tabeli tworzy serię z `MultiIndex` — a `unstack()` odwrotnie; nazwa poziomu w argumencie decyduje, który poziom staje się kolumnami. Transpozycja `.T` zamienia wiersze z kolumnami, pozostając przy postaci szerokiej — dla tabeli o jednym poziomie w wierszach i w kolumnach daje to samo, co `stack()` z `unstack("kategoria")`, stąd dwa identyczne wydruki. Te operacje spinają narzędzia z tego podrozdziału: `groupby()` po dwóch kluczach z `unstack()` daje ten sam wynik co `crosstab()`, co potwierdza `equals()`.

## Tabela do raportu

```python title="tabela-raport.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
raport = zamowienia.groupby("kategoria").agg(zamowien=("id", "size"), przychod=("wartosc", "sum"), srednia=("wartosc", "mean")).round(2)
raport = raport.sort_values("przychod", ascending=False)
raport["udzial_%"] = (raport["przychod"] / raport["przychod"].sum() * 100).round(1)
raport.index.name = "Kategoria"
raport = raport.rename(columns={"zamowien": "Zamówień", "przychod": "Przychód [zł]", "srednia": "Średnia [zł]", "udzial_%": "Udział [%]"})
print(raport.to_markdown(floatfmt=("", ".0f", ".2f", ".2f", ".1f")))
raport.to_excel("raport-kategorie.xlsx", sheet_name="kategorie")
print(pd.read_excel("raport-kategorie.xlsx", index_col=0).shape)
```

```{ .text .no-copy }
| Kategoria   |   Zamówień |   Przychód [zł] |   Średnia [zł] |   Udział [%] |
|:------------|-----------:|----------------:|---------------:|-------------:|
| elektronika |         46 |        85127.95 |        1850.61 |         61.8 |
| sport       |         35 |        23409.18 |         668.83 |         17.0 |
| zabawki     |         65 |        17024.87 |         261.92 |         12.4 |
| książki     |         94 |        12098.71 |         128.71 |          8.8 |
(4, 4)
```

Tabela wynikowa przed przekazaniem odbiorcy otrzymuje polskie nagłówki z jednostkami, sortowanie po najważniejszej kolumnie i kolumnę udziału; nazwy techniczne (`przychod`, `udzial_%`) zostają w kodzie, nazwy dla czytelnika nadaje `rename()` na końcu. `to_markdown()` (pakiet tabulate) wypisuje tabelę w składni Markdown — do notatnika, dokumentacji MkDocs czy wiadomości — a `to_excel()` zapisuje ją dla odbiorców pracujących w arkuszu; `floatfmt=` z krotką formatów — po jednym na kolumnę, z indeksem na początku — nadaje kwotom dwa miejsca po przecinku, a liczbie zamówień żadnego; tabulate stosuje kropkę dziesiętną, więc polski zapis z przecinkiem wymaga wcześniejszego sformatowania kolumn na napisy.
