# Testy, uruchomienie i dostawa

Trzy warstwy to trzy poziomy testów: operacje na bazie sprawdził rozdział 13, usługę przez klienta testowego — rozdział 15; tu testy usługi wracają w pakiecie, a dochodzą klient API z atrapą transportu i koszyk. Potem uruchamiamy całość z dwóch poleceń i pakujemy okno dla użytkownika.

## Testy

```python title="tests/conftest.py"
import os

import pytest
from fastapi.testclient import TestClient

os.environ["SKLEP_BAZA"] = "sqlite://"

from sklep import api  # noqa: E402
from sklep.baza import fabryka_sesji, utworz_silnik  # noqa: E402
from sklep.dane_przykladowe import wypelnij  # noqa: E402


@pytest.fixture
def klient(tmp_path):
    Sesja = fabryka_sesji(utworz_silnik(f"sqlite:///{tmp_path / 'test.db'}"))
    with Sesja() as sesja:
        wypelnij(sesja)

    def sesja_testowa():
        with Sesja.begin() as sesja:
            yield sesja

    api.app.dependency_overrides[api.otworz_sesje] = sesja_testowa
    with TestClient(api.app) as klient:
        yield klient
    api.app.dependency_overrides.clear()
```

```python title="tests/test_api.py"
def test_lista_klientow(klient):
    assert [k["nazwisko"] for k in klient.get("/klienci").json()][:2] == ["Nowak", "Kowalska"]


def test_zamowienie_zdejmuje_towar(klient):
    odpowiedz = klient.post("/zamowienia", json={"klient_id": 6, "koszyk": [{"produkt_id": 5, "ilosc": 3}], "data": "2025-04-01"})
    assert odpowiedz.status_code == 201
    assert klient.get("/produkty/5").json()["stan"] == 17
    assert klient.get("/klienci/6/podsumowanie").json() == {"zamowien": 1, "wartosc": 237.0}


def test_brak_towaru_to_409(klient):
    odpowiedz = klient.post("/zamowienia", json={"klient_id": 1, "koszyk": [{"produkt_id": 4, "ilosc": 1}]})
    assert odpowiedz.status_code == 409
    assert "produkt 4" in odpowiedz.json()["detail"]


def test_nieznany_klient_to_404(klient):
    assert klient.get("/klienci/99/podsumowanie").status_code == 404
```

```python title="tests/test_klient.py"
import httpx
import pytest

from sklep.klient import BladApi, KlientSklepu


def atrapa(zadanie):
    if zadanie.url.path == "/produkty":
        return httpx.Response(200, json=[{"id": 1, "nazwa": "Algorytmy", "kategoria": "książki", "cena": 89.0, "stan": 5}])
    if zadanie.method == "POST":
        return httpx.Response(409, json={"detail": "produkt 4: zamówiono 1, dostępne 0"})
    return httpx.Response(422, json={"detail": [{"loc": ["path", "klient_id"], "msg": "błąd"}]})


@pytest.fixture
def sklep():
    with KlientSklepu("http://test", transport=httpx.MockTransport(atrapa)) as klient:
        yield klient


def test_produkty_zwracaja_liste(sklep):
    assert sklep.produkty()[0]["nazwa"] == "Algorytmy"


def test_blad_serwera_to_wyjatek_z_komunikatem(sklep):
    with pytest.raises(BladApi) as informacja:
        sklep.zloz_zamowienie(1, [(4, 1)])
    assert (informacja.value.status, informacja.value.komunikat) == (409, "produkt 4: zamówiono 1, dostępne 0")


def test_blad_walidacji_ma_komunikat_ogolny(sklep):
    with pytest.raises(BladApi, match="422: niepoprawne dane"):
        sklep.podsumowanie("x")
```

