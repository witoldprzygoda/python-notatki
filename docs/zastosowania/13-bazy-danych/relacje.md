# Relacje i zapytania ORM

Klucz obcy w schemacie to liczba; w modelu odpowiada mu **relacja** — atrybut, pod którym zamówienie ma obiekt klienta, a klient listę zamówień. Ten podrozdział pokazuje, jak relacje działają w obie strony, kiedy SQLAlchemy je wczytuje i ile to kosztuje zapytań, oraz jak wyrazić w ORM złączenia i agregacje z podrozdziału o SQL — i sprawdzić, że dają te same liczby.

## Relacje między obiektami

```python title="relacje-obiekty.py"
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from dane_przykladowe import przygotuj
from modele import Klient, Pozycja, Produkt, Zamowienie

silnik = przygotuj()
with Session(silnik) as sesja:
    nowak = sesja.get(Klient, 1)
    print(nowak.zamowienia)
    pierwsze = nowak.zamowienia[0]
    print(pierwsze.klient is nowak, pierwsze.klient_id)
    print([(pozycja.produkt.nazwa, pozycja.ilosc, pozycja.cena) for pozycja in pierwsze.pozycje])
    mazur = sesja.scalar(select(Klient).where(Klient.nazwisko == "Mazur"))
    pilka, klocki = sesja.get(Produkt, 5), sesja.get(Produkt, 6)
    nowe = Zamowienie(klient=mazur, data=date(2025, 4, 1), pozycje=[Pozycja(produkt=pilka, ilosc=2, cena=pilka.cena), Pozycja(produkt=klocki, ilosc=1, cena=klocki.cena)])
    print(nowe in sesja, nowe.id)
    sesja.add(nowe)
    print(nowe in sesja, nowe.pozycje[0] in sesja, mazur.zamowienia)
    sesja.flush()
    print(nowe.id, nowe.klient_id, [pozycja.zamowienie_id for pozycja in nowe.pozycje])
    nowe.pozycje.remove(nowe.pozycje[0])
    sesja.flush()
    print(sesja.scalar(select(Pozycja).where(Pozycja.zamowienie_id == nowe.id)))
    sesja.rollback()
    print(mazur.zamowienia, sesja.get(Zamowienie, 8))
```

```{ .text .no-copy }
[Zamowienie(id=1, data=2025-01-04, status='wysłane'), Zamowienie(id=3, data=2025-02-02, status='wysłane')]
True 1
[('Python. Wprowadzenie', 2, 59.0), ('Słuchawki', 1, 249.0)]
False None
True True [Zamowienie(id=8, data=2025-04-01, status='nowe')]
8 6 [8, 8]
Pozycja(produkt_id=6, ilosc=1)
[] None
```

`relationship()` po obu stronach z `back_populates` tworzy parę atrybutów, które SQLAlchemy utrzymuje w zgodzie: przypisanie klienta do zamówienia dopisuje zamówienie do listy `klient.zamowienia`. Nowe zamówienie trzeba dodać do sesji jawnie — samo powiązanie z trwałym klientem tego nie robi — ale wraz z dodanym obiektem do sesji trafiają pozycje z listy `pozycje`: to **kaskada** zapisu. Klucze obce i identyfikatory pojawiają się przy `flush()` — tu już przed jawnym wywołaniem, bo odczyt listy `mazur.zamowienia` wymaga zapytania, a przed każdym zapytaniem sesja sama wykonuje `flush()` (ang. *autoflush*). Opcja `cascade="all, delete-orphan"` na liście pozycji oznacza, że pozycja należy do zamówienia: usunięta z listy zostaje usunięta z bazy, a usunięcie zamówienia usuwa jego pozycje. `rollback()` cofa wszystko od ostatniego `commit()`, więc zamówienie Mazura znika, a dane rozdziału pozostają niezmienione dla kolejnych skryptów.

## Ładowanie i problem N+1

```python title="ladowanie.py"
from sqlalchemy import event, select
from sqlalchemy.orm import Session, joinedload, selectinload

from dane_przykladowe import przygotuj
from modele import Zamowienie

silnik = przygotuj()
licznik = {"zapytania": 0}


@event.listens_for(silnik, "before_cursor_execute")
def policz(*_):
    licznik["zapytania"] += 1


def nazwiska(zamowienia):
    return [zamowienie.klient.nazwisko for zamowienie in zamowienia]


with Session(silnik) as sesja:
    licznik["zapytania"] = 0
    zamowienia = sesja.scalars(select(Zamowienie)).all()
    po_wczytaniu = licznik["zapytania"]
    print(nazwiska(zamowienia), po_wczytaniu, licznik["zapytania"])
with Session(silnik) as sesja:
    licznik["zapytania"] = 0
    zamowienia = sesja.scalars(select(Zamowienie).options(selectinload(Zamowienie.klient), selectinload(Zamowienie.pozycje))).all()
    print(nazwiska(zamowienia), [len(zamowienie.pozycje) for zamowienie in zamowienia], licznik["zapytania"])
with Session(silnik) as sesja:
    licznik["zapytania"] = 0
    zamowienia = sesja.scalars(select(Zamowienie).options(joinedload(Zamowienie.klient))).all()
    print(nazwiska(zamowienia), licznik["zapytania"])
print(select(Zamowienie).options(joinedload(Zamowienie.klient)))
```

