# Zadanie, dane i decyzje

Projekt uczenia maszynowego zaczyna się tak samo jak raport z rozdziału 6: od pytania odbiorcy i od oględzin pliku, zanim jakikolwiek model zobaczy dane. Dochodzą dwie rzeczy, których raport nie wymagał: koszty obu rodzajów błędu i pytanie, czy każda kolumna będzie znana w chwili, gdy model ma odpowiedzieć.

## Zadanie i koszt błędu

Odbiorca — dział utrzymania klientów — chce co miesiąc listę klientów, do których wysłać ofertę zatrzymującą. Model ma przewidzieć **rezygnację** (ang. *churn*) na podstawie danych o umowie i zachowaniu klienta. Dwa rodzaje błędów kosztują różnie: klient, który odejdzie bez oferty, to 500 zł utraconego przychodu; oferta — zakładamy, że zatrzymuje klienta — to 80 zł, wydane także wtedy, gdy klient i tak by został. Zgodnie z rozdziałem 8 klasę pozytywną definiujemy jako rezygnację, miarą porównania modeli jest AUC, a próg decyzyjny dobierzemy tak, aby zminimalizować łączny koszt — i porównamy go z kosztem oferty dla wszystkich (80 zł na klienta) oraz braku ofert (500 zł na każdego odchodzącego).

## Układ projektu

Układ z rozdziału 6 bez katalogu danych przetworzonych — czyszczenie jest szybkie i odbywa się w pamięci — za to z katalogiem wyników, w którym obok raportu zapisujemy pakiet modelu:

```{ .text .no-copy }
rezygnacja-klientow/
├── dane/
│   ├── surowe/            klienci.csv — nigdy nie zmieniany
│   └── nowi_klienci.csv   klienci do oceny (przykład)
├── skrypty/               eksploracja.py, przygotowanie.py, modele.py, rysunki.py, porownanie.py, trenuj.py, przewiduj.py
├── tests/                 conftest.py, test_przygotowanie.py, test_modele.py, test_przewiduj.py
├── wyniki/
│   ├── rysunki/           PNG do raportu
│   ├── model-rezygnacja.joblib
│   ├── raport.md
│   └── ryzyko.csv         wynik oceny nowych klientów
├── generuj_surowe.py      generator pliku surowego — poza potokiem
├── .gitignore
├── requirements.txt
└── README.md
```

Skrypty uruchamiamy z katalogu projektu (`python skrypty/trenuj.py`), więc ścieżki w kodzie są względne do niego.

## Dane surowe

Eksport od operatora generujemy skryptem z ziarnem, jak w rozdziale 6: zależność rezygnacji od cech jest wpisana w generator — ze współdziałaniem cech, którego model liniowy sam nie odda — a wady wprowadzamy celowo. Skrypt uruchamiamy raz; nie należy do potoku:

```python title="generuj_surowe.py"
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 2000
umowa = rng.choice(["miesięczna", "roczna", "dwuletnia"], n, p=[0.45, 0.35, 0.2])
plan = rng.choice(["podstawowy", "standard", "premium"], n, p=[0.4, 0.4, 0.2])
oplata_planu = {"podstawowy": 49, "standard": 79, "premium": 129}
oplata = np.array([oplata_planu[p] for p in plan]) + rng.integers(-10, 21, n)
staz = np.clip(rng.exponential(24, n), 1, 84).round(0)
uslugi = rng.integers(0, 4, n)
zgloszenia = rng.poisson(1.2, n)
opoznione = rng.poisson(0.7, n)
platnosc = rng.choice(["karta", "polecenie zapłaty", "przelew"], n, p=[0.4, 0.35, 0.25])
wiek = np.clip(rng.normal(42, 13, n), 18, 85).round(0)
miesieczna = umowa == "miesięczna"
logit = (-2.7 + 1.6 * miesieczna - 1.2 * (umowa == "dwuletnia") + 0.35 * zgloszenia + 0.6 * opoznione
         + 1.2 * (staz <= 6) - 0.015 * staz + 0.5 * zgloszenia * miesieczna + 0.015 * (oplata - 80)
         - 0.45 * uslugi + 0.6 * (platnosc == "przelew") + 0.012 * (wiek - 42)
         + 0.5 * (opoznione >= 2) * (platnosc == "przelew") + rng.normal(0, 0.3, n))
rezygnacja = (rng.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
klienci = pd.DataFrame({
    "id_klienta": np.arange(10001, 10001 + n),
    "umowa": umowa,
    "plan": plan,
    "oplata_miesieczna": oplata.astype(float),
    "staz_miesiecy": staz.astype(int),
    "uslugi_dodatkowe": uslugi,
    "zgloszenia": zgloszenia,
    "opoznione_platnosci": opoznione,
    "platnosc": platnosc,
    "wiek": wiek,
    "powod_rezygnacji": np.where(rezygnacja == 1, rng.choice(["cena", "jakość", "przeprowadzka", "konkurencja"], n), ""),
    "rezygnacja": np.where(rezygnacja == 1, "tak", "nie"),
})

surowe = klienci.copy()
wybrane = rng.choice(n, 260, replace=False)
surowe.loc[wybrane[:80], "rezygnacja"] = surowe.loc[wybrane[:80], "rezygnacja"].map({"tak": "1", "nie": "0"})
surowe.loc[wybrane[80:110], "rezygnacja"] = surowe.loc[wybrane[80:110], "rezygnacja"].str.upper()
surowe.loc[wybrane[110:150], "plan"] = surowe.loc[wybrane[110:150], "plan"].str.capitalize() + " "
surowe.loc[wybrane[150:240], "wiek"] = np.nan
surowe.loc[wybrane[240:245], "wiek"] = 0.0
surowe.loc[wybrane[245:250], "wiek"] = 140.0
surowe = pd.concat([surowe, surowe.iloc[wybrane[250:260]]], ignore_index=True)
surowe = surowe.sample(frac=1, random_state=42).reset_index(drop=True)

Path("dane/surowe").mkdir(parents=True, exist_ok=True)
surowe.to_csv("dane/surowe/klienci.csv", index=False)
print(surowe.shape, round(rezygnacja.mean(), 3))
print(Path("dane/surowe/klienci.csv").read_text(encoding="utf-8").splitlines()[:3])
```

