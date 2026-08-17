# 2. Konsola

Działania w interpreterze Pythona można prowadzić w dowolnym terminalu, zależnie od systemu operacyjnego. Przede wszystkim program interpretera powinien być dostępny z poziomu terminala — sposoby weryfikacji (`where.exe python`, `Get-Command python`, odczyt `sys.executable`) opisuje podrozdział [Instalacja klasyczna](../01-instalacja/instalacja-klasyczna.md).

Python można uruchomić w oknie **cmd** Windows (niewygodne), w **PowerShell** — najlepiej w aplikacji **Windows Terminal**, będącej obecnie domyślnym hostem terminala w Windows 11 — albo np. w programie **IDLE**, dołączonym do standardowej biblioteki (uruchomienie poleceniem `py -m idlelib`). Warto przećwiczyć wykonanie kilku komend, aby się oswoić.

Nawet prosta funkcja `print` ma kilka opcji, np. w IDLE możemy zobaczyć podpowiedź podczas pisania.

<!-- TODO: screenshot — podpowiedź sygnatury print() w IDLE -->

!!! tip "Skróty klawiszowe w IDLE"
    IDLE ma niekoniecznie intuicyjny zestaw skrótów klawiszowych, który można
    przedefiniować lub się ich nauczyć. Przykładowo, poprzednia (kolejna)
    wykonana instrukcja to ++alt+p++ (++alt+n++).

## Nowa konsola interaktywna

Konsola interaktywna (**REPL**, ang. *read-eval-print loop*) została w ostatnich wydaniach Pythona gruntownie unowocześniona. Od wersji 3.13 domyślna powłoka opiera się na kodzie projektu PyPy i oferuje:

- **edycję wieloliniową** — bloki kodu (np. funkcje, pętle) można poprawiać w całości, poruszając się strzałkami, zamiast wpisywać je od nowa,
- **kolorowe znaki zachęty i komunikaty błędów**,
- polecenia `help`, `exit` oraz `quit` działające **bez nawiasów**,
- przeglądanie pomocy klawiszem ++f1++, historii poleceń klawiszem ++f2++ oraz **tryb wklejania** większych fragmentów kodu pod klawiszem ++f3++ (ponowne ++f3++ wraca do zwykłego trybu).

Python 3.14 dodał do tego **kolorowanie składni na żywo** — słowa kluczowe, łańcuchy znaków, liczby i komentarze otrzymują własne kolory już podczas pisania — oraz **autouzupełnianie nazw modułów** klawiszem ++tab++ w instrukcjach `import`.

<!-- TODO: screenshot — nowy REPL z kolorowaniem składni (kolorów nie odda blok tekstowy) -->

!!! note "Powrót do klasycznej powłoki"
    Nową powłokę można wyłączyć, ustawiając zmienną środowiskową
    `PYTHON_BASIC_REPL`. Samo kolorowanie wyłączają zmienne `PYTHON_COLORS=0`
    lub `NO_COLOR=1`.

Do konsoli wchodzimy poleceniem `python` (lub `py`) — pojawi się znak zachęty `>>>`. Wychodzimy poleceniem `exit` (bez nawiasów; w starszych wersjach `exit()`) albo skrótem ++ctrl+z++ i ++enter++.

## Funkcja print — pierwsze eksperymenty

Spróbujmy:

```{ .python .no-copy }
>>> print("hello world"*2, ' ', 123, 'tez string', sep=",", end=" ||KONIEC\n")
hello worldhello world, ,123,tez string ||KONIEC

>>> print('hello world', end=', '); print("yeah")
hello world, yeah
```

Z powyższych przykładów widać, że argumenty funkcji mogą mieć postać **argumentów pozycyjnych** bez nazwy oraz **nazwanych** (`sep`, `end`) — te można pisać w dowolnej kolejności (spróbuj zamienić `end` z `sep`). Widać też, że może być separator `;`, jeśli kolejna funkcja jest w tej samej linii.

## Typy dynamiczne, bool i None

Obiekty w Pythonie tworzy się dynamicznie, bez deklaracji typów — są zbudowane na podstawie wielkości inicjalizujących.

Przykładowo, typ logiczny `bool` ma dwie wartości opisane jako `True` oraz `False` (z wielkich liter), gdzie `True` umownie ma wartość 1, ale też wszystko, co nie jest zerem, obiektem pustym lub `None`, jest traktowane w kontekście logiki jako `True`.

```{ .python .no-copy }
>>> logika = True
>>> if logika:
...     print("to jest prawda")
```

!!! info "Słowo kluczowe None"
    Słowo kluczowe `None` służy do definiowania wartości null lub braku wartości.
    `None` to **nie** to samo co `0`, `False` lub pusty ciąg.
    `None` jest własnym typem danych (`NoneType`).

## Formatowanie kodu — wcięcia

Formatowanie kodu w Pythonie odbywa się za pomocą `:` (dwukropka) oraz odpowiednich wcięć. Standard **PEP 8** zaleca wcięcia o szerokości **4 spacji** na każdy poziom. W praktyce najwygodniej skonfigurować edytor tak, aby klawisz ++tab++ wstawiał 4 spacje — Visual Studio Code robi tak w plikach Pythona domyślnie.

!!! tip "Tab size w Visual Studio Code"
    W Visual Studio Code (skrót ++ctrl+comma++) wpisując „tab size" znajdziemy
    odpowiednie pole, w którym wstawimy odpowiednią wartość.

**Nie można mieszać rodzaju wcięć.**

