# Rozdział 7. Moduły, pakiety i biblioteka standardowa — plan implementacyjny

Skondensowany projekt rozdziału zaakceptowany przez autora 5 września 2026 (z rozstrzygnięciami wymienionymi niżej). Mapa całej książki: `PLAN_ROZWOJU.md`. Katalog `docs/07-moduly/`, dziewięć plików; kolejność tworzenia: `moduly-i-import.md`, `skrypt-jako-program.md`, `argumenty-wiersza-polecen.md`, `pakiety.md`, `struktura-projektu.md`, `biblioteka-standardowa.md`, `functools.md`, `itertools.md`, `index.md`. Stan odniesienia: Python 3.14.7 (`.venv/Scripts/python.exe`), Windows, Python Install Manager. Projekt przeszedł niezależną recenzję (kolejność pojęć, sonda wykonalności na 3.14.7 z instalacją edytowalną w tymczasowym venv, przegląd kontradyktoryjny, zgodność z regułami repozytorium i laboratorium 3): 48 ustaleń, zero blokerów; korekty są wbudowane w ten plan.

## Decyzje autora (5 IX 2026)

1. **Struktura:** index + 8 podrozdziałów w kolejności: moduł i import → moduł jako program → argumenty wiersza poleceń → pakiety → struktura projektu i testy → biblioteka standardowa i collections → functools → itertools. `functools` nie jest łączony ze stroną o bibliotece standardowej.
2. **Testy — wariant A+:** najpierw test jako zwykła funkcja `test_*()` z `assert` i organizacja `tests/test_*.py`, wykonanie bez frameworka (żeby `assert` i idea testu były zrozumiałe niezależnie od narzędzia); potem jeden ograniczony H2 o pytest (ok. 50–70 linii): czym jest i że nie należy do biblioteki standardowej, instalacja w aktywnym venv, `python -m pytest`, automatyczne odnajdywanie `test_*.py` i `test_*()`, przykład zaliczony, przykład niezaliczony, kod wyjścia procesu. Bez `pytest.raises` (rozdz. 8), fixtures, parametryzacji, mockowania, `monkeypatch`, coverage, konfiguracji, wtyczek i CI (rozdz. 16). pytest nie trafia do `dependencies` w `pyproject.toml`.
3. **`namedtuple`:** krótka sekcja (ok. 20–30 linii) po `deque`, `Counter`, `defaultdict`. Terminologia: `collections.namedtuple()` jest funkcją fabryczną tworzącą nowy typ będący podklasą krotki; nie „bezklasowy rekord”. Pokazujemy zastosowanie, nazwane pola, dostęp przez nazwę i indeks, niemodyfikowalność odziedziczoną po krotce; bez dziedziczenia, MRO i implementacji klas. Na końcu zapowiedź innych mechanizmów reprezentowania rekordów danych, w tym klas danych. `OrderedDict` najwyżej jedno zdanie historyczne; `ChainMap` pominięty.
4. **`float`, `Decimal` i pierwszy test numeryczny:** w części o `assert` krótki przykład z laboratorium 3: `0.1 + 0.2 + 0.3 == 0.6`, właściwe sposoby zależnie od intencji — `math.isclose(...)` oraz `Decimal("0.1")` z modułu `decimal` (Decimal tworzony z napisów, nie z literałów `float`); `round()` krótko, jeśli pomaga odróżnić zaokrąglanie wyniku od testowania przybliżonej równości. Bez NumPy i bez analizy numerycznej.
5. **`itertools` bez dopisku w tytule:** H1 i etykieta nav „Moduł itertools”; opcjonalny charakter zaznaczony w pierwszym akapicie strony i w opisie podrozdziału w `index.md`.
6. **Nazwa strony o bibliotece standardowej:** „Biblioteka standardowa i moduł collections” jako H1 i etykieta nav.
7. **Długość stron:** bez twardej normy. Szacunki długości są orientacyjne i nie stanowią limitu; o długości decyduje kompletność merytoryczna, przykłady, wyniki wykonania i czytelna struktura. Orientacyjny rozmiar rozdziału ok. 2400–2900 linii; „do około 6 H2” jest wskazówką strukturalną, nie ograniczeniem.
8. **Wcześniejsze korekty utrzymane:** nota o `__spec__` w `pakiety.md` (przy różnicy `python geometria/figury.py` a `python -m geometria.figury`), nie w „Skrypt jako program”; `__all__` na stronie 1 tylko krótko (czym jest, związek z `from modul import *`, dlaczego `import *` zasadniczo nie jest preferowany), szerszy kontekst publicznego interfejsu pakietu w `pakiety.md`; `sys.path` pokazany z wyjaśnieniem mechanizmu wyszukiwania, `sys.path.append(...)` wyłącznie jako demonstracja, że lista może zostać zmieniona w czasie działania, z jasnym stwierdzeniem, że dla projektu rozwiązaniem jest poprawna struktura i instalacja pakietu; `argparse` z deterministycznymi wynikami na 3.14.7 (`prog=` ustawiony jawnie; kolorowanie i inne cechy zależne od terminala tylko w nocie o 3.14; `suggest_on_error` opisany zgodnie z rzeczywistym zakresem — `choices` i podkomendy); kod wyjścia programu jako pojęcie, `$LASTEXITCODE` najwyżej jednym zdaniem jako mechanizm konkretnej powłoki; pakiety przestrzeni nazw: „W tej książce tworzymy regularne pakiety zawierające `__init__.py`. Python obsługuje również pakiety przestrzeni nazw bez tego pliku” — bez sformułowania „pakiet zawsze musi mieć `__init__.py`”; `tests/__init__.py` użyty dla spójności i jawności struktury, nie jako techniczny warunek działania `python -m tests.test_figury`; `pyproject.toml` minimalny z Hatchling — `[build-system]` jako konfiguracja narzędzi potrzebnych do zbudowania i instalacji projektu, Hatchling jako konkretny backend użyty w przykładzie, bez porównywania backendów; `sys.getrecursionlimit()` wykonywalnie, `sys.setrecursionlimit()` jako istniejące API bez przykładu zachęcającego do zwiększania limitu; bez zapisywania liczby modułów biblioteki standardowej (`sys.stdlib_module_names` bez przywiązania do liczby); `functools.wraps` opisany przez stabilny efekt (sformułowanie w zasadach); `itertools` w rdzeniu: `count`, `cycle`/`repeat`, `islice`, `chain`, `pairwise`, `batched` (ze `strict=True`), `accumulate`, `groupby`, jeden wspólny fragment `product`/`permutations`/`combinations`, `starmap` krótko jako naturalne następstwo rozpakowywania; `zip_longest`, `takewhile`, `dropwhile`, `filterfalse`, `compress`, `tee` tylko wymienione.
9. **Bez Gita:** Git, GitHub, `.gitignore`, GitHub Actions, pull request i CI wykluczone, także z przykładowych drzew katalogów.

## Zasady obowiązujące w całym rozdziale

