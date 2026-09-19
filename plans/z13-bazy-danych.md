# Projekt rozdziału 13 części „Python Zastosowania” — Bazy danych — `sqlite3` i SQLAlchemy

Pierwszy rozdział ścieżki Aplikacje. Branch: `content/zastosowania-13` (z `dev` po `da8e027`). Realizacja autonomiczna na polecenie autora z 19 IX 2026.

## Decyzje redakcyjne (19 IX 2026)

1. **Zakres:** moduł `sqlite3` z biblioteki standardowej (plik bazy i połączenie, `CREATE TABLE`, wstawianie z parametrami `?` i `:nazwa`, wstrzyknięcie SQL, `executemany`, `fetchone`/`fetchall`/iteracja, `sqlite3.Row`, typy dynamiczne i daty jako ISO, transakcje: `commit`, `with polaczenie:`, `IntegrityError`, `:memory:`, `closing`); schemat sklepu z czterema tabelami i zapytania SQL (klucze obce z `PRAGMA foreign_keys`, `CHECK`, `ON DELETE CASCADE`, `JOIN`/`LEFT JOIN`, `GROUP BY`/`HAVING`, podzapytania, `strftime`, `UPDATE`/`DELETE` z `rowcount`, indeks i `EXPLAIN QUERY PLAN`, `sqlite_master`, `pd.read_sql`/`to_sql`); SQLAlchemy 2.0 — silnik i `text()`, model deklaratywny (`DeclarativeBase`, `Mapped`, `mapped_column`, `ForeignKey`), `create_all` i DDL, sesja i cykl życia obiektu (przejściowy, oczekujący, trwały, odłączony; `flush`, `commit`, wygaszanie), `select()` ze `scalars`/`execute`, `func`, wypisywanie SQL z `print(stmt)`, `IntegrityError` i `rollback`; relacje (`relationship`, `back_populates`, `cascade="all, delete-orphan"`), ładowanie leniwe i problem N+1 z licznikiem zapytań przez `event`, `selectinload`/`joinedload`, złączenia i agregacje w ORM (te same liczby co w SQL), `update()`/`delete()` i granice kaskady ORM; warstwa danych aplikacji (`baza.py` z fabryką silnika, `sessionmaker`, menedżer kontekstu sesji, `operacje.py` z operacją domenową w jednej transakcji, testy pytest z bazą w pamięci, migracje — Alembic jako wzmianka, inne bazy przez URL, kiedy `sqlite3`, a kiedy ORM). Pięć stron + index. Poza zakresem: SQLAlchemy Core (`Table`/`MetaData`), asynchroniczność, Alembic w praktyce, PostgreSQL w praktyce, ORM Django.
2. **Dane:** sklep internetowy jak w rozdziałach 5–6: `klienci` (6), `produkty` (6), `zamowienia` (7), `pozycje` (11) — wpisane w skrypty (brak plików do pobrania); to samo w ORM przez `dane_przykladowe.py` z funkcją `przygotuj(url)` (idempotentną: `create_all` i wypełnienie, gdy tabela pusta). Harness: staging modułów z bloków książki (`extract_project.py`) i `--data=staging`; skrypty stron tworzą pliki `sklep.db`, `sklep-orm.db` w katalogu roboczym.
3. **Środowisko:** `venv-ch13` — Python 3.14.7, SQLite 3.50.4 (w interpreterze), SQLAlchemy 2.0.54, pandas 3.0.5, pytest 9.1.1. Plik wymagań: dopisany `sqlalchemy==2.0.54`.
4. **Fakty sprawdzone 19 IX 2026:** `sqlite3.connect()` domyślnie `autocommit=-1` (sterowanie starsze): `INSERT` otwiera transakcję (`in_transaction`), `CREATE TABLE` nie; `with polaczenie:` wycofuje przy wyjątku i nie zamyka; `executescript` zatwierdza wcześniej; `Row` ma `keys()`, indeks nazwą i numerem, `dict(row)`; komunikaty: `UNIQUE constraint failed: klienci.email`, `NOT NULL constraint failed`, `FOREIGN KEY constraint failed`, `CHECK constraint failed: …`, `no such table`, `Cannot operate on a closed database`; `PRAGMA foreign_keys` domyślnie 0; `EXPLAIN QUERY PLAN` daje `SCAN zamowienia` → `SEARCH zamowienia USING INDEX …`; `pd.read_sql` przyjmuje połączenie `sqlite3` i silnik SQLAlchemy; `to_sql` tworzy tabelę z cudzysłowami; SQLAlchemy: `print(select(...))` daje SQL z `:miasto_1`; `Mapped[date]` → typ `DATE` (tekst w SQLite); `inspect(obiekt).transient/pending/persistent`; `session.get()` zwraca `None` dla braku; `DetachedInstanceError` przy leniwym ładowaniu po zamknięciu sesji; N+1: 3 zamówienia dwóch klientów — leniwie 1 + 2 zapytania, `selectinload` 3 zapytania, `joinedload` 1; `sqlite://` w pamięci dzieli bazę między sesjami w jednym wątku (`SingletonThreadPool`); `delete(Zamowienie)` jako instrukcja nie uruchamia kaskady ORM i przy `PRAGMA foreign_keys=ON` kończy się `FOREIGN KEY constraint failed` — kaskada działa dla `sesja.delete(obiekt)`; `Sesja.begin()` z `sessionmaker` zatwierdza po bloku.
5. **Terminy:** „baza danych relacyjna”, „tabela, wiersz, kolumna”, „klucz główny” (ang. *primary key*), „klucz obcy” (ang. *foreign key*), „zapytanie” (ang. *query*), „kursor” (ang. *cursor*), „zapytanie parametryzowane”, „wstrzyknięcie SQL” (ang. *SQL injection*), „transakcja” (ang. *transaction*), „zatwierdzenie / wycofanie” (ang. *commit* / *rollback*), „złączenie” (ang. *join*), „agregacja”, „indeks”, „ORM — mapowanie obiektowo-relacyjne” (ang. *object-relational mapping*), „silnik” (ang. *engine*), „sesja” (ang. *session*), „jednostka pracy” (ang. *unit of work*), „relacja”, „ładowanie leniwe / zachłanne” (ang. *lazy / eager loading*), „problem N+1”, „migracja schematu”.
6. Odsyłacze wstecz: „Python Notatki” 8 (`with`, wyjątki), 9 (CSV/JSON, `pathlib`), 10–12 (klasy, `dataclass`, adnotacje), 16 (pytest, fixture); „Python Zastosowania” 4–5 (pandas, `merge`, `groupby`), 6 (projekt), 12 (pakiet modelu). Zapowiedzi: 14 (HTTP i API), 15 (FastAPI — sesja na żądanie), 18 (projekt aplikacji) — `TODO`.
7. Domknięcia: marker „rozdziału o bazach danych” (12/model-i-raport) → `13-bazy-danych/index.md`.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty |
|---|---|---|
| `index.md` | Wprowadzenie / „13. Bazy danych — `sqlite3` i SQLAlchemy” | cel ścieżki i rozdziału; dane; wersje i plik wymagań; ---; ## W tym rozdziale (5) |
| `sqlite3.md` | Moduł sqlite3 | Baza zamiast pliku; Połączenie i pierwsza tabela (`polaczenie.py`); Parametry zapytań (`parametry.py`); Wiersze i typy (`wiersze.py`); Transakcje i błędy (`transakcje.py`) |
| `zapytania-sql.md` | Schemat i zapytania SQL | Schemat sklepu (`schemat.sql`, `utworz.py`); Ograniczenia (`ograniczenia.py`); Złączenia i agregacje (`zlaczenia.py`); Zmiany, indeksy i plan zapytania (`zmiany.py`); SQL i pandas (`pandas-sql.py`) |
| `sqlalchemy.md` | SQLAlchemy — model i sesja | Silnik i `text()` (`silnik.py`); Model deklaratywny (`modele.py`, `ddl.py`); Dane przykładowe (`dane_przykladowe.py`, `wypelnij.py`); Sesja i cykl życia obiektu (`sesja.py`); Zapytania `select()` (`zapytania-orm.py`); Błędy i wycofanie (`bledy-orm.py`) |
| `relacje.md` | Relacje i zapytania ORM | Relacje między obiektami (`relacje-obiekty.py`); Ładowanie i problem N+1 (`ladowanie.py`); Złączenia i agregacje (`agregacje-orm.py`); Zmiany i usuwanie (`zmiany-orm.py`) |
| `warstwa-danych.md` | Warstwa danych aplikacji | Moduł bazy (`baza.py`); Operacje domenowe (`operacje.py`, `demo.py`); Testy z bazą w pamięci (`tests/conftest.py`, `tests/test_operacje.py`, pytest); Migracje i inne bazy; Kiedy `sqlite3`, a kiedy ORM; Lista kontrolna; Dalej: HTTP i API (TODO 14) |

