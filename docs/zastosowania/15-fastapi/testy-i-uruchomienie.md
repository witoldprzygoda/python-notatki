# Testy i uruchomienie

Aplikacja nad bazą ma trzy warstwy: trasy, operacje i model danych. Testy z rozdziału 13 sprawdzały operacje na sesji; teraz sprawdzamy całość przez HTTP — bez serwera, na bazie tworzonej dla każdego testu. Podrozdział zamyka uruchomienie u odbiorcy: opcje serwera, konfiguracja i dziennik.

## Testy z klientem testowym

```python title="tests/conftest.py"
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["SKLEP_BAZA"] = "sqlite://"

from baza import fabryka_sesji, utworz_silnik  # noqa: E402
from dane_przykladowe import wypelnij  # noqa: E402
import sklep_baza  # noqa: E402


@pytest.fixture
def klient(tmp_path):
    Sesja = fabryka_sesji(utworz_silnik(f"sqlite:///{tmp_path / 'test.db'}"))
    with Sesja() as sesja:
        wypelnij(sesja)

    def sesja_testowa():
        with Sesja.begin() as sesja:
            yield sesja

    sklep_baza.app.dependency_overrides[sklep_baza.otworz_sesje] = sesja_testowa
    with TestClient(sklep_baza.app) as klient:
        yield klient
    sklep_baza.app.dependency_overrides.clear()
```

```python title="tests/test_api.py"
def test_lista_produktow_z_filtrem(klient):
    odpowiedz = klient.get("/produkty", params={"kategoria": "książki"})
    assert odpowiedz.status_code == 200
    assert [produkt["nazwa"] for produkt in odpowiedz.json()] == ["Python. Wprowadzenie", "Algorytmy"]


def test_zamowienie_zapisuje_i_zdejmuje_towar(klient):
    odpowiedz = klient.post("/zamowienia", json={"klient_id": 6, "koszyk": [{"produkt_id": 5, "ilosc": 3}], "data": "2025-04-01"})
    assert odpowiedz.status_code == 201
    assert odpowiedz.headers["location"] == "/zamowienia/8"
    assert odpowiedz.json()["pozycje"] == [{"produkt_id": 5, "ilosc": 3, "cena": 79.0}]
    assert klient.get("/produkty/5").json()["stan"] == 17


def test_brak_towaru_nie_zostawia_sladu(klient):
    odpowiedz = klient.post("/zamowienia", json={"klient_id": 1, "koszyk": [{"produkt_id": 1, "ilosc": 1}, {"produkt_id": 4, "ilosc": 1}]})
    assert odpowiedz.status_code == 409
    assert "produkt 4" in odpowiedz.json()["detail"]
    assert klient.get("/produkty/1").json()["stan"] == 12
    assert klient.get("/zamowienia/8").status_code == 404


def test_niepoprawna_tresc_to_422(klient):
    odpowiedz = klient.post("/zamowienia", json={"klient_id": 1, "koszyk": [{"produkt_id": 1, "ilosc": 0}]})
    assert odpowiedz.status_code == 422
    assert odpowiedz.json()["detail"][0]["loc"] == ["body", "koszyk", 0, "ilosc"]


def test_anulowanie_zwraca_towar(klient):
    assert klient.post("/zamowienia/7/anulowanie").json() == {"zwrocono": 2}
    assert klient.get("/zamowienia/7").json()["status"] == "anulowane"
    assert klient.post("/zamowienia/1/anulowanie").status_code == 409


def test_podsumowanie_pomija_anulowane(klient):
    assert klient.get("/klienci/1/podsumowanie").json() == {"zamowien": 2, "wartosc": 515.0}
```

```toml title="pyproject.toml"
[tool.pytest.ini_options]
filterwarnings = ["ignore::DeprecationWarning:starlette.testclient"]
```

```powershell title="Terminal"
python -m pytest -q
```

```{ .text .no-copy }
......                                                                   [100%]
6 passed in 0.25s
```

