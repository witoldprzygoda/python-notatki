# Typy, braki i czyszczenie

Wczytany plik rzadko ma od razu właściwe typy: liczby z jednym błędnym wpisem i daty stają się napisami, liczby całkowite z brakiem — zmiennoprzecinkowymi. Czyszczenie danych to doprowadzenie każdej kolumny do typu, który odpowiada jej znaczeniu, rozstrzygnięcie, co zrobić z brakami i duplikatami, oraz oszczędne przechowanie kolumn o niewielu wartościach.

## Typy kolumn

```python title="typy.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia.csv", sep=";", decimal=",", parse_dates=["data"])
print(zamowienia.dtypes)
print(zamowienia["rabat"].tolist())
print(pd.to_numeric(zamowienia["rabat"], errors="coerce").tolist())
zamowienia["rabat"] = pd.to_numeric(zamowienia["rabat"], errors="coerce")
zamowienia["ilosc"] = zamowienia["ilosc"].astype("Int64")
print(zamowienia[["ilosc", "rabat"]].dtypes.tolist())
print(zamowienia["ilosc"].tolist())
print(zamowienia["ilosc"].sum(), zamowienia["ilosc"].mean().round(2))
print(zamowienia["cena"].astype(int).head(3).tolist(), zamowienia["id"].astype(str).head(2).tolist())
print(pd.Series([1, 2, None]).dtype, pd.Series([1, 2, None], dtype="Int64").dtype)
```

```{ .text .no-copy }
id                    int64
data         datetime64[us]
klient                  str
miasto                  str
kategoria               str
ilosc               float64
cena                float64
rabat                   str
dtype: object
['0', '10', nan, '5', '0', '15', '15', 'brak', '0', '20']
[0.0, 10.0, nan, 5.0, 0.0, 15.0, 15.0, nan, 0.0, 20.0]
[Int64Dtype(), dtype('float64')]
[2, 1, 1, 3, <NA>, 2, 2, 1, 4, 2]
18 2.0
[39, 1299, 24] ['1', '2']
float64 Int64
```

Bez `na_values=["brak"]` kolumna `rabat` wczytuje się jako `str`, bo jeden wpis nie jest liczbą — a wtedy suma skleja napisy zamiast dodawać liczby, a średnia i porównanie z liczbą zgłaszają `TypeError`. `pd.to_numeric(errors="coerce")` zamienia wartości dające się odczytać jako liczby, a pozostałe na `NaN`; bez `errors=` zgłosiłaby wyjątek, co bywa właściwe, gdy błędny wpis ma zatrzymać analizę. Typ `Int64` (z wielką literą, odróżniającą go od `int64` NumPy) przechowuje liczby całkowite z brakiem oznaczonym `<NA>` — odpowiedź na problem z rozdziału 2 tej części, gdzie brak w tablicy całkowitoliczbowej wymuszał `float64`. `astype()` rzutuje kolumnę na wskazany typ; z `int` obcina część ułamkową, więc ceny najpierw zaokrąglamy, jeśli obcięcie nie jest zamierzone.

## Daty — `to_datetime()` i `.dt`

```python title="daty.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia.csv", sep=";", decimal=",", na_values=["brak"])
print(zamowienia["data"].dtype)
zamowienia["data"] = pd.to_datetime(zamowienia["data"])
print(zamowienia["data"].dtype, zamowienia["data"].min(), zamowienia["data"].max() - zamowienia["data"].min())
print(zamowienia["data"].dt.day.tolist())
print(zamowienia["data"].dt.day_name().head(3).tolist(), zamowienia["data"].dt.isocalendar().week.head(3).tolist())
print(zamowienia["data"].dt.strftime("%d.%m.%Y").head(2).tolist())
print(pd.to_datetime(pd.Series(["01.03.2025", "15.03.2025"]), format="%d.%m.%Y").tolist())
print(pd.to_datetime(pd.Series(["2025-03-01", "wczoraj"]), errors="coerce").tolist())
print((zamowienia["data"] + pd.Timedelta(days=14)).head(2).dt.date.tolist())
```

