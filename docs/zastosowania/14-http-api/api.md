# Interfejs API w praktyce

Serwer sklepu i klient httpx działają; zostaje uporządkować, co czyni interfejs dobrym, i zamknąć wywołania w module, z którego reszta programu korzysta jak ze zwykłych funkcji — z własnymi wyjątkami, ponawianiem po chwilowych błędach i testami, które nie potrzebują sieci.

## Zasady REST

Interfejs sklepu trzyma się konwencji **REST** (ang. *representational state transfer*), której przestrzega większość współczesnych API: interfejs składa się z **zasobów** (ang. *resource*) o stałych adresach, a działania wyrażają metody HTTP i kody stanu, nie nazwy w adresie. Dwa ostatnie wiersze tabeli to konwencja, której serwer sklepu nie implementuje.

| Działanie | Metoda i adres | Odpowiedź |
|---|---|---|
| lista produktów, z filtrem | `GET /produkty?kategoria=książki` | `200` i lista JSON |
| jeden produkt | `GET /produkty/3` | `200` i obiekt; `404`, gdy nie ma |
| złożenie zamówienia | `POST /zamowienia` z JSON | `201`, obiekt i `Location`; `401`, `400`, `422`, `404`, `409` |
| zmiana zamówienia | `PATCH /zamowienia/7` | `200` i obiekt po zmianie |
| usunięcie | `DELETE /zamowienia/7` | `204` bez treści |

Adresy nazywają rzeczy w liczbie mnogiej (`/produkty`, `/produkty/3`), nie czynności (`/pobierzProdukt`); parametry zapytania filtrują i stronicują listę (`?strona=2&na_stronie=50`), a każda odpowiedź z treścią — także błąd — jest JSON-em o przewidywalnym kształcie. Interfejs publiczny dostaje wersję w adresie (`/v1/produkty`), by zmiany nie psuły istniejących klientów, i dokumentację adresów, parametrów i kodów; FastAPI w rozdziale 15 generuje ją z kodu. Tych zasad nie wymusza protokół — to umowa, która sprawia, że klient napisany dla jednego API wygląda jak klient dla innego.

## Moduł klienta API

```python title="sklep_api.py"
"""Klient interfejsu sklepu: metody zamiast adresów, wyjątki zamiast kodów stanu, ponawianie po 503."""

import os
import time

import httpx

PROBY = 3


class BladApi(Exception):
    def __init__(self, status, komunikat):
        super().__init__(f"{status}: {komunikat}")
        self.status = status
        self.komunikat = komunikat


class KlientSklepu:
    def __init__(self, adres, klucz=None, transport=None):
        klucz = klucz or os.environ.get("SKLEP_KLUCZ")
        naglowki = {"Authorization": f"Bearer {klucz}"} if klucz else {}
        self._klient = httpx.Client(base_url=adres, headers=naglowki, timeout=5.0, transport=transport)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._klient.close()

    def _zapytaj(self, metoda, sciezka, **argumenty):
        for proba in range(1, PROBY + 1):
            odpowiedz = self._klient.request(metoda, sciezka, **argumenty)
            if odpowiedz.status_code != 503 or proba == PROBY:
                break
            time.sleep(float(odpowiedz.headers.get("retry-after", 1)))
        if odpowiedz.is_error:
            komunikat = odpowiedz.json().get("blad", odpowiedz.reason_phrase) if odpowiedz.headers.get("content-type", "").startswith("application/json") else odpowiedz.reason_phrase
            raise BladApi(odpowiedz.status_code, komunikat)
        return odpowiedz.json()

    def produkty(self, kategoria=None):
        return self._zapytaj("GET", "/produkty", params={"kategoria": kategoria} if kategoria else None)

    def produkt(self, numer):
        return self._zapytaj("GET", f"/produkty/{numer}")

    def zloz_zamowienie(self, produkt_id, ilosc):
        return self._zapytaj("POST", "/zamowienia", json={"produkt_id": produkt_id, "ilosc": ilosc})

    def niestabilne(self):
        return self._zapytaj("GET", "/niestabilny")
```

