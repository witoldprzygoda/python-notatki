# Ścieżki i utrzymanie interpreterów

Podrozdział [Instalacja Pythona](instalacja.md) opisuje czynności instalacyjne, wykonywane zazwyczaj jednorazowo. Niniejszy podrozdział gromadzi zagadnienia, do których wraca się w trakcie dalszej pracy: diagnostykę ścieżek systemowych oraz aktualizowanie i usuwanie interpreterów.

## PATH — pierwsze znaczenie „ścieżki”

Systemowa zmienna `PATH` odpowiada na pytanie, który program `.exe` zostanie uruchomiony po wpisaniu danej nazwy. Sprawdzenie:

```powershell title="Terminal"
where.exe python
where.exe py
where.exe pymanager
```

lub dokładniej, w programie PowerShell:

```powershell title="Terminal"
Get-Command python -All
Get-Command py -All
Get-Command pymanager -All
```

W przypadku Python Install Managera wypisane ścieżki mogą wskazywać na katalog `...\AppData\Local\Microsoft\WindowsApps\...`. Jest to zachowanie prawidłowe — `python` może być globalnym aliasem systemu Windows, a nie bezpośrednio właściwym plikiem `python.exe`; dokumentacja wskazuje katalog *WindowsApps* jako miejsce, przez które udostępniane są polecenia managera.

Polecenia `where.exe python` oraz `python -c "import sys; print(sys.executable)"` odpowiadają zatem na dwa różne pytania:

- pierwsze — który program system Windows uruchamia jako polecenie `python`,
- drugie — który interpreter faktycznie wykonuje kod.

W diagnostyce instalacji Pythona istotniejsza jest zazwyczaj odpowiedź na pytanie drugie.

