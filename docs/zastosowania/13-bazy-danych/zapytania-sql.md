# Schemat i zapytania SQL

Jedna tabela to jeszcze nie baza danych. Sklep z rozdziałów 5–6 rozpisujemy tu na klientów, produkty, zamówienia i pozycje zamówień — cztery tabele powiązane kluczami — a pytania raportu wymagają ich łączenia i agregowania. Ten podrozdział buduje taki schemat w SQLite i pisze do niego zapytania wykonujące to, co w rozdziale 5 robiły `merge()` i `groupby()`.

## Schemat sklepu

```sql title="schemat.sql"
CREATE TABLE klienci (
    id INTEGER PRIMARY KEY,
    nazwisko TEXT NOT NULL,
    miasto TEXT NOT NULL,
    segment TEXT NOT NULL CHECK (segment IN ('stały', 'nowy'))
);
CREATE TABLE produkty (
    id INTEGER PRIMARY KEY,
    nazwa TEXT NOT NULL UNIQUE,
    kategoria TEXT NOT NULL,
    cena REAL NOT NULL CHECK (cena > 0),
    stan INTEGER NOT NULL DEFAULT 0 CHECK (stan >= 0)
);
CREATE TABLE zamowienia (
    id INTEGER PRIMARY KEY,
    klient_id INTEGER NOT NULL REFERENCES klienci(id),
    data TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'nowe'
);
CREATE TABLE pozycje (
    id INTEGER PRIMARY KEY,
    zamowienie_id INTEGER NOT NULL REFERENCES zamowienia(id) ON DELETE CASCADE,
    produkt_id INTEGER NOT NULL REFERENCES produkty(id),
    ilosc INTEGER NOT NULL CHECK (ilosc > 0),
    cena REAL NOT NULL
);
```

```python title="utworz.py"
import sqlite3
from pathlib import Path

KLIENCI = [("Nowak", "Kraków", "stały"), ("Kowalska", "Tarnów", "stały"), ("Wiśniewski", "Rzeszów", "nowy"), ("Zielińska", "Nowy Sącz", "stały"), ("Lis", "Kraków", "nowy"), ("Mazur", "Tarnów", "nowy")]
PRODUKTY = [("Python. Wprowadzenie", "książki", 59.0, 12), ("Algorytmy", "książki", 89.0, 5), ("Słuchawki", "elektronika", 249.0, 8), ("Klawiatura", "elektronika", 199.0, 0), ("Piłka", "sport", 79.0, 20), ("Klocki", "zabawki", 149.0, 6)]
ZAMOWIENIA = [(1, "2025-01-04", "wysłane"), (2, "2025-01-15", "wysłane"), (1, "2025-02-02", "wysłane"), (3, "2025-02-20", "anulowane"), (5, "2025-03-03", "wysłane"), (2, "2025-03-18", "nowe"), (4, "2025-03-25", "nowe")]
POZYCJE = [(1, 1, 2, 59.0), (1, 3, 1, 249.0), (2, 5, 1, 79.0), (3, 2, 1, 89.0), (3, 1, 1, 59.0), (4, 6, 2, 149.0), (5, 3, 1, 249.0), (5, 5, 2, 79.0), (6, 1, 3, 59.0), (7, 6, 1, 149.0), (7, 2, 1, 89.0)]

Path("sklep.db").unlink(missing_ok=True)
polaczenie = sqlite3.connect("sklep.db")
polaczenie.executescript(Path("schemat.sql").read_text(encoding="utf-8"))
with polaczenie:
    polaczenie.executemany("INSERT INTO klienci (nazwisko, miasto, segment) VALUES (?, ?, ?)", KLIENCI)
    polaczenie.executemany("INSERT INTO produkty (nazwa, kategoria, cena, stan) VALUES (?, ?, ?, ?)", PRODUKTY)
    polaczenie.executemany("INSERT INTO zamowienia (klient_id, data, status) VALUES (?, ?, ?)", ZAMOWIENIA)
    polaczenie.executemany("INSERT INTO pozycje (zamowienie_id, produkt_id, ilosc, cena) VALUES (?, ?, ?, ?)", POZYCJE)
print([wiersz[0] for wiersz in polaczenie.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")])
print([polaczenie.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0] for tabela in ("klienci", "produkty", "zamowienia", "pozycje")])
polaczenie.close()
```

```{ .text .no-copy }
['klienci', 'pozycje', 'produkty', 'zamowienia']
[6, 6, 7, 11]
```

