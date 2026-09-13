# Projekt rozdziału 16 — Warsztat programisty i dalsza droga

Skondensowany projekt stron rozdziału 16 według `PLAN_ROZWOJU.md` (sekcja 4, „16. Warsztat programisty i dalsza droga”) i `DEVELOPMENT_WORKFLOW.md`. Branch: `content/16-warsztat` (z `dev` po integracji rozdziału 15). Realizacja autonomiczna na polecenie autora („Działaj z domknięciem części I”); rozdział zamyka część I książki.

## Decyzje redakcyjne (13 IX 2026)

1. **Wersje odniesienia (sprawdzone 13 IX 2026, `pip index versions`):** pytest 9.1.1, pytest-cov 7.1.0, mypy 2.3.1, ruff 0.16.7 (hook `ruff-pre-commit` rev `v0.16.7`, id `ruff-check` i `ruff-format`), pre-commit 4.6.2, black 26.5.1, pyright 1.1.414, Pyrefly 1.3.0, ty 0.0.80 (wersja rozwojowa), `actions/checkout@v7`, `actions/setup-python@v7`; Python 3.15.0 — rc2 z 1 IX 2026, wydanie finalne planowane na 1 X 2026 (PEP 790). Wersje w książce podawane „w chwili pisania”.
2. **Przykładowy projekt:** płaski układ w katalogu tymczasowym harnessu — moduł `kolo.py` (`pole_kola()`, `sredni_promien()`), `test_kolo.py`, `test_fixtures.py`, `conftest.py`, `pyproject.toml` z sekcjami `[tool.pytest.ini_options]`, `[tool.mypy]`, `[tool.ruff]`; układ `src` z rozdziału 7 przywołany odsyłaczem. Wydruki pytest, mypy, ruff i pre-commit pochodzą z rzeczywistych uruchomień (nagłówek `platform …` skrócony do wiersza z wersją pytest); bloki plików testowych są uruchamiane przez harness jako skrypty bez wyniku (rc = 0).
3. **Narzędzia wybrane:** pytest (fixtures, parametrize, conftest, markery, `-k/-x/--lf`, pytest-cov), mypy jako główny sprawdzacz typów, Ruff jako linter i formater (black, autopep8, pylint jako alternatywy z odsyłaczem do rozdziału 1), pre-commit, GitHub Actions. Zakładamy repozytorium Git, którego kurs używa organizacyjnie (GitHub Classroom); Git nie jest tematem książki — jedno zdanie i odsyłacz do dokumentacji. Sekcje o `unittest.mock` i o innych sprawdzaczach typów jako „(dla dociekliwych)”.
4. **mypy pokazany na programie, który działa, ale przypadkiem** (`bledy.py`: `wynik: str = podwoj(5)` i `znajdz(1).upper()` — uruchomienie kończy się poprawnie, mypy zgłasza dwa błędy) — harness nie wymaga tracebacku.
5. **Zrzut ekranu:** panel Testing w VSC — jedno miejsce `<!-- TODO: screenshot -->` z wpisem w `ZRZUTY.md` (kadr: panel z drzewem testów po uruchomieniu).
6. **„Co dalej”:** asyncio jako odsyłacz do rozdziału 15 (bez powtarzania przykładu), Flask i FastAPI po jednym minimalnym listingu `.python .no-copy`, data science jako odsyłacze do rozdziału 14 i części II, Python 3.15 jako nota (PEP 810, 686, 798, 814, 661, 799), ściągawka narzędzi (tabela), zasoby, posłowie odsyłające do części II (`plans/CZESC-II.md`).
7. **Modernizacje względem W12:** `py312` → `py314`; `typing.List/Optional/Union` tylko historycznie, `collections.abc.Callable`; `type` alias (3.12) i składnia generyków PEP 695; `pip install` → `python -m pip install`; hooki `ruff-check`/`ruff-format` zamiast `ruff`/black; `uvicorn main:app` → `fastapi dev`; pominięte: Godot, TensorFlow, rozdziały Git ze slajdów 15–18 (poza zakresem), sekcja profilowania (rozdział 13).
8. Terminologia: „sprawdzacz typów” (ang. *type checker*) — w rozdziale 3 użyto „narzędzia analizy statycznej”; oba wyrażenia z „(ang. …)” przy pierwszym użyciu; „fixture” bez tłumaczenia (kursywa przy pierwszym użyciu, dalej w kodzie); „ciągła integracja” (ang. *continuous integration*, CI).

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i pliki |
|---|---|---|
| `index.md` | Wprowadzenie / „16. Warsztat programisty i dalsza droga” | od działającego kodu do utrzymywalnego; mapa narzędzi (cel → narzędzie → miejsce w książce); ---; ## W tym rozdziale (5); nota: bez laboratorium, zamknięcie części I |
| `testowanie.md` | Testowanie z pytest — techniki zaawansowane | Przypomnienie (rozdz. 7 i 8; `kolo.py`, `pyproject.toml`); Fixtures (`test_fixtures.py`: `@pytest.fixture`, `yield`, `scope`, `tmp_path`, `capsys`, `monkeypatch`); Parametryzacja (`test_kolo.py`: `parametrize` z `ids`, `pytest.approx`, `raises(match=)`); `conftest.py` i markery (rejestracja w `pyproject.toml`, `-m`, `skip`, `xfail`); Uruchamianie i pokrycie (`-v`, `-k`, `-x`, `--lf`, pytest-cov; H3 Panel Testing w VSC); Atrapy — `monkeypatch` i `unittest.mock` (dla dociekliwych) |
| `typy-statyczne.md` | Adnotacje typów w praktyce | Przypomnienie (rozdz. 3 i 6); Typy złożone (`list[int]`, `dict[str, float]`, `X \| None`, `Callable`, `Iterable`, `Any`; `typing.List` historycznie) (`typy-zlozone.py`); Aliasy i generyki (`type Wektor = list[float]`, `def pierwszy[T](...)`) (`aliasy.py`); `TypedDict`, klasy danych i `Protocol` (`slowniki-typowane.py`; odsyłacze do 12); mypy (`bledy.py` + terminal; `[tool.mypy] strict`; `# type: ignore[kod]`); Inne sprawdzacze typów (dla dociekliwych) (Pylance/pyright, Pyrefly, ty; stan na IX 2026) — domyka 6, 11, 12, 13 |
| `styl-kodu.md` | Styl i formatowanie kodu | Zen Pythona w praktyce (tabela aforyzm → przykład; odsyłacz do rozdz. 2); PEP 8 w praktyce (tabela dobrze/źle; odsyłacz do rozdz. 1); Dokumenty PEP (tabela: 8, 20, 257, 484, 572, 634, 649, 703, 750, 810); Ruff — linter i formater (`brzydki.py` przed/po, `ruff check`, `--fix`, `ruff format`, `[tool.ruff]`, reguły E F I UP B); Alternatywy (black, autopep8, pylint) |
| `automatyzacja-jakosci.md` | Automatyzacja jakości — pre-commit i CI | Zasada: te same sprawdzenia lokalnie i na serwerze; pre-commit (`.pre-commit-config.yaml`: ruff-check, ruff-format, mypy z `mirrors-mypy`; `pre-commit install`, `run --all-files` — terminal); Narzędzia w edytorze (rozszerzenia Ruff `charliermarsh.ruff` i Mypy Type Checker `ms-python.mypy-type-checker`); GitHub Actions (`.github/workflows/ci.yml`: checkout@v7, setup-python@v7 z 3.14, `python -m pip install -e .[dev]` albo `-r requirements-dev.txt`, ruff, mypy, pytest); Instalacja narzędzi (`python -m pip` w venv; `pipx`/`uv tool` jako nota); Typowe błędy |
| `co-dalej.md` | Co dalej | Programowanie asynchroniczne (odsyłacz do 15, biblioteki); Aplikacje WWW — Flask i FastAPI (`.python .no-copy` ×2); Dane i uczenie maszynowe (odsyłacze do 14 i części II); Python 3.15 (nota); Ściągawka narzędzi (tabela); Zasoby i projekty na start; Posłowie |