Fixture buduje bazę w pliku w katalogu tymczasowym `tmp_path` z rozdziału 16 „Python Notatki” i wypełnia ją danymi przykładowymi, a potem **nadpisuje zależność**: słownik `app.dependency_overrides` każe FastAPI wywoływać `sesja_testowa` wszędzie tam, gdzie trasa żąda `otworz_sesje`. Aplikacja nie wie, że działa na innej bazie — ta sama zasada, według której w rozdziale 14 atrapa transportu podmieniała sieć. Baza w pliku, nie w pamięci: `sqlite://` istnieje tylko w obrębie jednego połączenia, a FastAPI wykonuje zależność w wątku z puli — z innym połączeniem niż to, w którym fixture wypełniła dane. Zmienna `SKLEP_BAZA` ustawiona przed importem sprawia, że cykl życia aplikacji nie tworzy pliku bazy w katalogu projektu. Testy sprawdzają umowę interfejsu: kody, nagłówek `Location`, kształt JSON-a i skutki w bazie widoczne przez kolejne żądania. Plik `pyproject.toml` wycisza ostrzeżenie o wycofaniu, które moduł klienta testowego Starlette zgłasza w tej wersji przy imporcie — pochodzi z biblioteki, nie z naszego kodu, a filtr wskazuje moduł, więc inne ostrzeżenia pozostają widoczne.

## Uruchomienie u odbiorcy

```powershell title="Terminal"
$env:SKLEP_BAZA = "sqlite:///C:\dane\sklep.db"
python -m uvicorn sklep_baza:app --host 0.0.0.0 --port 8000 --workers 2
```

| Opcja | Znaczenie |
|---|---|
| `--host 0.0.0.0` | nasłuch na wszystkich interfejsach — serwer widoczny z innych komputerów; domyślnie `127.0.0.1` |
| `--port 8000` | port; wartość `0` wybiera wolny |
| `--workers 2` | liczba **procesów roboczych** (ang. *worker*), każdy z własną kopią aplikacji |
| `--reload` | przeładowanie po zmianie plików; tylko przy pisaniu |
| `--log-level warning` | mniej wpisów w dzienniku; domyślnie `info` z każdym żądaniem |

Konfigurację przekazujemy zmiennymi środowiskowymi, jak adres bazy w rozdziale 13 i klucz API w rozdziale 14 — kod nie zmienia się między maszyną programisty a odbiorcą, a wartości nie trafiają do repozytorium. Wiersz dziennika uvicorn dla każdego żądania — adres klienta, linia żądania, kod — jest pierwszym narzędziem diagnostyki; własne wpisy dodajemy modułem `logging` z rozdziału 8 „Python Notatki”. Kilka procesów roboczych zwielokrotnia przepustowość, ale wymaga, by stan aplikacji był w bazie, nie w słowniku modułu — sklep w pamięci ze strony trzeciej działałby w każdym procesie osobno. Serwer dostępny z internetu umieszczamy za serwerem pośredniczącym (ang. *reverse proxy*), który obsługuje HTTPS i ogranicza ruch; uvicorn przyjmuje wprawdzie certyfikat opcjami `--ssl-keyfile` i `--ssl-certfile`, ale nie odnawia go ani nie ogranicza ruchu.

## Lista kontrolna

- **Adnotacje typów** w każdej trasie; ograniczenia w `Query()` i `Field()`, nie w `if`.
- **Modele Pydantic** dla treści żądania i odpowiedzi; `response_model` ucina to, czego klient nie ma widzieć.
- **Kody i kształt błędów** jednakowe w całym interfejsie; własne wyjątki tłumaczone w jednym miejscu.
- **Zależności** dla tego, co wspólne: klucz, sesja bazy, bieżący użytkownik.
- **Cykl życia** dla zasobów tworzonych raz: silnik bazy, model, klient cudzego API.
- **Testy** przez `TestClient` z nadpisaniem zależności; baza w pliku tymczasowym.
- **Konfiguracja** w zmiennych środowiskowych; `--reload` tylko w rozwoju; stan w bazie, gdy procesów jest więcej niż jeden.

## Dalej: okno, pakiet i projekt

Sklep ma bazę i API; użytkownik, który nie pisze programów, potrzebuje okna — [interfejs graficzny w bibliotece tkinter](../16-tkinter/index.md) jest tematem następnego rozdziału. Aplikację trzeba też dostarczyć odbiorcy jako pakiet z zależnościami i poleceniem uruchamiającym <!-- TODO: link po powstaniu rozdziału o pakowaniu i dystrybucji -->, a projekt ścieżki połączy bazę, API i okno w jeden program <!-- TODO: link po powstaniu rozdziału o projekcie aplikacji -->.
