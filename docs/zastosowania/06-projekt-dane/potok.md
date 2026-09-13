# Potok — czyszczenie, analiza i testy

Decyzje z poprzedniego podrozdziału zamieniamy w kod: moduł przygotowania, który z pliku surowego tworzy tabelę przetworzoną i liczy, co odrzucił, oraz moduł analizy, który z tabeli przetworzonej wytwarza odpowiedzi na pytania raportu. Oba są zwykłymi modułami z rozdziału 7 „Python Notatki” — funkcje przyjmują ramkę i zwracają ramkę, jak w potoku z rozdziału 5 — a testy sprawdzają je na kilku wierszach o znanym wyniku.

## Moduł przygotowania

```python title="skrypty/przygotowanie.py"
"""Wczytanie pliku surowego, czyszczenie według decyzji z README i zapis danych przetworzonych."""

from pathlib import Path

import pandas as pd

SUROWE = Path("dane/surowe/zamowienia_surowe.csv")
KLIENCI = Path("dane/surowe/klienci.csv")
PRZETWORZONE = Path("dane/przetworzone/zamowienia.parquet")
PROG_ODSTAJACEJ = 4


def wczytaj_surowe(sciezka=SUROWE):
    return pd.read_csv(sciezka, sep=";", decimal=",")


def parsuj_daty(napisy):
    iso = pd.to_datetime(napisy, format="%Y-%m-%d", errors="coerce")
    polskie = pd.to_datetime(napisy, format="%d.%m.%Y", errors="coerce")
    return iso.fillna(polskie)


def oczysc(surowe):
    """Zwraca oczyszczoną ramkę i słownik z liczbą wierszy dotkniętych każdą decyzją."""
    dziennik = {"wierszy_surowych": len(surowe)}
    czyste = surowe.drop_duplicates()
    dziennik["duplikaty"] = len(surowe) - len(czyste)
    dziennik["daty_polskie"] = int(czyste["data"].str.contains(".", regex=False).sum())
    dziennik["rabat_brak"] = int((czyste["rabat"] == "brak").sum())
    dziennik["pisownia"] = int((czyste["klient"] != czyste["klient"].str.strip().str.capitalize()).sum() + (czyste["kategoria"] != czyste["kategoria"].str.strip().str.lower()).sum())
    czyste = czyste.assign(
        data=parsuj_daty(czyste["data"]),
        klient=czyste["klient"].str.strip().str.capitalize(),
        kategoria=czyste["kategoria"].str.strip().str.lower(),
        rabat=pd.to_numeric(czyste["rabat"], errors="coerce").fillna(0).astype(int),
    )
    bez_ilosci = czyste["ilosc"].isna()
    dziennik["bez_ilosci"] = czyste.loc[bez_ilosci, "id"].tolist()
    czyste = czyste.loc[~bez_ilosci].astype({"ilosc": int})
    czyste["wartosc"] = (czyste["ilosc"] * czyste["cena"] * (1 - czyste["rabat"] / 100)).round(2)
    mediana = czyste.groupby("kategoria")["cena"].transform("median")
    czyste["odstajaca"] = czyste["cena"] > PROG_ODSTAJACEJ * mediana
    dziennik["odstajace"] = czyste.loc[czyste["odstajaca"], "id"].tolist()
    czyste = czyste.sort_values("data").reset_index(drop=True)
    dziennik["wierszy_czystych"] = len(czyste)
    return czyste, dziennik


def zapisz_przetworzone(czyste, sciezka=PRZETWORZONE):
    sciezka.parent.mkdir(parents=True, exist_ok=True)
    czyste.to_parquet(sciezka)
    return sciezka


if __name__ == "__main__":
    czyste, dziennik = oczysc(wczytaj_surowe())
    print(dziennik)
    print(czyste.dtypes.to_dict())
    print(czyste["data"].min().date(), czyste["data"].max().date(), czyste["data"].isna().sum())
    print(zapisz_przetworzone(czyste).as_posix(), pd.read_parquet(PRZETWORZONE).shape)
```