```{ .text .no-copy }
['Nowak', 'Kowalska', 'Nowak', 'Wiśniewski', 'Lis', 'Kowalska', 'Zielińska'] 1 6
['Nowak', 'Kowalska', 'Nowak', 'Wiśniewski', 'Lis', 'Kowalska', 'Zielińska'] [2, 1, 2, 1, 2, 1, 2] 3
['Nowak', 'Kowalska', 'Nowak', 'Wiśniewski', 'Lis', 'Kowalska', 'Zielińska'] 1
SELECT zamowienia.id, zamowienia.klient_id, zamowienia.data, zamowienia.status, klienci_1.id AS id_1, klienci_1.nazwisko, klienci_1.miasto, klienci_1.segment, klienci_1.email 
FROM zamowienia LEFT OUTER JOIN klienci AS klienci_1 ON klienci_1.id = zamowienia.klient_id
```

Domyślnie relacja jest ładowana **leniwie** (ang. *lazy loading*): zapytanie o zamówienia pobiera tylko zamówienia, a klient każdego z nich jest doczytywany osobnym zapytaniem przy pierwszym dostępie — siedem zamówień pięciu klientów to jedno zapytanie plus pięć, bo sesja pamięta raz wczytane obiekty. Przy tysiącach wierszy ten **problem N+1** zamienia jedną odpowiedź bazy w tysiąc. `options()` zapytania zmienia strategię: `selectinload()` doczytuje całą relację jednym dodatkowym zapytaniem `WHERE … IN (…)`, `joinedload()` dołącza tabelę złączeniem `LEFT OUTER JOIN` w tym samym zapytaniu. Pierwsza jest dobra dla list (pozycje), druga dla pojedynczych obiektów (klient); obie deklarujemy tam, gdzie wiemy, co będzie potrzebne. Licznik na zdarzeniu `before_cursor_execute` to prosty sposób, by zobaczyć, ile zapytań naprawdę wykonuje kod.

## Złączenia i agregacje

```python title="agregacje-orm.py"
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from dane_przykladowe import przygotuj
from modele import Klient, Pozycja, Produkt, Zamowienie

silnik = przygotuj()
wartosc = func.sum(Pozycja.ilosc * Pozycja.cena).label("wartosc")
with Session(silnik) as sesja:
    wartosc_zamowien = select(Zamowienie.id, Klient.nazwisko, Zamowienie.data, wartosc).join(Zamowienie.klient).join(Zamowienie.pozycje).where(Zamowienie.status != "anulowane").group_by(Zamowienie.id).order_by(Zamowienie.data)
    print(wartosc_zamowien)
    for wiersz in sesja.execute(wartosc_zamowien).mappings():
        print(dict(wiersz))
    zamowien_klienta = select(Klient.nazwisko, func.count(Zamowienie.id).label("zamowien")).join(Klient.zamowienia, isouter=True).group_by(Klient.id).order_by(func.count(Zamowienie.id).desc(), Klient.nazwisko)
    print(sesja.execute(zamowien_klienta).all())
    przychod_kategorii = select(Produkt.kategoria, wartosc).join(Pozycja.produkt).join(Pozycja.zamowienie).where(Zamowienie.status != "anulowane").group_by(Produkt.kategoria).having(wartosc > 200).order_by(wartosc.desc())
    print(sesja.execute(przychod_kategorii).all())
    print(sesja.execute(select(func.strftime("%Y-%m", Zamowienie.data), func.count()).group_by(func.strftime("%Y-%m", Zamowienie.data))).all())
    sredni_stan = select(func.avg(Produkt.stan)).scalar_subquery()
    print(sesja.execute(select(Produkt.nazwa, Produkt.stan).where(Produkt.stan < sredni_stan).order_by(Produkt.stan)).all())
    print(sesja.scalars(select(Klient.nazwisko).where(~Klient.zamowienia.any())).all())
```

