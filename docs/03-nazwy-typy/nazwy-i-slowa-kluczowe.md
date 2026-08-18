# Nazwy i słowa kluczowe

## Zasady nazywania

Nazwy zmiennych w Pythonie mogą mieć dowolną długość i mogą składać się z wielkich i małych liter (A–Z, a–z), cyfr (0–9) oraz znaku podkreślenia (`_`). Pierwszym znakiem nazwy zmiennej nie może być cyfra. Python **rozróżnia wielkość liter** — `name`, `Name` i `NAME` to trzy różne zmienne. Zgodnie z konwencją PEP 8 nazwy zmiennych i funkcji zapisujemy w stylu `snake_case` (małe litery, wyrazy rozdzielone podkreśleniem).

!!! note "Litery spoza ASCII"
    Formalnie identyfikatory mogą zawierać również litery Unicode (dokument
    [PEP 3131](https://peps.python.org/pep-3131/)) — zapis `zażółć_gęślą = 42` jest
    poprawny. W praktyce, zgodnie z konwencją PEP 8, nazwy zapisujemy znakami ASCII.

## Słowa kluczowe

Python ma też zestaw **słów kluczowych**, które są słowami zastrzeżonymi — nie można ich używać jako nazw zmiennych, nazw funkcji ani żadnych innych identyfikatorów. Choć na tym etapie poznawania języka jest to katalog 35 haseł, warto się z nimi zapoznać — ich znaczenie będziemy poznawać stopniowo:

```{ .text .no-copy }
and, as, assert, async, await, break, class, continue, def, del,
elif, else, except, False, finally, for, from, global, if, import,
in, is, lambda, None, nonlocal, not, or, pass, raise, return,
True, try, while, with, yield
```

Aktualny katalog przechowuje moduł `keyword` biblioteki standardowej:

```{ .python .no-copy }
>>> import keyword
>>> len(keyword.kwlist)
35
```

!!! note "Miękkie słowa kluczowe"
    Oprócz słów zastrzeżonych Python ma tzw. miękkie słowa kluczowe (ang. *soft
    keywords*): `match`, `case`, `type` oraz `_` (lista `keyword.softkwlist`). Pełnią
    one rolę specjalną tylko w określonym kontekście składniowym — poza nim mogą być
    używane jako zwykłe nazwy. Konstrukcję `match`/`case` omawia rozdział
    [4. Sterowanie przepływem](../04-sterowanie/wyrazenia-warunkowe.md).

## Nazwa jako referencja

Nazwa w języku Python to swego rodzaju „uchwyt”, referencja do obiektu. Generalnie nic nie może nas powstrzymać przed przypisaniem wartości czy wyrażeń różnych typów do tej samej nazwy:

```{ .python .no-copy }
x = 2
x = "abcd"
```

I jest to poprawny kod Pythona — typ jest cechą obiektu, nie nazwy. Model referencji, wraz z konsekwencjami dla pamięci, omawia podrozdział [Obiekty i pamięć](obiekty-i-pamiec.md).

Zmienne można ponadto tworzyć, wykonując przypisanie wielu wartości jednocześnie — także wartości różnych typów:

```{ .python .no-copy }
>>> x, y, z = 1, 2.5, "trzy"
```

Ta sama składnia pozwala zamienić wartości dwóch zmiennych bez zmiennej pomocniczej: `a, b = b, a`. Stojący za tym mechanizm rozpakowywania zostanie omówiony szerzej przy krotkach (rozdział [5. Typy złożone](../05-typy-zlozone/krotka.md)).

## Klasyfikacja typów

Typ obiektu określany jest podczas jego tworzenia. Typy wbudowane można klasyfikować według trzech kryteriów:

- ze względu na strukturę składowania (ang. *storage*) — typy proste oraz typy złożone (kontenery),
- ze względu na modyfikowalność (ang. *update*) — typy modyfikowalne i niemodyfikowalne,
- ze względu na rodzaj dostępu (ang. *access*) — dostęp bezpośredni (liczby) lub sekwencyjny (różne kontenery).

Między typami można wykonywać konwersję (rzutowanie) — opisuje ją podrozdział [Konwersje i adnotacje typów](konwersje-i-adnotacje.md).

Katalog typów wbudowanych:

- typ tekstowy (ang. *text type*): `str`
- typy liczbowe (ang. *numeric types*): `int`, `float`, `complex`
- typy sekwencyjne (ang. *sequence types*): `list`, `tuple`, `range`
- typ odwzorowujący (ang. *mapping type*): `dict`
- typy zbiorowe (ang. *set types*): `set`, `frozenset`
- typ logiczny (ang. *boolean type*): `bool`
- typy binarne (ang. *binary types*): `bytes`, `bytearray`, `memoryview`
- typ braku wartości: `NoneType` (jedyna wartość: `None`)

W tym rozdziale zajmujemy się typami prostymi; typy sekwencyjne (`list`, `tuple`), odwzorowujący (`dict`) i zbiorowe (`set`, `frozenset`) omawia rozdział [5. Typy złożone](../05-typy-zlozone/index.md).