Schemat trzymamy w osobnym pliku SQL, który `executescript()` wykonuje w całości — to jedyna metoda przyjmująca wiele poleceń naraz. Kolumna `klient_id` z `REFERENCES klienci(id)` to **klucz obcy** (ang. *foreign key*): zamówienie musi wskazywać istniejącego klienta, a pozycja — istniejące zamówienie i produkt; `ON DELETE CASCADE` każe usuwać pozycje razem z zamówieniem. `CHECK` ogranicza wartości (segment z listy, cena dodatnia, stan nieujemny), `DEFAULT` podaje wartość dla pominiętej kolumny. Pozycja zapamiętuje cenę z chwili zakupu, bo cena produktu może się zmienić, a wartość starych zamówień nie powinna. Tabela `sqlite_master` opisuje schemat bazy — tak sprawdzamy, co w niej jest.

## Ograniczenia

```python title="ograniczenia.py"
import sqlite3

polaczenie = sqlite3.connect("sklep.db")
print(polaczenie.execute("PRAGMA foreign_keys").fetchone())
polaczenie.execute("INSERT INTO zamowienia (klient_id, data) VALUES (99, '2025-04-01')")
print(polaczenie.execute("SELECT COUNT(*) FROM zamowienia WHERE klient_id = 99").fetchone()[0])
polaczenie.rollback()
polaczenie.execute("PRAGMA foreign_keys = ON")
for zapytanie in (
    "INSERT INTO zamowienia (klient_id, data) VALUES (99, '2025-04-01')",
    "INSERT INTO klienci (nazwisko, miasto, segment) VALUES ('Kaczmarek', 'Kielce', 'vip')",
    "UPDATE produkty SET stan = stan - 1 WHERE nazwa = 'Klawiatura'",
    "DELETE FROM klienci WHERE id = 1",
):
    try:
        polaczenie.execute(zapytanie)
    except sqlite3.IntegrityError as blad:
        print("IntegrityError:", blad)
polaczenie.execute("DELETE FROM zamowienia WHERE id = 4")
print(polaczenie.execute("SELECT COUNT(*) FROM pozycje").fetchone()[0])
polaczenie.rollback()
print(polaczenie.execute("SELECT COUNT(*) FROM pozycje").fetchone()[0])
polaczenie.close()
```

```{ .text .no-copy }
(0,)
1
IntegrityError: FOREIGN KEY constraint failed
IntegrityError: CHECK constraint failed: segment IN ('stały', 'nowy')
IntegrityError: CHECK constraint failed: stan >= 0
IntegrityError: FOREIGN KEY constraint failed
10
11
```

Klucze obce SQLite egzekwuje dopiero po `PRAGMA foreign_keys = ON`, które trzeba wydać na każdym połączeniu — bez tego zamówienie klienta 99 trafia do bazy bez błędu. Z włączonymi kluczami baza odrzuca zamówienie bez klienta i usunięcie klienta, do którego odwołują się zamówienia, a ograniczenia `CHECK` — segment spoza listy i ujemny stan magazynu. Wraz z anulowanym zamówieniem znika dzięki `ON DELETE CASCADE` jego jedyna pozycja — pozycji zostaje 10; `rollback()` cofa to wszystko, bo skrypt tylko sprawdza reguły. Reguły spisane w schemacie działają niezależnie od tego, który program pisze do bazy — to ich przewaga nad sprawdzaniem w kodzie.

## Złączenia i agregacje

