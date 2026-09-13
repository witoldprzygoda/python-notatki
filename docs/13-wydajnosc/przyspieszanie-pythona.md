# Drogi przyspieszania

Ten podrozdział ma charakter uzupełniający — przegląda drogi, którymi programy w Pythonie wychodzą poza możliwości interpretera, gdy algorytm i struktury danych są już właściwe. Żadnego z tych narzędzi nie instalujemy w środowisku kursu; kod pokazujemy poglądowo, a wyniki pomiarów pochodzą z osobnego środowiska z Pythonem 3.14.7, w którym zainstalowano NumPy 2.5.3 i Numba 0.67.0 (stan na wrzesień 2026).

## Skąd bierze się koszt interpretacji

Pętla `for x in dane: suma += x * x` w CPythonie wykonuje dla każdego elementu kilka instrukcji kodu bajtowego z poprzedniego podrozdziału (na Pythonie 3.14 — osiem), a każda z nich pracuje na obiektach: sprawdza typ `x`, wywołuje `int.__mul__`, tworzy nowy obiekt wyniku, aktualizuje liczniki referencji. Kod w C wykonałby tę samą pętlę kilkoma instrukcjami maszynowymi na element, na liczbach w ciągłym bloku pamięci, bez obiektów i sprawdzania typów. Wszystkie drogi przyspieszania sprowadzają się do usunięcia tej różnicy: albo przenoszą pętlę do kodu skompilowanego, albo kompilują sam kod Pythona, albo uruchamiają kilka pętli naraz.

## Wektoryzacja — NumPy

**Wektoryzacja** (ang. *vectorization*) zastępuje pętlę po elementach jedną operacją na całej tablicy. Biblioteka NumPy przechowuje liczby w tablicy o jednym typie i ciągłej pamięci, a operacje wykonuje w skompilowanym kodzie:

```{ .python .no-copy }
import numpy as np

n = 1_000_000
dane = list(range(n))
tablica = np.arange(n, dtype=np.int64)

suma = 0
for x in dane:          # czysty Python: ok. 34 ms
    suma += x * x

suma = sum(x * x for x in dane)      # sum() z generatorem: ok. 41 ms
suma = int(np.sum(tablica * tablica))  # NumPy: ok. 2,4 ms
```

