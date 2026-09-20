# Serwer sklepu

Serwer sklepu z rozdziału 14 miał listę produktów, zamówienia chronione kluczem, raport CSV i dwie trasy pomocnicze. Ten podrozdział przepisuje go w FastAPI z zachowaniem interfejsu — adresów, kodów i kształtu błędów — tak, by klient `sklep_api.py` z tamtego rozdziału działał bez żadnej zmiany.

## Trasy w routerach i własne błędy

```python title="sklep_fastapi.py"
"""Sklep z rozdziału 14 w FastAPI: trasy w routerach, własne błędy, klucz jako zależność."""

import time
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

KLUCZ = "tajny-klucz"
PRODUKTY = {
    1: {"id": 1, "nazwa": "Python. Wprowadzenie", "kategoria": "książki", "cena": 59.0, "stan": 12},
    2: {"id": 2, "nazwa": "Algorytmy", "kategoria": "książki", "cena": 89.0, "stan": 5},
    3: {"id": 3, "nazwa": "Słuchawki", "kategoria": "elektronika", "cena": 249.0, "stan": 8},
}
ZAMOWIENIA = {}
LICZNIK = {"niestabilny": 0}


class BladSklepu(Exception):
    def __init__(self, status, komunikat):
        self.status = status
        self.komunikat = komunikat


class NoweZamowienie(BaseModel):
    produkt_id: int
    ilosc: int = Field(ge=1)


class Zamowienie(NoweZamowienie):
    id: int
    wartosc: float


def wymagaj_klucza(authorization: Annotated[str | None, Header()] = None):
    if authorization != f"Bearer {KLUCZ}":
        raise BladSklepu(401, "brak lub zły klucz")


produkty = APIRouter(prefix="/produkty", tags=["produkty"])
zamowienia = APIRouter(prefix="/zamowienia", tags=["zamówienia"], dependencies=[Depends(wymagaj_klucza)])


@produkty.get("")
def lista(kategoria: str | None = None):
    return [produkt for produkt in PRODUKTY.values() if kategoria is None or produkt["kategoria"] == kategoria]


@produkty.get("/{produkt_id}")
def produkt(produkt_id: int):
    if produkt_id not in PRODUKTY:
        raise BladSklepu(404, f"nie ma produktu {produkt_id}")
    return PRODUKTY[produkt_id]


@zamowienia.post("", status_code=201, response_model=Zamowienie)
def zloz(nowe: NoweZamowienie, response: Response):
    produkt = PRODUKTY.get(nowe.produkt_id)
    if produkt is None:
        raise BladSklepu(404, f"nie ma produktu {nowe.produkt_id}")
    if produkt["stan"] < nowe.ilosc:
        raise BladSklepu(409, f"dostępne sztuk: {produkt['stan']}")
    produkt["stan"] -= nowe.ilosc
    zamowienie = Zamowienie(id=len(ZAMOWIENIA) + 1, wartosc=nowe.ilosc * produkt["cena"], **nowe.model_dump())
    ZAMOWIENIA[zamowienie.id] = zamowienie
    response.headers["Location"] = f"/zamowienia/{zamowienie.id}"
    return zamowienie


@zamowienia.get("/{zamowienie_id}", response_model=Zamowienie)
def zamowienie(zamowienie_id: int):
    if zamowienie_id not in ZAMOWIENIA:
        raise BladSklepu(404, f"nie ma zamówienia {zamowienie_id}")
    return ZAMOWIENIA[zamowienie_id]


app = FastAPI(title="Sklep", version="2.0")
app.include_router(produkty)
app.include_router(zamowienia)


@app.exception_handler(BladSklepu)
def obsluz_blad_sklepu(request: Request, blad: BladSklepu):
    return JSONResponse(status_code=blad.status, content={"blad": blad.komunikat})


@app.exception_handler(RequestValidationError)
def obsluz_walidacje(request: Request, blad: RequestValidationError):
    return JSONResponse(status_code=422, content={"blad": "niepoprawne dane", "szczegoly": jsonable_encoder(blad.errors())})


@app.get("/raport.csv")
def raport():
    wiersze = ["id;nazwa;cena"] + [f"{p['id']};{p['nazwa']};{p['cena']}" for p in PRODUKTY.values()]
    return Response("\n".join(wiersze) + "\n", media_type="text/csv; charset=utf-8")


@app.get("/wolny")
def wolny():
    time.sleep(2)
    return {"gotowe": True}


@app.get("/niestabilny")
def niestabilny():
    LICZNIK["niestabilny"] += 1
    if LICZNIK["niestabilny"] < 3:
        return JSONResponse(status_code=503, content={"blad": "chwilowo niedostępne"}, headers={"Retry-After": "1"})
    return {"proba": LICZNIK["niestabilny"]}
```

