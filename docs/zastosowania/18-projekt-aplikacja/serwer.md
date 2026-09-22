# Serwer: baza i API

Strona serwera to warstwa danych z rozdziału 13 i usługa z rozdziału 15, przeniesione do pakietu. Zmiany są niewielkie i celowe: importy względne, dane przykładowe wypełniane przy starcie usługi, trasa z listą klientów i punkt wejścia uruchamiający serwer.

## Układ pakietu

```{ .text .no-copy }
projekt/
├── pyproject.toml
├── README.md
├── LICENSE
├── uruchom_okno.py
├── src/
│   └── sklep/
│       ├── __init__.py
│       ├── modele.py            warstwa danych (rozdział 13)
│       ├── baza.py
│       ├── operacje.py
│       ├── dane_przykladowe.py
│       ├── api.py               usługa FastAPI (rozdział 15)
│       ├── klient.py            klient API (rozdział 14)
│       ├── koszyk.py            logika okna bez widżetów
│       └── okno.py              okno CustomTkinter (rozdział 16)
└── tests/
    ├── conftest.py
    ├── test_api.py
    ├── test_klient.py
    └── test_koszyk.py
```

```toml title="pyproject.toml"
[build-system]
requires = ["hatchling>=1.27"]
build-backend = "hatchling.build"

[project]
name = "sklep"
dynamic = ["version"]
description = "Sklep: baza danych, usługa API i okno klienta"
readme = "README.md"
requires-python = ">=3.12"
license = "MIT"
authors = [{ name = "Jan Kowalski", email = "jan.kowalski@example.com" }]
dependencies = [
    "sqlalchemy>=2,<3",
    "fastapi>=0.141,<1",
    "uvicorn>=0.53,<1",
    "httpx>=0.27,<1",
    "customtkinter>=6,<7",
]

[project.optional-dependencies]
test = ["pytest>=9", "httpx2>=2"]

[project.scripts]
sklep-serwer = "sklep.api:uruchom"

[project.gui-scripts]
sklep = "sklep.okno:main"

[tool.hatch.version]
path = "src/sklep/__init__.py"

[tool.pytest.ini_options]
filterwarnings = ["ignore::DeprecationWarning:starlette.testclient"]
```

```python title="src/sklep/__init__.py"
"""Sklep: warstwa danych, usługa API i okno klienta."""

__version__ = "1.0.0"
```

Zależności zapisujemy jako zakresy według rozdziału 17: dolna granica nie wyższa niż wersje sprawdzone w rozdziałach 13–16, górna — następna wersja główna. Pakiet ma dwa punkty wejścia: `sklep-serwer` w `[project.scripts]` (z konsolą, w której uvicorn pisze dziennik) i `sklep` w `[project.gui-scripts]` (na Windows bez konsoli). Grupa `test` dodaje pytest i `httpx2`, na którym działa klient testowy FastAPI; sekcja pytest wycisza ostrzeżenie biblioteki, jak w rozdziale 15. Plik `LICENSE` to tekst licencji MIT z rozdziału 17; Hatchling dołącza go do pakietu bez dodatkowej konfiguracji.

## Warstwa danych z rozdziału 13

Cztery moduły przechodzą do pakietu bez zmian w logice. Importy stają się względne (`from .modele import …`), bo moduły są teraz częścią pakietu `sklep`; pozostałe różnice omawiamy pod blokami.

