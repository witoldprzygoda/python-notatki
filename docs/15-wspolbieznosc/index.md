# 15. Współbieżność — wątki, procesy i GIL

Dotąd nasze programy wykonywały jedną instrukcję po drugiej. **Współbieżność** (ang. *concurrency*) to organizacja programu jako kilku zadań, które postępują naprzemiennie i mogą na siebie czekać; **równoległość** (ang. *parallelism*) to wykonywanie zadań w tej samej chwili na różnych rdzeniach procesora. Python oferuje obie, ale nie każdym narzędziem: wątki w standardowej kompilacji interpretera dają współbieżność bez równoległości — za sprawą globalnej blokady interpretera, o której traktuje pierwszy podrozdział — a równoległość zapewniają procesy, osobne interpretery i kompilacja free-threaded z rozdziału 1.

Wybór narzędzia zależy od rodzaju zadania. **Zadania ograniczone wejściem-wyjściem** (ang. *I/O-bound*) większość czasu czekają — na odpowiedź serwera, odczyt z dysku, wpis użytkownika — i przyspieszają dzięki wątkom albo `asyncio`, bo w czasie czekania procesor jest wolny. **Zadania ograniczone procesorem** (ang. *CPU-bound*) liczą bez przerwy i przyspieszają tylko wtedy, gdy rzeczywiście zajmą kilka rdzeni: w procesach, w osobnych interpreterach albo w wątkach kompilacji free-threaded. Rozdział kończy się pomiarami, które te reguły potwierdzają.

Materiał opiera się na funkcjach przekazywanych jako argumenty (rozdział 6), strażniku `if __name__ == "__main__":` (rozdział 7), instrukcji `with`, dzienniku `logging` i grupach wyjątków (rozdział 8), menedżerach kontekstu (rozdział 11) oraz pomiarach czasu (rozdział 13). Wszystkie czasy pochodzą z komputera autora i na innym sprzęcie będą inne; istotne są proporcje.

---

## W tym rozdziale

1. [Wątki i GIL](watki-i-gil.md) — proces a wątek, moduł `threading`, wątki demoniczne i `Event`, eksperyment z odliczaniem, globalna blokada interpretera, kompilacja free-threaded, dziennik z wielu wątków
2. [Synchronizacja](synchronizacja.md) — wyścig danych, blokada `Lock` i `with`, `RLock`, zakleszczenie, kolejka `queue.Queue`, wątki a interfejs graficzny, inne narzędzia
3. [Procesy i pule wykonawców](procesy-i-executory.md) — `multiprocessing.Pool`, `concurrent.futures` i obiekty `Future`, rozmiar puli, `InterpreterPoolExecutor`, dobór narzędzia
4. [Studia wydajności i asyncio](studia-wydajnosci.md) — zadania ograniczone wejściem-wyjściem i procesorem na kompilacjach 3.14 i 3.14t, kod w C a GIL, koszt procesów, zapowiedź `asyncio`

!!! note "Laboratorium 11"
    Zadania laboratoryjne — odliczanie w jednym i dwóch wątkach, wątek-logger, pula procesów — odpowiadają podrozdziałom 1 i 3; podrozdział 2 dostarcza narzędzi do bezpiecznej pracy na wspólnych danych, a podrozdział 4 pokazuje, jak zmierzyć, czy współbieżność w ogóle się opłaca.