Szacunek: 850–950 linii.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 15)

```yaml
  - 16. Warsztat programisty i dalsza droga:
      - Wprowadzenie: 16-warsztat/index.md
      - Testowanie z pytest — techniki zaawansowane: 16-warsztat/testowanie.md
      - Adnotacje typów w praktyce: 16-warsztat/typy-statyczne.md
      - Styl i formatowanie kodu: 16-warsztat/styl-kodu.md
      - Automatyzacja jakości — pre-commit i CI: 16-warsztat/automatyzacja-jakosci.md
      - Co dalej: 16-warsztat/co-dalej.md
```

`docs/index.md`: „16. [Warsztat programisty i dalsza droga](16-warsztat/index.md) — pytest zaawansowany, adnotacje typów i mypy, Ruff, pre-commit i CI, co dalej”.

## Zapowiedzi w przód

Brak zapowiedzi z `TODO`; posłowie odsyła do części II ogólnie (`plans/CZESC-II.md`).

## Domknięcia zapowiedzi z wcześniejszych rozdziałów

| Plik | Wiersz | Zapowiedź | Cel |
|---|---|---|---|
| `06-funkcje/definiowanie-funkcji.md` | 218 | admonition o adnotacjach — TODO | `typy-statyczne.md` (H1) |
| `06-funkcje/zasieg-nazw-i-domkniecia.md` | 18 | zasięgi adnotacji — TODO | `typy-statyczne.md#przypomnienie` |
| `11-model-danych/operatory.md` | 546 | narzędzia korzystające z adnotacji — TODO | `typy-statyczne.md#mypy` |
| `12-oop-zaawansowane/index.md` | 5 | analiza statyczna — TODO | `typy-statyczne.md#mypy` |
| `12-oop-zaawansowane/mixiny-i-abstrakcja.md` | 332 | analiza statyczna a `Protocol` — TODO | `typy-statyczne.md#typeddict-klasy-danych-i-protocol` |
| `13-wydajnosc/przyspieszanie-pythona.md` | 68 | mypy i adnotacje — TODO | `typy-statyczne.md#mypy` |
| `02-konsola/konsola-w-praktyce.md` | 117–119 | Zen of Python (bez TODO) | `styl-kodu.md#zen-pythona-w-praktyce` — tylko jeśli tekst zapowiada rozwinięcie |

