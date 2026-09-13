# Selekcja i filtrowanie

Wybieranie danych z tabeli ma w pandas trzy sposoby: nawiasy kwadratowe dla kolumn, `loc` dla etykiet i `iloc` dla pozycji. Do tego dochodzą maski logiczne — te same, co w NumPy w rozdziale 14 „Python Notatki” i rozdziale 2 tej części — zapytania tekstowe i sortowanie. Podrozdział kończy zasada, która w pandas 3 obowiązuje przy przypisywaniu: każda nowa tabela jest niezależną kopią.

## Kolumny i wiersze — `[]`, `loc` i `iloc`

```python title="loc-iloc.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia.csv", sep=";", decimal=",", parse_dates=["data"], na_values=["brak"])
print(zamowienia["klient"].head(3).tolist())
print(zamowienia[["klient", "cena"]].head(2))
print(zamowienia.loc[1:3, ["klient", "cena"]])
print(zamowienia.iloc[1:3, [2, 6]])
print(zamowienia.loc[4, "cena"], zamowienia.at[4, "cena"], zamowienia.iloc[-1, 0])
```

```{ .text .no-copy }
['Nowak', 'Kowalska', 'Nowak']
     klient    cena
0     Nowak    39.9
1  Kowalska  1299.0
       klient     cena
1    Kowalska  1299.00
2       Nowak    24.50
3  Wiśniewski    59.99
     klient    cena
1  Kowalska  1299.0
2     Nowak    24.5
44.9 44.9 9
```

`zamowienia["klient"]` to kolumna jako seria, a lista nazw w nawiasach — podtabela z wybranymi kolumnami. `loc[wiersze, kolumny]` adresuje **etykietami**: `1:3` obejmuje wiersze 1, 2 i 3, bo wycinek po etykietach zawiera koniec; `iloc[wiersze, kolumny]` adresuje **pozycjami** jak tablica NumPy, więc `1:3` to dwa wiersze. Dopóki indeks jest domyślnym `RangeIndex`, etykiety i pozycje wyglądają tak samo; po `set_index("id")` rozeszłyby się, jak w podrozdziale o indeksie. `at` i `iat` wybierają pojedynczą wartość szybciej niż `loc`.

## Maski logiczne

```python title="maski.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia.csv", sep=";", decimal=",", parse_dates=["data"], na_values=["brak"])
drogie = zamowienia["cena"] > 100
print(drogie.tolist())
print(zamowienia.loc[drogie, ["klient", "kategoria", "cena"]])
print(zamowienia.loc[(zamowienia["kategoria"] == "książki") & (zamowienia["ilosc"] >= 2), "klient"].tolist())
print(zamowienia.loc[zamowienia["miasto"].isin(["Kraków", "Tarnów"]), "id"].tolist())
print(zamowienia.loc[zamowienia["cena"].between(30, 100), "cena"].tolist())
print(zamowienia.loc[zamowienia["klient"].str.contains("ow"), "klient"].unique().tolist())
print(zamowienia.loc[zamowienia["miasto"].isna(), "id"].tolist())
print(zamowienia.loc[zamowienia["data"] >= "2025-03-04", "id"].tolist())
```

```{ .text .no-copy }
[False, True, False, False, False, True, True, False, False, True]
      klient    kategoria    cena
1   Kowalska  elektronika  1299.0
5  Zielińska  elektronika   249.0
6  Zielińska  elektronika   249.0
9  Zielińska      zabawki   119.0
['Nowak', 'Wiśniewski']
[1, 2, 3, 5, 7]
[39.9, 59.99, 44.9, 89.0]
['Nowak', 'Kowalska']
[4]
[6, 6, 7, 8, 9]
```

Porównanie kolumny z wartością daje serię logiczną — maskę — którą `loc` przyjmuje w miejscu wierszy; sama maska w nawiasach (`zamowienia[drogie]`) działa tak samo, ale `loc` pozwala od razu wskazać kolumny. Warunki łączymy operatorami `&`, `|` i `~` z rozdziału 14 „Python Notatki”, każdy warunek **w nawiasach**, bo operatory bitowe wiążą silniej niż porównania. Metody `isin()`, `between()` (oba końce włącznie), `str.contains()` i `isna()` zastępują dłuższe wyrażenia; kolumnę dat porównujemy z napisem ISO, który pandas zamienia na datę.

## Zapytania — `query()`

```python title="query.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia.csv", sep=";", decimal=",", parse_dates=["data"], na_values=["brak"])
print(zamowienia.query("cena > 100 and kategoria == 'elektronika'")[["klient", "cena"]])
prog = 50
print(zamowienia.query("cena < @prog and ilosc >= 2")["id"].tolist())
print(zamowienia.query("miasto in ['Kraków', 'Rzeszów']")["id"].tolist())
print(zamowienia.query("data >= '2025-03-04'")["id"].tolist())
```

```{ .text .no-copy }
      klient    cena
1   Kowalska  1299.0
5  Zielińska   249.0
6  Zielińska   249.0
[1, 8]
[1, 3, 7, 8]
[6, 6, 7, 8, 9]
```

