# Pakiety

W ciągu trzech podrozdziałów w katalogu `projekt` powstało kilka modułów: `narzedzia`, `statystyka`, `podatki`, `powitanie`. W większym programie moduły grupuje się w katalogi, a Python ma dla takich katalogów własny mechanizm — **pakiet** (ang. *package*). Słowo to padało już w podrozdziale [Pip — zarządzanie pakietami](../01-instalacja/pip.md) w innym znaczeniu: pakiet instalowany przez pip to **pakiet dystrybucyjny** (ang. *distribution package*) — wersjonowane archiwum z modułami, które pip pobiera i instaluje — i może zawierać jeden lub więcej **pakietów importowanych** (ang. *import package*), czyli katalogów z modułami wczytywanych instrukcją `import`. Do obu pojęć wracamy w podrozdziale o strukturze projektu; tu zajmujemy się wyłącznie drugim.

## Katalog jako pakiet

Pakiet jest rodzajem modułu: ma nazwę, przestrzeń nazw i atrybuty jak każdy moduł, a ponadto może zawierać **podmoduły** (ang. *submodule*) i podpakiety. W tej książce tworzymy **pakiety regularne** (ang. *regular package*): katalog o nazwie pakietu z plikiem `__init__.py` i plikami podmodułów. Zbudujmy pakiet `geometria` z dwoma podmodułami:

```{ .text .no-copy }
projekt/
    geometria/
        __init__.py
        figury.py
        jednostki.py
    program.py
```

```python title="geometria/__init__.py"
"""Udostępnia narzędzia geometryczne: pola figur i przeliczanie jednostek."""
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

```python title="geometria/jednostki.py"
"""Przelicza jednostki długości."""


def cm_na_m(centymetry):
    """Zwraca w metrach długość podaną w centymetrach."""
    return centymetry / 100
```

Podmoduł ma **pełną nazwę** złożoną z nazwy pakietu i nazwy podmodułu rozdzielonych kropką: `geometria.figury`. Tej nazwy kropkowej używamy w instrukcji `import`, a program z katalogu `projekt` sięga po funkcję przez pełną nazwę:

```python title="program.py"
import geometria.figury

print(geometria.figury.pole_kola(1))
print(geometria.figury.__name__)
```

```{ .text .no-copy }
3.141592653589793
geometria.figury
```

Instrukcja `import geometria.figury` wczytuje pakiet `geometria` i jego podmoduł `figury`, ale w bieżącej przestrzeni nazw wiąże tylko nazwę `geometria` — pierwszy człon nazwy kropkowej. Podmoduł jest dostępny jako atrybut pakietu, `geometria.figury`, a nazwa `figury` samodzielnie nie istnieje:

```{ .python .no-copy }
>>> import geometria.figury
>>> geometria.figury.pole_kola(2)
12.566370614359172
>>> figury
Traceback (most recent call last):
  File "<python-input-2>", line 1, in <module>
    figury
NameError: name 'figury' is not defined
>>> geometria.__name__, geometria.figury.__name__
('geometria', 'geometria.figury')
```

Pozostałe formy instrukcji `import` z podrozdziału [Moduły i instrukcja import](moduly-i-import.md#formy-instrukcji-import) działają z pakietami tak samo, jak z modułami — różnią się tym, co zostaje związane:

| Instrukcja | Wiązana nazwa | Obiekt |
|---|---|---|
| `import geometria.figury` | `geometria` | pakiet (podmoduł jako atrybut `geometria.figury`) |
| `from geometria.figury import pole_kola` | `pole_kola` (nazwa `geometria` nie powstaje) | funkcja z podmodułu |
| `from geometria import figury` | `figury` (nazwa `geometria` nie powstaje) | podmoduł |
| `import geometria.figury as f` | `f` (nazwa `geometria` nie powstaje) | podmoduł |

```{ .python .no-copy }
>>> from geometria.figury import pole_kola
>>> pole_kola(1)
3.141592653589793
>>> from geometria import figury
>>> figury.obwod_kola(1)
6.283185307179586
>>> import geometria.figury as f
>>> f is figury
True
```

Import samego pakietu nie wczytuje jego podmodułów. Po `import geometria` atrybut `geometria.figury` jeszcze nie istnieje — pojawia się dopiero wtedy, gdy podmoduł zostanie zaimportowany, którąkolwiek z powyższych form:

```{ .python .no-copy }
>>> import geometria
>>> geometria.figury
Traceback (most recent call last):
  File "<python-input-1>", line 1, in <module>
    geometria.figury