```{ .text .no-copy }
(2010, 12) 0.279
['id_klienta,umowa,plan,oplata_miesieczna,staz_miesiecy,uslugi_dodatkowe,zgloszenia,opoznione_platnosci,platnosc,wiek,powod_rezygnacji,rezygnacja', '11197,miesięczna,standard,97.0,10,1,1,1,karta,37.0,przeprowadzka,tak', '10527,dwuletnia,premium,134.0,9,1,2,0,karta,41.0,,nie']
```

Każdy klient ma umowę (miesięczna, roczna, dwuletnia), plan i opłatę miesięczną, staż w miesiącach, liczbę usług dodatkowych, zgłoszeń do pomocy technicznej i opóźnionych płatności w ostatnim roku, formę płatności i wiek. Rezygnacja zależy w generatorze najsilniej od rodzaju umowy, a zgłoszenia podnoszą ryzyko bardziej przy umowie miesięcznej — to współdziałanie cech z rozdziału 9. Wady: etykieta celu w sześciu zapisach (`tak`, `TAK`, `1`, `nie`, `NIE`, `0`), plan z wielką literą i spacją, wiek brakujący, zerowy albo równy 140, dziesięć powtórzonych klientów oraz kolumna `powod_rezygnacji`, wypełniona tylko u tych, którzy odeszli.

## Eksploracja

```python title="skrypty/eksploracja.py"
import pandas as pd

surowe = pd.read_csv("dane/surowe/klienci.csv")
print(surowe.shape)
print(surowe.dtypes.to_dict())
print(surowe.isna().sum()[lambda s: s > 0].to_dict())
print(surowe["id_klienta"].duplicated().sum(), surowe.duplicated().sum())
print(surowe["rezygnacja"].value_counts().to_dict())
print(surowe["plan"].value_counts().to_dict())
print(surowe["wiek"].describe().round(0)[["count", "min", "50%", "max"]].to_dict(), (surowe["wiek"] < 18).sum(), (surowe["wiek"] > 100).sum())
etykieta = surowe["rezygnacja"].str.strip().str.lower().isin(["tak", "1"]).astype(int)
print(round(etykieta.mean(), 3))
print(pd.crosstab(surowe["powod_rezygnacji"].notna(), etykieta, rownames=["podany powód"], colnames=["rezygnacja"]))
print(etykieta.groupby(surowe["umowa"]).mean().round(3).to_dict())
print(etykieta.groupby(pd.cut(surowe["staz_miesiecy"], [0, 6, 12, 24, 84]), observed=True).mean().round(3).to_dict())
```

