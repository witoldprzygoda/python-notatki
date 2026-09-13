# Rozdział 13. Wydajność i optymalizacja — plan implementacyjny

Skondensowany projekt stron rozdziału 13 według `PLAN_ROZWOJU.md` (sekcja 4, „13. Wydajność i optymalizacja”) i `DEVELOPMENT_WORKFLOW.md`. Branch: `content/13-wydajnosc` (z `dev` po integracji rozdziału 12, commit `1b3e9b9`). Stan odniesienia: Python 3.14.7 w `.venv` projektu (Windows), MkDocs Material. Rozdział realizowany autonomicznie na polecenie autora z 14 IX 2026.

## Decyzje redakcyjne (14 IX 2026)

1. **Struktura:** index + 3 podrozdziały: pomiar czasu i profilowanie → optymalizacja kodu → drogi przyspieszania. Etykieta i H1 ostatniej strony „Drogi przyspieszania” bez dopisku „(dla dociekliwych)”; charakter uzupełniający zaznaczony w pierwszym akapicie i w `index.md`.
2. **Wszystkie liczby z uruchomienia na 3.14.7 na komputerze autora**, z zastrzeżeniem prozą, że zależą od komputera; w harnessie czasy i rozmiary maskowane (`--mask=\d+\.\d+`, `--mask=\d+ B`), a bloki wyników zawierają wartości z jednego przebiegu. Liczby z wykładów (fib, 150 ms/2 ms, 48 B/40 B) zastąpione własnymi pomiarami.
3. **Dekorator mierzący czas** — w rozdziale 6 celowo pominięty (decyzja autora), tu napisany z `functools.wraps` z rozdziału 7 jako pierwszy przykład; stoper klasowy i `@contextmanager` z rozdziałów 8 i 11 przywołane odsyłaczami.
4. **Narzędzia biblioteki standardowej w kodzie:** `time.perf_counter()`, `timeit` (moduł: `timeit()`, `repeat()`; wiersz poleceń `python -m timeit`), `cProfile` z `pstats` (`Stats`, `sort_stats("cumulative")`, `print_stats(n)`; `python -m cProfile -s cumulative`), `tracemalloc` (`start()`, `get_traced_memory()`, `stop()`), `sys.getsizeof()`, `dis.dis()`, `functools.cache`, `collections.deque`. Narzędzia zewnętrzne (`snakeviz`) i biblioteki (NumPy, Numba, Cython, mypyc, PyPy) wyłącznie prozą lub jako bloki `.python .no-copy` — nie są instalowane w `.venv` projektu; wersje zweryfikowane w PyPI 14 IX 2026: Numba 0.67.0 (3.10–3.14), Cython 3.3.0 (3.9–3.14), mypy 2.3.1 z mypyc (3.14), PyPy 7.3.23 (implementuje 3.11 — bez 3.14).
5. **Pomiar `__slots__`:** `sys.getsizeof()` instancji daje 48 B w obu wersjach (słownik instancji tworzony leniwie, nie wliczany), więc pomiar przez `tracemalloc` na 100 000 obiektów: ok. 128 B a 88 B na obiekt (3.14.7, 64-bit); `slots=True` w klasach danych z rozdziału 12 jako ten sam mechanizm.
6. **`dis`:** porównanie `co_code` lambdy i `def` (równe) oraz listing 3.14 z `RESUME`, `LOAD_FAST_BORROW_LOAD_FAST_BORROW`, `BINARY_OP`, `LOAD_SMALL_INT`; wykład 4 i notatki s. 65 pokazują `BINARY_FLOOR_DIVIDE` z dawnych wersji — korekta prozą, bez tekstu z 3.14 jako „prawdy ostatecznej” (kod bajtowy zmienia się co wersję).
7. **Zasady optymalizacji** z wykładu 12 sl. 22 jako lista; złożoność obliczeniowa wprowadzona jawnie, w zakresie potrzebnym do porównania `in` na liście i zbiorze oraz `pop(0)` i `deque` (rozdziały 5 i 7 już to sygnalizowały).
8. **Drogi przyspieszania:** wektoryzacja NumPy z pomiarem w tymczasowym środowisku (kod i pełne omówienie → rozdział 14, tu wynik i idea), Numba `@njit` (kod jako `.python .no-copy` z wynikiem z pomiaru, jeśli instalacja w tymczasowym środowisku się powiedzie; inaczej tylko prozą), Cython i mypyc (adnotacje jako źródło przyspieszenia — jedno zdanie o kompilacji do rozszerzenia), PyPy (brak 3.14), wiele rdzeni — `3.14t` i procesy (zapowiedź rozdziału o współbieżności), Python 3.15 — pakiet `profiling` (PEP 799: `profiling.tracing` = `cProfile`, `profiling.sampling`; `profile` przestarzały).
9. **Nazwy i przykłady:** `fib()` i `fib_iter()` z rozdziału 6, `zbior`/`lista`, `Punkt` z `__slots__` i bez, `deque` z rozdziału 7; bez not o laboratorium (lab6 to źródło zapowiedzi, nie treści).
10. **Szacunek rozmiaru** z `PLAN_ROZWOJU.md` (450–520 linii) orientacyjny; spodziewane ok. 700–850 linii.
11. **Zapowiedzi w przód** prozą z `TODO` i wpisem w `PLAN_ROZWOJU.md` (sekcje 14, 15, 16); rejestrowane przy commicie planu.

