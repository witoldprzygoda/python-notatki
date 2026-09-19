# 13. Bazy danych — `sqlite3` i SQLAlchemy

Ścieżka aplikacji uczy budować programy, z których korzystają inni: z bazą danych, interfejsem HTTP, oknem i pakietem do instalacji. Zaczyna od bazy, bo każda aplikacja musi trwale przechowywać dane. Pliki CSV i JSON z rozdziału 9 „Python Notatki” wystarczają, dopóki dane czyta jeden program naraz, w całości i bez powiązań; gdy zamówienia odwołują się do klientów i produktów, kilka programów pisze jednocześnie, a zapis nie może zostać przerwany w połowie, potrzebna jest **relacyjna baza danych** (ang. *relational database*): tabele powiązane kluczami, język zapytań SQL i transakcje.

Rozdział pokazuje dwa poziomy pracy z bazą. Moduł `sqlite3` z biblioteki standardowej daje dostęp do **SQLite** — bazy w jednym pliku, bez serwera, wbudowanej w interpreter — i wymaga pisania SQL wprost; na nim poznajemy schemat, zapytania i transakcje. **SQLAlchemy** dokłada warstwę obiektową: tabele jako klasy, wiersze jako obiekty, zapytania jako wyrażenia Pythona — ten sam kod działa z SQLite w pliku, w pamięci na potrzeby testów i z serwerem PostgreSQL po zmianie adresu. Rozdział kończy warstwa danych małej aplikacji: moduły, operacja domenowa w jednej transakcji i testy.

Dane rozdziału to sklep internetowy z rozdziałów 5–6, tym razem w czterech tabelach — klienci, produkty, zamówienia i ich pozycje — wpisanych w skrypty; plików do pobrania nie ma. Rozdział buduje na rozdziałach 8 (`with`, wyjątki), 9 (pliki, `pathlib`), 10–12 (klasy, klasy danych) i 16 (adnotacje typów, pytest) części „Python Notatki” oraz na rozdziałach 4–5 tej części (pandas, `merge()`, `groupby()`). Wersje w chwili pisania: Python 3.14.7 z SQLite 3.50.4, SQLAlchemy 2.0.54, pandas 3.0.5, pytest 9.1.1. Plik wymagań projektu potrzebuje trzech wierszy — po ścieżce danych dopisujemy tylko ostatni:

```text title="requirements.txt"
pandas==3.0.5
pytest==9.1.1
sqlalchemy==2.0.54
```

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

---

## W tym rozdziale

1. [Moduł sqlite3](sqlite3.md) — baza zamiast pliku, połączenie i pierwsza tabela, parametry zapytań, wiersze i typy, transakcje i błędy
2. [Schemat i zapytania SQL](zapytania-sql.md) — schemat sklepu z kluczami obcymi, ograniczenia, złączenia i agregacje, zmiany, indeksy i plan zapytania, SQL i pandas
3. [SQLAlchemy — model i sesja](sqlalchemy.md) — silnik i `text()`, model deklaratywny, dane przykładowe, sesja i cykl życia obiektu, zapytania `select()`, błędy i wycofanie
4. [Relacje i zapytania ORM](relacje.md) — relacje między obiektami, ładowanie i problem N+1, złączenia i agregacje, zmiany i usuwanie
5. [Warstwa danych aplikacji](warstwa-danych.md) — moduł bazy, operacje domenowe w transakcji, testy z bazą w pamięci, migracje i inne bazy, lista kontrolna
