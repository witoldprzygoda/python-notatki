# Instalacja Pythona

Klasyczny instalator `python-3.x.x-amd64.exe`, pobierany dotychczas ze strony [python.org/downloads](https://www.python.org/downloads/), został uznany za przestarzały i jest wygaszany na rzecz narzędzia **Python Install Manager**, które według oficjalnej dokumentacji CPythona stanowi obecnie zalecany sposób instalowania Pythona w systemie Windows.

!!! warning "Zmiana modelu instalacji"
    Klasyczny pełny instalator `.exe` został uznany za przestarzały (ang. *deprecated*)
    począwszy od Pythona 3.14. Dla wersji 3.14 i 3.15 jest nadal publikowany, ale nie
    będzie już udostępniany dla Pythona 3.16 i wersji nowszych. Pełny opis nowego
    modelu instalacji zawiera oficjalna dokumentacja:
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

jego wariant free-threaded.

!!! note "Przyrostek „t” — wariant free-threaded"
    Przyrostek `t` oznacza oficjalną kompilację **free-threaded** („o swobodnych
    wątkach”) — wariant interpretera pozbawiony globalnej blokady GIL
    (ang. *Global Interpreter Lock*), w którym wątki mogą być wykonywane w pełni
    równolegle. Zmianę tę wprowadza dokument [PEP 703](https://peps.python.org/pep-0703/).
    Prekompilowane wersje free-threaded dla systemu Windows są udostępniane pod tagami
    zakończonymi literą `t`.

Docelowa konfiguracja powinna przedstawiać się następująco:

```{ .text .no-copy }
python          → standardowy Python 3.14
py              → standardowy Python 3.14

py -V:3.14      → standardowy Python 3.14
py -V:3.14t     → free-threaded Python 3.14
```

## Wersje i okresy wsparcia

Nowa wersja Pythona, oznaczana dwiema liczbami (np. 3.14), ukazuje się co roku w październiku. Wydania z trzecią liczbą (3.14.1, 3.14.2, …) są **wydaniami poprawkowymi**: nie wprowadzają nowych możliwości języka, lecz usuwają błędy i luki bezpieczeństwa, dlatego warto instalować je, gdy tylko staną się dostępne (aktualizację opisuje podrozdział [Ścieżki i utrzymanie interpreterów](sciezki-i-utrzymanie.md#aktualizacja-interpreterow)). Każda wersja przechodzi kolejne fazy wsparcia, które przedstawia wykres z przewodnika dla twórców Pythona (*Python Developer's Guide*), widoczny także na stronie [python.org/downloads](https://www.python.org/downloads/) w sekcji *Active Python Releases*:

![Wykres okresów wsparcia wersji Pythona od 2.7 do 3.16 na osi lat 2019–2032: wersje 2.7 i 3.7–3.10 mają czerwone paski zakończonego wsparcia, wersje 3.11–3.13 są w fazie poprawek bezpieczeństwa, 3.14 i 3.15 w fazie poprawek błędów, 3.16 w rozwoju; pionowa linia oznacza 9 października 2026 roku](img/python-cykl-wydan.svg){ width="760" }

Każdy pasek obejmuje pełny, planowany okres wsparcia wersji, a podpis przy nim podaje jej status w dniu wygenerowania wykresu:

- **rozwój** (ang. *feature*) — wersja w przygotowaniu, która przyjmuje jeszcze nowe możliwości; w tej fazie ukazują się wydania testowe alfa (na wykresie 3.16),
- **przed premierą** (ang. *prerelease*) — od pierwszego wydania beta, przypadającego w maju, do październikowej premiery: wydania testowe beta i kandydaci do wydania, już bez nowych możliwości (na wykresie żadna wersja nie jest w tej fazie),
- **poprawki błędów** (ang. *bugfix*, zielona część paska) — około dwóch lat od premiery (dla wersji starszych niż 3.13 — półtora roku); mniej więcej co dwa miesiące ukazuje się wydanie poprawkowe z gotowymi instalatorami (3.14 i 3.15),
- **poprawki bezpieczeństwa** (ang. *security*, żółta część paska) — do pięciu lat od premiery wyłącznie poprawki bezpieczeństwa, publikowane jako kod źródłowy, bez nowych instalatorów (3.11–3.13),
- **koniec wsparcia** (ang. *end-of-life*, czerwony pasek) — wersja nie otrzymuje już żadnych poprawek (3.10 i starsze; wsparcie wersji 3.10 zakończyło się 1 października 2026 roku).

Pionowa linia wskazuje dzień, w którym przewodnik wygenerował wykres (9 października 2026 roku, dzień premiery Pythona 3.15). Bieżącą wersję wykresu oraz tabelę dat premier i końca wsparcia zawiera strona [devguide.python.org/versions](https://devguide.python.org/versions/); przewodnik udostępniono na licencji CC0, więc wykres można swobodnie powielać.

!!! info "Wersja odniesienia notatek"
    Stanem odniesienia niniejszych notatek jest **Python 3.14**; przykłady sprawdzono
    na wydaniu poprawkowym 3.14.8 z 30 września 2026 roku. Gdy wersji nie wskażemy,
    manager instaluje najnowszą wersję stabilną (stan na 11 października 2026 roku:
    Python 3.15.0 z 9 października 2026 roku), dlatego w poleceniach instalacyjnych
    podajemy wersję 3.14 jawnie.

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

!!! warning "Wersja instalowana bez wskazania"
    Dopóki nie zainstalowano żadnego interpretera, polecenie uruchamiające Pythona —
    `python` albo `py` bez polecenia managera, np. `py -c "..."` — nie kończy się
    błędem, lecz samoczynnie, bez pytania, instaluje najnowszą wersję stabilną, a nie
    wersję 3.14, na której opiera się książka. Przed instalacją interpretera
    korzystamy więc wyłącznie z poleceń managera opisanych dalej (`py help`,
    `py list`, `py install`).

    Pierwsze uruchomienie aplikacji Python Install Manager, na przykład z menu Start,
    otwiera kreator konfiguracji (ang. *configuration checker*), który można też
    wywołać ponownie poleceniem `py install --configure`. Kreator najpierw proponuje
    zmiany ustawień systemu; te pytania kończą się znacznikiem `[y/N]`, czyli
    odpowiedzią domyślną jest „nie”. Gdy brakuje najnowszej wersji Pythona, kreator
    zadaje na końcu pytanie `Install CPython now? [Y/n]`. Na to pytanie odpowiadamy
    `n`, ponieważ odpowiedź domyślna, wybierana samym klawiszem ++enter++,
    zainstalowałaby najnowszą wersję stabilną; wersję 3.14 instalujemy jawnie, jak
    opisują dalsze sekcje. Gdyby
    najnowsza wersja została już zainstalowana, pozostanie interpreterem domyślnym —
    wersję 3.14 wskazujemy wtedy jawnie poleceniem `py -V:3.14`, także przy
    tworzeniu środowiska wirtualnego (podrozdział
    [Wirtualne środowisko venv](venv.md#utworzenie-srodowiska)).

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
    zawierać katalog `%UserProfile%\AppData\Local\Microsoft\WindowsApps`. Zapis
    `%UserProfile%` oznacza wartość zmiennej środowiskowej `UserProfile`; w tej postaci
    ścieżki zapisują dokumentacja Pythona i okno edycji zmiennych środowiskowych systemu
    Windows. Program PowerShell nie rozwija takiego zapisu — tę samą wartość zwraca
    w nim wyrażenie `$env:USERPROFILE` (podobnie `%LocalAppData%` odpowiada
    `$env:LOCALAPPDATA`). Po zmianie aliasów należy zamknąć terminal i otworzyć nowe
    okno programu PowerShell.

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
Tag     Name  Managed By  Version  Alias
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
Tag           Name           Managed By  Version  Alias
3.14[-64]     Python 3.14.8  PythonCore  3.14.8   python3[-64].exe, python3.14[-64].exe
```

```{ .text .no-copy }
Tag            Name                           Managed By  Version  Alias
3.14t[-64]     Python 3.14.8 (free-threaded)  PythonCore  3.14.8   python3.14t[-64].exe, python3t[-64].exe
```

Polecenie to jest szczególnie użyteczne, ponieważ wypisany w ten sposób pakiet jest dokładnie tym, który zostanie wybrany przez polecenie `py install 3.14`.

## Instalacja interpreterów

Instalację wykonujemy w zwykłym oknie PowerShell — uprawnienia administratora nie są wymagane:

```powershell title="Terminal"
py install 3.14 3.14t
```

Manager pobierze i zainstaluje oba warianty:

```{ .text .no-copy }
The signature for https://www.python.org/ftp/python/index-windows.json was successfully verified.
Installing Python 3.14.8.
...
Installing Python 3.14.8 (free-threaded).
...

Global shortcuts directory is not on PATH. Add it for easy access to global Python aliases.
Directory to add: C:\Users\...\AppData\Local\Python\bin
```

Polecenie `py install` przyjmuje jeden lub wiele tagów jednocześnie. Pierwszy wiersz wyniku potwierdza poprawność podpisu cyfrowego pobranego indeksu dostępnych wersji. Końcowy komunikat dotyczy katalogu `%LocalAppData%\Python\bin`, w którym manager umieszcza globalne aliasy interpreterów wymienione w kolumnie `Alias` (np. `python3.14.exe`); dodanie tego katalogu do zmiennej `PATH` jest opcjonalne, co wyjaśnia ramka w podrozdziale [Ścieżki i utrzymanie interpreterów](sciezki-i-utrzymanie.md#path-pierwsze-znaczenie-sciezki).

## Kontrola po instalacji

```powershell title="Terminal"
py list
```

Oczekiwany wynik:

```{ .text .no-copy }
Tag            Name                           Managed By  Version  Alias
3.14[-64]   *  Python 3.14.8                  PythonCore  3.14.8   python3[-64].exe, python3.14[-64].exe
3.14t[-64]     Python 3.14.8 (free-threaded)  PythonCore  3.14.8   python3.14t[-64].exe, python3t[-64].exe
```

Gwiazdka `*` oznacza **interpreter domyślny**. Domyślnym interpreterem powinien być wariant standardowy 3.14, a nie 3.14t. Spośród zainstalowanych interpreterów manager domyślnie wybiera najnowszą wersję stabilną, chyba że konfiguracja stanowi inaczej — domyślny tag można ustawić opcją konfiguracyjną `default_tag` lub zmienną środowiskową `PYTHON_MANAGER_DEFAULT`.

## Jawne wskazywanie wersji

Składnia `py -V:<TAG>` stanowi oficjalny sposób wskazania konkretnego interpretera. Wariant standardowy:

```powershell title="Terminal"
py -V:3.14 --version
```

```{ .text .no-copy }
Python 3.14.8
```

Wariant free-threaded:

```powershell title="Terminal"
py -V:3.14t --version
```

```{ .text .no-copy }
Python 3.14.8
```

Sama opcja `--version` nie ujawnia zatem różnicy między kompilacjami — służy do tego test opisany poniżej.

## Lokalizacja interpreterów

Wiarygodnym testem diagnostycznym jest odczytanie z interpretera ścieżki, pod którą został zainstalowany:

```powershell title="Terminal"
py -V:3.14 -c "import sys; print(sys.executable)"
```

```{ .text .no-copy }
C:\Users\...\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

Analogicznie dla wariantu free-threaded:

```powershell title="Terminal"
py -V:3.14t -c "import sys; print(sys.executable)"
```

```{ .text .no-copy }
C:\Users\...\AppData\Local\Python\pythoncore-3.14t-64\python3.14t.exe
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
Python 3.14.8
C:\Users\...\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

Wynik potwierdza, że polecenie `python` uruchamia standardowy interpreter 3.14.8, a nie wariant 3.14t.

## Polecenie python a polecenie py

Polecenie `python` uruchamia interpreter właściwy dla bieżącego kontekstu — może to być aktywne środowisko wirtualne (venv), interpreter wymagany przez skrypt albo interpreter domyślny. Polecenie `py` działa analogicznie, ale pełni dodatkowo funkcję **selektora wersji**:

- `py -V:3.14` oznacza dokładnie standardowy interpreter 3.14,
- `py -V:3.14t` — dokładnie wariant free-threaded 3.14.

Przy pracy z wieloma wersjami dokumentacja zaleca stosowanie polecenia `py`.

## Pierwsze uruchomienie interpretera

Na zakończenie instalacji warto wykonać prosty test: poleceniem `python` (lub `py`) wchodzimy do konsoli interpretera — pojawi się znak zachęty:

```{ .text .no-copy }
>>>
```

Interpreter opuszczamy poleceniem `exit` (od Pythona 3.13 bez nawiasów) lub kombinacją ++ctrl+z++ (i ++enter++). Jeżeli oba kroki działają, instalacja jest kompletna. Pracę w konsoli interpretera omawia szczegółowo rozdział [2. Konsola](../02-konsola/index.md).

Diagnostykę ścieżek systemowych oraz aktualizowanie i usuwanie interpreterów opisuje podrozdział [Ścieżki i utrzymanie interpreterów](sciezki-i-utrzymanie.md).
