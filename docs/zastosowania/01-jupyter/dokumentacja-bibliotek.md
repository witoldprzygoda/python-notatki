# Czytanie dokumentacji bibliotek

Biblioteki z tego tomu mają po kilkaset funkcji; żaden podręcznik ich nie wyczerpie i nie jest to jego celem. Umiejętnością trwałą jest sprawne czytanie dokumentacji: odnalezienie właściwej funkcji, zrozumienie jej sygnatury i sprawdzenie, czy opis dotyczy zainstalowanej wersji. Ten podrozdział pokazuje, jak zbudowana jest dokumentacja dużej biblioteki, jak czytać ją z poziomu notatnika i po czym poznać pakiet wart zainstalowania.

## Przewodnik a opis API

Dokumentacja dojrzałej biblioteki ma dwie części. **Przewodnik użytkownika** (ang. *user guide*) wyjaśnia pojęcia i typowe zadania w kolejności odpowiedniej do nauki — od niego zaczynamy, gdy biblioteka jest nowa. **Opis API** (ang. *API reference*) wylicza wszystkie funkcje, klasy i ich parametry alfabetycznie lub według modułów — do niego sięgamy, gdy wiemy, czego szukamy, i potrzebujemy szczegółów. Dokumentacja NumPy (`numpy.org/doc`) ma ponadto samouczek „NumPy quickstart”, a Matplotlib — galerię przykładów z kodem, w której szybciej znaleźć potrzebny wykres, niż czytając opisy. Do dokumentacji trafiamy, wpisując w wyszukiwarkę nazwę biblioteki i funkcji; wynik z domeny projektu jest wiarygodniejszy niż przypadkowy blog, a data wersji na stronie mówi, czy opis jest aktualny.

## Docstring, `help()` i `inspect.signature()`

Opis API jest generowany z docstringów, które poznaliśmy w rozdziale 6 tomu I — więc ten sam tekst czytamy bez przeglądarki: w notatniku znakiem `?`, w skrypcie funkcją `help()`, a samą sygnaturę daje moduł `inspect`:

```python title="sygnatura.py"
import inspect

import numpy as np

print(inspect.signature(np.linspace))
print(np.linspace.__doc__.strip().splitlines()[0])
print(inspect.signature(np.mean))
```

```{ .text .no-copy }
(start, stop, num=50, endpoint=True, retstep=False, dtype=None, axis=0, *, device=None)
Return evenly spaced numbers over a specified interval.
(a, axis=None, dtype=None, out=None, keepdims=<no value>, *, where=<no value>)
```

Sygnaturę czytamy tak, jak nauczyliśmy się w rozdziale 6: parametry bez wartości domyślnej są wymagane (`start`, `stop`), pozostałe mają wartości domyślne, a wszystko po gwiazdce trzeba podać jako argumenty nazwane. Wartość `<no value>` w `np.mean()` oznacza, że biblioteka rozróżnia „nie podano” od `None`. Pełny docstring opisuje każdy parametr w sekcji *Parameters*, wynik w *Returns*, a na końcu podaje przykłady w postaci sesji `>>>` — najszybszy sposób, aby sprawdzić, jak funkcji używać.

## Wersje, zmiany i ostrzeżenia o wycofaniu

Biblioteki zmieniają się: parametr dostaje nową nazwę, funkcja przenosi się do innego modułu, stare wywołanie przestaje działać. Numer wersji `2.5.3` czytamy jako *główna.mniejsza.poprawkowa*: trzecia liczba to poprawki błędów, druga — nowe możliwości i ostrzeżenia o wycofaniu, pierwsza — zmiany łamiące zgodność. NumPy, jak większość bibliotek naukowych, nie stosuje ścisłego **wersjonowania semantycznego** (ang. *semantic versioning*): wydanie mniejsze może usunąć funkcję, o której wycofaniu ostrzegało co najmniej dwa wydania wcześniej — dlatego ostrzeżeń nie wolno ignorować; przejście z NumPy 1 na 2 wymagało poprawek w wielu projektach. Zanim funkcja zniknie, biblioteka ostrzega — tak samo jak biblioteka standardowa:

