# Adnotacje typów w praktyce

Adnotacje typów z rozdziałów 3 i 6 nie wpływają na wykonanie programu — interpreter je zapisuje, ale nie sprawdza. Ich wartość ujawnia się poza interpreterem: **sprawdzacz typów** (ang. *type checker*) znajduje niezgodności przed uruchomieniem, edytor podpowiada na ich podstawie nazwy metod, a biblioteki takie jak klasy danych z rozdziału 12 budują na nich zachowanie. W tym podrozdziale poznajemy zapis typów złożonych, aliasy i generyki, słowniki typowane oraz narzędzie mypy.

## Przypomnienie i odczyt adnotacji

Adnotację zmiennej zapisujemy po dwukropku, parametru — w sygnaturze, a typ wyniku — po strzałce (rozdział [3. Nazwy i typy](../03-nazwy-typy/konwersje-i-adnotacje.md#adnotacje-typow-type-hinting) i [6. Funkcje](../06-funkcje/definiowanie-funkcji.md#adnotacje-w-sygnaturze)). Od Pythona 3.14 adnotacje są obliczane leniwie: interpreter zapamiętuje wyrażenie i oblicza je dopiero, gdy ktoś o adnotacje zapyta — dlatego w adnotacji można użyć nazwy zdefiniowanej później. Do odczytu służy moduł `annotationlib`:

```python title="odczyt-adnotacji.py"
import annotationlib


def pole_kola(promien: float, dokladnosc: int = 2) -> float:
    return round(3.14159 * promien**2, dokladnosc)


print(annotationlib.get_annotations(pole_kola))
print(pole_kola.__annotations__ == annotationlib.get_annotations(pole_kola))
```

```{ .text .no-copy }
{'promien': <class 'float'>, 'dokladnosc': <class 'int'>, 'return': <class 'float'>}
True
```

Wyrażenia w adnotacjach mają własny zasięg, zapowiedziany w rozdziale 6 obok zasięgów LEGB: widzą nazwy funkcji otaczającej oraz — inaczej niż ciało metody z rozdziału [10. Klasy i obiekty](../10-klasy/atrybuty-i-metody.md#zasieg-ciaa-klasy) — nazwy z ciała klasy, w której stoi sygnatura, a obliczane są dopiero na żądanie. Programy rzadko czytają adnotacje same; robią to za nie narzędzia opisane dalej.

## Typy złożone

Typy kolekcji zapisujemy nawiasami kwadratowymi na typach wbudowanych, a alternatywę — kreską pionową:

```python title="typy-zlozone.py"
from collections.abc import Callable, Iterable
from typing import Any


def srednia(liczby: Iterable[float]) -> float:
    dane = list(liczby)
    return sum(dane) / len(dane)


def znajdz(slownik: dict[str, int], klucz: str) -> int | None:
    return slownik.get(klucz)


def zastosuj(funkcja: Callable[[int], str], wartosc: int) -> str:
    return funkcja(wartosc)


def wypisz(cokolwiek: Any) -> None:
    print(cokolwiek)


print(srednia([1, 2, 3]), srednia(x * 0.5 for x in range(4)))
print(znajdz({"a": 1}, "a"), znajdz({"a": 1}, "b"))
print(zastosuj(lambda n: "*" * n, 3))
wypisz([1, "dwa", 3.0])
```

```{ .text .no-copy }
2.0 0.75
1 None
***
[1, 'dwa', 3.0]
```

| Zapis | Znaczenie |
|---|---|
| `list[int]`, `dict[str, float]`, `set[str]` | kolekcja o elementach danego typu |
| `tuple[int, str]`, `tuple[int, ...]` | krotka o ustalonych typach pozycji; krotka dowolnej długości |
| `int \| None` | wartość albo `None` (dawniej `Optional[int]`) |
| `int \| str` | jeden z kilku typów (dawniej `Union[int, str]`) |
| `Iterable[float]` | cokolwiek, po czym można iterować — lista, krotka, generator |
| `Callable[[int], str]` | obiekt wywoływalny przyjmujący `int` i zwracający `str` |
| `Any` | dowolny typ; wyłącza sprawdzanie w tym miejscu |

Parametry deklarujemy możliwie ogólnie (`Iterable`, gdy funkcja tylko iteruje), a wyniki — możliwie konkretnie. Typy `Iterable` i `Callable` importujemy z `collections.abc`, znanego z rozdziału 11. W starszym kodzie spotkamy `from typing import List, Dict, Optional` — te zapisy, odnotowane już w rozdziale 3, działają, ale od Pythona 3.9 (kolekcje) i 3.10 (alternatywa `|`) są zbędne, a Ruff z następnego podrozdziału proponuje ich zamianę.

## Aliasy i generyki

Instrukcja `type` (od Pythona 3.12) nadaje typowi nazwę, a nawiasy kwadratowe po nazwie funkcji deklarują **parametr typu** (ang. *type parameter*) — typ, który sprawdzacz ustala osobno dla każdego wywołania:

```python title="aliasy.py"
type Wektor = list[float]
type Macierz = list[Wektor]


def skaluj(wektor: Wektor, k: float) -> Wektor:
    return [x * k for x in wektor]


def pierwszy[T](elementy: list[T]) -> T:
    return elementy[0]


def pary[K, V](slownik: dict[K, V]) -> list[tuple[K, V]]:
    return list(slownik.items())


print(skaluj([1.0, 2.5], 2))
print(pierwszy([3, 4]), pierwszy(["a", "b"]))
print(pary({"x": 1}))
print(Wektor, Wektor.__value__)
```

```{ .text .no-copy }
[2.0, 5.0]
3 a
[('x', 1)]
Wektor list[float]
```

Funkcja `pierwszy` jest **generyczna** (ang. *generic*): dla listy liczb sprawdzacz wie, że wynik jest liczbą, a dla listy napisów — napisem, bez osobnych definicji. Ta składnia pochodzi z PEP 695; starszy zapis z `TypeVar` z modułu `typing` działa nadal. Alias `Wektor` jest obiektem, który pamięta swoją definicję, i można go używać w innych aliasach, jak `Macierz`.

## `TypedDict`, klasy danych i `Protocol`

Słownik z ustalonym zestawem kluczy — na przykład wczytany z JSON w rozdziale 9 — opisuje **`TypedDict`**: w czasie wykonania to zwykły `dict`, ale sprawdzacz zna nazwy i typy kluczy:

```python title="slowniki-typowane.py"
from dataclasses import dataclass
from typing import TypedDict


class Osoba(TypedDict):
    imie: str
    wiek: int


@dataclass
class Punkt:
    x: float
    y: float


osoba: Osoba = {"imie": "Anna", "wiek": 30}
print(type(osoba).__name__, osoba["imie"], Osoba.__annotations__)
print(Punkt(1, 2), Punkt.__annotations__)
```

```{ .text .no-copy }
dict Anna {'imie': <class 'str'>, 'wiek': <class 'int'>}
Punkt(x=1, y=2) {'x': <class 'float'>, 'y': <class 'float'>}
```

Wybór między trzema narzędziami jest prosty: `TypedDict` opisuje dane zewnętrzne, które program otrzymuje jako słowniki; klasa danych z rozdziału [12. Programowanie obiektowe — mechanizmy zaawansowane](../12-oop-zaawansowane/klasy-danych.md#dekorator-dataclass) — dane własne, dla których chcemy metod i `__repr__`; a `Protocol` z tego samego rozdziału opisuje zachowanie, nie dane. Klasa danych czyta adnotacje w czasie wykonania, aby wygenerować `__init__`; protokół natomiast służy przede wszystkim sprawdzaczowi typów, który porównuje strukturę klas bez uruchamiania programu — to zastosowanie zapowiedzieliśmy w sekcji o [typowaniu kaczym](../12-oop-zaawansowane/mixiny-i-abstrakcja.md#typowanie-kacze-i-typingprotocol-dla-dociekliwych).

## Sprawdzacz typów mypy

**mypy** — sprawdzacz typów znany z rozszerzenia Mypy Type Checker z rozdziału [3. Nazwy i typy](../03-nazwy-typy/konwersje-i-adnotacje.md#adnotacje-typow-type-hinting) — uruchamiamy tu z wiersza poleceń: instalujemy go w środowisku wirtualnym projektu i wskazujemy plik lub katalog:

```powershell title="Terminal"
python -m pip install mypy
```

Program poniżej działa i wypisuje poprawne wyniki, lecz poprawność ta jest przypadkowa — adnotacje mówią co innego niż kod:

```python title="bledy.py"
def podwoj(x: int) -> int:
    return x * 2


def znajdz(identyfikator: int) -> str | None:
    return None if identyfikator < 0 else "obiekt"


wynik: str = podwoj(5)
print(wynik)
print(znajdz(1).upper())
```

```{ .text .no-copy }
10
OBIEKT
```

```powershell title="Terminal"
python -m mypy bledy.py
```

```{ .text .no-copy }
bledy.py:9: error: Incompatible types in assignment (expression has type "int", variable has type "str")  [assignment]
bledy.py:11: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
Found 2 errors in 1 file (checked 1 source file)
```

Pierwszy błąd to niezgodność deklaracji z wartością; drugi — wywołanie metody na wartości, która może być `None`: dla `znajdz(-1)` program zakończyłby się wyjątkiem `AttributeError`, a mypy wskazuje to miejsce bez uruchamiania kodu. Kod błędu w nawiasie kwadratowym pozwala wyciszyć pojedynczy wiersz komentarzem `# type: ignore[union-attr]`, gdy sprawdzacz nie zna kontekstu — z umiarem, bo każdy taki komentarz wyłącza fragment kontroli typów. Konfigurację zapisujemy w `pyproject.toml` z rozdziału 7:

```toml title="pyproject.toml"
[tool.mypy]
python_version = "3.14"
strict = true
```

Bez `strict` mypy sprawdza tylko funkcje z adnotacjami, co pozwala wdrażać typy stopniowo; tryb ścisły wymaga adnotacji wszędzie i ostrzega, gdy wartość `Any` trafia do funkcji zadeklarowanej jako zwracająca konkretny typ oraz gdy typ generyczny występuje bez parametrów (gołe `list`); jawne `Any` w adnotacji pozostaje dozwolone. W nowym projekcie włączamy go od początku. Polecenie `python -m mypy .` sprawdza cały projekt, a wywołanie `reveal_type(wyrazenie)` w kodzie każe mypy wypisać, jaki typ wyprowadził — przydatne przy nauce; mypy rozpoznaje tę nazwę bez importu, ale uruchomienie programu wymaga `from typing import reveal_type` albo usunięcia wywołania.

## Inne sprawdzacze typów (dla dociekliwych)

| Narzędzie | Autor, język implementacji | Uwagi (stan na wrzesień 2026) |
|---|---|---|
| mypy 2.3 | społeczność, Python | referencyjny; rozwijany najdłużej ze wszystkich |
| pyright 1.1 | Microsoft, TypeScript | silnik rozszerzenia Pylance w VSC — podkreśla błędy podczas pisania |
| Pyrefly 1.3 | Meta, Rust | szybki, z rozszerzeniem do VSC |
| ty 0.0.x | Astral (twórcy Ruff), Rust | w wersji rozwojowej; z rozszerzeniem do VSC |

Wszystkie czytają te same adnotacje i realizują te same dokumenty PEP o typach, choć w szczegółach różnią się wyprowadzaniem typów; w projekcie wybieramy jedno narzędzie do sprawdzeń automatycznych z podrozdziału [Automatyzacja jakości](automatyzacja-jakosci.md), a edytor może korzystać z innego. W VSC błędy typów pokazuje rozszerzenie **Mypy Type Checker** zainstalowane w rozdziale 3; Pylance, dostarczany z rozszerzeniem Python, robi to również — o ile nie wyłączyliśmy go zgodnie z podrozdziałem [Konfigurowanie narzędzi](../01-instalacja/konfiguracja.md#usuwanie-pylance) rozdziału 1.