Trasy jednego zasobu grupuje **router** `APIRouter` z przedrostkiem adresu i etykietą w dokumentacji — pusta ścieżka `""` daje adres równy przedrostkowi, `"/"` dałaby `/produkty/`; aplikacja włącza routery przez `include_router()`, a w większym projekcie każdy router jest osobnym modułem. Klucz API sprawdza **zależność** (ang. *dependency*): funkcja, którą FastAPI wywołuje przed funkcją obsługi i której parametry rozwiązuje tak samo jak parametry trasy — `Header()` wiąże argument `authorization` z nagłówkiem `Authorization`. Zależność podana w `dependencies=` routera obowiązuje wszystkie jego trasy; to **wstrzykiwanie zależności** (ang. *dependency injection*), które na następnej stronie dostarczy sesję bazy. Własny wyjątek `BladSklepu` niesie kod i komunikat, a procedura zarejestrowana dekoratorem `@app.exception_handler` zamienia go w odpowiedź o kształcie z rozdziału 14: `{"blad": …}`. Druga procedura przechwytuje błędy walidacji FastAPI (`RequestValidationError`) i nadaje im ten sam kształt, dodając szczegóły — `jsonable_encoder()` zamienia listę błędów na typy JSON. Odpowiedzi inne niż JSON budujemy wprost: `Response` z treścią i typem dla CSV, `JSONResponse` z kodem i nagłówkami dla `503`.

## Żądania do sklepu

```python title="zamowienia-sklep.py"
from fastapi.testclient import TestClient

from sklep_fastapi import app

klient = TestClient(app)
odpowiedz = klient.post("/zamowienia", json={"produkt_id": 1, "ilosc": 2})
print(odpowiedz.status_code, odpowiedz.json())
naglowki = {"Authorization": "Bearer tajny-klucz"}
odpowiedz = klient.post("/zamowienia", json={"produkt_id": 1, "ilosc": 2}, headers=naglowki)
print(odpowiedz.status_code, odpowiedz.headers["location"], odpowiedz.json())
for tresc in ({"produkt_id": 9, "ilosc": 1}, {"produkt_id": 2, "ilosc": 50}, {"produkt_id": 1}):
    odpowiedz = klient.post("/zamowienia", json=tresc, headers=naglowki)
    print(odpowiedz.status_code, odpowiedz.json())
print(klient.get("/zamowienia/1", headers=naglowki).json(), klient.get("/produkty/1").json()["stan"])
for _ in range(3):
    odpowiedz = klient.get("/niestabilny")
    print(odpowiedz.status_code, odpowiedz.headers.get("retry-after"), odpowiedz.json())
odpowiedz = klient.get("/raport.csv")
print(odpowiedz.headers["content-type"], odpowiedz.text.splitlines()[:2])
print(list(klient.get("/openapi.json").json()["paths"]))
```