AttributeError: module 'geometria' has no attribute 'figury'
>>> import geometria.figury
>>> geometria.figury.pole_kola(1)
3.141592653589793
```

Nieudany import pakietu lub podmodułu zgłasza — jak przy modułach — `ModuleNotFoundError`, tym razem z pełną nazwą kropkową. Inną sytuacją jest brak nazwy w module, który istnieje: instrukcja `from … import …` zgłasza wtedy `ImportError` z nazwą i ścieżką pliku, w którym nazwy szukała. Nie każdy nieudany import oznacza więc brak modułu:

```{ .python .no-copy }
>>> import geometria.brak
Traceback (most recent call last):
  File "<python-input-0>", line 1, in <module>
    import geometria.brak
ModuleNotFoundError: No module named 'geometria.brak'
>>> from geometria.figury import pole
Traceback (most recent call last):
  File "<python-input-1>", line 1, in <module>
    from geometria.figury import pole
ImportError: cannot import name 'pole' from 'geometria.figury' (C:\...\projekt\geometria\figury.py)
```

## Plik `__init__.py`

Pakiet jest modułem, więc — jak każdy moduł — ma kod, który interpreter wykonuje przy imporcie. W pakiecie regularnym tym kodem jest plik `__init__.py`: jego docstring staje się docstringiem pakietu, a jego instrukcje wykonują się podczas **inicjalizacji** pakietu, czyli przy pierwszym imporcie pakietu albo któregokolwiek z jego podmodułów — na zasadzie jednokrotnego wykonania z sekcji [Wykonywanie modułu podczas importu](moduly-i-import.md#wykonywanie-moduu-podczas-importu):

```{ .python .no-copy }
>>> import geometria
>>> geometria.__doc__
'Udostępnia narzędzia geometryczne: pola figur i przeliczanie jednostek.'
>>> geometria.__file__.endswith("__init__.py")
True
```

Plik może być pusty — pakiet jest wtedy tylko katalogiem grupującym moduły. Częściej zawiera docstring i kilka instrukcji, które udostępniają najważniejsze nazwy bezpośrednio z pakietu. Na razie użytkownik pakietu `geometria` musi wiedzieć, że `pole_kola` jest zdefiniowana w podmodule `figury`, a `cm_na_m` — w `jednostki`. Importując te funkcje w `__init__.py`, wiążemy je w przestrzeni nazw pakietu; taki import nazywa się **re-eksportem** (ang. *re-export*):

```python title="geometria/__init__.py"
"""Udostępnia narzędzia geometryczne: pola figur i przeliczanie jednostek."""

from geometria.figury import pole_kola, obwod_kola
from geometria.jednostki import cm_na_m

__all__ = ["pole_kola", "obwod_kola", "cm_na_m"]
```

```python title="program.py"
from geometria import pole_kola, cm_na_m

print(pole_kola(cm_na_m(100)))
```

```{ .text .no-copy }
3.141592653589793
```

Nazwy `pole_kola`, `obwod_kola` i `cm_na_m` stały się atrybutami pakietu, więc program importuje je wprost z `geometria`, nie znając podziału na podmoduły. Tak buduje się **publiczny interfejs pakietu**: `__init__.py` wskazuje, co pakiet oferuje na zewnątrz, a podmoduły pozostają jego wewnętrzną organizacją. Import podmodułów w `__init__.py` ma skutek uboczny — atrybuty `geometria.figury` i `geometria.jednostki` istnieją od razu po `import geometria`. Plik `__init__.py` powinien jednak pozostać lekki: wykonuje się przy pierwszym imporcie pakietu w każdym programie, który z niego korzysta, także wtedy, gdy program potrzebuje tylko jednego podmodułu, więc nie umieszczamy w nim obliczeń ani części programowej.

### Publiczny interfejs pakietu i lista `__all__`

Lista `__all__`, poznana w sekcji [Import z gwiazdką i lista `__all__`](moduly-i-import.md#import-z-gwiazdka-i-lista-__all__), w pakiecie określa, co wprowadza instrukcja `from geometria import *`. Reguła jest następująca: bez `__all__` instrukcja wiąże wszystkie publiczne nazwy z przestrzeni nazw pakietu — także nazwy podmodułów, które zostały już zaimportowane, czy to w `__init__.py`, czy wcześniejszą instrukcją `import` w programie — ale nigdy nie przegląda katalogu i nie wczytuje pozostałych plików pakietu. Z `__all__` wiąże wyłącznie wymienione nazwy; jeżeli na liście znajdzie się nazwa podmodułu, ten podmoduł zostanie zaimportowany. W naszym `__init__.py` lista wymienia trzy funkcje, więc `import *` nie wprowadza nazw podmodułów:

```{ .python .no-copy }
>>> from geometria import *
>>> pole_kola(1)
3.141592653589793
>>> figury
Traceback (most recent call last):
  File "<python-input-2>", line 1, in <module>
    figury
