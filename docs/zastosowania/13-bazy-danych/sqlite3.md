# Moduł sqlite3

SQLite przechowuje całą bazę w jednym pliku, a moduł `sqlite3` z biblioteki standardowej pozwala z nią pracować bez instalowania czegokolwiek. Ten podrozdział omawia podstawy na jednej tabeli klientów: połączenie, tworzenie tabeli, wstawianie i odczyt, parametry zapytań, typy danych oraz transakcje i błędy.

## Baza zamiast pliku

**Tabela** ma stałe kolumny o zadeklarowanych typach i wiersze, z których każdy identyfikuje **klucz główny** (ang. *primary key*). Tabelami operujemy w języku **SQL** (ang. *Structured Query Language*): `CREATE TABLE` tworzy tabelę, `INSERT` wstawia wiersze, `SELECT` odczytuje, `UPDATE` i `DELETE` zmieniają i usuwają. Każde z tych poleceń to **zapytanie** (ang. *query*), które baza wykonuje w całości, zwracając tylko to, o co poproszono — w przeciwieństwie do pliku CSV, który program musi wczytać cały, żeby znaleźć jeden wiersz.

## Połączenie i pierwsza tabela

```python title="polaczenie.py"
import sqlite3
from pathlib import Path

Path("klienci.db").unlink(missing_ok=True)
polaczenie = sqlite3.connect("klienci.db")
polaczenie.execute("CREATE TABLE klienci (id INTEGER PRIMARY KEY, nazwisko TEXT NOT NULL, miasto TEXT, email TEXT UNIQUE)")
kursor = polaczenie.execute("INSERT INTO klienci (nazwisko, miasto, email) VALUES (?, ?, ?)", ("Nowak", "Kraków", "nowak@example.com"))
print(kursor.lastrowid, polaczenie.in_transaction)
polaczenie.commit()
print(polaczenie.in_transaction, Path("klienci.db").stat().st_size)
print(polaczenie.execute("SELECT * FROM klienci").fetchall())
polaczenie.close()
```

```{ .text .no-copy }
1 True
False 12288
[(1, 'Nowak', 'Kraków', 'nowak@example.com')]
```

`sqlite3.connect()` otwiera plik bazy — tworzy go, gdy nie istnieje — i zwraca **połączenie**; `execute()` wykonuje zapytanie i zwraca **kursor** (ang. *cursor*), przez który odczytujemy wyniki i metadane, jak `lastrowid` — klucz wstawionego wiersza, nadany automatycznie kolumnie `INTEGER PRIMARY KEY`. **Ograniczenia** (ang. *constraint*) w definicji tabeli — `NOT NULL`, `UNIQUE` — baza egzekwuje sama. Zapis nie trafia do pliku od razu: przed `INSERT` moduł otwiera **transakcję** (ang. *transaction*), a dopiero `commit()` ją **zatwierdza**; bez niego zamknięcie połączenia wycofałoby zmiany. `fetchall()` zwraca listę krotek.

## Parametry zapytań

```python title="parametry.py"
import sqlite3

polaczenie = sqlite3.connect("klienci.db")
nowi = [
    {"nazwisko": "Kowalska", "miasto": "Tarnów", "email": "kowalska@example.com"},
    {"nazwisko": "Lis", "miasto": "Kraków", "email": None},
    {"nazwisko": "Mazur", "miasto": "Tarnów", "email": "mazur@example.com"},
]
polaczenie.executemany("INSERT INTO klienci (nazwisko, miasto, email) VALUES (:nazwisko, :miasto, :email)", nowi)
polaczenie.commit()
print(polaczenie.total_changes)
miasto = "Kraków"
print(polaczenie.execute("SELECT nazwisko FROM klienci WHERE miasto = ?", (miasto,)).fetchall())
podejrzane = "Kraków' OR '1'='1"
print(polaczenie.execute(f"SELECT nazwisko FROM klienci WHERE miasto = '{podejrzane}'").fetchall())
print(polaczenie.execute("SELECT nazwisko FROM klienci WHERE miasto = ?", (podejrzane,)).fetchall())
print(polaczenie.execute("SELECT nazwisko FROM klienci WHERE miasto = :m AND email IS NOT NULL", {"m": "Tarnów"}).fetchall())
polaczenie.close()
```

