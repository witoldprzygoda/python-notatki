# API nad warstwą danych

Sklep w pamięci znika z procesem. Warstwa danych z rozdziału 13 — model, fabryka sesji i operacje domenowe — jest gotowa; brakuje jej tylko sposobu, by każde żądanie HTTP dostało własną sesję w transakcji. Ten podrozdział łączy obie części: silnik powstaje raz przy starcie aplikacji, sesję dostarcza zależność, a odpowiedzi budują modele Pydantic z obiektów ORM. Moduły `modele.py`, `baza.py`, `operacje.py` i `dane_przykladowe.py` z rozdziału 13 leżą w tym samym katalogu.

## Silnik przy starcie i sesja na żądanie

```python title="sklep_baza.py"
"""API nad warstwą danych z rozdziału 13: silnik przy starcie, sesja na żądanie."""

from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from baza import fabryka_sesji, utworz_silnik
from modele import Produkt, Zamowienie
from operacje import BrakTowaru, anuluj_zamowienie, podsumowanie_klienta, zloz_zamowienie


@asynccontextmanager
async def cykl_zycia(app: FastAPI):
    app.state.Sesja = fabryka_sesji(utworz_silnik())
    yield


app = FastAPI(title="Sklep", version="3.0", lifespan=cykl_zycia)


def otworz_sesje(request: Request):
    with request.app.state.Sesja.begin() as sesja:
        yield sesja


Sesja = Annotated[Session, Depends(otworz_sesje)]


class ProduktOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nazwa: str
    kategoria: str
    cena: float
    stan: int


class PozycjaIn(BaseModel):
    produkt_id: int
    ilosc: int = Field(ge=1)


class NoweZamowienie(BaseModel):
    klient_id: int
    koszyk: list[PozycjaIn] = Field(min_length=1)
    data: date = Field(default_factory=date.today)


class PozycjaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    produkt_id: int
    ilosc: int
    cena: float


class ZamowienieOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    klient_id: int
    data: date
    status: str
    pozycje: list[PozycjaOut]


@app.exception_handler(BrakTowaru)
def brak_towaru(request: Request, blad: BrakTowaru):
    return JSONResponse(status_code=409, content={"detail": str(blad)})


@app.get("/produkty", response_model=list[ProduktOut])
def produkty(sesja: Sesja, kategoria: str | None = None):
    zapytanie = select(Produkt).order_by(Produkt.id)
    if kategoria:
        zapytanie = zapytanie.where(Produkt.kategoria == kategoria)
    return sesja.scalars(zapytanie).all()


@app.get("/produkty/{produkt_id}", response_model=ProduktOut)
def produkt(produkt_id: int, sesja: Sesja):
    znaleziony = sesja.get(Produkt, produkt_id)
    if znaleziony is None:
        raise HTTPException(status_code=404, detail=f"nie ma produktu {produkt_id}")
    return znaleziony


@app.get("/klienci/{klient_id}/podsumowanie")
def podsumowanie(klient_id: int, sesja: Sesja):
    return podsumowanie_klienta(sesja, klient_id)


@app.post("/zamowienia", status_code=status.HTTP_201_CREATED, response_model=ZamowienieOut)
def zloz(nowe: NoweZamowienie, sesja: Sesja, response: Response):
    koszyk = [(pozycja.produkt_id, pozycja.ilosc) for pozycja in nowe.koszyk]
    try:
        numer = zloz_zamowienie(sesja, nowe.klient_id, koszyk, nowe.data)
    except ValueError as blad:
        raise HTTPException(status_code=404, detail=str(blad))
    response.headers["Location"] = f"/zamowienia/{numer}"
    return sesja.get(Zamowienie, numer)


@app.get("/zamowienia/{zamowienie_id}", response_model=ZamowienieOut)
def zamowienie(zamowienie_id: int, sesja: Sesja):
    znalezione = sesja.get(Zamowienie, zamowienie_id)
    if znalezione is None:
        raise HTTPException(status_code=404, detail=f"nie ma zamówienia {zamowienie_id}")
    return znalezione


@app.post("/zamowienia/{zamowienie_id}/anulowanie")
def anuluj(zamowienie_id: int, sesja: Sesja):
    try:
        return {"zwrocono": anuluj_zamowienie(sesja, zamowienie_id)}
    except ValueError as blad:
        raise HTTPException(status_code=409, detail=str(blad))
```