## Zasady obowiązujące w całym rozdziale

- Żaden przykład wykonywany przez harness nie importuje bibliotek spoza biblioteki standardowej; bloki z NumPy/Numba jako `.python .no-copy`.
- Kolejność: strona 1 (narzędzia pomiaru) → strona 2 (co mierzyć i jak poprawiać) → strona 3 (poza czysty Python). Strona 3 uzupełniająca.
- Pojęcia wprowadzane jawnie: „mikropomiar (ang. *micro-benchmark*)”, „profilowanie (ang. *profiling*)”, „profiler”, „wąskie gardło (ang. *bottleneck*)”, „złożoność obliczeniowa (ang. *computational complexity*)” z notacją `O(1)`, `O(n)`, `O(n log n)`, `O(n²)`, „mikrooptymalizacja”, „memoizacja” (rozdział 6), „wektoryzacja (ang. *vectorization*)”, „kompilacja w locie (ang. *just-in-time*, JIT)”, „kod bajtowy (ang. *bytecode*)” — rozdział 7 wspominał `__pycache__`.
- Konwencje `CLAUDE.md`; nagłówki rzeczownikowe; cudzysłowy „…”; `powershell title="Terminal"` dla `python -m timeit` i `python -m cProfile`; nazwy plików bez kolizji (nie: `timeit.py`, `profile.py`, `dis.py`, `time.py`, `tracemalloc.py`).
- Weryfikacja: `scripts/verify_page.py` z maskami; polecenia terminalowe ręcznie; oba buildy; trzy recenzje; commit; domknięcie; status; integracja do `dev` i push.

## Strony

### 1. `pomiar-i-profilowanie.md` — Pomiar czasu i profilowanie

**Kolejność H2/H3.** 1. Zasada: najpierw pomiar (dlaczego intuicja zawodzi; „mierz, nie zgaduj”); 2. `time.perf_counter()` i dekorator mierzący czas (`@mierz_czas` z `functools.wraps`; stoper z rozdziałów 8 i 11 — odsyłacze; `fib(30)` a `fib_iter(30)`); 3. Moduł `timeit` — mikropomiary (`timeit.timeit(stmt, setup, number, globals)`, `repeat()` i minimum, `python -m timeit`; pułapki: `number`, kod w łańcuchu, brak `print` w mierzonym kodzie); 4. Profilowanie — `cProfile` i `pstats` (`cProfile.run()`, `Profile()` z `enable()`/`disable()`, `pstats.Stats().sort_stats("cumulative").print_stats(5)`; kolumny `ncalls`, `tottime`, `percall`, `cumtime`; `python -m cProfile -s cumulative skrypt.py`, `-o plik.prof`; `snakeviz` prozą); 5. Pomiar pamięci — `sys.getsizeof()` i `tracemalloc` (co wlicza `getsizeof`, `get_traced_memory()`, `take_snapshot()` jednym zdaniem); 6. Fibonacci pod lupą (tabela: rekurencja, iteracja, `functools.cache` z rozdziału 7 — czasy i liczba wywołań z `cProfile`).

**Główne przykłady.** `mierz-czas.py` (dekorator, `fib`/`fib_iter`), `timeit-demo.py`, `timeit-repeat.py`, `profil-fib.py` (`cProfile` + `pstats`), `pamiec.py` (`getsizeof`, `tracemalloc`), `fibonacci-porownanie.py`.

**Wymagane zachowania (3.14.7).** `fib(30)` ok. 0,08 s, `fib_iter(30)` poniżej 1 ms, `functools.cache` — `CacheInfo(hits=28, misses=31, ...)`; `cProfile` dla `fib(22)`: `57314 function calls (2 primitive calls)`, wiersz `57313/1` (wywołania rekurencyjne); `getsizeof(0)` = 28 (rozdział 3).