```python title="src/sklep/modele.py"
"""Model sklepu: cztery tabele jako klasy SQLAlchemy."""

from datetime import date

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Baza(DeclarativeBase):
    pass


class Klient(Baza):
    __tablename__ = "klienci"
    id: Mapped[int] = mapped_column(primary_key=True)
    nazwisko: Mapped[str] = mapped_column(String(60))
    miasto: Mapped[str]
    segment: Mapped[str] = mapped_column(default="nowy")
    email: Mapped[str | None] = mapped_column(unique=True)
    zamowienia: Mapped[list["Zamowienie"]] = relationship(back_populates="klient")

    def __repr__(self):
        return f"Klient(id={self.id}, nazwisko={self.nazwisko!r})"


class Produkt(Baza):
    __tablename__ = "produkty"
    id: Mapped[int] = mapped_column(primary_key=True)
    nazwa: Mapped[str] = mapped_column(unique=True)
    kategoria: Mapped[str]
    cena: Mapped[float]
    stan: Mapped[int] = mapped_column(default=0)

    def __repr__(self):
        return f"Produkt(id={self.id}, nazwa={self.nazwa!r}, stan={self.stan})"


class Zamowienie(Baza):
    __tablename__ = "zamowienia"
    id: Mapped[int] = mapped_column(primary_key=True)
    klient_id: Mapped[int] = mapped_column(ForeignKey("klienci.id"))
    data: Mapped[date]
    status: Mapped[str] = mapped_column(default="nowe")
    klient: Mapped[Klient] = relationship(back_populates="zamowienia")
    pozycje: Mapped[list["Pozycja"]] = relationship(back_populates="zamowienie", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Zamowienie(id={self.id}, data={self.data}, status={self.status!r})"


class Pozycja(Baza):
    __tablename__ = "pozycje"
    id: Mapped[int] = mapped_column(primary_key=True)
    zamowienie_id: Mapped[int] = mapped_column(ForeignKey("zamowienia.id"))
    produkt_id: Mapped[int] = mapped_column(ForeignKey("produkty.id"))
    ilosc: Mapped[int]
    cena: Mapped[float]
    zamowienie: Mapped[Zamowienie] = relationship(back_populates="pozycje")
    produkt: Mapped[Produkt] = relationship()

    def __repr__(self):
        return f"Pozycja(produkt_id={self.produkt_id}, ilosc={self.ilosc})"
```

```python title="src/sklep/baza.py"
"""Połączenie z bazą aplikacji: silnik z adresu w zmiennej środowiskowej i fabryka sesji."""

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from .modele import Baza

ADRES = os.environ.get("SKLEP_BAZA", "sqlite:///sklep.db")


def utworz_silnik(adres=ADRES):
    silnik = create_engine(adres)
    if silnik.dialect.name == "sqlite":
        @event.listens_for(silnik, "connect")
        def wlacz_klucze_obce(polaczenie_dbapi, _):
            polaczenie_dbapi.execute("PRAGMA foreign_keys = ON")
    Baza.metadata.create_all(silnik)
    return silnik


def fabryka_sesji(silnik):
    return sessionmaker(silnik)
```

```python title="src/sklep/operacje.py"
"""Operacje sklepu na sesji: każda wykonuje się w całości albo wcale."""

from sqlalchemy import func, select

from .modele import Klient, Pozycja, Produkt, Zamowienie


class BrakTowaru(Exception):
    pass


def zloz_zamowienie(sesja, klient_id, koszyk, data):
    """Tworzy zamówienie z pozycjami z koszyka [(produkt_id, ilosc), ...] i zdejmuje towar ze stanu."""
    klient = sesja.get(Klient, klient_id)
    if klient is None:
        raise ValueError(f"nie ma klienta o id {klient_id}")
    zamowienie = Zamowienie(klient=klient, data=data)
    sesja.add(zamowienie)
    for produkt_id, ilosc in koszyk:
        produkt = sesja.get(Produkt, produkt_id)
        if produkt is None or produkt.stan < ilosc:
            dostepne = 0 if produkt is None else produkt.stan
            raise BrakTowaru(f"produkt {produkt_id}: zamówiono {ilosc}, dostępne {dostepne}")
        produkt.stan -= ilosc
        zamowienie.pozycje.append(Pozycja(produkt=produkt, ilosc=ilosc, cena=produkt.cena))
    sesja.flush()
    return zamowienie.id


def anuluj_zamowienie(sesja, zamowienie_id):
    """Oznacza zamówienie jako anulowane i zwraca towar na stan; zwraca liczbę zwróconych sztuk."""
    zamowienie = sesja.get(Zamowienie, zamowienie_id)
    if zamowienie is None or zamowienie.status != "nowe":
        raise ValueError(f"zamówienia {zamowienie_id} nie można anulować")
    zamowienie.status = "anulowane"
    for pozycja in zamowienie.pozycje:
        pozycja.produkt.stan += pozycja.ilosc
    return sum(pozycja.ilosc for pozycja in zamowienie.pozycje)


def podsumowanie_klienta(sesja, klient_id):
    wartosc = func.sum(Pozycja.ilosc * Pozycja.cena)
    zapytanie = select(func.count(func.distinct(Zamowienie.id)), wartosc).join(Zamowienie.pozycje).where(Zamowienie.klient_id == klient_id, Zamowienie.status != "anulowane")
    zamowien, suma = sesja.execute(zapytanie).one()
    return {"zamowien": zamowien, "wartosc": suma or 0.0}
```

