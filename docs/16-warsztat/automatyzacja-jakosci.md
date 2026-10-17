# Automatyzacja jakości — pre-commit i CI

Testy, sprawdzacz typów i Ruff przynoszą korzyść tylko wtedy, gdy są uruchamiane zawsze — nie wtedy, gdy ktoś o nich pamięta. W tym podrozdziale ustawiamy je w dwóch miejscach: przed zapisaniem zmian w repozytorium, na komputerze programisty, oraz na serwerze po każdym wysłaniu kodu. Zakładamy, że projekt jest w repozytorium Git; sam Git opisuje jego dokumentacja (git-scm.com/doc).

## Zasada: te same sprawdzenia lokalnie i na serwerze

Konfigurację narzędzi przechowujemy w `pyproject.toml` — sekcje z poprzednich podrozdziałów — a listę narzędzi deweloperskich trzymamy w osobnym pliku wymagań z rozdziału 1. Pliki pokazane w tym podrozdziale tworzymy, jeżeli projekt ich jeszcze nie ma; plik, który już istnieje — także plik `.github/workflows/ci.yml` — uzupełniamy o brakujące wpisy, zamiast zastępować jego treść:

```text title="requirements-dev.txt"
pytest==9.1.1
pytest-cov==7.1.0
mypy==2.3.1
ruff==0.16.7
pre-commit==4.6.2
```

Dzięki temu programista, hook pre-commit i serwer CI uruchamiają te same wersje z tą samą konfiguracją, a wynik „u mnie działa” przestaje zależeć od komputera.

## pre-commit

**pre-commit** to program, który rejestruje w repozytorium **hook** (ang. *hook*) — skrypt uruchamiany przez Git tuż przed utworzeniem commitu. Jeśli którekolwiek sprawdzenie nie przejdzie, commit nie powstaje. Konfigurację zapisujemy w pliku YAML w katalogu głównym projektu:

```yaml title=".pre-commit-config.yaml"
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.7
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
```

!!! warning "Hooki zmieniają pliki projektu"
    Hooki `ruff-check` z opcją `--fix` i `ruff-format` nie tylko sprawdzają pliki,
    lecz od razu je poprawiają, a polecenie `pre-commit run --all-files` obejmuje
    wszystkie pliki śledzone w repozytorium, także te z niezatwierdzonymi zmianami.
    Uruchamiamy je więc po zatwierdzeniu bieżącej pracy — `git status` nie pokazuje
    wtedy zmienionych plików — a poprawki narzędzi przeglądamy poleceniem `git diff`,
    zanim je zatwierdzimy.

!!! warning "Hook trafia do repozytorium katalogu bieżącego"
    Polecenia pre-commit działają w repozytorium, do którego należy katalog
    bieżący, także wtedy, gdy jest on podkatalogiem innego repozytorium:
    `pre-commit install` zapisałby wówczas hook w repozytorium nadrzędnym,
    a `pre-commit run --all-files` sprawdzałby i poprawiał pliki Pythona całego
    tamtego repozytorium. Repozytorium projektu tworzymy więc w katalogu
    przykładów poleceniem `git init`, a przed instalacją hooka sprawdzamy,
    że polecenie `git rev-parse --show-toplevel` wypisuje ścieżkę tego katalogu.
    Hook `pre-commit`, który repozytorium już ma, narzędzie zachowuje pod nazwą
    `pre-commit.legacy`, a polecenie `pre-commit uninstall` usuwa hook narzędzia
    i przywraca poprzedni.

pre-commit instalujemy w środowisku projektu z pliku wymagań, w wersji w nim przypiętej:

```powershell title="Terminal"
python -m pip install -r requirements-dev.txt
```

Następnie sprawdzamy katalog główny repozytorium, instalujemy hook i uruchamiamy sprawdzenia na wszystkich plikach:

```powershell title="Terminal"
git rev-parse --show-toplevel
pre-commit install
pre-commit run --all-files
```

```{ .text .no-copy }
C:/.../projekt
pre-commit installed at .git\hooks\pre-commit
[INFO] Initializing environment for https://github.com/astral-sh/ruff-pre-commit.
[INFO] Installing environment for https://github.com/astral-sh/ruff-pre-commit.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
ruff check...............................................................Passed
ruff format..............................................................Passed
```