```python title="uzycie.py"
from sklep_api import BladApi, KlientSklepu
from sklep_serwer import uruchom

serwer = uruchom()
with KlientSklepu("http://127.0.0.1:8765", klucz="tajny-klucz") as sklep:
    print([produkt["nazwa"] for produkt in sklep.produkty(kategoria="książki")])
    print(sklep.zloz_zamowienie(3, 2))
    for produkt_id, ilosc in ((9, 1), (3, 50), (1, 0)):
        try:
            sklep.zloz_zamowienie(produkt_id, ilosc)
        except BladApi as blad:
            print(blad, "|", blad.status, blad.komunikat)
    print(sklep.niestabilne())
with KlientSklepu("http://127.0.0.1:8765") as bez_klucza:
    try:
        bez_klucza.zloz_zamowienie(1, 1)
    except BladApi as blad:
        print(blad)
serwer.shutdown()
```

```{ .text .no-copy }
['Python. Wprowadzenie', 'Algorytmy']
{'id': 1, 'produkt_id': 3, 'ilosc': 2, 'wartosc': 498.0}
404: nie ma produktu 9 | 404 nie ma produktu 9
409: dostępne sztuk: 6 | 409 dostępne sztuk: 6
422: wymagane pola: produkt_id (liczba), ilosc (liczba >= 1) | 422 wymagane pola: produkt_id (liczba), ilosc (liczba >= 1)
{'proba': 3}
401: brak lub zły klucz
```

Klasa opakowuje `httpx.Client` i tłumaczy interfejs sieciowy na interfejs Pythona: reszta programu wywołuje `zloz_zamowienie(3, 2)` i dostaje słownik albo wyjątek `BladApi` z kodem i komunikatem serwera — nie zna adresów, nagłówków ani JSON-a; błędy sieci (`RequestError`) przechodzą bez zmian. Klucz pochodzi z argumentu albo zmiennej środowiskowej `SKLEP_KLUCZ`, jak adres bazy w rozdziale 13; bez niego serwer odpowiada `401`, co również dociera jako wyjątek. Jedna metoda prywatna `_zapytaj()` skupia wspólną logikę: **ponawianie** (ang. *retry*) żądania, gdy serwer odpowie `503`, z odczekaniem podanym w `Retry-After` — trasa `/niestabilny` odpowiada dopiero za trzecim razem — oraz zamianę kodów błędu na wyjątek z komunikatem z JSON-a, jeśli serwer go podał, a w przeciwnym razie z opisem kodu stanu. Ponawiamy tylko odpowiedzi `503` i najwyżej w trzech próbach łącznie (`PROBY`): `POST` powtórzony po zerwanym połączeniu mógłby złożyć zamówienie dwukrotnie, a nieskończone ponawianie pogłębia przeciążenie serwera. Blok `with` zamyka połączenia, jak w kliencie httpx.

## Testy z atrapą transportu

```python title="tests/conftest.py"
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
```

```python title="tests/test_sklep_api.py"
import httpx
import pytest

from sklep_api import BladApi, KlientSklepu

ODPOWIEDZI = {"licznik": 0}


def atrapa(zadanie):
    if zadanie.url.path == "/produkty/1":
        return httpx.Response(200, json={"id": 1, "nazwa": "Testowy", "cena": 10.0, "stan": 4})
    if zadanie.url.path == "/zamowienia" and zadanie.method == "POST":
        if zadanie.headers.get("Authorization") != "Bearer klucz-testowy":
            return httpx.Response(401, json={"blad": "brak lub zły klucz"})
        return httpx.Response(201, json={"id": 1, "ilosc": 2}, headers={"Location": "/zamowienia/1"})
    if zadanie.url.path == "/niestabilny":
        ODPOWIEDZI["licznik"] += 1
        if ODPOWIEDZI["licznik"] < 3:
            return httpx.Response(503, json={"blad": "chwilowo"}, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"proba": ODPOWIEDZI["licznik"]})
    return httpx.Response(404, json={"blad": "nie ma"})


@pytest.fixture
def sklep():
    with KlientSklepu("http://test", klucz="klucz-testowy", transport=httpx.MockTransport(atrapa)) as klient:
        yield klient


def test_produkt_zwraca_slownik(sklep):
    assert sklep.produkt(1)["nazwa"] == "Testowy"


def test_brak_produktu_to_wyjatek_z_kodem(sklep):
    with pytest.raises(BladApi, match="404: nie ma") as informacja:
        sklep.produkt(9)
    assert informacja.value.status == 404


def test_zamowienie_wysyla_klucz(sklep):
    assert sklep.zloz_zamowienie(1, 2) == {"id": 1, "ilosc": 2}


def test_zly_klucz_401():
    with KlientSklepu("http://test", klucz="zly", transport=httpx.MockTransport(atrapa)) as sklep:
        with pytest.raises(BladApi) as informacja:
            sklep.zloz_zamowienie(1, 2)
    assert informacja.value.status == 401


def test_ponawia_po_503(sklep):
    ODPOWIEDZI["licznik"] = 0
    assert sklep.niestabilne() == {"proba": 3}
```