```{ .text .no-copy }
3
[('Nowak',), ('Lis',)]
[('Nowak',), ('Kowalska',), ('Lis',), ('Mazur',)]
[]
[('Kowalska',), ('Mazur',)]
```

Wartości do zapytania podajemy osobno, jako **parametry**: znak `?` z krotką albo `:nazwa` ze słownikiem — nigdy przez sklejanie łańcucha. Wartość wklejona f-stringiem staje się częścią SQL: tekst `Kraków' OR '1'='1` domyka apostrof i dopisuje warunek zawsze prawdziwy, więc zapytanie zwraca wszystkich klientów — to **wstrzyknięcie SQL** (ang. *SQL injection*), jedna z najczęstszych luk w programach z bazą, bo tekst pochodzi zwykle od użytkownika. Ten sam tekst przekazany jako parametr jest porównywany dosłownie i nie pasuje do niczego. `executemany()` wykonuje jedno zapytanie dla każdego elementu sekwencji w jednej transakcji, a `total_changes` liczy zmienione wiersze od otwarcia połączenia.

## Wiersze i typy

```python title="wiersze.py"
import sqlite3

polaczenie = sqlite3.connect("klienci.db")
kursor = polaczenie.execute("SELECT id, nazwisko, miasto FROM klienci ORDER BY nazwisko")
print(kursor.fetchone())
print(kursor.fetchall())
polaczenie.row_factory = sqlite3.Row
for wiersz in polaczenie.execute("SELECT * FROM klienci WHERE miasto = ?", ("Kraków",)):
    print(wiersz["nazwisko"], wiersz[2], dict(wiersz))
print(polaczenie.execute("SELECT COUNT(*) AS ile, MIN(nazwisko) AS pierwszy FROM klienci").fetchone().keys())
polaczenie.execute("CREATE TABLE pomiary (wartosc, kiedy TEXT)")
polaczenie.executemany("INSERT INTO pomiary VALUES (?, ?)", [(1, "2025-03-05"), (2.5, "2025-03-06"), ("3", "2025-03-07"), (None, "2025-03-08")])
polaczenie.commit()
for wiersz in polaczenie.execute("SELECT wartosc, typeof(wartosc), kiedy FROM pomiary"):
    print(tuple(wiersz))
print(polaczenie.execute("SELECT SUM(wartosc), date(MAX(kiedy), '+1 month'), strftime('%Y-%m', MIN(kiedy)) FROM pomiary").fetchone()[:])
polaczenie.close()
```

```{ .text .no-copy }
(2, 'Kowalska', 'Tarnów')
[(3, 'Lis', 'Kraków'), (4, 'Mazur', 'Tarnów'), (1, 'Nowak', 'Kraków')]
Nowak Kraków {'id': 1, 'nazwisko': 'Nowak', 'miasto': 'Kraków', 'email': 'nowak@example.com'}
Lis Kraków {'id': 3, 'nazwisko': 'Lis', 'miasto': 'Kraków', 'email': None}
['ile', 'pierwszy']
(1, 'integer', '2025-03-05')
(2.5, 'real', '2025-03-06')
('3', 'text', '2025-03-07')
(None, 'null', '2025-03-08')
(6.5, '2025-04-08', '2025-03')
```

