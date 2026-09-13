# Styl i formatowanie kodu

Kod czyta się wielokrotnie częściej, niż pisze — także własny, po kilku miesiącach. Styl nie jest kwestią gustu, lecz umowy: PEP 8 z rozdziału 1 i Zen Pythona z rozdziału 2 opisują ją słowami, a narzędzia z tego podrozdziału egzekwują ją automatycznie, więc dyskusje o odstępach i cudzysłowach znikają z przeglądu kodu (ang. *code review*).

## Zen Pythona w praktyce

Aforyzmy z [PEP 20](https://peps.python.org/pep-0020/), przywołane w rozdziale [2. Konsola i pierwsze kroki](../02-konsola/konsola-w-praktyce.md), przekładają się na konkretne wybory:

| Aforyzm | W kodzie |
|---|---|
| Czytelność się liczy | nazwy opisowe: `srednia_ocen`, nie `s`; jedna myśl na wiersz |
| Jawne lepsze niż niejawne | `import math` zamiast `from math import *`; argumenty nazwane w wywołaniach z wieloma parametrami |
| Proste lepsze niż złożone | pętla zamiast zagnieżdżonego złożenia listowego (rozdział 13) |
| Płaskie lepsze niż zagnieżdżone | wczesny `return` zamiast kaskady `if`/`else` |
| Błędy nie powinny przechodzić bez echa | `except ValueError:` zamiast gołego `except:` (rozdział 8) |
| Powinien istnieć jeden oczywisty sposób | f-string do formatowania, `pathlib` do ścieżek, `with` do zasobów |
| Teraz jest lepsze niż nigdy | test i adnotacja pisane razem z kodem, nie „później” |

## PEP 8 w praktyce

[PEP 8](https://peps.python.org/pep-0008/) to przewodnik stylu biblioteki standardowej, przyjęty przez społeczność jako norma. Najczęstsze reguły:

| Reguła | Dobrze | Źle |
|---|---|---|
| nazwy funkcji i zmiennych małymi literami z podkreśleniem, klas — wielkimi literami początkowymi, stałych — wielkimi | `pole_kola`, `KontoBankowe`, `MAX_PROB` | `poleKola`, `konto_bankowe`, `maxProb` |
| wcięcia czterema spacjami; tabulatory tylko w kodzie już nimi wciętym | `    return x` | mieszane wcięcia |
| odstęp wokół operatorów i po przecinku, bez odstępu wewnątrz nawiasów | `suma = a + b`, `f(x, y)` | `suma=a+b`, `f( x,y )` |
| długość wiersza: 79 znaków według PEP 8; 88 w domyślnej konfiguracji Ruff i black | wiersz łamany w nawiasie | wiersz przewijany poziomo |
| importy na początku pliku, w trzech grupach: biblioteka standardowa, pakiety zewnętrzne, własne moduły — każda osobno | `import os`, pusty wiersz, `import numpy as np` | `import os, sys` |
| dwa puste wiersze między definicjami na poziomie modułu, jeden między metodami | — | definicje sklejone |
| porównanie z `None` przez `is`, pustość kolekcji przez jej wartość logiczną | `if x is None`, `if not lista` | `if x == None`, `if len(lista) == 0` |

W rozdziale [1. Instalacja i środowisko pracy](../01-instalacja/konfiguracja.md#pep-8-i-formatowanie-kodu) konfigurowaliśmy w VSC rozszerzenia pylint i autopep8; w tym podrozdziale poznajemy Ruff, który obie role — wykrywanie usterek i formatowanie — łączy w jednym narzędziu.

## Dokumenty PEP

Dokumenty **PEP**, wprowadzone w rozdziale [1. Instalacja i środowisko pracy](../01-instalacja/konfiguracja.md#pep-8-i-formatowanie-kodu), opisują propozycje zmian w języku, bibliotece lub procesie; numer PEP jest w społeczności skrótem nazwy. Kilka, których tematy pojawiły się w książce:

| PEP | Temat | Rozdział |
|---|---|---|
| 8 | przewodnik stylu | 1, 16 |
| 20 | Zen Pythona | 2, 16 |
| 257 | konwencje docstringów | 1, 6 |
| 484 | adnotacje typów | 3, 6, 16 |
| 572 | operator przypisania `:=` | 3 |
| 634 | dopasowanie wzorców `match` | 4, 12 |
| 649 i 749 | leniwe obliczanie adnotacji (3.14) | 6, 16 |
| 703 i 779 | kompilacja free-threaded (3.13, 3.14) | 1, 15 |
| 750 | szablony łańcuchów, t-stringi (3.14) | 9 |
| 810 | jawne leniwe importy (3.15) | 16 |

## Ruff — linter i formater

**Linter** (ang. *linter*) wykrywa usterki bez uruchamiania kodu: nieużywane importy, niezdefiniowane nazwy, przestarzałe konstrukcje, odstępstwa od PEP 8. **Formater** (ang. *formatter*) przepisuje kod do jednolitego układu. **Ruff** łączy obie funkcje; jest napisany w języku Rust i sprawdza duży projekt w ułamku sekundy; zastępuje starsze narzędzia flake8, isort i black. Instalujemy go jak każdy pakiet:

```powershell title="Terminal"
python -m pip install ruff
```

Zanim uruchomimy Ruff, zapisujemy konfigurację w `pyproject.toml`. Bez niej Ruff od wersji 0.16 włącza obszerny domyślny zestaw ponad czterystu reguł z kilkudziesięciu rodzin (między innymi `F`, `I`, `UP`, `B`), ale nie wszystkie reguły `E` — na przykład `E401` z poniższego raportu domyślnie nie jest zgłaszane; jawne `select` ustala zestaw niezależnie od zmian domyślnych między wydaniami:

```toml title="pyproject.toml"
[tool.ruff]
line-length = 88
target-version = "py314"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

Rodzina `B` (flake8-bugbear) wykrywa prawdopodobne błędy, jak modyfikowalna wartość domyślna parametru z rozdziału 6; `target-version` mówi Ruffowi, jakiej składni może używać w poprawkach. Plik poniżej świadomie łamie reguły:

```python title="brzydki.py"
import sys, os
from typing import List
def suma( liczby:List[int] )->int:
    wynik=0
    for x in liczby:
        wynik+=x
    return wynik
print( suma([1,2,3]) )
```

```powershell title="Terminal"
python -m ruff check brzydki.py --output-format concise
```

```{ .text .no-copy }
brzydki.py:1:1: E401 [*] Multiple imports on one line
brzydki.py:1:1: I001 [*] Import block is un-sorted or un-formatted
brzydki.py:1:8: F401 [*] `sys` imported but unused
brzydki.py:1:13: F401 [*] `os` imported but unused
brzydki.py:2:1: UP035 `typing.List` is deprecated, use `list` instead
brzydki.py:3:18: UP006 [*] Use `list` instead of `List` for type annotation
Found 6 errors.
[*] 5 fixable with the `--fix` option.
```

Każda uwaga ma kod reguły — litera oznacza rodzinę, na przykład `E` to błędy stylu z PEP 8, `F` — usterki logiczne wykrywane przez pyflakes, `I` — porządek importów, `UP` — konstrukcje do unowocześnienia — a gwiazdka w nawiasie oznacza, że Ruff potrafi ją naprawić sam. Domyślny raport pokazuje dodatkowo fragment kodu z zaznaczonym miejscem; opcja `--output-format concise` skraca go do jednego wiersza na uwagę. Naprawa i formatowanie to dwa polecenia:

```powershell title="Terminal"
python -m ruff check --fix brzydki.py
python -m ruff format brzydki.py
```

```{ .text .no-copy }
Found 5 errors (5 fixed, 0 remaining).
1 file reformatted
```

```{ .python .no-copy }
def suma(liczby: list[int]) -> int:
    wynik = 0
    for x in liczby:
        wynik += x
    return wynik


print(suma([1, 2, 3]))
```

Nieużywane importy zniknęły — wraz z nimi przestarzały `typing.List`, zastąpiony przez `list` — a formater ustawił odstępy i puste wiersze (w plikach z łańcuchami ujednolica też cudzysłowy na podwójne). Raport po `--fix` wymienia pięć uwag zamiast sześciu: gdy `UP006` zamienił `List` na `list`, import z `typing` stał się nieużywany i został usunięty jako `F401`, więc uwaga `UP035` — jedyna bez gwiazdki — straciła przedmiot. Uwagi, których Ruff nie naprawia sam, pozostają w raporcie: zmiana zachowania kodu wymaga decyzji programisty. Polecenia `python -m ruff check .` i `python -m ruff format .` sprawdzają cały projekt, a `python -m ruff format --check .` tylko raportuje pliki do sformatowania, nie zmieniając ich — w tej postaci trafią do automatyzacji w następnym podrozdziale.

## Alternatywy

**black** to formater, który spopularyzował zasadę „jeden styl bez konfiguracji”; Ruff format naśladuje jego wynik — na kodzie sformatowanym przez black ponad 99,9% wierszy pozostaje bez zmian — więc przejście na Ruff wymaga co najwyżej drobnych poprawek; obu narzędzi nie należy jednak stosować naprzemiennie w jednym projekcie. **autopep8** i **pylint** z rozdziału 1 działają nadal jako rozszerzenia VSC — pylint zgłasza więcej uwag, lecz działa wolniej; Ruff pokrywa większość z nich. **flake8** i **isort** to starsze narzędzia, które Ruff zastępuje w całości. W nowym projekcie wystarcza Ruff; w istniejącym warto zachować narzędzie, które zespół już zna.
