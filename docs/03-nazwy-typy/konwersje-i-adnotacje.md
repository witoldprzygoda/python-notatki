# Konwersje i adnotacje typów

## Sprawdzanie typu

Typ można sprawdzić za pomocą funkcji `type()` (poznanej w rozdziale [2. Konsola](../02-konsola/konsola-w-praktyce.md)) lub `isinstance(obiekt, typ)`:

```{ .python .no-copy }
>>> a = 42
>>> b = True
>>> c = 3.14
>>> e = [1, 2]
>>> isinstance(a, int)   # True
>>> isinstance(b, int)   # True — bool jest podtypem int!
>>> isinstance(c, int)   # False
>>> isinstance(e, str)   # False
```

Różnica między obiema funkcjami: `type()` zwraca dokładny typ obiektu i nie uwzględnia dziedziczenia, natomiast `isinstance()` hierarchię typów respektuje — stąd `isinstance(True, int)` daje `True`, choć `type(True)` to `bool`, nie `int`. W praktyce preferowana jest funkcja `isinstance()`.

Dla funkcji `isinstance()` drugim argumentem może być również kolekcja typów, wymienionych w okrągłym nawiasie, oddzielonych przecinkami (formalnie — jest to krotka, czyli typ `tuple`, rozdział [5. Typy złożone](../05-typy-zlozone/krotka.md)):

```{ .python .no-copy }
>>> isinstance(42, (int, float))
True
>>> isinstance(3.14, (int, float))
True
```

## Rzutowanie — jawna konwersja

Konwersję między typami wykonują funkcje-konstruktory `int()`, `float()`, `str()` i pokrewne. Warto znać ich zachowania szczególne:

```{ .python .no-copy }
>>> int(3.7)             # 3 — obcina część ułamkową, nie zaokrągla
>>> int(-3.7)            # -3 — obcinanie w stronę zera
>>> int('42')            # 42
>>> float('3.14')        # 3.14
>>> str(42)              # '42'
>>> int(True)            # 1
>>> int(False)           # 0

>>> int('3.14')          # ValueError! — to nie literał całkowity
>>> int('abc')           # ValueError!
>>> int(float('3.14'))   # 3 — dwuetapowo poprawnie
```

Konwersja łańcucha z podaną podstawą (`int('FF', 16)`) została omówiona w podrozdziale [Typy proste](typy-proste.md).

## Adnotacje typów (type hinting)

System podpowiedzi typów (ang. *type hints*) wprowadził dokument [PEP 484](https://peps.python.org/pep-0484/) w Pythonie 3.5 — dla sygnatur funkcji; adnotacje zmiennych w składni `nazwa: typ = <inicjalizator>` dodał [PEP 526](https://peps.python.org/pep-0526/) w Pythonie 3.6. Takie prezentowanie typów do niczego nie zmusza, ale pomaga w szybkim rozpoznaniu zamierzonego typu danego obiektu i zwiększa trafność podpowiedzi w IDE.

Współczesny zapis (standard w Pythonie 3.14) używa typów wbudowanych jako generycznych oraz operatora `|` dla unii typów:

```{ .python .no-copy }
wiek: int = 25
ceny: list[float] = []        # od Pythona 3.9 (PEP 585)
wynik: int | None = None      # od Pythona 3.10 (PEP 604)
```

W starszym kodzie można spotkać zapis z modułu `typing` (`List[float]`, `Optional[int]`) — aliasy te są dziś w dokumentacji oznaczone jako przestarzałe i w nowym kodzie nie są zalecane.

Pisanie kodu z podaniem typu nie zmienia dynamicznego charakteru tworzenia obiektów — Python w czasie działania programu **nie wymusza** zgodności z adnotacją; stanowi ona rodzaj etykiety zwiększającej czytelność kodu.

!!! tip "Podpowiedzi typów w Visual Studio Code"
    Wsparcie adnotacji zapewnia serwer językowy **Pylance**, instalowany domyślnie
    z rozszerzeniem Python. Może on także wyświetlać wywnioskowane typy bezpośrednio
    w kodzie (ang. *inlay hints*) — włączają je ustawienia
    `python.analysis.inlayHints.variableTypes` oraz
    `python.analysis.inlayHints.functionReturnTypes` w pliku `settings.json`.

<!-- TODO: screenshot — podpowiedź typu (inlay hint) Pylance w VSC -->

Jeżeli chcemy widzieć w edytorze ostrzeżenia o niewłaściwym używaniu typów — pylint tego nie robi. Klasycznym narzędziem analizy typów jest **mypy**, dostępne w Visual Studio Code jako osobne rozszerzenie **Mypy Type Checker** (wydawca Microsoft): instalujemy je z widoku **Extensions** (++ctrl+shift+x++), tak jak wcześniej Pylint. Rozszerzenie zawiera dołączoną kopię mypy — dodatkowa instalacja nie jest potrzebna, a ostrzeżenia pojawiają się w zakładce **Problems**.

!!! note "Mypy z własnego środowiska"
    Analogicznie jak przy pylincie, wersję mypy z aktywnego środowiska projektu
    (zainstalowaną poleceniem `python -m pip install mypy`) wskazuje ustawienie
    `"mypy-type-checker.importStrategy": "fromEnvironment"`.

Wtedy, przykładowo, próba utworzenia obiektu przez przypisanie wielkości o innym niż opisany typ zostanie przez mypy zauważona (ale nie może zostać zabroniona).

<!-- TODO: screenshot — ostrzeżenie Mypy Type Checker w VSC -->
