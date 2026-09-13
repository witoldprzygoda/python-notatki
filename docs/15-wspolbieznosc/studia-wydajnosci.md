# Studia wydajności i asyncio

Reguły doboru narzędzia z poprzedniego podrozdziału sprawdzamy pomiarami: zadanie czekające, zadanie liczące, kod w C oraz koszt samych procesów — na standardowej kompilacji 3.14 i na kompilacji free-threaded. Na koniec zapowiadamy czwartą drogę, `asyncio`.

## Zadania ograniczone wejściem-wyjściem

Pobieranie czterech plików z sieci symulujemy oczekiwaniem pół sekundy na każdy — dokładnie tak zachowuje się wątek czekający na odpowiedź serwera:

```python title="we-wy.py"
import time
from concurrent.futures import ThreadPoolExecutor


def pobierz(numer):
    time.sleep(0.5)  # symulacja oczekiwania na odpowiedź serwera
    return f"plik {numer}"


start = time.perf_counter()
wyniki = [pobierz(numer) for numer in range(4)]
print(f"sekwencyjnie: {time.perf_counter() - start:.2f} s, {wyniki}")

start = time.perf_counter()
with ThreadPoolExecutor() as pula:
    wyniki = list(pula.map(pobierz, range(4)))
print(f"4 wątki:      {time.perf_counter() - start:.2f} s, {wyniki}")
```

```{ .text .no-copy }
sekwencyjnie: 2.00 s, ['plik 0', 'plik 1', 'plik 2', 'plik 3']
4 wątki:      0.50 s, ['plik 0', 'plik 1', 'plik 2', 'plik 3']
```

Cztery oczekiwania nakładają się na siebie, więc całość trwa tyle, co jedno. Ten sam efekt daje rzeczywiste pobieranie stron modułem `urllib.request` z biblioteki standardowej — na komputerze autora cztery strony pobrane sekwencyjnie zajęły 0,81 s, a w wątkach 0,38 s:

```{ .python .no-copy }
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ADRESY = ["https://www.python.org/", "https://docs.python.org/3/",
          "https://pypi.org/", "https://peps.python.org/"]


def pobierz(adres):
    with urllib.request.urlopen(adres, timeout=10) as odpowiedz:
        return adres, len(odpowiedz.read())


with ThreadPoolExecutor() as pula:
    for adres, rozmiar in pula.map(pobierz, ADRESY):
        print(f"{adres}: {rozmiar} B")
```

Zysk zależy od liczby zadań i czasu czekania, nie od liczby rdzeni: dziesięć wątków pobierających dziesięć stron działa dobrze także na jednym rdzeniu.

## Zadania ograniczone procesorem

Zliczanie liczb pierwszych poniżej trzystu tysięcy z poprzedniego podrozdziału — cztery identyczne zadania — wykonujemy sekwencyjnie, w wątkach i w procesach:

```python title="cpu.py"
import sys
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

N = 300_000


def liczba_pierwszych(n):
    return sum(1 for k in range(2, n) if all(k % d for d in range(2, int(k**0.5) + 1)))


if __name__ == "__main__":
    start = time.perf_counter()
    wyniki = [liczba_pierwszych(N) for _ in range(4)]
    print(f"sekwencyjnie:        {time.perf_counter() - start:.2f} s  wynik {wyniki[0]}")
    for klasa in (ThreadPoolExecutor, ProcessPoolExecutor):
        start = time.perf_counter()
        with klasa(max_workers=4) as pula:
            wyniki = list(pula.map(liczba_pierwszych, [N] * 4))
        print(f"{klasa.__name__:<21}{time.perf_counter() - start:.2f} s  (GIL włączony: {sys._is_gil_enabled()})")
```

```{ .text .no-copy }
sekwencyjnie:        1.82 s  wynik 25997
ThreadPoolExecutor   1.94 s  (GIL włączony: True)
ProcessPoolExecutor  0.69 s  (GIL włączony: True)
```

```powershell title="Terminal"
py -V:3.14t cpu.py
```

```{ .text .no-copy }
sekwencyjnie:        1.89 s  wynik 25997
ThreadPoolExecutor   0.59 s  (GIL włączony: False)
ProcessPoolExecutor  0.67 s  (GIL włączony: False)
```

| Uruchomienie | 3.14 (GIL) | 3.14t (free-threaded) |
|---|---|---|
| sekwencyjnie | ok. 1,8 s | ok. 1,9 s |
| 4 wątki | ok. 1,9 s — bez zysku | ok. 0,6 s — trzykrotnie szybciej |
| 4 procesy | ok. 0,7 s — ponad dwuipółkrotnie szybciej | ok. 0,7 s |

