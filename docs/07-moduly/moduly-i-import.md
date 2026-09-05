# Moduły i instrukcja import

Dotychczas każdy program mieścił się w jednym pliku, a instrukcji `import` używaliśmy okazjonalnie: dla `math` w rozdziale [2. Konsola](../02-konsola/konsola-w-praktyce.md#funkcje-matematyczne), dla `sys` w rozdziale [1. Instalacja i środowisko pracy](../01-instalacja/sciezki-i-utrzymanie.md#syspath-drugie-znaczenie-sciezki) i w podrozdziale [Obiekty i pamięć](../03-nazwy-typy/obiekty-i-pamiec.md), dla `keyword` w podrozdziale [Nazwy i słowa kluczowe](../03-nazwy-typy/nazwy-i-slowa-kluczowe.md#sowa-kluczowe), dla `Decimal` i `Fraction` w podrozdziale [Typy proste](../03-nazwy-typy/typy-proste.md#typ-float). W tym podrozdziale instrukcja `import` staje się tematem głównym. Zbudujemy model, na którym opiera się reszta rozdziału: plik źródłowy jest **modułem**, moduł jest obiektem z własną przestrzenią nazw, jego kod wykonuje się podczas pierwszego importu, a interpreter przechowuje raz wczytany moduł w pamięci podręcznej i szuka modułów w ściśle określonych katalogach.

Mechanizm najlepiej pokazać na module własnym, a nie bibliotecznym — wtedy widać każdy jego krok.

## Moduł jako plik i jako obiekt

**Moduł** (ang. *module*) to plik z kodem Pythona. Jego nazwą jest nazwa pliku bez rozszerzenia `.py`, dlatego musi być poprawnym identyfikatorem według zasad z rozdziału [3. Nazwy i typy](../03-nazwy-typy/nazwy-i-slowa-kluczowe.md#zasady-nazywania): `narzedzia.py` jest modułem `narzedzia`, ale pliku `moje-narzedzia.py` nie da się zaimportować instrukcją `import`, bo `moje-narzedzia` nie jest identyfikatorem. Skrypty uruchamiane bezpośrednio, jak `pole-prostokata.py` z rozdziału 6, mogą nosić dowolne nazwy; plik przeznaczony do importu nazywamy w konwencji `snake_case`.

Zapiszmy prosty moduł z docstringiem, stałą i funkcją:

```python title="narzedzia.py"
"""Udostępnia proste narzędzia do pracy z tekstem."""

SEPARATOR = "-"


def policz_slowa(tekst):
    """Zwraca liczbę słów w tekście."""
    return len(tekst.split())
```

W tym samym katalogu — nazwijmy go `projekt` i w nim otwierajmy terminal — umieszczamy program, który z modułu korzysta:

```python title="program.py"
import narzedzia

zdanie = "Moduł to plik z kodem Pythona"
print(narzedzia.policz_slowa(zdanie))
print(narzedzia.SEPARATOR * 10)
```

```{ .text .no-copy }
6
----------
```

Instrukcja `import narzedzia` wczytuje plik `narzedzia.py` i wiąże nazwę `narzedzia` z **obiektem modułu**. Do nazw zdefiniowanych w pliku — funkcji `policz_slowa` i stałej `SEPARATOR` — sięgamy przez kropkę, tak jak do metod i atrybutów innych obiektów. Moduł jest bowiem zwykłym obiektem, co można sprawdzić w konsoli uruchomionej w katalogu `projekt`:

```{ .python .no-copy }
>>> import narzedzia
>>> type(narzedzia)
<class 'module'>
>>> type(narzedzia).__name__
'module'
>>> narzedzia.__name__
'narzedzia'
>>> narzedzia.__file__.endswith("narzedzia.py")
True
```

Obiekt modułu ma atrybuty opisujące jego pochodzenie. Atrybut `__name__` przechowuje nazwę modułu — tę samą, którą podaliśmy po `import`. Atrybut `__file__` zawiera pełną ścieżkę do pliku źródłowego, na przykład `C:\...\projekt\narzedzia.py`; jej początek zależy od tego, gdzie plik leży, dlatego w konsoli sprawdziliśmy tylko jej zakończenie metodą `endswith()`, bliźniaczą wobec `startswith()` z rozdziału 3.

Nie każdy moduł jest plikiem `.py`. Moduł `sys` jest wbudowany w interpreter i nie ma atrybutu `__file__`, a część modułów biblioteki standardowej to **moduły rozszerzeń** (ang. *extension modules*) skompilowane z języka C; inny rodzaj modułów, oparty na katalogach, poznamy w dalszej części rozdziału. Dla programu nie ma to znaczenia: każdy z nich importuje się tą samą instrukcją i każdy jest obiektem typu `module`. Obecność atrybutu sprawdza funkcja wbudowana `hasattr(obiekt, "nazwa")`, zwracająca `True` albo `False`:

```{ .python .no-copy }
>>> import sys
>>> hasattr(sys, "__file__")
False
```

### Docstring modułu

Pierwszy literał łańcuchowy w pliku jest **docstringiem modułu** — działa tu ten sam mechanizm, który opisaliśmy dla funkcji w podrozdziale [Definiowanie funkcji](../06-funkcje/definiowanie-funkcji.md#docstring-i-funkcja-help), i ten sam, o którym ostrzega pylint komunikatem *Missing module docstring* w podrozdziale [Konfigurowanie narzędzi](../01-instalacja/konfiguracja.md#wyciszanie-ostrzezen-pylint). Łańcuch trafia do atrybutu `__doc__` modułu i jest wykorzystywany przez funkcję `help()`:

```{ .python .no-copy }
>>> import narzedzia
>>> narzedzia.__doc__
'Udostępnia proste narzędzia do pracy z tekstem.'
>>> help(narzedzia)
```

```{ .text .no-copy }
Help on module narzedzia:

NAME
    narzedzia - Udostępnia proste narzędzia do pracy z tekstem.

FUNCTIONS
    policz_slowa(tekst)
        Zwraca liczbę słów w tekście.

DATA
    SEPARATOR = '-'

FILE
    c:\...\projekt\narzedzia.py
```

Funkcja `help()` składa opis z docstringu modułu, docstringów funkcji i listy pozostałych nazw; sekcja `FILE` zawiera ścieżkę zależną od komputera (funkcja `help()` wypisuje ją małymi literami), dlatego została tu skrócona. Docstring musi być pierwszą instrukcją pliku — mogą go poprzedzać jedynie komentarze i puste wiersze. Łańcuch umieszczony po instrukcji `import` albo po przypisaniu jest zwykłym wyrażeniem bez skutku, a `__doc__` modułu ma wtedy wartość `None`.

## Formy instrukcji import

Instrukcja `import` ma dwa skutki: zapewnia wczytanie modułu i **wiąże nazwę** w bieżącej przestrzeni nazw — dokładnie tak, jak przypisanie wiąże nazwę z obiektem w modelu z podrozdziału [Nazwy i słowa kluczowe](../03-nazwy-typy/nazwy-i-slowa-kluczowe.md#nazwa-jako-referencja). Cztery formy instrukcji różnią się tym, jaka nazwa zostaje związana i z jakim obiektem:

| Instrukcja | Wiązana nazwa | Obiekt |
|---|---|---|
| `import narzedzia` | `narzedzia` | moduł |
| `import narzedzia as n` | `n` (nazwa `narzedzia` nie powstaje) | moduł |
| `from narzedzia import policz_slowa` | `policz_slowa` (nazwa `narzedzia` nie powstaje) | funkcja z modułu |
| `from narzedzia import policz_slowa as policz` | `policz` | funkcja z modułu |

Wszystkie cztery prowadzą do tego samego obiektu funkcji:

```python title="formy.py"
import narzedzia
import narzedzia as n
from narzedzia import policz_slowa
from narzedzia import policz_slowa as policz

print(narzedzia.policz_slowa("a b c"))
print(n.policz_slowa("a b c"))
print(policz_slowa("a b c"))
print(policz("a b c"))
print(n is narzedzia, policz is narzedzia.policz_slowa)
```

```{ .text .no-copy }
3
3
3
3
True True
```

Alias po `as` jest przydatny przy długich nazwach modułów i w utrwalonych konwencjach bibliotek zewnętrznych. Forma `from … import …` pozwala pisać `policz_slowa(...)` zamiast `narzedzia.policz_slowa(...)`, ale nie tworzy nazwy `narzedzia` — moduł został wczytany, lecz nie jest w tej przestrzeni nazw dostępny pod własną nazwą:

```{ .python .no-copy }
>>> from narzedzia import policz_slowa
>>> policz_slowa("Ala ma kota")
3
>>> narzedzia
Traceback (most recent call last):
  File "<python-input-2>", line 1, in <module>
    narzedzia
NameError: name 'narzedzia' is not defined
>>> import narzedzia
>>> policz_slowa is narzedzia.policz_slowa
True
```

Forma `from … import …` nie kopiuje funkcji do bieżącego pliku. Nazwa `policz_slowa` i atrybut `narzedzia.policz_slowa` wskazują ten sam obiekt, a wiązanie powstaje w chwili wykonania instrukcji `import`. Późniejsze przypisanie nowego obiektu do atrybutu modułu nie zmienia więc wcześniej związanej nazwy — to dwa niezależne wiązania, jak dwie nazwy wskazujące ten sam obiekt w rozdziale [3. Nazwy i typy](../03-nazwy-typy/nazwy-i-slowa-kluczowe.md#nazwa-jako-referencja):

```{ .python .no-copy }
>>> import narzedzia
>>> from narzedzia import SEPARATOR
>>> narzedzia.SEPARATOR = "|"
>>> SEPARATOR
'-'
>>> narzedzia.SEPARATOR
'|'
```

Po `from` można wymienić kilka nazw rozdzielonych przecinkami: `from narzedzia import SEPARATOR, policz_slowa`. [PEP 8](https://peps.python.org/pep-0008/#imports) odradza natomiast importowanie kilku modułów jedną instrukcją (`import sys, narzedzia`) — każdy moduł w osobnym wierszu jest czytelniejszy.

### Import z gwiazdką i lista `__all__`

Składnia `from moduł import *` wiąże w bieżącej przestrzeni nazw wszystkie nazwy publiczne modułu, czyli te, które nie zaczynają się od podkreślenia. Moduł może zawęzić ten zestaw, definiując listę `__all__` z nazwami przeznaczonymi do takiego importu:

```python title="statystyka.py"
"""Udostępnia proste statystyki opisowe."""

__all__ = ["srednia"]


def srednia(dane):
    """Zwraca średnią arytmetyczną."""
    return sum(dane) / len(dane)


def mediana(dane):
    """Zwraca medianę."""
    posortowane = sorted(dane)
    n = len(posortowane)
    return (posortowane[(n - 1) // 2] + posortowane[n // 2]) / 2
```

```python title="gwiazdka.py"
from statystyka import *

print(srednia([1, 2, 3, 4]))
print(mediana([1, 2, 3, 4]))
```

```{ .text .no-copy }
2.5
Traceback (most recent call last):
  File "gwiazdka.py", line 4, in <module>
    print(mediana([1, 2, 3, 4]))
          ^^^^^^^
NameError: name 'mediana' is not defined
```

Import z gwiazdką wprowadził tylko `srednia`, bo tylko ta nazwa znajduje się w `__all__`; funkcja `mediana` istnieje w module i jest dostępna jako `statystyka.mediana` po zwykłym `import statystyka`. Bez listy `__all__` ta sama instrukcja wprowadziłaby obie funkcje.

Składnia ta istnieje, ale w zwykłym kodzie zasadniczo jej nie stosujemy. Po `from statystyka import *` czytelnik pliku nie wie, skąd pochodzi nazwa `srednia` ani jakie inne nazwy zostały niepostrzeżenie wprowadzone — a jeśli dwa moduły zaimportowane w ten sposób definiują tę samą nazwę, druga instrukcja przesłania pierwszą bez żadnego ostrzeżenia. Dodatkowe ograniczenie: import z gwiazdką jest dozwolony wyłącznie na poziomie modułu, a umieszczony w ciele funkcji kończy się błędem `SyntaxError: import * only allowed at module level`. Do listy `__all__` wrócimy przy pakietach, gdzie pełni ona szerszą rolę opisu publicznego interfejsu.

### Kolejność importów według PEP 8

PEP 8 zaleca umieszczać instrukcje `import` na początku pliku, bezpośrednio po docstringu modułu, w trzech grupach rozdzielonych pustym wierszem: najpierw moduły biblioteki standardowej, potem pakiety zewnętrzne instalowane osobno, na końcu moduły własne projektu. Szkic początku takiego pliku — grupę pakietów zewnętrznych, których jeszcze nie poznaliśmy, zaznacza komentarz:

```{ .python .no-copy }
"""Zestawia raport sprzedaży."""

import sys
from decimal import Decimal

# tu importy pakietów zewnętrznych zainstalowanych w środowisku wirtualnym

import narzedzia
import statystyka
```

Taki układ od razu mówi czytelnikowi, z czego plik korzysta i co trzeba zainstalować, by go uruchomić. Instrukcja `import` wykonana w środku pliku albo wewnątrz funkcji jest składniowo poprawna, ale w tej książce importujemy wyłącznie na początku pliku.

## Przestrzeń nazw modułu

Każdy moduł ma własną **globalną przestrzeń nazw**. W modelu LEGB z podrozdziału [Zasięg nazw i domknięcia](../06-funkcje/zasieg-nazw-i-domkniecia.md#przestrzenie-nazw-i-zasiegi) litera G oznacza właśnie przestrzeń nazw modułu, w którym funkcja została zdefiniowana — nie modułu, który ją wywołuje:

```python title="podatki.py"
"""Oblicza kwoty brutto według stawki VAT."""

STAWKA = 23


def brutto(netto):
    """Zwraca kwotę brutto dla podanej kwoty netto."""
    return netto * (1 + STAWKA / 100)
```

```python title="rachunek.py"
import podatki

STAWKA = 8
print(podatki.brutto(100))
print(STAWKA, podatki.STAWKA)
```

```{ .text .no-copy }
123.0
8 23
```

Funkcja `brutto()` nie znajduje nazwy `STAWKA` lokalnie, więc szuka jej w swojej przestrzeni globalnej, czyli w module `podatki`, i znajduje `23`. Nazwa `STAWKA` zdefiniowana w pliku `rachunek.py` należy do innej przestrzeni nazw i pozostaje niewidoczna dla funkcji — oba pliki mogą używać tej samej nazwy bez konfliktu. Na tym polega pożytek z modułów: każdy plik dostaje osobną przestrzeń nazw, a nazwy z innych modułów widzi tylko wtedy, gdy je zaimportuje.

Atrybuty modułu i jego nazwy globalne to ta sama przestrzeń nazw oglądana z dwóch stron. Przypisanie do atrybutu `podatki.STAWKA` zmienia nazwę globalną, którą funkcja `brutto()` odczytuje przy każdym wywołaniu:

```{ .python .no-copy }
>>> import podatki
>>> podatki.brutto(100)
123.0
>>> podatki.STAWKA = 8
>>> podatki.brutto(100)
108.0
```

Listę nazw z przestrzeni modułu zwraca funkcja `dir()`, znana z rozdziału [2. Konsola](../02-konsola/konsola-w-praktyce.md#pomoc-wbudowana-help-i-dir):

```{ .python .no-copy }
>>> import narzedzia
>>> dir(narzedzia)
['SEPARATOR', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', 'policz_slowa']
```

Obok `SEPARATOR` i `policz_slowa` widać nazwy techniczne, które interpreter dodaje do każdego modułu: poznaliśmy `__name__`, `__doc__` i `__file__`, a pozostałe to atrybuty techniczne systemu importu — część z nich dokumentacja oznacza jako przestarzałą, więc ich zestaw może się różnić między wersjami Pythona. Funkcja `dir()` jest narzędziem do oglądania przestrzeni nazw, nie specyfikacją tego, co moduł udostępnia — o tym mówią dokumentacja i ewentualna lista `__all__`. Wywołana bez argumentu, `dir()` zwraca nazwy bieżącej przestrzeni: w konsoli i w uruchomionym skrypcie jest nią również przestrzeń modułu głównego, którego nazwę poznamy w następnym podrozdziale.

## Wykonywanie modułu podczas importu

Atrybuty obiektu modułu powstają podczas importu: interpreter **wykonuje kod pliku** od góry do dołu, tak jak wykonywałby skrypt — instrukcja `def` tworzy obiekt funkcji i wiąże go z nazwą, przypisanie tworzy stałą, a każda inna instrukcja jest wykonywana tak samo jak w skrypcie, także `print()`. Efekt wykonania widać po module z instrukcją `print()`:

```python title="licznik.py"
"""Demonstruje wykonanie kodu modułu podczas importu."""

print("inicjalizacja modułu licznik")

WARTOSC = 0


def zwieksz():
    """Zwiększa licznik i zwraca nową wartość."""
    global WARTOSC
    WARTOSC += 1
    return WARTOSC
```

```python title="dwa-importy.py"
import licznik
import licznik

print(licznik.zwieksz())
print(licznik.zwieksz())
```

```{ .text .no-copy }
inicjalizacja modułu licznik
1
2
```

Komunikat pojawił się raz, choć instrukcja `import licznik` wystąpiła dwukrotnie, a licznik zachował stan między wywołaniami. Przebieg zwykłego importu wygląda następująco:

1. Interpreter sprawdza **pamięć podręczną modułów** — słownik `sys.modules`, który odwzorowuje nazwy modułów na obiekty modułów.
2. Jeżeli nazwy tam nie ma, odnajduje plik modułu (gdzie go szuka, opisuje następna sekcja), tworzy nowy obiekt modułu, zapisuje go w `sys.modules` i wykonuje kod pliku w przestrzeni nazw tego obiektu.
3. Wiąże nazwę w przestrzeni nazw importującego pliku — według jednej z form opisanych wyżej.

Ponowny import tej samej nazwy w tym samym procesie zwykle pomija krok drugi: interpreter bierze istniejący obiekt z `sys.modules` i od razu wiąże z nim nazwę, zamiast ponownie wykonywać kod modułu. Dlatego stan modułu — tu wartość `WARTOSC` — jest wspólny dla całego programu, a każdy plik, który wykona `import licznik`, otrzyma ten sam obiekt:

```python title="pamiec-podreczna.py"
import sys

import licznik

print("licznik" in sys.modules)
print(sys.modules["licznik"] is licznik)
print(type(sys.modules))
```

```{ .text .no-copy }
inicjalizacja modułu licznik
True
True
<class 'dict'>
```

Słownik `sys.modules` zawiera także moduły, których program nie importował jawnie, bo wczytał je sam interpreter podczas uruchamiania. Z modelu wynika praktyczna zasada: kod umieszczony na poziomie modułu wykonuje się podczas importu, więc moduł przeznaczony do importowania powinien na tym poziomie tylko definiować funkcje i stałe, a nie wykonywać obliczeń ani wypisywać wyników. Jak pogodzić to z plikiem, który ma być jednocześnie modułem i programem, pokazuje następny podrozdział.

!!! note "Dla dociekliwych — ponowne wczytanie modułu i skompilowany kod bajtowy"
    Prosty model „kod modułu wykonuje się przy pierwszym imporcie” ma wyjątki.
    Funkcja `importlib.reload(modul)` wykonuje kod pliku ponownie w tym samym
    obiekcie modułu, co bywa użyteczne w konsoli po zmianie pliku, lecz nie
    odświeża nazw związanych wcześniej przez `from … import …`; w programach
    nie jest częścią zwykłej pracy — po zmianie modułu uruchamiamy program od
    nowa. Interpreter może też zapisywać w podkatalogu `__pycache__`
    skompilowaną postać importowanych modułów (pliki `.pyc`), aby przy kolejnych
    uruchomieniach pominąć etap kompilacji. Nie jest to zapamiętany wynik
    działania programu — kod modułu i tak wykonuje się przy każdym pierwszym
    imporcie w procesie — a obecność tych plików zależy od sposobu
    uruchomienia, opcji interpretera i uprawnień do katalogu. Katalog
    `__pycache__` można bez szkody usunąć.

## Ścieżka wyszukiwania modułów

Plik `narzedzia.py` interpreter odnajduje, przeszukując pozycje listy `sys.path`, którą oglądaliśmy w podrozdziale [Ścieżki i utrzymanie interpreterów](../01-instalacja/sciezki-i-utrzymanie.md#syspath-drugie-znaczenie-sciezki) — o ile nazwa nie należy do modułów wbudowanych w interpreter, które są sprawdzane wcześniej. Jest to zwykła lista łańcuchów, zwykle ścieżek katalogów, przeglądana od początku: wyszukiwanie kończy się na pierwszej pozycji zawierającej plik o szukanej nazwie. Jej pierwszy element zależy od sposobu uruchomienia interpretera:

| Sposób uruchomienia | `sys.path[0]` |
|---|---|
| `python skrypt.py` | katalog, w którym leży skrypt |
| `python -m modul` | katalog bieżący terminala |
| `python -c "..."` i konsola interaktywna | `''`, czyli katalog bieżący terminala |

Sprawdźmy to skryptem wypisującym pierwszy element listy. Funkcja wbudowana `repr()` zwraca zapis obiektu w postaci, w jakiej wyświetla go konsola — dzięki niej pusty łańcuch zobaczymy jako `''`, a nie jako pusty wiersz:

```python title="sciezka.py"
import sys

print(repr(sys.path[0]))
```

```powershell title="Terminal"
python sciezka.py
python -c "import sys; print(repr(sys.path[0]))"
python -m sciezka
```

```{ .text .no-copy }
'C:\\...\\projekt'
''
'C:\\...\\projekt'
```

W pierwszym i trzecim przypadku wypisany katalog jest ten sam, ale z różnych powodów: `python sciezka.py` wstawia katalog skryptu, a `python -m sciezka` — katalog, w którym wydano polecenie. Różnica ujawnia się po uruchomieniu skryptu z innego katalogu, do czego wracamy w dalszej części tej sekcji.

Dalsze elementy `sys.path` pochodzą z instalacji: katalogi z modułami biblioteki standardowej oraz katalog `site-packages` aktywnego środowiska wirtualnego, w którym pip umieszcza instalowane pakiety (podrozdziały [Pip — zarządzanie pakietami](../01-instalacja/pip.md#miejsce-instalowania-pakietow) i [Wirtualne środowisko venv](../01-instalacja/venv.md)). Dodatkowe katalogi można dopisać zmienną środowiskową `PYTHONPATH`, z której w tej książce nie korzystamy. Lista porządkuje zarazem trzy źródła modułów dostępnych w programie:

| Źródło | Skąd pochodzi | Przykłady |
|---|---|---|
| **biblioteka standardowa** (ang. *standard library*) | zestaw modułów dostarczany wraz z interpreterem | `math`, `sys`, `decimal`, `keyword` |
| **pakiety zewnętrzne** | instalowane osobno przez `python -m pip` do środowiska wirtualnego | NumPy, pylint |
| **moduły własne** | pliki projektu | `narzedzia`, `statystyka` |

Bibliotece standardowej poświęcimy osobny podrozdział; tu wystarczy wiedzieć, że jest to zwykły zbiór modułów, które importuje się tak samo jak własne.

Reguła pierwszego elementu tłumaczy najczęstszy błąd początkujących. Program `program.py` z początku podrozdziału działa po uruchomieniu z dowolnego miejsca, bo katalog skryptu trafia na początek `sys.path`, ale ten sam import wykonany z katalogu nadrzędnego przez `python -c` już nie:

```powershell title="Terminal"
cd ..
python projekt\program.py
python -c "import narzedzia"
```

```{ .text .no-copy }
6
----------
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import narzedzia
ModuleNotFoundError: No module named 'narzedzia'
```

`ModuleNotFoundError` oznacza, że w żadnej pozycji `sys.path` nie ma modułu o podanej nazwie — w tym przypadku dlatego, że katalog bieżący to katalog nadrzędny, a nie `projekt`. Ten sam komunikat pojawia się po literówce w nazwie modułu i przy próbie importu pakietu zewnętrznego, którego nie zainstalowano w aktywnym środowisku wirtualnym. Wyjątki i ich obsługę omawia osobny rozdział; na razie komunikat czytamy wprost: interpreter szukał i nie znalazł.

Ponieważ `sys.path` jest zwykłą listą, technicznie można ją zmienić w czasie działania programu i w ten sposób „naprawić” import z katalogu nadrzędnego:

```{ .python .no-copy }
>>> import sys
>>> sys.path.append("projekt")
>>> import narzedzia
>>> narzedzia.__name__
'narzedzia'
```

Jest to doraźna manipulacja środowiskiem wyszukiwania, a nie sposób organizacji projektu: dopisany katalog zależy od miejsca, z którego uruchomiono interpreter, a instrukcję trzeba by powtarzać w każdym pliku, który z modułu korzysta. Właściwe rozwiązanie — uruchamianie programu z katalogu projektu oraz instalacja własnego pakietu w środowisku wirtualnym — jest tematem podrozdziału o strukturze projektu.

!!! note "Opcja -P"
    Automatyczne wstawianie katalogu skryptu lub katalogu bieżącego na
    początek `sys.path` jest wygodne, ale oznacza, że dowolny plik leżący obok
    skryptu może zostać zaimportowany zamiast modułu bibliotecznego. Opcja
    interpretera `-P` (albo zmienna środowiskowa `PYTHONSAFEPATH`) wyłącza ten
    wpis; wtedy własne moduły muszą być dostępne z katalogów instalacji, na
    przykład po zainstalowaniu pakietu w środowisku wirtualnym. Dokumentacja
    opcji: [docs.python.org/3/using/cmdline.html](https://docs.python.org/3/using/cmdline.html).

## Pułapki importu

Pierwsza pułapka wynika wprost z reguły pierwszego elementu. Biblioteka standardowa zawiera moduł `random`, który dostarcza liczb pseudolosowych — na przykład `random.randint(1, 6)` zwraca losową liczbę całkowitą od 1 do 6. Jeżeli własny plik w katalogu projektu nazwiemy tak samo, program zamierzający użyć modułu bibliotecznego otrzyma plik własny, bo katalog skryptu jest przeszukiwany jako pierwszy:

```python title="random.py"
"""Własny moduł, którego nazwa koliduje z modułem biblioteki standardowej."""


def losuj():
    """Zwraca stałą wartość."""
    return 4
```

```python title="gra.py"
import random

print(random.randint(1, 6))
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "gra.py", line 3, in <module>
    print(random.randint(1, 6))
          ^^^^^^^^^^^^^^
AttributeError: module 'random' has no attribute 'randint' (consider renaming 'C:\...\projekt\random.py' since it has the same name as the standard library module named 'random' and prevents importing that standard library module)
```

Od wersji 3.13 CPython rozpoznaje tę sytuację i dopisuje do komunikatu podpowiedź; nie należy jednak polegać na jej brzmieniu, bo diagnostyka interpretera zmienia się z wersji na wersję. Niezależnie od komunikatu problem rozpoznaje się po atrybucie `__file__` — `random.__file__` wskazuje wtedy własny plik zamiast pliku z instalacji Pythona. Przesłonięciu nie podlegają moduły wbudowane w interpreter, jak `sys`, bo są odnajdywane przed przeszukaniem `sys.path`; zdecydowana większość modułów biblioteki standardowej jest jednak odnajdywana przez `sys.path` i własny plik o tej samej nazwie ją przesłania. Wniosek: nazwy własnych modułów nie powinny przesłaniać modułów, które program zamierza importować — dotyczy to biblioteki standardowej, w tym mniej oczywistych nazw, jak `test` czy `email`, które łatwo nadać przez nieuwagę, oraz pakietów zewnętrznych.

Druga pułapka dotyczy dwóch modułów własnych, które importują się wzajemnie — jest to **import cykliczny** (ang. *circular import*). Podczas wykonywania kodu pierwszego modułu instrukcja `import` uruchamia wykonanie drugiego; drugi próbuje zaimportować pierwszy, ale ten jest już w `sys.modules` w postaci częściowo zainicjalizowanej — jego kod nie doszedł jeszcze do definicji funkcji. Sam cykl nie musi kończyć się błędem: dwie instrukcje `import modul`, po których do nazw sięga się przez kropkę dopiero wewnątrz funkcji, zwykle działają. Błąd pojawia się, gdy któryś z modułów podczas własnej inicjalizacji potrzebuje nazwy z modułu częściowo zainicjalizowanego — typowo przy formie `from modul import nazwa`, która kończy się błędem `ImportError` o niemożności zaimportowania nazwy (w Pythonie 3.13 i nowszych komunikat może zawierać mylącą podpowiedź o zmianie nazwy pliku, taką jak w pierwszej pułapce, bo interpreter nie odróżnia obu sytuacji). Właściwym rozwiązaniem jest taki podział kodu, by zależności między modułami biegły w jedną stronę: wspólne funkcje trafiają do osobnego modułu, z którego korzystają oba pozostałe. Przenoszenie instrukcji `import` do wnętrza funkcji bywa spotykane jako obejście, ale nie usuwa przyczyny i nie stosujemy go jako rozwiązania ogólnego.

Model z tego podrozdziału — plik jako moduł, obiekt modułu z przestrzenią nazw, jednokrotne wykonanie kodu i wyszukiwanie w `sys.path` — wystarcza, by w następnym podrozdziale rozstrzygnąć, jak ten sam plik może być raz modułem importowanym przez inne programy, a raz programem uruchamianym z terminala.
