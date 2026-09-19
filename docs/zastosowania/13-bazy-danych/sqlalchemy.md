# SQLAlchemy — model i sesja

SQL w łańcuchach znaków ma dwie wady: błąd w nim ujawnia się dopiero przy wykonaniu, a wynik wraca jako krotki, które trzeba samemu zamieniać na obiekty. **SQLAlchemy** rozwiązuje obie: tabele opisuje klasami Pythona, wiersze zwraca jako ich obiekty, a zapytania buduje z wyrażeń, które sprawdza edytor i mypy — to **mapowanie obiektowo-relacyjne** (ang. *object-relational mapping*, ORM). Ten podrozdział wprowadza silnik, model, sesję i zapytania; relacje między tabelami — następny.

## Silnik i `text()`

```python title="silnik.py"
from sqlalchemy import create_engine, text

silnik = create_engine("sqlite://")
print(silnik, silnik.dialect.name)
with silnik.connect() as polaczenie:
    polaczenie.execute(text("CREATE TABLE miasta (nazwa TEXT PRIMARY KEY, ludnosc INTEGER)"))
    polaczenie.execute(text("INSERT INTO miasta VALUES (:nazwa, :ludnosc)"), [{"nazwa": "Kraków", "ludnosc": 804000}, {"nazwa": "Tarnów", "ludnosc": 105000}, {"nazwa": "Wieliczka", "ludnosc": 24000}])
    polaczenie.commit()
    wynik = polaczenie.execute(text("SELECT nazwa, ludnosc FROM miasta WHERE ludnosc > :prog ORDER BY nazwa"), {"prog": 100000})
    print(wynik.all())
    print(polaczenie.execute(text("SELECT COUNT(*) FROM miasta")).scalar())
```

```{ .text .no-copy }
Engine(sqlite://) sqlite
[('Kraków', 804000), ('Tarnów', 105000)]
3
```

**Silnik** (ang. *engine*) reprezentuje bazę pod adresem URL: `sqlite://` to baza w pamięci, `sqlite:///sklep.db` — plik, `postgresql+psycopg://użytkownik:hasło@serwer/baza` — serwer PostgreSQL; zmiana adresu jest jedyną zmianą w kodzie. Silnik utrzymuje pulę połączeń i otwiera je na żądanie: `connect()` w bloku `with` daje połączenie, `text()` opakowuje surowy SQL z parametrami `:nazwa`, a `commit()` zatwierdza jak w `sqlite3`. Wynik `execute()` udostępnia `all()`, `first()`, `scalar()` i iterację po wierszach z dostępem po nazwie. Tak wygląda najniższy poziom SQLAlchemy; reszta rozdziału używa ORM.

## Model deklaratywny

```python title="modele.py"
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

```python title="ddl.py"
from sqlalchemy import create_engine, inspect
from sqlalchemy.schema import CreateTable

from modele import Baza, Zamowienie

print(list(Baza.metadata.tables))
print(str(CreateTable(Zamowienie.__table__)).strip())
silnik = create_engine("sqlite://")
Baza.metadata.create_all(silnik)
inspektor = inspect(silnik)
print(inspektor.get_table_names())
print([(kolumna["name"], str(kolumna["type"]), kolumna["nullable"]) for kolumna in inspektor.get_columns("klienci")])
```

```{ .text .no-copy }
['klienci', 'produkty', 'zamowienia', 'pozycje']
CREATE TABLE zamowienia (
	id INTEGER NOT NULL, 
	klient_id INTEGER NOT NULL, 
	data DATE NOT NULL, 
	status VARCHAR NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(klient_id) REFERENCES klienci (id)
)
['klienci', 'pozycje', 'produkty', 'zamowienia']
[('id', 'INTEGER', False), ('nazwisko', 'VARCHAR(60)', False), ('miasto', 'VARCHAR', False), ('segment', 'VARCHAR', False), ('email', 'VARCHAR', True)]
```

Model to klasy dziedziczące po wspólnej bazie `DeclarativeBase`: `__tablename__` nazywa tabelę, a każda adnotacja `Mapped[typ]` — kolumnę, której typ SQL wynika z typu Pythona (`int` → `INTEGER`, `str` → `VARCHAR`, `date` → `DATE`, `str | None` → kolumna dopuszczająca `NULL`). `mapped_column()` dodaje to, czego adnotacja nie wyrazi: klucz główny, `unique`, `default`, długość napisu, `ForeignKey` do kolumny innej tabeli. Pola `relationship()` nie są kolumnami — to powiązania między obiektami, o których mówi następny podrozdział. `Baza.metadata` zna wszystkie tabele modelu: `create_all()` tworzy brakujące (istniejących nie zmienia), `CreateTable` pokazuje generowany SQL, a `inspect(silnik)` czyta schemat z bazy (tabele alfabetycznie) — odpowiednik ręcznie pisanego schematu SQL, ale bez `CHECK` i `ON DELETE CASCADE`.

## Dane przykładowe

```python title="dane_przykladowe.py"
"""Dane przykładowe sklepu i przygotowanie bazy: tworzy tabele i wypełnia je, gdy są puste."""