```python title="ostrzezenie.py"
import datetime

print(datetime.datetime.utcnow())
```

```{ .text .no-copy }
ostrzezenie.py:3: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
  print(datetime.datetime.utcnow())
2026-09-13 20:38:33.813993
```

`DeprecationWarning` należy do gałęzi `Warning` z rozdziału 8 tomu I — jak każde ostrzeżenie nie przerywa programu, ale mówi, co zmienić i na co; w notatniku pojawia się pod komórką (JupyterLab wyróżnia je różowym tłem, VSC wypisuje jak zwykły tekst). Ostrzeżeń nie wyciszamy — poprawiamy wywołanie od razu, póki zmiana ogranicza się do jednego wiersza. Historię zmian biblioteki opisuje jej dziennik wydań (ang. *release notes*, *changelog*) — pierwsze miejsce, do którego zaglądamy po aktualizacji, gdy coś przestało działać. Wersję zainstalowanego pakietu podaje `python -m pip show numpy`, a dostępne wydania — `python -m pip index versions numpy`.

## Zasada „najpierw biblioteka standardowa”

Każdy pakiet zewnętrzny to zależność: wersja do przypięcia, ryzyko porzucenia przez autorów, dodatkowa instalacja u każdego użytkownika. Zanim go dodamy, sprawdzamy, czy zadania nie rozwiązuje biblioteka standardowa z tomu I:

| Zadanie | Biblioteka standardowa | Pakiet zewnętrzny — gdy |
|---|---|---|
| statystyki opisowe kilku liczb | `statistics` | NumPy, gdy danych są tysiące albo są w tablicach |
| odczyt i zapis CSV, JSON | `csv`, `json` | pandas, gdy tabela ma wiele kolumn do przekształcania |
| daty i czas | `datetime`, `zoneinfo` | pandas, gdy szeregi czasowe wymagają grupowania po czasie |
| pobranie strony lub pliku z sieci | `urllib.request` | `httpx` lub `requests`, gdy potrzebne sesje, nagłówki, ponawianie |
| wyrażenia regularne | `re` | — |
| wykres | — | Matplotlib |
| baza danych | `sqlite3` | SQLAlchemy, gdy baza jest serwerowa lub model danych jest złożony |

Reguła nie zabrania pakietów — pandas i Matplotlib są tematem tej ścieżki — lecz każe wybierać je z uzasadnionej potrzeby, nie z przyzwyczajenia.

## Ocena pakietu z PyPI

Gdy zadanie wymaga pakietu spoza tomu, oceniamy go na stronie PyPI i w repozytorium projektu, zanim go zainstalujemy:

- **data ostatniego wydania i rytm wydań** — pakiet bez wydań od kilku lat może nie działać z Pythonem 3.14;
- **obsługiwane wersje Pythona** w metadanych i w nazwach plików binarnych — **kół** (ang. *wheel*), o których wspomina rozdział 1 tomu I; `cp314` w nazwie pliku oznacza gotowe koło dla CPythona 3.14;
- **dokumentacja** — czy istnieje przewodnik i opis API, czy tylko README;
- **licencja** — czy pozwala na nasze zastosowanie; w projektach studenckich i naukowych zwykle tak, w komercyjnych wymaga sprawdzenia;
- **zależności** — `python -m pip show nazwa` po instalacji w osobnym środowisku pokazuje, jakie zależności pakiet instaluje;
- **liczba użytkowników i zgłoszeń** w repozytorium — nie jako kryterium rozstrzygające, lecz jako sygnał, że ktoś pakietu używa i go naprawia.

Nazwę pakietu wpisujemy uważnie: w PyPI istnieją pakiety o nazwach zbliżonych do popularnych, celowo mylące. Instalujemy pakiet pod nazwą podaną w dokumentacji projektu, a nie pod nazwą z pierwszego wyniku wyszukiwarki.
