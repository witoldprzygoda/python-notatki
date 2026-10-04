# Wirtualne środowisko venv

Pracując z różnymi projektami, warto utworzyć dla nich izolowane środowisko. Python posiada wbudowane narzędzie **venv** do tworzenia wirtualnych środowisk, które pozwalają na izolowanie zależności projektu. Dzięki temu każda aplikacja może mieć swoje własne, oddzielne pakiety, co zapobiega konfliktom między różnymi wersjami bibliotek — jest to szczególnie istotne podczas równoległej pracy nad wieloma projektami.

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

Środowisko tworzymy w katalogu projektu (tu `C:\projekty\moj-projekt`; katalog zakładamy wcześniej, np. w Eksploratorze plików). Polecenie `python -m venv` wykonane w katalogu, który zawiera już środowisko o tej nazwie, nie zgłasza błędu, lecz przestawia to środowisko na bieżący interpreter, przez co pakiety zainstalowane dla innej wersji Pythona mogą przestać działać. Dlatego środowisko tworzymy tylko wtedy, gdy katalogu `.venv` jeszcze nie ma — istniejące wystarczy aktywować:

```powershell title="Terminal"
cd C:\projekty\moj-projekt
if (-not (Test-Path .venv)) { python -m venv .venv }
```

Wersję interpretera można wskazać jawnie poleceniem `py` z Python Install Managera (opis w podrozdziale [Instalacja Pythona](instalacja.md)):

```powershell title="Terminal"
if (-not (Test-Path .venv)) { py -V:3.14 -m venv .venv }
```

Ostatni argument polecenia `venv` (`.venv`) to nazwa katalogu, który zostanie utworzony — może być dowolna, np. `venv` lub `nazwa_srodowiska`; tę samą nazwę podajemy wtedy w warunku `Test-Path`.

!!! tip "Popularna konwencja"
    Najczęściej stosowaną nazwą jest `.venv`. Katalog rozpoczynający się od kropki
    jest traktowany jako techniczny (w systemach uniksowych domyślnie ukryty),
    a środowiska o tej nazwie są automatycznie rozpoznawane m.in. przez Visual Studio Code.

Utworzony katalog zawiera m.in. kopię plików uruchomieniowych interpretera oraz skrypty aktywacyjne:

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

## Aktywacja

Aby korzystać z wirtualnego środowiska, trzeba je aktywować. Kroki aktywacji różnią się w zależności od systemu operacyjnego.

=== "Windows (PowerShell)"

    ```powershell title="Terminal"
    .venv\Scripts\Activate.ps1
    ```

    Jeżeli PowerShell odmawia uruchomienia skryptu `Activate.ps1`, ponieważ uruchamianie
    skryptów jest zablokowane (polecenie `Get-ExecutionPolicy` wypisuje wtedy `Restricted`,
    a bieżące ustawienia pokazuje polecenie `Get-ExecutionPolicy -List`), zezwalamy na nie
    jednorazowo poleceniem `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

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

Dla kompilacji free-threaded (opisanej w podrozdziale [Instalacja Pythona](instalacja.md)) tworzymy odrębne środowisko, np. o nazwie `.venv-t`:

```powershell title="Terminal"
if (-not (Test-Path .venv-t)) { py -V:3.14t -m venv .venv-t }
.venv-t\Scripts\Activate.ps1
```

Po aktywacji polecenie:

```powershell title="Terminal"
python -VV
```

(opcja `-VV` wypisuje rozszerzoną informację o wersji, obejmującą także rodzaj kompilacji) potwierdza, że uruchamiany jest interpreter free-threaded ze środowiska `.venv-t`, a standardowe `python -m pip install ...` instaluje pakiety właśnie do niego. Takie rozwiązanie jest znacznie wygodniejsze niż każdorazowe wskazywanie wariantu w postaci `py -V:3.14t -m pip ...`.

## Dezaktywacja

Środowisko opuszczamy poleceniem:

```powershell title="Terminal"
deactivate
```

Po dezaktywacji polecenie `python` ponownie wskazuje globalną instalację, a pakiety ze środowiska nie są już dostępne.

!!! info "Więcej szczegółowych informacji"
    [Python Virtual Environments: A Primer](https://realpython.com/python-virtual-environments-a-primer/)

## Integracja z Visual Studio Code

Visual Studio Code potrafi tworzyć środowiska venv i automatycznie je aktywować w terminalu zintegrowanym — opis tej integracji zawiera podrozdział [Konfigurowanie narzędzi](konfiguracja.md), poświęcony przygotowaniu edytora.

## Automatyczna aktywacja środowiska w terminalu

Ręczne aktywowanie środowiska przy każdym otwarciu terminala można zautomatyzować.

=== "Windows (Git Bash)"

    Na końcu pliku `~/.bashrc` (jeżeli go nie ma, tworzymy nowy) dopisujemy funkcję
    zastępującą polecenie `cd`, która po zmianie katalogu aktywuje środowisko, jeżeli
    znajdzie w nim plik `.venv/Scripts/activate`; dotychczasowa treść pliku pozostaje
    bez zmian:

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

    Analogiczną funkcję umieszczamy w profilu PowerShell, czyli skrypcie wykonywanym przy
    każdym uruchomieniu powłoki. Plik profilu otwieramy poleceniem `notepad $PROFILE`.
    Pierwsze z poniższych poleceń tworzy go tylko wtedy, gdy jeszcze nie istnieje (opcja
    `-Force` zakłada przy tym brakujący katalog), dzięki czemu istniejący profil pozostaje
    nienaruszony:

    ```powershell title="Terminal"
    if (-not (Test-Path $PROFILE)) { New-Item -ItemType File -Force $PROFILE }
    notepad $PROFILE
    ```

    Windows PowerShell 5.1, wbudowany w system, i PowerShell 7 korzystają z osobnych plików
    profilu (ścieżkę profilu bieżącej powłoki wypisuje polecenie `$PROFILE`), dlatego
    funkcję umieszczamy w profilu tej powłoki, z której korzystamy. Na końcu pliku
    dopisujemy:

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

    Profil, podobnie jak skrypt `Activate.ps1`, wymaga zezwolenia na uruchamianie
    lokalnych skryptów; postępowanie przy zablokowanych skryptach opisuje sekcja
    [Aktywacja](#aktywacja).

W środowisku Visual Studio Code analogiczną automatyzację zapewnia sam edytor (opis w podrozdziale [Konfigurowanie narzędzi](konfiguracja.md)).

!!! note "Ograniczenie"
    Powyższe funkcje aktywują środowisko przy wejściu do katalogu projektu, ale nie
    dezaktywują go automatycznie przy wyjściu — środowisko opuszczamy poleceniem
    `deactivate`.