NameError: name 'figury' is not defined
```

Importu z gwiazdką w kodzie programów zasadniczo nie stosujemy — z powodów podanych przy modułach. Lista `__all__` jest natomiast pożyteczna sama w sobie: dokumentuje, które nazwy pakietu są przeznaczone do użytku na zewnątrz.

## Importy absolutne między modułami pakietu

Podmoduły jednego pakietu zwykle korzystają z siebie nawzajem. Dodajmy do pakietu podmoduł `podsumowanie`, który korzysta z funkcji obu pozostałych podmodułów:

```python title="geometria/podsumowanie.py"
"""Wypisuje podsumowanie koła o promieniu podanym w centymetrach."""

from geometria.figury import pole_kola, obwod_kola
from geometria.jednostki import cm_na_m


def main():
    """Wypisuje pole i obwód koła o promieniu 100 cm."""
    promien = cm_na_m(100)
    print("Pole:", pole_kola(promien))
    print("Obwód:", obwod_kola(promien))
```

```{ .python .no-copy }
>>> from geometria.podsumowanie import main
>>> main()
Pole: 3.141592653589793
Obwód: 6.283185307179586
```

Instrukcje `from geometria.figury import …` to **importy absolutne** (ang. *absolute import*): nazwa modułu zaczyna się od nazwy pakietu najwyższego poziomu, dokładnie tak, jak w programie spoza pakietu. Interpreter odnajduje `geometria` w `sys.path`, a kolejne człony nazwy kropkowej — wewnątrz tego pakietu, niezależnie od tego, w którym pliku instrukcja się znajduje. [PEP 8](https://peps.python.org/pep-0008/#imports) zaleca tę formę jako zwykle czytelniejszą i dającą lepsze komunikaty błędów przy źle skonfigurowanym systemie importu, dopuszczając zarazem jawne importy względne, które poznamy teraz.

## Importy względne

Wewnątrz pakietu dostępna jest też krótsza forma. **Import względny** (ang. *relative import*) zapisuje nazwę modułu względem pakietu, do którego należy importujący moduł: pojedyncza kropka (`.`) oznacza bieżący pakiet, a dwie kropki (`..`) — pakiet nadrzędny, gdy pakiety są zagnieżdżone. Przepiszmy `podsumowanie.py` w tym stylu, używając obu podstawowych postaci, i dodajmy na końcu warunek uruchomienia modułu, który przyda się w następnej sekcji:

```python title="geometria/podsumowanie.py"
"""Wypisuje podsumowanie koła o promieniu podanym w centymetrach."""

from . import jednostki
from .figury import pole_kola, obwod_kola


def main():
    """Wypisuje pole i obwód koła o promieniu 100 cm."""
    promien = jednostki.cm_na_m(100)
    print("Pole:", pole_kola(promien))
    print("Obwód:", obwod_kola(promien))


if __name__ == "__main__":
    main()