**Cykl życia** (ang. *lifespan*) aplikacji to asynchroniczny menedżer kontekstu: część przed `yield` wykonuje się raz przy starcie serwera, część po nim — przy zatrzymaniu. W części przed `yield` tworzymy silnik z adresu w zmiennej środowiskowej `SKLEP_BAZA` (moduł `baza.py`) i fabrykę sesji, którą przechowujemy w `app.state`. Sesję na żądanie dostarcza zależność z `yield` — generator jak fixture pytest z rozdziału 16 „Python Notatki”: `begin()` fabryki sesji z `app.state` otwiera transakcję przed wywołaniem funkcji obsługi, a po jej zakończeniu zatwierdza ją (już po wysłaniu odpowiedzi) albo wycofuje, gdy funkcja zgłosiła wyjątek. Alias `Sesja` z `Annotated` pozwala zapisać tę zależność w każdej trasie jednym słowem. Modele odpowiedzi mają `from_attributes=True`, więc Pydantic czyta pola z obiektów ORM, także relację `pozycje` jako listę zagnieżdżonych modeli — obiekty ORM nie wychodzą poza sesję, na zewnątrz trafia ich obraz w JSON, jak zalecała lista kontrolna rozdziału 13. Wyjątki warstwy danych tłumaczymy na kody: `BrakTowaru` przez zarejestrowaną procedurę na `409`, `ValueError` z operacji — w miejscu wywołania — na `404` dla nieznanego klienta i `409` dla zamówienia, którego nie można anulować; ta strona zostaje przy kształcie `detail` FastAPI.

## Zamówienia w bazie

```python title="uzycie-baza.py"
from pathlib import Path

from fastapi.testclient import TestClient

from dane_przykladowe import przygotuj
from sklep_baza import app

Path("sklep-orm.db").unlink(missing_ok=True)
przygotuj("sqlite:///sklep-orm.db")

with TestClient(app) as klient:
    print([(p["id"], p["nazwa"], p["stan"]) for p in klient.get("/produkty", params={"kategoria": "książki"}).json()])
    print(klient.get("/klienci/1/podsumowanie").json())
    odpowiedz = klient.post("/zamowienia", json={"klient_id": 1, "koszyk": [{"produkt_id": 1, "ilosc": 2}, {"produkt_id": 5, "ilosc": 1}], "data": "2025-04-02"})
    print(odpowiedz.status_code, odpowiedz.headers["location"])
    print(odpowiedz.json())
    odpowiedz = klient.post("/zamowienia", json={"klient_id": 2, "koszyk": [{"produkt_id": 3, "ilosc": 1}, {"produkt_id": 5, "ilosc": 30}]})
    print(odpowiedz.status_code, odpowiedz.json())
    print([(p["id"], p["stan"]) for p in klient.get("/produkty").json() if p["id"] in (1, 3, 5)])
    print(klient.post("/zamowienia", json={"klient_id": 99, "koszyk": [{"produkt_id": 3, "ilosc": 1}]}).json())
    print(klient.post("/zamowienia", json={"klient_id": 1, "koszyk": []}).json()["detail"][0]["msg"])
    print(klient.post("/zamowienia/8/anulowanie").json(), klient.post("/zamowienia/1/anulowanie").json())
    print(klient.get("/zamowienia/8").json()["status"], klient.get("/klienci/1/podsumowanie").json())
```

```{ .text .no-copy }
[(1, 'Python. Wprowadzenie', 12), (2, 'Algorytmy', 5)]
{'zamowien': 2, 'wartosc': 515.0}
201 /zamowienia/8
{'id': 8, 'klient_id': 1, 'data': '2025-04-02', 'status': 'nowe', 'pozycje': [{'produkt_id': 1, 'ilosc': 2, 'cena': 59.0}, {'produkt_id': 5, 'ilosc': 1, 'cena': 79.0}]}
409 {'detail': 'produkt 5: zamówiono 30, dostępne 19'}
[(1, 10), (3, 8), (5, 19)]
{'detail': 'nie ma klienta o id 99'}
List should have at least 1 item after validation, not 0
{'zwrocono': 3} {'detail': 'zamówienia 1 nie można anulować'}
anulowane {'zamowien': 2, 'wartosc': 515.0}
```