!!! note "Katalog %LocalAppData%\\Python\\bin"
    Manager może zaproponować dodanie katalogu `%LocalAppData%\Python\bin` do zmiennej
    `PATH`. Krok ten jest **opcjonalny** przy korzystaniu z polecenia `py` — udostępnia
    pełniejszy zestaw globalnych aliasów, takich jak `python3.14` czy `python3.14t`.
    Nie należy natomiast ręcznie dodawać do `PATH` katalogów samych interpreterów
    (`...\pythoncore-3.14-64\` itd.) — ich obsługą zajmuje się manager.

## sys.path — drugie znaczenie „ścieżki”

Systemowa zmienna `PATH` określa, **który program** zostanie uruchomiony. Pythonowa lista `sys.path` określa natomiast, **w których katalogach** interpreter poszukuje modułów podczas wykonywania instrukcji `import`. Sprawdzenie:

```powershell title="Terminal"
python -c "import sys; print(*sys.path, sep='\n')"
```

lub dla wskazanych interpreterów:

```powershell title="Terminal"
py -V:3.14 -c "import sys; print(*sys.path, sep='\n')"
py -V:3.14t -c "import sys; print(*sys.path, sep='\n')"
```

Każdy interpreter dysponuje własnym środowiskiem importów. Pełniejszy raport, obejmujący katalogi *site-packages*, zwraca polecenie:

```powershell title="Terminal"
py -V:3.14 -m site
py -V:3.14t -m site
```

## Aktualizacja interpreterów

Stan bieżący sprawdzamy poleceniem `py list`, a dostępność nowszych wydań — poleceniem `py list --online --one` (opisanym w podrozdziale [Instalacja Pythona](instalacja.md)):

```powershell title="Terminal"
py list --online --one 3.14
py list --online --one 3.14t
```

Aktualizację wybranych interpreterów wykonujemy poleceniem:

```powershell title="Terminal"
py install --update 3.14 3.14t
```

a wszystkich zarządzanych przez managera — bez wskazywania tagów:

```powershell title="Terminal"
py install --update
```

Manager zastąpi interpreter nowszą wersją, o ile jest ona dostępna.

!!! warning "Aktualizacja a modyfikacje globalnej instalacji"
    Aktualizacja interpretera może usunąć modyfikacje dokonane bezpośrednio w jego
    globalnej instalacji — w tym pakiety doinstalowane globalnie poleceniem
    `python -m pip`. Istniejące środowiska wirtualne powinny natomiast działać nadal.
    Jest to kolejny istotny argument za pracą w środowiskach venv (opis w podrozdziale
    [Wirtualne środowisko venv](venv.md)).

## Usuwanie interpreterów

Wskazany interpreter usuwamy poleceniem:

```powershell title="Terminal"
py uninstall 3.14
```

analogicznie wariant free-threaded:

```powershell title="Terminal"
py uninstall 3.14t
```

Wszystkie interpretery zarządzane przez managera, wraz z ich wpisami rejestracyjnymi i pamięcią podręczną, usuwa polecenie:

```powershell title="Terminal"
py uninstall --purge
```

Opcja `--purge` nie obejmuje interpreterów, których manager sam nie instalował — instalacje wykonane innymi metodami pozostają nietknięte.

## Zalety nowego modelu instalacji

Na zakończenie warto podsumować, dlaczego Python Install Manager stanowi lepsze rozwiązanie niż klasyczny instalator. W starym modelu każda wersja była instalowana osobnym plikiem `.exe`, a odpowiedzialność za porządek spoczywała na użytkowniku:

```{ .text .no-copy }
python-3.13.x-amd64.exe → instalacja → wpis w PATH
python-3.14.x-amd64.exe → instalacja → kolejny wpis w PATH
        ↓
która wersja jest domyślna?
który pip.exe został właśnie uruchomiony?
```

Model ten łatwo prowadził do niespójności. Rozważmy hipotetyczny — a w praktyce częsty — przypadek: po kilku latach instalowania kolejnych wersji polecenie `python` uruchamia interpreter 3.13, polecenie `py` — wariant 3.14t, a w rejestrze systemu pozostają wpisy po czterech dawno usuniętych instalacjach. Diagnoza takiego stanu wymaga ręcznego przeglądania zmiennej `PATH` i rejestru.

Nowy model porządkuje cały cykl życia interpreterów w jednym narzędziu:

```{ .text .no-copy }
Python Install Manager
        │
        ├── py list               (przegląd)
        ├── py install            (instalacja)
        ├── py install --update   (aktualizacja)
        └── py uninstall          (usunięcie)
```

Najważniejsze zalety:

1. **Jedno narzędzie obsługuje cały cykl życia interpretera** — instalację (`py install 3.14`), aktualizację (`py install --update 3.14`), usunięcie (`py uninstall 3.14`) i przegląd (`py list`).
2. **Wiele wersji przestaje być problemem zmiennej PATH** — zamiast ręcznego dodawania katalogów `Python313`, `Python313\Scripts`, `Python314`… i pilnowania ich kolejności, wersję wskazujemy jednoznacznie: `py -V:3.14` lub `py -V:3.14t`.
3. **Wariant free-threaded jest zwykłym interpreterem** — nie wymaga specjalnych opcji instalatora; wystarczy `py install 3.14t`, a następnie `py -V:3.14t`.
4. **Wersję można sprawdzić przed instalacją** — polecenie `py list --online --one 3.14` pokazuje dokładnie ten pakiet, który zostanie wybrany przez `py install 3.14`; jest to szczególnie wygodne przy aktualizacjach.
5. **Manager aktualizuje się samodzielnie** — niezależnie od interpreterów. Komunikat w rodzaju `Python install manager was successfully updated to 26.3.` nie oznacza aktualizacji samego Pythona; interpretery aktualizujemy w sposób kontrolowany poleceniem `py install --update`.
6. **Łatwiejsza diagnostyka stanu systemu** — warianty polecenia `py list` (`--only-managed`, `--format=json`, `--format=prefix`, `--online`) odpowiadają na pytania: co jest zainstalowane, co jest zarządzane przez managera, co pochodzi z zewnątrz, gdzie się znajduje i co można zainstalować.
7. **Instalacje zarządzane mają pierwszeństwo** — manager rozróżnia własne interpretery od zainstalowanych innymi metodami i preferuje zarządzane, co zapewnia przewidywalne zachowanie podczas migracji.
8. **Manager jest oficjalnym kierunkiem rozwoju Pythona na Windows** — dokumentacja zaleca uzyskiwanie Pythona od zespołu CPython poprzez Install Manager; klasyczny instalator jest przestarzały od wersji 3.14 i nie będzie publikowany od wersji 3.16, a dawny *Python Launcher* również oznaczono jako przestarzały. Wybór pliku „Windows installer (64-bit)” jako pozornie najprostszej drogi oznacza dziś wybór modelu wygaszanego.
