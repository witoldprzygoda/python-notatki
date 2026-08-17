# Instalacja klasyczna

Klasyczny instalator `python-3.x.x-amd64.exe`, pobierany dotychczas ze strony [python.org/downloads](https://www.python.org/downloads/), został wycofany na rzecz narzędzia **Python Install Manager**, które według oficjalnej dokumentacji CPythona stanowi obecnie zalecany sposób instalowania Pythona w systemie Windows.

!!! warning "Zmiana modelu instalacji"
    Klasyczny pełny instalator `.exe` został uznany za przestarzały (ang. *deprecated*)
    począwszy od Pythona 3.14 i nie będzie już publikowany dla Pythona 3.16 i wersji
    nowszych. Pełny opis nowego modelu instalacji zawiera oficjalna dokumentacja:
    [docs.python.org/3/using/windows.html](https://docs.python.org/3/using/windows.html)

## Nowy model instalacji

Nowy model składa się z **dwóch warstw** — managera oraz zarządzanych przez niego interpreterów, nazywanych środowiskami uruchomieniowymi (ang. *runtime*):

```{ .text .no-copy }
Python Install Manager
        │
        ├── Python 3.14
        ├── Python 3.14t
        ├── Python 3.15 ...
        └── inne środowiska uruchomieniowe
```

Manager **nie jest** interpreterem Pythona — jest narzędziem służącym do instalowania, wybierania, aktualizowania i usuwania interpreterów. Polecenie:

```powershell title="Terminal"
py install 3.14
```

instaluje interpreter w wersji 3.14, natomiast:

```powershell title="Terminal"
py install 3.14t
```

jego wariant *free-threaded*.

!!! note "Przyrostek „t" — wariant free-threaded"
    Przyrostek `t` oznacza oficjalną kompilację **free-threaded** — wariant interpretera
    pozbawiony globalnej blokady GIL (ang. *Global Interpreter Lock*), w którym wątki
    mogą być wykonywane w pełni równolegle. Prekompilowane wersje free-threaded dla
    systemu Windows są udostępniane pod tagami zakończonymi literą `t`.

Docelowa konfiguracja powinna przedstawiać się następująco:

```{ .text .no-copy }
python          → standardowy Python 3.14
py              → standardowy Python 3.14

py -V:3.14      → standardowy Python 3.14
py -V:3.14t     → free-threaded Python 3.14
```

## Instalacja managera

W przypadku komputera bez wcześniejszych instalacji Pythona Python Install Manager instalujemy ze strony [python.org/downloads](https://www.python.org/downloads/) albo ze sklepu Microsoft Store — obie wersje są identyczne. Po instalacji dostępne powinny być trzy polecenia:

```{ .text .no-copy }
python
py
pymanager
```

- `python` — uruchamia domyślny interpreter,
- `py` — działa analogicznie, ale dodatkowo pozwala wybierać wersje i zarządzać interpreterami,
- `pymanager` — jednoznaczna nazwa samego managera, przydatna zwłaszcza przy migracji ze starszego programu uruchomieniowego `py.exe`.

## Aliasy wykonywania aplikacji

Po instalacji należy sprawdzić ustawienia systemu Windows:

```{ .text .no-copy }
Start → Zarządzaj aliasami wykonywania aplikacji / Manage app execution aliases
```

Włączone powinny być pozycje:

```{ .text .no-copy }
Python (default)
    python.exe
    python3.exe

Python (default windowed)
    pythonw.exe

Python install manager
    py.exe
    pymanager.exe
    ...
```

!!! warning "Polecenie python otwiera Microsoft Store"
    Jeżeli polecenie `python` otwiera sklep Microsoft Store albo nie jest rozpoznawane,
    oficjalna dokumentacja zaleca sprawdzenie powyższych aliasów, a jeśli są już
    włączone — ich wyłączenie i ponowne włączenie. Zmienna `PATH` powinna ponadto
    zawierać katalog `%UserProfile%\AppData\Local\Microsoft\WindowsApps`. Po zmianie
    aliasów należy zamknąć terminal i otworzyć nowe okno programu PowerShell.

## Sprawdzenie managera

Przed zainstalowaniem interpretera warto zweryfikować działanie samego managera:

```powershell title="Terminal"
py help
```

oraz:

```powershell title="Terminal"
pymanager help
```

Na ekranie powinna pojawić się lista poleceń, m.in. `install`, `uninstall`, `list`, `exec`, `help`. Jeżeli żaden interpreter nie został jeszcze zainstalowany, polecenie:

```powershell title="Terminal"
py list
```

zwróci:

```{ .text .no-copy }
Tag  Name  Managed By  Version  Alias
-- No runtimes. Use 'py install <version>' to install one. --
```

!!! note "py list zamiast py -0p"
    Polecenie `py list` jest obecnie podstawowym sposobem przeglądania dostępnych
    interpreterów. Dawne `py -0p` zachowano wyłącznie dla zgodności z poprzednim
    programem uruchomieniowym.

## Weryfikacja pakietu przed instalacją

Przed instalacją warto sprawdzić, którą dokładnie wersję manager zamierza pobrać. Dla interpretera standardowego:

```powershell title="Terminal"
py list --online --one 3.14
```

Dla wariantu free-threaded:

```powershell title="Terminal"
py list --online --one 3.14t
```

Przykładowe wyniki:

```{ .text .no-copy }
Tag           Name           Managed By  Version
3.14[-64]     Python 3.14.7  PythonCore  3.14.7
```

```{ .text .no-copy }
Tag            Name                           Managed By  Version
3.14t[-64]     Python 3.14.7 (free-threaded)  PythonCore  3.14.7
```

Polecenie to jest szczególnie użyteczne, ponieważ wypisany w ten sposób pakiet jest dokładnie tym, który zostanie wybrany przez polecenie `py install 3.14`.

## Instalacja interpreterów

Instalację wykonujemy w zwykłym oknie PowerShell — uprawnienia administratora nie są wymagane:

```powershell title="Terminal"
py install 3.14 3.14t
```

Manager pobierze i zainstaluje oba warianty:

```{ .text .no-copy }
Installing Python 3.14.7.
...
Installing Python 3.14.7 (free-threaded).
...
```

Polecenie `py install` przyjmuje jeden lub wiele tagów jednocześnie.

## Kontrola po instalacji

```powershell title="Terminal"
py list
```

Oczekiwany wynik:

```{ .text .no-copy }
Tag            Name                           Managed By  Version
3.14[-64]   *  Python 3.14.7                  PythonCore  3.14.7
3.14t[-64]     Python 3.14.7 (free-threaded)  PythonCore  3.14.7
```

Gwiazdka `*` oznacza **interpreter domyślny**. Domyślnym interpreterem powinien być wariant standardowy 3.14, a nie 3.14t. Manager domyślnie wybiera najnowszą stabilną wersję, chyba że konfiguracja stanowi inaczej — domyślny tag można ustawić opcją konfiguracyjną `default_tag` lub zmienną środowiskową `PYTHON_MANAGER_DEFAULT`.

## Jawne wskazywanie wersji

Składnia `py -V:<TAG>` stanowi oficjalny sposób wskazania konkretnego interpretera. Wariant standardowy:

```powershell title="Terminal"
py -V:3.14 --version
```

```{ .text .no-copy }
Python 3.14.7
```

Wariant free-threaded:

```powershell title="Terminal"
py -V:3.14t --version
```

```{ .text .no-copy }
Python 3.14.7
```

Sama opcja `--version` nie ujawnia zatem różnicy między kompilacjami — służy do tego test opisany poniżej.

## Lokalizacja interpreterów

Wiarygodnym testem diagnostycznym jest odczytanie z interpretera ścieżki, pod którą został zainstalowany:

```powershell title="Terminal"
py -V:3.14 -c "import sys; print(sys.executable)"
```

```{ .text .no-copy }
C:\Users\wit\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

Analogicznie dla wariantu free-threaded:

```powershell title="Terminal"
py -V:3.14t -c "import sys; print(sys.executable)"
```

```{ .text .no-copy }
C:\Users\wit\AppData\Local\Python\pythoncore-3.14t-64\python3.14t.exe
```

Widoczna jest tu istotna zmiana względem poprzedniego instalatora. Dawniej typową lokalizacją było:

```{ .text .no-copy }
C:\Users\...\AppData\Local\Programs\Python\Python314\
```

natomiast interpretery zarządzane przez managera trafiają do jego własnego drzewa katalogów. Zamiast odgadywać ścieżkę instalacji, należy odczytać ją bezpośrednio z atrybutu `sys.executable`.

Pozostaje sprawdzenie domyślnego polecenia `python`:

```powershell title="Terminal"
python --version
python -c "import sys; print(sys.executable)"
```

```{ .text .no-copy }
Python 3.14.7
C:\Users\wit\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

Wynik potwierdza, że polecenie `python` uruchamia standardowy interpreter 3.14.7, a nie wariant 3.14t.

## Polecenie python a polecenie py

Polecenie `python` uruchamia interpreter właściwy dla bieżącego kontekstu — może to być aktywne środowisko wirtualne (venv), interpreter wymagany przez skrypt albo interpreter domyślny. Polecenie `py` działa analogicznie, ale pełni dodatkowo funkcję **selektora wersji**:

- `py -V:3.14` oznacza dokładnie standardowy interpreter 3.14,
- `py -V:3.14t` — dokładnie wariant free-threaded 3.14.

Przy pracy z wieloma wersjami dokumentacja zaleca stosowanie polecenia `py`.

## PATH — pierwsze znaczenie „ścieżki"

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

## sys.path — drugie znaczenie „ścieżki"

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

Stan bieżący sprawdzamy poleceniem `py list`, a dostępność nowszych wydań — znanym już poleceniem:

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
    globalnej instalacji — w tym pakiety doinstalowane globalnie poleceniem `pip`.
    Istniejące środowiska wirtualne powinny natomiast działać nadal. Jest to kolejny
    istotny argument za pracą w środowiskach venv (opis w podrozdziale
    [Wirtualne środowisko pracy venv](venv.md)).

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
8. **Manager jest oficjalnym kierunkiem rozwoju Pythona na Windows** — dokumentacja zaleca uzyskiwanie Pythona od zespołu CPython poprzez Install Manager; klasyczny instalator jest przestarzały od wersji 3.14 i nie będzie publikowany od wersji 3.16, a dawny *Python Launcher* również oznaczono jako przestarzały. Wybór pliku „Windows installer (64-bit)" jako pozornie najprostszej drogi oznacza dziś wybór modelu wygaszanego.

## Praca z interpreterem

Do linii poleceń interpretera wchodzimy poleceniem `python` lub `py` — pojawi się znak zachęty:

```{ .text .no-copy }
>>>
```

Interpreter opuszczamy funkcją `quit()` lub szybciej kombinacją ++ctrl+z++ (i ++enter++).
