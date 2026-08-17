# Wirtualne środowisko pracy venv

Pracując z różnymi projektami, warto utworzyć dla nich izolowane środowisko. Python posiada wbudowane narzędzie **venv** do tworzenia wirtualnych środowisk, które pozwalają na izolowanie zależności projektu. Dzięki temu każda aplikacja może mieć swoje własne, oddzielne pakiety, co zapobiega konfliktom między różnymi wersjami bibliotek.

## Zalecany model pracy

Oficjalna dokumentacja Pythona dla systemu Windows zaleca tworzenie osobnego wirtualnego środowiska dla każdego projektu. Globalna instalacja pozostaje wówczas nienaruszona, a zależności poszczególnych projektów nie kolidują ze sobą:

```{ .text .no-copy }
globalny Python
        │
        ├── projekt A → .venv
        ├── projekt B → .venv
        └── projekt C → .venv
```

## Utworzenie środowiska

Środowisko tworzymy w katalogu projektu:

```powershell title="Terminal"
cd C:\projekty\moj-projekt
python -m venv .venv
```

Wersję interpretera można wskazać jawnie poleceniem `py` z Python Install Managera (opis w podrozdziale [Instalacja klasyczna](instalacja-klasyczna.md)):

```powershell title="Terminal"
py -V:3.14 -m venv .venv
```

Ostatni argument (`.venv`) to nazwa katalogu, który zostanie utworzony — może być dowolna, np. `venv` lub `nazwa_srodowiska`.

!!! tip "Popularna konwencja"
    Najczęściej stosowaną nazwą jest `.venv`. Katalog rozpoczynający się od kropki
    jest traktowany jako techniczny (w systemach uniksowych domyślnie ukryty),
    a środowiska o tej nazwie są automatycznie rozpoznawane m.in. przez Visual Studio Code.

## Aktywacja

Aby korzystać z wirtualnego środowiska, trzeba je aktywować. Kroki aktywacji różnią się w zależności od systemu operacyjnego.

=== "Windows (PowerShell)"

    ```powershell title="Terminal"
    .venv\Scripts\Activate.ps1
    ```

=== "Windows (Git Bash)"

    ```bash title="Terminal"
    source .venv/Scripts/activate
    ```

=== "Linux / macOS"

    ```bash title="Terminal"
    source .venv/bin/activate
    ```

Po aktywacji nazwa wirtualnego środowiska pojawia się przed znakiem zachęty, np. `(.venv)`. Oznacza to, że pracujemy w środowisku venv i wszystkie zainstalowane pakiety będą ograniczone tylko do tego środowiska.

## Kontrola aktywnego środowiska

Po aktywacji polecenie `python` powinno wskazywać interpreter ze środowiska, a nie z globalnej instalacji:

```powershell title="Terminal"
python --version
python -c "import sys; print(sys.executable)"
```

Wypisana ścieżka powinna prowadzić do wnętrza katalogu projektu:

```{ .text .no-copy }
C:\projekty\moj-projekt\.venv\Scripts\python.exe
```

## Instalowanie pakietów w środowisku

Przy aktywnym środowisku pakiety instalujemy poleceniem:

```powershell title="Terminal"
python -m pip install requests
```

Zainstalowane w ten sposób biblioteki trafiają wyłącznie do katalogu `.venv` i są dostępne tylko w tym środowisku. Zarządzanie pakietami opisuje szerzej podrozdział [Pip — zarządzanie pakietami](pip.md).

## Osobne środowisko dla wariantu free-threaded

Dla kompilacji free-threaded (opisanej w podrozdziale [Instalacja klasyczna](instalacja-klasyczna.md)) tworzymy odrębne środowisko, np. o nazwie `.venv-t`:

```powershell title="Terminal"
py -V:3.14t -m venv .venv-t
.venv-t\Scripts\Activate.ps1
```

Po aktywacji polecenie:

```powershell title="Terminal"
python -VV
```

potwierdza, że uruchamiany jest interpreter free-threaded ze środowiska `.venv-t`, a standardowe `python -m pip install ...` instaluje pakiety właśnie do niego. Takie rozwiązanie jest znacznie wygodniejsze niż każdorazowe wskazywanie wariantu w postaci `py -V:3.14t -m pip ...`.

## Dezaktywacja