- Żaden przykład nie wymaga mechanizmu wprowadzanego później: bez `try/except` i `raise` (rozdz. 8), plików i `open()` (rozdz. 9), klas (rozdz. 10), `dataclass`/`NamedTuple` (rozdz. 12). Wyjątki (`ModuleNotFoundError`, `ImportError`, `AttributeError`, `IndexError`, `AssertionError`) pojawiają się wyłącznie w śladach wywołań i komunikatach, nigdy jako obsługiwane obiekty; `SystemExit` nie pada z nazwy.
- Kolejność wewnątrz rozdziału jest bezwzględna: podrozdział korzysta wyłącznie z pojęć podrozdziałów wcześniejszych i rozdziałów 1–6. Moduły biblioteki standardowej użyte w kodzie: `sys`, `math`, `decimal` (znany z rozdz. 3), `random` (jedno zdanie wprowadzające przy pułapce kolizji), `argparse`, `functools`, `collections`, `itertools`, `importlib` (tylko nota o `reload()`); pytest wyłącznie w zakresie decyzji 2. Żaden inny moduł nie pojawia się w kodzie (`json`, `pathlib`, `re`, `datetime`, `os`, `time`, `statistics` wyłącznie prozą w mapie biblioteki).
- Pojęcia, które trzeba wprowadzić jawnie, bo nie istnieją w rozdziałach 1–6: `__file__`; `sys.modules`; kod wyjścia programu wraz z regułą „nieprzechwycony wyjątek → ślad i kod 1”; `ModuleNotFoundError` (forma podstawowa na stronie 1, kropkowa na stronie 4); idiom zliczania słownikiem (budowany na stronie 6 przed `Counter`); `math.prod()` (w miejscu użycia); format TOML (dwa zdania przed `pyproject.toml`); rozróżnienie „pakiet importowany (ang. *import package*)” a „pakiet dystrybucyjny (ang. *distribution package*)”, znany z rozdz. 1 jako „pakiet instalowany przez pip” (początek strony 4, powtórzone przy kluczu `name` na stronie 5). Bez notacji O(1) — koszt operacji opisujemy słownie, jak w `lista.md`.
- Atrybuty modułu nauczane jako wiedza podstawowa: `__name__`, `__doc__`, `__file__`; `__spec__` tylko w nocie na stronie 4. Wydruk `dir(modul)` pokazujemy w całości z jednym zdaniem, że pozostałe nazwy to atrybuty techniczne (część udokumentowana jako przestarzała); interpreter 3.14.7 nie ostrzega przy ich odczycie, więc o ostrzeżeniach nie piszemy.
- Model użytkowy przed mechanizmem: formy importu i przestrzeń nazw modułu przed `sys.modules` i `sys.path`; `__name__` przed strażnikiem; `sys.argv` przed `argparse`; test bez frameworka przed pytest; układ płaski przed układem `src/`; `pyproject.toml` wyłącznie razem z układem `src/`. Findery, loadery, `importlib` jako API, `runpy`, `PYTHONPATH` poza jednym zdaniem — poza rozdziałem.
- `sys.path.append()` pokazane raz, w bloku `.no-copy`, jako demonstracja zmiany listy w czasie działania, z oceną: zależy od ścieżki na jednym komputerze i musi być powtarzane w każdym pliku; dla projektu rozwiązaniem jest poprawna struktura i instalacja pakietu (strona 5). pip wyłącznie jako `python -m pip …`; goły `pip` (także cytowany z laboratorium) w blokach `.no-copy`.
- Wszystkie nazwy plików i modułów w przykładach bez kolizji z biblioteką standardową (`narzedzia.py`, `powitanie.py`, pakiet `geometria`); kolizja (`random.py`) pokazana wyłącznie jako pułapka z komunikatem 3.14. Moduły wbudowane w interpreter (`math`, `sys`, `itertools`; `sys.builtin_module_names`) nie podlegają przesłonięciu — stąd wybór `random`.
- Każdy przykład o deterministycznym wyniku uruchomiony na interpreterze projektu przed wpisaniem wyniku; wydruki `dir()`, `sys.path`, komunikaty pip, teksty pomocy `argparse`, wyniki pytest i ślady wywołań w brzmieniu 3.14.7 (prefiksy ścieżek zamaskowane jednolicie; ślady spod `python -m` zawierają ramki `<frozen runpy>` — pokazujemy je w całości z jednym zdaniem wyjaśnienia albo jawnie oznaczamy skrót). Liczby zależne od implementacji (limit rekurencji 1000, statystyki `cache_info()`, zestaw dunder w `dir()`) oznaczone jako szczegół CPythona. Bez przekierowań wyjścia do pliku przy polskich znakach (na Windows poza konsolą obowiązuje cp1252). Instalacja edytowalna i pytest weryfikowane w tymczasowym venv poza repozytorium; w świeżym środowisku wymagają dostępu do sieci (backend budowania, pakiet pytest).
- Terminologia: „moduł”, „pakiet regularny”, „pakiet przestrzeni nazw (ang. *namespace package*)”, „pakiet importowany” / „pakiet dystrybucyjny”, „import absolutny”, „import względny”, „moduł główny (`__main__`)”, „strażnik uruchomienia” dla warunku `if __name__ == "__main__"`, „kod wyjścia (ang. *exit code*)”, „funkcja testowa”, „instalacja edytowalna (ang. *editable install*)”, „układ `src`” (ang. *src layout*), „backend budowania (ang. *build backend*)”, „pamięć podręczna modułów” dla `sys.modules`, „ścieżka wyszukiwania modułów” dla `sys.path`; „podrozdział” dla części książki, „strona” tylko dla stron WWW i dokumentacji; „haszowalny”; „generator” wyłącznie dla obiektu generatora.
- Nagłówki w formie rzeczownikowej; nazwy w nagłówkach zapisane w kodzie (np. „Atrybut `__name__` i nazwa `"__main__"`”, „Warunek `if __name__ == "__main__"`”), proste cudzysłowy wyłącznie wewnątrz kodu.
- Docstringi w stylu `"""Zwraca ..."""`, `"""Oblicza ..."""`, `"""Sprawdza ..."""`; docstring modułu jednym zdaniem opisującym przeznaczenie pliku.
- `functools.wraps` opisujemy przez stabilny efekt: „`@functools.wraps` zachowuje istotne metadane funkcji opakowywanej, między innymi jej nazwę, docstring i adnotacje, oraz udostępnia odwołanie `__wrapped__`”; wykonywalnie pokazujemy `__name__`, `__doc__`, `help()` i `__wrapped__`. Bez `WRAPPER_ASSIGNMENTS`, bez `__module__` i bez narracji o różnicy `__annotations__`/`__annotate__` między tekstem dokumentacji a CPythonem 3.14.7 (fakt do ponownej kontroli przy pisaniu strony 7: dokumentacja 3.14 wymienia `__annotations__`, `functools.WRAPPER_ASSIGNMENTS` w 3.14.7 zawiera `__annotate__`; efekt dla czytelnika jest ten sam).
- Konwencje redakcyjne z `CLAUDE.md`: bloki `python title="plik.py"` dla plików, `toml title="pyproject.toml"` i `text title="…"` dla plików konfiguracyjnych, `powershell title="Terminal"` dla poleceń, `{ .python .no-copy }` dla sesji REPL, `{ .text .no-copy }` dla wyników, drzew katalogów i tekstów pomocy; admonitions z polskimi tytułami; cudzysłowy „…”; klawisze `++ctrl+c++`; terminy angielskie kursywą z „ang.” przy pierwszym użyciu.
- `index.md` w układzie istniejących rozdziałów: wstęp prozą, `---`, `## W tym rozdziale`. Bez „Powiązane laboratorium” i bez „Ściągi”.
- Odsyłacze do rozdziałów 1–6 wewnątrz nowych stron dozwolone od razu; zmiany w plikach rozdziałów 1–6 (zamiana komentarzy `TODO` i zapowiedzi na odsyłacze) wykonujemy zbiorczo dopiero po ukończeniu wszystkich stron rozdziału 7, według tabeli na końcu tego pliku. Strony rozdziału 4 z markerami aktywności nie są dotykane.

## Strony

### 1. `moduly-i-import.md` — Moduły i instrukcja import

**Cel.** Czytelnik traktuje plik `.py` jako moduł i jako obiekt z atrybutami, świadomie wybiera formę instrukcji `import`, wie, że kod modułu wykonuje się raz przy pierwszym imporcie i że interpreter przechowuje moduł w pamięci podręcznej, oraz wie, skąd interpreter bierze moduły i jakie są typowe pułapki.

**Kolejność H2/H3.**
1. Moduł jako plik i jako obiekt (H3: Docstring modułu)
2. Formy instrukcji import (H3: Import z gwiazdką i lista `__all__` — krótko; H3: Kolejność importów według PEP 8)
3. Przestrzeń nazw modułu
4. Wykonywanie modułu podczas importu (nota „Dla dociekliwych — `importlib.reload()` i katalog `__pycache__`”)
5. Ścieżka wyszukiwania modułów
6. Pułapki importu

**Pojęcia wprowadzane.** Moduł; obiekt modułu (`type()` → `module`); atrybuty `__name__`, `__doc__`, `__file__`; `help(modul)`; `import m`, `import m as alias`, `from m import nazwa`, `from m import nazwa as alias`; wiązanie nazw w przestrzeni importującego i przesłanianie; `from m import *` i `__all__` (czym jest, związek z `import *`, dlaczego `import *` nie jest preferowany; `SyntaxError` wewnątrz funkcji); grupowanie importów według PEP 8; przestrzeń nazw modułu jako przestrzeń globalna z LEGB, `dir(modul)` i `dir()`; jednokrotne wykonanie i pamięć podręczna `sys.modules`; ścieżka wyszukiwania `sys.path` (katalog skryptu, `''` dla `-c` i konsoli, katalog bieżący dla `-m`; `site-packages` środowiska wirtualnego; `-P` w nocie; `PYTHONPATH` jednym zdaniem); `ModuleNotFoundError` w formie podstawowej; `sys.path.append()` jako demonstracja; `random` jednym zdaniem (liczby pseudolosowe, `randint(a, b)`) przed pułapką kolizji; formalna definicja biblioteki standardowej.

**Zależności.** `import math`, `python -c` (`02-konsola/konsola-w-praktyce.md`, `pierwszy-skrypt.md`); `from decimal import Decimal`, `from fractions import Fraction` (`03-nazwy-typy/typy-proste.md:164–170` — forma użyta bez objaśnienia, teraz objaśniona), `import ctypes`, `import copy` (rozdz. 3 i 5); `sys.path`, `site-packages`, venv (`01-instalacja/sciezki-i-utrzymanie.md`, `venv.md`); `keyword`, `sys` (`03-nazwy-typy/nazwy-i-slowa-kluczowe.md`, `obiekty-i-pamiec.md`); LEGB, `__name__`, `__doc__`, `help()`, docstring (`06-funkcje/zasieg-nazw-i-domkniecia.md`, `definiowanie-funkcji.md`); słownik (`05-typy-zlozone/slownik.md`).

**Główne przykłady.** `narzedzia.py` (docstring „Narzędzia do pracy z tekstem.”, stała `SEPARATOR`, funkcja `policz_slowa()`) i `program.py` z czterema formami importu; REPL: `type(narzedzia)`, `narzedzia.__name__`, `narzedzia.__doc__`, `narzedzia.__file__`, `help(narzedzia)`, `dir(narzedzia)` w całości; `from narzedzia import policz_slowa` a późniejsze przypisanie w module (nazwa importowana nie śledzi zmian); moduł z `print()` importowany dwukrotnie w jednej sesji, `sys.modules["narzedzia"]`, `"narzedzia" in sys.modules`; `import *` w funkcji; wydruk `sys.path` w venv, `python -c` z `''`; `program.py` uruchomiony spoza katalogu z `narzedzia.py` jako motywacja reguły `sys.path[0]`; `sys.path.append(...)` w konsoli (blok `.no-copy`); własny `random.py` obok skryptu; import cykliczny wyłącznie prozą (ewentualny cytat z wariantu pakietowego); nota o `__pycache__`.

