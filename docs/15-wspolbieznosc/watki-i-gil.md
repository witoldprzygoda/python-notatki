# Wątki i GIL

Wątek to najprostszy sposób, aby program wykonywał dwie czynności jednocześnie: czekał na dane i jednocześnie odświeżał ekran, obsługiwał kilku klientów, wypisywał postęp długiego obliczenia. W tym podrozdziale poznajemy moduł `threading`, mierzymy zysk z wątków w obliczeniach, i wyjaśniamy wynik tego pomiaru: globalną blokadę interpretera oraz jej brak w kompilacji free-threaded.

## Proces a wątek

**Proces** (ang. *process*) to uruchomiony program z własną, odseparowaną pamięcią; system operacyjny nie pozwala jednemu procesowi czytać pamięci drugiego. **Wątek** (ang. *thread*) to ścieżka wykonania wewnątrz procesu: każdy proces ma co najmniej jeden wątek — główny — i może utworzyć kolejne. Wątki jednego procesu dzielą pamięć: widzą te same nazwy globalne i te same obiekty, więc komunikują się bez kopiowania danych. To ich największa zaleta i zarazem źródło błędów, którym poświęcamy następny podrozdział. System operacyjny przydziela wątkom czas procesora i przełącza je bez udziału programu.

## Moduł `threading` — `Thread`, `start()` i `join()`

Wątek tworzymy obiektem `Thread`, podając funkcję do wykonania i jej argumenty; `start()` uruchamia funkcję w nowym wątku i natychmiast wraca, a `join()` czeka na zakończenie wątku:

```python title="pierwsze-watki.py"
import threading
import time


def praca(nazwa, czas):
    time.sleep(czas)
    print(f"{nazwa}: koniec po {czas} s w wątku {threading.current_thread().name}")


watki = [
    threading.Thread(target=praca, args=("A", 0.3), name="watek-A"),
    threading.Thread(target=praca, args=("B", 0.1), name="watek-B"),
    threading.Thread(target=praca, args=("C", 0.2), name="watek-C"),
]
for watek in watki:
    watek.start()
print("wątek główny: uruchomiono", threading.active_count() - 1, "wątki")
for watek in watki:
    watek.join()
print("wątek główny: wszystkie zakończone", [watek.is_alive() for watek in watki])
```

```{ .text .no-copy }
wątek główny: uruchomiono 3 wątki
B: koniec po 0.1 s w wątku watek-B
C: koniec po 0.2 s w wątku watek-C
A: koniec po 0.3 s w wątku watek-A
wątek główny: wszystkie zakończone [False, False, False]
```

Wątek główny wypisuje swój komunikat, zanim którykolwiek wątek skończy, bo `start()` nie czeka; wątki kończą w kolejności wyznaczonej przez czas pracy, nie przez kolejność uruchomienia. Funkcja `current_thread()` zwraca obiekt bieżącego wątku z jego nazwą (bez argumentu `name=` byłyby to `Thread-1 (praca)`, `Thread-2 (praca)`, …), `active_count()` liczy żyjące wątki razem z głównym, a `is_alive()` mówi, czy wątek jeszcze pracuje. Wątek można też zdefiniować jako podklasę `Thread` z metodą `run()`; funkcja przekazana przez `target=` jest prostsza i wystarcza w większości programów. Metody `run()` nie wywołujemy samodzielnie — wykonałaby funkcję w bieżącym wątku.

## Wątki demoniczne i zatrzymywanie przez `Event`

Program kończy się, gdy zakończy się wątek główny **i** wszystkie zwykłe wątki — interpreter czeka na nie tak, jakby wywołał `join()`. **Wątek demoniczny** (ang. *daemon thread*), utworzony z argumentem `daemon=True`, nie wstrzymuje zakończenia programu: gdy zostaną tylko demony, interpreter kończy się, a demony są przerywane w dowolnym miejscu, bez sprzątania. Trzy warianty wątku-loggera wypisującego komunikat co ułamek sekundy pokazują to w praktyce: jako demon bez `join()` zostaje przerwany w połowie pracy, z `join()` wstrzymuje program, a jako zwykły wątek z pętlą nieskończoną nie pozwala programowi się zakończyć. Właściwe rozwiązanie to sygnał zatrzymania — obiekt `Event`:

```python title="logger.py"
import threading
import time


def logger(stop):
    while not stop.is_set():
        print("logger: ping")
        stop.wait(0.4)
    print("logger: koniec")


stop = threading.Event()
watek = threading.Thread(target=logger, args=(stop,), daemon=True)
watek.start()
for numer in range(1, 4):
    time.sleep(0.5)
    print(f"serwer: zadanie {numer} wykonane")
stop.set()
watek.join()
print("serwer: zamknięty")
```

```{ .text .no-copy }
logger: ping
logger: ping
serwer: zadanie 1 wykonane
logger: ping
serwer: zadanie 2 wykonane
logger: ping
serwer: zadanie 3 wykonane
logger: koniec
serwer: zamknięty
```

`Event` to flaga widoczna dla wszystkich wątków: `set()` ją ustawia, `is_set()` sprawdza, a `wait(timeout)` czeka na ustawienie najwyżej podany czas — zastępuje `sleep()`, bo budzi wątek natychmiast po `set()`. Wątek główny po wykonaniu zadań ustawia flagę i czeka `join()`, więc logger kończy pracę w sposób kontrolowany, wypisując ostatni komunikat. Flaga `daemon=True` pozostaje jako zabezpieczenie: gdyby wątek główny zakończył się wyjątkiem przed `stop.set()`, program i tak się zamknie.

## Eksperyment — odliczanie w jednym i dwóch wątkach

Skoro wątki działają „naraz”, podział obliczenia na dwa wątki powinien skrócić czas o połowę. Sprawdzamy to na pętli odliczającej od pięćdziesięciu milionów do zera — zadaniu, które nie czeka na nic, tylko liczy:

```python title="odliczanie.py"
import sys
import threading
import time

N = 50_000_000


def odliczaj(n):
    while n > 0:
        n -= 1


start = time.perf_counter()
odliczaj(N)
print(f"1 wątek: {time.perf_counter() - start:.2f} s")

watki = [threading.Thread(target=odliczaj, args=(N // 2,)) for _ in range(2)]
start = time.perf_counter()
for watek in watki:
    watek.start()
for watek in watki:
    watek.join()
print(f"2 wątki: {time.perf_counter() - start:.2f} s  (GIL włączony: {sys._is_gil_enabled()})")
```

```{ .text .no-copy }
1 wątek: 1.05 s
2 wątki: 1.06 s  (GIL włączony: True)
```

Dwa wątki nie są szybsze od jednego — różnica mieści się w błędzie pomiaru, a przełączanie wątków dokłada własny koszt. Wyjaśnieniem jest blokada wypisana w ostatnim wierszu.

## Globalna blokada interpretera