```python title="tests/test_koszyk.py"
import pytest

from sklep.koszyk import Koszyk

PRODUKTY = {1: {"cena": 59.0}, 5: {"cena": 79.0}}


def test_koszyk_sumuje_sztuki_i_liczy_wartosc():
    koszyk = Koszyk()
    koszyk.dodaj(1, 2)
    koszyk.dodaj(5, 1)
    koszyk.dodaj(1, 1)
    assert koszyk.pozycje() == [(1, 3), (5, 1)]
    assert koszyk.wartosc(PRODUKTY) == 256.0


def test_koszyk_odrzuca_zla_ilosc_i_czysci_sie():
    koszyk = Koszyk()
    with pytest.raises(ValueError):
        koszyk.dodaj(1, 0)
    koszyk.dodaj(1, 1)
    koszyk.usun(1)
    assert koszyk.pozycje() == [] and koszyk.wartosc(PRODUKTY) == 0
```

```powershell title="Terminal"
python -m pip install -e ".[test]"
python -m pytest -q
```

```{ .text .no-copy }
.........                                                                [100%]
9 passed in 0.25s
```

Fixture usługi to ta z rozdziału 15 — baza w pliku tymczasowym, nadpisana zależność sesji i `SKLEP_BAZA` ustawiona na bazę w pamięci przed importem, żeby cykl życia nie tworzył pliku `sklep.db` w katalogu projektu — z jedną zmianą: importy z zainstalowanego pakietu zamiast wpisu w `sys.path`, jak w rozdziale 17. Testy klienta nie potrzebują serwera: atrapa transportu z rozdziału 14 odpowiada według ścieżki i metody, a testy sprawdzają obie strony tłumaczenia — dane po sukcesie, `BladApi` z komunikatem serwera po `409` i komunikat ogólny po `422`. Koszyk testujemy jak zwykłą klasę. Testów okna nie ma: jego logika jest w koszyku i kliencie, a złożenie całości sprawdza skrypt kontrolny z poprzedniej strony.

## Uruchomienie

```powershell title="Terminal"
$env:SKLEP_PORT = "8010"
sklep-serwer
```

```{ .text .no-copy }
INFO:     Started server process [11960]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8010 (Press CTRL+C to quit)
```

```powershell title="Terminal"
$env:SKLEP_ADRES = "http://127.0.0.1:8010"
sklep
```

Pierwsze polecenie uruchamia usługę nad plikiem `sklep.db` w katalogu bieżącym (przy pierwszym starcie z danymi przykładowymi) i zostaje w terminalu, wypisując dziennik żądań; dokumentacja interfejsu jest pod adresem usługi z dopiskiem `/docs`. Port domyślny to 8000; gdy zajmuje go inny program, zmienna `SKLEP_PORT` wskazuje inny — tu 8010. Drugie polecenie, w osobnym terminalu, otwiera okno; `SKLEP_ADRES` jest potrzebna tylko wtedy, gdy usługa działa gdzie indziej niż domyślnie — jak tutaj. Serwer można uruchomić na innej maszynie: `SKLEP_HOST=0.0.0.0` udostępnia go w sieci lokalnej, a w oknie u użytkownika wystarczy zmienić `SKLEP_ADRES`; ruch z internetu wymaga serwera pośredniczącego z HTTPS, jak w rozdziale 15.

## Dostawa

```python title="uruchom_okno.py"
from sklep.okno import main

if __name__ == "__main__":
    main()
```