```python title="src/sklep/dane_przykladowe.py"
"""Dane przykładowe sklepu: wypełnia puste tabele."""

from datetime import date

from .modele import Klient, Pozycja, Produkt, Zamowienie

KLIENCI = [("Nowak", "Kraków", "stały", "nowak@example.com"), ("Kowalska", "Tarnów", "stały", None), ("Wiśniewski", "Rzeszów", "nowy", None), ("Zielińska", "Nowy Sącz", "stały", None), ("Lis", "Kraków", "nowy", None), ("Mazur", "Tarnów", "nowy", None)]
PRODUKTY = [("Python. Wprowadzenie", "książki", 59.0, 12), ("Algorytmy", "książki", 89.0, 5), ("Słuchawki", "elektronika", 249.0, 8), ("Klawiatura", "elektronika", 199.0, 0), ("Piłka", "sport", 79.0, 20), ("Klocki", "zabawki", 149.0, 6)]
ZAMOWIENIA = [(1, date(2025, 1, 4), "wysłane"), (2, date(2025, 1, 15), "wysłane"), (1, date(2025, 2, 2), "wysłane"), (3, date(2025, 2, 20), "anulowane"), (5, date(2025, 3, 3), "wysłane"), (2, date(2025, 3, 18), "nowe"), (4, date(2025, 3, 25), "nowe")]
POZYCJE = [(1, 1, 2), (1, 3, 1), (2, 5, 1), (3, 2, 1), (3, 1, 1), (4, 6, 2), (5, 3, 1), (5, 5, 2), (6, 1, 3), (7, 6, 1), (7, 2, 1)]


def wypelnij(sesja):
    """Dodaje obiekty w kolejności list, więc identyfikatory są takie jak w schemacie SQL."""
    klienci = [Klient(nazwisko=n, miasto=m, segment=s, email=e) for n, m, s, e in KLIENCI]
    produkty = [Produkt(nazwa=n, kategoria=k, cena=c, stan=s) for n, k, c, s in PRODUKTY]
    sesja.add_all(klienci + produkty)
    for numer, (nr_klienta, data, status) in enumerate(ZAMOWIENIA, start=1):
        pozycje = [Pozycja(produkt=produkty[nr_produktu - 1], ilosc=ilosc, cena=produkty[nr_produktu - 1].cena) for nr_zamowienia, nr_produktu, ilosc in POZYCJE if nr_zamowienia == numer]
        sesja.add(Zamowienie(klient=klienci[nr_klienta - 1], data=data, status=status, pozycje=pozycje))
    sesja.commit()
```

Moduł danych przykładowych stracił własne funkcje `utworz_silnik()` i `przygotuj()` — silnik tworzy `baza.py`, a wypełnianie przejmuje usługa przy starcie. Adres bazy domyślnie wskazuje plik `sklep.db` w katalogu roboczym (w rozdziale 13: `sklep-orm.db`); zmienna `SKLEP_BAZA` pozwala wskazać inny bez zmiany kodu.

## Usługa API

```python title="src/sklep/api.py"
"""Usługa API sklepu: silnik przy starcie, sesja na żądanie, trasy REST."""

import os
from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import __version__
from .baza import fabryka_sesji, utworz_silnik
from .dane_przykladowe import wypelnij
from .modele import Klient, Produkt, Zamowienie
from .operacje import BrakTowaru, anuluj_zamowienie, podsumowanie_klienta, zloz_zamowienie


@asynccontextmanager
async def cykl_zycia(app: FastAPI):
    app.state.Sesja = fabryka_sesji(utworz_silnik())
    with app.state.Sesja() as sesja:
        if sesja.scalar(select(Klient).limit(1)) is None:
            wypelnij(sesja)
    yield


app = FastAPI(title="Sklep", version=__version__, lifespan=cykl_zycia)


def otworz_sesje(request: Request):
    with request.app.state.Sesja.begin() as sesja:
        yield sesja


Sesja = Annotated[Session, Depends(otworz_sesje)]


class KlientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nazwisko: str
    miasto: str
    segment: str


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


@app.get("/klienci", response_model=list[KlientOut])
def klienci(sesja: Sesja):
    return sesja.scalars(select(Klient).order_by(Klient.id)).all()


@app.get("/klienci/{klient_id}/podsumowanie")
def podsumowanie(klient_id: int, sesja: Sesja):
    if sesja.get(Klient, klient_id) is None:
        raise HTTPException(status_code=404, detail=f"nie ma klienta o id {klient_id}")
    return podsumowanie_klienta(sesja, klient_id)


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


def uruchom():
    """Punkt wejścia polecenia sklep-serwer."""
    uvicorn.run(app, host=os.environ.get("SKLEP_HOST", "127.0.0.1"), port=int(os.environ.get("SKLEP_PORT", "8000")))
```

