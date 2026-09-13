# Zadanie, dane i decyzje

Projekt zaczyna się nie od kodu, lecz od pytań i od spojrzenia na dane: co raport ma odpowiedzieć, jak wyglądają pliki wejściowe i co w nich trzeba naprawić, zanim jakakolwiek liczba trafi do tabeli. Decyzje z tego etapu spisujemy — bez tego za miesiąc nikt nie odtworzy, dlaczego część zamówień zniknęła z sum.

## Pytania raportu

Odbiorca — kierownik sklepu — chce wiedzieć:

1. Jak zmieniał się przychód z miesiąca na miesiąc i z tygodnia na tydzień?
2. Które kategorie dają największy przychód i jaki mają udział?
3. Którzy klienci kupują najwięcej i czy klienci nowi różnią się od stałych?
4. Jakiej jakości są dane: ile wierszy odrzucono, co uzupełniono, które wartości są podejrzane?

Każde pytanie otrzyma w raporcie tabelę lub rysunek, a czwarte — sekcję o jakości danych, którą w raportach pomija się najczęściej i najbardziej niesłusznie.

## Układ projektu

Układ z rozdziału 1 tej części — bez katalogu `notatniki/`, bo projekt działa skryptami — uzupełniony o katalog testów z rozdziału 7 i `conftest.py` z rozdziału 16 „Python Notatki”:

```{ .text .no-copy }
raport-sprzedazy/
├── dane/
│   ├── surowe/            zamowienia_surowe.csv, klienci.csv — nigdy nie zmieniane
│   └── przetworzone/      zamowienia.parquet — wynik potoku
├── skrypty/               eksploracja.py, przygotowanie.py, analiza.py, podglad.py, rysunki.py, generuj_raport.py
├── tests/                 conftest.py, test_przygotowanie.py, test_analiza.py
├── wyniki/
│   ├── tabele/            CSV z tabelami raportu
│   ├── rysunki/           PNG
│   └── raport.md          dokument końcowy
├── generuj_surowe.py      generator pliku surowego — poza potokiem
├── .gitignore
├── requirements.txt
└── README.md
```

Skrypty uruchamiamy z katalogu projektu (`python skrypty/generuj_raport.py`), więc ścieżki w kodzie są względne do niego.

## Dane surowe

Plik od sklepu ma wady typowe dla eksportu edytowanego przez kilka osób w dwóch arkuszach; aby projekt był powtarzalny, plik generujemy skryptem z ziarnem — na bazie zamówień z rozdziału 5, do których wprowadzamy wady celowo. Skrypt uruchamiamy raz, z katalogu projektu; nie należy do potoku:

```python title="generuj_surowe.py"
from pathlib import Path

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

surowe = zamowienia.astype({"ilosc": "object", "rabat": "object"})
surowe["data"] = surowe["data"].dt.strftime("%Y-%m-%d")
wybrane = rng.choice(n, 40, replace=False)
surowe.loc[wybrane[:12], "data"] = zamowienia.loc[wybrane[:12], "data"].dt.strftime("%d.%m.%Y")
surowe.loc[wybrane[12:18], "klient"] = " " + surowe.loc[wybrane[12:18], "klient"].str.upper() + " "
surowe.loc[wybrane[18:22], "klient"] = surowe.loc[wybrane[18:22], "klient"].str.lower()
surowe.loc[wybrane[22:26], "rabat"] = "brak"
surowe.loc[wybrane[26:30], "ilosc"] = None
surowe.loc[wybrane[30:33], "kategoria"] = surowe.loc[wybrane[30:33], "kategoria"].str.capitalize() + " "
surowe.loc[wybrane[33:35], "cena"] = (surowe.loc[wybrane[33:35], "cena"] * 10).round(2)
surowe = pd.concat([surowe, surowe.iloc[wybrane[35:40]]], ignore_index=True)
surowe = surowe.sample(frac=1, random_state=42).reset_index(drop=True)

Path("dane/surowe").mkdir(parents=True, exist_ok=True)
surowe.to_csv("dane/surowe/zamowienia_surowe.csv", index=False, sep=";", decimal=",")
print(surowe.shape)
print(Path("dane/surowe/zamowienia_surowe.csv").read_text(encoding="utf-8").splitlines()[:4])
```

```{ .text .no-copy }
(245, 7)
['id;data;klient;kategoria;ilosc;cena;rabat', '25;2025-02-08;Kowalska;książki;1;47,58;0', '7;2025-01-14;Mazur;elektronika;4;792,01;0', '154;2025-05-08;Mazur;książki;4;44,2;5']
```

Wady wprowadzone do pliku: dwanaście dat w formacie `dd.mm.yyyy` obok ISO, dziesięć nazwisk ze spacjami i inną wielkością liter, cztery rabaty jako słowo `brak`, cztery puste ilości, trzy kategorie z wielką literą i spacją na końcu, dwie ceny dziesięciokrotnie za wysokie (przesunięty przecinek) i pięć powtórzonych wierszy; kolejność wierszy jest losowa. Drugi plik to spis klientów z rozdziału 5:

```text title="dane/surowe/klienci.csv"
klient,miasto,segment
Nowak,Kraków,stały
Kowalska,Tarnów,stały
Wiśniewski,Rzeszów,nowy
Zielińska,Nowy Sącz,stały
Lis,Kraków,nowy
Mazur,Tarnów,nowy
Kaczmarek,Kielce,nowy
```

## Eksploracja

Zanim napiszemy potok, oglądamy plik narzędziami z rozdziału 4 — w notatniku albo, jak tu, w skrypcie eksploracyjnym, który uruchamiamy raz i zostawiamy w projekcie jako zapis pierwszych oględzin:

