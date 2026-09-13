# Łączenie tabel

Dane rzadko mieszczą się w jednej tabeli: zamówienia mają nazwisko klienta, a miasto i segment klienta leżą w drugim pliku; stawki VAT — w trzecim; kolejne miesiące — w kolejnych plikach. **Złączenie** (ang. *join*) dwóch tabel po wspólnym **kluczu** i sklejanie tabel o tych samych kolumnach to dwie operacje, które pandas wykonuje funkcjami `merge()` i `concat()`.

## `merge()` — klucz i rodzaje złączeń

```python title="merge.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
klienci = pd.read_csv("klienci.csv")
polaczone = zamowienia.merge(klienci, on="klient", how="left")
print(polaczone.shape, polaczone.columns.tolist()[-3:])
print(polaczone[["id", "klient", "miasto", "segment"]].head(3))
for rodzaj in ("inner", "left", "right", "outer"):
    print(rodzaj, zamowienia.merge(klienci, on="klient", how=rodzaj).shape)
pelne = zamowienia.merge(klienci, on="klient", how="outer", indicator=True)
print(pelne["_merge"].value_counts().to_dict())
print(pelne.loc[pelne["_merge"] == "right_only", ["klient", "miasto", "segment"]])
```

```{ .text .no-copy }
(240, 10) ['wartosc', 'miasto', 'segment']
   id     klient     miasto segment
0   1   Kowalska     Tarnów   stały
1   2      Nowak     Kraków   stały
2   3  Zielińska  Nowy Sącz   stały
inner (240, 10)
left (240, 10)
right (241, 10)
outer (241, 10)
{'both': 240, 'right_only': 1, 'left_only': 0}
      klient  miasto segment
0  Kaczmarek  Kielce    nowy
```

`merge()` dopasowuje wiersze obu tabel po wartościach kolumny `on=` i dokłada kolumny prawej tabeli do lewej. Rodzaj złączenia `how=` decyduje o wierszach bez pary: **wewnętrzne** (`inner`, domyślne) zostawia tylko dopasowane, **lewe** (`left`) wszystkie wiersze lewej tabeli — zamówienia klienta spoza słownika dostałyby `NaN` w nowych kolumnach — **prawe** (`right`) wszystkie wiersze prawej, a **zewnętrzne** (`outer`) wszystkie z obu. `indicator=True` dodaje kolumnę `_merge` z pochodzeniem każdego wiersza; tu ujawnia Kaczmarka, który jest w spisie klientów, ale nie złożył zamówienia. Do zamówień zwykle dołączamy **tabele słownikowe** — klientów, kategorii, stawek VAT — złączeniem lewym, aby nie zgubić żadnego zamówienia.

## Klucze, sufiksy i walidacja

```python title="merge-klucze.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
stawki = pd.DataFrame({"nazwa": ["książki", "elektronika", "zabawki", "sport"], "vat": [5, 23, 23, 23]})
z_vat = zamowienia.merge(stawki, left_on="kategoria", right_on="nazwa").drop(columns="nazwa")
z_vat["netto"] = (z_vat["wartosc"] / (1 + z_vat["vat"] / 100)).round(2)
print(z_vat[["kategoria", "wartosc", "vat", "netto"]].head(2))

lewa = pd.DataFrame({"klient": ["Nowak", "Lis"], "miasto": ["Kraków", "Kraków"]})
prawa = pd.DataFrame({"klient": ["Nowak", "Lis"], "miasto": ["Warszawa", "Gdańsk"]})
print(lewa.merge(prawa, on="klient").columns.tolist())
print(lewa.merge(prawa, on="klient", suffixes=("_zamowienie", "_dostawa")).columns.tolist())

telefony = pd.DataFrame({"klient": ["Nowak", "Nowak"], "telefon": ["111", "222"]})
print(zamowienia.merge(telefony, on="klient").shape)
try:
    zamowienia.merge(telefony, on="klient", validate="many_to_one")
except pd.errors.MergeError as blad:
    print("MergeError:", str(blad)[:45])
```

```{ .text .no-copy }
  kategoria  wartosc  vat   netto
0   książki    33.68    5   32.08
1   zabawki   131.47   23  106.89
['klient', 'miasto_x', 'miasto_y']
['klient', 'miasto_zamowienie', 'miasto_dostawa']
(82, 9)
MergeError: Merge keys are not unique in right dataset; n
```