```{ .text .no-copy }
str
datetime64[us] 2025-03-01 00:00:00 6 days 00:00:00
[1, 1, 2, 3, 3, 4, 4, 5, 6, 7]
['Saturday', 'Saturday', 'Sunday'] [9, 9, 9]
['01.03.2025', '01.03.2025']
[Timestamp('2025-03-01 00:00:00'), Timestamp('2025-03-15 00:00:00')]
[Timestamp('2025-03-01 00:00:00'), NaT]
[datetime.date(2025, 3, 15), datetime.date(2025, 3, 15)]
```

Bez `parse_dates=` daty są napisami; `pd.to_datetime()` zamienia je na typ `datetime64` — pandas 3 zapisuje daty odczytane z napisów z rozdzielczością mikrosekund (`datetime64[us]`) zamiast dawnych nanosekund — z którym działają porównania, różnice (`Timedelta`) i minimum. **Akcesor** (ang. *accessor*) `.dt` daje dostęp do składników daty: dnia, nazwy dnia tygodnia, numeru tygodnia ISO, sformatowanego napisu przez `strftime()` z rozdziału 3 tej części. Format inny niż ISO podajemy jawnie przez `format=` z tymi samymi kodami; `errors="coerce"` zamienia nieczytelne wpisy na `NaT` — brak dla dat. Dodanie `Timedelta` przesuwa wszystkie daty naraz.

## Wartości brakujące

```python title="braki.py"
import numpy as np
import pandas as pd

zamowienia = pd.read_csv("zamowienia.csv", sep=";", decimal=",", parse_dates=["data"], na_values=["brak"], dtype={"ilosc": "Int64"})
print(zamowienia.isna().sum().to_dict())
print(zamowienia.loc[zamowienia.isna().any(axis=1), "id"].tolist())
print(zamowienia["rabat"].mean(), zamowienia["rabat"].count(), len(zamowienia))
print(zamowienia.dropna().shape, zamowienia.dropna(subset=["miasto"]).shape)
uzupelnione = zamowienia.fillna({"rabat": 0, "miasto": "nieznane"})
print(uzupelnione.isna().sum().sum())
print(zamowienia["ilosc"].ffill().tolist())
print(np.nan == np.nan, pd.NA == pd.NA, pd.isna(np.nan), pd.isna(pd.NA), pd.isna(pd.NaT))
print(zamowienia["ilosc"].isna().tolist()[4], zamowienia.loc[4, "ilosc"])
```

```{ .text .no-copy }
{'id': 0, 'data': 0, 'klient': 0, 'miasto': 1, 'kategoria': 0, 'ilosc': 1, 'cena': 0, 'rabat': 2}
[3, 4, 5, 7]
8.125 8 10
(6, 8) (9, 8)
1
[2, 1, 1, 3, 3, 2, 2, 1, 4, 2]
False <NA> True True True
True <NA>
```

pandas oznacza brak trzema wartościami: `NaN` w kolumnach zmiennoprzecinkowych i napisowych, `<NA>` w typach rozszerzonych pandas (`Int64`, `Float64`, `boolean`, `string`) i `NaT` w datach; wszystkie wykrywa `isna()` (i jej negacja `notna()`), bo porównanie `== np.nan` jest zawsze fałszywe, a `pd.NA == pd.NA` daje `<NA>`. Metody statystyczne pomijają braki — `mean()` liczy średnią z ośmiu rabatów, `count()` zlicza wartości niepuste. Decyzję o brakach podejmujemy kolumna po kolumnie: `dropna()` usuwa wiersze z brakiem (z `subset=` tylko w wybranych kolumnach), `fillna()` ze słownikiem wstawia wartość zastępczą osobno dla każdej kolumny, `ffill()`/`bfill()` przenoszą poprzednią lub następną wartość — właściwe dla szeregów czasowych, nie dla zamówień, gdzie brakująca ilość nie ma nic wspólnego z poprzednim wierszem. Uzupełnianie zmienia wyniki, więc w raporcie zapisujemy, które braki i czym zastąpiliśmy.