```

Zapis `from . import jednostki` wiąże nazwę podmodułu `jednostki` z bieżącego pakietu, a `from .figury import pole_kola, obwod_kola` — wybrane nazwy z podmodułu `figury`. Import względny dopuszcza wyłącznie postać `from … import …`; zapis `import .figury` jest błędem składni. Funkcja `main()` nie zwraca kodu wyjścia, więc wystarcza zwykłe wywołanie — program kończy się kodem `0`; wzorzec `sys.exit(main())` z poprzedniego podrozdziału wraca, gdy program ma sygnalizować błędy.

Istotne jest, do czego odnosi się kropka. Nie jest to katalog pliku, lecz **pakiet, do którego moduł należy w systemie importu**: pakietem modułu `geometria.podsumowanie` jest `geometria`, bo tak brzmi pierwszy człon jego pełnej nazwy, i stąd `.figury` oznacza `geometria.figury`. Import względny ma więc sens tylko dla modułu wykonywanego jako część pakietu — nie jest skrótem ścieżki plikowej. Konsekwencję tej zasady zobaczymy w następnej sekcji. W tym samym stylu zapisujemy w `__init__.py` importy budujące publiczny interfejs pakietu, który od tej pory wygląda następująco:

```python title="geometria/__init__.py"
"""Udostępnia narzędzia geometryczne: pola figur i przeliczanie jednostek."""

from .figury import pole_kola, obwod_kola
from .jednostki import cm_na_m

__all__ = ["pole_kola", "obwod_kola", "cm_na_m"]
```

Obie formy — absolutna i względna — są poprawne wewnątrz pakietu; względna jest krótsza i nie zmienia się przy zmianie nazwy pakietu, absolutna mówi wprost, skąd pochodzi nazwa. W tej książce w kodzie pakietów stosujemy formę względną, a spoza pakietu zawsze absolutną.

## Uruchamianie modułów pakietu: `python -m` i `__main__.py`

Moduł `podsumowanie` ma warunek uruchomienia modułu, więc powinien dać się uruchomić jak program. Bezpośrednie wskazanie pliku kończy się jednak błędem:

```powershell title="Terminal"
python geometria\podsumowanie.py
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "geometria\podsumowanie.py", line 3, in <module>
    from . import jednostki
ImportError: attempted relative import with no known parent package
```

Komunikat opisuje dokładnie, co się stało: interpreter otworzył plik jako moduł główny o nazwie `__main__`, bez pakietu nadrzędnego, więc kropka nie ma do czego się odnieść. Uruchomienie pliku podanego ścieżką nie ustanawia kontekstu pakietu. Wersja z importami absolutnymi również by tu zawiodła, choć z innego powodu: katalogiem skryptu, wstawianym na początek `sys.path`, jest wtedy `geometria`, a nie `projekt`, więc pakietu `geometria` nie da się odnaleźć. Właściwym sposobem jest opcja `-m` z pełną nazwą modułu:

```powershell title="Terminal"
python -m geometria.podsumowanie
```

```{ .text .no-copy }
Pole: 3.141592653589793
Obwód: 6.283185307179586
```

Przy `-m` interpreter odnajduje moduł przez system importu — inicjalizuje pakiet `geometria`, ustala pełną nazwę `geometria.podsumowanie` — i dopiero potem wykonuje go jako moduł główny. Moduł ma wtedy `__name__` równe `"__main__"`, ale system importu pamięta, do którego pakietu należy, więc importy względne działają. Polecenie wydajemy z katalogu `projekt`, bo z tego katalogu pakiet jest osiągalny przez `sys.path`. Jedno zastrzeżenie: przez `-m` nie uruchamiamy modułu importowanego w `__init__.py`, jak `figury` — zostałby wykonany dwukrotnie, raz podczas inicjalizacji pakietu i raz jako moduł główny, o czym CPython ostrzega komunikatem `RuntimeWarning`.

!!! note "Dla dociekliwych — specyfikacja modułu"
    Informację o pakiecie nadrzędnym moduł uruchomiony przez `-m` otrzymuje
    od systemu importu, który zapisuje w atrybucie `__spec__` modułu jego
    **specyfikację** — w tym pełną nazwę w systemie importu. Plik uruchomiony
    bezpośrednio takiej specyfikacji nie ma. Sprawdźmy to plikiem próbnym,
    który po próbie usuwamy z pakietu:

    ```python title="geometria/kontekst.py"
    """Pokazuje kontekst uruchomienia modułu."""

    print("__name__:", __name__)
    print("__spec__ is None:", __spec__ is None)
    if __spec__ is not None:
        print("__spec__.name:", __spec__.name)
    ```

    ```powershell title="Terminal"
    python geometria\kontekst.py
    python -m geometria.kontekst
    ```

    ```{ .text .no-copy }
    __name__: __main__
    __spec__ is None: True
    __name__: __main__
    __spec__ is None: False
    __spec__.name: geometria.kontekst
    ```

    W obu przypadkach `__name__` to `"__main__"`, ale tylko przy `-m` moduł
    ma specyfikację z nazwą `geometria.kontekst` — z niej system importu
    wyprowadza pakiet nadrzędny dla importów względnych. Wewnętrznej budowy
    tej specyfikacji nie musimy znać.

Pakiet jako całość również można uruchomić jak program. Polecenie `python -m geometria` szuka w pakiecie podmodułu o nazwie `__main__` — pliku `geometria/__main__.py` — i wykonuje go jako moduł główny. Bez tego pliku polecenie kończy się komunikatem mechanizmu uruchamiającego CPythona, jak przy `python -m sciezka` w podrozdziale [Skrypt jako program](skrypt-jako-program.md#uruchamianie-przez-python-m):

```powershell title="Terminal"
python -m geometria
```

```{ .text .no-copy }
C:\...\python.exe: No module named geometria.__main__; 'geometria' is a package and cannot be directly executed
```

Dodajmy ten plik w postaci minimalnej:

```python title="geometria/__main__.py"
"""Uruchamia pakiet geometria jako program."""

