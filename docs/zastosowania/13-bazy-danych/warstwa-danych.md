# Warstwa danych aplikacji

W skryptach z poprzednich podrozdziałów każdy plik tworzył silnik i sesję osobno. Aplikacja potrzebuje jednego miejsca, które wie, gdzie jest baza i jak otworzyć transakcję, oraz funkcji wyrażających operacje z dziedziny — „złóż zamówienie”, „anuluj zamówienie” — z których każda wykonuje się w całości albo wcale. Ten podrozdział buduje taką **warstwę danych** i testuje ją na bazie w pamięci.

## Moduł bazy

```python title="baza.py"
"""Połączenie z bazą aplikacji: silnik z adresu w zmiennej środowiskowej i fabryka sesji."""

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from modele import Baza

ADRES = os.environ.get("SKLEP_BAZA", "sqlite:///sklep-orm.db")


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

Adres bazy pochodzi ze zmiennej środowiskowej z wartością domyślną — `os.environ.get()` z rozdziału 9 „Python Notatki” — więc ten sam kod działa z plikiem SQLite u programisty i z serwerem u odbiorcy. `PRAGMA foreign_keys` dotyczy tylko SQLite, dlatego zdarzenie rejestrujemy warunkowo. `sessionmaker()` zwraca fabrykę sesji związaną z silnikiem: `Sesja()` otwiera sesję, a `Sesja.begin()` — sesję w transakcji, która zatwierdza się po bloku `with` i wycofuje przy wyjątku.

## Operacje domenowe

```python title="operacje.py"
"""Operacje sklepu na sesji: każda wykonuje się w całości albo wcale."""

from datetime import date

from sqlalchemy import func, select

from modele import Klient, Pozycja, Produkt, Zamowienie


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

```python title="demo.py"
from datetime import date

from sqlalchemy import select

from baza import fabryka_sesji, utworz_silnik
from dane_przykladowe import przygotuj
from modele import Produkt, Zamowienie
from operacje import BrakTowaru, anuluj_zamowienie, podsumowanie_klienta, zloz_zamowienie

przygotuj("sqlite:///sklep-orm.db")
Sesja = fabryka_sesji(utworz_silnik("sqlite:///sklep-orm.db"))


def stany(sesja):
    return dict(sesja.execute(select(Produkt.nazwa, Produkt.stan).where(Produkt.id.in_([1, 3, 5]))).all())


with Sesja.begin() as sesja:
    print(podsumowanie_klienta(sesja, 1), stany(sesja))
    nowe = zloz_zamowienie(sesja, 1, [(1, 2), (5, 1)], date(2025, 4, 2))
    print(nowe, stany(sesja))
try:
    with Sesja.begin() as sesja:
        zloz_zamowienie(sesja, 2, [(3, 1), (5, 30)], date(2025, 4, 3))
except BrakTowaru as blad:
    print("BrakTowaru:", blad)
with Sesja.begin() as sesja:
    print(stany(sesja), sesja.scalar(select(Zamowienie).where(Zamowienie.data == date(2025, 4, 3))))
    print(anuluj_zamowienie(sesja, nowe), stany(sesja), sesja.get(Zamowienie, nowe).status)
    print(podsumowanie_klienta(sesja, 1), podsumowanie_klienta(sesja, 6))
```

```{ .text .no-copy }
{'zamowien': 2, 'wartosc': 515.0} {'Python. Wprowadzenie': 12, 'Słuchawki': 8, 'Piłka': 20}
8 {'Python. Wprowadzenie': 10, 'Słuchawki': 8, 'Piłka': 19}
BrakTowaru: produkt 5: zamówiono 30, dostępne 19
{'Python. Wprowadzenie': 10, 'Słuchawki': 8, 'Piłka': 19} None
3 {'Python. Wprowadzenie': 12, 'Słuchawki': 8, 'Piłka': 20} anulowane
{'zamowien': 2, 'wartosc': 515.0} {'zamowien': 0, 'wartosc': 0.0}
```

