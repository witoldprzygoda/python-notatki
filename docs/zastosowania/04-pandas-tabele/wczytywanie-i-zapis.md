# Wczytywanie i zapis

Dane rzadko powstają w kodzie — przychodzą w plikach: CSV wyeksportowanym z arkusza z polskimi ustawieniami, skoroszycie Excel, JSON z API, Parquet z hurtowni danych. pandas czyta każdy z nich jedną funkcją i zapisuje jedną metodą; ten podrozdział pokazuje, jak wczytać plik poprawnie za pierwszym razem, obejrzeć wynik i zapisać go w formacie, którego oczekuje odbiorca.

## Plik CSV — `read_csv()`

Wspólny zbiór danych rozdziału to dziesięć wierszy z zamówieniami sklepu — dane przykładowe z typowymi wadami plików eksportowanych z arkusza: średnik jako separator, przecinek dziesiętny, brakujące pola, słowo zamiast liczby i powtórzony wiersz:

```text title="zamowienia.csv"
id;data;klient;miasto;kategoria;ilosc;cena;rabat
1;2025-03-01;Nowak;Kraków;książki;2;39,90;0
2;2025-03-01;Kowalska;Tarnów;elektronika;1;1299,00;10
3;2025-03-02;Nowak;Kraków;książki;1;24,50;
4;2025-03-03;Wiśniewski;;zabawki;3;59,99;5
5;2025-03-03;Kowalska;Tarnów;książki;;44,90;0
6;2025-03-04;Zielińska;Nowy Sącz;elektronika;2;249,00;15
6;2025-03-04;Zielińska;Nowy Sącz;elektronika;2;249,00;15
7;2025-03-05;Nowak;Kraków;zabawki;1;89,00;brak
8;2025-03-06;Wiśniewski;Rzeszów;książki;4;29,90;0
9;2025-03-07;Zielińska;Nowy Sącz;zabawki;2;119,00;20
```

```python title="wczytanie.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia.csv", sep=";", decimal=",", parse_dates=["data"], na_values=["brak"])
print(zamowienia)
zamowienia.info()
```

```{ .text .no-copy }
   id       data      klient     miasto    kategoria  ilosc     cena  rabat
0   1 2025-03-01       Nowak     Kraków      książki    2.0    39.90    0.0
1   2 2025-03-01    Kowalska     Tarnów  elektronika    1.0  1299.00   10.0
2   3 2025-03-02       Nowak     Kraków      książki    1.0    24.50    NaN
3   4 2025-03-03  Wiśniewski        NaN      zabawki    3.0    59.99    5.0
4   5 2025-03-03    Kowalska     Tarnów      książki    NaN    44.90    0.0
5   6 2025-03-04   Zielińska  Nowy Sącz  elektronika    2.0   249.00   15.0
6   6 2025-03-04   Zielińska  Nowy Sącz  elektronika    2.0   249.00   15.0
7   7 2025-03-05       Nowak     Kraków      zabawki    1.0    89.00    NaN
8   8 2025-03-06  Wiśniewski    Rzeszów      książki    4.0    29.90    0.0
9   9 2025-03-07   Zielińska  Nowy Sącz      zabawki    2.0   119.00   20.0
<class 'pandas.DataFrame'>
RangeIndex: 10 entries, 0 to 9
Data columns (total 8 columns):
 #   Column     Non-Null Count  Dtype         
---  ------     --------------  -----         
 0   id         10 non-null     int64         
 1   data       10 non-null     datetime64[us]
 2   klient     10 non-null     str           
 3   miasto     9 non-null      str           
 4   kategoria  10 non-null     str           
 5   ilosc      9 non-null      float64       
 6   cena       10 non-null     float64       
 7   rabat      8 non-null      float64       
dtypes: datetime64[us](1), float64(3), int64(1), str(3)
memory usage: 1020.0 bytes
```

`read_csv()` domyślnie oczekuje przecinka jako separatora i kropki dziesiętnej; `sep=";"` i `decimal=","` dostosowują ją do pliku z polskiego arkusza, `parse_dates=` wskazuje kolumny do zamiany na daty, a `na_values=` — dodatkowe napisy, które oznaczają brak (puste pole oraz napisy w rodzaju `NA`, `null` i `NaN` są brakiem domyślnie). Kodowanie domyślne to UTF-8 — plik z Windows-1250 wymaga `encoding="cp1250"`, jak w rozdziale 9 „Python Notatki”. Metoda `info()` podsumowuje wynik: liczbę wierszy, dla każdej kolumny liczbę wartości niepustych i typ. Kolumna `ilosc` stała się `float64`, choć zawiera liczby całkowite — jeden brak wymusza typ zmiennoprzecinkowy, bo `NaN` jest liczbą zmiennoprzecinkową; podrozdział o typach pokazuje typ `Int64`, który mieści brak w liczbach całkowitych.