from .podsumowanie import main

main()
```

```powershell title="Terminal"
python -m geometria
```

```{ .text .no-copy }
Pole: 3.141592653589793
Obwód: 6.283185307179586
```

Plik `__main__.py` jest zwykłym podmodułem o umownej nazwie; jego jedynym zadaniem jest wskazanie, od czego zaczyna się działanie programu. Polecenie `python -m geometria` powoduje wykonanie właśnie tego pliku, więc nie potrzebujemy w nim warunku sprawdzającego `__name__` — warunek uruchomienia modułu pozostaje użyteczny w zwykłych modułach, jak `podsumowanie`, które mają działać zarówno po imporcie, jak i przy bezpośrednim uruchomieniu. Zgodnie z dokumentacją `__main__.py` jest cienkim punktem wejścia: właściwa logika programu pozostaje w importowalnym module i jego funkcji `main()`. Tak działają polecenia `python -m venv` i `python -m pip` z rozdziału 1 — `venv` jest pakietem biblioteki standardowej, a `pip` pakietem zainstalowanym w środowisku wirtualnym; oba mają własny plik `__main__.py`. Jeżeli program pakietu ma przyjmować argumenty wiersza poleceń, `main()` buduje parser `argparse` dokładnie tak, jak w podrozdziale [Argumenty wiersza poleceń](argumenty-wiersza-polecen.md#modu-argparse).

Model jest więc następujący: plik podany interpreterowi ścieżką jest wykonywany bez kontekstu pakietu, a moduł o nazwie podanej po `-m` jest odnajdywany przez system importu i wykonywany w kontekście swojego pakietu. Dotyczy to także katalogu pakietu podanego wprost — `python geometria` wykonuje wprawdzie `geometria\__main__.py`, ale jak skrypt, bez kontekstu pakietu, więc jego import względny kończy się tym samym błędem co w `podsumowanie.py`. Dlatego moduły należące do pakietów uruchamiamy zawsze przez `python -m pakiet.modul` albo `python -m pakiet`, z katalogu, z którego pakiet jest osiągalny. Pakiet w postaci końcowej — bez pliku próbnego z noty — wygląda następująco:

```{ .text .no-copy }
projekt/
    geometria/
        __init__.py
        __main__.py
        figury.py
        jednostki.py
        podsumowanie.py
    program.py
```

## Pakiety przestrzeni nazw

W tej książce tworzymy pakiety regularne z plikiem `__init__.py`. Python obsługuje również **pakiety przestrzeni nazw** (ang. *namespace package*, [PEP 420](https://peps.python.org/pep-0420/)), które tego pliku nie wymagają: katalog bez `__init__.py` leżący w jednej z pozycji `sys.path` także daje się zaimportować jako pakiet. Ich zastosowania wykraczają poza projekty z tej książki. Obecność `__init__.py` jest więc naszą konwencją, a nie wymogiem języka — wybieramy ją, bo czyni strukturę pakietu jawną i daje miejsce na jego interfejs.

Do pakietu `geometria` wracamy w następnym podrozdziale, gdzie staje się on częścią kompletnego projektu z testami i instalacją w środowisku wirtualnym.