Funkcje operacji przyjmują sesję jako argument i nie zatwierdzają jej same — o granicach transakcji decyduje kod wywołujący, który może złożyć kilka operacji w jedną. Złożenie zamówienia zmienia trzy tabele: dodaje zamówienie z pozycjami i zdejmuje towar ze stanu; gdy drugiej pozycji brakuje na magazynie, wyjątek przerywa blok `Sesja.begin()`, a wycofanie cofa także zdjęcie słuchawek ze stanu z pierwszej pozycji — w bazie nie ma ani zamówienia, ani zmiany stanów. Bez transakcji taki błąd zostawiłby magazyn niezgodny z zamówieniami. `flush()` w `zloz_zamowienie()` zapewnia, że zwracany identyfikator już istnieje. Wyjątek własnej klasy, jak w rozdziale 10 „Python Notatki”, pozwala warstwie wyżej odróżnić brak towaru od błędu programu.

## Testy z bazą w pamięci

```python title="tests/conftest.py"
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from baza import fabryka_sesji, utworz_silnik  # noqa: E402
from dane_przykladowe import wypelnij  # noqa: E402


@pytest.fixture
def sesja():
    Sesja = fabryka_sesji(utworz_silnik("sqlite://"))
    with Sesja() as sesja:
        wypelnij(sesja)
        yield sesja
```

```python title="tests/test_operacje.py"
from datetime import date

import pytest
from sqlalchemy import func, select

from modele import Pozycja, Produkt, Zamowienie
from operacje import BrakTowaru, anuluj_zamowienie, podsumowanie_klienta, zloz_zamowienie


def test_zlozenie_zamowienia_zdejmuje_towar(sesja):
    nowe = zloz_zamowienie(sesja, 6, [(5, 3)], date(2025, 4, 1))
    sesja.commit()
    zamowienie = sesja.get(Zamowienie, nowe)
    assert zamowienie.klient.nazwisko == "Mazur"
    assert [(pozycja.produkt_id, pozycja.ilosc, pozycja.cena) for pozycja in zamowienie.pozycje] == [(5, 3, 79.0)]
    assert sesja.get(Produkt, 5).stan == 17


def test_brak_towaru_nie_zostawia_sladu(sesja):
    przed = sesja.scalar(select(func.count()).select_from(Pozycja))
    with pytest.raises(BrakTowaru, match="produkt 4"):
        zloz_zamowienie(sesja, 1, [(1, 1), (4, 1)], date(2025, 4, 1))
    sesja.rollback()
    assert sesja.scalar(select(func.count()).select_from(Pozycja)) == przed
    assert sesja.get(Produkt, 1).stan == 12


def test_anulowanie_zwraca_towar(sesja):
    assert anuluj_zamowienie(sesja, 7) == 2
    sesja.commit()
    assert sesja.get(Zamowienie, 7).status == "anulowane"
    assert (sesja.get(Produkt, 6).stan, sesja.get(Produkt, 2).stan) == (7, 6)
    with pytest.raises(ValueError):
        anuluj_zamowienie(sesja, 1)


def test_podsumowanie_pomija_anulowane(sesja):
    assert podsumowanie_klienta(sesja, 1) == {"zamowien": 2, "wartosc": 515.0}
    assert podsumowanie_klienta(sesja, 3) == {"zamowien": 0, "wartosc": 0.0}
```

```powershell title="Terminal"
python -m pytest -q
```

```{ .text .no-copy }
....                                                                     [100%]
4 passed in 0.09s
```