```{ .text .no-copy }
{'wierszy_surowych': 245, 'duplikaty': 5, 'daty_polskie': 12, 'rabat_brak': 4, 'pisownia': 13, 'bez_ilosci': [110, 207, 50, 88], 'odstajace': [163, 231], 'wierszy_czystych': 236}
{'id': dtype('int64'), 'data': dtype('<M8[us]'), 'klient': <StringDtype(na_value=nan)>, 'kategoria': <StringDtype(na_value=nan)>, 'ilosc': dtype('int64'), 'cena': dtype('float64'), 'rabat': dtype('int64'), 'wartosc': dtype('float64'), 'odstajaca': dtype('bool')}
2025-01-04 2025-06-29 0
dane/przetworzone/zamowienia.parquet (236, 9)
```

Moduł ma cztery funkcje o jednym zadaniu każda oraz stałe — ścieżki i próg — na górze, gdzie łatwo je odnaleźć i zmienić. `oczysc()` zwraca dwie rzeczy: tabelę i **dziennik decyzji** — słownik z liczbą duplikatów, dat w drugim formacie i pól z ujednoliconą pisownią oraz identyfikatorami odrzuconych i odstających wierszy — który trafi do raportu, więc przebieg czyszczenia pozostaje jawny dla odbiorcy. Rabat `brak` nie wymaga osobnej gałęzi: `to_numeric(errors="coerce")` z `fillna(0)`, jak w rozdziale 4, wykonuje decyzję „brak to zero”. Blok strażnika `__main__` z rozdziału 7 pozwala uruchomić moduł jako skrypt i obejrzeć dziennik; wynik trafia do pliku Parquet z rozdziału 4, z typami — przede wszystkim datą — które CSV zapisałby jako tekst; przy każdym wczytaniu CSV datę trzeba by odtwarzać przez `parse_dates=`, a typy liczb i wartości logicznej pandas odgadywałby na nowo z napisów.

## Moduł analizy

```python title="skrypty/analiza.py"
"""Tabele raportu z danych przetworzonych: przychód w czasie, kategorie, klienci."""

import pandas as pd


def do_analizy(czyste):
    return czyste.loc[~czyste["odstajaca"]]


def miesiecznie(czyste):
    dane = do_analizy(czyste).set_index("data")["wartosc"]
    tabela = dane.resample("MS").agg(przychod="sum", zamowien="count", srednia="mean").round(0)
    tabela["zmiana_%"] = (tabela["przychod"].pct_change() * 100).round(1)
    tabela.index = tabela.index.strftime("%Y-%m")
    return tabela


def tygodniowo(czyste):
    dane = do_analizy(czyste).set_index("data")["wartosc"].resample("W").sum()
    return pd.DataFrame({"przychod": dane, "srednia_4tyg": dane.rolling(4).mean()}).round(0)


def wedlug_kategorii(czyste):
    dane = do_analizy(czyste)
    tabela = dane.groupby("kategoria").agg(zamowien=("id", "size"), przychod=("wartosc", "sum"), srednia=("wartosc", "mean")).round(0)
    tabela["udzial_%"] = (tabela["przychod"] / tabela["przychod"].sum() * 100).round(1)
    return tabela.sort_values("przychod", ascending=False)


def wedlug_klientow(czyste, klienci):
    dane = do_analizy(czyste).merge(klienci, on="klient", how="left", validate="many_to_one")
    tabela = dane.groupby(["segment", "klient"]).agg(zamowien=("id", "size"), przychod=("wartosc", "sum")).round(0)
    return tabela.sort_values(["segment", "przychod"], ascending=[True, False])


def segmenty(czyste, klienci):
    dane = do_analizy(czyste).merge(klienci, on="klient", how="left", validate="many_to_one")
    return dane.groupby("segment").agg(klientow=("klient", "nunique"), zamowien=("id", "size"), przychod=("wartosc", "sum"), srednie_zamowienie=("wartosc", "mean")).round(0)


def odstajace(czyste):
    tabela = czyste.loc[czyste["odstajaca"], ["id", "data", "klient", "kategoria", "ilosc", "cena"]]
    return tabela.assign(data=tabela["data"].dt.strftime("%Y-%m-%d"))
```

