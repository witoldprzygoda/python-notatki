# Dekoratory

Dekorator łączy pojęcia wprowadzone w tym rozdziale: funkcja jest obiektem (strona [Definiowanie funkcji](definiowanie-funkcji.md#funkcja-jako-obiekt)), można ją przekazać innej funkcji i zwrócić z funkcji, a funkcja zagnieżdżona zachowuje wiązania zmiennych wolnych z funkcji otaczającej jako domknięcie. **Dekorator** (ang. *decorator*) to funkcja, która przyjmuje funkcję i zwraca w jej miejsce inną funkcję — zwykle domknięcie wywołujące funkcję pierwotną i wykonujące dodatkowe działania przed nią lub po niej. Zapis z symbolem `@` nad definicją jest jedynie skrótem dla przypisania wyniku dekoratora nazwie funkcji. Na tej stronie przechodzimy tę drogę krok po kroku, bez nowych mechanizmów języka, tak by składnia `@` nie była niczym więcej niż wygodnym zapisem operacji, którą umiemy wykonać ręcznie.

## Od funkcji do dekoratora

### Funkcja przyjmująca i zwracająca funkcję

Na stronie [Funkcje jako obiekty](funkcje-jako-obiekty.md#funkcje-pierwszej-klasy) przekazywaliśmy funkcje jako argumenty, a na stronie [Zasięg nazw i domknięcia](zasieg-nazw-i-domkniecia.md#domkniecia) zwracaliśmy je jako wyniki. Najprostsza funkcja przyjmująca funkcję wywołuje ją z podanym argumentem; najprostsza funkcja zwracająca funkcję oddaje otrzymany obiekt bez zmian:

```python title="wykonaj.py"
def wykonaj(funkcja, imie):
    """Zwraca wynik wywołania funkcji dla podanego imienia."""
    return funkcja(imie)


def bez_zmian(funkcja):
    """Zwraca otrzymaną funkcję bez zmian."""
    return funkcja


def powitanie(imie):
    """Zwraca powitanie dla podanego imienia."""
    return f"Witaj, {imie}!"


print(wykonaj(powitanie, "Ola"))
print(wykonaj(str.upper, "Ola"))
to_samo = bez_zmian(powitanie)
print(to_samo is powitanie)
print(to_samo("Ala"))
```

```{ .text .no-copy }
Witaj, Ola!
OLA
True
Witaj, Ala!
```

Funkcja `bez_zmian()` jest już, formalnie, dekoratorem: przyjmuje funkcję i zwraca funkcję, jest więc funkcją wyższego rzędu w rozumieniu strony [Funkcje jako obiekty](funkcje-jako-obiekty.md#funkcje-pierwszej-klasy), łączącą obie wymienione tam cechy. Nie wnosi niczego użytecznego, ale pokazuje kontrakt, który spełnia każdy dekorator — argumentem jest obiekt funkcji, wynikiem obiekt, który zostaje związany z jej nazwą: zwykle funkcja lub inny obiekt wywoływalny.

### Ręczne opakowanie

Pożyteczny dekorator zwraca nową funkcję, zbudowaną wokół otrzymanej. Funkcja `z_ramka()` tworzy funkcję zagnieżdżoną `opakowana()`, która wypisuje ramkę, wywołuje funkcję pierwotną i przekazuje dalej jej wynik. Zwrócona funkcja jest domknięciem: parametr `funkcja` pozostaje dla niej dostępny jako zmienna wolna (sekcja [Funkcje zagnieżdżone i zmienne wolne](zasieg-nazw-i-domkniecia.md#funkcje-zagniezdzone-i-zmienne-wolne)) po zakończeniu wywołania `z_ramka()`. Funkcję zagnieżdżoną, która wywołuje inną funkcję, dodając działania przed nią lub po niej, nazywamy **funkcją opakowującą** (ang. *wrapper*); w kodzie tej książki nosi ona nazwę `opakowana`, a gdy w jednym skrypcie jest ich kilka — nazwę z przyrostkiem, np. `opakowana_a`. Na razie stosujemy dekorator ręcznie, przypisując jego wynik nazwie funkcji pierwotnej:

```python title="z-ramka-recznie.py"
def z_ramka(funkcja):
    """Zwraca funkcję opakowującą, która wypisuje ramkę wokół wywołania."""
    def opakowana():
        print("---")
        wynik = funkcja()
        print("---")
        return wynik

    return opakowana


def powitanie():
    print("Witaj!")
    return "gotowe"


powitanie = z_ramka(powitanie)
print(powitanie())
print(powitanie)
```

```{ .text .no-copy }
---
Witaj!
---
gotowe
<function z_ramka.<locals>.opakowana at 0x...>
```

Po przypisaniu `powitanie = z_ramka(powitanie)` nazwa `powitanie` nie wskazuje już na funkcję z definicji, lecz na obiekt `opakowana` utworzony wewnątrz `z_ramka()` — pokazuje to reprezentacja obiektu ze znanym ze strony o domknięciach zapisem `z_ramka.<locals>.opakowana`. Pierwotna funkcja nie zniknęła: obiekt opakowujący przechowuje do niej referencję w zmiennej wolnej `funkcja` i wywołuje ją przy każdym wywołaniu `powitanie()`. Wartość `"gotowe"` przechodzi przez funkcję opakowującą dzięki instrukcji `return wynik`.

### Składnia @

Przypisanie `powitanie = z_ramka(powitanie)` po definicji ma wadę: informacja o opakowaniu funkcji stoi z dala od jej nagłówka, a przy dłuższym ciele łatwo ją przeoczyć. Python pozwala zapisać to samo wierszem `@z_ramka` bezpośrednio nad instrukcją `def`:

```python title="z-ramka-dekorator.py"
def z_ramka(funkcja):
    """Zwraca funkcję opakowującą, która wypisuje ramkę wokół wywołania."""
    def opakowana():
        print("---")
        wynik = funkcja()
        print("---")
        return wynik

    return opakowana


@z_ramka
def powitanie():
    print("Witaj!")
    return "gotowe"


print(powitanie())
```

```{ .text .no-copy }
---
Witaj!
---
gotowe
```

Oba skrypty działają identycznie. Zgodnie z dokumentacją języka definicja

```{ .python .no-copy }
@z_ramka
def powitanie():
    ...
```

jest w zasadzie równoważna zapisowi

```{ .python .no-copy }
def powitanie():
    ...


powitanie = z_ramka(powitanie)
```

z jedną różnicą: w zapisie z `@` pierwotna funkcja nie zostaje nawet na chwilę związana z nazwą `powitanie`. Instrukcja `def` jest — jak ustaliliśmy na stronie [Definiowanie funkcji](definiowanie-funkcji.md#anatomia-definicji-i-wywoania) — instrukcją wykonywalną, która tworzy obiekt funkcji i wiąże go z nazwą; z dekoratorem interpreter tworzy obiekt funkcji, przekazuje go dekoratorowi i dopiero wynik wiąże z nazwą. Wyrażenie po `@` jest obliczane w chwili wykonania instrukcji `def`, w zasięgu, w którym ta instrukcja stoi, a jego wartość musi być obiektem wywoływalnym. Składnia dekoratora, wprowadzona przez [PEP 318](https://peps.python.org/pep-0318/) w Pythonie 2.4, jest więc elementem gramatyki definicji funkcji, ale cały mechanizm opiera się na zwykłych obiektach funkcji i przypisaniu: dekoratorem może być każda funkcja spełniająca kontrakt z sekcji [Funkcja przyjmująca i zwracająca funkcję](#funkcja-przyjmujaca-i-zwracajaca-funkcje), także `bez_zmian`.

!!! note "Wyrażenie po znaku @"
    Od Pythona 3.9 ([PEP 614](https://peps.python.org/pep-0614/)) po znaku `@`
    może stać dowolne wyrażenie, którego wartością jest obiekt wywoływalny —
    nie tylko nazwa lub wywołanie, jak w składni z PEP 318. Zwykle jest to
    jednak nazwa dekoratora albo jego wywołanie z argumentami, opisane
    w ostatniej sekcji tej strony.

## Funkcja opakowująca

Funkcja opakowująca z poprzedniej sekcji ma sztywną sygnaturę: nie przyjmuje argumentów, więc dekorator `z_ramka` nadaje się wyłącznie do funkcji bezargumentowych. Zastosowany do funkcji z parametrem zawodzi przy wywołaniu, bo wywołanie trafia do `opakowana()`, a nie do funkcji pierwotnej:

```python title="z-ramka-blad.py"
def z_ramka(funkcja):
    """Zwraca funkcję opakowującą, która wypisuje ramkę wokół wywołania."""
    def opakowana():
        print("---")
        wynik = funkcja()
        print("---")
        return wynik

    return opakowana


@z_ramka
def pozegnanie(imie):
    print(f"Do widzenia, {imie}!")


pozegnanie("Ola")
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "z-ramka-blad.py", line 17, in <module>
    pozegnanie("Ola")
    ~~~~~~~~~~^^^^^^^
TypeError: z_ramka.<locals>.opakowana() takes 0 positional arguments but 1 was given
```

Komunikat wskazuje funkcję `opakowana` — to ona jest teraz obiektem związanym z nazwą `pozegnanie`. Sygnatura funkcji, którą dekorator ogólnego użytku będzie opakowywał, nie jest z góry ustalona, dlatego funkcja opakowująca przyjmuje dowolne argumenty pozycyjne i nazwane przez parametry `*args` i `**kwargs` ze strony [Argumenty i parametry](argumenty-i-parametry.md#zmienna-liczba-argumentow) i przekazuje je funkcji pierwotnej w niezmienionej postaci przez rozpakowanie `*args, **kwargs`:

```python title="z-ramka-ogolna.py"
def z_ramka(funkcja):
    """Zwraca funkcję opakowującą, która wypisuje ramkę wokół wywołania."""
    def opakowana(*args, **kwargs):
        print("---")
        wynik = funkcja(*args, **kwargs)
        print("---")
        return wynik

    return opakowana


@z_ramka
def pozegnanie(imie, znak="!"):
    print(f"Do widzenia, {imie}{znak}")
    return len(imie)


print(pozegnanie("Ola"))
print(pozegnanie("Ola", znak="."))
```

```{ .text .no-copy }
---
Do widzenia, Ola!
---
3
---
Do widzenia, Ola.
---
3
```

Zapis `def opakowana(*args, **kwargs)` z instrukcją `return funkcja(*args, **kwargs)` w ciele jest wzorcem, od którego zaczyna się niemal każdy dekorator. Druga część wzorca — `return` — bywa pomijana przez początkujących. Funkcja opakowująca bez instrukcji `return` wykonuje funkcję pierwotną, ale jej wynik porzuca i, jak każda funkcja bez `return`, zwraca `None`:

```python title="bez-return.py"
def bez_return(funkcja):
    def opakowana(*args, **kwargs):
        print("wywołuję", funkcja.__name__)
        funkcja(*args, **kwargs)

    return opakowana


@bez_return
def kwadrat(x):
    return x * x


wynik = kwadrat(4)
print(wynik)
print(wynik + 1)
```

```{ .text .no-copy }
wywołuję kwadrat
None
Traceback (most recent call last):
  File "bez-return.py", line 16, in <module>
    print(wynik + 1)
          ~~~~~~^~~
TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
```

Błąd ujawnia się dopiero przy próbie użycia wyniku, często daleko od dekoratora. Poprawna funkcja opakowująca zwraca to, co zwróciła funkcja pierwotna — nawet jeśli sama nie wykonuje na tym wyniku żadnych działań. Oba elementy wzorca — przekazanie argumentów i zwrócenie wyniku — łączy dekorator rejestrujący wywołania, który wypisuje nazwę funkcji, otrzymane argumenty i wynik, a sam wynik przekazuje dalej:

```python title="rejestruj.py"
def rejestruj(funkcja):
    """Zwraca funkcję opakowującą, która wypisuje wywołanie i jego wynik."""
    def opakowana(*args, **kwargs):
        wynik = funkcja(*args, **kwargs)
        print(f"{funkcja.__name__}{args} {kwargs} -> {wynik}")
        return wynik

    return opakowana


@rejestruj
def pole(a, b=1):
    """Zwraca pole prostokąta o bokach a i b."""
    return a * b


print(pole(3, 4) + pole(5, b=2))
```

```{ .text .no-copy }
pole(3, 4) {} -> 12
pole(5,) {'b': 2} -> 10
22
```

Krotka `args` i słownik `kwargs` są wypisywane w swojej zwykłej postaci, stąd zapis `(5,)` dla jednego argumentu pozycyjnego, znany z rozdziału [5. Typy złożone](../05-typy-zlozone/krotka.md). Funkcja opakowująca wykonuje tu działania po wywołaniu funkcji pierwotnej — kolejność instrukcji wewnątrz `opakowana()` decyduje, co dzieje się przed wywołaniem, a co po nim.

## Stan w dekoratorze

Funkcja opakowująca jest domknięciem, więc może przechowywać stan między wywołaniami tak samo jak licznik z sekcji [Deklaracje global i nonlocal](zasieg-nazw-i-domkniecia.md#deklaracje-global-i-nonlocal). Dekorator `licz_wywolania` zlicza, ile razy wywołano opakowaną funkcję:

```python title="licz-wywolania.py"
def licz_wywolania(funkcja):
    """Zwraca funkcję opakowującą, która numeruje kolejne wywołania."""
    licznik = 0

    def opakowana(*args, **kwargs):
        nonlocal licznik
        licznik += 1
        print(f"Wywołanie {licznik}: {funkcja.__name__}")
        return funkcja(*args, **kwargs)

    return opakowana


@licz_wywolania
def kwadrat(x):
    return x * x


@licz_wywolania
def powitanie(imie):
    return f"Witaj, {imie}!"


print(kwadrat(3))
print(kwadrat(4))
print(powitanie("Ola"))
print(kwadrat(5))
```

```{ .text .no-copy }
Wywołanie 1: kwadrat
9
Wywołanie 2: kwadrat
16
Wywołanie 1: powitanie
Witaj, Ola!
Wywołanie 3: kwadrat
25
```

Każde zastosowanie dekoratora jest osobnym wywołaniem `licz_wywolania()`, tworzy więc osobną nazwę lokalną `licznik` i osobne domknięcie: funkcje `kwadrat` i `powitanie` mają niezależne liczniki. Deklaracja `nonlocal` jest konieczna, bo `licznik += 1` wiąże nazwę — bez niej, jak ustaliliśmy w sekcji [Nazwy lokalne](zasieg-nazw-i-domkniecia.md#nazwy-lokalne), kompilator uznałby `licznik` za nazwę lokalną funkcji opakowującej. Stan przechowywany w domknięciu nie wymaga żadnej nazwy globalnej i jest dostępny wyłącznie przez wywołania funkcji opakowującej.

## Memoizacja

Najczęstszym zastosowaniem stanu w dekoratorze jest memoizacja, zapowiedziana na stronie [Rekurencja](rekurencja.md#rekurencja-a-iteracja): zapamiętywanie wyników funkcji dla argumentów, z którymi została już wywołana. **Pamięcią podręczną** (ang. *cache*) jest słownik w domknięciu, którego kluczem jest krotka argumentów `args`, a wartością wynik. Dekorator `zapamietuj` wywołuje funkcję pierwotną tylko wtedy, gdy wyniku dla danych argumentów jeszcze nie ma:

```python title="fib-pamiec.py"
def zapamietuj(funkcja):
    """Zwraca funkcję opakowującą, która zapamiętuje wyniki dla argumentów."""
    pamiec = {}

    def opakowana(*args):
        if args not in pamiec:
            pamiec[args] = funkcja(*args)
        return pamiec[args]

    return opakowana


def utworz_fib():
    """Zwraca parę (fib, ile); ile zwraca liczbę wywołań ciała fib."""
    wywolania = 0

    @zapamietuj
    def fib(n):
        nonlocal wywolania
        wywolania += 1
        if n < 2:
            return n
        return fib(n - 1) + fib(n - 2)

    def ile():
        return wywolania

    return fib, ile


fib, ile = utworz_fib()
print(fib(30), ile())
print(fib(100), ile())
```

```{ .text .no-copy }
832040 31
354224848179261915075 101
```

Na stronie o rekurencji obliczenie `fib(30)` wymagało 2 692 537 wywołań; teraz ciało funkcji wykonuje się 31 razy — po jednym dla każdej wartości od 0 do 30 — a `fib(100)` wymaga tylko 70 kolejnych. O tym wyniku decyduje wiązanie nazwy: wewnątrz funkcji `fib` wywołania `fib(n - 1)` i `fib(n - 2)` trafiają do nazwy `fib` z przestrzeni funkcji `utworz_fib()`, a ta nazwa — od chwili zastosowania dekoratora — wskazuje na funkcję opakowującą; domknięcie zachowuje bowiem wiązanie zmiennej wolnej, a nie wartość z chwili definicji, jak ustaliliśmy w sekcji [Domknięcia](zasieg-nazw-i-domkniecia.md#domkniecia). Wywołania rekurencyjne przechodzą więc przez pamięć podręczną, a nie omijają jej. Licznik `wywolania` zlicza wyłącznie wykonania ciała funkcji pierwotnej, dlatego jest umieszczony wewnątrz niej, a nie w dekoratorze.

Ręczna memoizacja ma dwa ograniczenia. Argumenty służą za klucz słownika, muszą więc być **haszowalne** (ang. *hashable*) — mieć wyliczalną wartość skrótu, jak ustaliliśmy dla krotek w rozdziale [5. Typy złożone](../05-typy-zlozone/krotka.md). Wywołanie z listą — w konsoli otwartej po uruchomieniu skryptu poleceniem `python -i fib-pamiec.py` (opcja `-i` z podrozdziału [Pierwszy skrypt](../02-konsola/pierwszy-skrypt.md#python-bez-wchodzenia-do-konsoli-opcje-c-m-oraz-i)) — kończy się błędem `TypeError`; w CPythonie od wersji 3.14 komunikat wskazuje zarówno krotkę użytą jako klucz, jak i niehaszowalny element, wcześniej brzmiał wyłącznie `unhashable type: 'list'`:

```{ .python .no-copy }
>>> fib([1])
Traceback (most recent call last):
  File "<python-input-0>", line 1, in <module>
    fib([1])
    ~~~^^^^^
  File "fib-pamiec.py", line 6, in opakowana
    if args not in pamiec:
       ^^^^^^^^^^^^^^^^^^
TypeError: cannot use 'tuple' as a dict key (unhashable type: 'list')
```

Drugie ograniczenie: funkcja opakowująca `opakowana(*args)` obsługuje tylko argumenty pozycyjne — argumenty nazwane wymagałyby włączenia `kwargs` do klucza. To ograniczenie znoszą gotowe dekoratory `functools.cache` i `functools.lru_cache` z biblioteki standardowej, które włączają argumenty nazwane do klucza; wymóg haszowalności argumentów obowiązuje także w nich, bo pamięcią podręczną jest również słownik. Poznamy je po wprowadzeniu modułów; są standardowym sposobem memoizacji i w programach użytkowych zastępują własny dekorator. <!-- TODO: link po powstaniu rozdziału o modułach -->

!!! note "Słownik jako wartość domyślna"
    Na stronie [Argumenty i parametry](argumenty-i-parametry.md#puapka-modyfikowalnej-wartosci-domyslnej)
    zapowiedzieliśmy przypadek, w którym współdzielenie modyfikowalnej wartości
    domyślnej jest zamierzone. Jest nim właśnie pamięć podręczna: słownik
    utworzony raz, przy definicji, przechowuje wyniki między wywołaniami.

    ```python title="fib-domyslna.py"
    def fib(n, pamiec={}):
        """Zwraca n-ty wyraz ciągu Fibonacciego, zapamiętując wyniki."""
        if n < 2:
            return n
        if n not in pamiec:
            pamiec[n] = fib(n - 1) + fib(n - 2)
        return pamiec[n]


    print(fib(100))
    ```

    ```{ .text .no-copy }
    354224848179261915075
    ```

    Zapis jest zwięzły, ale miesza obliczenie z mechanizmem zapamiętywania
    i pozwala wywołującemu podać własny słownik. Dekorator rozdziela oba
    zadania i nadaje się do każdej funkcji, dlatego jest formą preferowaną.

## Metadane funkcji

Dekorowanie ma koszt, który łatwo przeoczyć. Skoro po zastosowaniu dekoratora nazwa funkcji wskazuje na obiekt `opakowana`, to atrybuty opisujące funkcję — jej **metadane** (ang. *metadata*): `__name__` i `__doc__` ze strony [Definiowanie funkcji](definiowanie-funkcji.md#funkcja-jako-obiekt) — opisują funkcję opakowującą, a nie pierwotną. Tak samo zachowuje się atrybut `__qualname__` — **nazwa kwalifikowana** (ang. *qualified name*), zawierająca ścieżkę zagnieżdżenia, którą widzieliśmy w reprezentacjach obiektów — oraz funkcja `help()`:

```python title="metadane.py"
def z_ramka(funkcja):
    """Zwraca funkcję opakowującą, która wypisuje ramkę wokół wywołania."""
    def opakowana(*args, **kwargs):
        """Wypisuje ramkę wokół wywołania."""
        print("---")
        wynik = funkcja(*args, **kwargs)
        print("---")
        return wynik

    return opakowana


@z_ramka
def powitanie(imie):
    """Zwraca powitanie dla podanego imienia."""
    return f"Witaj, {imie}!"


print(powitanie.__name__)
print(powitanie.__qualname__)
print(powitanie.__doc__)
help(powitanie)
```

```{ .text .no-copy }
opakowana
z_ramka.<locals>.opakowana
Wypisuje ramkę wokół wywołania.
Help on function opakowana in module __main__:

opakowana(*args, **kwargs)
    Wypisuje ramkę wokół wywołania.

```

Dla czytelnika dokumentacji, dla narzędzi analizy kodu i dla śladów wywołań funkcja `powitanie` stała się funkcją `opakowana` o sygnaturze `(*args, **kwargs)` — docstring pierwotnej funkcji i informacja o jej parametrze zostały utracone. Atrybuty `__name__` i `__doc__` można przypisywać, więc nasuwa się pomysł, by skopiować je ręcznie do funkcji opakowującej; nie jest to jednak rozwiązanie właściwe, bo metadanych jest więcej. Biblioteka standardowa dostarcza `functools.wraps` — dekorator z argumentem, stosowany wewnątrz dekoratora jako `@functools.wraps(funkcja)` nad funkcją opakowującą, w sposób opisany w ostatniej sekcji tej strony. W Pythonie 3.14 przenosi on między innymi nazwę, nazwę kwalifikowaną, docstring, nazwę modułu i adnotacje — te ostatnie w leniwej postaci wprowadzonej w tej wersji — oraz zapisuje referencję do funkcji pierwotnej w atrybucie `__wrapped__`. Wrócimy do niego po wprowadzeniu modułów i od tamtej chwili każdy dekorator w książce będzie z niego korzystał; na tej stronie, gdzie nie używamy jeszcze importów, pozostajemy przy prostej funkcji opakowującej. <!-- TODO: link po powstaniu rozdziału o modułach -->

## Dekoratory z argumentami i składanie dekoratorów

Dekorator otrzymuje dokładnie jeden argument — funkcję. Gdy działanie dekoratora ma zależeć od dodatkowej wartości, np. od liczby powtórzeń, potrzebna jest funkcja, która tę wartość przyjmie i **zwróci dekorator**. Funkcja `powtorz(ile)` jest **fabryką dekoratorów**, analogiczną do fabryki funkcji `mnoznik(przez)` z sekcji [Domknięcia](zasieg-nazw-i-domkniecia.md#domkniecia):

```python title="powtorz.py"
def powtorz(ile):
    """Zwraca dekorator powtarzający wywołanie funkcji ile razy."""
    def dekorator(funkcja):
        def opakowana(*args, **kwargs):
            wynik = None
            for _ in range(ile):
                wynik = funkcja(*args, **kwargs)
            return wynik

        return opakowana

    return dekorator


@powtorz(3)
def powiedz(tekst):
    print(tekst)
    return len(tekst)


print(powiedz("Hej"))
```

```{ .text .no-copy }
Hej
Hej
Hej
3
```

W zapisie `@powtorz(3)` po znaku `@` stoi wywołanie, a nie nazwa. Interpreter oblicza je najpierw: wynikiem jest funkcja `dekorator`, dopiero ona zostaje zastosowana do `powiedz`. Zapis jest równoważny przypisaniu `powiedz = powtorz(3)(powiedz)`. Trzy poziomy zagnieżdżenia odpowiadają trzem momentom:

```{ .text .no-copy }
powtorz(3)            →  zwraca dekorator (ile = 3 w domknięciu)
dekorator(powiedz)    →  zwraca funkcję opakowującą (funkcja = powiedz)
opakowana("Hej")      →  wykonuje powiedz("Hej") trzykrotnie i zwraca wynik
```

Wartość `ile` jest zmienną wolną funkcji opakowującej, tak jak `funkcja`: obie pochodzą z otaczających wywołań i pozostają dostępne po ich zakończeniu.

Nad jedną definicją może stać kilka dekoratorów. Dokumentacja języka określa, że są one stosowane w sposób zagnieżdżony — zapis z dwoma dekoratorami jest w zasadzie równoważny przypisaniu `f = a(b(f))`. Dekorator napisany bezpośrednio nad `def` jest stosowany jako pierwszy, a jego wynik trafia do dekoratora stojącego wyżej. Kolejność wykonywania funkcji opakowujących przy późniejszym wywołaniu jest odwrotna, bo wywołanie trafia najpierw do najbardziej zewnętrznej z nich:

```python title="skladanie.py"
def a(funkcja):
    print("stosuję a")

    def opakowana_a(*args, **kwargs):
        print("a: przed")
        wynik = funkcja(*args, **kwargs)
        print("a: po")
        return wynik

    return opakowana_a


def b(funkcja):
    print("stosuję b")

    def opakowana_b(*args, **kwargs):
        print("b: przed")
        wynik = funkcja(*args, **kwargs)
        print("b: po")
        return wynik

    return opakowana_b


@a
@b
def f():
    print("f: właściwa funkcja")


print("--- wywołanie")
f()
```

```{ .text .no-copy }
stosuję b
stosuję a
--- wywołanie
a: przed
b: przed
f: właściwa funkcja
b: po
a: po
```

Dwa porządki trzeba rozróżniać. Podczas wykonywania instrukcji `def` dekoratory są stosowane od dołu do góry: najpierw `b` opakowuje `f`, potem `a` opakowuje wynik — stąd komunikaty „stosuję b”, „stosuję a”. Same wyrażenia po znaku `@` — także wywołania fabryk, jak `powtorz(3)` — interpreter oblicza wcześniej, w kolejności od góry do dołu; od dołu do góry stosowane są dopiero otrzymane dekoratory. Podczas wywołania `f()` sterowanie wchodzi od góry: `opakowana_a` wypisuje „a: przed” i wywołuje `opakowana_b`, ta wypisuje „b: przed” i wywołuje pierwotną funkcję, po czym obie funkcje opakowujące kończą działanie w kolejności odwrotnej do wejścia. Ma to praktyczne znaczenie: dekorator zliczający wywołania umieszczony nad dekoratorem zapamiętującym wyniki policzy każde wywołanie, a umieszczony pod nim — tylko te, które nie zostały obsłużone z pamięci podręcznej.

Składnia dekoratora powraca w dalszych rozdziałach książki. Przy klasach spotkamy dekoratory `@property`, `@classmethod` i `@staticmethod`, a przy klasach danych `@dataclass`; w rozdziale o modułach — `functools.cache` i `functools.wraps`. Każdy z nich korzysta z mechanizmu opisanego na tej stronie: przyjmuje obiekt zdefiniowany instrukcją `def` lub `class` i zwraca obiekt, który zostaje związany z tą samą nazwą. <!-- TODO: linki po powstaniu rozdziałów o modułach i klasach -->
