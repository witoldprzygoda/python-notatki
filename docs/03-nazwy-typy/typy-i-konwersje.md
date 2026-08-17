# Typy i konwersje

## Sprawdzanie typu i rzutowanie

Typ można sprawdzić za pomocą funkcji `type()` lub `isinstance(obiekt, typ)`.

```{ .python .no-copy }
>>> isinstance(a, int)   # True
>>> isinstance(b, int)   # True
>>> isinstance(c, int)   # False
>>> isinstance(e, str)   # False
```

Dla funkcji `isinstance()` drugim argumentem może być również kolekcja typów, wymienionych w okrągłym nawiasie, oddzielonych przecinkami (formalnie — jest to krotka, czyli typ `tuple`).

<!-- TODO: przykład z PDF (zrzut): isinstance z krotką typów; rzutowanie (jawna konwersja) -->

Nazwa w języku Python to swego rodzaju „uchwyt”, referencja. Generalnie nic nas nie może powstrzymać przed przypisaniem wartości czy wyrażeń różnych typów do tej samej nazwy:

```python
x = 2
x = "abcd"
```

I jest to poprawny kod Pythona.

## Adnotacje typów (type hinting)

Od wersji 3.5 wprowadzono możliwość opisu typu zmiennej (dokument PEP 484), nazywa się to *type hinting* albo *type annotation*. Takie prezentowanie typów nadal do niczego nie zmusza, ale pomaga w szybkim rozpoznaniu zamierzonego typu danego obiektu, według składni `nazwa: typ = <inicjalizator>`.

Zatem pisanie kodu z podaniem typu nie zmienia dynamicznego charakteru tworzenia obiektów — stanowi coś na kształt etykiety, czyli zwiększa czytelność kodu (jak również trafność podpowiedzi w IDE). Dla zainteresowanych: [pyannotate](https://pypi.org/project/pyannotate/) lub [MonkeyType](https://pypi.org/project/MonkeyType/).

!!! tip "Wsparcie w Visual Studio Code"
    Jeśli chcemy wsparcie dla takich opisów, można w VSC zainstalować dodatek **Python Type Hint**.

<!-- TODO: screenshot — podpowiedź Type Hint w VSC -->

Niemniej, jeśli chcielibyśmy widzieć w edytorze ostrzeżenia niewłaściwego używania typu obiektu — pylint tego nie robi. Z listy dostępnych linterów (++ctrl+shift+p++ czyli konsola: **Python: Select Linter**) wybieramy **mypy**. Otrzymamy zapewne komunikat, że nie jest zainstalowany (należy wybrać *Install*). Instalacja zostanie wykonana za pomocą komendy typu:

```{ .text .no-copy title="Polecenie wykona się automatycznie" }
"C:/Program Files/Python/python.exe" -m pip install -U mypy
```

<!-- TODO-AKTUALIZACJA: "Python: Select Linter" wycofane w nowszych VSC — mypy
     instaluje się dziś jako rozszerzenie "Mypy Type Checker" -->

Wtedy, przykładowo, próba utworzenia obiektu przez przypisanie wielkości o innym niż opisany typ zostanie przez mypy zauważona (ale nie może zostać zabroniona).

<!-- TODO: screenshot — ostrzeżenie mypy w VSC -->
