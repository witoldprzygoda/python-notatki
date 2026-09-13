# Instrukcja with i menedżery kontekstu

Klauzula `finally` z pierwszego podrozdziału rozwiązuje problem sprzątania: kod w niej umieszczony wykonuje się niezależnie od tego, czy wystąpił wyjątek. Problem ten jest tak częsty — każdy otwarty plik trzeba zamknąć, każdą zajętą blokadę zwolnić, każdy rozpoczęty pomiar zakończyć — że Python ma dla niego osobną składnię: instrukcję `with`, spotkaną już przy `pytest.raises()`. W tym podrozdziale wychodzimy od zapisu z `try`/`finally`, zastępujemy go instrukcją `with`, wyjaśniamy, co ta instrukcja robi, i piszemy własne **menedżery kontekstu** (ang. *context manager*) za pomocą funkcji generatorowej z rozdziału 6. Na koniec, dla dociekliwych, przeglądamy narzędzia modułu `contextlib`.

## Problem zwalniania zasobów

**Zasób** (ang. *resource*) to element systemu lub obiekt, który program zajmuje na czas pracy i musi zwolnić: otwarty plik, połączenie sieciowe, blokada, katalog roboczy, rozpoczęty pomiar. Najprostszym zasobem jest plik. Funkcja wbudowana `open()` otwiera plik i zwraca **obiekt pliku**, po którego wierszach można iterować pętlą `for` albo wczytać całość metodą `read()`; pełne omówienie plików, trybów otwarcia i kodowań znajduje się w podrozdziale [Pliki tekstowe](../09-wejscie-wyjscie/pliki-tekstowe.md) rozdziału 9, a tutaj `open()` służy wyłącznie za przykład zasobu i zawsze otrzymuje argument `encoding="utf-8"`. W katalogu programu umieszczamy plik z trzema liczbami:

```text title="dane.txt"
12
7
23
```

Otwarty plik zajmuje zasób systemu operacyjnego, dlatego po użyciu należy go zamknąć metodą `close()`. Gdyby jednak `int()` zgłosił wyjątek przy którymś wierszu, instrukcja `close()` zapisana za pętlą nigdy by się nie wykonała. W krótkim skrypcie uchodzi to uwadze, bo interpreter zamyka pliki przy zakończeniu programu, ale w programie działającym dłużej każdy niezamknięty plik zajmuje zasób systemu, a ich liczba jest ograniczona. Zapis z `try`/`finally` gwarantuje zamknięcie w obu przypadkach:

```python title="bez-with.py"
plik = open("dane.txt", encoding="utf-8")
try:
    liczby = [int(wiersz) for wiersz in plik]
finally:
    plik.close()
print(sum(liczby), plik.closed)
```

```{ .text .no-copy }
42 True
```

Atrybut `closed` obiektu pliku potwierdza zamknięcie. Wiersze odczytane z pliku zawierają na końcu znak nowego wiersza, który `int()` pomija tak samo jak spacje. Zapis działa, ale ma dwie wady: otwarcie i zamknięcie zasobu są od siebie oddalone, a schemat „zajmij, `try`, użyj, `finally`, zwolnij” trzeba powtarzać przy każdym zasobie.

## Instrukcja `with`

Instrukcja `with` zapisuje ten schemat w jednej konstrukcji: wyrażenie po `with` zajmuje zasób, nazwa po `as` otrzymuje obiekt, z którym pracujemy w bloku, a po wyjściu z bloku — zwykłym, przez `return`, przez `break` albo przez wyjątek — zasób jest zwalniany automatycznie:

```python title="z-with.py"
with open("dane.txt", encoding="utf-8") as plik:
    liczby = [int(wiersz) for wiersz in plik]
print(sum(liczby), plik.closed)
```

```{ .text .no-copy }
42 True
```

Blok `with` odpowiada blokowi `try` z poprzedniego zapisu, a zamknięcie pliku zostało wbudowane w instrukcję. Nazwa `plik` pozostaje związana po bloku — wskazuje zamknięty obiekt pliku — dlatego można sprawdzić `plik.closed`. Gwarancja obejmuje także wyjątki zgłoszone w bloku:

```python title="z-with-wyjatek.py"
try:
    with open("dane.txt", encoding="utf-8") as plik:
        liczby = [int(wiersz) for wiersz in plik]
        print(liczby[10])
except IndexError:
    print("za mało danych; plik zamknięty:", plik.closed)
```