from datetime import date

from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import Session

from modele import Baza, Klient, Pozycja, Produkt, Zamowienie

KLIENCI = [("Nowak", "Kraków", "stały", "nowak@example.com"), ("Kowalska", "Tarnów", "stały", None), ("Wiśniewski", "Rzeszów", "nowy", None), ("Zielińska", "Nowy Sącz", "stały", None), ("Lis", "Kraków", "nowy", None), ("Mazur", "Tarnów", "nowy", None)]
PRODUKTY = [("Python. Wprowadzenie", "książki", 59.0, 12), ("Algorytmy", "książki", 89.0, 5), ("Słuchawki", "elektronika", 249.0, 8), ("Klawiatura", "elektronika", 199.0, 0), ("Piłka", "sport", 79.0, 20), ("Klocki", "zabawki", 149.0, 6)]
ZAMOWIENIA = [(1, date(2025, 1, 4), "wysłane"), (2, date(2025, 1, 15), "wysłane"), (1, date(2025, 2, 2), "wysłane"), (3, date(2025, 2, 20), "anulowane"), (5, date(2025, 3, 3), "wysłane"), (2, date(2025, 3, 18), "nowe"), (4, date(2025, 3, 25), "nowe")]
POZYCJE = [(1, 1, 2), (1, 3, 1), (2, 5, 1), (3, 2, 1), (3, 1, 1), (4, 6, 2), (5, 3, 1), (5, 5, 2), (6, 1, 3), (7, 6, 1), (7, 2, 1)]


def utworz_silnik(adres):
    silnik = create_engine(adres)

    @event.listens_for(silnik, "connect")
    def wlacz_klucze_obce(polaczenie_dbapi, _):
        polaczenie_dbapi.execute("PRAGMA foreign_keys = ON")

    return silnik


def wypelnij(sesja):
    """Dodaje obiekty w kolejności list, więc identyfikatory są takie jak w schemacie SQL."""
    klienci = [Klient(nazwisko=n, miasto=m, segment=s, email=e) for n, m, s, e in KLIENCI]
    produkty = [Produkt(nazwa=n, kategoria=k, cena=c, stan=s) for n, k, c, s in PRODUKTY]
    sesja.add_all(klienci + produkty)
    for numer, (nr_klienta, data, status) in enumerate(ZAMOWIENIA, start=1):
        pozycje = [Pozycja(produkt=produkty[nr_produktu - 1], ilosc=ilosc, cena=produkty[nr_produktu - 1].cena) for nr_zamowienia, nr_produktu, ilosc in POZYCJE if nr_zamowienia == numer]
        sesja.add(Zamowienie(klient=klienci[nr_klienta - 1], data=data, status=status, pozycje=pozycje))
    sesja.commit()


def przygotuj(adres="sqlite:///sklep-orm.db"):
    silnik = utworz_silnik(adres)
    Baza.metadata.create_all(silnik)
    with Session(silnik) as sesja:
        if sesja.scalar(select(func.count()).select_from(Klient)) == 0:
            wypelnij(sesja)
    return silnik
```

```python title="wypelnij.py"
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from dane_przykladowe import przygotuj
from modele import Klient, Pozycja, Produkt, Zamowienie

Path("sklep-orm.db").unlink(missing_ok=True)
silnik = przygotuj()
silnik = przygotuj()
with Session(silnik) as sesja:
    print([sesja.scalar(select(func.count()).select_from(tabela)) for tabela in (Klient, Produkt, Zamowienie, Pozycja)])
    print(sesja.get(Zamowienie, 1), sesja.get(Zamowienie, 1).pozycje)
