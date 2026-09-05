# Rekurencja

Funkcja może wywołać samą siebie. Taką technikę nazywamy **rekurencją** (ang. *recursion*), a funkcję — **funkcją rekurencyjną** (ang. *recursive function*). Rekurencja jest pośrednia, gdy funkcja wywołuje inną funkcję, która wywołuje pierwszą; w tym podrozdziale ograniczamy się do rekurencji bezpośredniej. Opieramy się na ustaleniu z podrozdziału [Zasięg nazw i domknięcia](zasieg-nazw-i-domkniecia.md#przestrzenie-nazw-i-zasiegi): każde wywołanie funkcji tworzy własną przestrzeń lokalną — także wtedy, gdy wywołaną funkcją jest ta sama funkcja. Pokażemy, z czego składa się poprawna definicja rekurencyjna, jak prześledzić jej wykonanie, kiedy rekurencja jest naturalniejsza od pętli, a kiedy kosztowniejsza, jak przetwarzać nią struktury zagnieżdżone z rozdziału 5 oraz dlaczego interpreter ogranicza jej głębokość.

## Przypadek bazowy i krok rekurencyjny

Klasycznym przykładem jest silnia: n! = n · (n − 1)!, przy czym 0! = 1! = 1. Definicja matematyczna odwołuje się do samej siebie dla mniejszego argumentu, a dla najmniejszych argumentów podaje wynik wprost. Funkcja rekurencyjna ma dokładnie te same dwie części:

```python title="silnia.py"
def silnia(n):
    """Zwraca silnię nieujemnej liczby całkowitej n."""
    if n <= 1:
        return 1
    return n * silnia(n - 1)


print(silnia(4))
print(silnia(1))
print(silnia(10))
```

```{ .text .no-copy }
24
1
3628800
```

**Przypadek bazowy** (ang. *base case*) to warunek `n <= 1`, przy którym funkcja zwraca wynik bez kolejnego wywołania. **Krok rekurencyjny** (ang. *recursive step*) to instrukcja `return n * silnia(n - 1)`: zadanie dla `n` sprowadza się do tego samego zadania dla `n - 1` i jednego mnożenia. Poprawna definicja rekurencyjna wymaga obu części oraz gwarancji, że każdy krok przybliża do przypadku bazowego — tu argument maleje o 1, więc od dowolnej nieujemnej liczby całkowitej dochodzi do `1` lub `0`. Bez przypadku bazowego albo bez tej gwarancji wywołania nigdy się nie kończą; zachowanie interpretera w takiej sytuacji opisuje sekcja [Limit rekurencji](#limit-rekurencji).

Wynik wywołania `silnia(4)` nie może zostać obliczony, dopóki nie zostanie obliczona wartość `silnia(3)`; ta z kolei zależy od wartości `silnia(2)`, a tamta — od `silnia(1)`. Dopiero przypadek bazowy zwraca `1`, po czym mnożenia wykonują się w kolejności odwrotnej do wywołań:

```{ .text .no-copy }
silnia(4)
= 4 * silnia(3)
= 4 * (3 * silnia(2))
= 4 * (3 * (2 * silnia(1)))
= 4 * (3 * (2 * 1))
= 4 * (3 * 2)
= 4 * 6
= 24
```

Schemat pokazuje kolejność obliczeń, nie techniczny opis pamięci interpretera. Wywołanie rozpoczęte, lecz jeszcze niezakończone, nazywamy **aktywnym wywołaniem**. Dla każdego aktywnego wywołania interpreter utrzymuje **ramkę wywołania** (ang. *call frame*): zapis zawierający przestrzeń lokalną tego wywołania i informację, gdzie kontynuować program po instrukcji `return`. W górnej połowie schematu powstają kolejne ramki, w dolnej — kolejne wywołania kończą się i ich ramki znikają. W chwili obliczania `silnia(1)` aktywne są cztery wywołania funkcji `silnia`, każde z własnym parametrem `n`: `4`, `3`, `2` i `1`. Widać to w wersji diagnostycznej, która wypisuje przebieg wywołań z wcięciem zależnym od poziomu zagnieżdżenia:

```python title="silnia-slad.py"
def silnia_slad(n, poziom=0):
    """Zwraca silnię n, wypisując przebieg wywołań z wcięciem."""
    wciecie = "  " * poziom
    print(f"{wciecie}silnia_slad({n})")
    if n <= 1:
        print(f"{wciecie}zwraca 1")
        return 1
    wynik = n * silnia_slad(n - 1, poziom + 1)
    print(f"{wciecie}zwraca {wynik}")
    return wynik


print(silnia_slad(4))
```

```{ .text .no-copy }
silnia_slad(4)
  silnia_slad(3)
    silnia_slad(2)
      silnia_slad(1)
      zwraca 1
    zwraca 2
  zwraca 6
zwraca 24
24
```

Parametr `poziom` z wartością domyślną `0` (podrozdział [Argumenty i parametry](argumenty-i-parametry.md#wartosci-domyslne)) rośnie o 1 w każdym wywołaniu wewnętrznym; nazwy `n`, `poziom`, `wciecie` i `wynik` są lokalne dla każdego wywołania osobno, dlatego po powrocie z `silnia_slad(3)` wywołanie `silnia_slad(4)` nadal ma własne `n` równe `4` i wcięcie zerowe. Wiersze „zwraca” pojawiają się od najgłębszego wywołania do najpłytszego — wywołanie wewnętrzne kończy się w całości, zanim zewnętrzne wykona swoje mnożenie.

### Funkcja pomocnicza w funkcji zewnętrznej

Sprawdzanie poprawności argumentu w każdym wywołaniu rekurencyjnym byłoby zbędne — warunek jest ten sam, a argument tylko maleje. Sprawdzenie wykonujemy raz, w funkcji zewnętrznej, a rekurencję przenosimy do funkcji zagnieżdżonej, jak w sekcji [Funkcje zagnieżdżone i zmienne wolne](zasieg-nazw-i-domkniecia.md#funkcje-zagniezdzone-i-zmienne-wolne):

```python title="silnia-bezpieczna.py"
def silnia_bezpieczna(n):
    """Zwraca silnię n albo None, gdy n nie jest nieujemną liczbą całkowitą."""
    if not isinstance(n, int) or n < 0:
        return None

    def pomocnicza(k):
        if k <= 1:
            return 1
        return k * pomocnicza(k - 1)

    return pomocnicza(n)


print(silnia_bezpieczna(5))
print(silnia_bezpieczna(-3))
print(silnia_bezpieczna(2.5))
```

```{ .text .no-copy }
120
None
None
```

Funkcja `pomocnicza()` jest widoczna wyłącznie wewnątrz `silnia_bezpieczna()` i zakłada, że argument jest już sprawdzony. Zwracanie `None` jako sygnału błędnego argumentu pozostaje rozwiązaniem tymczasowym, jak ustaliliśmy w podrozdziale [Definiowanie funkcji](definiowanie-funkcji.md#instrukcja-return); właściwym mechanizmem będą wyjątki. <!-- TODO: link po powstaniu rozdziału o wyjątkach -->

## Rekurencja a iteracja

Silnię równie dobrze oblicza pętla `for` z rozdziału [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md#petla-for):

```python title="silnia-iteracyjna.py"
def silnia_iter(n):
    """Zwraca silnię nieujemnej liczby całkowitej n, obliczoną pętlą."""
    wynik = 1
    for k in range(2, n + 1):
        wynik *= k
    return wynik


print(silnia_iter(4), silnia_iter(1), silnia_iter(10))
```

```{ .text .no-copy }
24 1 3628800
```

Obie wersje dają te same wyniki. Wersja iteracyjna przez cały czas ma jedną ramkę z nazwami `wynik` i `k`, rekurencyjna — dla `n >= 1` tyle ramek, ile wynosi `n`. Żadna z form nie jest zawsze lepsza. Rekurencja jest naturalna wtedy, gdy sama struktura problemu jest rekurencyjna: zadanie rozpada się na mniejsze zadania tego samego rodzaju, a wynik składa się z ich wyników — tak jest przy strukturach zagnieżdżonych z następnej sekcji. Prosty ciąg powtarzanych działań, jak kolejne mnożenia, zwykle łatwiej zapisać i wykonać pętlą; w Pythonie przemawia za tym także limit głębokości rekurencji opisany dalej.

Ciąg Fibonacciego pokazuje inny problem. Każdy jego wyraz jest sumą dwóch poprzednich, a dwa pierwsze wyrazy to 0 i 1. Definicja rekurencyjna jest naturalna, ale zawiera dwa wywołania rekurencyjne:

```python title="fib.py"
def fib(n):
    """Zwraca n-ty wyraz ciągu Fibonacciego (fib(0) = 0, fib(1) = 1)."""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def fib_iter(n):
    """Zwraca n-ty wyraz ciągu Fibonacciego, obliczony pętlą."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


print([fib(n) for n in range(10)])
print([fib_iter(n) for n in range(10)])
```

```{ .text .no-copy }
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

Wersja iteracyjna korzysta z przypisania wielokrotnego, poznanego w rozdziale [3. Nazwy i typy](../03-nazwy-typy/nazwy-i-slowa-kluczowe.md#nazwa-jako-referencja) przy zamianie `a, b = b, a` — tu w postaci `a, b = b, a + b`, w której prawa strona jest obliczana w całości przed przypisaniem (rozdział [5. Typy złożone](../05-typy-zlozone/krotka.md#pakowanie-i-rozpakowywanie)) — i wykonuje `n` dodawań. Wersja rekurencyjna wielokrotnie oblicza te same wartości. Schemat rozgałęziających się wywołań, zwany **drzewem wywołań** (ang. *call tree*), wygląda dla `fib(5)` następująco:

```{ .text .no-copy }
fib(5)
├── fib(4)
│   ├── fib(3)
│   │   ├── fib(2)
│   │   │   ├── fib(1)
│   │   │   └── fib(0)
│   │   └── fib(1)
│   └── fib(2)
│       ├── fib(1)
│       └── fib(0)
└── fib(3)
    ├── fib(2)
    │   ├── fib(1)
    │   └── fib(0)
    └── fib(1)
```

Wartość `fib(3)` jest obliczana dwa razy, `fib(2)` — trzy razy, `fib(1)` — pięć razy; łącznie 15 wywołań dla wyniku `5`. Liczbę wywołań zliczymy licznikiem w domknięciu z deklaracją `nonlocal`, poznanym w sekcji [Deklaracje global i nonlocal](zasieg-nazw-i-domkniecia.md#deklaracje-global-i-nonlocal). Funkcja `fib_z_licznikiem()` zwraca parę funkcji: `fib` zliczającą własne wywołania oraz `ile` odczytującą licznik:

```python title="fib-licznik.py"
def fib_z_licznikiem():
    """Zwraca parę (fib, ile); ile zwraca liczbę wywołań funkcji fib."""
    wywolania = 0

    def fib(n):
        nonlocal wywolania
        wywolania += 1
        if n < 2:
            return n
        return fib(n - 1) + fib(n - 2)

    def ile():
        return wywolania

    return fib, ile


for n in (5, 10, 20, 30):
    fib, ile = fib_z_licznikiem()
    print(f"fib({n}) = {fib(n)}, wywołań: {ile()}")
```

```{ .text .no-copy }
fib(5) = 5, wywołań: 15
fib(10) = 55, wywołań: 177
fib(20) = 6765, wywołań: 21891
fib(30) = 832040, wywołań: 2692537
```

Każdy obrót pętli tworzy nowe domknięcie, więc licznik zaczyna od zera. Liczba wywołań rośnie **wykładniczo**: zwiększenie `n` o 10 mnoży ją około 123 razy, czyli w takim tempie, w jakim rosną same liczby Fibonacciego — obliczenie n-tego wyrazu wymaga dokładnie 2·fib(n + 1) − 1 wywołań, co można sprawdzić na powyższych liczbach. Obliczenie `fib(30)` to niemal 2,7 miliona wywołań, podczas gdy `fib_iter(30)` wykonuje 30 dodawań. Przyczyną nie jest rekurencja sama w sobie, lecz powtarzanie obliczeń; rozwiązaniem jest zapamiętywanie raz obliczonych wyników, zwane **memoizacją** (ang. *memoization*) — wracamy do niej w podrozdziale [Dekoratory](dekoratory.md#memoizacja), a gotowe narzędzie biblioteki standardowej poznamy w następnym rozdziale. <!-- TODO: link po powstaniu rozdziału o modułach -->

## Rekurencja na strukturach zagnieżdżonych

W rozdziale [5. Typy złożone](../05-typy-zlozone/lista.md#tworzenie-listy) elementami listy były także inne listy, a `len()` liczyła wyłącznie elementy najwyższego poziomu. Definicja listy zagnieżdżonej jest sama rekurencyjna: jej element jest albo pojedynczą wartością, albo listą zagnieżdżoną — tą samą strukturą o poziom niżej. Dlatego funkcja, która ma dotrzeć do wszystkich wartości, naturalnie wywołuje samą siebie dla elementów będących listami. Funkcja `splaszcz()` zwraca płaską listę wszystkich wartości:

```python title="splaszcz.py"
def splaszcz(lista):
    """Zwraca płaską listę wszystkich wartości z listy zagnieżdżonej."""
    wynik = []
    for element in lista:
        if isinstance(element, list):
            wynik.extend(splaszcz(element))
        else:
            wynik.append(element)
    return wynik


zagniezdzona = [1, [2, 3], [[4], 5]]
print(splaszcz(zagniezdzona))
print(len(zagniezdzona), len(splaszcz(zagniezdzona)))
print(splaszcz([]))
print(splaszcz([[[[7]]]]))
```

```{ .text .no-copy }
[1, 2, 3, 4, 5]
3 5
[]
[7]
```

Funkcja `isinstance()` z rozdziału [3. Nazwy i typy](../03-nazwy-typy/konwersje-i-adnotacje.md#sprawdzanie-typu) rozstrzyga, która z dwóch części definicji ma zastosowanie. Przypadkiem bazowym jest lista bez list zagnieżdżonych, także pusta: pętla dołącza elementy metodą `append()` i funkcja zwraca wynik bez wywołania rekurencyjnego. Krok rekurencyjny to wywołanie `splaszcz(element)` dla elementu będącego listą; zwróconą płaską listę dołączamy metodą `extend()`. Pętla i rekurencja uzupełniają się: pętla przechodzi wszerz po elementach jednego poziomu, rekurencja schodzi w głąb. Głębokość rekurencji równa się głębokości zagnieżdżenia, nie liczbie elementów — dla typowych danych jest to kilka poziomów. Zamiana obu instrukcji dołączania na zliczanie daje funkcję liczącą wszystkie wartości; zamiana na dodawanie — sumującą je.

Definicja zakłada, że zagnieżdżenie jest skończone: schodząc w głąb, dochodzimy w końcu do wartości niebędących listami. Lista, jako obiekt modyfikowalny, może to założenie naruszyć. W rozdziale [5. Typy złożone](../05-typy-zlozone/lista.md#tworzenie-listy) wspomnieliśmy o liście zagnieżdżonej w samej sobie i o funkcji sprawdzającej typ elementu warunkiem `isinstance`, którą właśnie napisaliśmy jako `splaszcz()`:

```python title="cykl.py"
lista = [1, 2]
lista.append(lista)
print(lista)
print(lista[2] is lista)
```

```{ .text .no-copy }
[1, 2, [...]]
True
```

!!! warning "Struktura z cyklem"
    Trzecim elementem listy jest ona sama, więc struktura zawiera **cykl**. Tekstowa
    reprezentacja listy, którą wypisuje `print()`, wykrywa cykl i oznacza go skrótem
    `[...]`, ale `splaszcz(lista)` nie ma takiego zabezpieczenia: trzeci element jest
    listą, więc następuje wywołanie `splaszcz(lista)` z tym samym argumentem, w nim
    znowu takie samo wywołanie — przypadek bazowy nigdy nie zostaje osiągnięty.
    Naiwny algorytm rekurencyjny, zakładający strukturę bez cykli (drzewo), na
    strukturze z cyklem nie zakończy się sam; kończy go dopiero mechanizm opisany
    w następnej sekcji. Wykrywanie cykli wykracza poza ten podrozdział.

## Limit rekurencji

Definicja bez przypadku bazowego wywołuje samą siebie bez końca. Funkcja `silnia()` pozbawiona warunku `n <= 1` schodzi przez `5`, `4`, `3`, `2`, `1`, `0`, `-1` i dalej w liczby ujemne:

```python title="brak-bazy.py"
def silnia(n):
    return n * silnia(n - 1)


print(silnia(5))
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "brak-bazy.py", line 5, in <module>
    print(silnia(5))
          ~~~~~~^^^
  File "brak-bazy.py", line 2, in silnia
    return n * silnia(n - 1)
               ~~~~~~^^^^^^^
  File "brak-bazy.py", line 2, in silnia
    return n * silnia(n - 1)
               ~~~~~~^^^^^^^
  File "brak-bazy.py", line 2, in silnia
    return n * silnia(n - 1)
               ~~~~~~^^^^^^^
  [Previous line repeated 996 more times]
RecursionError: maximum recursion depth exceeded
```

Każde aktywne wywołanie zajmuje ramkę, a ramki nigdy nie znikają, bo żadne wywołanie się nie kończy. Interpreter zlicza aktywne ramki kodu Pythona — funkcji i modułu — i gdy ich liczba przekroczy **limit rekurencji** (ang. *recursion limit*), zgłasza wyjątek `RecursionError`; dla rekurencji w kodzie Pythona, jak wyżej, komunikat brzmi `maximum recursion depth exceeded`. Dokumentacja modułu `sys` opisuje limit jako zabezpieczenie przed przepełnieniem stosu i awarią interpretera: zamiast niekontrolowanego wzrostu liczby ramek otrzymujemy czytelny komunikat. Ślad wywołań składa się z ramki modułu i długiego ciągu identycznych ramek funkcji `silnia`; powtarzające się identyczne wiersze śladu są skracane — wypisanych jest kilka pierwszych powtórzeń (w CPythonie trzy), a pozostałe podsumowuje wiersz `[Previous line repeated 996 more times]`.

W CPythonie limit wynosi domyślnie 1000 ramek; jest to jednak szczegół implementacyjny, a głębokość dostępna dla programu jest mniejsza i zależy od kontekstu wykonania, co opisuje nota poniżej. Z tych powodów nie uzależniamy poprawności algorytmu od konkretnej liczby poziomów: poprawna rekurencja osiąga przypadek bazowy po liczbie kroków wynikającej z danych — jak głębokość zagnieżdżenia w `splaszcz()` — a nie po setkach czy tysiącach poziomów. Gdy zadanie rzeczywiście wymaga tysięcy kroków, jak `silnia(5000)`, właściwym rozwiązaniem jest wersja iteracyjna, nie podnoszenie limitu.

!!! note "Granica zależy od kontekstu"
    Ta sama funkcja może osiągnąć inną głębokość rekurencji uruchomiona w skrypcie,
    wywołana z wnętrza innych funkcji albo w konsoli, bo do limitu liczą się
    wszystkie aktywne ramki kodu Pythona, nie tylko ramki funkcji rekurencyjnej:
    ramkę zajmuje moduł, w którym rozpoczyna się wywołanie, każda funkcja pośrednia
    zajmuje kolejną, a w nowej konsoli interaktywnej (od Pythona 3.13), napisanej
    w Pythonie, część ramek zajmuje kod samej konsoli. Od Pythona 3.12 limit
    dotyczy wyłącznie ramek kodu w Pythonie; funkcje wbudowane chroni osobny
    mechanizm. Dokładna liczba poziomów jest więc właściwością środowiska
    wykonania, a nie gwarancją języka.

Standardowy moduł `sys` udostępnia funkcje do odczytu i zmiany limitu rekurencji; wrócimy do nich po wprowadzeniu modułów. Dokumentacja ostrzega, że zbyt wysoki limit może doprowadzić do awarii interpretera, a zwiększanie limitu nie naprawia definicji, która nie osiąga przypadku bazowego. <!-- TODO: link po powstaniu rozdziału o modułach -->

## Rekurencja ogonowa

Ta sekcja jest przeznaczona dla dociekliwych; dalsze podrozdziały z niej nie korzystają. W kroku `return n * silnia(n - 1)` wywołanie rekurencyjne nie jest ostatnią operacją: po jego powrocie trzeba jeszcze wykonać mnożenie, dlatego ramka wywołania zewnętrznego musi istnieć do zakończenia wywołania wewnętrznego. Wywołanie, którego wynik funkcja zwraca bezpośrednio, bez dalszych działań, nazywa się **wywołaniem ogonowym** (ang. *tail call*), a rekurencję złożoną wyłącznie z takich wywołań — **rekurencją ogonową** (ang. *tail recursion*). Silnię można tak zapisać, przekazując dotychczasowy iloczyn w dodatkowym parametrze, zwanym **akumulatorem** (ang. *accumulator*) — w poniższym kodzie jest nim parametr `wynik`:

```python title="silnia-ogonowa.py"
def silnia_ogonowa(n, wynik=1):
    """Zwraca silnię n; wynik gromadzi iloczyn obliczony dotychczas."""
    if n <= 1:
        return wynik
    return silnia_ogonowa(n - 1, wynik * n)


print(silnia_ogonowa(5))
print(silnia_ogonowa(5000))
```

```{ .text .no-copy }
120
Traceback (most recent call last):
  File "silnia-ogonowa.py", line 9, in <module>
    print(silnia_ogonowa(5000))
          ~~~~~~~~~~~~~~^^^^^^
  File "silnia-ogonowa.py", line 5, in silnia_ogonowa
    return silnia_ogonowa(n - 1, wynik * n)
  File "silnia-ogonowa.py", line 5, in silnia_ogonowa
    return silnia_ogonowa(n - 1, wynik * n)
  File "silnia-ogonowa.py", line 5, in silnia_ogonowa
    return silnia_ogonowa(n - 1, wynik * n)
  [Previous line repeated 996 more times]
RecursionError: maximum recursion depth exceeded
```

Brak podkreśleń w powtarzanych wierszach śladu nie jest pominięciem — interpreter opuszcza je, gdy wskazane wywołanie stanowi całe wyrażenie instrukcji `return`. W niektórych językach, np. w Scheme, którego standard wymaga tego od każdej implementacji, wywołanie ogonowe jest zastępowane skokiem, a bieżąca ramka wykorzystywana ponownie — jest to **optymalizacja wywołań ogonowych** (ang. *tail call optimization*, także *tail call elimination*), dzięki której rekurencja ogonowa zużywa stałą liczbę ramek. Python takiej optymalizacji nie wykonuje — dokumentacja referencyjna języka jej nie przewiduje, a CPython jej nie implementuje: każde wywołanie, także ogonowe, tworzy nową ramkę, więc `silnia_ogonowa(5000)` wyczerpuje limit dokładnie tak samo jak zwykła wersja rekurencyjna. Guido van Rossum uzasadnił tę decyzję we wpisie *Tail Recursion Elimination* z 2009 roku: usunięte ramki nie pojawiałyby się w śladzie wywołań, co utrudnia diagnostykę; kod polegający na tej optymalizacji nie działałby w implementacjach, które jej nie mają; wreszcie rekurencja nie jest w Pythonie podstawowym sposobem wyrażania powtórzeń — są nim pętle i iteratory.

!!! note "Interpreter z wywołaniami ogonowymi w Pythonie 3.14"
    Python 3.14 wprowadził opcjonalny wariant interpretera CPython, dostępny tylko
    przy kompilacji kompilatorem Clang 19 lub nowszym na architekturach x86-64
    i AArch64 (oficjalne instalatory dla Windows są budowane kompilatorem MSVC,
    widocznym w wyniku `python -VV`, więc go nie zawierają), zbudowany z małych
    funkcji w języku C wywołujących się nawzajem ogonowo, co może przyspieszyć
    wykonywanie programów. Dokumentacja
    zastrzega, że nie jest to optymalizacja wywołań ogonowych funkcji Pythona — ta
    nadal nie jest zaimplementowana — i że wariant ten nie zmienia obserwowalnego
    zachowania programów.

Najważniejszy wniosek: zapis ogonowy nie usuwa w Pythonie problemu głębokości rekurencji. Ma jednak wartość praktyczną — funkcja z akumulatorem przekłada się wprost na pętlę: w każdym obrocie `wynik` jest mnożony przez `n`, a `n` maleje o 1, aż osiągnie przypadek bazowy. Na tej samej zasadzie działa `silnia_iter()` z sekcji [Rekurencja a iteracja](#rekurencja-a-iteracja), różniąc się jedynie kolejnością czynników — od `2` do `n` zamiast od `n` w dół. Gdy głębokość rekurencji staje się problemem, rozwiązaniem jest ta zamiana, a nie zmiana limitu.