```{ .text .no-copy }
za mało danych; plik zamknięty: True
```

Wyjątek `IndexError` opuścił blok `with`, plik został zamknięty, a dopiero potem wyjątek dotarł do klauzuli `except` na zewnątrz. Instrukcja `with` nie przechwytuje wyjątków — zwalnia zasób i przepuszcza je dalej. Nie obejmuje też samego zajęcia zasobu: gdy `open()` zawodzi, blok `with` w ogóle się nie rozpoczyna i nie ma czego zwalniać:

```python title="brak-pliku.py"
with open("brak.txt", encoding="utf-8") as plik:
    print(plik.read())
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "brak-pliku.py", line 1, in <module>
    with open("brak.txt", encoding="utf-8") as plik:
         ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'brak.txt'
```

Wyjątek z `open()` obsługujemy, jeśli trzeba, instrukcją `try` obejmującą całą instrukcję `with`, jak w poprzednim przykładzie. Od tej chwili każde `open()` w książce występuje w instrukcji `with`; zapis z `try`/`finally` pokazaliśmy tylko po to, by było jasne, co `with` zastępuje.

### Kilka zasobów w jednej instrukcji

Jedna instrukcja `with` może zajmować kilka zasobów, rozdzielonych przecinkami; od Pythona 3.10 listę można ująć w nawiasy i rozpisać w kilku wierszach, co przy dłuższych wyrażeniach jest czytelniejsze:

```text title="progi.txt"
10
20
```

```python title="dwa-pliki.py"
with (
    open("dane.txt", encoding="utf-8") as dane,
    open("progi.txt", encoding="utf-8") as progi,
):
    liczby = [int(wiersz) for wiersz in dane]
    granice = [int(wiersz) for wiersz in progi]
print([x for x in liczby if x > max(granice)])
print(dane.closed, progi.closed)
```

```{ .text .no-copy }
[23]
True True
```

Zasoby są zajmowane w kolejności zapisu, a zwalniane w kolejności odwrotnej — najpierw `progi`, potem `dane` — tak jak przy zagnieżdżonych instrukcjach `with`, których zapis z przecinkami jest skrótem. Jeżeli zajęcie drugiego zasobu zawiedzie, pierwszy zostaje zwolniony.

## Protokół menedżera kontekstu

Instrukcja `with` nie jest związana z plikami. Działa z każdym obiektem, który udostępnia dwie metody o ustalonych nazwach: `__enter__()`, wywoływaną na początku, i `__exit__()`, wywoływaną na końcu. Taki obiekt nazywamy menedżerem kontekstu, a umowę co do nazw i zachowania metod — **protokołem menedżera kontekstu** (ang. *context manager protocol*). Podobnie pętla `for` z rozdziału 4 współpracuje z każdym obiektem iterowalnym, nie tylko z listą, bo opiera się na umowie co do metod, a nie na konkretnym typie. Wykonanie instrukcji `with wyrażenie as nazwa:` przebiega w czterech krokach:

1. Interpreter oblicza wyrażenie i otrzymuje menedżer kontekstu.
2. Wywołuje jego metodę `__enter__()`; jej wynik wiąże z nazwą po `as` (obiekt pliku zwraca z `__enter__()` samego siebie).
3. Wykonuje blok.
4. Wywołuje metodę `__exit__()` — zawsze, także gdy blok opuścił wyjątek; metoda otrzymuje wtedy informację o wyjątku i może go stłumić, lecz obiekt pliku tego nie robi: zamyka plik i przepuszcza wyjątek dalej.

Menedżerami kontekstu są obiekty plików, obiekt zwracany przez `pytest.raises()` z poprzedniego podrozdziału (jego `__exit__()` sprawdza, czy blok zgłosił oczekiwany wyjątek, i właśnie ten wyjątek tłumi), blokady w programach wielowątkowych i wiele innych obiektów biblioteki standardowej. Metody o nazwach z podwójnymi podkreśleniami definiuje się we własnych klasach; napiszemy taki menedżer po wprowadzeniu klas, w rozdziale o modelu danych. <!-- TODO: link po powstaniu rozdziału o modelu danych --> Prostszą drogę do własnego menedżera kontekstu — bez klasy — daje moduł `contextlib`.

## Dekorator `contextlib.contextmanager`