W standardowej kompilacji wątki liczą naprzemiennie i nie skracają czasu; procesy wykorzystują cztery rdzenie, a od czterokrotnego przyspieszenia dzieli je koszt ich uruchomienia. W kompilacji free-threaded wątki dorównują procesom bez kosztu ich uruchamiania i bez serializacji danych. To domknięcie dróg do wielu rdzeni z rozdziału [13. Wydajność i optymalizacja](../13-wydajnosc/przyspieszanie-pythona.md#wiele-rdzeni-314t-i-procesy): dla kodu liczącego w czystym Pythonie mamy procesy, interpretery i `3.14t`; dla kodu, który da się zapisać na tablicach — NumPy z rozdziału 14.

## Kod w C zwalnia GIL

Funkcja `hashlib.pbkdf2_hmac()` wyprowadza klucz z hasła setkami tysięcy iteracji funkcji skrótu — obliczenie czysto procesorowe, ale wykonywane w C, a moduł `hashlib` zwalnia na ten czas globalną blokadę:

```python title="skrot.py"
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor


def skrot(haslo):
    return hashlib.pbkdf2_hmac("sha256", haslo, b"sol", 200_000).hex()[:8]


hasla = [b"haslo1", b"haslo2", b"haslo3", b"haslo4"]

start = time.perf_counter()
print([skrot(haslo) for haslo in hasla], f"sekwencyjnie {time.perf_counter() - start:.2f} s")

start = time.perf_counter()
with ThreadPoolExecutor() as pula:
    print(list(pula.map(skrot, hasla)), f"4 wątki {time.perf_counter() - start:.2f} s")
```

```{ .text .no-copy }
['b0763404', '1086077a', '5a6ef483', 'e506e0b8'] sekwencyjnie 0.12 s
['b0763404', '1086077a', '5a6ef483', 'e506e0b8'] 4 wątki 0.06 s
```

Wątki przyspieszają to obliczenie także ze standardową blokadą, bo pętla iteracji przebiega w C bez udziału interpretera. Tak samo zachowują się duże operacje NumPy, kompresja z modułu `zlib` i odczyt plików. Reguła „zadania liczące wymagają procesów” dotyczy więc kodu liczącego **w Pythonie**; kod w C trzeba zmierzyć.

## Koszt procesów i zadań zbyt małych

Uruchomienie procesu potomnego metodą `spawn` zajmuje na komputerze autora około 0,1 s — nowy interpreter startuje i importuje moduł główny — a każde zlecenie kosztuje serializację argumentów i wyniku. Zadanie trwające mikrosekundy, rozdzielone na procesy, wykona się wolniej niż sekwencyjnie; podobnie zadanie czekające na sieć zyska na wątkach, nie na procesach, które jedynie dodadzą koszt startu. Trzy typowe powody, dla których kod współbieżny bywa wolniejszy od sekwencyjnego: wątki użyte do obliczeń w czystym Pythonie, procesy użyte do zadań czekających oraz zadania zbyt drobne, by opłacało się je zlecać. Odpowiedź daje zawsze pomiar — narzędziami z rozdziału 13 — a nie przypuszczenie.

## Zapowiedź `asyncio`

Czwarta droga — po wątkach, procesach i interpreterach — nie używa ani wątków, ani procesów. **Programowanie asynchroniczne** (ang. *asynchronous programming*) prowadzi wiele zadań w jednym wątku: zadanie, które czeka, oddaje sterowanie **pętli zdarzeń** (ang. *event loop*), a ta uruchamia kolejne gotowe zadanie. Służą do tego słowa kluczowe `async` i `await` z katalogu w rozdziale 3 — `async def` definiuje funkcję, której wywołanie — jak `pobierz(1, 1.0)` — nie wykonuje kodu, lecz zwraca **korutynę** (ang. *coroutine*) do uruchomienia przez pętlę zdarzeń, a `await` zaznacza miejsce, w którym zadanie może oddać sterowanie:

```python title="asyncio-demo.py"
import asyncio
import time


async def pobierz(numer, czas):
    await asyncio.sleep(czas)  # oczekiwanie oddaje sterowanie pętli zdarzeń
    return f"plik {numer} po {czas} s"


async def zawiedz(numer):
    await asyncio.sleep(0)  # oddaje sterowanie na jeden obrót pętli
    raise ValueError(f"zadanie {numer} nie powiodło się")


async def main():
    start = time.perf_counter()
    wyniki = await asyncio.gather(pobierz(1, 1.0), pobierz(2, 1.0), pobierz(3, 1.0))
    print(wyniki, f"{time.perf_counter() - start:.1f} s")

    try:
        async with asyncio.TaskGroup() as grupa:
            grupa.create_task(pobierz(4, 0.2))
            grupa.create_task(zawiedz(5))
            grupa.create_task(zawiedz(6))
    except* ValueError as bledy:
        print("niepowodzenia:", sorted(str(e) for e in bledy.exceptions))


asyncio.run(main())
```

```{ .text .no-copy }
['plik 1 po 1.0 s', 'plik 2 po 1.0 s', 'plik 3 po 1.0 s'] 1.0 s
niepowodzenia: ['zadanie 5 nie powiodło się', 'zadanie 6 nie powiodło się']
```

`asyncio.run()` uruchamia pętlę zdarzeń i korutynę główną; `gather()` wykonuje kilka korutyn współbieżnie i zwraca listę wyników w kolejności podania — trzy sekundowe oczekiwania trwają łącznie sekundę. `TaskGroup` (od Pythona 3.11) prowadzi grupę zadań dodawanych metodą `create_task()`: gdy którekolwiek zawiedzie, anuluje pozostałe — tu niedokończone `pobierz(4, 0.2)`, po którym w wyniku nie ma śladu — a wyjątki zadań, także pojedynczy, zbiera w grupę `ExceptionGroup`, którą obsługujemy składnią `except*` z rozdziału [8. Wyjątki i zarządzanie zasobami](../08-wyjatki/styl-i-testowanie.md#grupy-wyjatkow-i-except-dla-dociekliwych) — to właśnie programy współbieżne były powodem jej powstania. Ponieważ wszystko dzieje się w jednym wątku, a przełączenie następuje tylko przy `await`, nie ma wyścigów danych między zadaniami; w zamian każda operacja czekająca musi być asynchroniczna — `time.sleep()` zablokowałby całą pętlę, stąd `asyncio.sleep()`, a zamiast `urllib` używa się bibliotek asynchronicznych. Python 3.14 dodał narzędzia diagnostyczne `python -m asyncio ps PID` i `pstree`, wypisujące zadania działającego programu. `asyncio` jest właściwym narzędziem dla serwerów i klientów obsługujących setki połączeń; jego pełne omówienie wykracza poza część I książki.
