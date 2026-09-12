# Struktura projektu i pierwsze testy

Pakiet `geometria` z poprzedniego podrozdziału to już więcej niż skrypt: kilka modułów i wspólny interfejs. Taki kod zaczyna wymagać dwóch rzeczy, których pojedynczy plik nie potrzebował — sposobu sprawdzania, czy funkcje nadal działają poprawnie po każdej zmianie, oraz przewidywalnego układu katalogów, dzięki któremu kod daje się importować bez względu na to, skąd uruchomiono program. Ten podrozdział wprowadza jedno i drugie w najprostszej postaci: instrukcję `assert`, testy jako zwykłe funkcje, narzędzie pytest, układ `src` z plikiem `pyproject.toml` oraz instalację projektu w środowisku wirtualnym. Nie jest to kurs testowania ani pakowania projektów — pokazujemy tylko tyle, ile potrzeba, by projekt z kilku modułów był uporządkowany i sprawdzalny.

## Od skryptu do projektu

Przez **projekt** rozumiemy katalog zawierający kod (pakiet), testy i pliki pomocnicze. Zacznijmy od **układu płaskiego** (ang. *flat layout*), w którym pakiet i katalog testów leżą bezpośrednio w katalogu projektu. Pakiet `geometria` przyjmujemy w uproszczonej postaci, z jednym podmodułem — pozostałe podmoduły pomijamy dla zwięzłości, a wszystko, co pokażemy, przebiega z nimi tak samo:

```{ .text .no-copy }
projekt/
├── geometria/
│   ├── __init__.py
│   └── figury.py
├── tests/
│   ├── __init__.py
│   └── test_figury.py
└── program.py
```

```python title="geometria/__init__.py"
"""Udostępnia narzędzia geometryczne: pola figur."""

from .figury import pole_kola, obwod_kola

__all__ = ["pole_kola", "obwod_kola"]
```

```python title="geometria/figury.py"
"""Oblicza pola i obwody figur."""

import math


def pole_kola(promien):
    """Zwraca pole koła o podanym promieniu."""
    return math.pi * promien ** 2


def obwod_kola(promien):
    """Zwraca obwód koła o podanym promieniu."""
    return 2 * math.pi * promien
```

```python title="program.py"
from geometria import pole_kola

print(pole_kola(1))
```

```{ .text .no-copy }
3.141592653589793
```