**Wymagane zachowania do weryfikacji na 3.14.7.** `type(narzedzia)` → `<class 'module'>`; pełny wydruk `dir(narzedzia)` (`SEPARATOR`, `__builtins__`, `__cached__`, `__doc__`, `__file__`, `__loader__`, `__name__`, `__package__`, `__spec__`, `policz_slowa`); `help(narzedzia)` z sekcją FILE (ścieżka na Windows może być małymi literami); drugi `import` bez ponownego wydruku; `SyntaxError: import * only allowed at module level`; `sys.path[0]` = katalog skryptu / `''` / katalog bieżący pod `-m`; `ModuleNotFoundError: No module named 'narzedzia'` przy uruchomieniu z innego katalogu; `AttributeError: module 'random' has no attribute 'randint' (consider renaming '…\random.py' since it has the same name as the standard library module named 'random' …)`; `'math' in sys.builtin_module_names` → `True`; `.pyc` powstaje w `__pycache__` po imporcie i po `python -m narzedzia`, nie po `python narzedzia.py`; brak ostrzeżeń przy odczycie `__package__`/`__loader__`/`__cached__` pod `-W error`.

**Źródła repozytorium.** `PythonNotatki.txt` 2841–2953, 2982–3007 (s. 76–79; `test.py` → `narzedzia.py`; „moduł `re` w C” → moduł rozszerzenia `_sqlite3`; `imp`/`deepreload` pominięte); `Wyklad_05.txt` sl. 3–6, 8, 34–36, 43 (sl. 6: `sys.path.append()` — pokazane z oceną); `lab3.txt` sl. 1.

**Źródła zewnętrzne.** Tutorial *Modules* (6.1–6.2, *The Module Search Path*, *“Compiled” Python files*); Language Reference *The import system* (module cache, `sys.modules`), *The import statement*; `sys.path`, `sys.modules`, `sys.flags.safe_path`, `sys.builtin_module_names`; *Command line and environment* (`-P`, `PYTHONSAFEPATH`, `PYTHONPATH`); datamodel *Modules* (`__name__`, `__doc__`, `__file__`); PEP 8 *Imports*; `importlib.reload()`; glosariusz (*module*, *importing*, *standard library*).

**TODO/zapowiedzi do domknięcia.** `06-funkcje/definiowanie-funkcji.md:177` (docstring modułu) → sekcja 1; `03-nazwy-typy/nazwy-i-slowa-kluczowe.md:14` (`import`, `from`, `as`) → uzgodniony tekst z tabeli końcowej.

**Odłożone.** Findery i loadery; `importlib` jako API (poza notą o `reload()`); `PYTHONPATH` w szczegółach; `vars(modul)` i `__dict__`; `import builtins`; `__package__`/`__loader__`/`__cached__`; `__spec__` (nota na stronie 4); sortowanie importów narzędziem (rozdz. 16); import wewnątrz funkcji (jedno zdanie: dopuszczalny, ale nie w tej książce); szerszy kontekst `__all__` jako interfejsu pakietu (strona 4).

**Ryzyka kolejności pojęć.** `__file__` i `sys.modules` nowe — wprowadzić jawnie; słowo „pakiet” pada tu tylko w znaczeniu z rozdz. 1 („pakiety zewnętrzne w `site-packages`”), rozróżnienie następuje na stronie 4; komunikaty błędów wyłącznie jako ślady; nie sugerować, że `sys.path.append()` naprawia strukturę projektu.

**Orientacyjny rozmiar.** ok. 350–400 linii.

### 2. `skrypt-jako-program.md` — Skrypt jako program

**Cel.** Czytelnik rozumie, że ten sam plik może być zaimportowany albo uruchomiony, rozróżnia te przypadki przez wartość `__name__`, stosuje strażnik uruchomienia i funkcję `main()` ze zrozumieniem, a nie jako zaklęcie, oraz uruchamia moduły przez `python -m`.

**Kolejność H2/H3.**
1. Ten sam plik jako moduł i jako program
2. Atrybut `__name__` i nazwa `"__main__"`
3. Warunek `if __name__ == "__main__"`
4. Konwencja `main()`
5. Uruchamianie przez `python -m`

**Pojęcia wprowadzane.** Moduł główny; wartość `__name__` przy uruchomieniu (`"__main__"`) i przy imporcie (nazwa pliku); strażnik uruchomienia; `main()` jako punkt wejścia (funkcje definiowane na górze, wywołanie na dole; testowalność i importowalność — powiązanie z funkcjami czystymi z rozdz. 6); `python -m nazwa` (wyszukiwanie w `sys.path` od katalogu bieżącego; moduły biblioteki standardowej uruchamiane tak samo, np. `python -m calendar 2026 9`); różnica `python plik.py` a `python -m plik` (`sys.path[0]`, `.pyc` dla modułu uruchamianego przez `-m`).

**Zależności.** Strona 1; opcje `-m`, `-c`, `-i` (`02-konsola/pierwszy-skrypt.md#python-bez-wchodzenia-do-konsoli-opcje-c-m-oraz-i`); funkcje i `return` (rozdz. 6); przedrostek `__main__.` w `TypeError` i „in module `__main__`” w `help()` (`06-funkcje/argumenty-i-parametry.md`, `definiowanie-funkcji.md`).

**Główne przykłady.** `narzedzia.py` z wywołaniem próbnym na końcu — import w `program.py` wypisuje wynik próby (problem); `print(__name__)` w obu trybach; wersja ze strażnikiem; skrypt liniowy przepisany do funkcji i `main()`; `python -m narzedzia`; `python -m narzedzia.py` pokazane dopiero po wprowadzeniu strażnika (interpreter najpierw importuje `narzedzia`, potem zgłasza błąd z podpowiedzią) — jedno zdanie: nazwa z kropką jest czytana jako nazwa kropkowa; `python -m calendar`; wydruk `sys.path[0]` w obu trybach. Zakończenie: zdanie-most „dane z wiersza poleceń program odczytuje z `sys.argv` — następny podrozdział”.

**Wymagane zachowania do weryfikacji na 3.14.7.** `__name__` → `'__main__'` dla `python plik.py`, `python -m plik`, `python -c`, konsoli; nazwa pliku przy imporcie; komunikat `python -m narzedzia.py`: „Error while finding module specification for 'narzedzia.py' (ModuleNotFoundError: __path__ attribute not found on 'narzedzia' while trying to find 'narzedzia.py'). Try using 'narzedzia' instead of 'narzedzia.py' as the module name.” po wydruku modułu (jeśli moduł ma efekty uboczne); `python -m calendar 2026 9` wypisuje kalendarz września; `sys.path[0]` = katalog skryptu wobec katalogu bieżącego pod `-m`.

**Źródła repozytorium.** `PythonNotatki.txt` 2953–2980 (s. 79; samoimport `test.py` zastąpiony dwoma plikami); `Wyklad_05.txt` sl. 7; `Wyklad_01.txt` sl. 32.

**Źródła zewnętrzne.** `library/__main__.html` (*Idiomatic Usage*, `main()`); *Command line and environment* (`-m`, `sys.path[0]`); tutorial *Executing modules as scripts*; `runpy` tylko jako nazwa mechanizmu.

**TODO/zapowiedzi do domknięcia.** `06-funkcje/argumenty-i-parametry.md:317` (przedrostek `__main__.`) → sekcja 2.

**Odłożone.** `sys.exit(main())` → strona 3; `__main__.py`, `python -m pakiet` i nota o `__spec__` → strona 4; `runpy`, `python katalog/`, `python archiwum.zip`.

**Ryzyka kolejności pojęć.** Przykład musi obywać się bez pakietów; nie obciążać strony `__spec__` ani `sys.argv`; komunikat `python -m narzedzia.py` bez strażnika zawiera także wyjście modułu — pokazać po strażniku.

**Orientacyjny rozmiar.** ok. 250–300 linii.

### 3. `argumenty-wiersza-polecen.md` — Argumenty wiersza poleceń

**Cel.** Czytelnik przekazuje programowi dane z wiersza poleceń: rozumie `sys.argv` jako listę łańcuchów, widzi granice ręcznej obsługi, buduje minimalny parser `argparse` z automatyczną pomocą i komunikatami błędów oraz rozumie kod wyjścia programu.

**Kolejność H2/H3.**
1. Lista `sys.argv`
2. Ręczna obsługa argumentów i jej granice
3. Moduł argparse (H3: Parser, argument pozycyjny i opcja; H3: Automatyczna pomoc i komunikaty błędów; nota „Nowości Pythona 3.14”)
4. Kody wyjścia i funkcja `sys.exit()`