```{ .text .no-copy }
(2010, 12)
{'id_klienta': dtype('int64'), 'umowa': <StringDtype(na_value=nan)>, 'plan': <StringDtype(na_value=nan)>, 'oplata_miesieczna': dtype('float64'), 'staz_miesiecy': dtype('int64'), 'uslugi_dodatkowe': dtype('int64'), 'zgloszenia': dtype('int64'), 'opoznione_platnosci': dtype('int64'), 'platnosc': <StringDtype(na_value=nan)>, 'wiek': dtype('float64'), 'powod_rezygnacji': <StringDtype(na_value=nan)>, 'rezygnacja': <StringDtype(na_value=nan)>}
{'wiek': 90, 'powod_rezygnacji': 1451}
10 10
{'nie': 1377, 'tak': 523, '0': 55, '1': 25, 'NIE': 19, 'TAK': 11}
{'podstawowy': 804, 'standard': 783, 'premium': 383, 'Podstawowy ': 16, 'Standard ': 15, 'Premium ': 9}
{'count': 1920.0, 'min': 0.0, '50%': 43.0, 'max': 140.0} 5 5
0.278
rezygnacja       0    1
podany powód           
False         1451    0
True             0  559
{'dwuletnia': 0.043, 'miesięczna': 0.495, 'roczna': 0.138}
{Interval(0, 6, closed='right'): 0.413, Interval(6, 12, closed='right'): 0.276, Interval(12, 24, closed='right'): 0.258, Interval(24, 84, closed='right'): 0.194}
```

Wydruki potwierdzają wady i pokazują skalę zadania: rezygnuje 28% klientów, więc klasy są nierównoliczne, ale nie skrajnie; przy umowie miesięcznej odchodzi połowa, przy dwuletniej mniej niż co dwudziesty; klienci w pierwszym półroczu odchodzą najczęściej. Tabela krzyżowa ujawnia **wyciek celu** z rozdziału 9: powód rezygnacji jest wpisany dokładnie u tych, którzy zrezygnowali, i u nikogo więcej. Kolumna powstaje po odejściu klienta — w chwili, gdy model ma wskazać, komu złożyć ofertę, nie istnieje — więc model nauczony na niej osiągnąłby AUC równe 1 i byłby bezużyteczny. To pytanie o każdą kolumnę („czy znam ją w chwili predykcji?”) zadajemy przed treningiem, bo walidacja krzyżowa wycieku nie wykryje.

## Decyzje

| Wada | Decyzja | Skutek |
|---|---|---|
| powtórzeni klienci | zostaje pierwszy wiersz o danym `id_klienta` | 10 wierszy mniej |
| etykieta `tak`/`TAK`/`1`/`nie`/`NIE`/`0` | `strip()`, `lower()`, słownik na 0/1; inna wartość zatrzymuje potok błędem | 110 etykiet ujednoliconych |
| pisownia planu | `strip()`, `lower()` | 40 wartości ujednoliconych |
| wiek poza 18–100 | traktujemy jako brak | 10 wartości |
| brak wieku | imputacja medianą w potoku, ze wskaźnikiem braku (rozdział 9) | 100 braków |
| `powod_rezygnacji` | usuwamy — wyciek celu | kolumna poza modelem |

```text title="README.md"
# Ryzyko rezygnacji klientów

Dane: `dane/surowe/klienci.csv` — eksport operatora (2010 wierszy, otrzymany 1 IX 2026);
plików surowych nie zmieniamy. Cel: `rezygnacja` (tak/nie) w roku poprzedzającym eksport.

Koszty (uzgodnione z działem utrzymania klientów): utrata klienta 500 zł, oferta 80 zł.
Miara porównania modeli: AUC; próg decyzyjny minimalizuje koszt na walidacji krzyżowej.

Decyzje czyszczenia (skrypty/przygotowanie.py): duplikaty po id_klienta usunięte;
etykiety i plan ujednolicone; wiek poza 18–100 jako brak, braki imputowane medianą;
kolumna powod_rezygnacji usunięta (wyciek celu — znana dopiero po odejściu).

Odtworzenie: `python -m pip install -r requirements.txt`, `python -m pytest -q`,
`python skrypty/trenuj.py` → wyniki/model-rezygnacja.joblib, wyniki/raport.md.
Ocena nowych klientów: `python skrypty/przewiduj.py plik.csv wyniki/ryzyko.csv`.
```

```text title=".gitignore"
.venv/
__pycache__/
.pytest_cache/
wyniki/
```

Decyzja o etykiecie ma jedną nowość wobec rozdziału 6: wartość spoza słownika nie zamienia się bez ostrzeżenia w brak, tylko zatrzymuje potok — etykieta celu jest zbyt ważna, by ją zgadywać. Pozostałe decyzje to czyszczenie z rozdziału 4 i imputacja z rozdziału 9, a usunięcie kolumny z wyciekiem jest decyzją najważniejszą i najłatwiejszą do pominięcia, dlatego trafia do README i do raportu.
