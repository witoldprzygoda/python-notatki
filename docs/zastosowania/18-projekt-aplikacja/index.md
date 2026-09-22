# 18. Projekt: aplikacja z bazą, API i oknem

Ścieżka Aplikacje dała pięć elementów: warstwę danych na SQLAlchemy (rozdział 13), protokół HTTP z klientem httpx (14), usługę FastAPI (15), okno w tkinter i CustomTkinter (16) oraz pakowanie (17). Projekt składa je w jeden program o **architekturze warstwowej** (ang. *layered architecture*): baza danych, nad nią usługa API, a z usługą komunikuje się okno klienta — przez sieć, jak każdy inny program. Sklep z rozdziału 13 staje się pakietem `sklep` z dwoma poleceniami: `sklep-serwer` uruchamia usługę nad bazą SQLite, `sklep` otwiera okno, w którym użytkownik wybiera klienta, dodaje produkty do koszyka i składa zamówienie.

```{ .text .no-copy }
okno (CustomTkinter)  ──HTTP/JSON──▶  usługa (FastAPI)  ──sesja──▶  baza (SQLAlchemy, SQLite)
 okno.py, klient.py                       api.py                     modele.py, operacje.py
```

Podział na warstwy ma cenę — dwa procesy zamiast jednego (SQLite działa w procesie usługi), umowa interfejsu (ang. *API contract*) do utrzymania — i zysk: każdą warstwę można testować, wymieniać i uruchamiać osobno. Okno nie zna SQL-a, usługa nie zna widżetów, a ta sama usługa obsłuży inne okno, skrypt albo przeglądarkę.

Rozdział buduje na rozdziałach 13–17 tej części: kod warstwy danych i usługi pochodzi z rozdziałów 13 i 15 (ze zmianami omówionymi na następnej stronie), klient API ze wzorca rozdziału 14, okno z rozdziału 16, a pakiet, punkty wejścia i plik wykonywalny z rozdziału 17. Z części „Python Notatki” korzysta z rozdziałów 7 (`__main__`, argumenty), 15 (wątki) i 16 (pytest). Wersje bibliotek jak w tamtych rozdziałach; plik wymagań narzędzi:

```text title="requirements.txt"
pytest==9.1.1
httpx2==2.13.0
build==1.6.1
pyinstaller==6.22.3
```

Zależności samego pakietu — SQLAlchemy, FastAPI, uvicorn, httpx, CustomTkinter — deklaruje `pyproject.toml` i instaluje je `python -m pip install -e .`; plików do pobrania nie ma, bazę wypełniają dane przykładowe z rozdziału 13.

---

## W tym rozdziale

1. [Serwer: baza i API](serwer.md) — układ pakietu, warstwa danych z rozdziału 13, usługa API, pierwsze żądania
2. [Klient: moduł API i okno](okno.md) — klient API i koszyk, okno, okno w działaniu
3. [Testy, uruchomienie i dostawa](dostawa.md) — testy, uruchomienie, dostawa, lista kontrolna ścieżki