**Pojęcia wprowadzane.** Argument wiersza poleceń; `sys.argv[0]` i `sys.argv[1:]` (listing dla `python plik.py`; pod `-m` `argv[0]` jest ścieżką bezwzględną — jedno zdanie); konwersja `int()`; brakujący argument jako `IndexError` w śladzie; `--help` wypisujące `__doc__` modułu; `ArgumentParser(prog=…, description=…)`, `add_argument()` dla argumentu pozycyjnego i opcji `-n/--liczba` z `type=int` i `default`, `parse_args()`, obiekt `Namespace` i dostęp przez atrybuty; wygenerowana pomoc (`usage:`, `positional arguments:`, `options:`); błąd → `usage` i komunikat na stderr, kod wyjścia 2; skróty nazw opcji przyjmowane domyślnie (`allow_abbrev`); nota 3.14: `suggest_on_error` (podpowiedzi wyłącznie dla `choices` i podkomend), `color` (zależne od terminala, poza blokami porównywanymi znak w znak), `prog` domyślnie odzwierciedla sposób uruchomienia (dlatego ustawiamy `prog=`); kod wyjścia programu: 0 przy normalnym zakończeniu, 1 przy nieprzechwyconym wyjątku (ślad + kod 1 — reguła wprowadzona tu, wykorzystywana na stronie 5), 2 z `argparse`, `sys.exit(kod)`, wzorzec `sys.exit(main())`; sposób odczytu kodu w powłoce jednym zdaniem jako mechanizm konkretnej powłoki.

**Zależności.** Strony 1–2; `input()` (rozdz. 2); `int()` (rozdz. 3); lista i wycinki (rozdz. 5); argumenty nazwane jako analogia do opcji (rozdz. 6).

**Główne przykłady.** `powitanie.py` w trzech wersjach: `sys.argv` (`python powitanie.py Ola 3`), wersja z `--help` przez `__doc__` (PDF), wersja `argparse` z `prog="powitanie"`; bloki terminalowe: `--help`, brak argumentu, `-n abc`, `--xyz`; `main()` zwracające 0/1 i `sys.exit(main())`; trzy zakończenia programu (normalne, ślad, błąd `argparse`) z kodami 0, 1, 2.

**Wymagane zachowania do weryfikacji na 3.14.7.** Tekst `--help` z nagłówkiem `options:` i linią `-n, --liczba LICZBA`; `powitanie: error: the following arguments are required: imie` (kod 2); `powitanie: error: argument -n/--liczba: invalid int value: 'abc'` (kod 2); `powitanie: error: unrecognized arguments: --xyz` (kod 2); `--licz 2` przyjmowane jako skrót; literówka w nazwie opcji nie dostaje podpowiedzi także z `suggest_on_error=True` (podpowiedź tylko dla `choices`: „invalid choice: … maybe you meant …?”); bez `prog=` pod `-m` linia `usage:` zaczyna się od `python.exe -m …`; sygnatura `ArgumentParser` w 3.14.7 zawiera `suggest_on_error=False` i `color=True` jako parametry tylko nazwane; `IndexError: list index out of range` przy brakującym argumencie w wersji ręcznej; kod 1 po nieprzechwyconym wyjątku.

**Źródła repozytorium.** `PythonNotatki.txt` 2004–2018 (s. 59; `sys.argv`, `__doc__` jako pomoc); `lab1.txt` (`cli.py` z `argparse` — wyłącznie kontekst kursu).

**Źródła zewnętrzne.** `sys.argv`, `sys.exit`; *Argparse Tutorial* i referencja `argparse` (3.14: `suggest_on_error`, `color`, `prog`, `allow_abbrev`); `library/__main__.html` (`sys.exit(main())`); What's New in Python 3.14 (argparse).

**TODO/zapowiedzi do domknięcia.** Brak bezpośrednich; domyka lukę planu „`sys.argv`/`argparse`”.

**Odłożone.** `choices` poza notą; `nargs`; `action="store_true"` (najwyżej jedno zdanie); podkomendy; `exit_on_error=False` (wymaga `try/except`); `SystemExit` i `finally` (rozdz. 8); `deprecated=` (3.13); `getopt`; `click`/`typer`.

**Ryzyka kolejności pojęć.** Bez `try/except`; `sys.exit()` opisany jako „kończy program z kodem wyjścia”; nie obiecywać podpowiedzi literówek w nazwach opcji; wyniki zależne od terminala (kolor) poza blokami porównywanymi.

**Orientacyjny rozmiar.** ok. 250–300 linii.

### 4. `pakiety.md` — Pakiety

**Cel.** Czytelnik organizuje moduły w katalog-pakiet z `__init__.py`, importuje między modułami pakietu absolutnie i względnie, rozumie, kiedy import względny zawodzi i dlaczego, oraz uruchamia moduł pakietu i cały pakiet przez `python -m`.

**Kolejność H2/H3.**
1. Katalog jako pakiet (otwarcie: „pakiet importowany” a „pakiet dystrybucyjny” z rozdz. 1)
2. Plik `__init__.py` (H3: Publiczny interfejs pakietu i lista `__all__`)
3. Importy absolutne między modułami pakietu
4. Importy względne
5. Uruchamianie modułów pakietu: `python -m` i `__main__.py` (nota „Dla dociekliwych — `__spec__`”)
6. Pakiety przestrzeni nazw (krótka sekcja)

**Pojęcia wprowadzane.** Pakiet regularny; `__init__.py` (pusty albo z inicjalizacją; wykonywany przy pierwszym imporcie pakietu lub podmodułu); nazwa kropkowa i `__name__` podmodułu; `import pakiet.modul` (wiąże `pakiet`), `import pakiet.modul as m` (wiąże tylko `m`), `from pakiet.modul import nazwa`, `from pakiet import modul`; podmoduł jako atrybut pakietu dopiero po imporcie; import podmodułów w `__init__.py` jako publiczny interfejs, `__all__` pakietu i `from pakiet import *` (bez `__all__` — nazwy z `__init__`, nie podmoduły); import absolutny między modułami pakietu; import względny `from . import modul`, `from .modul import nazwa`, `..` prozą; `__main__.py` i `python -m pakiet`; `python pakiet/` uruchamia `__main__.py` jak skrypt, więc importy względne działają tylko pod `-m` (jedno zdanie); nota o `__spec__`: przy `python plik.py` jest `None`, pod `-m` przechowuje nazwę modułu, dlatego importy względne mają wtedy „rodzica”; pakiety przestrzeni nazw (PEP 420): „W tej książce tworzymy regularne pakiety zawierające `__init__.py`. Python obsługuje również pakiety przestrzeni nazw bez tego pliku.”

**Zależności.** Strony 1–2; funkcje (rozdz. 6; klasy `K1..K3` z PDF zastąpione funkcjami); „pakiet” w znaczeniu pip (`01-instalacja/pip.md`).

**Główne przykłady.** Pakiet `geometria/` z `__init__.py`, `figury.py` (`pole_kola()`, `obwod_kola()`), `jednostki.py` (`cm_na_m()`), drzewo katalogów jako blok tekstowy; REPL: `import geometria` a `geometria.figury`; `ModuleNotFoundError` w wariancie kropkowym; `ImportError: cannot import name …`; `figury.py` z `from .jednostki import cm_na_m`; `python geometria/figury.py` a `python -m geometria.figury`; `geometria/__main__.py` i `python -m geometria`; pakiet bez `__main__.py`.

**Wymagane zachowania do weryfikacji na 3.14.7.** `AttributeError: module 'geometria' has no attribute 'figury'` przed importem podmodułu i dostęp po `import geometria.figury`; `ModuleNotFoundError: No module named 'geometria.brak'`; `ImportError: cannot import name 'pole' from 'geometria.figury' (…\figury.py)`; `import geometria.figury as f` nie wiąże `geometria` (`NameError`); `ImportError: attempted relative import with no known parent package` dla `python geometria/figury.py` i dla `python geometria`; `python -m geometria.figury` i `python -m geometria` działają, `__name__` → `__main__`, `__spec__.name` → `geometria.figury` / `geometria.__main__`; pakiet bez `__main__.py`: „No module named geometria.__main__; 'geometria' is a package and cannot be directly executed”; `from geometria import *` bez `__all__` daje nazwy z `__init__.py`.

**Źródła repozytorium.** `PythonNotatki.txt` 3008–3185 (s. 80–84; `pkg/md1..md3` → `geometria`; kaskadowe `import *` w `__init__` pominięte); `Wyklad_05.txt` sl. 10–13, 36 (korekta tezy „bez `__all__` `import *` → nic”); `lab3.txt` sl. 1.

**Źródła zewnętrzne.** Tutorial *Packages*, *Importing * From a Package*, *Intra-package References*; Language Reference *The import system* (*Regular packages*, *Namespace packages*, *Submodules*, `__spec__`), *The import statement* (relative imports); `library/__main__.html` (`__main__.py`); PEP 420; PEP 328; glosariusz (*regular package*, *namespace package*); Python Packaging User Guide, glosariusz (*import package*, *distribution package*).

**TODO/zapowiedzi do domknięcia.** Brak bezpośrednich; przygotowuje stronę 5.

**Odłożone.** Głębokie subpakiety (jedno zdanie o `..`); `__path__`; `importlib.resources`; `python archiwum.zip`; wtyczki i dynamiczne importy.

**Ryzyka kolejności pojęć.** Kaskadowe `from pkg.pkg1 import *` w `__init__` z PDF daje pod `-m` `RuntimeWarning` — nie kopiować; `__main__.py` z importami względnymi pokazywać wyłącznie pod `-m`; słowo „pakiet” wymaga rozróżnienia na początku strony.

**Orientacyjny rozmiar.** ok. 320–370 linii.

### 5. `struktura-projektu.md` — Struktura projektu i pierwsze testy

**Cel.** Czytelnik układa kod w katalog projektu, sprawdza założenia instrukcją `assert`, pisze pierwsze testy jako funkcje w katalogu `tests/` i uruchamia je najpierw bez frameworka, potem narzędziem pytest, rozumie, po co istnieje układ `src/` i plik `pyproject.toml`, i instaluje własny pakiet edytowalnie w środowisku wirtualnym.

