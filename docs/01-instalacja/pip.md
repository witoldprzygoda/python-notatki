# Pip — zarządzanie pakietami

W praktyce niemal zawsze istnieje konieczność doinstalowania pakietów. Służy do tego **pip** — oficjalny menedżer pakietów Pythona, który pozwala instalować, aktualizować oraz usuwać biblioteki. Pakiety pobierane są z Python Package Index ([PyPI](https://pypi.org/)), czyli największego repozytorium oprogramowania open source dla Pythona.

## Najważniejsza zasada: pip poprzez interpreter

Przy kilku zainstalowanych wersjach Pythona nie zaleca się używania samodzielnego polecenia:

```{ .text .no-copy }
pip install requests
```

ponieważ powstaje wówczas pytanie, który plik `pip.exe` został odnaleziony przez system Windows. Po instalacji samym managerem polecenie `pip` zwykle w ogóle nie działa: plik `pip.exe` trafia do katalogu `%LocalAppData%\Python\bin`, którego domyślnie nie ma w zmiennej `PATH` (opis w podrozdziale [Ścieżki i utrzymanie](sciezki-i-utrzymanie.md)). Zamiast tego stosujemy formę `INTERPRETER -m pip`, która jednoznacznie wiąże polecenie z konkretnym interpreterem. Dla interpretera domyślnego:

```powershell title="Terminal"
python -m pip install requests
```

Dla jawnie wskazanych interpreterów (składnia `py -V:<TAG>` opisana w podrozdziale [Instalacja Pythona](instalacja.md)):

```powershell title="Terminal"
py -V:3.14 -m pip install requests
py -V:3.14t -m pip install requests
```

Dokumentacja Python Install Managera również rekomenduje formę `python -m pip` w przypadku problemów z globalnym poleceniem `pip`. Wszystkie przykłady w niniejszym podrozdziale stosują tę konwencję.

## Przypisanie pip do interpretera

Po świeżej instalacji warto zweryfikować przypisanie:

```powershell title="Terminal"
python -m pip --version
py -V:3.14 -m pip --version
py -V:3.14t -m pip --version
```

Dwa pierwsze polecenia powinny odnosić się do standardowego interpretera 3.14, trzecie — do wariantu 3.14t. Obowiązuje prosta reguła:

```{ .text .no-copy }
py -V:3.14 -m pip
       │
       └── pip standardowego 3.14

py -V:3.14t -m pip
        │
        └── pip free-threaded 3.14t
```

Nie należy zakładać, że biblioteka zainstalowana dla jednego interpretera jest automatycznie dostępna dla drugiego — każdy interpreter dysponuje własnym, odrębnym zestawem pakietów.

## Miejsce instalowania pakietów

!!! warning "Zalecenie: pakiety instalujemy w środowisku venv"
    Zdecydowanie zaleca się nieinstalowanie pakietów w globalnej instalacji interpretera,
    lecz w utworzonym dla projektu środowisku wirtualnym (opis w podrozdziale
    [Wirtualne środowisko venv](venv.md)). Przemawiają za tym dwa względy:
    globalna instalacja jest współdzielona przez wszystkie projekty, co prowadzi do
    konfliktów wersji bibliotek, a ponadto aktualizacja interpretera przez managera
    usuwa globalnie doinstalowane pakiety (opis w podrozdziale
    [Ścieżki i utrzymanie interpreterów](sciezki-i-utrzymanie.md)). Po aktywacji
    środowiska polecenie `python -m pip install ...` instaluje pakiety wyłącznie
    do katalogu `.venv` danego projektu.

## Przykład instalacji

Zainstalujmy rozszerzenie [IPython](https://ipython.org/) (ang. *An enhanced Interactive Python*), które m.in. numeruje kolejne wykonywane polecenia. Przykład najlepiej wykonać w aktywnym środowisku wirtualnym projektu (opis w podrozdziale [Wirtualne środowisko venv](venv.md)):

```powershell title="Terminal"
python -m pip install ipython
```

Po zainstalowaniu powłokę uruchamiamy poleceniem `ipython`:

```{ .text .no-copy }
(.venv) PS C:\projekty\moj-projekt> ipython
Python 3.14.8 (tags/v3.14.8:8e6e75d, Sep 30 2026, 18:19:33) [MSC v.1944 64 bit (AMD64)]
Type 'copyright', 'credits' or 'license' for more information
IPython 9.17.1 -- An enhanced Interactive Python. Type '?' for help.
Tip: The `%timeit` magic has a `-o` flag, which returns the results, making it easy to plot. See `%timeit?`.

In [1]: print("hello")
hello

In [2]:
```

Znaki zachęty `In [1]:`, `In [2]:` … pokazują wspomnianą numerację kolejnych poleceń. Wiersz rozpoczynający się od `Tip:` zawiera losowo wybraną wskazówkę dotyczącą pracy w powłoce, dlatego przy kolejnych uruchomieniach może mieć inną treść. Powłokę opuszczamy poleceniem `exit`.

Jeżeli w PyPI dostępna jest nowsza wersja pip niż zainstalowana, sam pip informuje o tym na końcu wyniku instalacji (wiersze rozpoczynające się od `[notice]`) i zachęca do aktualizacji — wykonujemy ją poleceniem:

```powershell title="Terminal"
python -m pip install --upgrade pip
```

## Przydatne polecenia

Na przykładzie pakietu `requests`:

- `python -m pip show requests` — sprawdzenie, czy requests jest zainstalowane; wersja i inne informacje,
- `python -m pip install requests==2.32.3` — zainstalowanie konkretnej wersji pakietu, tutaj 2.32.3,
- `python -m pip uninstall requests` — usunięcie pakietu,
- `python -m pip index versions requests` — sprawdzenie dostępnych wersji,
- `python -m pip install --upgrade requests` — aktualizacja do najnowszej wersji,
- `python -m pip list` — wypisanie wszystkich zainstalowanych pakietów.

Jeżeli instalacja pakietu ulegnie uszkodzeniu (zdarza się tak np. w wyniku ręcznych manipulacji zainstalowanymi wersjami Pythona), można wymusić jego ponowną instalację w tej samej wersji. Pierwsze polecenie odczytuje zainstalowaną wersję pakietu i zapisuje ją w zmiennej powłoki `$wersja`, drugie instaluje ponownie dokładnie tę wersję, bez zależności; jeżeli pakietu nie ma, oba polecenia kończą się komunikatem o błędzie i niczego nie zmieniają:

```powershell title="Terminal"
$wersja = python -c "from importlib.metadata import version; print(version('requests'))"
python -m pip install --force-reinstall --no-deps "requests==$wersja"
```

albo dodatkowo z pominięciem pamięci podręcznej (wymuszeniem ponownego pobrania pakietu):

```powershell title="Terminal"
$wersja = python -c "from importlib.metadata import version; print(version('requests'))"
python -m pip install --force-reinstall --no-deps --no-cache-dir "requests==$wersja"
```

Odczyt wersji i opcja `--no-deps` są tu istotne: bez nich `--force-reinstall` instaluje najnowsze wersje pakietu i wszystkich jego zależności, zastępując wersje dotychczasowe — także te przypięte w pliku wymagań projektu.

!!! note "Zgodność pakietu z wersją interpretera"
    Pakiety z rozszerzeniami kompilowanymi (np. NumPy) publikują gotowe pliki binarne
    (ang. *wheel*) osobno dla każdej wersji interpretera. Starsze wydania pakietu mogą
    nie obsługiwać najnowszego Pythona — próba instalacji kończy się wtedy komunikatem
    o braku pasującej dystrybucji. Dostępność wersji dla używanego interpretera
    sprawdzamy poleceniem `python -m pip index versions <pakiet>`.

## Plik requirements.txt

Informację o zainstalowanych pakietach, sformatowaną pod kątem instalacji całej grupy, zwraca polecenie `python -m pip freeze`. Najczęściej wynik zapisuje się (przekierowując strumień standardowy) do pliku o nazwie `requirements.txt`. Przekierowanie `>` zastępuje bez ostrzeżenia całą zawartość istniejącego pliku — także pliku wymagań przygotowanego ręcznie, jak w przykładach poniżej — dlatego polecenie zapisuje wynik tylko wtedy, gdy pliku jeszcze nie ma; do istniejącego pliku potrzebne wiersze z wydruku `python -m pip freeze` przenosimy ręcznie:

```powershell title="Terminal"
if (-not (Test-Path requirements.txt)) { python -m pip freeze > requirements.txt }
```

Pisząc projekt wymagający określonych bibliotek, warto załączyć do niego taki plik wymagań. Przykładowo, podstawowy zestaw do obliczeń numerycznych, manipulacji danymi oraz wizualizacji:

```text title="requirements.txt"
numpy==2.5.3
pandas==3.0.5
matplotlib==3.11.2
```

Można podać samą nazwę pakietu, maskę wersji głównej (np. `2.*` dla numpy, aby nie zainstalowała się przyszła wersja 3.x), wersję minimalną, jak i maksymalną. Ilustruje to poniższy przykład:

```text title="requirements.txt"
numpy==2.*
pandas>=3.0.0,<4.0.0
matplotlib>=3.10.0
scipy          # dowolna wersja
```

Instalacja pakietów z pliku wymagań:

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

Można dodać opcję aktualizacji (`-U` lub `--upgrade`).

!!! warning "Usuwanie pakietów według pliku wymagań"
    Następne polecenie usuwa z bieżącego środowiska wszystkie pakiety wymienione
    w pliku. Wykonujemy je wyłącznie w aktywnym środowisku venv projektu (sprawdzenie
    opisuje sekcja [Kontrola aktywnego środowiska](venv.md#kontrola-aktywnego-srodowiska));
    poza nim usunęłoby pakiety globalnej instalacji interpretera, z których mogą
    korzystać inne programy.

Odinstalowanie pakietów wymienionych w pliku:

```powershell title="Terminal"
python -m pip uninstall -r requirements.txt
```

Przed usunięciem każdego pakietu pip wypisuje jego pliki i pyta o zgodę (`Proceed (Y/n)?`; samo ++enter++ oznacza zgodę). Opcja `-y` pomija te pytania; przy usuwaniu jej nie dodajemy.

!!! info "Więcej szczegółowych informacji"
    [What Is Pip? A Guide for New Pythonistas](https://realpython.com/what-is-pip/)

## Rozwiązania alternatywne

Alternatywne rozwiązania dla pip to menedżer [Conda](https://conda.org/), najczęściej wykorzystywany wraz z pakietem [Anaconda](https://www.anaconda.com/), a także system [Poetry](https://python-poetry.org/).
