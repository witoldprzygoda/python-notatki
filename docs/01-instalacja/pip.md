# Pip — zarządzanie pakietami

W praktyce niemal zawsze istnieje konieczność doinstalowania pakietów. Służy do tego **pip** — oficjalny menedżer pakietów Pythona, który pozwala instalować, aktualizować oraz usuwać biblioteki. Pakiety pobierane są z Python Package Index ([PyPI](https://pypi.org/)), czyli największego repozytorium oprogramowania open source dla Pythona.

## Najważniejsza zasada: pip poprzez interpreter

Przy kilku zainstalowanych wersjach Pythona nie zaleca się używania samodzielnego polecenia:

```{ .text .no-copy }
pip install requests
```

ponieważ powstaje wówczas pytanie, który plik `pip.exe` został odnaleziony przez system Windows. Zamiast tego stosujemy formę `INTERPRETER -m pip`, która jednoznacznie wiąże polecenie z konkretnym interpreterem. Dla interpretera domyślnego:

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
    może usunąć globalnie doinstalowane pakiety (opis w podrozdziale
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
PS C:\> ipython
Python 3.14.7 (tags/v3.14.7, ...) [MSC v.1944 64 bit (AMD64)]
Type 'copyright', 'credits' or 'license' for more information
IPython 9.16.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: print("hello")
hello

In [2]:
```

Znaki zachęty `In [1]:`, `In [2]:` … pokazują wspomnianą numerację kolejnych poleceń. Powłokę opuszczamy poleceniem `exit`.

Python często informuje przy tej okazji, że sam pip ma nowszą wersję, i zachęca do aktualizacji — wykonujemy ją poleceniem:

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

Jeżeli instalacja pakietu ulegnie uszkodzeniu (zdarza się tak np. w wyniku ręcznych manipulacji zainstalowanymi wersjami Pythona), można wymusić jego ponowną instalację:

```powershell title="Terminal"
python -m pip install --force-reinstall requests
```

albo dodatkowo z pominięciem pamięci podręcznej (wymuszeniem ponownego pobrania pakietu):

```powershell title="Terminal"
python -m pip install --force-reinstall --no-cache-dir requests
```

!!! note "Zgodność pakietu z wersją interpretera"
    Pakiety z rozszerzeniami kompilowanymi (np. NumPy) publikują gotowe pliki binarne
    (ang. *wheel*) osobno dla każdej wersji interpretera. Starsze wydania pakietu mogą
    nie obsługiwać najnowszego Pythona — próba instalacji kończy się wtedy komunikatem
    o braku pasującej dystrybucji. Dostępność wersji dla używanego interpretera
    sprawdzamy poleceniem `python -m pip index versions <pakiet>`.

## Plik requirements.txt

Informację o zainstalowanych pakietach, sformatowaną pod kątem instalacji całej grupy, zwraca polecenie `python -m pip freeze`. Najczęściej wynik zapisuje się (przekierowując strumień standardowy) do pliku o nazwie `requirements.txt`:

```powershell title="Terminal"
python -m pip freeze > requirements.txt
```

Pisząc projekt wymagający określonych bibliotek, warto załączyć do niego taki plik wymagań. Przykładowo, podstawowy zestaw do obliczeń numerycznych, manipulacji danymi oraz wizualizacji:

```text title="requirements.txt"
numpy==2.5.2
pandas==3.0.3
matplotlib==3.11.1
```

Można podać samą nazwę pakietu, maskę wersji głównej (np. `2.*` dla numpy, aby nie zainstalowała się przyszła wersja 3.x), wersję minimalną, jak i maksymalną. Ilustruje to poniższy przykład:

```text title="requirements.txt"
numpy==2.*
pandas>=2.0.0,<3.0.0
matplotlib>=3.10.0
scipy          # dowolna wersja
```

Instalacja pakietów z pliku wymagań:

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

Można dodać opcję aktualizacji (`-U` lub `--upgrade`). Odinstalowanie pakietów wraz z domyślnym potwierdzeniem:

```powershell title="Terminal"
python -m pip uninstall -r requirements.txt -y
```

!!! info "Więcej szczegółowych informacji"
    [What Is Pip? A Guide for New Pythonistas](https://realpython.com/what-is-pip/)

## Rozwiązania alternatywne

Alternatywne rozwiązania dla pip to menedżer [Conda](https://conda.org/), najczęściej wykorzystywany wraz z pakietem [Anaconda](https://www.anaconda.com/), a także system [Poetry](https://python-poetry.org/).
