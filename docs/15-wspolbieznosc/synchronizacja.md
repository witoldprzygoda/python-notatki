# Synchronizacja

Wątki dzielą pamięć, więc dwa wątki mogą zmieniać ten sam obiekt w tej samej chwili. W tym podrozdziale pokazujemy, jak taki dostęp psuje dane, i poznajemy narzędzia, które go porządkują: blokady, kolejkę oraz — w skrócie — semafory, zdarzenia, warunki i bariery.

## Wyścig danych

Zwiększenie licznika wygląda jak jedna operacja, ale składa się z trzech: odczytu wartości, obliczenia nowej i zapisu. Jeśli między odczytem a zapisem system operacyjny przełączy wątki, drugi wątek odczyta starą wartość i jeden z przyrostów zginie. Opóźnienie `sleep()` wstawione w to miejsce sprawia, że przełączenie następuje na pewno:

```python title="wyscig.py"
import threading
import time


class Licznik:
    def __init__(self):
        self.wartosc = 0

    def zwieksz(self):
        odczyt = self.wartosc
        time.sleep(0.1)  # inna praca między odczytem a zapisem
        self.wartosc = odczyt + 1


licznik = Licznik()
watki = [threading.Thread(target=licznik.zwieksz) for _ in range(2)]
for watek in watki:
    watek.start()
for watek in watki:
    watek.join()
print("oczekiwane 2, otrzymane", licznik.wartosc)
```

```{ .text .no-copy }
oczekiwane 2, otrzymane 1
```

Taką sytuację nazywamy **wyścigiem danych** (ang. *data race*): wynik zależy od tego, który wątek zdąży pierwszy. Bez `sleep()` błąd zdarza się rzadziej — a niekiedy, jak zaraz pokażemy, standardowa kompilacja maskuje go zupełnie — lecz jego przyczyna pozostaje: wystarczy, że przełączenie wątków wypadnie między odczytem a zapisem. Pętla zwiększająca licznik milion razy w czterech wątkach pokazuje, jak bardzo zależy to od kompilacji interpretera:

```python title="licznik.py"
import sys
import threading


class Licznik:
    def __init__(self):
        self.wartosc = 0

    def zwiekszaj(self, ile):
        for _ in range(ile):
            self.wartosc += 1


licznik = Licznik()
watki = [threading.Thread(target=licznik.zwiekszaj, args=(1_000_000,)) for _ in range(4)]
for watek in watki:
    watek.start()
for watek in watki:
    watek.join()
print(f"oczekiwane 4000000, otrzymane {licznik.wartosc} (GIL włączony: {sys._is_gil_enabled()})")
```

```{ .text .no-copy }
oczekiwane 4000000, otrzymane 4000000 (GIL włączony: True)
```

```powershell title="Terminal"
py -V:3.14t licznik.py
```

```{ .text .no-copy }
oczekiwane 4000000, otrzymane 1599200 (GIL włączony: False)
```

W standardowej kompilacji wynik jest poprawny, ale przypadkiem: interpreter przełącza wątki tylko w wybranych miejscach kodu bajtowego — w obecnym CPythonie przy skokach wstecz i wywołaniach funkcji, tu więc między obrotami pętli, nigdy między odczytem a zapisem atrybutu — więc GIL działa jak ukryta blokada. Jest to szczegół implementacji, nie gwarancja języka: wystarczy wywołanie wewnątrz tej sekwencji (właściwość zamiast atrybutu, `print()`), by okno na przełączenie wróciło. Kompilacja free-threaded takiej gwarancji nie daje i gubi ponad połowę przyrostów, za każdym uruchomieniem inną liczbę. Kod poprawny tylko dzięki GIL jest kodem błędnym.

## Blokada `Lock` i instrukcja `with`