```python title="zlaczenia.py"
import sqlite3

polaczenie = sqlite3.connect("sklep.db")
polaczenie.row_factory = sqlite3.Row
wartosc_zamowien = """
SELECT z.id, k.nazwisko, z.data, SUM(p.ilosc * p.cena) AS wartosc
FROM zamowienia z
JOIN klienci k ON k.id = z.klient_id
JOIN pozycje p ON p.zamowienie_id = z.id
WHERE z.status != 'anulowane'
GROUP BY z.id
ORDER BY z.data
"""
for wiersz in polaczenie.execute(wartosc_zamowien):
    print(dict(wiersz))
zamowien_klienta = """
SELECT k.nazwisko, COUNT(z.id) AS zamowien
FROM klienci k LEFT JOIN zamowienia z ON z.klient_id = k.id
GROUP BY k.id
ORDER BY zamowien DESC, k.nazwisko
"""
print([tuple(wiersz) for wiersz in polaczenie.execute(zamowien_klienta)])
przychod_kategorii = """
SELECT pr.kategoria, SUM(p.ilosc * p.cena) AS przychod
FROM pozycje p
JOIN produkty pr ON pr.id = p.produkt_id
JOIN zamowienia z ON z.id = p.zamowienie_id
WHERE z.status != 'anulowane'
GROUP BY pr.kategoria
HAVING przychod > 200
ORDER BY przychod DESC
"""
print([tuple(wiersz) for wiersz in polaczenie.execute(przychod_kategorii)])
print([tuple(wiersz) for wiersz in polaczenie.execute("SELECT strftime('%Y-%m', data) AS miesiac, COUNT(*) FROM zamowienia GROUP BY miesiac")])
print([tuple(wiersz) for wiersz in polaczenie.execute("SELECT nazwa, stan FROM produkty WHERE stan < (SELECT AVG(stan) FROM produkty) ORDER BY stan")])
print([tuple(wiersz) for wiersz in polaczenie.execute("SELECT nazwisko FROM klienci WHERE id NOT IN (SELECT klient_id FROM zamowienia)")])
polaczenie.close()
```

```{ .text .no-copy }
{'id': 1, 'nazwisko': 'Nowak', 'data': '2025-01-04', 'wartosc': 367.0}
{'id': 2, 'nazwisko': 'Kowalska', 'data': '2025-01-15', 'wartosc': 79.0}
{'id': 3, 'nazwisko': 'Nowak', 'data': '2025-02-02', 'wartosc': 148.0}
{'id': 5, 'nazwisko': 'Lis', 'data': '2025-03-03', 'wartosc': 407.0}
{'id': 6, 'nazwisko': 'Kowalska', 'data': '2025-03-18', 'wartosc': 177.0}
{'id': 7, 'nazwisko': 'Zielińska', 'data': '2025-03-25', 'wartosc': 238.0}
[('Kowalska', 2), ('Nowak', 2), ('Lis', 1), ('Wiśniewski', 1), ('Zielińska', 1), ('Mazur', 0)]
[('książki', 532.0), ('elektronika', 498.0), ('sport', 237.0)]
[('2025-01', 2), ('2025-02', 2), ('2025-03', 3)]
[('Klawiatura', 0), ('Algorytmy', 5), ('Klocki', 6), ('Słuchawki', 8)]
[('Mazur',)]
```

**Złączenie** (ang. *join*) `JOIN … ON` łączy wiersze dwóch tabel po warunku — zwykle klucz obcy równy kluczowi głównemu — i odpowiada `merge()` z rozdziału 5; aliasy `z`, `k`, `p` skracają nazwy tabel. `GROUP BY` z funkcjami agregującymi `SUM()`, `COUNT()`, `AVG()` odpowiada `groupby()`, a `HAVING` filtruje grupy po agregacji — tu odrzuca zabawki z przychodem 149 — gdy `WHERE` filtruje wiersze przed nią. `LEFT JOIN` zachowuje klientów bez zamówień — Mazur ma zero, bo `COUNT(z.id)` nie liczy `NULL` — jak `how="left"` w pandas. Podzapytanie w nawiasach dostarcza wartość (średni stan) albo listę (klienci z zamówieniami) do warunku zewnętrznego. Baza wykonuje całość i zwraca gotowy wynik; zapytanie napisane raz służy każdemu programowi, który się do niej podłączy.

## Zmiany, indeksy i plan zapytania

```python title="zmiany.py"
import sqlite3

polaczenie = sqlite3.connect("sklep.db")
polaczenie.execute("PRAGMA foreign_keys = ON")
with polaczenie:
    print(polaczenie.execute("UPDATE zamowienia SET status = 'wysłane' WHERE status = 'nowe' AND data < '2025-03-20'").rowcount)
    print(polaczenie.execute("DELETE FROM zamowienia WHERE status = 'anulowane'").rowcount, polaczenie.execute("SELECT COUNT(*) FROM pozycje").fetchone()[0])
print(polaczenie.execute("EXPLAIN QUERY PLAN SELECT * FROM zamowienia WHERE klient_id = 1").fetchall())
polaczenie.execute("CREATE INDEX idx_zamowienia_klient ON zamowienia (klient_id)")
print(polaczenie.execute("EXPLAIN QUERY PLAN SELECT * FROM zamowienia WHERE klient_id = 1").fetchall())
print(polaczenie.execute("EXPLAIN QUERY PLAN SELECT * FROM zamowienia WHERE id = 1").fetchall())
print([wiersz[0] for wiersz in polaczenie.execute("SELECT name FROM sqlite_master WHERE type = 'index'")])
polaczenie.commit()
polaczenie.close()
```

