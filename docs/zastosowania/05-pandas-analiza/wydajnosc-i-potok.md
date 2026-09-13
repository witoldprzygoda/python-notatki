# Wydajność i potok analizy

Na 240 wierszach każda operacja trwa milisekundy; na dwóch milionach różnice między sposobami zapisu tej samej analizy rosną do sekund i setek megabajtów. Ten podrozdział mierzy je narzędziami z rozdziału 13 „Python Notatki”, a potem składa poznane operacje w **potok** (ang. *pipeline*): łańcuch funkcji, który z pliku wejściowego produkuje tabele raportu i daje się przetestować.

## Pomiar na dużej tabeli

```python title="duza-tabela.py"
import time

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 2_000_000
duza = pd.DataFrame({"kategoria": rng.choice(["książki", "elektronika", "zabawki", "sport"], n), "wartosc": rng.normal(100, 30, n).round(2), "klient": rng.integers(0, 1000, n)})
print(duza.memory_usage(deep=True).to_dict())


def zmierz(opis, funkcja):
    start = time.perf_counter()
    funkcja()
    print(f"{opis:<28}{(time.perf_counter() - start) * 1000:7.1f} ms")


zmierz("groupby po str", lambda: duza.groupby("kategoria")["wartosc"].mean())
duza["kategoria"] = duza["kategoria"].astype("category")
zmierz("groupby po category", lambda: duza.groupby("kategoria")["wartosc"].mean())
zmierz("maska i suma", lambda: duza.loc[duza["wartosc"] > 150, "wartosc"].sum())
zmierz("sort_values", lambda: duza.sort_values("wartosc"))
zmierz("merge z tabelą słownikową", lambda: duza.merge(pd.DataFrame({"klient": range(1000), "segment": rng.choice(["nowy", "stały"], 1000)}), on="klient"))
print(duza.memory_usage(deep=True)["kategoria"])
```

```{ .text .no-copy }
{'Index': 132, 'kategoria': 32002198, 'wartosc': 16000000, 'klient': 16000000}
groupby po str                 65.1 ms
groupby po category            26.9 ms
maska i suma                    6.0 ms
sort_values                   214.5 ms
merge z tabelą słownikową      73.7 ms
2000065
```

Dwa miliony wierszy z kolumną napisów zajmują kilkadziesiąt megabajtów; sama kolumna `kategoria` jako napisy — dwa razy więcej niż każda z kolumn liczbowych. Zamiana na typ kategorialny z rozdziału 4 zmniejsza ją kilkanaście razy i przyspiesza grupowanie, bo pandas grupuje po małych kodach całkowitych. Maska, sortowanie i złączenie z tysiącem wierszy tabeli słownikowej mieszczą się w ułamkach sekundy — to operacje wektorowe, wykonywane w kodzie skompilowanym. Funkcja `zmierz()` z `perf_counter()` z rozdziału 13 wystarcza do porównań rzędu wielkości; dokładniejsze pomiary daje `timeit`.

## Agregacje wbudowane zamiast własnych

```python title="agregacje-koszt.py"
import time

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 2_000_000
duza = pd.DataFrame({"klient": rng.integers(0, 1000, n), "wartosc": rng.normal(100, 30, n).round(2)})


def zmierz(opis, funkcja):
    start = time.perf_counter()
    wynik = funkcja()
    print(f"{opis:<32}{(time.perf_counter() - start) * 1000:7.1f} ms")
    return wynik


a = zmierz("agg('mean')", lambda: duza.groupby("klient")["wartosc"].agg("mean"))
b = zmierz("agg(lambda s: s.mean())", lambda: duza.groupby("klient")["wartosc"].agg(lambda s: s.mean()))
c = zmierz("apply(lambda s: s.mean())", lambda: duza.groupby("klient")["wartosc"].apply(lambda s: s.mean()))
print(np.allclose(a, b), np.allclose(a, c))
zmierz("transform('sum')", lambda: duza.groupby("klient")["wartosc"].transform("sum"))
```

```{ .text .no-copy }
agg('mean')                        27.3 ms
agg(lambda s: s.mean())           132.1 ms
apply(lambda s: s.mean())         120.8 ms
True True
transform('sum')                   33.7 ms
```