**Kolejność H2/H3.**
1. Od skryptu do projektu
2. Instrukcja `assert` (H3: Porównania liczb zmiennoprzecinkowych)
3. Katalog `tests`
4. Narzędzie pytest
5. Układ `src` i plik `pyproject.toml`
6. Instalacja edytowalna w środowisku wirtualnym

**Pojęcia wprowadzane.** Katalog projektu w układzie płaskim (`projekt/geometria/`, `projekt/program.py`, `projekt/tests/`), uruchamianie z katalogu projektu i związek z `sys.path[0]`; `assert wyrażenie` i `assert wyrażenie, komunikat`, `AssertionError` w śladzie, pułapka `assert (warunek, "komunikat")` pokazana na skrypcie (`SyntaxWarning` przy kompilacji, program biegnie dalej z kodem 0; przy imporcie ostrzeżenie tylko za pierwszym razem), zasada „nie do walidacji danych użytkownika” (zapowiedź wyjątków); H3: `0.1 + 0.2 + 0.3 == 0.6` → `False`, `math.isclose()` gdy chodzi o przybliżoną równość, `Decimal("0.1")` z napisów gdy chodzi o dokładną reprezentację dziesiętną, `round()` krótko jako zaokrąglanie wyniku (nie test równości); funkcja testowa `test_*()`, plik `test_*.py` (wariant `*_test.py` jednym zdaniem; plik testów może leżeć obok modułu jak w laboratorium), `tests/__init__.py` dla spójności i jawności struktury (nie warunek działania), `tests/test_figury.py` ze strażnikiem wywołującym testy i wypisującym „OK”, `python -m tests.test_figury`, kod wyjścia 0/1 (reguła ze strony 3); pytest: czym jest, pakiet zewnętrzny spoza biblioteki standardowej, `python -m pip install pytest` w aktywnym venv (rozdz. 1), `python -m pytest` z katalogu projektu (dodaje katalog bieżący do `sys.path`), automatyczne odnajdywanie `test_*.py` i `test_*()`, wynik zaliczony, wynik niezaliczony (linie `E   assert …`, `FAILED tests/test_figury.py::test_…`), kod wyjścia 0/1; format TOML (dwa zdania: tabele `[…]`, pary `klucz = "wartość"`, listy `[]`, porównanie z `settings.json` z rozdz. 1); układ `src/` (import dopiero po instalacji; różnica pokazana jednym poleceniem `python -c "import tests"` z innego katalogu przed i po); `pyproject.toml`: `[build-system]` jako konfiguracja narzędzi potrzebnych do zbudowania i instalacji projektu (Hatchling jako konkretny backend użyty w przykładzie), `[project]` z `name` (musi odpowiadać nazwie katalogu pakietu w `src/`, bo na tej podstawie Hatchling odnajduje pliki; nazwa pakietu dystrybucyjnego a importowanego), `version`, `requires-python`, `dependencies = []` (pytest nie jest zależnością wykonawczą); `python -m pip install -e .` (pip pobiera backend do izolowanego środowiska budowania — potrzebna sieć), `python -m pip show geometria` (linia „Editable project location”; pełny wydruk z pustymi polami albo oznaczony skrót), `dependencies` a `requirements.txt`; admonition „Układ z laboratorium 3” (`src/__init__.py` i `from src.kalkulator import …` — działa, bo pytest wstawia katalog projektu na `sys.path`, ale `src` nie jest nazwą biblioteki; w książce pakietem jest `src/geometria/`).

**Zależności.** Strony 1–4; venv, `python -m pip`, `pip show`, `requirements.txt`, `site-packages` (rozdz. 1); `float`, `Decimal`, `round()` (rozdz. 3; `typy-proste.md:113–125` pułapka `==` dla `float`); `math` (rozdz. 2–3); funkcje czyste jako testowalne (rozdz. 6).

**Główne przykłady.** Drzewa katalogów obu układów jako bloki tekstowe (bez plików Gita); refaktoryzacja liniowego skryptu z lab2 do `przetworz_wejscie()` + `main()` jako drugi moduł projektu (`program.py`); skrypt z `assert` i przykład `float`/`Decimal`; `test_figury.py` z `test_pole_kola()`, `test_obwod_kola()`, `test_cm_na_m()` (`math.isclose`); przebieg zaliczony („OK”, kod 0) i niezaliczony (ślad `AssertionError`, kod 1); `python -m tests.test_figury` z innego katalogu; `python tests/test_figury.py` (`sys.path[0]` to `tests/`); sesja `python -m pytest` z wynikiem zaliczonym i niezaliczonym; `pyproject.toml`; sesja `python -m pip install -e .` w `.venv` (wydruk skrócony z oznaczeniem) i `python -m pip show geometria`; testy i program uruchomione z dowolnego katalogu po instalacji.

**Wymagane zachowania do weryfikacji na 3.14.7.** `SyntaxWarning: assertion is always true, perhaps remove parentheses?` (kod 0); `AssertionError: komunikat` (kod 1); `0.1 + 0.2 + 0.3 == 0.6` → `False`, `math.isclose(0.1 + 0.2 + 0.3, 0.6)` → `True`, `Decimal("0.1") + Decimal("0.2") + Decimal("0.3") == Decimal("0.6")` → `True`; `python -m tests.test_figury` → „OK”, kod 0, także bez `tests/__init__.py`; ślad niezaliczonego testu z ramkami `<frozen runpy>`; z innego katalogu jednolinijkowy komunikat „Error while finding module specification for 'tests.test_figury' (ModuleNotFoundError: No module named 'tests')”; `python tests/test_figury.py` → `ModuleNotFoundError: No module named 'geometria'`; pytest 9.x na 3.14: „3 passed”, „1 failed, 2 passed” z sekcją `FAILURES` i linią `E   assert …`, kody wyjścia 0/1 (w tymczasowym venv); `python -m pip install -e .` z Hatchling: „Successfully installed geometria-0.1.0”, w drzewie projektu bez nowych plików; `name` różny od nazwy katalogu w `src/` → `metadata-generation-failed` (fakt do zdania przy `name`, bez pokazywania pełnego komunikatu); `pip show`: „Editable project location: …\projekt”; po instalacji import `geometria` z dowolnego katalogu; `import tests` z innego katalogu: działa w układzie płaskim po instalacji edytowalnej, `ModuleNotFoundError` w układzie `src/`.

**Źródła repozytorium.** `Wyklad_05.txt` sl. 32–33, 46 (kroki venv i instalacji; układ „src jako pakiet” omówiony w admonition); `lab3.txt` sl. 1–3, 5–6; `lab2.txt` sl. 6–8.

**Źródła zewnętrzne.** Language Reference *The assert statement*; `math.isclose()`; `decimal` (*Quick-start Tutorial*); Python Packaging User Guide: *src layout vs flat layout*, *Writing your pyproject.toml*, *Packaging Python Projects* (samouczek z Hatchling); pip *Local project installs* (editable); PEP 621 (`[project]`), PEP 517/518 (`[build-system]`); pytest *Get Started*, *Good Integration Practices* (`python -m pytest` a `sys.path`), *How to invoke pytest* (kody wyjścia).

**TODO/zapowiedzi do domknięcia.** `03-nazwy-typy/nazwy-i-slowa-kluczowe.md:14` (`assert`) → uzgodniony tekst; luka planu „pytest lab3”.

**Odłożone.** `pytest.raises` (rozdz. 8); fixtures, parametryzacja, `-k`/`-x`, `conftest.py`, konfiguracja pytest, wtyczki, coverage, `monkeypatch`/mock (rozdz. 16); `unittest` (wymaga klas); `-O` i `__debug__` (rozdz. 8); budowanie (`python -m build`), koło (*wheel*), publikacja; Git, `.gitignore`, `README`, `LICENSE`, CI; `dependencies` niepuste; `[project.scripts]`; NumPy (rozdz. 14); `python -m pip freeze` poza jednym zdaniem.

**Ryzyka kolejności pojęć.** Kod wyjścia 1 z nieprzechwyconego wyjątku musi być wprowadzony na stronie 3; TOML nowy; słowo „pakiet” w `pip show` i `pip install -e .` wymaga przypomnienia rozróżnienia ze strony 4; pytest w tekście książki tylko w zakresie decyzji 2; wydruki pip i pytest zależne od wersji — cytować oszczędnie i oznaczać skróty.

**Orientacyjny rozmiar.** ok. 420–480 linii.

### 6. `biblioteka-standardowa.md` — Biblioteka standardowa i moduł collections

**Cel.** Czytelnik rozumie bibliotekę standardową jako zestaw gotowych modułów importowanych według potrzeb, umie odnaleźć i czytać dokumentację modułu, wraca do modułu `sys` (w tym do limitu rekurencji) i poznaje cztery typy z `collections` jako uzupełnienie typów złożonych.

**Kolejność H2/H3.**
1. Moduły w zestawie
2. Moduł sys
3. Kolejka dwustronna deque
4. Licznik Counter
5. Słownik z wartością domyślną defaultdict
6. Krotka z nazwanymi polami namedtuple (krótko; na końcu jedno zdanie historyczne o `OrderedDict`)