**Globalna blokada interpretera** (ang. *global interpreter lock*, GIL), wspomniana w rozdziałach 1 i [13. Wydajność i optymalizacja](../13-wydajnosc/przyspieszanie-pythona.md#wiele-rdzeni-314t-i-procesy), to blokada, którą w standardowej kompilacji CPythona musi trzymać wątek wykonujący kod bajtowy Pythona. W danej chwili trzyma go jeden wątek; pozostałe czekają, a wątek czekający po pięciu milisekundach prosi bieżący o oddanie blokady:

```{ .python .no-copy }
>>> import sys
>>> sys.getswitchinterval()
0.005
```

Blokada powstała, bo mechanizm zarządzania pamięcią z rozdziału [10. Klasy i obiekty](../10-klasy/cykl-zycia-obiektu.md#licznik-referencji-i-sysgetrefcount) — licznik referencji w każdym obiekcie — nie jest bezpieczny przy równoczesnym dostępie z wielu wątków; jedna blokada na cały interpreter rozwiązuje ten problem prosto i tanio dla programów jednowątkowych. Ceną jest brak równoległości: dwa wątki liczące w Pythonie wykonują się naprzemiennie — w danej chwili tylko jeden z nich — jak w eksperymencie powyżej.

Wątki pomagają mimo GIL w dwóch sytuacjach. Po pierwsze, wątek oddaje blokadę na czas oczekiwania — na odpowiedź z sieci, odczyt pliku, `sleep()`, wpis użytkownika — więc inne wątki pracują, gdy on czeka; to przypadek zadań ograniczonych wejściem-wyjściem. Po drugie, kod w C może zwolnić blokadę na czas własnych obliczeń: robią to między innymi funkcje skrótów z modułu `hashlib`, kompresja i duże operacje NumPy. Oba przypadki mierzymy w ostatnim podrozdziale.

## Kompilacja free-threaded

Od Pythona 3.13 istnieje kompilacja interpretera bez globalnej blokady — **free-threaded** ([PEP 703](https://peps.python.org/pep-0703/)), w Pythonie 3.14 oficjalnie wspierana, choć nadal nie domyślna ([PEP 779](https://peps.python.org/pep-0779/)). Instalujemy ją managerem z rozdziału [1. Instalacja i środowisko pracy](../01-instalacja/instalacja.md#instalacja-interpreterow) jako wariant `3.14t` i uruchamiamy ten sam skrypt:

```powershell title="Terminal"
py -V:3.14t odliczanie.py
```

```{ .text .no-copy }
1 wątek: 0.98 s
2 wątki: 0.54 s  (GIL włączony: False)
```

Dwa wątki liczą teraz równolegle na dwóch rdzeniach i czas spada o połowę. Funkcja `sys._is_gil_enabled()`, znana z rozdziału 13, mówi, czy blokada działa w bieżącym procesie; w kompilacji free-threaded można ją włączyć z powrotem zmienną środowiskową `PYTHON_GIL=1` albo opcją `-X gil=1`. Kompilacja ma swoją cenę: typowy kod jednowątkowy wykonuje się o około 5–10% wolniej — w tak prostej pętli jak powyższa różnica ginie w błędzie pomiaru — a moduł rozszerzeń w C, który nie deklaruje obsługi kompilacji free-threaded, po zaimportowaniu włącza blokadę z ostrzeżeniem. Aby licznik referencji był bezpieczny bez wspólnej blokady, każdy obiekt ma go w dwóch częściach — jedną zmienia wyłącznie wątek, który obiekt utworzył, drugą, współdzieloną, wszystkie pozostałe operacjami atomowymi — a obiekty takie jak małe liczby i stałe kodu są nieśmiertelne i licznika nie zmieniają; stąd inne wyniki `sys.getrefcount()`, co zapowiedzieliśmy w rozdziale 10. Programy poprawnie synchronizowane działają na obu kompilacjach tak samo; programy, które polegały na GIL jako na ukrytej blokadzie, w wariancie free-threaded ujawniają błędy — pokazujemy to w następnym podrozdziale.

## Dziennik z wielu wątków

Funkcja `print()` z kilku wątków bywa przeplatana w połowie wiersza; moduł `logging` z rozdziału [8. Wyjątki i zarządzanie zasobami](../08-wyjatki/logging.md#dziennik-w-pliku-i-dalsze-mozliwosci) jest **bezpieczny wątkowo** (ang. *thread-safe*) — każdy wpis trafia do dziennika w całości — i potrafi dopisać nazwę wątku:

```python title="dziennik.py"
import logging
import threading
import time

logging.basicConfig(level=logging.INFO, format="%(threadName)s: %(message)s")


def praca(czas):
    logging.info("start")
    time.sleep(czas)
    logging.info("koniec po %.1f s", czas)


watki = [threading.Thread(target=praca, args=(0.3 - 0.1 * numer,), name=f"robotnik-{numer}") for numer in range(3)]
for watek in watki:
    watek.start()
for watek in watki:
    watek.join()
logging.info("wszystkie wątki zakończone")
```

```{ .text .no-copy }
robotnik-0: start
robotnik-1: start
robotnik-2: start
robotnik-2: koniec po 0.1 s
robotnik-1: koniec po 0.2 s
robotnik-0: koniec po 0.3 s
MainThread: wszystkie wątki zakończone
```

Pole `%(threadName)s` w formacie wpisu identyfikuje wątek; dostępne jest też `%(thread)d` z numerem systemowym. W programie z wieloma wątkami dziennik jest właściwym narzędziem diagnostyki, bo `breakpoint()` i pdb z rozdziału [8. Wyjątki i zarządzanie zasobami](../08-wyjatki/diagnostyka.md#funkcja-breakpoint-i-pdb) zatrzymują tylko wątek, w którym je wywołano, a pozostałe pracują dalej.