Wpis `repo` wskazuje repozytorium z definicją hooków, `rev` — jego wersję (odpowiadającą wersji Ruff), a `hooks` — które z nich włączamy; hook `ruff-check` z argumentem `--fix` poprzedza `ruff-format`, bo poprawki lintera mogą wymagać ponownego sformatowania. Przy pierwszym uruchomieniu pre-commit pobiera narzędzia do własnego, odizolowanego środowiska — o tym informują wiersze `[INFO]` — więc nie muszą być zainstalowane w venv projektu; kolejne uruchomienia korzystają z gotowego środowiska i wypisują tylko wyniki hooków. W repozytorium bez plików Pythona hooki zgłaszają zamiast `Passed` wynik `(no files to check)Skipped`. Polecenie `run --all-files` sprawdza cały projekt; od tej chwili każdy commit sprawdza tylko pliki dodane do niego poleceniem `git add`. Tak wygląda commit pliku, który łamie reguły:

```python title="zly.py"
import os

x=1
print( x )
```

```powershell title="Terminal"
git add zly.py
git commit -m "Dodaj zly.py"
```

```{ .text .no-copy }
ruff check...............................................................Failed
- hook id: ruff-check
- files were modified by this hook

Found 1 error (1 fixed, 0 remaining).

ruff format..............................................................Failed
- hook id: ruff-format
- files were modified by this hook

1 file reformatted
```

Hooki usunęły nieużywany import i sformatowały plik, ale commit nie powstał — narzędzie zmieniło pliki, więc programista ma je obejrzeć i dodać ponownie. Drugie `git add zly.py` i `git commit` przechodzą z wynikiem `Passed`. Wersje hooków podnosimy poleceniem `pre-commit autoupdate`, które zmienia wpisy `rev` w pliku `.pre-commit-config.yaml` na najnowsze wydania (zmianę oglądamy poleceniem `git diff`); wersje tych samych narzędzi w `requirements-dev.txt` uzgadniamy wtedy z nowymi wpisami `rev`, aby hook, środowisko projektu i serwer CI nadal używały jednej wersji. Opcja `git commit --no-verify` pomija hooki i jest przeznaczona na wyjątkowe sytuacje, nie na codzienną pracę.

Do konfiguracji można dodać mypy z repozytorium `pre-commit/mirrors-mypy`:

```yaml title=".pre-commit-config.yaml"
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v2.3.1
    hooks:
      - id: mypy
```

Hook uruchamia mypy w osobnym środowisku, w którym nie ma pakietów projektu — importy zewnętrzne trzeba dopisać jako `additional_dependencies`. Wielu programistów zostawia więc mypy serwerowi CI, a w hookach trzyma tylko szybkie sprawdzenia Ruff. Niezależnie od miejsca uruchomienia tryb `strict` wymaga adnotacji także w testach. Funkcje testowe potrzebują typu wyniku `-> None` oraz typów parametrów — fixture (`tmp_path: Path`, `capsys: pytest.CaptureFixture[str]`, `monkeypatch: pytest.MonkeyPatch`, `promienie: list[float]`) i parametrów z `parametrize`; same fixture potrzebują typu wyniku: `promienie() -> list[float]`, a fixture z `yield`, będąca funkcją generatorową, `plik_z_liczbami(tmp_path: Path) -> Iterator[Path]` z typem `Iterator` importowanym z modułu `collections.abc`. Testy z podrozdziału o pytest trzeba tak uzupełnić, zanim `python -m mypy .` przejdzie.

## Narzędzia w edytorze