```powershell title="Terminal"
python -m pytest -q
```

```{ .text .no-copy }
.....                                                                    [100%]
5 passed in 0.06s
```

`httpx.MockTransport` podstawia w miejsce sieci funkcję, która dostaje obiekt żądania i zwraca odpowiedź — **atrapę** (ang. *mock*) z rozdziału 16 „Python Notatki”, tyle że na poziomie transportu, więc cały kod klienta łącznie z httpx wykonuje się naprawdę. Testy sprawdzają to, co w module jest decyzją: tłumaczenie kodów na wyjątki, wysyłanie klucza, ponawianie po `503` (atrapa zwraca `Retry-After: 0`, więc test nie czeka). Nie sprawdzają serwera — od tego są testy serwera — i nie zależą od sieci, więc działają w każdym środowisku; jeden test przeciw prawdziwemu serwerowi, jak `uzycie.py`, uzupełnia je jako test integracyjny.

## Klucze, limity i konfiguracja

Klucz API identyfikuje program i bywa odpłatny — nigdy nie trafia do kodu ani do repozytorium, tylko do zmiennej środowiskowej albo pliku wyłączonego z repozytorium przez `.gitignore` z rozdziału 16 „Python Notatki”, a program czyta go przy starcie; klucz wysyłamy wyłącznie przez `https`, bo w `http` nagłówki idą jawnym tekstem. Usługi ograniczają liczbę żądań w czasie: kod `429` z `Retry-After` oznacza, że trzeba zwolnić, a odpowiedzi warto zapisywać lokalnie, zamiast pytać o to samo w pętli. Każde żądanie ma limit czasu, a ponawiane są tylko żądania idempotentne albo takie, o których wiemy, że serwer nie zaczął ich wykonywać (`503`). Do konfiguracji należą też adres bazowy (inny w testach, inny u odbiorcy) i `User-Agent` z nazwą programu — dobre obyczaje wobec cudzej usługi.

## Lista kontrolna klienta i interfejsu

- **Limit czasu** w każdym żądaniu; `RequestError` i `HTTPStatusError` obsłużone osobno.
- **Kod stanu sprawdzony przed `json()`**; błąd serwera ma komunikat w JSON, który trafia do wyjątku.
- **Klucz** ze środowiska, przez `https`, nigdy w repozytorium; adres bazowy w konfiguracji.
- **Ponawianie** tylko po `503`/`429` albo dla żądań idempotentnych, z `Retry-After` i górnym limitem prób.
- **Duże odpowiedzi** strumieniowo, do pliku.
- **Testy** z `MockTransport` dla logiki klienta; jeden test integracyjny przeciw serwerowi.
- **Serwer**: zasoby w adresach, metody i kody według REST, odpowiedzi błędów w JSON, `Location` po `201`, walidacja przed zmianą stanu.

## Dalej: FastAPI

Serwer w `http.server` pokazał każdy element interfejsu, ale każdy trzeba było napisać ręcznie: rozbiór ścieżki, dekodowanie JSON-a, walidację pól, kody błędów. [Framework FastAPI](../15-fastapi/index.md) z następnego rozdziału robi to z definicji funkcji i typów, generuje dokumentację interfejsu i pozwala podłączyć warstwę danych z rozdziału 13 — z sesją na każde żądanie; [projekt ścieżki](../18-projekt-aplikacja/index.md) połączy bazę, API i okno aplikacji. Klient httpx przyda się jeszcze w ścieżce automatyzacji, przy [pobieraniu stron](../21-scraping/index.md).
