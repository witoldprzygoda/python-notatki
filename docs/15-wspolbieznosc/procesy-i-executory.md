# Procesy i pule wykonawców

Gdy zadanie liczy, a nie czeka, wątki standardowej kompilacji nie skracają czasu. Równoległość dają osobne procesy — każdy z własnym interpreterem i własną blokadą — a od Pythona 3.14 także osobne interpretery w jednym procesie. Wspólnym interfejsem do wątków, procesów i interpreterów jest moduł `concurrent.futures`, który poznajemy w tym podrozdziale.

## Procesy zamiast wątków — `multiprocessing.Pool`

Moduł `multiprocessing` uruchamia dodatkowe procesy interpretera i rozdziela między nie pracę. Klasa `Pool` tworzy **pulę** (ang. *pool*) procesów, a jej metoda `map()` działa jak wbudowane `map()` z rozdziału 6, ale wywołania wykonują procesy potomne:

```python title="procesy.py"
import multiprocessing
import time

N = 50_000_000


def odliczaj(n):
    while n > 0:
        n -= 1
    return n


if __name__ == "__main__":
    start = time.perf_counter()
    odliczaj(N)
    print(f"1 proces:  {time.perf_counter() - start:.2f} s")

    start = time.perf_counter()
    with multiprocessing.Pool(processes=2) as pula:
        wyniki = pula.map(odliczaj, [N // 2, N // 2])
    print(f"2 procesy: {time.perf_counter() - start:.2f} s, wyniki {wyniki}")
    print("metoda startu:", multiprocessing.get_start_method())
```

```{ .text .no-copy }
1 proces:  1.09 s
2 procesy: 0.73 s, wyniki [0, 0]
metoda startu: spawn
```

