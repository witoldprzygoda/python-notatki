# Co dalej

Część „Python Notatki” kończy się na języku i jego bibliotece standardowej — to fundament, na którym stoją wszystkie zastosowania Pythona. Ten podrozdział wskazuje najczęstsze kierunki dalszej nauki, zbiera narzędzia z całej książki w jedną ściągawkę i podaje, gdzie szukać materiałów.

## Programowanie asynchroniczne

Zapowiedź `asyncio` z rozdziału [15. Współbieżność — wątki, procesy i GIL](../15-wspolbieznosc/studia-wydajnosci.md#zapowiedz-asyncio) otwiera drogę do serwerów i klientów obsługujących setki połączeń w jednym wątku. Dalsze kroki to biblioteki asynchroniczne: klient HTTP `httpx` (działa też synchronicznie) lub `aiohttp`, sterowniki baz danych `asyncpg` i `aiosqlite` oraz szkielety aplikacji WWW (ang. *web framework*) zbudowane na `asyncio`, jak FastAPI z następnej sekcji. Regułą pozostaje ta z rozdziału 15: `asyncio` opłaca się przy wielu zadaniach czekających, nie przy obliczeniach.

## Aplikacje WWW — Flask i FastAPI

Aplikacja WWW w Pythonie to funkcje przypisane do adresów. **Flask** (w chwili pisania wersja 3.1) jest szkieletem minimalnym; poniższy plik `aplikacja.py` jest kompletną aplikacją:

```{ .python .no-copy }
from flask import Flask

app = Flask(__name__)


@app.route("/")
def strona_glowna():
    return "Witaj!"


@app.route("/api/uzytkownicy")
def uzytkownicy():
    return [{"id": 1, "imie": "Anna"}, {"id": 2, "imie": "Jan"}]
```

```powershell title="Terminal"
python -m pip install flask
flask --app aplikacja run
```

**FastAPI** (wersja 0.141) buduje na adnotacjach typów z podrozdziału [Adnotacje typów w praktyce](typy-statyczne.md): model danych to klasa Pydantic, a szkielet sam sprawdza poprawność żądań i generuje dokumentację interfejsu pod adresem `/docs`; plik zapisany jako `aplikacja.py`:

```{ .python .no-copy }
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Uzytkownik(BaseModel):
    imie: str
    wiek: int


@app.get("/")
async def strona_glowna():
    return {"wiadomosc": "Witaj!"}


@app.post("/uzytkownicy")
async def dodaj(uzytkownik: Uzytkownik):
    return {"dodano": uzytkownik.imie}
```

```powershell title="Terminal"
python -m pip install "fastapi[standard]"
fastapi dev aplikacja.py
```

Duże aplikacje z panelem administracyjnym, obsługą użytkowników i bazą danych buduje **Django**; bazy danych (`sqlite3`, SQLAlchemy), interfejsy HTTP i pakowanie aplikacji to tematy części „Python Zastosowania”.

## Dane i uczenie maszynowe

Rozdział [14. NumPy i Matplotlib](../14-numpy-matplotlib/index.md) otworzył ścieżkę danych. Kolejne jej etapy: **pandas** (wersja 3.0) — tabele z nazwanymi kolumnami, wczytywanie CSV i Excela, grupowanie i łączenie; **scikit-learn** (1.9) — klasyczne uczenie maszynowe w jednolitym interfejsie `fit()`/`predict()`; **PyTorch** (2.14) — sieci neuronowe; **Jupyter** — notatniki łączące kod, wyniki i tekst, także w VSC. pandas, scikit-learn i notatniki Jupyter są tematem części „Python Zastosowania”; PyTorch wykracza poza jej plan. Narzędzia AI wspierające pisanie kodu omówiliśmy w rozdziale [1. Instalacja i środowisko pracy](../01-instalacja/ai-tools.md).

## Python 3.15

Wydanie 3.15.0 jest planowane na 1 października 2026 roku ([PEP 790](https://peps.python.org/pep-0790/)); w chwili pisania dostępny jest drugi kandydat do wydania. Zmiany, które dotykają treści książki:

- **UTF-8 jako domyślne kodowanie** ([PEP 686](https://peps.python.org/pep-0686/)) — tryb UTF-8 z rozdziału [9. Wejście, wyjście i pliki](../09-wejscie-wyjscie/pliki-tekstowe.md#kodowanie) staje się domyślny; `open()` bez `encoding=` czyta i zapisuje UTF-8 także na Windows.
- **Jawne leniwe importy** ([PEP 810](https://peps.python.org/pep-0810/)) — instrukcja `lazy import` odkłada wczytanie modułu do pierwszego użycia, skracając start programów.
- **Rozpakowanie w złożeniach** ([PEP 798](https://peps.python.org/pep-0798/)) — `[*lista for lista in listy]` spłaszcza listę list bez zagnieżdżonej pętli.
- **Typ `frozendict`** ([PEP 814](https://peps.python.org/pep-0814/)) — niemodyfikowalny słownik — haszowalny, gdy haszowalne są jego wartości — odpowiednik `frozenset` z rozdziału 5.
- **Pakiet `profiling`** ([PEP 799](https://peps.python.org/pep-0799/)) — profiler próbkujący zapowiedziany w rozdziale 13.

Pełną listę zawiera dokument „What's New In Python 3.15” w dokumentacji; nowy interpreter instalujemy managerem z rozdziału 1 poleceniem `py install 3.15`, obok istniejącego.

## Ściągawka narzędzi

| Zadanie | Narzędzia | Rozdział |
|---|---|---|
| interpretery i środowiska | Python Install Manager, `venv`, `python -m pip`, `requirements.txt`; alternatywnie `uv` | 1 |
| edytor | Visual Studio Code z rozszerzeniami Python, Mypy Type Checker, Ruff | 1, 3, 16 |
| diagnostyka | `breakpoint()` i pdb, debugger VSC, `logging` | 8 |
| testy | pytest, pytest-cov; `unittest` z biblioteki standardowej | 7, 16 |
| typy | mypy z rozszerzeniem Mypy Type Checker, pyright (Pylance), Pyrefly, ty | 3, 16 |
| styl | Ruff (linter i formater); black, pylint, autopep8 | 1, 16 |
| automatyzacja | pre-commit, GitHub Actions | 16 |
| wydajność | `timeit`, `cProfile` i `pstats`, `tracemalloc`; `profiling` w 3.15 | 13 |
| dokumentacja | docstringi i `help()`; generatory dokumentacji Sphinx i MkDocs (poza książką) | 6 |
| pakowanie | `pyproject.toml`, instalacja edytowalna | 7 |

## Zasoby i projekty na start

Najlepszym podręcznikiem pozostaje dokumentacja Pythona (docs.python.org) z samouczkiem i opisem biblioteki standardowej; serwis Real Python publikuje przystępne artykuły, a exercism.org oferuje zadania z komentarzem mentora. Z książek: „Fluent Python” (Luciano Ramalho, wyd. 2), „Python Crash Course” (Eric Matthes, wyd. 3), „Effective Python” (Brett Slatkin, wyd. 3) i „Architecture Patterns with Python” (Harry Percival, Bob Gregory).

Umiejętności utrwala własny projekt, doprowadzony do końca i opublikowany w repozytorium z testami i plikiem README. Kilka pomysłów w zasięgu tej książki:

- lista zadań z wiersza poleceń — `argparse`, zapis do JSON (rozdział 9), testy pytest;
- pobieranie i zestawianie danych ze stron WWW — `urllib`, CSV, wykres w Matplotlib;
- rejestr wydatków — zapis w CSV lub JSON (rozdział 9), klasy danych, wykresy miesięczne; w wersji rozszerzonej moduł `sqlite3` z jego dokumentacją;
- narzędzie porządkujące pliki — `pathlib` i `shutil`, dziennik `logging`, wątki dla wielu katalogów;
- prosty interfejs API — FastAPI z tego podrozdziału, modele Pydantic, testy z atrapami.

## Posłowie

Szesnaście rozdziałów prowadziło od instalacji interpretera do narzędzi pracy zespołowej: składnia, typy i kolekcje, funkcje, moduły, wyjątki, pliki, programowanie obiektowe, wydajność, tablice, współbieżność. To zamknięty kurs języka — wystarczający, aby czytać cudzy kod ze zrozumieniem i pisać własny, który można utrzymywać. Część „Python Zastosowania” poświęcamy bibliotekom: ścieżkom danych, uczenia maszynowego, aplikacji i automatyzacji. Niezależnie od wybranej drogi zasada z rozdziału 13 pozostaje w mocy — najpierw kod poprawny i czytelny, potem wszystko inne.