Nazwa funkcji w `agg()` uruchamia implementację pandas, która liczy wszystkie grupy w jednym przebiegu skompilowanego kodu; ta sama średnia podana jako `lambda` jest wywoływana tysiąc razy — raz na grupę — i trwa kilka razy dłużej; `apply()` z tą samą funkcją kosztuje tyle samo, bo również wywołuje ją raz na grupę, a wolniejsze jest dopiero `apply()` na całych ramkach grup. Na poziomie pojedynczych wierszy różnica jest jeszcze większa, co rozdział 4 zmierzył dla `apply()` wobec operacji wektorowej. Zasada z rozdziału 4 obowiązuje więc także przy grupowaniu: nazwy funkcji, `transform()` z nazwą i operacje wektorowe najpierw, funkcje własne tylko tam, gdzie wbudowanych nie ma.

## Pamięć i format pośredni

```python title="pamiec.py"
import time
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 2_000_000
duza = pd.DataFrame({"kategoria": rng.choice(["książki", "elektronika", "zabawki", "sport"], n), "wartosc": rng.normal(100, 30, n).round(2), "klient": rng.integers(0, 1000, n)})
print(duza.memory_usage(deep=True).sum() // 1_000_000)
oszczedna = duza.assign(kategoria=duza["kategoria"].astype("category"), klient=pd.to_numeric(duza["klient"], downcast="integer"), wartosc=pd.to_numeric(duza["wartosc"], downcast="float"))
print(oszczedna.dtypes.to_dict())
print(oszczedna.memory_usage(deep=True).sum() // 1_000_000)

for nazwa, zapis, odczyt in (("duza.csv", lambda: oszczedna.to_csv("duza.csv", index=False), lambda: pd.read_csv("duza.csv")), ("duza.parquet", lambda: oszczedna.to_parquet("duza.parquet"), lambda: pd.read_parquet("duza.parquet"))):
    start = time.perf_counter()
    zapis()
    czas_zapisu = time.perf_counter() - start
    start = time.perf_counter()
    wczytana = odczyt()
    czas_odczytu = time.perf_counter() - start
    print(f"{nazwa:<14}{Path(nazwa).stat().st_size // 1_000_000:>3} MB  zapis {czas_zapisu:.2f} s  odczyt {czas_odczytu:.2f} s  {wczytana['kategoria'].dtype}")
```

```{ .text .no-copy }
64
{'kategoria': CategoricalDtype(categories=['elektronika', 'książki', 'sport', 'zabawki'], ordered=False, categories_dtype=str), 'wartosc': dtype('float32'), 'klient': dtype('int16')}
14
duza.csv       40 MB  zapis 1.53 s  odczyt 0.67 s  str
duza.parquet    6 MB  zapis 0.19 s  odczyt 0.06 s  category
```

Trzy oszczędności zmniejszają ramkę kilkakrotnie: typ kategorialny dla kolumn o niewielu wartościach, `to_numeric(downcast=)` dobierający najmniejszy typ całkowity lub zmiennoprzecinkowy, który mieści dane (`int16` zamiast `int64`, gdy wartości mieszczą się w zakresie ±32 767; `float32` kosztem precyzji, o której mówił rozdział 2), oraz format pośredni Parquet z rozdziału 4 — kilkakrotnie mniejszy od CSV, wielokrotnie szybszy w zapisie i odczycie, a przy tym zachowujący typy, także kategorialny, który po odczycie z CSV wraca jako `str`. Wyniki pośrednie długiej analizy zapisujemy w Parquet, a duży CSV wczytujemy raz i od razu konwertujemy.

## Potok — łańcuch metod i `pipe()`

```python title="potok.py"
import pandas as pd


def wczytaj(sciezka):
    return pd.read_csv(sciezka, parse_dates=["data"]).drop_duplicates().dropna(subset=["ilosc"])


def dolacz_klientow(zamowienia, klienci):
    return zamowienia.merge(klienci, on="klient", how="left", validate="many_to_one")


def miesiecznie(zamowienia, kolumna):
    return zamowienia.groupby([pd.Grouper(key="data", freq="MS"), kolumna])["wartosc"].sum().round(0).unstack(fill_value=0)


klienci = pd.read_csv("klienci.csv")
raport = wczytaj("zamowienia-2025.csv").pipe(dolacz_klientow, klienci).pipe(miesiecznie, "segment")
raport.index = raport.index.strftime("%Y-%m")
print(raport)
print(wczytaj("zamowienia-2025.csv").query("kategoria == 'sport'").pipe(miesiecznie, "klient").iloc[:2, :3])
```