```

```{ .text .no-copy }
[6, 6, 7, 11]
Zamowienie(id=1, data=2025-01-04, status='wysłane') [Pozycja(produkt_id=1, ilosc=2), Pozycja(produkt_id=3, ilosc=1)]
```

Dane z poprzedniego podrozdziału wracają jako obiekty: zamówienie dostaje obiekt klienta w argumencie `klient` i listę pozycji w `pozycje` — klucze obce i identyfikatory SQLAlchemy uzupełnia sam przy zapisie. SQLAlchemy wstawia obiekty jednej klasy w kolejności dodania do sesji — także tych, które trafiły do niej kaskadą — dlatego klientów i produkty dodajemy jawnie przed zamówieniami; gdyby weszły do sesji kaskadą przez relacje, kolejność `INSERT` wynikałaby z kolejności napotkania i numery różniłyby się od schematu SQL. Moduł `dane_przykladowe.py` służy kolejnym stronom i testom: `utworz_silnik()` włącza klucze obce na każdym nowym połączeniu (zdarzenie `connect` — odpowiednik `PRAGMA` z poprzedniego podrozdziału), a `przygotuj()` jest idempotentne: tworzy tabele i wypełnia je tylko wtedy, gdy są puste, więc drugie wywołanie niczego nie dubluje.

## Sesja i cykl życia obiektu

```python title="sesja.py"
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from dane_przykladowe import przygotuj
from modele import Klient

silnik = przygotuj()
with Session(silnik) as sesja:
    kaczmarek = Klient(nazwisko="Kaczmarek", miasto="Kielce")
    stan = inspect(kaczmarek)
    print(kaczmarek, stan.transient)
    sesja.add(kaczmarek)
    print(stan.pending, kaczmarek.id, sesja.new)
    sesja.flush()
    print(stan.persistent, kaczmarek.id, kaczmarek.segment)
    sesja.commit()
    print(stan.expired)
    print(kaczmarek.nazwisko, stan.expired)
    kaczmarek.miasto = "Radom"
    print(sesja.dirty)
    sesja.commit()
    print(sesja.get(Klient, 7).miasto)
    sesja.delete(kaczmarek)
    print(sesja.deleted)
    sesja.commit()
    print(stan.detached, sesja.get(Klient, 7))
```

```{ .text .no-copy }
Klient(id=None, nazwisko='Kaczmarek') True
True None IdentitySet([Klient(id=None, nazwisko='Kaczmarek')])
True 7 nowy
True
Kaczmarek False
IdentitySet([Klient(id=7, nazwisko='Kaczmarek')])
Radom
IdentitySet([Klient(id=7, nazwisko='Kaczmarek')])
True None
```

**Sesja** (ang. *session*) to jednostka pracy z bazą (ang. *unit of work*): śledzi obiekty, gromadzi zmiany i wysyła je do bazy w jednej transakcji. Obiekt przechodzi stany: **przejściowy** (`transient`) po utworzeniu (baza o nim nie wie), **oczekujący** (`pending`) po `add()` (w `sesja.new`), **trwały** (`persistent`) po `flush()`, gdy `INSERT` trafił do bazy i obiekt dostał klucz — `commit()` wykonuje `flush()` sam, więc zwykle go nie wywołujemy — oraz **odłączony** (`detached`) po usunięciu lub zamknięciu sesji. Wartość domyślna `segment` pojawia się dopiero po zapisie. Po `commit()` sesja **wygasza** atrybuty obiektów (`expired`): kolejny odczyt pobiera aktualne dane z bazy. Zmianę atrybutu sesja zauważa sama (`sesja.dirty`) i zapisuje jako `UPDATE` przy następnym `commit()`; `delete()` planuje `DELETE`. `Session(silnik)` w bloku `with` zamyka sesję na końcu — bez `commit()` niezapisane zmiany przepadają.

## Zapytania `select()`

```python title="zapytania-orm.py"
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from dane_przykladowe import przygotuj
from modele import Klient, Produkt