Nawet „na oko" dobrze sformatowany kod, jeśli ma pomieszane tabulacje i spacje, może być błędny. Żeby tego doświadczyć, trzeba oczywiście najpierw zapisać plik, w którym rzeczywiście jedno wcięcie będzie wypełnione znakiem Tab, a drugie zbudowane ze spacji. Można taką sytuację uzyskać np. pisząc fragment kodu w prostym edytorze typu Notatnik (Windows) i jedno wcięcie tworząc klawiszem ++tab++, a drugie wstawiając 8 spacji. Optycznie wygląda identycznie. Jednak po skopiowaniu takiego kodu do interpretera (np. okienko IDLE) zobaczymy błąd niekonsystencji znaków użytych we wcięciach (`TabError`).

## Komentarze

Komentarz jest na prawo od znaku `#`. Komentarz zapisany w wielu liniach osiąga się przez stworzenie wielolinijkowego łańcucha znakowego, bez jego przypisania. Tworzy się go za pomocą trzy razy powtórzonego pojedynczego `'''` lub podwójnego `"""` cudzysłowu.

```python
"""
To jest komentarz
zapisany w wielu liniach
"""
```

!!! tip "Komentowanie wielu linii w Visual Studio Code"
    Jeśli zaznaczymy kilka linijek kodu, to skrótem klawiszowym ++ctrl+k++ ++ctrl+c++
    (lub prościej ++ctrl+slash++) możemy dodać znak komentarza `#`,
    a skrótem ++ctrl+k++ ++ctrl+u++ go usunąć — w wielu liniach jednocześnie.

## Przypisanie wielokrotne

Zmienne można tworzyć, wykonując przypisanie wielu wartości jednocześnie, np.:

```{ .python .no-copy }
>>> x, y, z = 1, 2.5, "trzy"
```

## Konsola jako kalkulator

Konsolę można użyć jako kalkulatora. Spróbujmy:

```{ .python .no-copy }
>>> 2 + 2
>>> 50 - 5*6
>>> (50 - 5*6) / 4
>>> 8 / 5      # float, dzielenie prawdziwe
>>> 17 // 3    # dzielenie bez reszty
>>> 17 % 3     # modulo, czyli reszta z dzielenia
>>> 5 * 3 + 2
>>> 5 ** 2     # 5^2
>>> 2 ** 7     # 2^7
>>> width = 20
>>> height = 5 * 9
>>> width * height
```

Ostatnia wyświetlona w konsoli wartość jest dostępna również pod nazwą (znaczkiem) `_`:

```{ .python .no-copy }
>>> 5      # spróbuj (Enter)
>>> _
>>> _ + _
```

## Funkcje matematyczne

Aby mieć dostęp do większej liczby funkcji matematycznych, trzeba skorzystać z dodatkowych modułów. Przed użyciem moduł należy zaimportować. W tym przypadku:

```{ .python .no-copy }
>>> import math
>>> math.sqrt(4)
2.0
```

Spis funkcji: [docs.python.org/3/library/math.html](https://docs.python.org/3/library/math.html) — w przypadku liczb zespolonych użyjemy [cmath](https://docs.python.org/3/library/cmath.html).

## Pomoc wbudowana: help i dir

Konsola jest też najszybszą drogą do dokumentacji. Funkcja `help` wyświetla opis wskazanego obiektu:

```{ .python .no-copy }
>>> help(print)
>>> help(math.sqrt)
```

a wywołana bez argumentu (`help()`) uruchamia interaktywną przeglądarkę pomocy — wpisujemy w niej nazwy funkcji czy modułów, a wychodzimy wpisując `q` (w nowej powłoce tę samą przeglądarkę otwiera klawisz ++f1++). Z kolei funkcja `dir` wypisuje dostępne atrybuty obiektu — np. wszystkie metody typu łańcuchowego:

```{ .python .no-copy }
>>> dir(str)
```

## Python bez wchodzenia do konsoli: opcje -c, -m oraz -i

Interpreter przyjmuje opcje wiersza poleceń, dzięki którym krótkie zadania wykonamy bez otwierania konsoli interaktywnej.

Opcja **`-c`** wykonuje przekazany kod i kończy działanie — nasz „kalkulator" mieści się wtedy w jednym poleceniu terminala:

```powershell title="Terminal"
python -c "print(2 ** 10)"
```

Kilka instrukcji rozdzielamy średnikami:

```powershell title="Terminal"
python -c "import math; print(math.pi * 2)"
```

Tę formę stosowaliśmy już w podrozdziale [Instalacja klasyczna](../01-instalacja/instalacja-klasyczna.md), odczytując `sys.executable` czy `sys.path`. Uwaga na cudzysłowy: całość kodu najbezpieczniej ująć w cudzysłowy podwójne, a łańcuchy wewnątrz kodu zapisywać w pojedynczych, np. `python -c "print('hello')"`.

Opcja **`-m`** uruchamia wskazany moduł jako program — spotkaliśmy ją już przy `python -m pip` czy `python -m venv`. Moduły standardowej biblioteki potrafią zaskoczyć, np.:

```powershell title="Terminal"
python -m calendar 2026
```

wypisze w terminalu kalendarz na cały rok.

Opcja **`-i`** wykonuje wskazany plik, a następnie — zamiast zakończyć działanie — pozostawia nas w konsoli interaktywnej z dostępem do wszystkich utworzonych w nim zmiennych i funkcji:

```powershell title="Terminal"
python -i main.py
```

Jest to bardzo wygodny sposób eksperymentowania z własnym kodem. Pełny wykaz opcji wypisze `python --help`, a ich omówienie zawiera dokumentacja: [docs.python.org/3/using/cmdline.html](https://docs.python.org/3/using/cmdline.html).