## Duplikaty i niespójne napisy

```python title="duplikaty.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia.csv", sep=";", decimal=",", parse_dates=["data"], na_values=["brak"])
print(zamowienia.duplicated().tolist())
print(zamowienia.duplicated(subset=["klient", "data"], keep=False).sum())
bez_duplikatow = zamowienia.drop_duplicates()
print(bez_duplikatow.shape, bez_duplikatow["id"].is_unique)
klienci = pd.Series(["Nowak", " nowak", "NOWAK ", "Kowalska", "kowalska"])
print(klienci.str.strip().str.lower().str.capitalize().unique().tolist())
print(klienci.str.strip().str.lower().nunique())
miasta = pd.Series(["Krakow", "Kraków", "Tarnow", "Tarnów"])
print(miasta.replace({"Krakow": "Kraków", "Tarnow": "Tarnów"}).value_counts().to_dict())
```

```{ .text .no-copy }
[False, False, False, False, False, False, True, False, False, False]
2
(9, 8) True
['Nowak', 'Kowalska']
2
{'Kraków': 2, 'Tarnów': 2}
```

`duplicated()` oznacza wiersze, które powtarzają wcześniejszy — domyślnie w całości, z `subset=` w wybranych kolumnach, a `keep=False` oznacza wszystkie wystąpienia, nie tylko powtórzenia po pierwszym; `drop_duplicates()` je usuwa. Powtórzone zamówienie o `id` 6 znika; `subset=["klient", "data"]` wskazuje tę samą parę, ale gdyby klient złożył dwa zamówienia jednego dnia, oznaczyłby je tak samo — zbieżność w wybranych kolumnach wymaga sprawdzenia, nie automatycznego usunięcia. Drugie źródło pozornych różnic to napisy: spacje na końcach, wielkość liter, brak polskich znaków; `str.strip()`, `str.lower()` i `replace()` ze słownikiem sprowadzają je do jednej postaci przed zliczaniem, inaczej `value_counts()` policzy jednego klienta trzykrotnie.

## Typ kategorialny

```python title="kategorie.py"
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
kategoria = pd.Series(rng.choice(["książki", "elektronika", "zabawki"], size=1_000_000))
jako_kategoria = kategoria.astype("category")
print(kategoria.dtype, jako_kategoria.dtype)
print(kategoria.memory_usage(deep=True) // 1_000_000, jako_kategoria.memory_usage(deep=True) // 1_000_000)
print(jako_kategoria.cat.categories.tolist(), jako_kategoria.cat.codes.head(3).tolist())
rozmiar = pd.Series(["M", "S", "L", "M"]).astype(pd.CategoricalDtype(["S", "M", "L"], ordered=True))
print(rozmiar.sort_values().tolist(), (rozmiar > "S").tolist(), rozmiar.max())
print(jako_kategoria.value_counts().to_dict())
```

```{ .text .no-copy }
str category
17 1
['elektronika', 'książki', 'zabawki'] [1, 2, 0]
['S', 'M', 'M', 'L'] [True, False, True, True] L
{'książki': 333685, 'elektronika': 333663, 'zabawki': 332652}
```

Kolumna z milionem napisów, wśród których są tylko trzy różne, zajmuje w typie `str` kilkanaście megabajtów; jako `category` — jeden, bo pandas przechowuje słownik kategorii i tablicę małych kodów całkowitych (akcesor `.cat` odsłania obie). Operacje na kategoriach — zliczanie, grupowanie, porównania — są też szybsze. `CategoricalDtype` z `ordered=True` nadaje kategoriom porządek, więc rozmiary ubrań sortują się S, M, L, nie alfabetycznie, i można je porównywać. Typ kategorialny wybieramy dla kolumn o niewielu wartościach powtarzających się w wielu wierszach — kategorii produktów, miast, kodów — a nie dla nazwisk czy identyfikatorów, gdzie każda wartość jest inna.