Względem rozdziału 15 usługa zmieniła się w kilku miejscach. Cykl życia po utworzeniu silnika sprawdza, czy tabela klientów jest pusta, i wtedy wypełnia bazę danymi przykładowymi — pierwsze uruchomienie u odbiorcy daje działający sklep, kolejne nie dublują danych. Trasa `/klienci` dostarcza oknu listę klientów do wyboru, a `/klienci/{id}/podsumowanie` odpowiada `404` dla nieznanego klienta zamiast zerowego podsumowania. Funkcja `uruchom()` to punkt wejścia polecenia `sklep-serwer`: `uvicorn.run()` robi to, co `python -m uvicorn` z rozdziału 15, a adres i port pochodzą ze zmiennych środowiskowych. Wersja usługi w dokumentacji `/docs` jest wersją pakietu.

## Pierwsze żądania

```python title="uzycie-api.py"
import os
from pathlib import Path

os.environ["SKLEP_BAZA"] = "sqlite:///sklep-proba.db"
Path("sklep-proba.db").unlink(missing_ok=True)

from fastapi.testclient import TestClient  # noqa: E402

from sklep.api import app  # noqa: E402

with TestClient(app) as klient:
    opis = klient.get("/openapi.json").json()
    print(opis["info"], sorted(opis["paths"]))
    print([(k["id"], k["nazwisko"], k["segment"]) for k in klient.get("/klienci").json()][:3])
    print([(p["nazwa"], p["stan"]) for p in klient.get("/produkty", params={"kategoria": "elektronika"}).json()])
    odpowiedz = klient.post("/zamowienia", json={"klient_id": 3, "koszyk": [{"produkt_id": 3, "ilosc": 1}, {"produkt_id": 6, "ilosc": 2}], "data": "2025-05-06"})
    print(odpowiedz.status_code, odpowiedz.headers["location"], odpowiedz.json()["pozycje"])
    print(klient.get("/klienci/3/podsumowanie").json(), klient.get("/produkty/6").json()["stan"])
    print(klient.post("/zamowienia", json={"klient_id": 3, "koszyk": [{"produkt_id": 4, "ilosc": 1}]}).json())
    print(klient.get("/klienci/99/podsumowanie").json())
```

```{ .text .no-copy }
{'title': 'Sklep', 'version': '1.0.0'} ['/klienci', '/klienci/{klient_id}/podsumowanie', '/produkty', '/produkty/{produkt_id}', '/zamowienia', '/zamowienia/{zamowienie_id}', '/zamowienia/{zamowienie_id}/anulowanie']
[(1, 'Nowak', 'stały'), (2, 'Kowalska', 'stały'), (3, 'Wiśniewski', 'nowy')]
[('Słuchawki', 8), ('Klawiatura', 0)]
201 /zamowienia/8 [{'produkt_id': 3, 'ilosc': 1, 'cena': 249.0}, {'produkt_id': 6, 'ilosc': 2, 'cena': 149.0}]
{'zamowien': 1, 'wartosc': 547.0} 4
{'detail': 'produkt 4: zamówiono 1, dostępne 0'}
{'detail': 'nie ma klienta o id 99'}
```

Skrypt ustawia zmienną `SKLEP_BAZA` przed importem pakietu — moduł `baza.py` czyta ją przy imporcie, jak w rozdziale 13 — i usuwa plik próbny, więc każde uruchomienie zaczyna od pustej bazy, którą cykl życia wypełnia danymi przykładowymi. Klient testowy w bloku `with` uruchamia cykl życia jak prawdziwy serwer. Reszta to umowa interfejsu z rozdziału 15: `201` z `Location` po zamówieniu, stan produktu pomniejszony o zamówioną ilość, `409` z komunikatem warstwy danych, gdy towaru brakuje, `404` dla nieznanego klienta — tu w nowej trasie podsumowania. Z tych tras korzysta okno z następnej strony.
