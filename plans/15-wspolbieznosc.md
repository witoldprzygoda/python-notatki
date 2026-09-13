# Projekt rozdziału 15 — Współbieżność: wątki, procesy i GIL

Skondensowany projekt stron rozdziału 15 według `PLAN_ROZWOJU.md` (sekcja 4, „15. Współbieżność — wątki, procesy i GIL”) i `DEVELOPMENT_WORKFLOW.md`. Branch: `content/15-wspolbieznosc` (z `dev` po integracji rozdziału 14, commit `fcd94ec`). Realizacja autonomiczna na polecenie autora („Działaj z domknięciem części I”).

## Decyzje redakcyjne (13 IX 2026)

1. **Interpretery:** przykłady weryfikowane harnessem na Pythonie 3.14.7 (venv kursu); wyniki dla kompilacji free-threaded jako bloki terminalowe `py -V:3.14t skrypt.py` z rzeczywistych uruchomień na komputerze autora (jak w rozdziale 13). Czasy w blokach maskowane w harnessie (`--mask=\d+\.\d+ s`); proza podaje proporcje, nie wartości.
2. **Terminologia:** „współbieżność” (ang. *concurrency*) a „równoległość” (ang. *parallelism*); „zadania ograniczone wejściem-wyjściem” (ang. *I/O-bound*) i „ograniczone procesorem” (ang. *CPU-bound*); „globalna blokada interpretera” (GIL); „kompilacja free-threaded” (jak w rozdziałach 1 i 13); „wyścig danych” (ang. *data race*); „zakleszczenie” (ang. *deadlock*); „pula wykonawców” dla *executor*; „obiekt `Future`” bez tłumaczenia; „wątek demoniczny” (ang. *daemon thread*).
3. **Determinizm przykładów:** kolejność wydruków z wątków ustalana czasami `sleep()` z marginesem ≥ 0,1 s; wyścig danych pokazany wersją z opóźnieniem między odczytem a zapisem (wynik 1 zamiast 2 na obu kompilacjach) oraz pętlą `+=` — na 3.14 pełne 4 000 000 „przypadkiem”, na 3.14t ok. 1,8 mln (blok terminalowy); zakleszczenie pokazane przez `acquire(timeout=)` z różnymi limitami (1 s i 2 s), bez wieszania programu.
4. **Zadania ograniczone wejściem-wyjściem** symulowane przez `time.sleep()` (harness bez sieci); pobieranie stron przez `urllib.request` jako blok `.python .no-copy` z czasem z komputera autora. Zadania obciążające procesor: zliczanie liczb pierwszych poniżej 300 000 (ok. 0,55 s) w czterech identycznych zadaniach; odliczanie 50 000 000 (ok. 1,2 s) jak w lab11.
5. **Kod w C zwalnia GIL:** `hashlib.pbkdf2_hmac()` z materiałów źródłowych przyspiesza w wątkach także na standardowej kompilacji — pokazane jako zastrzeżenie, nie jako przykład CPU-bound (rozbieżność ze źródłem, patrz HANDOFF).
6. **Modernizacje:** `time.perf_counter()` zamiast `time.time()`; wątek-logger zatrzymywany przez `threading.Event`, nie zabijany jako demon; `queue.Queue.shutdown()` (3.13) zamiast wartownika; `os.process_cpu_count()` (3.13); `multiprocessing` z metodą `spawn` na Windows i macOS, `forkserver` na innych Uniksach od 3.14; `concurrent.futures.InterpreterPoolExecutor` i `concurrent.interpreters` (3.14, PEP 734) jako sekcja dla dociekliwych; `asyncio.TaskGroup` z `except*` (domyka grupy wyjątków z rozdziału 8); `python -m asyncio ps` (3.14) jednym zdaniem.
7. **`multiprocessing.Pool`** pokazany raz (lab11), dalej `concurrent.futures` jako interfejs zalecany; strażnik `if __name__ == "__main__":` wyjaśniony przez mechanizm `spawn` (proces potomny importuje moduł).
8. **asyncio** tylko jako zapowiedź w ostatniej sekcji (składnia `async`/`await`, `asyncio.run()`, `gather()`, `TaskGroup`); pełny materiał poza zakresem części I.
9. Etykiety nav bez dopisku „(dla dociekliwych)”; sekcje uzupełniające oznaczone w nagłówkach H2.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty |
|---|---|---|
| `index.md` | Wprowadzenie / „15. Współbieżność — wątki, procesy i GIL” | współbieżność a równoległość; dwa rodzaje zadań; cztery drogi (wątki, procesy, interpretery, asyncio); ---; ## W tym rozdziale (4); nota lab11 |
| `watki-i-gil.md` | Wątki i GIL | Proces a wątek; Moduł `threading` — `Thread`, `start()` i `join()` (`pierwsze-watki.py`: nazwy, `current_thread()`, kolejność kończenia); Wątki demoniczne i zatrzymywanie przez `Event` (`logger.py`: lab11 A/B/C jako omówienie, kod z `Event`); Eksperyment — odliczanie w jednym i dwóch wątkach (`odliczanie.py`, 50 mln); Globalna blokada interpretera (co robi, `getswitchinterval()`, kiedy wątki pomagają); Kompilacja free-threaded (terminal `py -V:3.14t odliczanie.py`; `sys._is_gil_enabled()`, `PYTHON_GIL`, narzut 5–10 %, rozszerzenia w C włączają GIL z ostrzeżeniem, licznik referencji dzielony na część wątku i współdzieloną, PEP 703/779) — domyka rozdz. 10; Dziennik z wielu wątków (`dziennik.py`: `%(threadName)s`) — domyka rozdz. 8 |
| `synchronizacja.md` | Synchronizacja | Wyścig danych (`wyscig.py`: licznik z opóźnieniem → 1; `licznik.py`: `+=` ×4 mln + terminal 3.14t); Blokada `Lock` i instrukcja `with` (`blokada.py` → 2 i 4 000 000; `acquire()`/`release()`; domyka rozdz. 11); Blokada wielokrotna `RLock`; Zakleszczenie (`zakleszczenie.py` z `timeout=`; zasada stałej kolejności); Kolejka `queue.Queue` — producent i konsument (`kolejka.py` z `shutdown()`); Wątki a interfejs graficzny (akapit: pętla zdarzeń w jednym wątku, kolejka + odpytywanie; zapowiedź części II); Inne narzędzia — `Semaphore`, `Event`, `Condition`, `Barrier` (dla dociekliwych) (tabela) |
| `procesy-i-executory.md` | Procesy i pule wykonawców | Procesy zamiast wątków — `multiprocessing.Pool` (`procesy.py`: odliczanie w 2 procesach; metody startu; strażnik `__main__`; picklowalność); Wspólny interfejs — `concurrent.futures` (`futures.py`: `submit()`, `Future.result()`, `as_completed()`, `map()`, wyjątek z zadania); Rozmiar puli (`max_workers`: `min(32, cpu + 4)`, `os.process_cpu_count()`); Interpretery w jednym procesie — `InterpreterPoolExecutor` (dla dociekliwych) (`interpretery.py`; PEP 734; ograniczenia: izolacja, `pickle`); Dobór narzędzia (tabela) |
| `studia-wydajnosci.md` | Studia wydajności i asyncio | Zadania ograniczone wejściem-wyjściem (`we-wy.py`: `sleep` ×4 sekwencyjnie a `ThreadPoolExecutor`; `urllib` jako `.no-copy`); Zadania ograniczone procesorem (`cpu.py`: liczby pierwsze ×4 — sekwencyjnie, wątki, procesy; terminal 3.14t; tabela 3.14 a 3.14t); Kod w C zwalnia GIL (`skrot.py`: `pbkdf2_hmac` w wątkach); Koszt procesów i zadań zbyt małych (akapit z pomiarem uruchomienia procesu ok. 0,1 s); Zapowiedź `asyncio` (`asyncio-demo.py`: `gather()` 3 × 1 s → 1 s; `TaskGroup` + `except*`; `python -m asyncio ps`) — domyka rozdz. 8 (grupy wyjątków) i katalog słów kluczowych |