Dekorator `contextlib.contextmanager` zamienia funkcję generatorową z podrozdziału [Funkcje generatorowe](../06-funkcje/funkcje-generatorowe.md) w fabrykę menedżerów kontekstu. Funkcja musi zawierać dokładnie jedną instrukcję `yield`: kod przed nią wykonuje się jako `__enter__()`, wartość podana w `yield` trafia do nazwy po `as`, a kod po `yield` wykonuje się jako `__exit__()`. Ponieważ wyjątek z bloku `with` jest zgłaszany wewnątrz funkcji generatorowej w miejscu `yield`, kod zwalniający zasób umieszczamy w klauzuli `finally`. Symulowany zasób, który wypisuje, kiedy jest zajmowany i zwalniany, zapisujemy w module `zasoby.py`, aby korzystać z niego w dalszych przykładach:

```python title="zasoby.py"
"""Udostępnia symulowane zasoby do demonstracji instrukcji with."""

from contextlib import contextmanager


@contextmanager
def zasob(nazwa):
    """Udostępnia symulowany zasób o podanej nazwie i zwalnia go po użyciu."""
    print("zajmuję", nazwa)
    try:
        yield nazwa.upper()
    finally:
        print("zwalniam", nazwa)
```

```python title="uzycie-zasobu.py"
from zasoby import zasob

with zasob("a") as x:
    print("pracuję z", x)

with zasob("a") as x, zasob("b") as y:
    print("pracuję z", x, "i", y)
```

```{ .text .no-copy }
zajmuję a
pracuję z A
zwalniam a
zajmuję a
zajmuję b
pracuję z A i B
zwalniam b
zwalniam a
```

Wywołanie `zasob("a")` nie wykonuje jeszcze ciała funkcji — jak każde wywołanie funkcji generatorowej zwraca obiekt, tu opakowany przez dekorator w menedżer kontekstu. Dopiero `__enter__()` uruchamia ciało do pierwszego `yield`, a `__exit__()` wznawia je po `yield`. Kolejność zwalniania przy dwóch zasobach jest odwrotna do kolejności zajmowania, dokładnie jak przy dwóch plikach.

Drugi menedżer mierzy czas wykonania bloku. Funkcja `time.perf_counter()` z modułu `time` zwraca odczyt zegara o wysokiej rozdzielczości, przeznaczonego do mierzenia odstępów czasu — różnica dwóch odczytów to czas w sekundach; szczegółowe omówienie pomiarów czasu i profilowania znajdzie się w rozdziale o wydajności. <!-- TODO: link po powstaniu rozdziału o wydajności --> Menedżer nie udostępnia żadnego obiektu, więc `yield` stoi bez wartości, a instrukcja `with` bez `as`:

```python title="stoper.py"
import time
from contextlib import contextmanager


@contextmanager
def stoper(nazwa):
    """Mierzy czas wykonania bloku with i wypisuje go po zakończeniu."""
    start = time.perf_counter()
    try:
        yield
    finally:
        czas = time.perf_counter() - start
        print(f"{nazwa}: {czas:.3f} s")


with stoper("sortowanie"):
    posortowane = sorted(range(1_000_000, 0, -1))
print(posortowane[:3])
```

```{ .text .no-copy }
sortowanie: 0.035 s
[1, 2, 3]
```

Zmierzony czas zależy od komputera. Menedżer `stoper()` zastępuje dekorator mierzący czas, który moglibyśmy napisać technikami z rozdziału 6, i ma nad nim przewagę: mierzy dowolny fragment kodu, nie tylko całą funkcję.

### Wyjątek wewnątrz bloku `with`

Klauzula `finally` w funkcji generatorowej jest konieczna. Gdy blok `with` zgłosi wyjątek, interpreter przekazuje go do wstrzymanej funkcji generatorowej — tak jakby zgłosiła go instrukcja `yield` — więc kod po `yield` bez `finally` w ogóle by się nie wykonał:

```python title="zasob-wyjatek.py"
from zasoby import zasob

with zasob("c") as x:
    print(1 / 0)
print("po bloku")
```

```{ .text .no-copy }
zajmuję c
zwalniam c
Traceback (most recent call last):
  File "zasob-wyjatek.py", line 4, in <module>
    print(1 / 0)
          ~~^~~
ZeroDivisionError: division by zero
```