## Pierwsze oględziny

```python title="ogledziny.py"
import pandas as pd

zamowienia = pd.read_csv("zamowienia.csv", sep=";", decimal=",", parse_dates=["data"], na_values=["brak"])
print(zamowienia.head(3))
print(zamowienia.sample(2, random_state=42))
print(zamowienia.describe().round(2))
print(zamowienia["kategoria"].value_counts())
print(zamowienia["miasto"].nunique(), zamowienia["klient"].unique().tolist())
print(zamowienia.isna().sum())
print(zamowienia.duplicated().sum(), zamowienia["id"].is_unique)
```

```{ .text .no-copy }
   id       data    klient  miasto    kategoria  ilosc    cena  rabat
0   1 2025-03-01     Nowak  Kraków      książki    2.0    39.9    0.0
1   2 2025-03-01  Kowalska  Tarnów  elektronika    1.0  1299.0   10.0
2   3 2025-03-02     Nowak  Kraków      książki    1.0    24.5    NaN
   id       data      klient   miasto    kategoria  ilosc    cena  rabat
8   8 2025-03-06  Wiśniewski  Rzeszów      książki    4.0    29.9    0.0
1   2 2025-03-01    Kowalska   Tarnów  elektronika    1.0  1299.0   10.0
          id                 data  ilosc     cena  rabat
count  10.00                   10    9.0    10.00   8.00
mean    5.10  2025-03-03 14:24:00    2.0   220.42   8.12
min     1.00  2025-03-01 00:00:00    1.0    24.50   0.00
25%     3.25  2025-03-02 06:00:00    1.0    41.15   0.00
50%     5.50  2025-03-03 12:00:00    2.0    74.50   7.50
75%     6.75  2025-03-04 18:00:00    2.0   216.50  15.00
max     9.00  2025-03-07 00:00:00    4.0  1299.00  20.00
std     2.60                  NaN    1.0   388.21   7.99
kategoria
książki        4
elektronika    3
zabawki        3
Name: count, dtype: int64
4 ['Nowak', 'Kowalska', 'Wiśniewski', 'Zielińska']
id           0
data         0
klient       0
miasto       1
kategoria    0
ilosc        1
cena         0
rabat        2
dtype: int64
1 False
```

Kilka metod wystarcza na pierwsze oględziny: `head()`/`tail()` i `sample()` (z `random_state=` dla powtarzalności, jak ziarno generatora w rozdziale 2) pokazują wiersze; `describe()` liczy statystyki kolumn liczbowych — i zakres dat — a `value_counts()` zlicza wartości kolumny o niewielu różnych wartościach (tu tekstowej), posortowane malejąco. `nunique()` i `unique()` podają liczbę i listę różnych wartości, `isna().sum()` — liczbę braków w każdej kolumnie, najważniejszą informację przed czyszczeniem, a `duplicated().sum()` — liczbę powtórzonych wierszy. Z tych wydruków wiemy już, że plik ma po jednym braku w mieście i ilości, dwa w rabacie oraz że jeden wiersz się powtarza, przez co kolumna `id` nie jest unikalna.

## Analiza z rozdziału 1 w pandas

Rozdział 1 tej części odpowiadał na trzy pytania o plik `pomiary.csv` — który rok był cieplejszy, który miesiąc najcieplejszy i jaki jest związek temperatury z opadami — tablicą strukturalną i maskami. W pandas te same odpowiedzi to trzy wyrażenia:

```text title="pomiary.csv"
rok,miesiac,temperatura,opady
2024,1,-1.5,40
2024,2,1.2,35
2024,3,5.4,42
2024,4,10.8,55
2024,5,15.6,78
2024,6,19.2,95
2024,7,21.4,102
2024,8,20.7,88
2024,9,15.3,64
2024,10,9.8,52
2024,11,4.6,48
2024,12,0.3,44
2025,1,-2.8,38
2025,2,0.6,30
2025,3,4.9,45
2025,4,11.5,50
2025,5,14.9,84
2025,6,18.8,110
2025,7,22.1,96
2025,8,21.3,79
2025,9,16.0,58
2025,10,10.2,60
2025,11,3.9,51
2025,12,-0.4,42
```