Fixture buduje bazę w pamięci (`sqlite://`), tworzy tabele i wypełnia je danymi przykładowymi — każdy test dostaje świeżą bazę w ułamku sekundy, a plik projektu pozostaje nietknięty. Testy sprawdzają to, co w operacjach jest decyzją: że zamówienie zdejmuje towar, że nieudane zamówienie nie zostawia śladu, że anulowanie zwraca sztuki i odmawia dla zamówień wysłanych, że podsumowanie pomija anulowane. Wartość 515 zł dla Nowaka to zamówienia 1 i 3 z podrozdziału o SQL (367 + 148). Kod produkcyjny i testy używają tych samych modułów, różni je tylko adres bazy przekazany do silnika.

## Migracje i inne bazy

`create_all()` tworzy tabele, których nie ma, ale nie zmienia istniejących: dodanie kolumny do klasy nie doda jej do bazy z danymi. Zmiany schematu w działającej aplikacji prowadzi się **migracjami** (ang. *schema migration*) — skryptami, które przekształcają bazę z wersji na wersję i dają się cofnąć; w ekosystemie SQLAlchemy robi to narzędzie Alembic, które porównuje model z bazą i generuje skrypt migracji. Przejście na PostgreSQL wymaga sterownika (pakiet `psycopg`) i adresu `postgresql+psycopg://…` w zmiennej środowiskowej; model, zapytania i testy zostają. Różnice ujawniają się w szczegółach: SQLite typuje dynamicznie, a PostgreSQL ściśle, `strftime()` jest funkcją SQLite, a klucze obce w PostgreSQL działają zawsze — dlatego to, co zależy od bazy, zbieramy w jednym module.

## Kiedy `sqlite3`, a kiedy ORM

Moduł `sqlite3` wystarcza, gdy program jest skryptem z kilkoma zapytaniami, dane mieszczą się w jednym pliku i nikt nie planuje zmiany bazy — a SQL, który pisze się wprost, jest łatwy do przeczytania i sprawdzenia w narzędziu do przeglądania SQLite. SQLAlchemy opłaca się, gdy tabel jest wiele i są powiązane, obiekty domeny mają metody i testy, aplikacja ma działać z różnymi bazami albo rośnie przez lata — model jest wtedy jedynym opisem schematu, a sesja pilnuje transakcji. W obu przypadkach obowiązują te same zasady: parametry zamiast sklejania SQL, ograniczenia w schemacie, transakcja wokół każdej operacji, która zmienia więcej niż jeden wiersz, i testy na bazie w pamięci.

## Lista kontrolna warstwy danych

- **Schemat z ograniczeniami**: klucze główne i obce, `NOT NULL`, `UNIQUE`, `CHECK`; w SQLite klucze obce włączone na każdym połączeniu.
- **Parametry zapytań** zawsze; SQL sklejany z tekstem od użytkownika — nigdy.
- **Transakcja** wokół każdej operacji domenowej; funkcje operacji przyjmują sesję i nie zatwierdzają same.
- **Obiekty ORM nie wychodzą poza sesję**; na zewnątrz idą wartości, słowniki lub klasy danych.
- **Relacje ładowane świadomie**: `selectinload()`/`joinedload()` tam, gdzie pętla po obiektach dotknęłaby relacji; licznik zapytań w razie wątpliwości.
- **Indeksy** na kolumnach z `WHERE` i `JOIN` przy większych danych; `EXPLAIN QUERY PLAN` jako sprawdzian.
- **Adres bazy** w konfiguracji, nie w kodzie; testy na `sqlite://`; zmiany schematu przez migracje.

## Dalej: HTTP i API

Warstwa danych jest gotowa, ale korzysta z niej tylko skrypt na tej samej maszynie. Następne rozdziały ścieżki udostępniają ją przez sieć: najpierw [protokół HTTP od strony klienta i serwera](../14-http-api/index.md), potem [usługa FastAPI](../15-fastapi/baza.md), w której każde żądanie dostaje własną sesję z fabryki z tego podrozdziału; [projekt ścieżki](../18-projekt-aplikacja/index.md) połączy bazę, API i okno aplikacji.
