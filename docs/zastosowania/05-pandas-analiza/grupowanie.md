# Grupowanie

Grupowanie odpowiada na pytania „ile na każdą kategorię”, „średnio na klienta”, „najdroższe zamówienie w każdym miesiącu”. W NumPy wymagało to `np.unique()` z `np.add.at()` (rozdział 2 tej części) albo pętli z maskami (rozdział 1); pandas wykonuje to jedną metodą `groupby()`, która dzieli tabelę według wartości kolumny, stosuje do każdej grupy funkcję i składa wyniki w nową tabelę — schemat **podział–zastosowanie–złączenie** (ang. *split-apply-combine*).

## Dane rozdziału

Zamówienia generujemy skryptem, aby były większe niż plik z rozdziału 4 i w pełni powtarzalne — ziarno generatora z rozdziału 2 gwarantuje ten sam plik na każdym komputerze z tą samą wersją NumPy:

```python title="generuj.py"
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 240
klienci = ["Nowak", "Kowalska", "Wiśniewski", "Zielińska", "Lis", "Mazur"]
kategorie = ["książki", "elektronika", "zabawki", "sport"]
zakresy_cen = {"książki": (20, 80), "elektronika": (150, 1500), "zabawki": (30, 200), "sport": (50, 400)}
dni = np.sort((rng.beta(1.6, 1.2, n) * 181).astype(int))
kategoria = rng.choice(kategorie, n, p=[0.4, 0.2, 0.25, 0.15])
zamowienia = pd.DataFrame({
    "id": np.arange(1, n + 1),
    "data": pd.Timestamp("2025-01-01") + pd.to_timedelta(dni, unit="D"),
    "klient": rng.choice(klienci, n),
    "kategoria": kategoria,
    "ilosc": rng.integers(1, 5, n),
    "cena": [round(rng.uniform(*zakresy_cen[k]), 2) for k in kategoria],
    "rabat": rng.choice([0, 0, 0, 5, 10, 20], n),
})
zamowienia["wartosc"] = (zamowienia["ilosc"] * zamowienia["cena"] * (1 - zamowienia["rabat"] / 100)).round(2)
zamowienia.to_csv("zamowienia-2025.csv", index=False)
print(zamowienia.shape, zamowienia["data"].min().date(), zamowienia["data"].max().date())
print(zamowienia.head(3))
```

```{ .text .no-copy }
(240, 8) 2025-01-04 2025-06-29
   id       data     klient kategoria  ilosc    cena  rabat  wartosc
0   1 2025-01-04   Kowalska   książki      1   33.68      0    33.68
1   2 2025-01-05      Nowak   zabawki      1  138.39      5   131.47
2   3 2025-01-06  Zielińska   książki      3   23.05      5    65.69
```

Daty pochodzą z rozkładu beta przeskalowanego do 181 dni półrocza, więc w drugim kwartale zamówień jest wyraźnie więcej niż w pierwszym; kategorie mają różne prawdopodobieństwa i zakresy cen, rabat najczęściej wynosi zero. Drugi plik to klienci — jeden z nich, Kaczmarek, nie złożył żadnego zamówienia, co wykorzystamy przy łączeniu tabel:

```text title="klienci.csv"
klient,miasto,segment
Nowak,Kraków,stały
Kowalska,Tarnów,stały
Wiśniewski,Rzeszów,nowy
Zielińska,Nowy Sącz,stały
Lis,Kraków,nowy
Mazur,Tarnów,nowy
Kaczmarek,Kielce,nowy
```

## Podział, zastosowanie, złączenie

```python title="grupowanie.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
grupy = zamowienia.groupby("kategoria")
print(type(grupy).__name__, grupy.ngroups)
print(grupy.size())
print(grupy["wartosc"].sum().round(0).sort_values(ascending=False))
print(grupy[["ilosc", "wartosc"]].mean().round(1))
print(zamowienia.groupby("klient", as_index=False)["wartosc"].sum().round(0).head(3))
for nazwa, grupa in grupy:
    print(nazwa, len(grupa), grupa["wartosc"].max())
```

```{ .text .no-copy }
DataFrameGroupBy 4
kategoria
elektronika    46
książki        94
sport          35
zabawki        65
dtype: int64
kategoria
elektronika    85128.0
sport          23409.0
zabawki        17025.0
książki        12099.0
Name: wartosc, dtype: float64
             ilosc  wartosc
kategoria                  
elektronika    2.3   1850.6
książki        2.6    128.7
sport          2.7    668.8
zabawki        2.3    261.9
     klient  wartosc
0  Kowalska  13091.0
1       Lis  32560.0
2     Mazur  29402.0
elektronika 46 5612.71
książki 94 315.2
sport 35 1513.12
zabawki 65 773.24
```