```{ .text .no-copy }
401 {'blad': 'brak lub zły klucz'}
201 /zamowienia/1 {'produkt_id': 1, 'ilosc': 2, 'id': 1, 'wartosc': 118.0}
404 {'blad': 'nie ma produktu 9'}
409 {'blad': 'dostępne sztuk: 5'}
422 {'blad': 'niepoprawne dane', 'szczegoly': [{'type': 'missing', 'loc': ['body', 'ilosc'], 'msg': 'Field required', 'input': {'produkt_id': 1}}]}
{'produkt_id': 1, 'ilosc': 2, 'id': 1, 'wartosc': 118.0} 10
503 1 {'blad': 'chwilowo niedostępne'}
503 1 {'blad': 'chwilowo niedostępne'}
200 None {'proba': 3}
text/csv; charset=utf-8 ['id;nazwa;cena', '1;Python. Wprowadzenie;59.0']
['/produkty', '/produkty/{produkt_id}', '/zamowienia', '/zamowienia/{zamowienie_id}', '/raport.csv', '/wolny', '/niestabilny']
```

Kolejność sprawdzeń jest jak w rozdziale 14 — klucz, treść, produkt, stan — ale tylko dwa ostatnie napisaliśmy sami: klucz sprawdza zależność, a treść model. Dwie różnice klientowi nie szkodzą: treść niebędącą JSON-em FastAPI odrzuca kodem `422` (nie `400`) jeszcze przed zależnościami, a `404` i `405` dla nieznanych adresów zachowują kształt `detail` — klient bez pola `blad` bierze opis kodu. Błędy walidacji mają teraz pole `blad` i listę `szczegoly`, więc klient, który zna tylko `blad`, nadal ma komunikat. Lista adresów z opisu OpenAPI potwierdza, co zbudowały routery.

## Klient z rozdziału 14

```python title="klient14.py"
import threading
import time

import uvicorn

from sklep_api import BladApi, KlientSklepu
from sklep_fastapi import app

serwer = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8765, log_level="warning"))
threading.Thread(target=serwer.run, daemon=True).start()
while not serwer.started:
    time.sleep(0.05)

with KlientSklepu("http://127.0.0.1:8765", klucz="tajny-klucz") as sklep:
    print([produkt["nazwa"] for produkt in sklep.produkty("książki")])
    print(sklep.zloz_zamowienie(3, 1))
    for wywolanie in (lambda: sklep.produkt(9), lambda: sklep.zloz_zamowienie(2, 50), lambda: sklep.zloz_zamowienie(1, 0)):
        try:
            wywolanie()
        except BladApi as blad:
            print(blad.status, blad.komunikat)
    print(sklep.niestabilne())
serwer.should_exit = True
```

```{ .text .no-copy }
['Python. Wprowadzenie', 'Algorytmy']
{'produkt_id': 3, 'ilosc': 1, 'id': 1, 'wartosc': 249.0}
404 nie ma produktu 9
409 dostępne sztuk: 5
422 niepoprawne dane
{'proba': 3}
```

Tym razem żądania idą przez sieć: uvicorn uruchomiony w wątku — obiekt `Server` z konfiguracją, flaga `started` po starcie, `should_exit` do zatrzymania — nasłuchuje na porcie `8765`, a klient z rozdziału 14 łączy się z nim przez httpx; zmiana frameworka po stronie serwera jest dla niego niewidoczna. Ponawianie po `503` z `Retry-After` działa jak poprzednio. Interfejs jest umową między programami; implementację można wymienić, dopóki umowa jest dotrzymana — dlatego opłaca się ją spisać w tabeli, jak w rozdziale 14, zanim zmieni się kod.

## Porównanie z `http.server`

Serwer w bibliotece standardowej zajmował się protokołem: rozbierał ścieżkę na segmenty, dekodował JSON w bloku `try`, sprawdzał obecność i typy pól, liczył `Content-Length`, pisał nagłówki. W FastAPI zniknęło wszystko, co nie jest decyzją sklepu — zostały reguły: kto może zamawiać, co znaczy brak towaru, jaki kod i komunikat dostaje klient. To, co pozostało, jest krótsze i sprawdzalne bez sieci, a dokumentacja interfejsu powstaje sama. Cena: kolejna biblioteka z własnymi regułami — konwencją nazw parametrów, wymogiem rejestrowania procedur obsługi wyjątków przed pierwszym żądaniem, kształtem błędów `detail` — które trzeba znać, zanim się je zmieni.