**Źródła.** `Wyklad_12.txt` sl. 20–21; `08-wyjatki/with-i-contextlib.md` (stoper), `11-model-danych/menedzery-kontekstu.md`, `06-funkcje/rekurencja.md` (`fib`, `fib_iter`), `07-moduly/functools.md` (`cache`); docs: `time.perf_counter`, `timeit`, *The Python Profilers*, `tracemalloc`, `sys.getsizeof`.

**Domyka.** `08 with-i-contextlib.md:159` (`TODO`).

**Rozmiar.** ok. 300–340 linii.

### 2. `optymalizacja-kodu.md` — Optymalizacja kodu

**Kolejność H2/H3.** 1. Zasady optymalizacji (lista z wykładu 12: działający kod → pomiar → wąskie gardło → pomiar po → algorytm przed mikrooptymalizacją → wbudowane → generatory → biblioteki numeryczne → bez przedwczesnej optymalizacji); 2. Złożoność obliczeniowa i wybór struktury danych (notacja `O`; `in` na liście `O(n)` a na zbiorze `O(1)` z pomiarem; `pop(0)` a `deque.popleft()`; słownik jako indeks); 3. Idiomy szybkiego kodu (`str.join()` a konkatenacja w pętli; złożenie listowe a pętla z `append()`; generator a lista przy dużych danych; funkcje wbudowane `sum()`, `max()`, `sorted()` zamiast pętli; `map()` a wyrażenie generatorowe; nazwy lokalne — krótko); 4. Memoizacja (odsyłacze do rozdziałów 6 i 7; kiedy działa — funkcje czyste, argumenty haszowalne); 5. Pamięć — `__slots__` z pomiarem (`getsizeof` 48 B w obu przypadkach — dlaczego; `tracemalloc` na 100 000 obiektów; szybkość dostępu z `timeit`; `slots=True` w klasach danych — rozdział 12); 6. Kod bajtowy — moduł `dis` (dla dociekliwych) (`co_code` lambdy i `def` równe; listing `dis.dis()` na 3.14 z objaśnieniem instrukcji; kod bajtowy zmienia się między wersjami — wykład 4 i notatki pokazują `BINARY_FLOOR_DIVIDE` z dawnych wersji; specjalizacja od 3.11 jednym zdaniem).

**Główne przykłady.** `zbior-a-lista.py`, `deque-a-lista.py`, `idiomy.py` (join, złożenie, generator), `memoizacja-pomiar.py`, `slots-pamiec.py`, `dis-demo.py`.

**Wymagane zachowania (3.14.7).** `in` lista 100 000: ok. 0,5 ms na sprawdzenie a zbiór ok. 20 ns; `pop(0)` × 50 000 ok. 0,39 s a `popleft()` ok. 0,001 s; konkatenacja 10 000 słów ok. 0,6 ms a `join` ok. 0,03 ms; `co_code` równe; `dis` z `RESUME`, `LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (a, b)`, `BINARY_OP 2 (//)`, `RETURN_VALUE`.

**Źródła.** `Wyklad_12.txt` sl. 22; `Wyklad_03.txt` sl. 9, 38; `Wyklad_06.txt` sl. 19; `Wyklad_07.txt` sl. 40; `Wyklad_04.txt` sl. 46; `PythonNotatki.txt` 2405–2440 (s. 64–65); `05-typy-zlozone/lista.md#kolejka-i-stos`, `zbiory.md`, `07-moduly/biblioteka-standardowa.md#kolejka-dwustronna-deque`, `10-klasy/atrybuty-i-metody.md#atrybut-__slots__`, `12-oop-zaawansowane/klasy-danych.md`; docs: *Time Complexity* (wiki), `dis`, `collections.deque`.

**Domyka.** `10 atrybuty-i-metody.md:260` (`TODO`); zdania bez `TODO` w 11 (`total_ordering`, deskryptory) i 12 (`slots=True`, `Protocol`) — jednym akapitem w sekcji 5 i 1.

**Rozmiar.** ok. 300–340 linii.

### 3. `przyspieszanie-pythona.md` — Drogi przyspieszania

**Kolejność H2/H3.** 1. Skąd bierze się koszt interpretacji (dynamiczne typy, obiekty, pętla interpretera — krótko); 2. Wektoryzacja — NumPy (suma kwadratów: pętla a `np.sum(tablica**2)` — wynik pomiaru z tymczasowego środowiska, kod jako `.python .no-copy`, pełne omówienie → rozdział 14); 3. Kompilacja w locie — Numba (`@njit` na czystej pętli, pierwsze wywołanie kompiluje; ograniczenia; wynik pomiaru, jeśli dostępny); 4. Kompilacja do rozszerzeń — Cython i mypyc (adnotacje typów jako źródło przyspieszenia; `mypyc` w pakiecie `mypy`; jedno zdanie o `.pyd`/`.so`); 5. Inny interpreter — PyPy (JIT dla całego programu; 7.3.23 implementuje 3.11); 6. Wiele rdzeni — `3.14t` i procesy (GIL z rozdziału 1; `sys._is_gil_enabled()`; zapowiedź rozdziału o współbieżności); 7. Python 3.15 — pakiet `profiling` (PEP 799: `profiling.tracing` = dotychczasowy `cProfile`, `profiling.sampling` — profiler próbkujący; `profile` przestarzały).