Gdy klucz nosi w tabelach różne nazwy, wskazujemy je przez `left_on=`/`right_on=` — obie kolumny zostają w wyniku, więc zbędną usuwamy. Kolumny o tej samej nazwie poza kluczem dostają sufiksy `_x` i `_y`; własne, opisowe sufiksy podane w `suffixes=` czynią wynik jednoznacznym. Najgroźniejsza pułapka to klucz powtórzony w prawej tabeli: każde zamówienie Nowaka zostaje **zwielokrotnione** — raz na każdy telefon — a sumy po złączeniu rosną bez ostrzeżenia. `validate="many_to_one"` sprawdza, czy prawy klucz jest unikalny, i zgłasza `MergeError`, zanim błąd trafi do raportu; przy tabelach słownikowych warto go podawać zawsze.

## Pułapki kluczy

```python title="merge-pulapki.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
klienci = pd.read_csv("klienci.csv")
wielkie = klienci.assign(klient=klienci["klient"].str.upper())
print(zamowienia.merge(wielkie, on="klient", how="left")["miasto"].isna().sum())
znormalizowane = zamowienia.merge(wielkie.assign(klient=wielkie["klient"].str.capitalize()), on="klient", how="left")
print(znormalizowane["miasto"].isna().sum())

kody_int = pd.DataFrame({"kod": [1, 2], "x": ["a", "b"]})
kody_str = pd.DataFrame({"kod": ["1", "2"], "y": ["c", "d"]})
try:
    kody_int.merge(kody_str, on="kod")
except ValueError as blad:
    print("ValueError:", str(blad)[:58])
print(kody_int.merge(kody_str.assign(kod=kody_str["kod"].astype(int)), on="kod").shape)

z_brakiem = pd.DataFrame({"klient": ["Nowak", None], "uwaga": ["a", "b"]})
print(z_brakiem.merge(pd.DataFrame({"klient": [None, "Lis"], "z": [1, 2]}), on="klient").to_dict("records"))
```

```{ .text .no-copy }
240
0
ValueError: You are trying to merge on int64 and str columns for key '
(2, 3)
[{'klient': nan, 'uwaga': 'b', 'z': 1}]
```

Klucze porównywane są dosłownie: `NOWAK` i `Nowak` to różne wartości, więc złączenie lewe daje same braki — normalizacja napisów z rozdziału 4 (`str.strip()`, `str.lower()`, `str.capitalize()`) musi poprzedzić złączenie. Klucz liczbowy w jednej tabeli i tekstowy w drugiej pandas odrzuca wyjątkiem `ValueError` — to lepsze niż złączenie, które bez ostrzeżenia nie dopasowałoby żadnego wiersza; jeden z kluczy rzutujemy metodą `astype()`. Brak w kluczu dopasowuje się do braku po drugiej stronie, co rzadko jest zamierzone — wiersze z brakującym kluczem usuwamy `dropna(subset=)` przed złączeniem.

## `concat()` — sklejanie wierszy i kolumn

```python title="concat.py"
from pathlib import Path

import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
zamowienia[zamowienia["data"].dt.month <= 3].to_csv("zamowienia-q1.csv", index=False)
zamowienia[zamowienia["data"].dt.month > 3].to_csv("zamowienia-q2.csv", index=False)
pliki = sorted(Path(".").glob("zamowienia-q*.csv"))
calosc = pd.concat([pd.read_csv(plik, parse_dates=["data"]) for plik in pliki], ignore_index=True)
print([plik.name for plik in pliki], calosc.shape, calosc.index[-1])
ze_zrodlem = pd.concat({plik.stem: pd.read_csv(plik) for plik in pliki}, names=["plik", "wiersz"])
print(ze_zrodlem.index[:2].tolist())
print(ze_zrodlem.groupby(level="plik").size().to_dict())
obok = pd.concat([zamowienia[["id", "klient"]].head(2), zamowienia[["wartosc"]].head(2)], axis=1)
print(obok)
print(pd.concat([pd.DataFrame({"a": [1]}), pd.DataFrame({"b": [2]})]))
```

```{ .text .no-copy }
['zamowienia-q1.csv', 'zamowienia-q2.csv'] (240, 8) 239
[('zamowienia-q1', 0), ('zamowienia-q1', 1)]
{'zamowienia-q1': 89, 'zamowienia-q2': 151}
   id    klient  wartosc
0   1  Kowalska    33.68
1   2     Nowak   131.47
     a    b
0  1.0  NaN
0  NaN  2.0
```