```{ .text .no-copy }
SELECT zamowienia.id, klienci.nazwisko, zamowienia.data, sum(pozycje.ilosc * pozycje.cena) AS wartosc 
FROM zamowienia JOIN klienci ON klienci.id = zamowienia.klient_id JOIN pozycje ON zamowienia.id = pozycje.zamowienie_id 
WHERE zamowienia.status != :status_1 GROUP BY zamowienia.id ORDER BY zamowienia.data
{'id': 1, 'nazwisko': 'Nowak', 'data': datetime.date(2025, 1, 4), 'wartosc': 367.0}
{'id': 2, 'nazwisko': 'Kowalska', 'data': datetime.date(2025, 1, 15), 'wartosc': 79.0}
{'id': 3, 'nazwisko': 'Nowak', 'data': datetime.date(2025, 2, 2), 'wartosc': 148.0}
{'id': 5, 'nazwisko': 'Lis', 'data': datetime.date(2025, 3, 3), 'wartosc': 407.0}
{'id': 6, 'nazwisko': 'Kowalska', 'data': datetime.date(2025, 3, 18), 'wartosc': 177.0}
{'id': 7, 'nazwisko': 'Zielińska', 'data': datetime.date(2025, 3, 25), 'wartosc': 238.0}
[('Kowalska', 2), ('Nowak', 2), ('Lis', 1), ('Wiśniewski', 1), ('Zielińska', 1), ('Mazur', 0)]
[('książki', 532.0), ('elektronika', 498.0), ('sport', 237.0)]
[('2025-01', 2), ('2025-02', 2), ('2025-03', 3)]
[('Klawiatura', 0), ('Algorytmy', 5), ('Klocki', 6), ('Słuchawki', 8)]
['Mazur']
```

Złączenie po relacji — `join(Zamowienie.klient)` — nie wymaga warunku `ON`, bo SQLAlchemy zna klucz obcy; `isouter=True` daje `LEFT OUTER JOIN`. Wyrażenie agregujące przypisane do zmiennej (`wartosc`) służy naraz w `select()`, `having()` i `order_by()`, a `label()` nadaje mu nazwę kolumny. `scalar_subquery()` zamienia zapytanie w wartość do warunku, `Klient.zamowienia.any()` z negacją wybiera klientów bez zamówień — czytelniej niż `NOT IN`. Liczby są zgodne z podrozdziałem o SQL: ORM generuje zapytania, których nie trzeba pisać, ale które wciąż warto umieć przeczytać — `print()` zapytania pokazuje, co pójdzie do bazy.

## Zmiany i usuwanie

```python title="zmiany-orm.py"
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dane_przykladowe import przygotuj
from modele import Pozycja, Produkt, Zamowienie

silnik = przygotuj()
with Session(silnik) as sesja:
    klawiatura = sesja.scalar(select(Produkt).where(Produkt.nazwa == "Klawiatura"))
    klawiatura.stan = 4
    sesja.commit()
    wynik = sesja.execute(update(Zamowienie).where(Zamowienie.status == "nowe", Zamowienie.data < "2025-03-20").values(status="wysłane"))
    print(wynik.rowcount, sesja.scalars(select(Zamowienie.status).distinct().order_by(Zamowienie.status)).all())
    sesja.commit()
    try:
        sesja.execute(delete(Zamowienie).where(Zamowienie.status == "anulowane"))
    except IntegrityError as blad:
        sesja.rollback()
        print("IntegrityError:", blad.orig)
    anulowane = sesja.scalars(select(Zamowienie).where(Zamowienie.status == "anulowane")).all()
    for zamowienie in anulowane:
        sesja.delete(zamowienie)
    sesja.commit()
    print([sesja.scalar(select(func.count()).select_from(tabela)) for tabela in (Zamowienie, Pozycja)])
```

```{ .text .no-copy }
1 ['anulowane', 'nowe', 'wysłane']
IntegrityError: FOREIGN KEY constraint failed
[6, 10]
```

Zmiana przez obiekt (`klawiatura.stan = 4`) to `UPDATE` jednego wiersza przy `commit()`; instrukcje `update()` i `delete()` działają na wielu wierszach jednym zapytaniem, bez wczytywania obiektów, i zwracają `rowcount`. Instrukcja `delete()` omija jednak kaskady ORM — te są w Pythonie, nie w bazie — więc przy włączonych kluczach obcych usunięcie zamówienia z pozycjami kończy się błędem klucza obcego; `sesja.delete(obiekt)` usuwa pozycje razem z zamówieniem, jak każe kaskada `delete` zawarta w `all`. Kaskadę na poziomie bazy daje `ForeignKey(..., ondelete="CASCADE")` — jak `ON DELETE CASCADE` w schemacie SQL — wtedy zbiorowe `delete()` też działa. Po skrypcie baza ma sześć zamówień, tak jak po podrozdziale o SQL.
