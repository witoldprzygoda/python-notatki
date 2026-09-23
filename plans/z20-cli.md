# Projekt rozdziału 20 części „Python Zastosowania” — Narzędzia wiersza poleceń

Drugi rozdział ścieżki Automatyzacja. Branch: `content/zastosowania-20` (z `dev` po rozdziale 19). Realizacja autonomiczna w ramach zbiorczego polecenia autora z 23 IX 2026.

## Decyzje redakcyjne (23 IX 2026)

1. **Zakres:** argumenty i opcje ponad rozdział 7 „Python Notatki” (typ `Path`, `nargs`, `choices` z `%(default)s` w pomocy, `action="count"`, `BooleanOptionalAction`, grupa wzajemnie wykluczająca, `metavar`, `epilog`, kod `2` przy błędzie użycia; narzędzie `porzadek` porządkujące pliki według rozszerzenia lub daty z `--dry-run`, `-v`/`-q` i dziennikiem `logging`); strumienie, kody wyjścia i dziennik (filtr `licznik` czytający pliki albo `stdin`, konwencja `-`, wyniki na `stdout`, komunikaty na `stderr`, kody 0/1/2 i 130 po `KeyboardInterrupt`, `BrokenPipeError`, `logging` na `stderr` sterowane opcjami, kodowanie na Windows — `PYTHONUTF8`, `reconfigure`); procesy, pliki i konfiguracja (`subprocess.run` z listą argumentów, `capture_output`, `text`/`encoding`, `check` i `CalledProcessError`, `timeout`, `input`, `sys.executable`, `shutil.which`, archiwum `shutil.make_archive`, `tempfile`; kolejność źródeł konfiguracji: wartości domyślne < plik TOML < zmienne środowiskowe < argumenty); od skryptu do polecenia (testy narzędzia: `main(argv)` z `capsys` i `tmp_path`, `monkeypatch.setenv`, test procesu przez `subprocess`; polecenie w pakiecie — `[project.scripts]` i `__main__.py` z odsyłaczem do rozdziału 17, `pipx`, `zipapp`; alternatywy Click/Typer/rich jednym akapitem; lista kontrolna). Cztery strony + index. Poza zakresem: `curses`, kolorowanie ANSI poza wzmianką (rozdział 9 „Python Notatki” ma animacje), `readline`/autouzupełnianie, `argparse` w wersji z `parse_known_args`, obsługa sygnałów poza `KeyboardInterrupt`, `asyncio.subprocess`.
2. **Biblioteki:** tylko biblioteka standardowa (`argparse`, `sys`, `logging`, `pathlib`, `shutil`, `subprocess`, `tomllib`, `os`, `tempfile`); pytest 9.1.1 do testów. Plik wymagań: `pytest==9.1.1`.
3. **Dane:** pliki przykładowe tworzone przez skrypty kontrolne (`os.utime` ustawia daty modyfikacji, więc katalogi `rok-miesiąc` są deterministyczne); plik konfiguracji TOML jako blok. Harness: narzędzia (`porzadek.py`, `licznik.py`, `konfiguracja.py`) w `--skip`, uruchamiane przez skrypty `uzycie-*.py` — wywołania `main(argv)` i `subprocess.run([sys.executable, …])` z `PYTHONUTF8=1` w środowisku potomnym; pomoc `argparse` deterministyczna (szerokość 80 kolumn przy przechwyconym wyjściu).
4. **Fakty sprawdzone 23 IX 2026 (Python 3.14.7):** `argparse` przy błędzie użycia wypisuje `usage` i `error` na `stderr` i kończy kodem `2`; `BooleanOptionalAction` tworzy parę `--kolor/--no-kolor`; `action="count"` z `default=0`; `type=Path` zwraca `WindowsPath`; grupa wzajemnie wykluczająca zgłasza „not allowed with argument”; `subprocess.run(..., capture_output=True, text=True, encoding="utf-8")` zwraca `CompletedProcess` z `returncode`, `stdout`, `stderr`, `args`; `check=True` → `CalledProcessError.returncode`; `timeout` → `TimeoutExpired.timeout`; `input=` przekazuje tekst na `stdin` potomka; `shutil.which("python")` znajduje interpreter, nieistniejące → `None`; `shutil.disk_usage` zwraca krotkę nazwaną; `sys.stdin.isatty()` `False` przy przechwyceniu; `tomllib.loads` zwraca słownik zagnieżdżony; `sys.flags.utf8_mode` 1 przy `-X utf8`.
5. **Terminy:** „narzędzie wiersza poleceń” (ang. *command-line tool*, CLI), „opcja” i „flaga”, „podpolecenie”, „próbne uruchomienie” (ang. *dry run*), „strumień standardowy”, „kod wyjścia” (ang. *exit code*), „potok” (ang. *pipe*), „filtr”, „proces potomny” (ang. *child process*), „zmienna środowiskowa”, „plik konfiguracyjny”.
6. Odsyłacze wstecz: „Python Notatki” 7 (`argparse`, kody wyjścia, `sys.exit(main())`), 8 (`logging`), 9 (strumienie, `pathlib`, `shutil`, `tempfile`, `tomllib`), 16 (pytest, `tmp_path`, `capsys`, `monkeypatch`); „Python Zastosowania” 17 (podpolecenia, punkty wejścia, pipx, zipapp), 19 (wzorce w filtrze). Zapowiedzi: 21 (pobieranie stron), 23 (projekt narzędzia) — `TODO`.
7. Domknięcia: markery „narzędziach wiersza poleceń” w 12/model-i-raport i 19/pulapki → `20-cli/index.md`.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i pliki |
|---|---|---|
| `index.md` | Wprowadzenie / „20. Narzędzia wiersza poleceń” | cel; biblioteka; plik wymagań; ---; ## W tym rozdziale (4) |
| `argumenty.md` | Argumenty i opcje | Narzędzie porządkujące (`porzadek.py`); Uruchomienie i pomoc (`uzycie-porzadek.py`); Reguły projektowania opcji (tabela) |
| `strumienie.md` | Strumienie, kody wyjścia i dziennik | Filtr tekstu (`licznik.py`); Potoki i kody wyjścia (`uzycie-licznik.py`); Dziennik na `stderr`; Kodowanie na Windows |
| `procesy.md` | Procesy, pliki i konfiguracja | Procesy potomne (`procesy.py`); Archiwa i narzędzia systemowe (`archiwum.py`); Źródła konfiguracji (`ustawienia.toml`, `konfiguracja.py`, `uzycie-konfiguracja.py`) |
| `narzedzie.md` | Od skryptu do polecenia | Testy narzędzia (`test_porzadek.py`, `test_licznik.py`, pytest); Polecenie w pakiecie; Alternatywy; Lista kontrolna; Dalej (TODO 21, 23) |