`groupby("kategoria")` nie liczy jeszcze niczego — zwraca obiekt, który zna klucz podziału, a sam podział wyznacza przy pierwszym użyciu (także dla `ngroups`) i zapamiętuje; dopiero metoda agregująca uruchamia obliczenie w każdej grupie i składa wyniki w serię lub ramkę z etykietami grup w indeksie. `size()` liczy wiersze grupy, wybór kolumn w nawiasach ogranicza agregację do nich, a `as_index=False` zostawia klucz jako zwykłą kolumnę — wygodne przed zapisem lub dalszym łączeniem. Obiekt grupujący można też przeglądać w pętli po parach (nazwa grupy, ramka grupy) — jak pętla z maskami w rozdziale 1, tylko bez ręcznego maskowania — choć do agregacji pętla jest zbędna.

## Agregacje — `agg()`

```python title="agregacje.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
grupy = zamowienia.groupby("kategoria")
print(grupy["wartosc"].agg(["count", "sum", "mean", "max"]).round(1))
podsumowanie = grupy.agg(zamowienia=("id", "size"), sztuk=("ilosc", "sum"), przychod=("wartosc", "sum"), klientow=("klient", "nunique"))
print(podsumowanie)
print(grupy["cena"].agg(rozstep=lambda s: s.max() - s.min()).round(2))
wiele = grupy.agg({"wartosc": ["sum", "mean"], "ilosc": "sum"}).round(1)
print(wiele)
print(wiele.columns.tolist())
wiele.columns = ["_".join(kolumna) for kolumna in wiele.columns]
print(wiele.columns.tolist())
```

```{ .text .no-copy }
             count      sum    mean     max
kategoria                                  
elektronika     46  85128.0  1850.6  5612.7
książki         94  12098.7   128.7   315.2
sport           35  23409.2   668.8  1513.1
zabawki         65  17024.9   261.9   773.2
             zamowienia  sztuk  przychod  klientow
kategoria                                         
elektronika          46    107  85127.95         6
książki              94    247  12098.71         6
sport                35     94  23409.18         6
zabawki              65    149  17024.87         6
             rozstep
kategoria           
elektronika  1321.22
książki        57.82
sport         339.63
zabawki       160.62
             wartosc         ilosc
                 sum    mean   sum
kategoria                         
elektronika  85128.0  1850.6   107
książki      12098.7   128.7   247
sport        23409.2   668.8    94
zabawki      17024.9   261.9   149
[('wartosc', 'sum'), ('wartosc', 'mean'), ('ilosc', 'sum')]
['wartosc_sum', 'wartosc_mean', 'ilosc_sum']
```

`agg()` przyjmuje listę nazw funkcji — każda staje się kolumną wyniku — albo **agregację nazwaną**: `nazwa_wyniku=("kolumna", "funkcja")`, która od razu daje czytelne nagłówki i pozwala liczyć różne funkcje na różnych kolumnach. Nazwy funkcji (`"sum"`, `"mean"`, `"max"`, `"size"`) wskazują szybkie implementacje pandas; własną funkcję przekazujemy jako obiekt, ale kosztem szybkości, o czym w ostatnim podrozdziale. Słownik z listami funkcji tworzy kolumny dwupoziomowe — krotki `("wartosc", "sum")` — które przed zapisem spłaszczamy, łącząc poziomy w jedną nazwę.

## Grupowanie po kilku kolumnach — `MultiIndex`

```python title="wiele-kluczy.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
suma = zamowienia.groupby(["kategoria", "klient"])["wartosc"].sum().round(0)
print(suma.head(4))
print(suma.index.nlevels, suma.index.names)
print(suma.loc["sport"].head(2))
print(suma.loc[("sport", "Lis")], suma.xs("Lis", level="klient").to_dict())
print(suma.unstack(fill_value=0).iloc[:2, :3])
print(suma.reset_index().head(2))
print(zamowienia.groupby(zamowienia["data"].dt.month)["wartosc"].sum().round(0).to_dict())
print(zamowienia.groupby(zamowienia["cena"] > 200)["wartosc"].mean().round(0).to_dict())
```