## CONTENT HANDOFF (rozbieżności ze źródłami)

(a) W12 sl. 10–13: `python_version = "3.12"`, `target-version = "py312"` → 3.14; (b) W12 sl. 13–14: hooki `ruff` + black + mypy → `ruff-check` + `ruff-format` (Ruff zastępuje black), mypy przez `mirrors-mypy`; (c) W12 sl. 9: `typing.Optional/Union/List` jako składnia bieżąca → w 3.14 `X | None`, `list[int]`, `collections.abc.Callable`; (d) W12 sl. 24: `uvicorn main:app --reload` → `fastapi dev main.py` (pakiet `fastapi[standard]`); (e) W12 sl. 15–18 (Git) i 20–21 (profilowanie) poza rozdziałem — Git jako materiał organizacyjny kursu, profilowanie w rozdziale 13; (f) W12 sl. 25: TensorFlow i Godot pominięte; wersje bibliotek zaktualizowane (scikit-learn 1.9, PyTorch 2.14, pandas 3.0); (g) W12 sl. 6: `pip install pytest-cov` → `python -m pip install pytest-cov`; próg pokrycia jako wskazówka, nie reguła.

## Listy kontrolne

- Przed commitem stron: harness (skrypty bez wyników rc = 0), wydruki narzędzi z rzeczywistych uruchomień w `scratchpad/probe16`, oba buildy `--strict`, audyt kotwic, cudzysłowy, kolokwializmy, trzy recenzje.
- Po commicie: domknięcia z tabeli, wpis w `ZRZUTY.md`, status w `PLAN_ROZWOJU.md` (część I ukończona), integracja do `dev`, wpis w pamięci, raport końcowy z CONTENT HANDOFF rozdziałów 14–16.