Zasób został zwolniony, a wyjątek propagował dalej i przerwał program przed `print("po bloku")` — dokładnie tak, jak przy obiekcie pliku. Gdyby funkcja generatorowa przechwyciła wyjątek klauzulą `except` i nie zgłosiła go ponownie, menedżer stłumiłby go, a program wykonałby `print("po bloku")`; z tej możliwości korzysta `pytest.raises()`, ale w menedżerach zwalniających zasoby jej nie używamy. Menedżer utworzony z funkcji generatorowej jest jednorazowy z założenia: obiektu zwróconego przez `zasob("a")` można użyć tylko w jednej instrukcji `with`, a drugie użycie tego samego obiektu kończy się błędem — dlatego wyrażenie tworzące menedżer zapisujemy bezpośrednio w instrukcji `with`, a nie w nazwie używanej wielokrotnie.

## Narzędzia modułu `contextlib` (dla dociekliwych)

Moduł `contextlib` zawiera kilka gotowych menedżerów kontekstu do typowych sytuacji. `suppress(typ)` tłumi wyjątki podanego typu zgłoszone w bloku — jest jawną formą uciszenia wyjątku, o której była mowa przy antywzorcach: typ jest nazwany, a intencja widoczna w jednym wierszu. Program poniżej wczytuje plik z ustawieniami, jeśli istnieje, a jego brak traktuje jako sytuację zwyczajną:

```python title="suppress.py"
from contextlib import suppress

ustawienia = "domyślne"
with suppress(FileNotFoundError):
    with open("ustawienia.txt", encoding="utf-8") as plik:
        ustawienia = plik.read().strip()
print("ustawienia:", ustawienia)
```

```{ .text .no-copy }
ustawienia: domyślne
```

`nullcontext()` jest menedżerem, który nie robi nic — przydaje się, gdy zasób jest potrzebny tylko pod pewnym warunkiem, a instrukcja `with` ma pozostać jedna:

```python title="nullcontext.py"
from contextlib import nullcontext

from zasoby import zasob


def przetworz(dane, z_zasobem):
    """Sumuje dane, zajmując symulowany zasób tylko na życzenie."""
    kontekst = zasob("bufor") if z_zasobem else nullcontext()
    with kontekst:
        return sum(dane)


print(przetworz([1, 2, 3], z_zasobem=True))
print(przetworz([1, 2, 3], z_zasobem=False))
```

```{ .text .no-copy }
zajmuję bufor
zwalniam bufor
6
6
```

`ExitStack` obsługuje zmienną liczbę zasobów — na przykład listę plików o nieznanej z góry długości — których nie da się wypisać w nagłówku `with`. Metoda `enter_context()` zajmuje zasób i dopisuje go do stosu, a wyjście z bloku zwalnia wszystkie w kolejności odwrotnej:

```python title="exitstack.py"
from contextlib import ExitStack

from zasoby import zasob

nazwy = ["a", "b", "c"]
with ExitStack() as stos:
    zasoby = [stos.enter_context(zasob(nazwa)) for nazwa in nazwy]
    print("pracuję z", zasoby)
```

```{ .text .no-copy }
zajmuję a
zajmuję b
zajmuję c
pracuję z ['A', 'B', 'C']
zwalniam c
zwalniam b
zwalniam a
```

Moduł zawiera ponadto `chdir()` (od Pythona 3.11), tymczasowo zmieniający katalog roboczy, oraz `redirect_stdout()`, kierujący wyjście `print()` do innego obiektu; oba wracają w rozdziale 9: `chdir()` w podrozdziale [Ścieżki i system plików](../09-wejscie-wyjscie/pathlib.md#moduy-os-shutil-i-tempfile), a `redirect_stdout()` w podrozdziale [Funkcja print i strumienie](../09-wejscie-wyjscie/print-i-strumienie.md#argument-file-wyjscie-do-pliku-i-redirect_stdout). Dokumentacja modułu `contextlib` zawiera pełną listę wraz z przykładami.

Instrukcja `with` zamyka część rozdziału poświęconą składni. Dwa ostatnie podrozdziały dotyczą warsztatu: jak czytać i zapisywać ślady wywołań, jak zatrzymać program w wybranym miejscu i obejrzeć jego stan pod debuggerem oraz jak zastąpić `print()` dziennikiem rejestrującym, kiedy i gdzie zaszło zdarzenie.
