# Środowisko projektu danych

Analiza, która działa dziś na jednym komputerze, ma działać za pół roku na innym — u współpracownika, recenzenta albo u nas po zmianie sprzętu. **Powtarzalność** (ang. *reproducibility*) nie powstaje samoistnie; wynika z kilku nawyków: stałego układu katalogu, przypiętych wersji bibliotek, niezmienianych danych surowych i notatnika, który wykonuje się od góry do dołu. Ten podrozdział zbiera je w jeden wzorzec projektu.

## Katalog projektu

Projekt danych to katalog o stałym układzie, w którym każdy plik ma swoje miejsce:

```{ .text .no-copy }
analiza-pogody/
├── .venv/                 środowisko wirtualne (poza repozytorium)
├── dane/
│   ├── surowe/            pliki wejściowe — nigdy nie zmieniane
│   └── przetworzone/      dane po czyszczeniu, generowane z surowych
├── notatniki/             notatniki .ipynb w kolejności numerowanej
├── skrypty/               moduły i skrypty z kodem wielokrotnego użytku
├── wyniki/                tabele i wykresy do raportu
├── requirements.txt
└── README.md
```

Zasady są proste: dane surowe czytamy, nigdy nie nadpisujemy — każda zmiana to nowy plik w `przetworzone/`, wytworzony kodem, który da się uruchomić ponownie; notatniki numerujemy według kolejności pracy (`01-wczytanie.ipynb`, `02-wykresy.ipynb`); kod, który powtarza się w kilku notatnikach, przenosimy do modułu w `skrypty/`. Plik `README.md` mówi, skąd pochodzą dane i jak odtworzyć wyniki.

## Środowisko i wersje