```{ .text .no-copy }
kategoria    klient  
elektronika  Kowalska     8546.0
             Lis         22565.0
             Mazur       20273.0
             Nowak       10579.0
Name: wartosc, dtype: float64
2 ['kategoria', 'klient']
klient
Kowalska     642.0
Lis         6125.0
Name: wartosc, dtype: float64
6125.0 {'elektronika': 22565.0, 'książki': 908.0, 'sport': 6125.0, 'zabawki': 2962.0}
klient       Kowalska      Lis    Mazur
kategoria                              
elektronika    8546.0  22565.0  20273.0
książki        1835.0    908.0   1628.0
     kategoria    klient  wartosc
0  elektronika  Kowalska   8546.0
1  elektronika       Lis  22565.0
{1: 13235.0, 2: 20297.0, 3: 26090.0, 4: 26233.0, 5: 18628.0, 6: 33179.0}
{False: 198.0, True: 1586.0}
```

Lista kolumn w `groupby()` daje wynik z **indeksem wielopoziomowym** (ang. *MultiIndex*): każda etykieta wiersza jest krotką (kategoria, klient). `loc` z pierwszym poziomem zwraca podserię, z pełną krotką — wartość, a `xs()` wybiera po dowolnym poziomie; `unstack()` przenosi ostatni poziom do kolumn i tworzy tabelę dwuwymiarową, `reset_index()` zamienia poziomy w zwykłe kolumny. Kluczem grupowania może być też dowolna seria o tym samym indeksie — miesiąc wyjęty akcesorem `.dt` albo maska logiczna — bez dodawania kolumny do tabeli.

## `transform()` i `filter()`

```python title="transform.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
suma_klienta = zamowienia.groupby("klient")["wartosc"].transform("sum")
print(suma_klienta.head(3).round(0).tolist(), len(suma_klienta))
zamowienia["udzial"] = (zamowienia["wartosc"] / suma_klienta * 100).round(2)
zamowienia["odchylenie"] = (zamowienia["wartosc"] - zamowienia.groupby("kategoria")["wartosc"].transform("mean")).round(0)
print(zamowienia[["klient", "kategoria", "wartosc", "udzial", "odchylenie"]].head(3))
duzi = zamowienia.groupby("klient").filter(lambda grupa: grupa["wartosc"].sum() > 20_000)
print(duzi["klient"].unique().tolist(), duzi.shape)
```

```{ .text .no-copy }
[13091.0, 20545.0, 24149.0] 240
      klient kategoria  wartosc  udzial  odchylenie
0   Kowalska   książki    33.68    0.26       -95.0
1      Nowak   zabawki   131.47    0.64      -130.0
2  Zielińska   książki    65.69    0.27       -63.0
['Nowak', 'Zielińska', 'Mazur', 'Lis'] (165, 10)
```

`agg()` zwraca jeden wiersz na grupę; `transform()` zwraca serię o długości **całej tabeli**, w której każdy wiersz dostaje wynik swojej grupy — dzięki temu można policzyć udział zamówienia w sumie klienta albo odchylenie od średniej kategorii bez łączenia tabel. `filter()` z funkcją zwracającą wartość logiczną zostawia całe grupy spełniające warunek — tu zamówienia klientów, którzy wydali ponad dwadzieścia tysięcy — w odróżnieniu od maski, która wybiera pojedyncze wiersze.

## `apply()` na grupach

```python title="apply-grupy.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
najwieksze = zamowienia.groupby("kategoria", group_keys=False)[["klient", "data", "wartosc"]].apply(lambda grupa: grupa.nlargest(1, "wartosc"))
print(najwieksze)
print(zamowienia.groupby("kategoria")["klient"].agg(lambda s: ", ".join(sorted(s.unique())))["sport"])
print(zamowienia.groupby("kategoria")["wartosc"].apply(lambda s: s.nlargest(2).sum()).round(0))
```

```{ .text .no-copy }
         klient       data  wartosc
151         Lis 2025-05-07  5612.71
229  Wiśniewski 2025-06-23   315.20
95   Wiśniewski 2025-04-08  1513.12
215         Lis 2025-06-14   773.24
Kowalska, Lis, Mazur, Nowak, Wiśniewski, Zielińska
kategoria
elektronika    10364.0
książki          620.0
sport           2959.0
zabawki         1445.0
Name: wartosc, dtype: float64
```

`apply()` wywołuje funkcję dla każdej grupy jako ramki i łączy zwrócone wyniki — dowolnego kształtu: wiersz, kilka wierszy, wartość. `group_keys=False` pomija dodawanie klucza grupy do indeksu, gdy wynik zachowuje oryginalne etykiety wierszy. To najogólniejsze narzędzie grupowania i — jak każda własna funkcja w `agg()` — wolne, bo funkcja Pythona uruchamia się raz na grupę; jeśli zadanie da się wyrazić przez `agg()` lub `transform()` z nazwą funkcji, wybieramy je — `apply()` zostawiamy operacjom, które potrzebują całej grupy naraz, jak wybór największych wierszy.