Szacunek: 750–850 linii.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 14)

```yaml
  - 15. Współbieżność — wątki, procesy i GIL:
      - Wprowadzenie: 15-wspolbieznosc/index.md
      - Wątki i GIL: 15-wspolbieznosc/watki-i-gil.md
      - Synchronizacja: 15-wspolbieznosc/synchronizacja.md
      - Procesy i pule wykonawców: 15-wspolbieznosc/procesy-i-executory.md
      - Studia wydajności i asyncio: 15-wspolbieznosc/studia-wydajnosci.md
```

`docs/index.md`: „15. [Współbieżność — wątki, procesy i GIL](15-wspolbieznosc/index.md) — wątki i GIL, synchronizacja, procesy i pule wykonawców, pomiary i asyncio”.

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `synchronizacja.md` (Wątki a interfejs graficzny) | tkinter — `after()` i kolejka w programie okienkowym | część II (sekcja 18 planu) |

## Domknięcia zapowiedzi z wcześniejszych rozdziałów

| Plik | Wiersz | Zapowiedź | Cel |
|---|---|---|---|
| `08-wyjatki/logging.md` | 156 | wpisy z wielu wątków — TODO | `watki-i-gil.md#dziennik-z-wielu-watkow` |
| `08-wyjatki/styl-i-testowanie.md` | 332 | grupy wyjątków w programach współbieżnych — TODO | `studia-wydajnosci.md#zapowiedz-asyncio` |
| `10-klasy/cykl-zycia-obiektu.md` | 108 | licznik referencji w kompilacji free-threaded — TODO | `watki-i-gil.md#kompilacja-free-threaded` |
| `11-model-danych/menedzery-kontekstu.md` | 249 | `with blokada:` — TODO | `synchronizacja.md#blokada-lock-i-instrukcja-with` |
| `13-wydajnosc/przyspieszanie-pythona.md` | 99 | wątki, procesy, `3.14t` — TODO | `studia-wydajnosci.md#zadania-ograniczone-procesorem` |

