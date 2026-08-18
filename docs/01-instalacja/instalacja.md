# Instalacja Pythona

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

!!! info "Wersja odniesienia notatek"
    Stanem odniesienia niniejszych notatek jest **Python 3.14** (najnowsze wydanie
    stabilne w chwili pisania: 3.14.7). Premiera Pythona 3.15 jest planowana na
    październik 2026 roku — po premierze świeża instalacja managera będzie
    domyślnie proponować wersję 3.15, natomiast przykłady w notatkach pozostają
    oparte na wersji 3.14.

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
Python 3.14.7
C:\Users\...\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

Wynik potwierdza, że polecenie `python` uruchamia standardowy interpreter 3.14.7, a nie wariant 3.14t.

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