```python title="zbuduj-okno.py"
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

os.environ["SKLEP_BAZA"] = "sqlite:///sklep-proba.db"
Path("sklep-proba.db").unlink(missing_ok=True)

import uvicorn  # noqa: E402

from sklep.api import app  # noqa: E402

polecenie = [sys.executable, "-m", "PyInstaller", "--onefile", "--windowed", "--name", "Sklep", "--paths", "src", "--noconfirm", "--log-level", "WARN", "uruchom_okno.py"]
budowanie = subprocess.run(polecenie, capture_output=True, text=True, encoding="utf-8")
plik = Path("dist/Sklep.exe")
print("PyInstaller:", budowanie.returncode, "|", plik.name, f"{plik.stat().st_size / 1e6:.0f} MB")

serwer = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8765, log_level="warning"))
threading.Thread(target=serwer.run, daemon=True).start()
while not serwer.started:
    time.sleep(0.05)
srodowisko = {**os.environ, "SKLEP_ADRES": "http://127.0.0.1:8765"}
print("uruchomienie okna:", subprocess.run([str(plik), "--zamknij-po", "2000"], env=srodowisko).returncode)
serwer.should_exit = True
```

```{ .text .no-copy }
PyInstaller: 0 | Sklep.exe 25 MB
uruchomienie okna: 0
```

```markdown title="README.md"
# sklep

Sklep z trzech warstw: baza SQLite (SQLAlchemy), usługa HTTP (FastAPI) i okno klienta (CustomTkinter).

## Instalacja i uruchomienie

    python -m pip install sklep-1.0.0-py3-none-any.whl
    sklep-serwer            # usługa na http://127.0.0.1:8000, dokumentacja pod /docs
    sklep                   # okno klienta (w drugim terminalu)

Zmienne środowiskowe: `SKLEP_BAZA` (adres bazy, domyślnie `sqlite:///sklep.db`),
`SKLEP_HOST` i `SKLEP_PORT` (serwer), `SKLEP_ADRES` (adres usługi dla okna).

## Rozwój

    python -m pip install -e ".[test]"
    python -m pytest -q
    python -m build
```

Dostawa ma dwie postacie, jak w rozdziale 17. Koło z `python -m build` daje pakiet z zależnościami i oboma poleceniami każdemu, kto ma Pythona — to postać dla serwera i dla administratora. Plik `Sklep.exe` z PyInstallera to okno dla użytkownika bez Pythona; PyInstaller ma gotowe reguły dla CustomTkinter, więc jego zasoby trafiają do pliku bez dodatkowych opcji, a `--paths src` wskazuje pakiet. Skrypt kontrolny buduje plik, uruchamia usługę w wątku i otwiera zbudowane okno ze zmienną `SKLEP_ADRES` wskazującą tę usługę — kod wyjścia `0` oznacza, że okno otworzyło się i zamknęło bez wyjątku; błąd połączenia trafiłby na pasek stanu, nie do kodu wyjścia. README opisuje obie drogi; wersję pakietu widać w tytule okna i w dokumentacji usługi.

## Lista kontrolna ścieżki

- **Warstwa danych** (13): model z ograniczeniami, operacje w transakcjach, adres bazy w konfiguracji, testy na bazie tymczasowej.
- **Umowa interfejsu** (14): zasoby i kody REST, klient z własnymi wyjątkami, ponawianie tam, gdzie bezpieczne, klucze poza kodem.
- **Usługa** (15): modele Pydantic, zależności dla sesji i uwierzytelnienia, cykl życia dla zasobów, konfiguracja w zmiennych środowiskowych, `TestClient` z nadpisaniem zależności.
- **Okno** (16): logika poza widżetami, długie operacje w wątku z kolejką i `after()`, komunikaty zamiast wyjątków.
- **Pakiet** (17): `pyproject.toml` z zakresami zależności i punktami wejścia, testy bez `sys.path`, koło dla odbiorców z Pythonem, plik wykonywalny dla użytkowników bez niego, budowanie sprawdzone uruchomieniem z `--zamknij-po`.

## Dalej: ścieżka Automatyzacja

Aplikacja jest gotowa; następna ścieżka odchodzi od budowania programów dla użytkowników na rzecz programów, które wykonują pracę za nas: wyszukują wzorce w tekście, obsługują wiersz poleceń, pobierają strony, czytają i piszą pliki pakietu Office i obrazy. Zaczyna się od [wyrażeń regularnych](../19-re/index.md).