Każdy projekt ma własne [środowisko wirtualne](../../01-instalacja/venv.md) z rozdziału 1 i [plik wymagań](../../01-instalacja/pip.md#plik-requirementstxt) z przypiętymi wersjami — nie tylko pakietów, których importujemy, lecz także narzędzi notatnika; w projekcie danych, który nie jest pakietem, jeden plik wystarcza, a podział na `requirements.txt` i `requirements-dev.txt` z rozdziału 16 stosujemy, gdy kod trafia do pakietu:

```text title="requirements.txt"
numpy==2.5.3
matplotlib==3.11.2
ipykernel==7.3.0
jupyterlab==4.6.3
```

```powershell title="Terminal"
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Wersje ustalamy świadomie: `python -m pip index versions numpy` pokazuje wydania dostępne w chwili tworzenia projektu, a `python -m pip freeze` wypisuje wszystko, co zainstalowano — razem z zależnościami, których nie wybieraliśmy. Do pliku wymagań trafiają pakiety, o które prosimy; pełny wydruk `freeze` warto zachować obok jako `requirements-lock.txt`, gdy dokładne odtworzenie środowiska ma znaczenie. Bibliotek nie aktualizujemy w trakcie analizy; zmiana wersji to osobny krok z ponownym wykonaniem wszystkich notatników.

## Dane wejściowe i ścieżki

Dane wejściowe to najczęściej pliki [CSV i JSON](../../09-wejscie-wyjscie/csv-i-json.md) z rozdziału 9 — z pomiarów, z eksportu arkusza, z otwartych zbiorów danych instytucji publicznych. Zapisujemy je w `dane/surowe/` w postaci otrzymanej, wraz z notatką o źródle i dacie pobrania. Ścieżki w notatniku budujemy obiektami `Path` z podrozdziału [Ścieżki i system plików](../../09-wejscie-wyjscie/pathlib.md) względem katalogu projektu:

```python title="01-wczytanie.ipynb — komórka 1"
from pathlib import Path

PROJEKT = Path.cwd().parent  # notatnik leży w notatniki/
SUROWE = PROJEKT / "dane" / "surowe"
WYNIKI = PROJEKT / "wyniki"
```

W VSC katalogiem roboczym notatnika jest domyślnie katalog, w którym leży plik `.ipynb` (ustawienie `jupyter.notebookFileRoot`), stąd `Path.cwd().parent`. Bezwzględne ścieżki w rodzaju `C:\Users\anna\...` psują powtarzalność na innym komputerze; ścieżki względne od katalogu projektu działają wszędzie.

## Powtarzalność

Trzy źródła niepowtarzalności mają trzy środki zaradcze: losowość — generator z ziarnem; kolejność wykonania — **Restart** i **Run All**; nadpisywanie wyników — pliki z datą w nazwie. Pierwszy z nich, jak w podrozdziale [Operacje na tablicach](../../14-numpy-matplotlib/operacje.md) rozdziału 14:

```python title="powtarzalnosc.ipynb — komórka 1"
import numpy as np

rng = np.random.default_rng(42)
probka = rng.normal(170, 10, size=5)
probka.round(1)
```

```{ .text .no-copy }
array([173. , 159.6, 177.5, 179.4, 150.5])
```

Kolejność wykonania — **Restart** i **Run All** przed zapisaniem notatnika, aby wyniki pod komórkami odpowiadały kodowi czytanemu od góry. Nadpisywanie wyników — pliki pośrednie z datą w nazwie, aby kolejne uruchomienie nie zatarło poprzedniego (plik wynikowy, do którego odwołuje się raport, zachowuje stałą nazwę):

```python title="powtarzalnosc.ipynb — komórka 2"
from datetime import date

nazwa = f"srednie-{date.today():%Y-%m-%d}.csv"
nazwa
```

```{ .text .no-copy }
'srednie-2026-09-13.csv'
```

Format `%Y-%m-%d` porządkuje pliki alfabetycznie w kolejności czasowej. Na koniec zapisujemy do `README.md` wersję Pythona i polecenie, które odtwarza wszystko: `python -m jupyter nbconvert --execute --to notebook --inplace notatniki/*.ipynb`. nbconvert wykonuje każdy notatnik w jego własnym katalogu, więc `Path.cwd().parent` nadal wskazuje katalog projektu.

## Z notatnika do modułu

Notatnik jest dobry do prób, gorszy do kodu wielokrotnego użytku: funkcja skopiowana do trzech notatników to trzy miejsca do poprawiania. Gdy fragment kodu ustabilizuje się, przenosimy go do modułu w `skrypty/` — zwykłego pliku `.py` z rozdziału 7, z docstringiem z rozdziału 6 i testem z rozdziałów 7 i 16 — a w notatniku zostaje import i wywołanie:

```python title="skrypty/narzedzia.py"
"""Funkcje pomocnicze projektu analizy pogody."""

import numpy as np


def srednia_roczna(temperatury: np.ndarray, lata: np.ndarray, rok: int) -> float:
    """Zwraca średnią temperaturę z wierszy danego roku."""
    return float(temperatury[lata == rok].mean())
```

```python title="01-wczytanie.ipynb — komórka 2"
import sys

sys.path.append(str(PROJEKT / "skrypty"))
from narzedzia import srednia_roczna
```

```python title="01-wczytanie.ipynb — komórka 3"
import numpy as np

srednia_roczna(np.array([1.0, 2.0, 3.0]), np.array([2024, 2024, 2025]), 2024)
```

```{ .text .no-copy }
1.5
```

Dopisanie katalogu do `sys.path` — tu ścieżki `PROJEKT` z pierwszej komórki — to najprostsze rozwiązanie na początek; w większym projekcie moduły trafiają do pakietu z `pyproject.toml` instalowanego edytowalnie, jak w podrozdziale [Struktura projektu i pierwsze testy](../../07-moduly/struktura-projektu.md#instalacja-edytowalna-w-srodowisku-wirtualnym) rozdziału 7 — wtedy import działa z każdego miejsca bez zmian ścieżki. Po każdej zmianie modułu jądro trzeba zrestartować (albo wywołać `importlib.reload()` z rozdziału 7), bo `import` wczytuje moduł raz; polecenia `%load_ext autoreload` i `%autoreload 2` na początku notatnika każą IPythonowi przeładowywać zmienione moduły automatycznie.
