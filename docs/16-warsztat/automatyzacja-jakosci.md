# Automatyzacja jakości — pre-commit i CI

Testy, sprawdzacz typów i Ruff przynoszą korzyść tylko wtedy, gdy są uruchamiane zawsze — nie wtedy, gdy ktoś o nich pamięta. W tym podrozdziale ustawiamy je w dwóch miejscach: przed zapisaniem zmian w repozytorium, na komputerze programisty, oraz na serwerze po każdym wysłaniu kodu. Zakładamy, że projekt jest w repozytorium Git; sam Git opisuje jego dokumentacja (git-scm.com/doc).

## Zasada: te same sprawdzenia lokalnie i na serwerze

Konfigurację narzędzi przechowujemy w `pyproject.toml` — sekcje z poprzednich podrozdziałów — a listę narzędzi deweloperskich trzymamy w osobnym pliku wymagań z rozdziału 1:

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

```powershell title="Terminal"
python -m pip install pre-commit
pre-commit install
pre-commit run --all-files
```

```{ .text .no-copy }
pre-commit installed at .git\hooks\pre-commit
ruff check...............................................................Passed
ruff format..............................................................Passed
```

Wpis `repo` wskazuje repozytorium z definicją hooków, `rev` — jego wersję (odpowiadającą wersji Ruff), a `hooks` — które z nich włączamy; hook `ruff-check` z argumentem `--fix` poprzedza `ruff-format`, bo poprawki lintera mogą wymagać ponownego sformatowania. Przy pierwszym uruchomieniu pre-commit pobiera narzędzia do własnego, odizolowanego środowiska, więc nie muszą być zainstalowane w venv projektu. Polecenie `run --all-files` sprawdza cały projekt; od tej chwili każdy commit sprawdza tylko pliki dodane do niego poleceniem `git add`. Tak wygląda commit pliku, który łamie reguły:

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

Hooki usunęły nieużywany import i sformatowały plik, ale commit nie powstał — narzędzie zmieniło pliki, więc programista ma je obejrzeć i dodać ponownie. Drugie `git add zly.py` i `git commit` przechodzą z wynikiem `Passed`. Wersje hooków podnosimy poleceniem `pre-commit autoupdate`; opcja `git commit --no-verify` pomija hooki i jest przeznaczona na wyjątkowe sytuacje, nie na codzienną pracę.

Do konfiguracji można dodać mypy z repozytorium `pre-commit/mirrors-mypy`:

```yaml title=".pre-commit-config.yaml"
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v2.3.1
    hooks:
      - id: mypy
```

Hook uruchamia mypy w osobnym środowisku, w którym nie ma pakietów projektu — importy zewnętrzne trzeba dopisać jako `additional_dependencies`. Wielu programistów zostawia więc mypy serwerowi CI, a w hookach trzyma tylko szybkie sprawdzenia Ruff. Niezależnie od miejsca uruchomienia tryb `strict` wymaga adnotacji także w funkcjach testowych: typu wyniku `-> None` oraz typów parametrów — fixture (`tmp_path: Path`, `capsys: pytest.CaptureFixture[str]`, `monkeypatch: pytest.MonkeyPatch`, `promienie: list[float]`) i parametrów z `parametrize`; testy z podrozdziału o pytest trzeba nimi uzupełnić, zanim `python -m mypy .` przejdzie.

## Narzędzia w edytorze

Te same sprawdzenia warto widzieć podczas pisania. Rozszerzenie **Ruff** (`charliermarsh.ruff`) w VSC podkreśla uwagi lintera i formatuje plik przy zapisie po dodaniu do ustawień:

```json title="settings.json"
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true
    }
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

Po każdym `git push` i przy każdym żądaniu scalenia (ang. *pull request*) serwis uruchamia maszynę z systemem Linux, pobiera repozytorium (`actions/checkout`), instaluje wskazaną wersję Pythona (`actions/setup-python`) i wykonuje kolejne polecenia; wynik — zielony lub czerwony znacznik — pojawia się przy commicie, a szczegóły w zakładce **Actions**. Wersje akcji (`@v7`) są aktualne w chwili pisania. Ten sam plik można rozszerzyć o macierz wersji Pythona i systemów (`windows-latest`, `macos-latest`), gdy projekt ma działać na wielu platformach.

## Instalacja narzędzi — `pipx` i `uv`

Narzędzia takie jak Ruff czy pre-commit służą we wszystkich projektach, więc zamiast instalować je w każdym venv, można zainstalować je raz, w odizolowanych środowiskach, poleceniem `pipx install ruff` albo `uv tool install ruff`. Książka trzyma się konwencji `python -m pip` w środowisku projektu z rozdziału 1 — jest jednoznaczna i wystarcza; `uv`, wspomniane w sekcji [Rozwiązania alternatywne](../01-instalacja/pip.md#rozwiazania-alternatywne), łączy rolę pip, venv i pipx w jednym, szybkim narzędziu i warto je poznać po opanowaniu podstaw.

## Typowe błędy

- **Narzędzia w różnych wersjach** u programisty, w hooku i w CI — stąd plik wymagań z przypiętymi wersjami i `rev` w konfiguracji pre-commit.
- **Testy zależne od sieci lub zegara** — w CI zawodzą losowo; zastępujemy zależności atrapami z podrozdziału o testowaniu.
- **Hook mypy bez zależności projektu** — zgłasza fałszywe błędy importów; potrzebne `additional_dependencies` albo mypy tylko w CI.
- **Pliki robocze w repozytorium** — `.venv`, `__pycache__`, `.coverage`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache` należą do pliku `.gitignore`, w którym Git trzyma listę pomijanych ścieżek, nie do historii projektu.
- **Nawyk `--no-verify`** — hooki, które się omija, przestają chronić przed czymkolwiek.
- **Sprawdzenia dodane na końcu projektu** — setki uwag naraz zniechęcają; konfigurację narzędzi tworzymy w pierwszym commicie, gdy nie ma jeszcze kodu do poprawiania.