```{ .text .no-copy }
segment     nowy    stały
data                     
2025-01  10330.0   2905.0
2025-02  12153.0   8144.0
2025-03  14933.0  11157.0
2025-04  14521.0  11711.0
2025-05  10972.0   7656.0
2025-06  16967.0  16212.0
klient      Kowalska     Lis  Mazur
data                               
2025-01-01       0.0   874.0    0.0
2025-02-01       0.0  1184.0    0.0
```

Analiza to ciąg przekształceń: wczytaj i oczyść, dołącz tabele słownikowe, zagreguj, sformatuj. Każdy krok jako funkcja przyjmująca ramkę i zwracająca ramkę daje się nazwać, przetestować i użyć ponownie, a `pipe()` wpina taką funkcję w łańcuch metod — `ramka.pipe(f, argumenty)` to `f(ramka, argumenty)` zapisane w kolejności czytania, bez zagnieżdżonych nawiasów i zmiennych pośrednich. Ten sam krok `miesiecznie()` liczy tabelę według segmentu i według klienta, bo kolumna grupowania jest parametrem; `Grouper` z częstotliwością miesiąca zastępuje ręczne wycinanie miesiąca z daty.

## Z notatnika do modułu i testu

Funkcje potoku przenosimy z notatnika do modułu w katalogu `skrypty/` projektu z rozdziału 1 — tu, dla zwięzłości, moduł i test leżą w jednym katalogu, jak w rozdziale 16 „Python Notatki” — a obok powstaje test na kilkuwierszowej ramce, dla której wynik znamy z góry:

```python title="analiza.py"
"""Potok analizy zamówień: wczytanie, złączenie z klientami, agregacje miesięczne."""

import pandas as pd


def wczytaj(sciezka):
    return pd.read_csv(sciezka, parse_dates=["data"]).drop_duplicates().dropna(subset=["ilosc"])


def dolacz_klientow(zamowienia, klienci):
    return zamowienia.merge(klienci, on="klient", how="left", validate="many_to_one")


def miesiecznie(zamowienia, kolumna):
    return zamowienia.groupby([pd.Grouper(key="data", freq="MS"), kolumna])["wartosc"].sum().round(0).unstack(fill_value=0)
```

```python title="test_analiza.py"
import pandas as pd
import pytest

from analiza import dolacz_klientow, miesiecznie


@pytest.fixture
def zamowienia():
    return pd.DataFrame({"data": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-02-03"]), "klient": ["Nowak", "Lis", "Nowak"], "wartosc": [100.0, 50.0, 25.0]})


def test_miesiecznie_sumuje_w_miesiacach(zamowienia):
    wynik = miesiecznie(zamowienia, "klient")
    assert wynik.loc["2025-01-01", "Nowak"] == 100.0
    assert wynik.loc["2025-02-01", "Lis"] == 0.0
    assert wynik.shape == (2, 2)


def test_dolacz_klientow_zachowuje_zamowienia_bez_klienta(zamowienia):
    klienci = pd.DataFrame({"klient": ["Nowak"], "segment": ["stały"]})
    wynik = dolacz_klientow(zamowienia, klienci)
    assert len(wynik) == 3
    assert wynik["segment"].isna().sum() == 1


def test_dolacz_klientow_odrzuca_zduplikowany_slownik(zamowienia):
    klienci = pd.DataFrame({"klient": ["Nowak", "Nowak"], "segment": ["stały", "nowy"]})
    with pytest.raises(pd.errors.MergeError):
        dolacz_klientow(zamowienia, klienci)
```

```powershell title="Terminal"
python -m pytest -q test_analiza.py
```

```{ .text .no-copy }
...                                                                      [100%]
3 passed in 0.53s
```

Test nie potrzebuje pliku z 240 zamówieniami — trzy wiersze o znanych wartościach wystarczą, aby sprawdzić sumowanie w miesiącach, zachowanie zamówień bez klienta w słowniku i odrzucenie zduplikowanego słownika; `pd.testing.assert_frame_equal()` porównuje całe ramki, gdy oczekiwany wynik jest tabelą. Notatnik importuje moduł i zostaje miejscem na wykresy i wnioski, a potok — powtarzalny i przetestowany — uruchamia skrypt generujący na wzór rozdziału 3, wytwarzający tabele i rysunki raportu.

## Dalej: projekt raportu

Ścieżkę danych zamyka [projekt](../06-projekt-dane/index.md): z pliku surowego, przez czyszczenie, złączenia i agregacje z tego rozdziału, do raportu z tabelami i wykresami odtwarzanego jednym poleceniem — w układzie projektu z rozdziału 1 i ze skryptem generującym z rozdziału 3.