`query()` przyjmuje warunek jako napis, w którym nazwy kolumn występują bez cudzysłowów i nawiasów, a spójniki to `and`, `or` i `not`; `@nazwa` wstawia zmienną z programu. Zapis jest krótszy od masek przy kilku warunkach i czytelny dla osób znających SQL, ale kolumny o nazwach ze spacjami wymagają odwrotnych apostrofów, a błędy w napisie ujawniają się dopiero w czasie wykonania — dlatego w kodzie wielokrotnego użytku wybieramy maski, a `query()` zostawiamy do pracy w notatniku.

## Sortowanie i wartości skrajne

```python title="sortowanie.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia.csv", sep=";", decimal=",", parse_dates=["data"], na_values=["brak"])
print(zamowienia.sort_values("cena", ascending=False)[["klient", "cena"]].head(3))
print(zamowienia.sort_values(["kategoria", "cena"], ascending=[True, False])[["kategoria", "cena"]].head(4))
print(zamowienia.nlargest(2, "cena")["id"].tolist(), zamowienia.nsmallest(2, "cena")["id"].tolist())
print(zamowienia.sort_values("rabat", na_position="first")["rabat"].head(3).tolist())
print(zamowienia.sort_values("klient").index.tolist()[:4])
print(zamowienia["cena"].idxmax(), zamowienia["cena"].rank(ascending=False).head(3).tolist())
```

```{ .text .no-copy }
      klient    cena
1   Kowalska  1299.0
5  Zielińska   249.0
6  Zielińska   249.0
     kategoria    cena
1  elektronika  1299.0
5  elektronika   249.0
6  elektronika   249.0
4      książki    44.9
[2, 6] [3, 8]
[nan, nan, 0.0]
[1, 4, 0, 2]
1 [8.0, 1.0, 10.0]
```

`sort_values()` sortuje po jednej lub kilku kolumnach z osobnym kierunkiem dla każdej i zwraca **nową** ramkę z zachowanymi etykietami wierszy — indeks po sortowaniu pokazuje pierwotne pozycje, a `reset_index(drop=True)` numeruje od nowa. Braki trafiają na koniec, chyba że `na_position="first"`. `nlargest()`/`nsmallest()` wybierają skrajne wiersze bez sortowania całości, `idxmax()` daje etykietę maksimum, a `rank()` — pozycję każdej wartości w porządku.

## Przypisywanie i kopiowanie przy zapisie

```python title="cow.py"
import warnings

import pandas as pd

zamowienia = pd.read_csv("zamowienia.csv", sep=";", decimal=",", parse_dates=["data"], na_values=["brak"])
zamowienia.loc[zamowienia["rabat"].isna(), "rabat"] = 0
zamowienia.loc[zamowienia["cena"] > 1000, "kategoria"] = "elektronika premium"
print(zamowienia["rabat"].tolist())
print(zamowienia.loc[1, "kategoria"])

ceny = zamowienia["cena"]
ceny.iloc[0] = 0.0
print(ceny.iloc[0], zamowienia.loc[0, "cena"])

krakow = zamowienia[zamowienia["miasto"] == "Kraków"]
krakow["rabat"] = 50
print(krakow["rabat"].tolist(), zamowienia["rabat"].tolist()[:3])

with warnings.catch_warnings(record=True) as ostrzezenia:
    warnings.simplefilter("always")
    zamowienia["rabat"][0] = 99
print(type(ostrzezenia[0].message).__name__, zamowienia.loc[0, "rabat"])
```

```{ .text .no-copy }
[0.0, 10.0, 0.0, 5.0, 0.0, 15.0, 15.0, 0.0, 0.0, 20.0]
elektronika premium
0.0 39.9
[50, 50, 50] [0.0, 10.0, 0.0]
ChainedAssignmentError 0.0
```

Wartości zmieniamy przez `loc[maska, kolumna] = wartość` — jedno wyrażenie, które wskazuje ramkę, wiersze i kolumnę. pandas 3 stosuje **kopiowanie przy zapisie** (ang. *copy-on-write*): seria wyjęta z ramki i wyniki wielu metod (`rename()`, `fillna()`, `reset_index()`) dzielą dane z oryginałem tylko do pierwszej modyfikacji, a wtedy dostają własną kopię; przefiltrowana podtabela czy wynik sortowania są kopiami od razu — w obu wypadkach zmiana `ceny` ani `krakow` nie zmienia `zamowienia`. Dlatego **przypisanie łańcuchowe** `zamowienia["rabat"][0] = 99` nie może zadziałać: modyfikuje tymczasową kopię kolumny, a pandas zgłasza `ChainedAssignmentError` — mimo nazwy ostrzeżenie, nie wyjątek, więc program działa dalej (tu przechwycone menedżerem kontekstu `warnings.catch_warnings()` z biblioteki standardowej, składnią `with` z rozdziału 8 „Python Notatki”, aby je wypisać) — i zostawia dane bez zmian. W starszych wersjach pandas ta sama operacja czasem działała, czasem nie i wywoływała `SettingWithCopyWarning` — w pandas 3 reguła jest jedna: zapis zawsze przez `loc`/`iloc` na ramce, a argument `inplace=True` znany ze starszych wersji oszczędza kopię tylko w metodach zmieniających wartości (`fillna()`, `replace()`), w `sort_values()` czy `dropna()` nigdy jej nie oszczędzał — w pandas 3 czytelniej jest przypisywać wynik.