**Blokada** (ang. *lock*) dopuszcza do chronionego fragmentu kodu jeden wątek naraz: `acquire()` zajmuje blokadę — a jeśli trzyma ją inny wątek, czeka na jej zwolnienie — `release()` ją oddaje. Blokada jest menedżerem kontekstu, co zapowiedzieliśmy w rozdziale [11. Model danych](../11-model-danych/menedzery-kontekstu.md#zapowiedz-blokady): instrukcja `with` zajmuje ją na wejściu i zwalnia na wyjściu, także gdy blok zakończy wyjątek:

```python title="blokada.py"
import sys
import threading
import time


class Licznik:
    def __init__(self):
        self.wartosc = 0
        self.blokada = threading.Lock()

    def zwieksz(self):
        with self.blokada:
            odczyt = self.wartosc
            time.sleep(0.1)
            self.wartosc = odczyt + 1

    def zwiekszaj(self, ile):
        for _ in range(ile):
            with self.blokada:
                self.wartosc += 1


licznik = Licznik()
watki = [threading.Thread(target=licznik.zwieksz) for _ in range(2)]
watki += [threading.Thread(target=licznik.zwiekszaj, args=(250_000,)) for _ in range(4)]
for watek in watki:
    watek.start()
for watek in watki:
    watek.join()
print(f"oczekiwane 1000002, otrzymane {licznik.wartosc} (GIL włączony: {sys._is_gil_enabled()})")
```

```{ .text .no-copy }
oczekiwane 1000002, otrzymane 1000002 (GIL włączony: True)
```

Ten sam wynik daje uruchomienie w kompilacji free-threaded. Fragment między zajęciem a zwolnieniem blokady nazywamy **sekcją krytyczną** (ang. *critical section*); powinna być jak najkrótsza, bo wątki czekające na blokadę nie pracują. Opóźnienie w `zwieksz()` pozostaje wewnątrz sekcji celowo: zastępuje pracę, która musi zajść między odczytem a zapisem, i nie może zostać wyłączona spod blokady. Blokada chroni dane tylko wtedy, gdy **każdy** dostęp do nich przechodzi przez nią — stąd blokada jako atrybut instancji, obok danych, które chroni. Wywołanie `acquire(timeout=1)` rezygnuje z czekania po sekundzie i zwraca `False`; przyda się w następnych sekcjach.

## Blokada wielokrotna `RLock`

Zwykła blokada nie pamięta, kto ją trzyma: wątek, który zajął `Lock` i spróbuje zająć go ponownie, zablokuje sam siebie. **Blokada wielokrotna** `RLock` (ang. *reentrant lock*) pozwala temu samemu wątkowi zająć ją wiele razy i zwalnia się po tylu samo wywołaniach `release()`:

```{ .python .no-copy }
>>> import threading
>>> blokada = threading.Lock()
>>> blokada.acquire()
True
>>> blokada.acquire(timeout=0.5)
False
>>> wielokrotna = threading.RLock()
>>> with wielokrotna:
...     with wielokrotna:
...         print("ten sam wątek dwa razy")
...
ten sam wątek dwa razy
```

Typowy przypadek to metoda chroniona blokadą, która wywołuje inną metodę tej samej klasy chronioną tą samą blokadą; ze zwykłym `Lock` drugie wywołanie czekałoby w nieskończoność.

## Zakleszczenie

Dwie blokady zajmowane w różnej kolejności prowadzą do **zakleszczenia** (ang. *deadlock*): pierwszy wątek trzyma A i czeka na B, drugi trzyma B i czeka na A — i żaden nie ustąpi. Z limitem czasu w `acquire()` program nie zawiesza się, a wynik pokazuje mechanizm:

```python title="zakleszczenie.py"
import threading
import time

blokada_a = threading.Lock()
blokada_b = threading.Lock()


def pierwszy():
    with blokada_a:
        time.sleep(0.1)
        dostal = blokada_b.acquire(timeout=1)
        print("pierwszy: mam A, dostałem B:", dostal)
        if dostal:
            blokada_b.release()


def drugi():
    with blokada_b:
        time.sleep(0.1)
        dostal = blokada_a.acquire(timeout=2)
        print("drugi: mam B, dostałem A:", dostal)
        if dostal:
            blokada_a.release()


watki = [threading.Thread(target=pierwszy), threading.Thread(target=drugi)]
for watek in watki:
    watek.start()
for watek in watki:
    watek.join()
```

```{ .text .no-copy }
pierwszy: mam A, dostałem B: False
drugi: mam B, dostałem A: True
```

Po sekundzie pierwszy wątek rezygnuje i zwalnia A, dzięki czemu drugi — czekający do dwóch sekund — dostaje A i kończy poprawnie. Bez limitów oba wątki czekałyby wiecznie, a program trzeba by przerwać z zewnątrz. Zasada, która zakleszczeniom zapobiega: wszystkie wątki zajmują blokady **w tej samej kolejności** — a najlepiej, gdy wystarcza jedna blokada. Limit czasu jest zabezpieczeniem, nie rozwiązaniem: program musi wiedzieć, co zrobić po `False`.

## Kolejka `queue.Queue` — producent i konsument

Zamiast chronić wspólne dane blokadą, wątki mogą przekazywać sobie dane przez **kolejkę**: jeden wkłada zadania, drugi je wyjmuje, a synchronizację zapewnia sama kolejka. Metoda `get()` czeka, aż w kolejce pojawi się element; `shutdown()` zamyka kolejkę, a czekający konsument otrzymuje wyjątek `ShutDown`:

```python title="kolejka.py"
import queue
import threading
import time

kolejka = queue.Queue()


def producent():
    for numer in range(1, 4):
        time.sleep(0.1)
        print(f"producent: dodaję zadanie {numer}")
        kolejka.put(f"zadanie {numer}")
    kolejka.shutdown()


def konsument():
    try:
        while True:
            zadanie = kolejka.get()
            print(f"konsument: przetwarzam {zadanie}")
            kolejka.task_done()
    except queue.ShutDown:
        print("konsument: kolejka zamknięta")


watki = [threading.Thread(target=producent), threading.Thread(target=konsument)]
for watek in watki:
    watek.start()
for watek in watki:
    watek.join()
```

```{ .text .no-copy }
producent: dodaję zadanie 1
konsument: przetwarzam zadanie 1
producent: dodaję zadanie 2
konsument: przetwarzam zadanie 2
producent: dodaję zadanie 3
konsument: przetwarzam zadanie 3
konsument: kolejka zamknięta
```

`Queue` jest bezpieczna wątkowo — jej metody mają wbudowaną blokadę — więc wątki nie odwołują się do wspólnych struktur bezpośrednio. Wzorzec **producent–konsument** (ang. *producer–consumer*) skaluje się bez zmian: wielu producentów i wielu konsumentów korzysta z tej samej kolejki. Argument `maxsize=` ogranicza jej długość, a wtedy `put()` czeka, gdy konsumenci nie nadążają; `task_done()` w parze z `kolejka.join()` pozwala poczekać na przetworzenie wszystkich zadań. Metoda `shutdown()` istnieje od Pythona 3.13 — w starszym kodzie tę rolę pełni specjalna wartość wkładana na koniec, na przykład `None`. Zasada ogólna: lepiej przekazywać dane niż dzielić je, bo kod bez wspólnego stanu nie ma wyścigów.

## Wątki a interfejs graficzny

Biblioteki okienkowe prowadzą pętlę zdarzeń w jednym wątku i nie gwarantują bezpiecznego zmieniania elementów okna z innych wątków. Długie obliczenie wykonujemy więc w osobnym wątku, wynik przekazujemy przez kolejkę, a wątek okna odpytuje ją co kilkadziesiąt milisekund za pomocą zegara biblioteki — w tkinter jest to metoda `after()`. Do tego wzorca wracamy przy interfejsach graficznych w części „Python Zastosowania”. <!-- TODO: link po powstaniu rozdziału o tkinter -->

## Inne narzędzia — `Semaphore`, `Condition`, `Barrier`, `Timer` (dla dociekliwych)

| Narzędzie | Działanie | Typowe użycie |
|---|---|---|
| `Semaphore(n)` | wpuszcza do sekcji najwyżej `n` wątków naraz | ograniczenie liczby równoczesnych połączeń |
| `Event` | flaga z poprzedniego podrozdziału; `clear()` ją zeruje | sygnał zatrzymania, „dane gotowe” |
| `Condition` | blokada z metodami `wait()` i `notify()` | czekanie, aż inny wątek zmieni stan |
| `Barrier(n)` | zatrzymuje wątki, aż zbierze się `n` | synchronizacja faz obliczeń |
| `Timer(czas, funkcja)` | wątek, który po odczekaniu wywołuje funkcję | jednorazowe opóźnione działanie |

W większości programów wystarczają `Lock`, `Event` i `Queue`; pozostałe narzędzia opisuje dokumentacja modułu `threading`.