## CONTENT HANDOFF (rozbieżności ze źródłami)

(a) python_thread sl. 33–34 i lab11: `hashlib.pbkdf2_hmac()` jako zadanie „obciążające CPU” przyspieszane tylko procesami — w rzeczywistości `hashlib` zwalnia GIL, więc wątki dają ten sam zysk (4 wywołania: 0,12 s → 0,04 s na 3.14); w książce jako zastrzeżenie o kodzie w C; (b) python_thread sl. 8–11: czasy „ze starego laptopa” (5 s, 3 s) — własne pomiary na 3.14.7 (odliczanie 50 mln: 1,2 s; 2 procesy 0,8 s; 3.14t 2 wątki 0,6 s); (c) python_thread sl. 25–26: `threading._shutdown()` — pominięte (szczegół implementacji); sl. 30: zasada „2 × cpu_count() + 1” — zastąpiona domyślnym `min(32, cpu + 4)` z dokumentacji; (d) lab11: `time.time()` → `perf_counter()`; wątek-logger jako demon w pętli nieskończonej → zatrzymanie przez `Event` (wersja z demonem omówiona jako część A/B/C); (e) python_thread sl. 16: „ThreadPoolExecutor (…) wersja mniej wydajna” przy pobieraniu plików — w rzeczywistości wątki są tu właściwe, a procesy wolniejsze przez koszt startu; (f) `requests` → `urllib.request` (biblioteka standardowa); (g) GIL opisany w źródłach jako bezwarunkowy — od 3.13/3.14 kompilacja free-threaded (PEP 703, 779).

## Listy kontrolne

- Przed commitem stron: harness (`--mask=\d+\.\d+ s`), `refresh_outputs.py`, bloki 3.14t z rzeczywistych uruchomień, oba buildy `--strict`, audyt kotwic, cudzysłowy, kolokwializmy, trzy recenzje.
- Po commicie: domknięcia z tabeli, status w `PLAN_ROZWOJU.md`, integracja do `dev`, wpis w pamięci.