To samo odliczanie, które w dwóch wątkach nie przyspieszyło, w dwóch procesach trwa wyraźnie krócej — choć nie dwa razy, bo uruchomienie procesów kosztuje. Metoda startu `spawn`, domyślna na Windows i macOS, uruchamia nowy interpreter, który **importuje moduł główny**, aby poznać definicję funkcji `odliczaj`; dlatego kod uruchamiający pulę musi być objęty strażnikiem `if __name__ == "__main__":` z sekcji [Warunek `if __name__ == "__main__"`](../07-moduly/skrypt-jako-program.md#warunek-if-__name__-__main__) rozdziału 7 — bez niego każdy proces potomny próbowałby utworzyć własną pulę i kończyłby się błędem `RuntimeError` z podpowiedzią o brakującym strażniku, a program główny nie zakończyłby się wcale — pula bez końca uruchamiałaby kolejne procesy robocze (z `ProcessPoolExecutor` program kończy się wyjątkiem `BrokenProcessPool`). Na innych systemach uniksowych od Pythona 3.14 domyślną metodą jest `forkserver`; wcześniejsze `fork` kopiowało pamięć procesu bez jego pozostałych wątków, więc blokada zajęta w chwili kopiowania przez inny wątek pozostawała w procesie potomnym zajęta na zawsze — stąd zakleszczenia. Funkcja i jej argumenty wędrują do procesu potomnego w postaci serializowanej modułem `pickle` z rozdziału 9, a wynik wraca tą samą drogą; stąd dwa ograniczenia: funkcja musi być zdefiniowana na poziomie modułu (nie `lambda`, nie funkcja zagnieżdżona), a argumenty i wyniki muszą dać się serializować. Metoda `apply_async()` zleca pojedyncze wywołanie i zwraca obiekt, z którego wynik odbieramy metodą `get()`.

## Wspólny interfejs — `concurrent.futures`

Moduł `concurrent.futures` udostępnia **pule wykonawców** (ang. *executors*) o jednakowym interfejsie: `ThreadPoolExecutor` dla wątków, `ProcessPoolExecutor` dla procesów i — od 3.14 — `InterpreterPoolExecutor` dla interpreterów. Metoda `submit()` zleca wywołanie i natychmiast zwraca obiekt `Future` — obietnicę wyniku, który dopiero powstanie:

```python title="futures.py"
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def kwadrat(x):
    time.sleep(0.3 - 0.1 * x)
    return x * x


with ThreadPoolExecutor(max_workers=3) as pula:
    zadania = [pula.submit(kwadrat, x) for x in range(3)]
    print("w kolejności ukończenia:", [zadanie.result() for zadanie in as_completed(zadania)])
    print("w kolejności zlecenia:  ", list(pula.map(kwadrat, range(3))))

    zadanie = pula.submit(kwadrat, "a")
    print("wyjątek z zadania:", repr(zadanie.exception()))
    try:
        zadanie.result()
    except TypeError as e:
        print("result() zgłasza go ponownie:", e)
```

```{ .text .no-copy }
w kolejności ukończenia: [4, 1, 0]
w kolejności zlecenia:   [0, 1, 4]
wyjątek z zadania: TypeError("can't multiply sequence by non-int of type 'float'")
result() zgłasza go ponownie: can't multiply sequence by non-int of type 'float'
```

`Future.result()` czeka na wynik i go zwraca; jeśli zadanie zgłosiło wyjątek — tu już przy obliczaniu czasu oczekiwania `0.1 * "a"`, nie przy `x * x` — `result()` zgłasza go ponownie w wątku wywołującym, a `exception()` zwraca go jako wartość. Funkcja `as_completed()` wydaje obiekty `Future` w kolejności kończenia — przydatnej, gdy wyniki chcemy przetwarzać od razu; `map()` zwraca wyniki w kolejności zlecenia i zgłasza wyjątek zadania przy pobieraniu jego wyniku. Instrukcja `with` czeka na zakończenie wszystkich zadań i zamyka pulę. Zamiana wątków na procesy to zmiana jednej nazwy klasy — z zastrzeżeniami o strażniku `__main__` i serializacji z poprzedniej sekcji.

## Rozmiar puli

Argument `max_workers=` określa liczbę wątków lub procesów. Bez niego `ThreadPoolExecutor` tworzy `min(32, liczba_rdzeni + 4)` wątków — zadania czekające na wejście i wyjście korzystają z większej liczby wątków niż rdzeni — a `ProcessPoolExecutor` tyle procesów, ile rdzeni dostępnych dla procesu (na Windows najwyżej 61):

```{ .python .no-copy }
>>> import os
>>> os.cpu_count(), os.process_cpu_count()
(22, 22)
```

`os.process_cpu_count()` (od Pythona 3.13) uwzględnia zbiór procesorów przydzielonych procesowi przez system oraz zmienną środowiskową `PYTHON_CPU_COUNT`; dla zadań obciążających procesor więcej procesów niż rdzeni nie przyspiesza, a każdy proces zajmuje pamięć.

## Interpretery w jednym procesie — `InterpreterPoolExecutor` (dla dociekliwych)

Python 3.14 udostępnia w bibliotece standardowej wiele interpreterów w jednym procesie (PEP 734, moduł `concurrent.interpreters`). Każdy interpreter ma własną globalną blokadę, więc kod w różnych interpreterach wykonuje się równolegle, a uruchomienie interpretera jest tańsze niż procesu. Pula `InterpreterPoolExecutor` daje do nich ten sam interfejs co pozostałe pule; porównujemy ją z pulą procesów na zliczaniu liczb pierwszych — zadaniu, które w następnym podrozdziale posłuży do pełnych pomiarów:

```python title="interpretery.py"
import time
from concurrent.futures import InterpreterPoolExecutor, ProcessPoolExecutor

N = 300_000


def liczba_pierwszych(n):
    return sum(1 for k in range(2, n) if all(k % d for d in range(2, int(k**0.5) + 1)))


if __name__ == "__main__":
    for klasa in (ProcessPoolExecutor, InterpreterPoolExecutor):
        start = time.perf_counter()
        with klasa(max_workers=4) as pula:
            wyniki = list(pula.map(liczba_pierwszych, [N] * 4))
        print(f"{klasa.__name__:<24}{time.perf_counter() - start:.2f} s  wynik {wyniki[0]}")
```

```{ .text .no-copy }
ProcessPoolExecutor     0.66 s  wynik 25997
InterpreterPoolExecutor 0.55 s  wynik 25997
```

Interpretery są od siebie odizolowane: nie dzielą obiektów ani zaimportowanych modułów, a funkcja i argumenty wędrują do nich przez `pickle`, jak do procesów. Czasy obu pul są zbliżone: interpretery oszczędzają koszt uruchamiania procesów systemowych i zużywają mniej pamięci, ale mechanizm jest nowy i nie wszystkie moduły rozszerzeń go obsługują. Moduł `concurrent.interpreters` pozwala też sterować interpreterami wprost: `create()` tworzy interpreter, `exec()` wykonuje w nim kod, a `Queue` przekazuje dane między interpreterami.

## Dobór narzędzia

| Zadanie | Narzędzie | Uzasadnienie |
|---|---|---|
| czeka na sieć, dysk, użytkownika | `ThreadPoolExecutor` albo `asyncio` | wątek oddaje GIL na czas czekania |
| liczy w czystym Pythonie | `ProcessPoolExecutor`, `InterpreterPoolExecutor` albo wątki w `3.14t` | potrzebna równoległość na rdzeniach |
| liczy w kodzie C (NumPy, `hashlib`) | `ThreadPoolExecutor` | kod w C zwalnia GIL |
| wiele bardzo krótkich zadań | wykonanie sekwencyjne albo wektoryzacja z rozdziału 14 | koszt zlecenia przewyższa zysk |
| obliczenie w programie okienkowym | jeden wątek roboczy i kolejka | pętla zdarzeń musi pozostać wolna |

Pomiary, które stoją za tą tabelą, zbieramy w następnym podrozdziale.