silnik = przygotuj()
with Session(silnik) as sesja:
    print(sesja.scalars(select(Klient).order_by(Klient.nazwisko)).all())
    print(sesja.scalar(select(Klient).where(Klient.nazwisko == "Nowak")))
    zapytanie = select(Klient).where(Klient.miasto == "Kraków", Klient.segment == "nowy")
    print(zapytanie)
    print(sesja.scalars(zapytanie).all())
    print(sesja.execute(select(Klient.nazwisko, Klient.miasto).where(Klient.miasto.in_(["Tarnów", "Rzeszów"]))).all())
    print(sesja.execute(select(Klient.miasto, func.count()).group_by(Klient.miasto).order_by(Klient.miasto)).all())
    print(sesja.scalar(select(func.count()).select_from(Produkt).where(Produkt.stan == 0)))
    print(sesja.scalars(select(Produkt.nazwa).where(Produkt.nazwa.like("%a")).order_by(Produkt.cena.desc())).all())
    print(sesja.execute(select(Produkt.kategoria, func.avg(Produkt.cena).label("srednia")).group_by(Produkt.kategoria).having(func.count() > 1)).mappings().all())
    print(sesja.get(Produkt, 3), sesja.get(Produkt, 99))
```

```{ .text .no-copy }
[Klient(id=2, nazwisko='Kowalska'), Klient(id=5, nazwisko='Lis'), Klient(id=6, nazwisko='Mazur'), Klient(id=1, nazwisko='Nowak'), Klient(id=3, nazwisko='Wiśniewski'), Klient(id=4, nazwisko='Zielińska')]
Klient(id=1, nazwisko='Nowak')
SELECT klienci.id, klienci.nazwisko, klienci.miasto, klienci.segment, klienci.email 
FROM klienci 
WHERE klienci.miasto = :miasto_1 AND klienci.segment = :segment_1
[Klient(id=5, nazwisko='Lis')]
[('Kowalska', 'Tarnów'), ('Wiśniewski', 'Rzeszów'), ('Mazur', 'Tarnów')]
[('Kraków', 2), ('Nowy Sącz', 1), ('Rzeszów', 1), ('Tarnów', 2)]
1
['Klawiatura', 'Piłka']
[{'kategoria': 'elektronika', 'srednia': 224.0}, {'kategoria': 'książki', 'srednia': 74.0}]
Produkt(id=3, nazwa='Słuchawki', stan=8) None
```

`select()` buduje zapytanie z klas i ich atrybutów: `where()` przyjmuje warunki jako wyrażenia Pythona (`==`, `in_()`, `like()`, kilka warunków to koniunkcja), `order_by()`, `group_by()` i `having()` odpowiadają klauzulom SQL, a `func` udostępnia funkcje agregujące. Wypisanie zapytania pokazuje SQL, który powstanie — z parametrami zamiast wartości, więc wstrzyknięcie z podrozdziału o `sqlite3` jest tu niemożliwe. Wykonanie zależy od tego, czego chcemy: `scalars()` daje obiekty (albo pojedyncze wartości, gdy wybrano jedną kolumnę), `scalar()` — pierwszą wartość pierwszego wiersza, `execute()` — wiersze podobne do krotek, z `mappings()` jako słowniki. `get()` pobiera obiekt po kluczu głównym i zwraca `None`, gdy go nie ma.

## Błędy i wycofanie

```python title="bledy-orm.py"
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dane_przykladowe import przygotuj
from modele import Klient

silnik = przygotuj()
with Session(silnik) as sesja:
    sesja.add(Klient(nazwisko="Dubel", miasto="Kraków", email="nowak@example.com"))
    try:
        sesja.commit()
    except IntegrityError as blad:
        sesja.rollback()
        print("IntegrityError:", blad.orig)
    print(sesja.scalar(select(func.count()).select_from(Klient)))
    nowak = sesja.get(Klient, 1)
print(nowak.nazwisko)
try:
    print(nowak.zamowienia)
except Exception as blad:
    print(type(blad).__name__, "—", str(blad)[:60])
```

```{ .text .no-copy }
IntegrityError: UNIQUE constraint failed: klienci.email
6
Nowak
DetachedInstanceError — Parent instance <Klient at 0x1debc3ef250> is not bound to a 
```

Błąd bazy dociera jako wyjątek SQLAlchemy z oryginalnym wyjątkiem sterownika w `orig`; po nim sesja jest w stanie błędu i wymaga `rollback()`, które usuwa też odrzucony obiekt. Obiekt pobrany w sesji żyje po jej zamknięciu — atrybuty już wczytane i niewygaszone przez `commit()` są dostępne — ale relacji nieodczytanej wcześniej nie da się doczytać bez sesji (`DetachedInstanceError`). Stąd reguła: zapytania i praca na obiektach mieszczą się w bloku sesji, a poza nim wychodzą tylko dane, nie obiekty ORM; jak to zorganizować w aplikacji, pokazuje ostatni podrozdział.