Kursor zwraca wiersze po jednym (`fetchone()`), wszystkie naraz (`fetchall()`) albo w pętli `for`; `fetchall()` po `fetchone()` zwraca tylko to, czego nie pobrano wcześniej. Domyślnie wiersz jest krotką; `row_factory = sqlite3.Row` daje obiekt z dostępem po nazwie kolumny i po numerze (wycinek `[:]` daje krotkę), z `keys()` i konwersją na słownik — nazwy pochodzą z kolumn lub aliasów `AS`. SQLite typuje **dynamicznie**: typ w definicji kolumny jest tylko preferencją, a każda wartość niesie własny typ, więc kolumna bez typu przyjmie liczbę całkowitą, ułamek, tekst i `NULL`; `SUM()` mimo to zsumuje tekst `'3'` jako liczbę. Typu daty SQLite nie ma — daty przechowuje jako tekst ISO `RRRR-MM-DD`, który porównuje się i sortuje poprawnie, a funkcje `date()` i `strftime()` liczą na nim daty jak pandas w rozdziale 5.

## Transakcje i błędy

```python title="transakcje.py"
import sqlite3
from contextlib import closing

polaczenie = sqlite3.connect("klienci.db")
try:
    polaczenie.execute("INSERT INTO klienci (nazwisko, email) VALUES ('Dubel', 'nowak@example.com')")
except sqlite3.IntegrityError as blad:
    print("IntegrityError:", blad)
try:
    polaczenie.execute("INSERT INTO klienci (miasto) VALUES ('Kielce')")
except sqlite3.IntegrityError as blad:
    print("IntegrityError:", blad)
try:
    polaczenie.execute("SELECT * FROM zamowienia")
except sqlite3.OperationalError as blad:
    print("OperationalError:", blad)
try:
    with polaczenie:
        polaczenie.execute("INSERT INTO klienci (nazwisko, miasto) VALUES ('Zielińska', 'Nowy Sącz')")
        polaczenie.execute("INSERT INTO klienci (nazwisko, email) VALUES ('Dubel', 'nowak@example.com')")
except sqlite3.IntegrityError as blad:
    print("wycofane:", blad)
print(polaczenie.execute("SELECT COUNT(*) FROM klienci").fetchone()[0], polaczenie.in_transaction)
with polaczenie:
    polaczenie.execute("INSERT INTO klienci (nazwisko, miasto) VALUES ('Zielińska', 'Nowy Sącz')")
print(polaczenie.execute("SELECT COUNT(*) FROM klienci").fetchone()[0], polaczenie.in_transaction)
polaczenie.close()
try:
    polaczenie.execute("SELECT 1")
except sqlite3.ProgrammingError as blad:
    print("ProgrammingError:", blad)
with closing(sqlite3.connect(":memory:")) as tymczasowe:
    tymczasowe.execute("CREATE TABLE t (x)")
    tymczasowe.executemany("INSERT INTO t VALUES (?)", [(1,), (2,), (3,)])
    print(tymczasowe.execute("SELECT SUM(x), sqlite_version() FROM t").fetchone())
```

```{ .text .no-copy }
IntegrityError: UNIQUE constraint failed: klienci.email
IntegrityError: NOT NULL constraint failed: klienci.nazwisko
OperationalError: no such table: zamowienia
wycofane: UNIQUE constraint failed: klienci.email
4 False
5 False
ProgrammingError: Cannot operate on a closed database.
(6, '3.50.4')
```

Naruszenie ograniczenia zgłasza `IntegrityError` z nazwą reguły i kolumny, błąd w samym zapytaniu — `OperationalError`; oba dziedziczą po `sqlite3.Error`, więc obsługa z rozdziału 8 „Python Notatki” działa jak zwykle. Transakcja łączy kilka zapytań w całość: `with polaczenie:` zatwierdza ją po bloku, a przy wyjątku **wycofuje** (ang. *rollback*) — wpis Zielińskiej znika razem z błędnym duplikatem, bo albo wchodzą oba, albo żaden. Ten blok `with` nie zamyka połączenia (inaczej niż przy plikach); zamyka je `close()`, a użycie połączenia po nim to `ProgrammingError`. Zamknięcie razem z blokiem daje `closing()` z modułu `contextlib`, znanego z rozdziału 8 „Python Notatki”. Nazwa `:memory:` tworzy bazę w pamięci, która znika z połączeniem — przydatną w testach i przykładach.