**Pojęcia wprowadzane.** Biblioteka standardowa jako zestaw dostarczany z interpreterem; `sys.stdlib_module_names` jako źródło listy nazw (bez zapisywania liczby); spis modułów w dokumentacji, noty „Added in version”/„Changed in version”, `help(modul)`; tabela w dwóch jawnych grupach: (a) moduły użyte w rozdziałach 1–7 — `sys`, `math`, `keyword`, `decimal`, `fractions`, `copy`, `ctypes`, `this`, `calendar`, `venv`, `pip`, `random` (pułapka na stronie 1), `argparse`, `collections`, `functools`, `itertools`, `importlib`; (b) zapowiadane prozą na dalsze rozdziały — `json`, `pathlib`, `os`, `re` (z admonition, że osobny temat wykracza poza książkę), `datetime`, `statistics`, `time` — bez odsyłaczy; `sys.executable`, `sys.path`, `sys.argv` (przypomnienia), `sys.getrecursionlimit()` wykonywalnie, `sys.setrecursionlimit()` jako istniejące API z zastrzeżeniami z rozdz. 6 (bez przykładu zachęcającego do zwiększania), `sys.stdlib_module_names` jako test kolizji nazw; `deque` (`append`, `appendleft`, `popleft`, `maxlen`, `rotate`; koszt stały niezależny od długości wobec `list.pop(0)` — słownie); idiom zliczania słownikiem zbudowany na miejscu (`licznik[slowo] = licznik.get(slowo, 0) + 1`, odsyłacz do `get()`/`setdefault()` w `slownik.md`) → `Counter` (`most_common()`, `total()`, `+`/`-`), porównanie z `sorted(key=…)` z `funkcje-jako-obiekty.md`; `defaultdict` (`default_factory` jako obiekt wywoływalny, wpis powstaje tylko przy `d[k]`, porównanie z `get()` i `setdefault()`); `namedtuple()` jako funkcja fabryczna tworząca nowy typ będący podklasą krotki: `Punkt = namedtuple("Punkt", ["x", "y"])`, nazwane pola, dostęp `p.x` i `p[0]`, `repr`, niemodyfikowalność odziedziczona po krotce (`AttributeError: can't set attribute`), rozpakowanie jak krotki; zapowiedź innych mechanizmów reprezentowania rekordów danych, w tym klas danych.

**Zależności.** Strona 1; lista, słownik, `get()`, `setdefault()`, `pop(0)`, krotka (rozdz. 5); `callable()`, funkcje klucza, rekurencja i limit (rozdz. 6).

**Główne przykłady.** `"json" in sys.stdlib_module_names`; skrypt z `sys.getrecursionlimit()` (1000 jako szczegół CPythona); kolejka zadań na `deque` i `deque(maxlen=3)` jako bufor ostatnich elementów; zliczanie słownikiem, potem `Counter("abracadabra").most_common(3)`; `defaultdict(list)` grupujące słowa według pierwszej litery i `defaultdict(int)` do zliczania; `Punkt(1, 2)`, `p.x`, `p[0]`, próba `p.x = 5`; `repr` każdego typu.

**Wymagane zachowania do weryfikacji na 3.14.7.** `sys.getrecursionlimit()` → `1000`; `Counter("abracadabra").most_common(3)` → `[('a', 5), ('b', 2), ('r', 2)]`, `.total()` → `11`; `repr` `deque([...], maxlen=3)` po przepełnieniu; `defaultdict(<class 'list'>, {...})`; `Punkt(x=1, y=2)`, `p.x = 5` → `AttributeError: can't set attribute`; `isinstance(p, tuple)` → `True` (jedno zdanie, że nowy typ jest podklasą krotki); `sys.setrecursionlimit()` tylko jako nazwa API.

**Źródła repozytorium.** `Wyklad_05.txt` sl. 9, 40; `Wyklad_03.txt` sl. 15 (namedtuple), 22–23; `PythonNotatki.txt` 2704–2707 (`sys.__dict__` — pominięte).

**Źródła zewnętrzne.** *The Python Standard Library* (wstęp); `sys` (`getrecursionlimit`, `setrecursionlimit`, `stdlib_module_names`, `executable`); `collections` (`deque`, `Counter`, `defaultdict`, `namedtuple` — „factory function for creating tuple subclasses with named fields”); tutorial *Brief Tour of the Standard Library*.

**TODO/zapowiedzi do domknięcia.** `06-funkcje/rekurencja.md:310` (limit w `sys`) → sekcja 2; `05-typy-zlozone/lista.md:487` (`collections.deque`) → sekcja 3; `06-funkcje/index.md:7` (zdanie o `sys`) → sekcja 2.

**Odłożone.** `typing.NamedTuple`, `dataclass` (rozdz. 12; tu tylko zapowiedź); metody `_replace()`, `_asdict()`, `_fields` (najwyżej wzmianka); `OrderedDict` poza zdaniem; `ChainMap`; `re` jako temat; `statistics`, `time`, `os`, `pathlib`, `json` (rozdziały 9–14); `python -m pydoc`.

**Ryzyka kolejności pojęć.** `namedtuple` opisujemy bez wykładu o klasach (słowo „podklasa krotki” pada z odesłaniem do przyszłych rozdziałów); tabela nie może linkować do nieistniejących rozdziałów; idiom zliczania budujemy na miejscu; `Counter`/`deque`/`defaultdict` to użycie gotowych typów, jak `Decimal` w rozdz. 3.

**Orientacyjny rozmiar.** ok. 380–430 linii.

### 7. `functools.md` — Moduł functools

**Cel.** Czytelnik zastępuje własne dekoratory z rozdziału 6 gotowymi narzędziami `functools`: memoizuje rekurencję dekoratorem `cache`, pisze dekoratory z `wraps` (od tej chwili obowiązkowo), stosuje `partial` i zna miejsce `reduce`.

**Kolejność H2/H3.**
1. Pamięć podręczna wyników: cache i lru_cache
2. Zachowanie metadanych: wraps
3. Częściowe zastosowanie: partial
4. Funkcja reduce

**Pojęcia wprowadzane.** `@functools.cache` na `fib`, `cache_info()` (`hits`, `misses` jako szczegół CPythona), wymóg haszowalności argumentów, `lru_cache(maxsize=…)` i kiedy ograniczać pamięć, `cache_clear()`; `@functools.wraps(funkcja)` w dekoratorze `z_ramka`/`licz_wywolania`, kontrast `__name__` = `opakowana` i `__doc__` = `None` bez `wraps` wobec nazwy, docstringu i `help()` funkcji pierwotnej z `wraps`, atrybut `__wrapped__`; `functools.partial(int, base=2)`, `partial(print, sep=", ")`, związek z fabryką funkcji i domknięciem; `functools.reduce()` jednym akapitem z dwoma wywołaniami (iloczyn bez `initial`; sklejanie napisów z `initial=` — od 3.14 także jako argument nazwany), zdanie o pustym iterowalnym, zalecenie książki: `sum()`, `max()`, `math.prod()` (wprowadzone w miejscu użycia) albo pętla.

**Zależności.** Dekoratory, memoizacja, `fib`, fabryki funkcji, domknięcia (`06-funkcje/dekoratory.md`, `rekurencja.md`, `zasieg-nazw-i-domkniecia.md`); haszowalność (rozdz. 5); strona 1.

**Główne przykłady.** `fib` z `@functools.cache`, `fib(100)` i `fib.cache_info()`; `fib([1])`; `z_ramka` z rozdz. 6 bez i z `wraps` — `powitanie.__name__`, `powitanie.__doc__`, `help(powitanie)`, `powitanie.__wrapped__`; `licz_wywolania` z `wraps`; `binarna = partial(int, base=2)`; `reduce(lambda a, b: a * b, [1, 2, 3, 4])` obok `math.prod([1, 2, 3, 4])`; `reduce(lambda a, b: a + " " + b, slowa, initial="Słowa:")`.

**Wymagane zachowania do weryfikacji na 3.14.7.** `fib(100)` → `354224848179261915075`, `fib.cache_info()` → `CacheInfo(hits=98, misses=101, maxsize=None, currsize=101)`; `fib([1])` → `TypeError: unhashable type: 'list'`; bez `wraps`: `__name__` → `'opakowana'`, `__doc__` → `None`, `help()` pokazuje `opakowana(*args, **kwargs)`; z `wraps`: nazwa, docstring i sygnatura pierwotna w `help()`, `__wrapped__` wskazuje funkcję pierwotną, `__annotations__` funkcji pierwotnej dostępne; `functools.WRAPPER_ASSIGNMENTS` w 3.14.7 zawiera `__annotate__` (fakt do kontroli wobec tekstu dokumentacji — nie trafia do książki); `partial(int, base=2)("101")` → `5`; `reduce(..., initial=...)` działa jako argument nazwany; `reduce(f, [])` → `TypeError: reduce() of empty iterable with no initial value`; `math.prod([1, 2, 3, 4])` → `24`.

**Źródła repozytorium.** `Wyklad_04.txt` sl. 21, 26, 28; `lab6.txt` sl. 1–2; `PythonNotatki.txt` 2651–2681 (`reduce` — oba przykłady).

**Źródła zewnętrzne.** `functools` (`cache`, `lru_cache`, `wraps`, `update_wrapper`, `partial`, `reduce` — „Changed in version 3.14: initial as keyword”; `Placeholder` tylko do świadomości); `Lib/functools.py` 3.14 (kontrola zachowania `wraps`); HOWTO *Functional Programming* (`reduce`); `math.prod()`.