```python title="pomiary-pandas.py"
import pandas as pd

pomiary = pd.read_csv("pomiary.csv")
print(pomiary.dtypes.tolist())
print(pomiary.groupby("rok")[["temperatura", "opady"]].mean().round(2))
print(pomiary.loc[[pomiary["temperatura"].idxmax()], ["rok", "miesiac", "temperatura"]])
print(pomiary[["temperatura", "opady"]].corr().round(2))
```

```{ .text .no-copy }
[dtype('int64'), dtype('int64'), dtype('float64'), dtype('int64')]
      temperatura  opady
rok                     
2024        10.23  61.92
2025        10.08  61.92
     rok  miesiac  temperatura
18  2025        7         22.1
             temperatura  opady
temperatura          1.0    0.9
opady                0.9    1.0
```

`read_csv()` bez argumentów wystarcza dla pliku z przecinkami i kropkami; każda kolumna dostaje własny typ, więc `rok` i `miesiac` są całkowite. `groupby("rok")` dzieli tabelę na grupy według roku i liczy średnie każdej grupy — to jedno wyrażenie zastępuje pętlę z maskami z rozdziału 1, a pełne omówienie grupowania to następny rozdział ścieżki. <!-- TODO: link po powstaniu rozdziału o analizie w pandas --> `idxmax()` zwraca etykietę wiersza z największą wartością, a `loc` z tą etykietą w liście zwraca jednowierszową ramkę (z pojedynczą etykietą zwróciłby serię, w której liczby całkowite zmieniłyby się w zmiennoprzecinkowe); `corr()` liczy macierz korelacji kolumn.

## Zapis — `to_csv()`

```python title="zapis.py"
from pathlib import Path

import pandas as pd

zamowienia = pd.read_csv("zamowienia.csv", sep=";", decimal=",", parse_dates=["data"], na_values=["brak"])
zamowienia.to_csv("zamowienia_czyste.csv", index=False)
print(Path("zamowienia_czyste.csv").read_text(encoding="utf-8").splitlines()[:3])
zamowienia.to_csv("zamowienia_pl.csv", index=False, sep=";", decimal=",", date_format="%d.%m.%Y", encoding="utf-8-sig")
print(Path("zamowienia_pl.csv").read_text(encoding="utf-8-sig").splitlines()[:2])
ponownie = pd.read_csv("zamowienia_czyste.csv", parse_dates=["data"])
print(ponownie.equals(zamowienia))
```

```{ .text .no-copy }
['id,data,klient,miasto,kategoria,ilosc,cena,rabat', '1,2025-03-01,Nowak,Kraków,książki,2.0,39.9,0.0', '2,2025-03-01,Kowalska,Tarnów,elektronika,1.0,1299.0,10.0']
['id;data;klient;miasto;kategoria;ilosc;cena;rabat', '1;01.03.2025;Nowak;Kraków;książki;2,0;39,9;0,0']
True
```

`to_csv()` domyślnie zapisuje przecinki, kropki, daty ISO i UTF-8 — postać, którą `read_csv()` odczyta bez argumentów o separatorach i kodowaniu — daty nadal wskazujemy przez `parse_dates=` — co potwierdza `equals()`. `index=False` pomija indeks; bez niego plik dostałby dodatkową kolumnę numerów wierszy, którą przy odczycie trzeba by usuwać. Plik dla polskiego Excela dostaje `sep=";"`, `decimal=","`, `date_format=` i kodowanie `utf-8-sig` — UTF-8 ze znacznikiem kolejności bajtów z rozdziału 9, po którym Excel rozpoznaje polskie znaki. Braki są zapisywane jako puste pola.

## Excel, JSON i Parquet