Te same sprawdzenia warto widzieć podczas pisania. Rozszerzenie **Ruff** (`charliermarsh.ruff`) w VSC podkreśla uwagi lintera i formatuje plik przy zapisie po dodaniu dwóch ustawień w bloku `"[python]"` pliku `settings.json` (otwieranego jak w sekcji [Usuwanie Pylance](../01-instalacja/konfiguracja.md#usuwanie-pylance)). Jeżeli plik ma już ten blok — na przykład z domyślnym formaterem ustawionym w rozdziale 1 — zmieniamy w nim wartość `"editor.defaultFormatter"` i dopisujemy `"editor.formatOnSave"`; w przeciwnym razie dopisujemy cały blok jako ostatni wpis — przed zamykającym nawiasem klamrowym `}` pliku, po przecinku za poprzednim wpisem:

```json title="settings.json"
"[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
}
```

Rozszerzenie **Mypy Type Checker** (`ms-python.mypy-type-checker`), zainstalowane w rozdziale 3, pokazuje błędy mypy w edytorze; Pylance robi to również, o ile nie wyłączyliśmy go zgodnie z rozdziałem [1. Instalacja i środowisko pracy](../01-instalacja/konfiguracja.md#usuwanie-pylance). Rozszerzenia czytają konfigurację z `pyproject.toml`, więc edytor i wiersz poleceń zgłaszają to samo.

## GitHub Actions — ciągła integracja

**Ciągła integracja** (ang. *continuous integration*, CI) to uruchamianie testów i sprawdzeń na serwerze po każdym wysłaniu zmian, niezależnie od komputera programisty. W serwisie GitHub służy do tego **GitHub Actions**: plik YAML w katalogu `.github/workflows` opisuje, kiedy i co uruchomić:

```yaml title=".github/workflows/ci.yml"
name: CI

on: [push, pull_request]

jobs:
  testy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v7
        with:
          python-version: "3.14"
      - run: python -m pip install -r requirements-dev.txt
      - run: python -m ruff check .
      - run: python -m ruff format --check .
      - run: python -m mypy .
      - run: python -m pytest --cov
```

Po każdym `git push` i przy każdym żądaniu scalenia (ang. *pull request*) serwis uruchamia maszynę z systemem Linux, pobiera repozytorium (`actions/checkout`), instaluje wskazaną wersję Pythona (`actions/setup-python`) i wykonuje kolejne polecenia; wynik — zielony lub czerwony znacznik — pojawia się przy commicie, a szczegóły w zakładce **Actions**. Wersje akcji (`@v7`) to według stanu na 17 X 2026 najnowsze wydania główne obu akcji. Ten sam plik można rozszerzyć o macierz wersji Pythona i systemów (`windows-latest`, `macos-latest`), gdy projekt ma działać na wielu platformach.

## Instalacja narzędzi — `pipx` i `uv`

Narzędzia takie jak Ruff czy pre-commit służą we wszystkich projektach, więc zamiast instalować je w każdym venv, można zainstalować je raz, w odizolowanych środowiskach, poleceniem `pipx install ruff` albo `uv tool install ruff`. Książka trzyma się konwencji `python -m pip` w środowisku projektu z rozdziału 1 — jest jednoznaczna i wystarcza; `uv`, wspomniane w sekcji [Rozwiązania alternatywne](../01-instalacja/pip.md#rozwiazania-alternatywne), łączy rolę pip, venv i pipx w jednym, szybkim narzędziu i warto je poznać po opanowaniu podstaw.

## Typowe błędy

- **Narzędzia w różnych wersjach** u programisty, w hooku i w CI — stąd plik wymagań z przypiętymi wersjami i `rev` w konfiguracji pre-commit.
- **Testy zależne od sieci lub zegara** — w CI zawodzą losowo; zastępujemy zależności atrapami z podrozdziału o testowaniu.
- **Hook mypy bez zależności projektu** — zgłasza fałszywe błędy importów; potrzebne `additional_dependencies` albo mypy tylko w CI.
- **Pliki robocze w repozytorium** — `.venv`, `__pycache__`, `.coverage`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache` należą do pliku `.gitignore`, w którym Git trzyma listę pomijanych ścieżek, nie do historii projektu.
- **Nawyk `--no-verify`** — hooki, które się omija, przestają chronić przed czymkolwiek.
- **Sprawdzenia dodane na końcu projektu** — setki uwag naraz zniechęcają; konfigurację narzędzi tworzymy w pierwszym commicie, gdy nie ma jeszcze kodu do poprawiania.