```python title="skrypty/eksploracja.py"
import pandas as pd

surowe = pd.read_csv("dane/surowe/zamowienia_surowe.csv", sep=";", decimal=",")
print(surowe.shape)
print(surowe.dtypes.to_dict())
print(surowe.isna().sum().to_dict())
print(surowe.duplicated().sum(), surowe["id"].duplicated().sum())
print(sorted(surowe["klient"].unique().tolist()))
print(surowe["kategoria"].unique().tolist(), surowe["rabat"].unique().tolist())
print(surowe["data"].str.contains(".", regex=False).sum())
zgadywane = pd.to_datetime(surowe["data"], format="mixed", dayfirst=True)
print(zgadywane.min().date(), zgadywane.max().date())
iso = pd.to_datetime(surowe["data"], format="%Y-%m-%d", errors="coerce")
polskie = pd.to_datetime(surowe["data"], format="%d.%m.%Y", errors="coerce")
daty = iso.fillna(polskie)
print(daty.isna().sum(), daty.min().date(), daty.max().date())
mediana = surowe.groupby(surowe["kategoria"].str.strip().str.lower())["cena"].transform("median")
print(surowe.loc[surowe["cena"] > 4 * mediana, ["id", "kategoria", "cena"]].to_dict("records"))
```

```{ .text .no-copy }
(245, 7)
{'id': dtype('int64'), 'data': <StringDtype(na_value=nan)>, 'klient': <StringDtype(na_value=nan)>, 'kategoria': <StringDtype(na_value=nan)>, 'ilosc': dtype('float64'), 'cena': dtype('float64'), 'rabat': <StringDtype(na_value=nan)>}
{'id': 0, 'data': 0, 'klient': 0, 'kategoria': 0, 'ilosc': 4, 'cena': 0, 'rabat': 0}
5 5
[' KOWALSKA ', ' MAZUR ', ' NOWAK ', ' WIŚNIEWSKI ', 'Kowalska', 'Lis', 'Mazur', 'Nowak', 'Wiśniewski', 'Zielińska', 'mazur', 'wiśniewski', 'zielińska']
['książki', 'elektronika', 'zabawki', 'sport', 'Książki ', 'Zabawki '] ['0', '5', '10', '20', 'brak']
12
2025-01-02 2025-12-06
0 2025-01-04 2025-06-29
[{'id': 163, 'kategoria': 'sport', 'cena': 2123.4}, {'id': 231, 'kategoria': 'zabawki', 'cena': 1802.0}]
```

Wydruki potwierdzają każdą z wad i ujawniają jedną pułapkę: `to_datetime()` z `format="mixed"` i `dayfirst=True` odczytuje daty w obu formatach bez błędu, ale w datach ISO zamienia dzień z miesiącem, gdy dzień nie przekracza dwunastu — stąd zamówienia z grudnia w pliku z pierwszego półrocza. Bezpieczne rozwiązanie to dwa jawne wzorce z `errors="coerce"` i `fillna()`: każda data pasuje dokładnie do jednego, a niepasująca do żadnego zostałaby brakiem, który wychwyci test. **Ceny odstające** (ang. *outlier*) znajdujemy porównaniem z medianą kategorii — statystyką odporną na skrajne wartości, znaną z rozdziału 2 — dwie ceny przekraczają ją ponad czterokrotnie.

## Decyzje czyszczenia

Każda wada wymaga decyzji, a decyzja — uzasadnienia, które trafia do `README.md` i do sekcji raportu o jakości danych:

| Wada | Decyzja | Skutek |
|---|---|---|
| powtórzone wiersze | usuwamy dokładne duplikaty | 5 wierszy mniej |
| dwa formaty dat | parsujemy jawnie oba wzorce | 0 braków |
| pisownia nazwisk i kategorii | `strip()`, `capitalize()` dla nazwisk, `lower()` dla kategorii | 6 klientów, 4 kategorie |
| rabat `brak` | traktujemy jako 0% — brak wpisu oznacza brak rabatu | wartość liczona z pełnej ceny |
| pusta ilość | odrzucamy wiersz — wartości nie da się policzyć | 4 wiersze mniej, wymienione w raporcie |
| cena ponad 4× mediany kategorii | oznaczamy jako odstającą, wyłączamy z sum, wymieniamy w raporcie | 2 wiersze poza sumami |

```text title="README.md"
# Raport sprzedaży — I półrocze 2025

Dane: `dane/surowe/zamowienia_surowe.csv` (eksport sklepu, otrzymany 1 VII 2025),
`dane/surowe/klienci.csv` (spis klientów). Plików surowych nie zmieniamy.

Decyzje czyszczenia (skrypty/przygotowanie.py):
- duplikaty usunięte; daty w formatach ISO i dd.mm.yyyy parsowane jawnie;
- nazwiska i kategorie ujednolicone (spacje, wielkość liter);
- rabat „brak” = 0%; wiersze bez ilości odrzucone; ceny > 4× mediany kategorii
  oznaczone jako odstające i wyłączone z sum (lista w raporcie).

Odtworzenie: `python -m pip install -r requirements.txt`, `python -m pytest -q`,
`python skrypty/generuj_raport.py` → wyniki/raport.md, wyniki/tabele/, wyniki/rysunki/.
```

```text title=".gitignore"
.venv/
__pycache__/
dane/przetworzone/
wyniki/
```

Plik `.gitignore` z rozdziału 16 „Python Notatki” wyłącza z repozytorium to, co powstaje z kodu — dane przetworzone i wyniki odtwarza skrypt, więc w historii zmian zostają tylko dane surowe, kod i README. Progi i reguły — „ponad cztery mediany”, „brak to zero” — są decyzjami merytorycznymi, nie technicznymi; w prawdziwym projekcie uzgadniamy je z odbiorcą i zapisujemy, kto i kiedy je przyjął.