**TODO/zapowiedzi do domknięcia.** `06-funkcje/dekoratory.md:374` (`cache`/`lru_cache`) → sekcja 1; `06-funkcje/dekoratory.md:443` (`wraps`) → sekcja 2; `06-funkcje/dekoratory.md:540` (`cache` i `wraps`) → sekcje 1–2 (część o klasach pozostaje zapowiedzią z komentarzem); `06-funkcje/rekurencja.md:207` (memoizacja) → sekcja 1; `06-funkcje/funkcje-jako-obiekty.md:431` (`reduce`, `partial`, `operator` prozą) → sekcje 3–4; `06-funkcje/index.md:7` (`functools`) → podrozdział.

**Odłożone.** `cached_property`, `singledispatch`, `total_ordering` (klasy); `Placeholder` (3.14); moduł `operator` (jedno zdanie); `cmp_to_key`; `lru_cache` na metodach.

**Ryzyka kolejności pojęć.** Opis `wraps` w brzmieniu z zasad, bez listy atrybutów; `math.prod()` wprowadzony w zdaniu; `reduce` nie jako preferowana alternatywa dla pętli i `sum()`.

**Orientacyjny rozmiar.** ok. 260–300 linii.

### 8. `itertools.md` — Moduł itertools

**Cel.** Czytelnik poznaje gotowe iteratory `itertools` jako uzupełnienie własnych generatorów z rozdziału 6 — bez encyklopedycznego przeglądu — i wie, gdzie szukać reszty. Pierwszy akapit zaznacza, że materiał jest opcjonalny i można do niego wrócić później.

**Kolejność H2/H3.**
1. Iteratory nieskończone: count, cycle, repeat
2. Wycinki i łączenie: islice, chain
3. Okna i porcje: pairwise, batched
4. Akumulacja i przekształcanie: accumulate, starmap
5. Grupowanie: groupby
6. Kombinatoryka: product, permutations, combinations (jeden krótki wspólny fragment; na końcu akapit „Dalsze narzędzia” z wyliczeniem `zip_longest`, `takewhile`, `dropwhile`, `filterfalse`, `compress`, `tee` oraz odesłaniem do przepisów z dokumentacji i `more-itertools`)

**Pojęcia wprowadzane.** `count()` (odpowiednik `naturalne()` z rozdz. 6), `cycle()`, `repeat()` z `islice()` jako bezpiecznym odbiorcą; `islice()`, `chain()` (a `polacz()` z `yield from`); `pairwise()` (3.10), `batched()` (3.12) ze `strict=True` (3.13); `accumulate()` (a `sum()`/`reduce()`), `starmap()` krótko jako naturalne następstwo rozpakowywania `*args` (a `map()`); `groupby()` z wymogiem posortowania (wynik „przed i po” `sorted()`) i funkcją klucza; `product()`, `permutations()`, `combinations()` w jednym fragmencie; jednorazowość iteratorów (od 3.14 iteratory `itertools` nie obsługują kopiowania ani piklowania — prozą), `tee()` wymieniony z uwagą, że oryginał zostaje zużyty.

**Zależności.** Iteratory (rozdz. 4); `zip` (rozdz. 5); generatory, potoki, `yield from`, funkcje klucza, `lambda`, `map()`, `*args` (rozdz. 6); `reduce` (strona 7).

**Główne przykłady.** `list(islice(count(1), 5))`; `cycle` z `islice`; `chain("ab", [1, 2])`; `pairwise([1, 2, 3, 4])`; `batched("ABCDEFG", 3)` i `strict=True`; `accumulate([1, 2, 3, 4])`; `starmap(pow, [(2, 3), (3, 2)])`; `groupby` na danych nieposortowanych (grupy rozbite) i posortowanych; `product("ab", repeat=2)`, `permutations`, `combinations` na jednym krótkim zbiorze.

**Wymagane zachowania do weryfikacji na 3.14.7.** `list(islice(count(1), 5))` → `[1, 2, 3, 4, 5]`; `list(batched("ABCDEFG", 3))` → `[('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]`, ze `strict=True` → `ValueError: batched(): incomplete batch`; `list(pairwise([1, 2, 3, 4]))` → `[(1, 2), (2, 3), (3, 4)]`; `list(accumulate([1, 2, 3, 4]))` → `[1, 3, 6, 10]`; `list(starmap(pow, [(2, 3), (3, 2)]))` → `[8, 9]`; `groupby` bez sortowania daje rozbite grupy, po `sorted()` scalone; `copy.copy(count())` → `TypeError` (komunikat mówi o pickle — nie cytować); `itertools` ma 20 nazw publicznych w 3.14.7 (bez zapisywania liczby).

**Źródła repozytorium.** `Wyklad_08.txt` sl. 26–31, 40; `Wyklad_03.txt` sl. 31, 43.

**Źródła zewnętrzne.** `itertools` (tabele, `batched`, `pairwise`, *Itertools Recipes*); What's New 3.12 (`batched`), 3.13 (`strict`), 3.14 (usunięcie kopiowania i piklowania iteratorów); HOWTO *Functional Programming*.

**TODO/zapowiedzi do domknięcia.** `06-funkcje/funkcje-generatorowe.md:248` (`itertools`) → sekcje 1–2; `06-funkcje/funkcje-jako-obiekty.md:431` (`itertools`) → podrozdział; `06-funkcje/index.md:7` (`itertools`) → podrozdział.

**Odłożone.** Pełne przykłady `zip_longest`, `takewhile`, `dropwhile`, `filterfalse`, `compress`, `tee`; `combinations_with_replacement`; `chain.from_iterable`; implementacje przepisów (w tym `chunked` z W08); `islice` na pliku (rozdz. 9).

**Ryzyka kolejności pojęć.** `groupby` zwraca iteratory grup — pokazać `list()`; bez obietnic o kolejności `set`; strona ma pozostać zwięzła mimo liczby narzędzi.

**Orientacyjny rozmiar.** ok. 280–330 linii.

### 9. `index.md` — Wprowadzenie

Wstęp (dwa–trzy akapity): od pojedynczego pliku do projektu — plik staje się modułem, moduły układają się w pakiety, a pakiet w projekt z testami; instrukcja `import` jako mechanizm, na którym opierają się wszystkie dalsze rozdziały; nawiązanie do rozdz. 1 (venv, pip, `sys.path`), rozdz. 2 (`python -m`) i rozdz. 6 (zapowiedzi `functools`, `itertools`, `sys`). Następnie `---` i `## W tym rozdziale` z ośmioma pozycjami „Tytuł — tematy” w konwencji istniejących rozdziałów; przy „Moduł itertools” zaznaczony charakter opcjonalny. Bez „Powiązane laboratorium” i bez „Ściągi”. Orientacyjny rozmiar: ok. 20 linii.

## Nawigacja (dodawana wraz z powstającymi stronami, za zgodą autora)

```yaml
  - 7. Moduły, pakiety i biblioteka standardowa:
      - Wprowadzenie: 07-moduly/index.md
      - Moduły i instrukcja import: 07-moduly/moduly-i-import.md
      - Skrypt jako program: 07-moduly/skrypt-jako-program.md
      - Argumenty wiersza poleceń: 07-moduly/argumenty-wiersza-polecen.md
      - Pakiety: 07-moduly/pakiety.md
      - Struktura projektu i pierwsze testy: 07-moduly/struktura-projektu.md
      - Biblioteka standardowa i moduł collections: 07-moduly/biblioteka-standardowa.md
      - Moduł functools: 07-moduly/functools.md
      - Moduł itertools: 07-moduly/itertools.md
```

Pozycja w `docs/index.md` (dodawana wraz z `index.md` rozdziału): „7. [Moduły, pakiety i biblioteka standardowa](07-moduly/index.md) — moduły i import, skrypt jako program, argumenty wiersza poleceń, pakiety, struktura projektu i pierwsze testy, biblioteka standardowa i collections, functools, itertools”.

## Kolejność tworzenia stron i odbiór

Każda strona przechodzi cykl: research w dokumentacji 3.14 → napisanie → uruchomienie wszystkich przykładów (`verify_page.py` dla skryptów, osobna weryfikacja bloków REPL, ręczne wykonanie poleceń terminalowych w katalogu próbnym poza repozytorium) → `mkdocs build` i `mkdocs build -f mkdocs.clean.yml` → niezależna recenzja (styl, fakty, kolejność pojęć, aktualność 3.14) → naniesienie ustaleń → raport → akceptacja autora → commit z komunikatem autora. Kolejność: 1 `moduly-i-import.md`, 2 `skrypt-jako-program.md`, 3 `argumenty-wiersza-polecen.md`, 4 `pakiety.md`, 5 `struktura-projektu.md`, 6 `biblioteka-standardowa.md`, 7 `functools.md`, 8 `itertools.md`, 9 `index.md`. Wpis nav i pozycja na stronie głównej rosną wraz z powstającymi stronami (zmiany `mkdocs.yml` i `docs/index.md` za zgodą autora). Pakiet `geometria` ze strony 4 jest wspólny dla stron 4–5 i musi pozostać spójny.

## Zmiany w rozdziałach 1–6 (wyłącznie domknięcie zapowiedzi, zbiorczo po ukończeniu rozdziału 7)