Skrypt odtwarza bazę z danymi przykładowymi rozdziału 13 i otwiera klienta testowego w bloku `with` — dopiero wtedy działa cykl życia, więc silnik powstaje jak przy prawdziwym starcie. Zamówienie z dwiema pozycjami zapisuje się w trzech tabelach w jednej transakcji i wraca jako JSON z datą w formacie ISO i listą pozycji. Zamówienie, w którym brakuje piłek, kończy się kodem `409`, a stany po nim są nietknięte — także słuchawek z pierwszej pozycji, bo wyjątek przerwał blok `with … begin()` w zależności i transakcja została wycofana. Nieznany klient to `404`, pusty koszyk to `422` z komunikatem Pydantic. Anulowanie zwraca sztuki na stan i zmienia status, a podsumowanie klienta pomija anulowane zamówienie — tę samą logikę testował rozdział 13 bez sieci; API dołożyło tylko adresy i kody.

## Model za API

Ten sam wzorzec — zasób ładowany raz przy starcie, żądanie z danymi wejściowymi, odpowiedź obliczona — obsługuje model uczenia maszynowego. Klasyfikator irysów ze scikit-learn zastępuje tu pakiet z rozdziału 12, który czytelnik ścieżki uczenia maszynowego wczytałby w cyklu życia przez `joblib.load()`:

```python title="model_api.py"
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


@asynccontextmanager
async def cykl_zycia(app: FastAPI):
    irysy = load_iris()
    app.state.model = make_pipeline(StandardScaler(), LogisticRegression()).fit(irysy.data, irysy.target)
    app.state.gatunki = list(irysy.target_names)
    yield


app = FastAPI(title="Irysy", lifespan=cykl_zycia)


class Kwiat(BaseModel):
    dlugosc_dzialki: float = Field(gt=0)
    szerokosc_dzialki: float = Field(gt=0)
    dlugosc_platka: float = Field(gt=0)
    szerokosc_platka: float = Field(gt=0)


class Przewidywanie(BaseModel):
    gatunek: str
    prawdopodobienstwo: float


@app.post("/przewiduj", response_model=Przewidywanie)
def przewiduj(kwiat: Kwiat, request: Request):
    cechy = [[kwiat.dlugosc_dzialki, kwiat.szerokosc_dzialki, kwiat.dlugosc_platka, kwiat.szerokosc_platka]]
    prawdopodobienstwa = request.app.state.model.predict_proba(cechy)[0]
    numer = int(prawdopodobienstwa.argmax())
    return Przewidywanie(gatunek=request.app.state.gatunki[numer], prawdopodobienstwo=round(float(prawdopodobienstwa[numer]), 3))


@app.post("/przewiduj-wiele", response_model=list[Przewidywanie])
def przewiduj_wiele(kwiaty: list[Kwiat], request: Request):
    return [przewiduj(kwiat, request) for kwiat in kwiaty]


with TestClient(app) as klient:
    for kwiat in ((5.1, 3.5, 1.4, 0.2), (6.0, 2.9, 4.5, 1.5), (6.3, 3.3, 6.0, 2.5)):
        tresc = dict(zip(Kwiat.model_fields, kwiat))
        print(klient.post("/przewiduj", json=tresc).json())
    odpowiedz = klient.post("/przewiduj", json={"dlugosc_dzialki": -1, "szerokosc_dzialki": 3.5, "dlugosc_platka": 1.4})
    print(odpowiedz.status_code, [(blad["loc"][1], blad["type"]) for blad in odpowiedz.json()["detail"]])
    print(klient.post("/przewiduj-wiele", json=[dict(zip(Kwiat.model_fields, (5.1, 3.5, 1.4, 0.2)))] * 2).json())
```

```{ .text .no-copy }
{'gatunek': 'setosa', 'prawdopodobienstwo': 0.985}
{'gatunek': 'versicolor', 'prawdopodobienstwo': 0.779}
{'gatunek': 'virginica', 'prawdopodobienstwo': 0.994}
422 [('dlugosc_dzialki', 'greater_than'), ('szerokosc_platka', 'missing')]
[{'gatunek': 'setosa', 'prawdopodobienstwo': 0.985}, {'gatunek': 'setosa', 'prawdopodobienstwo': 0.985}]
```

Model trenuje się raz, przy starcie, i jest przechowywany w `app.state` — żądania tylko liczą. Model wejścia nazywa cechy i pilnuje zakresów, więc do `predict_proba()` nie trafi ujemna długość ani brakujące pole; `float()` i `int()` zamieniają typy NumPy na typy JSON, jak w rozdziale 2. Trasa dla listy kwiatów przyjmuje `list[Kwiat]` i zwraca listę przewidywań — jedno żądanie zamiast stu. W prawdziwym wdrożeniu do odpowiedzi warto dodać wersję modelu, a do cyklu życia — wczytanie pliku modelu ze ścieżki w zmiennej środowiskowej.