Szacunek: 650–800 linii; bez wykresów i zrzutów.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 19)

```yaml
      - 20. Narzędzia wiersza poleceń:
          - Wprowadzenie: zastosowania/20-cli/index.md
          - Argumenty i opcje: zastosowania/20-cli/argumenty.md
          - Strumienie, kody wyjścia i dziennik: zastosowania/20-cli/strumienie.md
          - Procesy, pliki i konfiguracja: zastosowania/20-cli/procesy.md
          - Od skryptu do polecenia: zastosowania/20-cli/narzedzie.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `narzedzie.md` | pobieranie stron; projekt narzędzia automatyzującego | rozdziały 21, 23 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/12-projekt-ml/model-i-raport.md` (marker CLI) | `20-cli/index.md` |
| `zastosowania/19-re/pulapki.md` (marker CLI) | `20-cli/index.md` |

## CONTENT HANDOFF

Brak wykładu źródłowego; rozdział rozwija `argparse` z rozdziału 7 „Python Notatki” (parser, argument pozycyjny, opcja, pomoc, kody wyjścia) i podpolecenia z rozdziału 17.

## Listy kontrolne

- Przed commitem: staging z bloków; `refresh_outputs.py`; `verify_page.py` dwa przebiegi z `--skip` narzędzi i testów; pytest w stagingu; oba buildy `--strict`; cudzysłowy; kolokwializmy; recenzje z weryfikacją uwag.
- Po commicie: domknięcia w 12/model-i-raport i 19/pulapki, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć.
