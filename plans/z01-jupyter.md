# Projekt rozdziału 1 tomu II — Jupyter i warsztat danych

Pierwszy rozdział „Python Zastosowania” (ścieżka Dane) według `PLAN_ZASTOSOWANIA.md`. Branch: `content/zastosowania-01` (z `dev` po `066079b`). Realizacja autonomiczna na polecenie autora z 13 IX 2026.

## Decyzje redakcyjne (13 IX 2026)

1. **Cel:** warsztat pracy z danymi w notatniku — od pierwszej komórki po powtarzalny projekt — bez wprowadzania nowych bibliotek numerycznych; NumPy i Matplotlib w zakresie rozdziału 14 tomu I. Rozdział otwiera ścieżkę Dane i jest wymagany przez pozostałe jej rozdziały.
2. **Środowisko odniesienia:** Python 3.14.7; JupyterLab 4.6.3, notebook 7.6.2, ipykernel 7.3.0, IPython 9.17.1, nbconvert 7.17.1 (sprawdzone 13 IX 2026, `pip index versions`); rozszerzenie Jupyter dla VSC (`ms-toolsai.jupyter`). Instalacja w venv projektu: `python -m pip install jupyterlab ipykernel` (JupyterLab tylko do pracy w przeglądarce; VSC wymaga `ipykernel`).
3. **Konwencja komórek:** ```python title="<nazwa>.ipynb — komórka N"``` z wynikiem w `{ .text .no-copy }` (wartość ostatniego wyrażenia wypisywana jak w notatniku, bez `Out[N]:`); weryfikacja skryptem `scripts/verify_cells.py` (`nbclient`, jądro venv, maski czasów; `--cwd=notatniki` dla strony o środowisku); `verify_page.py` pomija bloki `.ipynb`. Polecenia magiczne i `?` pokazane w komórkach; `?` jako `.python .no-copy` (wynik w panelu pomocy, nie w strumieniu).
4. **Wykresy w notatniku** powstają pod komórką; w książce komórka dodatkowo zapisuje plik, a obraz w `img/` generuje `verify_cells.py` (kopiuje pliki PNG utworzone przez komórki).
5. **Dane przykładowe** osadzone jako blok `text title="pomiary.csv"` (średnie miesięczne temperatury i opady dwóch lat, oznaczone jako dane przykładowe); brak katalogu `data/`.
6. **Zrzuty ekranu** (2): tworzenie notatnika i wybór jądra w VSC; wpisy w `ZRZUTY.md`.
7. **Odsyłacze wstecz:** tom I — 1 (venv, pip, Notebook i Colab), 7 (moduły, `pyproject.toml`), 9 (CSV, `pathlib`), 13 (`timeit`), 14 (NumPy, Matplotlib), 16 (`requirements-dev.txt`, Ruff). Zapowiedzi w przód: rozdział 2 (NumPy w praktyce), 4 (pandas) — `TODO` po temacie.
8. Terminy: „notatnik” (ang. *notebook*), „jądro” (ang. *kernel*), „komórka” (ang. *cell*), „polecenie magiczne” (ang. *magic command*), „powtarzalność” (ang. *reproducibility*).

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i pliki |
|---|---|---|
| `index.md` | Wprowadzenie / „1. Jupyter i warsztat danych” | po co notatnik; co zakłada rozdział (tom I); ---; ## W tym rozdziale (4) |
| `notatnik-jupyter.md` | Notatnik Jupyter w VSC | Notatnik a skrypt; Instalacja i pierwszy notatnik (terminal, VSC, jądro; zrzuty); Komórki kodu i wartość ostatniego wyrażenia (`pierwszy.ipynb` komórki 1–4); Komórki Markdown; Stan jądra i kolejność wykonania (`stan.ipynb` 1–3; restart, „Run All”); Polecenia magiczne (`magia.ipynb`: `%timeit`, `%%time`, `%who`); Pomoc w notatniku (`?`, `??`, `help()`); JupyterLab w przeglądarce i eksport (`python -m jupyter lab`, `nbconvert --to script/html`, notatnik w Git) |
| `srodowisko-projektu.md` | Środowisko projektu danych | Katalog projektu (schemat); Środowisko i wersje (`requirements.txt`, `pip freeze`, `pip index versions`); Dane wejściowe i ścieżki (`pathlib`, katalog roboczy notatnika w VSC); Powtarzalność (ziarno, „Restart and Run All”, wyniki z datą — `powtarzalnosc.ipynb`); Z notatnika do modułu (`narzedzia.py`, import, `%autoreload`) |
| `dokumentacja-bibliotek.md` | Czytanie dokumentacji bibliotek | Przewodnik a opis API; Docstring, `help()` i `inspect.signature()` (`sygnatura.py`); Wersje, zmiany i ostrzeżenia o wycofaniu (`ostrzezenie.py` z `DeprecationWarning`; `pip index versions`, `pip show`); Zasada „najpierw biblioteka standardowa” (tabela); Ocena pakietu z PyPI |
| `pierwsza-analiza.md` | Pierwsza analiza w notatniku | Zadanie i dane (`pomiary.csv`); Wczytanie (`analiza.ipynb` komórki: `np.genfromtxt(names=True)`); Statystyki (średnie roczne, najcieplejszy miesiąc); Wykres (linie temperatur i słupki opadów, `fig.savefig`); Wnioski w Markdown i zapis wyników (`np.savetxt` do `wyniki/`); Od notatnika do skryptu (`nbconvert --to script`); Co dalej (zapowiedzi 2 i 4) |

Szacunek: 700–800 linii.

## CONTENT HANDOFF

Rozdział nie ma odpowiednika w `sources/`; strona `01-instalacja/notebook.md` tomu I opisuje Jupyter Notebook klasyczny i Anacondę — rozdział odsyła do niej i uzupełnia o pracę w VSC (bez zmian w tomie I).

## Listy kontrolne

- Przed commitem: `verify_cells.py` na stronach z notatnikami, harness na skryptach, oba buildy `--strict`, audyt kotwic i obrazów, cudzysłowy, kolokwializmy, trzy recenzje.
- Po commicie: status w `PLAN_ZASTOSOWANIA.md`, `ZRZUTY.md`, integracja do `dev`, wpis w pamięci, raport.