```python title="formaty.py"
from pathlib import Path

import pandas as pd

zamowienia = pd.read_csv("zamowienia.csv", sep=";", decimal=",", parse_dates=["data"], na_values=["brak"])
zamowienia.to_excel("zamowienia.xlsx", index=False, sheet_name="marzec")
zamowienia.to_json("zamowienia.json", orient="records", indent=1, force_ascii=False, date_format="iso")
zamowienia.to_parquet("zamowienia.parquet")
print(Path("zamowienia.json").read_text(encoding="utf-8")[:90])
for nazwa in ("zamowienia.xlsx", "zamowienia.json", "zamowienia.parquet"):
    print(f"{nazwa:<20}{Path(nazwa).stat().st_size / 1000:>5.1f} kB")
z_excela = pd.read_excel("zamowienia.xlsx", sheet_name="marzec")
z_parquet = pd.read_parquet("zamowienia.parquet")
print(z_excela["data"].dtype, z_parquet["data"].dtype, pd.read_json("zamowienia.json")["data"].dtype)
print(z_parquet.equals(zamowienia))
```

```{ .text .no-copy }
[
 {
  "id":1,
  "data":"2025-03-01T00:00:00.000",
  "klient":"Nowak",
  "miasto":"Kraków"
zamowienia.xlsx       5.5 kB
zamowienia.json       1.7 kB
zamowienia.parquet    5.6 kB
datetime64[us] datetime64[us] str
True
```

Trzy formaty, trzy zastosowania. **Excel** (`to_excel()`/`read_excel()`, pakiet openpyxl) to format odbiorcy — arkusz z nazwą, który otworzy każdy; daty przechodzą jako daty, a liczby wracają z typem odgadniętym z wartości — Excel nie rozróżnia liczb całkowitych od zmiennoprzecinkowych, więc kolumna `float64` o wartościach całkowitych wróciłaby jako `int64`. **JSON** z `orient="records"` — lista słowników, jak w rozdziale 9 — to format wymiany z aplikacjami i API; daty stają się napisami ISO, które `read_json()` odtwarza tylko w kolumnach o nazwach takich jak `date` lub z końcówką `_at`, więc kolumnę `data` wskazujemy argumentem `convert_dates=["data"]` albo zamieniamy po odczycie funkcją `to_datetime()` z podrozdziału o typach. **Parquet** (pakiet pyarrow) to format binarny, kolumnowy i skompresowany: zachowuje typy co do bitu (`equals()` daje `True`), czyta się szybciej niż CSV i zajmuje mniej miejsca przy dużych danych — dla dziesięciu wierszy metadane pliku zajmują więcej miejsca niż same dane, dla milionów wierszy proporcja się odwraca. Wyniki pośrednie analizy zapisujemy w Parquet, wyniki dla odbiorców — w CSV lub Excelu.

## Duże pliki — porcje i wybór kolumn

```python title="porcje.py"
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
pd.DataFrame({"klient": rng.integers(1, 1_000, 200_000), "kwota": rng.normal(100, 30, 200_000).round(2)}).to_csv("duzy.csv", index=False)
suma = 0.0
wiersze = 0
for porcja in pd.read_csv("duzy.csv", chunksize=50_000):
    suma += porcja["kwota"].sum()
    wiersze += len(porcja)
    print(len(porcja), end=" ")
print()
print(wiersze, round(suma / wiersze, 2))
tylko_kwota = pd.read_csv("duzy.csv", usecols=["kwota"], dtype={"kwota": "float32"})
print(Path("duzy.csv").stat().st_size // 1000, pd.read_csv("duzy.csv").memory_usage(deep=True).sum() // 1000, tylko_kwota.memory_usage(deep=True).sum() // 1000)
```

```{ .text .no-copy }
50000 50000 50000 50000 
200000 100.06
2258 3200 800
```

Plik większy od pamięci czytamy **porcjami** (ang. *chunk*): `chunksize=` zamienia `read_csv()` w iterator ramek po tyle wierszy, a agregaty — sumy, liczności, maksima — składamy z porcji jak w przykładzie z `memmap` w rozdziale 2. Gdy potrzebujemy tylko części kolumn, `usecols=` pomija resztę już przy odczycie — tu połowę — a `dtype=` z mniejszym typem zmniejsza pamięć o kolejną połowę; obie zmiany razem dają czterokrotną oszczędność. Metoda `memory_usage(deep=True)` podaje rzeczywisty rozmiar ramki z napisami włącznie (`deep=` ma znaczenie dla kolumn `object`, dla typu `str` wynik jest ten sam); porównanie z rozmiarem pliku pokazuje, że wczytana całość zajmuje więcej niż plik, bo każda liczba w ramce ma 8 bajtów niezależnie od liczby cyfr w pliku.