Każda funkcja odpowiada na jedno pytanie raportu i zwraca ramkę gotową do wydruku; wspólny krok — wyłączenie wartości odstających — jest osobną funkcją, więc reguła istnieje w jednym miejscu. Nazwy kolumn to nazwy techniczne bez polskich znaków; polskie nagłówki nada dopiero skrypt generujący, tuż przed zapisem. Moduł nie czyta plików ani niczego nie drukuje — dostaje ramki i oddaje ramki, jak potok z rozdziału 5.

## Podgląd wyników

```python title="skrypty/podglad.py"
import pandas as pd

from analiza import miesiecznie, odstajace, segmenty, tygodniowo, wedlug_kategorii, wedlug_klientow
from przygotowanie import KLIENCI, oczysc, wczytaj_surowe

czyste, dziennik = oczysc(wczytaj_surowe())
klienci = pd.read_csv(KLIENCI)
print(miesiecznie(czyste))
print(tygodniowo(czyste).tail(3))
print(wedlug_kategorii(czyste))
print(wedlug_klientow(czyste, klienci))
print(segmenty(czyste, klienci))
print(odstajace(czyste))
```

```{ .text .no-copy }
         przychod  zamowien  srednia  zmiana_%
data                                          
2025-01   13235.0        18    735.0       NaN
2025-02   20297.0        27    752.0      53.4
2025-03   25847.0        42    615.0      27.3
2025-04   25665.0        56    458.0      -0.7
2025-05   18440.0        39    473.0     -28.2
2025-06   32315.0        52    621.0      75.2
            przychod  srednia_4tyg
data                              
2025-06-15   11166.0        7128.0
2025-06-22    6299.0        7049.0
2025-06-29    4853.0        7863.0
             zamowien  przychod  srednia  udzial_%
kategoria                                         
elektronika        45   84445.0   1877.0      62.2
sport              34   23207.0    683.0      17.1
zabawki            63   16271.0    258.0      12.0
książki            92   11877.0    129.0       8.7
                    zamowien  przychod
segment klient                        
nowy    Lis               36   32566.0
        Mazur             47   28430.0
        Wiśniewski        42   17591.0
stały   Zielińska         38   24149.0
        Nowak             40   19971.0
        Kowalska          31   13091.0
         klientow  zamowien  przychod  srednie_zamowienie
segment                                                  
nowy            3       125   78588.0               629.0
stały           3       109   57212.0               525.0
      id        data      klient kategoria  ilosc    cena
159  163  2025-05-13       Mazur     sport      1  2123.4
229  231  2025-06-23  Wiśniewski   zabawki      1  1802.0
```

Skrypt w `skrypty/` importuje sąsiednie moduły wprost, bo Python dodaje katalog uruchamianego pliku do `sys.path` — to samo, co w rozdziale 1 robił notatnik przez `sys.path.append()`. Podgląd służy do sprawdzenia, czy tabele są wiarygodne, zanim trafią do raportu: sumy miesięczne zgadzają się z rozdziałem 5 z dokładnością do wierszy odrzuconych i odstających oraz rabatów `brak`, które w danych rozdziału 5 wynosiły 10%, a dwie ceny odstające to dokładnie te, które wprowadził generator.

## Testy

Testy — pytest z rozdziałów 7 i 16 „Python Notatki” — leżą w `tests/`; plik `conftest.py` dodaje katalog `skrypty/` do ścieżki importu, żeby testy widziały moduły bez instalowania pakietu — rozwiązanie doraźne, wystarczające dla projektu bez pakietu; w większym projekcie moduły trafiłyby do pakietu z `pyproject.toml` instalowanego edytowalnie, jak w rozdziale 7:

```python title="tests/conftest.py"
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skrypty"))
```