Skrypt najpierw dzieli zamówienia na dwa pliki kwartalne, aby odtworzyć sytuację oddzielnych eksportów; `concat()` skleja listę ramek jedna pod drugą; `ignore_index=True` numeruje wynik od nowa, bo inaczej indeksy plików by się powtarzały. Wzorzec „wiele plików jednego kształtu” to `Path.glob()` z rozdziału 9 „Python Notatki” i wyrażenie listowe — tak łączymy miesięczne eksporty. Słownik (`dict`) zamiast listy dodaje poziom indeksu z nazwą źródła, po którym można grupować. `axis=1` skleja kolumny obok siebie, dopasowując wiersze po indeksie. Ramki o różnych kolumnach sklejają się bez błędu, a brakujące komórki dostają `NaN` — po sklejeniu sprawdzamy więc `columns` i `isna().sum()`.

## `join()` i wyrównanie serii

```python title="join.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
klienci = pd.read_csv("klienci.csv").set_index("klient")
po_kliencie = zamowienia.groupby("klient")["wartosc"].sum().round(0).to_frame("przychod")
print(po_kliencie.join(klienci, how="left"))
liczba = zamowienia["klient"].value_counts()
srednia = zamowienia.groupby("klient")["wartosc"].mean().round(0)
print(pd.DataFrame({"zamowien": liczba, "srednia": srednia, "segment": klienci["segment"]}))
```

```{ .text .no-copy }
            przychod     miasto segment
klient                                 
Kowalska     13091.0     Tarnów   stały
Lis          32560.0     Kraków    nowy
Mazur        29402.0     Tarnów    nowy
Nowak        20545.0     Kraków   stały
Wiśniewski   17913.0    Rzeszów    nowy
Zielińska    24149.0  Nowy Sącz   stały
            zamowien  srednia segment
klient                               
Kaczmarek        NaN      NaN    nowy
Kowalska        31.0    422.0   stały
Lis             36.0    904.0    nowy
Mazur           50.0    588.0    nowy
Nowak           41.0    501.0   stały
Wiśniewski      44.0    407.0    nowy
Zielińska       38.0    636.0   stały
```

`join()` łączy po **indeksach** — wygodne, gdy obie tabele już mają klucz w indeksie, jak wyniki `groupby()` i słownik po `set_index()`; to `merge()` z `left_index=True, right_index=True`, tyle że domyślnie lewe, nie wewnętrzne — `how="left"` w skrypcie jedynie to uwidacznia. Najprostsze złączenie nie wymaga żadnej funkcji: konstruktor `DataFrame` ze słownikiem serii wyrównuje je po indeksie, jak w rozdziale 4 — serie o wspólnych etykietach klientów układają się w kolumny, a Kaczmarek bez zamówień dostaje `NaN` w liczbie i średniej.

## Analiza po złączeniu

```python title="po-zlaczeniu.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia-2025.csv", parse_dates=["data"])
klienci = pd.read_csv("klienci.csv")
polaczone = zamowienia.merge(klienci, on="klient", how="left", validate="many_to_one")
print(polaczone.groupby("miasto")["wartosc"].sum().round(0).sort_values(ascending=False))
print(polaczone.groupby(["segment", "kategoria"])["wartosc"].sum().unstack().round(0))
print(polaczone.groupby("segment").agg(klientow=("klient", "nunique"), zamowien=("id", "size"), srednia=("wartosc", "mean")).round(0))
```

```{ .text .no-copy }
miasto
Kraków       53105.0
Tarnów       42493.0
Nowy Sącz    24149.0
Rzeszów      17913.0
Name: wartosc, dtype: float64
kategoria  elektronika  książki    sport  zabawki
segment                                          
nowy           49217.0   4924.0  15338.0  10396.0
stały          35911.0   7175.0   8071.0   6629.0
         klientow  zamowien  srednia
segment                             
nowy            3       130    614.0
stały           3       110    525.0
```

Złączenie jest krokiem, nie celem: dopiero po dołączeniu miasta i segmentu można zapytać, które miasto daje największy przychód i czy nowi klienci kupują inne kategorie niż stali. Wzorzec z tego podrozdziału — złączenie lewe z walidacją, potem grupowanie po kolumnach z obu tabel — powtarza się w każdej analizie wielu źródeł; czytelnicy znający SQL rozpoznają w nim `JOIN` z `GROUP BY`, do których wrócimy przy bazach danych w ścieżce aplikacji.