```{ .text .no-copy }
1
1 10
[(2, 0, 216, 'SCAN zamowienia')]
[(3, 0, 61, 'SEARCH zamowienia USING INDEX idx_zamowienia_klient (klient_id=?)')]
[(2, 0, 33, 'SEARCH zamowienia USING INTEGER PRIMARY KEY (rowid=?)')]
['sqlite_autoindex_produkty_1', 'idx_zamowienia_klient']
```

`UPDATE` i `DELETE` zwracają w `rowcount` liczbę zmienionych wierszy — kontrolę, którą warto wypisać albo sprawdzić w teście; pozycja usunięta kaskadowo razem z zamówieniem nie wchodzi do tej liczby, stąd `1 10`. **Indeks** (ang. *index*) to osobna struktura, która pozwala odnaleźć wiersze po wartości kolumny bez przeglądania całej tabeli: `EXPLAIN QUERY PLAN` — istotny jest ostatni element każdej krotki, opis kroku — pokazuje, że wyszukiwanie po `klient_id` zmienia się ze `SCAN` (cała tabela) na `SEARCH … USING INDEX`, a `INTEGER PRIMARY KEY` osobnego indeksu nie potrzebuje — jest aliasem `rowid`, po którym uporządkowana jest sama tabela. Na sześciu wierszach różnicy nie widać; przy milionach indeks na kolumnach z `WHERE` i `JOIN` decyduje o czasie odpowiedzi, kosztem wolniejszego zapisu i miejsca. `UNIQUE` tworzy indeks automatycznie (`sqlite_autoindex_…`).

## SQL i pandas

```python title="pandas-sql.py"
import sqlite3

import pandas as pd

polaczenie = sqlite3.connect("sklep.db")
zamowienia = pd.read_sql("SELECT z.id, k.nazwisko, z.data, z.status FROM zamowienia z JOIN klienci k ON k.id = z.klient_id", polaczenie, parse_dates=["data"], index_col="id")
print(zamowienia.dtypes.to_dict())
print(zamowienia.groupby(zamowienia["data"].dt.month)["nazwisko"].count().to_dict())
produkty = pd.read_sql("SELECT * FROM produkty", polaczenie, index_col="id")
produkty.assign(cena_brutto=(produkty["cena"] * 1.23).round(2)).to_sql("produkty_brutto", polaczenie, if_exists="replace")
print(polaczenie.execute("SELECT nazwa, cena, cena_brutto FROM produkty_brutto ORDER BY cena_brutto DESC LIMIT 3").fetchall())
print(polaczenie.execute("SELECT sql FROM sqlite_master WHERE name = 'produkty_brutto'").fetchone()[0])
polaczenie.close()
```

```{ .text .no-copy }
{'nazwisko': <StringDtype(storage='python', na_value=nan)>, 'data': dtype('<M8[us]'), 'status': <StringDtype(storage='python', na_value=nan)>}
{1: 2, 2: 1, 3: 3}
[('Słuchawki', 249.0, 306.27), ('Klawiatura', 199.0, 244.77), ('Klocki', 149.0, 183.27)]
CREATE TABLE "produkty_brutto" (
"id" INTEGER,
  "nazwa" TEXT,
  "kategoria" TEXT,
  "cena" REAL,
  "stan" INTEGER,
  "cena_brutto" REAL
)
```

`pd.read_sql()` wykonuje zapytanie i zwraca ramkę — z datami sparsowanymi przez `parse_dates` i indeksem z `index_col` — więc obliczenia z rozdziałów 4–5 wracają tam, gdzie pandas jest wygodniejszy niż SQL; w lutym zostało jedno zamówienie, bo anulowane usunął `zmiany.py`. `to_sql()` zapisuje ramkę jako tabelę (`if_exists="replace"` nadpisuje tabelę, gdy już istnieje; domyślnie byłby to błąd); tworzy ją z typami odgadniętymi z ramki i bez ograniczeń, więc nadaje się do tabel pomocniczych i wyników, nie do schematu aplikacji. Podział ról jest naturalny: baza filtruje, łączy i agreguje duże dane, pandas dostaje już zawężony wynik do analizy i rysunków.