Program działa, bo uruchamiamy go z katalogu `projekt`: zgodnie z regułami z sekcji [Ścieżka wyszukiwania modułów](moduly-i-import.md#sciezka-wyszukiwania-moduow) katalog skryptu trafia na początek `sys.path`, a przy `python -m` — katalog bieżący. W obu przypadkach jest to `projekt`, więc pakiet `geometria` jest osiągalny. Ta zależność od katalogu roboczego jest cechą układu płaskiego, do której wrócimy w drugiej części podrozdziału. Katalog `tests` tworzymy jako pakiet regularny z pustym `__init__.py` — dla jawnej, jednolitej struktury, tak jak wszystkie pakiety w tej książce; polecenie `python -m tests.test_figury`, którego użyjemy niżej, działałoby także bez tego pliku, z `tests` jako pakietem przestrzeni nazw. Zawartość `test_figury.py` powstanie w sekcji o katalogu `tests`.

## Instrukcja `assert`

Zanim napiszemy test, potrzebujemy narzędzia do zapisania oczekiwania. Instrukcja `assert` sprawdza **założenie** (ang. *assertion*) programu: wyrażenie po słowie kluczowym musi być prawdziwe, a jeśli nie jest, instrukcja zgłasza wyjątek `AssertionError`, który — jak każdy nieprzechwycony wyjątek — przerywa program śladem wywołań i kodem `1`. Drugie, opcjonalne wyrażenie po przecinku staje się komunikatem tego wyjątku. Sprawdźmy to plikiem próbnym, który nie należy do projektu:

```python title="zalozenie.py"
def srednia(dane):
    """Zwraca średnią arytmetyczną niepustej listy."""
    assert len(dane) > 0, "lista nie może być pusta"
    return sum(dane) / len(dane)


print(srednia([2, 4]))
print(srednia([]))
```

```{ .text .no-copy }
3.0
Traceback (most recent call last):
  File "zalozenie.py", line 8, in <module>
    print(srednia([]))
          ~~~~~~~^^^^
  File "zalozenie.py", line 3, in srednia
    assert len(dane) > 0, "lista nie może być pusta"
           ^^^^^^^^^^^^^
AssertionError: lista nie może być pusta
```

Pierwsze wywołanie przeszło przez `assert` bez skutku, drugie zatrzymało program na założeniu, które nie było spełnione. Bez drugiego wyrażenia ślad kończy się samym `AssertionError`. Instrukcja `assert` służy do wykrywania błędów w programie — sytuacji, które według programisty nie powinny wystąpić — a nie do sprawdzania danych od użytkownika: użytkownik, który poda pustą listę, powinien otrzymać zrozumiały komunikat, nie ślad wywołań. Właściwe narzędzia do tego, wraz z pełnym modelem wyjątków, omawia sekcja [Instrukcja `raise`](../08-wyjatki/zglaszanie-wyjatkow.md#instrukcja-raise); opcję interpretera, która pozwala pominąć instrukcje `assert` przy uruchamianiu, opisuje sekcja [Instrukcja `assert` a wyjątki](../08-wyjatki/zglaszanie-wyjatkow.md#instrukcja-assert-a-wyjatki).

Częsty błąd początkujących to ujęcie warunku i komunikatu w nawiasy, tak jakby `assert` był funkcją. Nawiasy z przecinkiem tworzą krotkę, a niepusta krotka jest zawsze prawdziwa, więc takie założenie nigdy nie zawodzi. Kompilator CPythona ostrzega o tym podczas kompilacji pliku — ostrzeżenie trafia na strumień błędów, zanim program się rozpocznie — ale program wykonuje się dalej:

```python title="krotka.py"
x = 2
assert (x == 3, "x powinno być równe 3")
print("program wykonuje się dalej")
```

```{ .text .no-copy }
krotka.py:2: SyntaxWarning: assertion is always true, perhaps remove parentheses?
  assert (x == 3, "x powinno być równe 3")
program wykonuje się dalej
```

### Porównania liczb zmiennoprzecinkowych

Założenia dotyczące liczb zmiennoprzecinkowych wymagają ostrożności. Pułapkę z podrozdziału [Typy proste](../03-nazwy-typy/typy-proste.md#typ-float) łatwo przenieść do testu:

```{ .python .no-copy }
>>> 0.1 + 0.2 + 0.3 == 0.6
False
>>> 0.1 + 0.2 + 0.3
0.6000000000000001
>>> import math
>>> math.isclose(0.1 + 0.2 + 0.3, 0.6)
True
>>> from decimal import Decimal
>>> Decimal("0.1") + Decimal("0.2") + Decimal("0.3") == Decimal("0.6")
True
```

Wybór narzędzia zależy od problemu. Gdy wynik jest z natury przybliżony — pole koła, pierwiastek, średnia — sprawdzamy bliskość funkcją `math.isclose()`, a nie równość. Gdy dane są z natury dziesiętne i dokładne, jak kwoty, właściwym typem jest `Decimal` tworzony z łańcuchów znaków (`Decimal("0.1")`, nie `Decimal(0.1)`, bo literał `0.1` już jest przybliżeniem). Zaokrąglenie wyniku funkcją `round()` to jeszcze inna operacja: zmienia wartość, którą program pokazuje, ale nie rozstrzyga, czy dwie obliczone wartości są równe.

## Katalog `tests`

**Funkcja testowa** — krócej: test — to funkcja, która wywołuje sprawdzany kod i zapisuje oczekiwania instrukcją `assert`. Nie potrzebuje niczego więcej: jeśli wszystkie założenia są spełnione, kończy się bez skutku; jeśli nie — zatrzymuje się na pierwszym niespełnionym. Umieszczamy testy w pliku `tests/test_figury.py`, po jednej funkcji na sprawdzaną właściwość, a na końcu dodajemy funkcję `main()`, która wywołuje je po kolei:

```python title="tests/test_figury.py"
"""Sprawdza funkcje modułu geometria.figury."""

import math

from geometria.figury import pole_kola, obwod_kola


def test_pole_kola():
    """Sprawdza pole koła dla promienia 0 i 1."""
    assert pole_kola(0) == 0
    assert math.isclose(pole_kola(1), math.pi)


def test_obwod_kola():
    """Sprawdza obwód koła o promieniu 1."""
    assert math.isclose(obwod_kola(1), 2 * math.pi)


def main():
    """Uruchamia wszystkie testy z tego pliku."""
    test_pole_kola()
    test_obwod_kola()
    print("OK")


if __name__ == "__main__":
    main()
```

```powershell title="Terminal"
python -m tests.test_figury
```

```{ .text .no-copy }
OK
```

Nazwy zaczynające się od `test_` — pliku i funkcji — to konwencja, którą w następnej sekcji wykorzysta narzędzie do uruchamiania testów (pliki testów bywają też nazywane `*_test.py`, a w małych projektach leżą obok sprawdzanego modułu; w książce trzymamy się katalogu `tests` i przedrostka `test_`). Plik uruchamiamy przez `python -m tests.test_figury` z katalogu `projekt`, bo test importuje pakiet `geometria` tak, jak robiłby to program; bezpośrednie `python tests\test_figury.py` skończyłoby się `ModuleNotFoundError`, gdyż katalogiem skryptu, a więc pierwszym elementem `sys.path`, byłby wtedy `tests`. Program zakończył się kodem `0`: wszystkie założenia były spełnione.

Zmieńmy teraz oczekiwanie w drugim teście na błędne — zaokrągloną wartość porównywaną operatorem `==`:

```python title="tests/test_figury.py"
"""Sprawdza funkcje modułu geometria.figury."""

import math

from geometria.figury import pole_kola, obwod_kola


def test_pole_kola():
    """Sprawdza pole koła dla promienia 0 i 1."""
    assert pole_kola(0) == 0
    assert math.isclose(pole_kola(1), math.pi)


def test_obwod_kola():
    """Sprawdza obwód koła o promieniu 1."""
    assert obwod_kola(1) == 6.28


def main():
    """Uruchamia wszystkie testy z tego pliku."""
    test_pole_kola()
    test_obwod_kola()
    print("OK")


if __name__ == "__main__":
    main()
```

```powershell title="Terminal"
python -m tests.test_figury
```

```{ .text .no-copy }
Traceback (most recent call last):
...
  File "C:\...\projekt\tests\test_figury.py", line 27, in <module>
    main()
    ~~~~^^
  File "C:\...\projekt\tests\test_figury.py", line 22, in main
    test_obwod_kola()
    ~~~~~~~~~~~~~~~^^
  File "C:\...\projekt\tests\test_figury.py", line 16, in test_obwod_kola
    assert obwod_kola(1) == 6.28
           ^^^^^^^^^^^^^^^^^^^^^
AssertionError
```

Niespełnione założenie przerwało program śladem wywołań, a kod wyjścia wyniósł `1` — jak przy każdym nieprzechwyconym wyjątku. Ślad rozpoczyna się dwiema ramkami mechanizmu uruchamiającego `-m`, które pominęliśmy wierszem `...`; istotne są ramki wskazujące plik testów. Taki sposób uruchamiania ma jednak wyraźne ograniczenia: wykonanie zatrzymuje się na pierwszym niezaliczonym teście, nie wiemy, ile testów przeszło, a `AssertionError` bez komunikatu nie mówi, jaką wartość funkcja zwróciła. Każdy nowy test trzeba też ręcznie dopisać do `main()`.

## Narzędzie pytest

Te ograniczenia usuwa **pytest** — narzędzie do uruchamiania testów. Nie należy ono do biblioteki standardowej; jest pakietem zewnętrznym, który instalujemy w aktywnym środowisku wirtualnym tak, jak w podrozdziale [Wirtualne środowisko venv](../01-instalacja/venv.md#instalowanie-pakietow-w-srodowisku):

```powershell title="Terminal"
python -m pip install pytest
```

Po instalacji polecenie `python -m pytest` wydane w katalogu projektu samo odnajduje pliki `test_*.py` (a także `*_test.py`), a w nich funkcje `test_*`, i wywołuje każdą z nich osobno. Jak każde `python -m`, umieszcza ono katalog bieżący na początku `sys.path`, więc testy importują pakiet `geometria` tak samo jak przy `python -m tests.test_figury`. Same funkcje testowe nie wymagają zmian; funkcja `main()` i warunek uruchomienia modułu przestają być potrzebne. Uruchommy pytest na wersji z błędnym oczekiwaniem:

```powershell title="Terminal"
python -m pytest
```

```{ .text .no-copy }
...
collected 2 items

tests\test_figury.py .F                                                  [100%]

================================== FAILURES ===================================
_______________________________ test_obwod_kola _______________________________

    def test_obwod_kola():
        """Sprawdza obwód koła o promieniu 1."""
>       assert obwod_kola(1) == 6.28
E       assert 6.283185307179586 == 6.28
E        +  where 6.283185307179586 = obwod_kola(1)

tests\test_figury.py:16: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_figury.py::test_obwod_kola - assert 6.283185307179586 == 6.28
========================= 1 failed, 1 passed in 0.01s =========================
```

Raport pominięty na początku wierszem `...` zawiera nagłówek z wersjami narzędzi i informacjami o katalogu projektu; czas w ostatnim wierszu oraz szerokość separatorów z `=` i położenie `[100%]` zależą od komputera i szerokości okna terminala, dlatego cytujemy tylko treść wierszy, nie ich układ. Kropka i litera `F` w wierszu `tests\test_figury.py .F` oznaczają kolejno test zaliczony i niezaliczony; sekcja `FAILURES` pokazuje wiersz z niespełnionym założeniem wraz z wartościami obu stron porównania — pytest sam wypisuje, że `obwod_kola(1)` zwróciło `6.283185307179586`, czego zwykły `AssertionError` nie mówił. Wiersz postępu podaje ścieżkę pliku w zapisie Windows, a wiersz `FAILED` — identyfikator testu `plik::funkcja`, w którym pytest zawsze używa ukośnika. Program zakończył się kodem `1`. Przywracamy w `test_obwod_kola()` porównanie przez `math.isclose()` i usuwamy zbędne już `main()` wraz z warunkiem uruchomienia modułu — od tej pory testy uruchamia wyłącznie pytest:

```python title="tests/test_figury.py"
"""Sprawdza funkcje modułu geometria.figury."""

import math

from geometria.figury import pole_kola, obwod_kola


def test_pole_kola():
    """Sprawdza pole koła dla promienia 0 i 1."""
    assert pole_kola(0) == 0
    assert math.isclose(pole_kola(1), math.pi)


def test_obwod_kola():
    """Sprawdza obwód koła o promieniu 1."""
    assert math.isclose(obwod_kola(1), 2 * math.pi)
```

```powershell title="Terminal"
python -m pytest
```

```{ .text .no-copy }
...
collected 2 items

tests\test_figury.py ..                                                  [100%]

============================== 2 passed in 0.01s ==============================
```

Kod wyjścia `0` oznacza, że wszystkie zebrane testy zostały zaliczone, kod `1` — że co najmniej jeden nie przeszedł; pytest ma także inne kody dla innych sytuacji, na przykład gdy nie znalazł żadnego testu albo nie mógł zaimportować pliku testów. W katalogu projektu pojawia się przy tym katalog roboczy `.pytest_cache`, który — jak `__pycache__` — pomijamy w drzewach. Na tym poprzestajemy: pytest ma wiele dalszych możliwości, które poznamy w rozdziale poświęconym warsztatowi programisty. Jedno zastrzeżenie: pytest jest narzędziem pracy nad projektem, a nie częścią programu, więc nie trafia do zależności projektu, o których mowa w następnej sekcji.

## Układ `src` i plik `pyproject.toml`

Wróćmy do zależności od katalogu roboczego. W układzie płaskim pakiet `geometria` jest importowalny tylko dlatego, że katalog `projekt` znajduje się na ścieżce wyszukiwania — jako katalog skryptu albo katalog bieżący. Wystarczy uruchomić program z innego miejsca, by import zawiódł, a na ścieżce wyszukiwania znajdują się wtedy także `tests` i `program`, choć nie są przeznaczone do importowania. Rozwiązaniem przyjętym w samouczku pakowania projektów w Pythonie i zalecanym przez dokumentację pytest jest **układ `src`** (ang. *src layout*): w katalogu projektu tworzymy podkatalog `src` i przenosimy do niego katalog `geometria` (w eksploratorze plików albo w panelu VSC); katalog `tests` i plik `program.py` pozostają na miejscu, a obok powstaje plik `pyproject.toml` opisujący projekt.

<!-- verify: move geometria src/geometria -->

```{ .text .no-copy }
projekt/
├── pyproject.toml
├── program.py
├── src/
│   └── geometria/
│       ├── __init__.py
│       └── figury.py
└── tests/
    ├── __init__.py
    └── test_figury.py
```

Po przeniesieniu pakiet przestaje być osiągalny z katalogu projektu — `src` nie jest na ścieżce wyszukiwania:

```powershell title="Terminal"
python -c "import geometria"
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import geometria
ModuleNotFoundError: No module named 'geometria'
```

To zamierzony skutek: w układzie `src` kod projektu importuje się przez **zainstalowany pakiet**, a nie przypadkiem przez katalog roboczy. Dzięki temu testy i programy sprawdzają dokładnie to, co otrzyma użytkownik pakietu, a nazwa `geometria` działa z każdego katalogu. Układ ten nie jest obowiązkowy — małe projekty często pozostają płaskie — ale jest dobrze udokumentowaną praktyką i od tej pory stosujemy go w książce.

Instalację umożliwia plik `pyproject.toml`. Zapisany jest w formacie TOML, który przypomina `settings.json` z podrozdziału [Konfigurowanie narzędzi](../01-instalacja/konfiguracja.md), lecz jest prostszy: składa się z **tabel** (ang. *table*) oznaczanych nagłówkiem w nawiasach kwadratowych i par `klucz = wartość`, gdzie wartością może być łańcuch w cudzysłowach albo lista w nawiasach kwadratowych. Minimalny plik dla naszego projektu:

```toml title="pyproject.toml"
[build-system]
requires = ["hatchling >= 1.26"]
build-backend = "hatchling.build"

[project]
name = "geometria"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = []
```

Tabela `[build-system]` określa narzędzia potrzebne do zbudowania i zainstalowania projektu: **backend budowania** (ang. *build backend*), tu Hatchling, oraz jego minimalną wersję (`>= 1.26`, jak w samouczku pakowania; pip pobierze najnowszą wersję spełniającą ten warunek). Hatchling jest jednym z kilku dostępnych backendów — konkretnym wyborem tego przykładu, a nie elementem samego formatu `pyproject.toml`. Tabela `[project]` przechowuje metadane projektu: nazwę i wersję, minimalną wersję Pythona oraz `dependencies` — listę pakietów zewnętrznych, których projekt potrzebuje do działania, na razie pustą.

Nazwa w kluczu `name` to nazwa **pakietu dystrybucyjnego** — tej jednostki, którą pip instaluje i wyświetla — a nie nazwa pakietu importowanego w Pythonie. W naszym przykładzie obie brzmią `geometria`, ale Python nie wymaga, by były identyczne: projekt o nazwie dystrybucyjnej `moje-narzedzia` może udostępniać pakiet importowany `narzedzia`. Hatchling w tak prostej konfiguracji jak nasza odnajduje kod automatycznie właśnie po zgodności nazwy projektu z nazwą katalogu w `src`; przy nazwach różnych trzeba by wskazać katalog pakietu w dodatkowej tabeli konfiguracji — to właściwość wybranego backendu, nie ogólna reguła pakowania.

## Instalacja edytowalna w środowisku wirtualnym

Projekt instalujemy w aktywnym środowisku wirtualnym poleceniem pip z opcją `-e`, wskazując katalog projektu (kropka oznacza katalog bieżący):

```powershell title="Terminal"
python -m pip install -e .
```

Pip odczytuje `pyproject.toml`, przygotowuje wskazany backend budowania — pobierając go, jeśli nie jest jeszcze dostępny, jak przy każdej instalacji pakietu — i kończy komunikatem `Successfully installed geometria-0.1.0`. Jest to **instalacja edytowalna** (ang. *editable install*): środowisko otrzymuje wpis instalacyjny powiązany z katalogiem projektu, więc interpreter importuje kod wprost z `src`, a zmiany w plikach źródłowych są widoczne bez ponownej instalacji. Zainstalowany projekt widać w spisie pakietów środowiska:

```powershell title="Terminal"
python -m pip show geometria
```

```{ .text .no-copy }
Name: geometria
Version: 0.1.0
...
Editable project location: C:\...\projekt
...
```

Wiersze oznaczone `...` to pola metadanych, których w minimalnym `pyproject.toml` nie wypełniliśmy, oraz ścieżka do `site-packages` środowiska; istotny jest wiersz `Editable project location`, wskazujący katalog projektu. Od tej chwili pakiet `geometria` importuje się z dowolnego katalogu, a testy i program nie zależą już od tego, czy katalog projektu jest pierwszym elementem ścieżki wyszukiwania — pakiet jest odnajdywany przez wpis instalacyjny w środowisku:

```powershell title="Terminal"
python -m pytest
cd ..
python projekt\program.py
python -c "import geometria; print(geometria.__file__)"
```

```{ .text .no-copy }
...
collected 2 items

tests\test_figury.py ..                                                  [100%]

============================== 2 passed in 0.01s ==============================
3.141592653589793
C:\...\projekt\src\geometria\__init__.py
```

Atrybut `__file__` wskazuje plik w katalogu projektu — nie kopię w `site-packages` — bo instalacja jest edytowalna. Z katalogu nadrzędnego katalog `tests` nie jest natomiast osiągalny: po instalacji z dowolnego miejsca dostępny jest wyłącznie pakiet z `src`, dokładnie tak, jak w środowisku użytkownika; w katalogu projektu `tests` pozostaje importowalny tylko na mocy reguły katalogu bieżącego. Lista `dependencies` z `pyproject.toml` odpowiada plikowi `requirements.txt` z podrozdziału [Pip — zarządzanie pakietami](../01-instalacja/pip.md#plik-requirementstxt), ale opisuje potrzeby samego pakietu, które pip instaluje razem z nim; narzędzia pracy, jak pytest, instalujemy w środowisku osobno.

!!! note "Układ z laboratorium 3"
    Materiały laboratorium 3 (zajęć kursu, do którego książka jest materiałem
    pomocniczym) stosują inny wariant struktury: katalog `src` zawiera tam plik
    `__init__.py` i jest importowany jako pakiet o nazwie `src`
    (`from src.kalkulator import dodaj`), bez `pyproject.toml` i instalacji.
    Taki układ działa tylko dlatego, że pytest wstawia katalog projektu na
    ścieżkę wyszukiwania (katalog `tests` ma `__init__.py`, więc jego katalog
    nadrzędny staje się pierwszą pozycją `sys.path`), ale nazwa `src` nie jest
    nazwą biblioteki, a projekt bez `pyproject.toml` nie jest przygotowany do
    instalacji. W książce `src` jest wyłącznie katalogiem, a pakietem jest
    `src/geometria` — układ stosowany w samouczku pakowania projektów.

Projekt ma teraz kompletny szkielet: pakiet w `src`, testy w `tests`, opis w `pyproject.toml` i instalację w środowisku wirtualnym. Trzy ostatnie podrozdziały poświęcamy modułom, których nie piszemy samodzielnie, lecz importujemy z biblioteki standardowej.