```python title="tests/test_przygotowanie.py"
import pandas as pd
import pytest

from przygotowanie import oczysc, parsuj_daty


@pytest.fixture
def surowe():
    return pd.DataFrame({
        "id": [1, 2, 2, 3, 4, 5, 6],
        "data": ["2025-03-01", "05.03.2025", "05.03.2025", "2025-03-09", "2025-03-10", "2025-03-11", "2025-03-12"],
        "klient": ["Nowak", " NOWAK ", " NOWAK ", "lis", "Lis", "lis", "LIS"],
        "kategoria": ["książki", "Książki ", "Książki ", "sport", "sport", "sport", "Sport"],
        "ilosc": [2, 1, 1, None, 1, 2, 1],
        "cena": [40.0, 50.0, 50.0, 100.0, 5000.0, 120.0, 90.0],
        "rabat": ["0", "brak", "brak", "10", "0", "10", "0"],
    })


def test_parsuj_daty_oba_formaty():
    daty = parsuj_daty(pd.Series(["2025-03-01", "05.03.2025", "2025-06-12"]))
    assert daty.dt.strftime("%Y-%m-%d").tolist() == ["2025-03-01", "2025-03-05", "2025-06-12"]


def test_oczysc_stosuje_decyzje(surowe):
    czyste, dziennik = oczysc(surowe)
    assert dziennik["duplikaty"] == 1
    assert dziennik["daty_polskie"] == 1
    assert dziennik["pisownia"] == 6
    assert dziennik["rabat_brak"] == 1
    assert dziennik["bez_ilosci"] == [3]
    assert czyste["data"].notna().all()
    assert czyste["klient"].tolist() == ["Nowak", "Nowak", "Lis", "Lis", "Lis"]
    assert czyste["kategoria"].unique().tolist() == ["książki", "sport"]
    assert czyste["rabat"].tolist() == [0, 0, 0, 10, 0]
    assert czyste["wartosc"].tolist() == [80.0, 50.0, 5000.0, 216.0, 90.0]


def test_oczysc_oznacza_odstajace(surowe):
    czyste, dziennik = oczysc(surowe)
    assert dziennik["odstajace"] == [4]
    assert czyste.loc[czyste["id"] == 4, "odstajaca"].item()
```

```python title="tests/test_analiza.py"
import pandas as pd
import pytest

from analiza import miesiecznie, wedlug_kategorii


@pytest.fixture
def czyste():
    return pd.DataFrame({
        "id": [1, 2, 3, 4],
        "data": pd.to_datetime(["2025-01-05", "2025-01-20", "2025-02-03", "2025-02-10"]),
        "klient": ["Nowak", "Lis", "Nowak", "Lis"],
        "kategoria": ["książki", "sport", "książki", "sport"],
        "wartosc": [100.0, 50.0, 25.0, 75.0],
        "odstajaca": [False, True, False, False],
    })


def test_miesiecznie_pomija_odstajace(czyste):
    tabela = miesiecznie(czyste)
    assert tabela.index.tolist() == ["2025-01", "2025-02"]
    assert tabela["przychod"].tolist() == [100.0, 100.0]
    assert tabela["zmiana_%"].tolist()[1] == 0.0


def test_wedlug_kategorii_udzialy_sumuja_sie_do_stu(czyste):
    tabela = wedlug_kategorii(czyste)
    assert tabela.index.tolist() == ["książki", "sport"]
    assert tabela["udzial_%"].tolist() == [62.5, 37.5]
```

```powershell title="Terminal"
python -m pytest -q
```

```{ .text .no-copy }
.....                                                                    [100%]
5 passed in 0.61s
```

Dane testowe są małe i ułożone tak, aby uruchomić każdą decyzję: duplikat, oba formaty dat, nazwisko w trzech pisowniach, `brak`, pustą ilość i cenę odstającą — z dwiema zwykłymi cenami tej samej kategorii, bo mediana z jednej wartości nie wykryłaby odstającej. Test dat sprawdza wprost datę 12 czerwca — tę, którą `format="mixed"` odwróciłby na 6 grudnia — więc gdyby ktoś „uprościł” parsowanie, test to wykryje. Testy analizy podają jako fixture ramkę już oczyszczoną — jak w rozdziale 5 — więc awaria testu wskazuje moduł, nie dane.