| Plik:linia | Zmiana | Uwagi |
|---|---|---|
| `03-nazwy-typy/nazwy-i-slowa-kluczowe.md:14` | dopisanie do uzgodnionego zdania: „…, `import`, `from` i `as` w podrozdziale [Moduły i instrukcja import](../07-moduly/moduly-i-import.md), a `assert` w podrozdziale [Struktura projektu i pierwsze testy](../07-moduly/struktura-projektu.md)” | jedna edycja; zachować dotychczasowe cztery odsyłacze |
| `05-typy-zlozone/lista.md:487–492` | nota „collections.deque” → odsyłacz do `biblioteka-standardowa.md#kolejka-dwustronna-deque` | tekst noty zachowany |
| `06-funkcje/index.md:7` | zdanie o `functools`, `itertools` i `sys` → odsyłacze do `functools.md`, `itertools.md`, `biblioteka-standardowa.md` | |
| `06-funkcje/definiowanie-funkcji.md:177` | `TODO` → odsyłacz do `moduly-i-import.md` (docstring modułu) | |
| `06-funkcje/argumenty-i-parametry.md:317` | `TODO` → odsyłacz do `skrypt-jako-program.md` (`__main__`) | |
| `06-funkcje/rekurencja.md:207` | `TODO` → odsyłacz do `functools.md` (`cache`) | |
| `06-funkcje/rekurencja.md:310` | `TODO` → odsyłacz do `biblioteka-standardowa.md` (moduł `sys`) | |
| `06-funkcje/funkcje-jako-obiekty.md:431` | `TODO` → odsyłacze do `functools.md` i `itertools.md` | |
| `06-funkcje/funkcje-generatorowe.md:248` | `TODO` → odsyłacz do `itertools.md` | |
| `06-funkcje/dekoratory.md:374`, `:443` | `TODO` → odsyłacze do `functools.md` | |
| `06-funkcje/dekoratory.md:540` | `TODO` → odsyłacz do `functools.md`; część o klasach pozostaje zapowiedzią z komentarzem | |
| `docs/index.md`, `mkdocs.yml` | pozycja „7. Moduły, pakiety i biblioteka standardowa” w spisie i w nav (blok wyżej) | nav rośnie wraz z powstającymi stronami |

Reguła: powyższe zmiany wykonujemy jednym zbiorczym etapem redakcji po zaakceptowaniu wszystkich stron rozdziału 7 (jak przy rozdziale 6), z kontrolą semantyczną każdego zdania i sprawdzeniem kotwic w zbudowanym HTML. Nie wykonujemy innych zmian w rozdziałach 1–6 (`01-instalacja/konfiguracja.md:102` i `02-konsola/pierwszy-skrypt.md:62` są już domknięte odsyłaczami do rozdz. 6; zdanie o `*.pyc` w `01-instalacja/index.md:25` pozostaje do osobnego etapu według `PLAN_ROZWOJU.md`, sekcja 6).

## CONTENT HANDOFF (rozbieżności ze starszymi materiałami i laboratorium 3)

Książka ma rację, materiały kursu do poprawki: (a) układ „`src` jako pakiet” (`src/__init__.py`, `from src.kalkulator import …`) działa tylko dzięki temu, że pytest wstawia katalog projektu na `sys.path`; standardem jest `src/<pakiet>/` z instalacją edytowalną (książka omawia wariant laboratoryjny w admonition); (b) opis `sys.path[0]` jako „katalog, w którym uruchomiono skrypt” — poprawnie: katalog skryptu, `''` w konsoli i przy `-c`, katalog bieżący przy `-m`; (c) teza „bez `__all__` `from pkg import *` → nic” — importowane są nazwy z `__init__.py` bez wiodącego podkreślenia; (d) goły `pip install pytest` → `python -m pip install pytest`; (e) termin „pakiet przestrzenny” → „pakiet przestrzeni nazw (ang. *namespace package*)”; (f) wzorzec `assert dodaj(2.5, 3.1) == 5.6` dla `float` jest kruchy — książka uczy `math.isclose()` i `Decimal` z napisów. Bez konfliktu: konwencje nazw testów, `__init__.py` w `tests/`, `sys.modules`/`reload`, plik testów obok modułu, pytest jako narzędzie laboratorium (zakres książki: decyzja 2).

## Checklista weryfikacyjna strony (przed odbiorem)

1. Wszystkie deterministyczne przykłady uruchomione na `.venv` (Python 3.14.7): skrypty przez `verify_page.py`, sesje REPL osobno, polecenia terminalowe (`python -m`, `argparse`, `python -m pytest`, `python -m pip install -e .`) ręcznie w katalogu próbnym poza repozytorium; pytest i instalacja edytowalna w tymczasowym venv, nigdy w `.venv` projektu; wyniki, ślady wywołań, teksty pomocy, wyniki pytest i komunikaty pip wpisane z uruchomienia; dostęp do sieci odnotowany tam, gdzie był potrzebny.
2. Brak mechanizmów z późniejszych rozdziałów: `try/except`, `raise`, `open()`, `class`, `dataclass`; wyjątki wyłącznie w śladach wywołań; pytest wyłącznie w zakresie decyzji 2.
3. Kolejność wewnątrz rozdziału: podrozdział używa wyłącznie pojęć z podrozdziałów wcześniejszych i rozdziałów 1–6; pojęcia z listy „do wprowadzenia jawnie” wprowadzone w miejscu pierwszego użycia; odsyłacze w przód tylko jako zapowiedzi prozą, bez linków do nieistniejących rozdziałów.
4. Nazwy plików przykładowych bez kolizji z biblioteką standardową; pakiet `geometria` spójny między stronami 4–5; nazwa projektu w `pyproject.toml` równa nazwie katalogu pakietu w `src/`; drzewa katalogów bez plików Gita.
5. Atrybuty modułu ograniczone do `__name__`, `__doc__`, `__file__` (+ `__spec__` w nocie na stronie 4); brak twierdzeń o ostrzeżeniach przy atrybutach przestarzałych; brak zapisanych liczb modułów biblioteki standardowej.
6. `sys.path.append()` i goły `pip` wyłącznie w blokach `.no-copy`, z oceną zgodną z zasadami; `sys.setrecursionlimit()` bez przykładu zwiększania limitu.
7. `functools.wraps` opisany uzgodnionym sformułowaniem, bez listy atrybutów i bez `__module__`.
8. Terminologia i docstringi zgodne z zasadami; „podrozdział” dla części książki; nagłówki rzeczownikowe z nazwami w kodzie; `namedtuple()` jako funkcja fabryczna tworząca podklasę krotki.
9. Konwencje `CLAUDE.md`: bloki kodu z `title=` albo `.no-copy`, `toml title="pyproject.toml"`, admonitions z polskimi tytułami, cudzysłowy „…”, terminy angielskie z „ang.”, `python -m pip`, klawisze `++…++`.
10. Szczegóły CPythona (limit rekurencji, `cache_info()`, zestaw dunder w `dir()`, ścieżki, ramki `<frozen runpy>`) oznaczone jako szczegół implementacyjny; ścieżki Windows zamaskowane jednolicie; brak przekierowań wyjścia z polskimi znakami; wyniki zależne od terminala (kolor `argparse`) poza blokami porównywanymi.
11. `mkdocs build` bez ostrzeżeń oraz `mkdocs build -f mkdocs.clean.yml` (bez warstwy interaktywnej w wyniku).
12. Każdy odsyłacz względny prowadzi do istniejącego pliku i sekcji (`id` sprawdzone w zbudowanym HTML; „ł” w slugach jest pomijane); teksty odsyłaczy współdzielonych identyczne z ustalonymi wyżej.
13. Struktura: do około 6 H2 jako wskazówka; sekcje opcjonalne oznaczone w tytule H3/noty „Dla dociekliwych”; długość według treści, nie limitu.

## Checklista finalnego odbioru rozdziału

1. Wszystkie dziewięć plików zaakceptowanych; nav i `docs/index.md` zawierają komplet pozycji; H1 = etykieta nav (index: „Wprowadzenie” / H1 „7. Moduły, pakiety i biblioteka standardowa”).
2. Zbiorcza redakcja: ujednolicona terminologia (pakiet importowany / dystrybucyjny, pakiet przestrzeni nazw, strażnik uruchomienia, kod wyjścia, instalacja edytowalna), spójny pakiet `geometria`, spójne maskowanie ścieżek, brak powtórzeń między stronami 1–2 (`sys.path[0]`) i 3–5 (kody wyjścia).
3. Tabela „Zmiany w rozdziałach 1–6” wykonana w całości; w `docs/06-funkcje/` nie pozostał żaden komentarz `TODO` wskazujący na moduły; komentarze wskazujące na wyjątki, klasy, narzędzia typów, tkinter i korutyny pozostają.
4. Pełny przebieg weryfikacji: `verify_page.py` dla wszystkich stron rozdziału (zero rozbieżności), bloki REPL, polecenia terminalowe, audyt odsyłaczy i kotwic w zbudowanym HTML, `mkdocs build` i `mkdocs build -f mkdocs.clean.yml`, `node --test` i `python -m unittest discover -s tests` bez regresji, `git diff --check`.
5. Ponowna kontrola faktów zależnych od wersji: `functools.WRAPPER_ASSIGNMENTS` wobec tekstu dokumentacji, sygnatura `ArgumentParser` 3.14, `batched(strict=)`, wersja pytest i pip w tymczasowym venv, komunikaty 3.14.7.
6. `PLAN_ROZWOJU.md`: status rozdziału 7 „ukończony” z rzeczywistą liczbą linii; CONTENT HANDOFF przekazany autorowi w raporcie końcowym.
7. Commit końcowy z komunikatem autora; bez zmian brancha i bez integracji do `dev` bez osobnego polecenia.