Wersja NumPy jest kilkanaście razy szybsza od pętli, choć `tablica * tablica` tworzy pośrednią tablicę miliona kwadratów — obie operacje przebiegają w C, bez obiektów Pythona dla poszczególnych liczb. Wersja z `sum()` i wyrażeniem generatorowym nie jest szybsza od pętli: wyrażenie `x * x` nadal wykonuje interpreter, a wznawianie generatora dokłada własny koszt — zysk z funkcji wbudowanych z poprzedniego podrozdziału dotyczy przypadków, w których cała iteracja przebiega w C, jak `sum(range(...))`. Kosztem wektoryzacji jest inny sposób zapisu obliczeń: zamiast „dla każdego elementu” piszemy „dla całej tablicy”, a kod, którego nie da się tak zapisać, wraca do pętli. Bibliotekę tę omawiamy w rozdziale [14. NumPy i Matplotlib](../14-numpy-matplotlib/index.md), a kod i pomiar w środowisku kursu — w podrozdziale [Operacje na tablicach](../14-numpy-matplotlib/operacje.md#wektoryzacja-pomiar).

## Kompilacja w locie — Numba

Biblioteka Numba kompiluje wybrane funkcje Pythona do kodu maszynowego przy pierwszym wywołaniu — **w locie** (ang. *just-in-time*, JIT) — na podstawie typów przekazanych argumentów. Funkcja pozostaje zwykłą pętlą w Pythonie, a przyspieszenie przynosi dekorator:

```{ .python .no-copy }
import numpy as np
from numba import njit


@njit
def suma_kwadratow(tablica):
    wynik = 0
    for x in tablica:
        wynik += x * x
    return wynik


tablica = np.arange(1_000_000, dtype=np.int64)
suma_kwadratow(tablica)   # pierwsze wywołanie: kompilacja, ok. 230 ms
suma_kwadratow(tablica)   # kolejne wywołania: ok. 0,5 ms
```

Pierwsze wywołanie trwa dłużej niż pętla w Pythonie, bo obejmuje kompilację; każde następne jest kilkadziesiąt razy szybsze od pętli i szybsze od wersji NumPy, bo nie tworzy tablicy pośredniej. Numba obsługuje podzbiór języka — liczby, tablice NumPy, pętle, proste krotki — a kod korzystający z dowolnych obiektów Pythona — zwykłych słowników przekazanych z zewnątrz, własnych klas, bibliotek spoza NumPy — nie skompiluje się w trybie `nopython` (bez obiektów Pythona), który daje pełne przyspieszenie. Narzędzie wybieramy wtedy, gdy wąskim gardłem jest pętla numeryczna, której nie da się zwektoryzować.

## Kompilacja do rozszerzeń — Cython i mypyc

Dwa narzędzia kompilują kod Pythona przed uruchomieniem, do modułu rozszerzenia (plik `.pyd` na Windows, `.so` na innych systemach), który importuje się jak zwykły moduł. **Cython** przyjmuje kod Pythona, w którym typy zmiennych można zadeklarować jego własną składnią w pliku `.pyx` albo — w zwykłym pliku `.py` — adnotacjami w zapisie z rozdziału 3, ale z typami C z modułu `cython` (na przykład `n: cython.longlong`); gołej adnotacji `int` Cython celowo nie zamienia na typ C. Zysk zależy od tego, ile typów zadeklarowano, a ceną jest ograniczony zakres typów C:

```{ .python .no-copy }
# suma.pyx — kompilowany przez Cython do modułu rozszerzenia
def suma_kwadratow(long long n):
    cdef long long wynik = 0
    cdef long long x
    for x in range(n):
        wynik += x * x
    return wynik
```

**mypyc**, dostarczany razem z narzędziem `mypy`, kompiluje zwykłe pliki `.py` z adnotacjami typów — te same adnotacje, które sprawdza analiza statyczna, stają się informacją dla kompilatora. Oba narzędzia wymagają kompilatora C zainstalowanego w systemie i osobnego kroku budowania, więc stosuje się je w bibliotekach i większych projektach, nie w skryptach. Adnotacje typów i `mypy` omawiamy w podrozdziale [Adnotacje typów w praktyce](../16-warsztat/typy-statyczne.md#sprawdzacz-typow-mypy) rozdziału 16.

## Inny interpreter — PyPy

PyPy to osobna implementacja Pythona z wbudowanym kompilatorem JIT, który przyspiesza cały program bez zmian w kodzie — typowo kilkakrotnie dla kodu z pętlami w czystym Pythonie. Ograniczenia: PyPy implementuje starszą wersję języka (wydanie 7.3.23 odpowiada Pythonowi 3.11, bez mechanizmów z 3.12–3.14 opisanych w tej książce), a rozszerzenia w C, w tym część bibliotek numerycznych, działają w nim wolniej albo wcale. Dla programów naukowych właściwą drogą pozostaje NumPy; PyPy sprawdza się w długo działających programach operujących na obiektach Pythona.

## Wiele rdzeni — `3.14t` i procesy

Wszystkie dotychczasowe drogi przyspieszają jeden wątek. W rozdziale 1 wspomnieliśmy o globalnej blokadzie interpretera GIL, przez którą w standardowym CPythonie kod Pythona wykonuje w danej chwili tylko jeden wątek, niezależnie od liczby rdzeni, oraz o wariancie `3.14t` bez tej blokady:

```python title="gil.py"
import sys

print(sys.version)
print("GIL włączony:", sys._is_gil_enabled())
```

```{ .text .no-copy }
3.14.7 (tags/v3.14.7:823f032, Aug  5 2026, 10:51:32) [MSC v.1944 64 bit (AMD64)]
GIL włączony: True
```

```powershell title="Terminal"
py -V:3.14t gil.py
```

```{ .text .no-copy }
3.14.7 free-threading build (tags/v3.14.7:823f032, Aug  5 2026, 10:52:03) [MSC v.1944 64 bit (AMD64)]
GIL włączony: False
```

W wariancie free-threaded wątki mogą wykonywać kod Pythona równolegle na wielu rdzeniach; w standardowym interpreterze równoległość dają osobne procesy. Wątki w wariancie free-threaded, procesy, a także wątki w standardowym interpreterze dla zadań czekających na wejście i wyjście — wszystkie te drogi omawiamy w rozdziale [15. Współbieżność — wątki, procesy i GIL](../15-wspolbieznosc/index.md), a pomiary — w podrozdziale [Studia wydajności i asyncio](../15-wspolbieznosc/studia-wydajnosci.md#zadania-ograniczone-procesorem).

## Python 3.15 — pakiet `profiling`

Narzędzia z pierwszego podrozdziału czeka porządkowanie. Dokument [PEP 799](https://peps.python.org/pep-0799/) wprowadza w Pythonie 3.15 pakiet `profiling`: `profiling.tracing` to dotychczasowy `cProfile` (nazwa `cProfile` pozostaje dostępna), a `profiling.sampling` — nowy **profiler próbkujący** (ang. *sampling profiler*), który zamiast rejestrować każde wywołanie funkcji, w regularnych odstępach sprawdza, co program właśnie wykonuje. Profiler próbkujący nie spowalnia mierzonego programu i nadaje się do obserwowania działających procesów; jego wyniki są statystyczne, więc krótkie funkcje mogą w nich nie wystąpić. Przestarzały moduł `profile` — czysto pythonowy poprzednik `cProfile` — ma zniknąć w Pythonie 3.17. Zasada z początku rozdziału nie zmienia się: niezależnie od narzędzia najpierw mierzymy, a dopiero potem poprawiamy.