**Główne przykłady.** `gil.py` (`sys._is_gil_enabled()`, `sys.version`), bloki `.python .no-copy`: `numpy-suma.py`, `numba-suma.py`, `cython-suma.pyx`.

**Źródła.** `Wyklad_09.txt` sl. 11–12, 35; `lab6.txt` sl. 1 (zapowiedź); `01-instalacja/instalacja.md` (3.14t); PyPI (Numba 0.67.0, Cython 3.3.0, mypy 2.3.1), pypy.org (7.3.23), PEP 799.

**Rozmiar.** ok. 180–220 linii.

### 4. `index.md` — Wprowadzenie

Wstęp: „najpierw działa, potem mierz”; co rozdział domyka (stoper z 8, `__slots__` z 10, zapowiedzi z 11–12); trzy podrozdziały; strona 3 uzupełniająca; zapowiedź NumPy (14) i współbieżności (15). `---`, `## W tym rozdziale`.

## Nawigacja

```yaml
  - 13. Wydajność i optymalizacja:
      - Wprowadzenie: 13-wydajnosc/index.md
      - Pomiar czasu i profilowanie: 13-wydajnosc/pomiar-i-profilowanie.md
      - Optymalizacja kodu: 13-wydajnosc/optymalizacja-kodu.md
      - Drogi przyspieszania: 13-wydajnosc/przyspieszanie-pythona.md
```

Pozycja w `docs/index.md`: „13. [Wydajność i optymalizacja](13-wydajnosc/index.md) — pomiar czasu i profilowanie, optymalizacja kodu, drogi przyspieszania”.

## Zapowiedzi w przód (do zarejestrowania w `PLAN_ROZWOJU.md`)

- Rozdział 14: wektoryzacja i kod NumPy (strona 3), pliki `.npy` — nie; benchmark pętla a NumPy (strona 3).
- Rozdział 15: `3.14t`, procesy i wątki (strona 3); `timeit` dla kodu współbieżnego — nie.
- Rozdział 16: `mypy` i adnotacje jako wejście dla mypyc (strona 3); profil w CI — nie.

## Zmiany w rozdziałach 1–12 (zbiorczo po ukończeniu rozdziału 13)

| Plik:linia | Zmiana |
|---|---|
| `08-wyjatki/with-i-contextlib.md:159` | `TODO` (pomiary czasu) → odsyłacz do `pomiar-i-profilowanie.md` |
| `10-klasy/atrybuty-i-metody.md:260` | `TODO` (pomiar pamięci `__slots__`) → odsyłacz do `optymalizacja-kodu.md#pamiec-__slots__-z-pomiarem` |
| `docs/index.md`, `mkdocs.yml` | pozycja „13. …” |

## CONTENT HANDOFF (rozbieżności ze źródłami)

(a) W04 sl. 46 i notatki s. 65: listing `dis` z `BINARY_FLOOR_DIVIDE` pochodzi z Pythona ≤ 3.10; w 3.14 `RESUME`, `LOAD_FAST_BORROW_LOAD_FAST_BORROW`, `BINARY_OP 2 (//)`; teza „identyczny bytecode” pozostaje prawdziwa (`co_code` równe); (b) W07 sl. 40: `sys.getsizeof()` instancji (~152 B a ~56 B) — w 3.14 `getsizeof` daje 48 B w obu przypadkach, bo nie wlicza leniwie tworzonego `__dict__`; różnicę pokazuje `tracemalloc` (ok. 128 B a 88 B na obiekt); (c) W09 sl. 11–12: czasy orientacyjne — w książce własne pomiary; (d) W12 sl. 21: `pip install snakeviz` → `python -m pip install snakeviz`; (e) W03 sl. 9: „comprehension szybsze ~20–30%” — w 3.14 różnica mniejsza (pomiar), zysk głównie w czytelności; (f) lab6 sl. 1: „biblioteki wynikowej (.so)” — na Windows `.pyd`.

## Checklisty

Jak w rozdziałach 10–12: harness z maskami, brak importów spoza biblioteki standardowej w blokach wykonywanych, kolejność pojęć, konwencje, oba buildy, kotwice, trzy recenzje, domknięcie tabeli, status z liczbą linii, integracja do `dev`.