Środowisko opuszczamy poleceniem:

```powershell title="Terminal"
deactivate
```

Po dezaktywacji polecenie `python` ponownie wskazuje globalną instalację, a pakiety ze środowiska nie są już dostępne.

venv jest łatwe w użyciu i bardzo przydatne, szczególnie podczas pracy nad wieloma projektami jednocześnie, aby uniknąć konfliktów między pakietami.

!!! info "Więcej szczegółowych informacji"
    [Python Virtual Environments: A Primer](https://realpython.com/python-virtual-environments-a-primer/)

## Venv w Visual Studio Code

Visual Studio Code pozwala na utworzenie wirtualnego środowiska przy okazji wyboru interpretera.

Po skrócie klawiszowym ++ctrl+shift+p++ wpisujemy **Python: Select Interpreter**. Pojawi się lista dostępnych interpreterów wraz z opcją utworzenia nowego środowiska:

![Lista wyboru interpretera w Visual Studio Code](img/vsc-select-interpreter.png)

Wybierzmy **Create Virtual Environment**, a następnie menedżera środowiska **venv**:

![Wybór menedżera środowiska w Visual Studio Code](img/vsc-environment-manager.png)

Po wskazaniu wersji interpretera zostanie lokalnie utworzony podkatalog `.venv` wraz z wirtualnym środowiskiem dla danego projektu:

```{ .text .no-copy }
moj-projekt/
├── .venv/
│   ├── Include/
│   ├── Lib/
│   │   └── site-packages/
│   ├── Scripts/
│   │   ├── Activate.ps1
│   │   ├── activate
│   │   ├── pip.exe
│   │   └── python.exe
│   └── pyvenv.cfg
└── main.py
```

!!! note "Wygląd a wersja VSC"
    Szczegóły wyglądu okien Visual Studio Code mogą się nieznacznie różnić między
    wersjami — stałe pozostają natomiast nazwy poleceń palety (**Python: Select
    Interpreter**, **Create Virtual Environment**) i to nimi należy się kierować.

## Automatyczna aktywacja środowiska

Ręczne aktywowanie środowiska przy każdym otwarciu terminala można zautomatyzować.

=== "Visual Studio Code"

    Po wskazaniu interpretera ze środowiska (opisane powyżej **Python: Select Interpreter**)
    VSC aktywuje `.venv` automatycznie w każdym nowo otwieranym terminalu zintegrowanym —
    dodatkowa konfiguracja nie jest potrzebna. Odpowiada za to domyślnie włączona opcja
    `python.terminal.activateEnvironment`.

=== "Windows (Git Bash)"

    W pliku `~/.bashrc` definiujemy funkcję zastępującą polecenie `cd`, która po zmianie
    katalogu aktywuje środowisko, jeżeli znajdzie w nim plik `.venv/Scripts/activate`:

    ```bash title="~/.bashrc"
    cd() {
        builtin cd "$@" || return
        if [ -f .venv/Scripts/activate ]; then
            source .venv/Scripts/activate
        fi
    }
    ```

    Zmiany zaczną obowiązywać w nowym terminalu (lub po wykonaniu `source ~/.bashrc`).

=== "Windows (PowerShell)"

    Analogiczną funkcję umieszczamy w profilu PowerShell. Plik profilu otwieramy poleceniem
    `notepad $PROFILE`; jeżeli nie istnieje, najpierw go tworzymy:

    ```powershell title="Terminal"
    New-Item -ItemType File -Force $PROFILE
    notepad $PROFILE
    ```

    Zawartość:

    ```powershell title="Profil PowerShell ($PROFILE)"
    Remove-Item Alias:cd -ErrorAction SilentlyContinue
    function cd {
        param($Path = $HOME)
        Set-Location $Path
        if (Test-Path .venv\Scripts\Activate.ps1) {
            .\.venv\Scripts\Activate.ps1
        }
    }
    ```

    Skrypt `Activate.ps1` wymaga zezwolenia na uruchamianie lokalnych skryptów —
    jednorazowo: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

!!! note "Ograniczenie"
    Powyższe funkcje aktywują środowisko przy wejściu do katalogu projektu, ale nie
    dezaktywują go automatycznie przy wyjściu — środowisko opuszczamy poleceniem
    `deactivate`.