Szacunek: 1000–1200 linii; bez wykresów.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 12)

```yaml
      - 13. Bazy danych — sqlite3 i SQLAlchemy:
          - Wprowadzenie: zastosowania/13-bazy-danych/index.md
          - Moduł sqlite3: zastosowania/13-bazy-danych/sqlite3.md
          - Schemat i zapytania SQL: zastosowania/13-bazy-danych/zapytania-sql.md
          - SQLAlchemy — model i sesja: zastosowania/13-bazy-danych/sqlalchemy.md
          - Relacje i zapytania ORM: zastosowania/13-bazy-danych/relacje.md
          - Warstwa danych aplikacji: zastosowania/13-bazy-danych/warstwa-danych.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `warstwa-danych.md` | HTTP i API; FastAPI (sesja na żądanie); projekt aplikacji | rozdziały 14, 15, 18 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/12-projekt-ml/model-i-raport.md` | `13-bazy-danych/index.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/`; „Python Notatki” 16 (co-dalej) wspomina `sqlite3` i SQLAlchemy jako tematy tej części — bez markera.

## Listy kontrolne

- Przed commitem: staging modułów z bloków; harness z `--data=staging` i interpreterem `venv-ch13`; `refresh_outputs.py`; pytest ręcznie dla bloku wyniku; dwa przebiegi weryfikacji; oba buildy `--strict`; kotwice; cudzysłowy; kolokwializmy; recenzje z weryfikacją uwag.
- Po commicie: domknięcie w rozdziale 12, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
