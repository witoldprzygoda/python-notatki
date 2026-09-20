# Projekt rozdziału 15 części „Python Zastosowania” — FastAPI

Trzeci rozdział ścieżki Aplikacje. Branch: `content/zastosowania-15` (z `dev` po `447e21e`). Realizacja autonomiczna na polecenie autora z 20 IX 2026.

## Decyzje redakcyjne (20 IX 2026)

1. **Zakres:** pierwsza aplikacja (obiekt `FastAPI`, dekoratory tras, parametry ścieżki i zapytania z typami, automatyczne `422`, `HTTPException`, uruchomienie `python -m uvicorn`, dokumentacja `/docs` i `/openapi.json`, klient testowy `TestClient`); modele danych Pydantic (`BaseModel`, `Field` z ograniczeniami, koercja typów, `ValidationError`, `model_dump`/`model_validate`, `extra="forbid"`, `field_validator`, treść żądania, `response_model`, modele zagnieżdżone, schematy w OpenAPI); serwer sklepu (port serwera z rozdziału 14: trasy w `APIRouter`, własny wyjątek z `exception_handler` dający kształt `{"blad": …}`, klucz API jako zależność `Depends` z `Header`, `201` z `Location`, `503` z `Retry-After`, CSV; klient `sklep_api.py` z rozdziału 14 wobec nowego serwera przez prawdziwe HTTP — uvicorn w wątku); API nad warstwą danych z rozdziału 13 (silnik w `lifespan`, sesja na żądanie jako zależność z `yield` i `Sesja.begin()`, schematy `from_attributes`, tłumaczenie `BrakTowaru`/`ValueError` na kody, zamówienie z koszykiem; model uczenia maszynowego za API — klasyfikator irysów ładowany przy starcie, `/przewiduj`); testy i uruchomienie (pytest z `TestClient`, nadpisanie zależności sesji bazą w pliku tymczasowym `tmp_path`, `pyproject.toml` z filtrem ostrzeżenia biblioteki; `uvicorn` z opcjami `--reload`, `--host`, `--port`, `--workers`, dziennik żądań, konfiguracja zmiennymi środowiskowymi; lista kontrolna). Pięć stron + index. Poza zakresem: `async def` i biblioteki asynchroniczne (wzmianka), formularze i pliki, ciasteczka i logowanie użytkowników, OAuth2/JWT, CORS, WebSocket, szablony HTML, wdrożenie za serwerem pośredniczącym i HTTPS (wzmianka), Alembic.
2. **Biblioteki i wersje (sonda 20 IX 2026, Python 3.14.7):** FastAPI 0.141.1, Pydantic 2.13.5, Starlette 1.6.0, uvicorn 0.53.0, httpx 0.28.1 (klient z rozdziału 14), **httpx2 2.13.0** — Starlette 1.x buduje `TestClient` na pakiecie `httpx2` (następca httpx wydany pod nową nazwą, ten sam autor); z samym httpx 0.28 działa, ale zgłasza ostrzeżenie o wycofaniu. `scikit-learn 1.9.1` tylko dla sekcji „Model za API”. Plik wymagań: pandas, pytest, sqlalchemy, httpx + `fastapi==0.141.1`, `uvicorn==0.53.0`, `httpx2==2.13.0`, `scikit-learn==1.9.1` (ostatni oznaczony jako opcjonalny). Uruchomienie serwera przez `python -m uvicorn` (nie `fastapi dev`, który wymaga dodatku `fastapi[standard]` — wzmianka).
3. **Dane:** sklep w pamięci (trzy produkty jak w rozdziale 14) na stronach 1–3; na stronach 4–5 moduły warstwy danych z rozdziału 13 (`modele.py`, `baza.py`, `operacje.py`, `dane_przykladowe.py`) w tym samym katalogu, baza `sklep-orm.db` odtwarzana przez skrypt; na stronie 3 moduł `sklep_api.py` z rozdziału 14. Harness: `--data=` z kopią tych modułów (staging z bloków rozdziałów 13 i 14). Skrypty wywołują aplikację przez `TestClient` (bez portu); jeden skrypt uruchamia uvicorn w wątku na porcie 8765 i zatrzymuje go (`should_exit`). Data zamówienia podawana jawnie w treści żądania (wydruk deterministyczny). Brak plików do pobrania, brak wykresów; jeden zrzut (`/docs`) jako `TODO` w `ZRZUTY.md`.
4. **Fakty sprawdzone 20 IX 2026:** parametr ścieżki z typem `int` → `422` z `detail` listą (`type`, `loc`, `msg`, `input`); `Query(ge=1, le=100)`; `HTTPException(404, detail=…)` → `{"detail": …}`; `405 Method Not Allowed`, `404 Not Found` dla nieznanych tras; `/docs` (Swagger UI), `/redoc`, `/openapi.json` z `components.schemas`; `TestClient` dziedziczy po `httpx2.Client`, `base_url` `http://testserver`; `lifespan` uruchamia się tylko w bloku `with TestClient(app)`; procedury obsługi wyjątków rejestrować przed pierwszym żądaniem (stos pośredników budowany raz); `Header()` zamienia `authorization` na nagłówek `Authorization`; `dependencies=[Depends(…)]` w dekoratorze; `response_model` filtruje pola, adnotacja zwracanego typu działa tak samo; Pydantic: `"89"` → `89.0` (koercja), `extra` ignorowane domyślnie, `ValidationError.errors()`, `error_count()`, `model_validate_json`; `from_attributes=True` w `ConfigDict` czyta obiekty ORM z relacjami (`pozycje: list[PozycjaOut]`), `date` serializowana jako ISO; `/produkty/` → `307` na `/produkty` (httpx nie podąża za przekierowaniem domyślnie); baza w pamięci `sqlite://` bez `StaticPool` daje `no such table` przy sesji na żądanie (osobne połączenia) — testy na pliku `tmp_path`; uvicorn w wątku: `Server(Config(app, port=…, log_level="warning"))`, `started`, `should_exit`; dziennik uvicorn: `INFO: 127.0.0.1:PORT - "GET / HTTP/1.1" 200 OK`; `--reload` dodaje wiersze `Will watch…`, `Started reloader process … using StatReload` (bez dodatku `uvicorn[standard]` brak watchfiles); ostrzeżenie `DeprecationWarning` z `starlette/testclient.py` (alias `anyio.abc.BlockingPortal`) widoczne tylko w podsumowaniu pytest — filtr `ignore::DeprecationWarning:starlette.testclient` w `pyproject.toml`; klient `KlientSklepu` z rozdziału 14 działa wobec aplikacji FastAPI bez zmian (błędy walidacji bez pola `blad` → opis kodu). Regresja logistyczna na irysach: setosa 0,985, virginica 0,994, versicolor 0,779.
5. **Terminy:** „framework” (ang. *web framework*), „trasa” (ang. *route*), „funkcja obsługi” (ang. *path operation function*), „parametr ścieżki/zapytania” (ang. *path/query parameter*), „walidacja” (ang. *validation*), „model danych”, „schemat” (ang. *schema*), „OpenAPI”, „zależność” (ang. *dependency*), „wstrzykiwanie zależności” (ang. *dependency injection*), „cykl życia” (ang. *lifespan*), „serwer ASGI” (ang. *Asynchronous Server Gateway Interface*), „klient testowy”, „przeładowanie” (ang. *auto-reload*), „proces roboczy” (ang. *worker*).
6. Odsyłacze wstecz: „Python Notatki” 3 (adnotacje typów), 6 (dekoratory, generatory), 8 (wyjątki, `with`), 9 (JSON, zmienne środowiskowe), 10 (klasy, własne wyjątki), 12 (klasy danych), 15 (wątki, asyncio), 16 (pytest, `pyproject.toml`, fixture `tmp_path`); „Python Zastosowania” 13 (warstwa danych), 14 (HTTP, REST, httpx, klient API), 12 (model jako pakiet — sekcja „Model za API”). Zapowiedzi: 16 (tkinter), 17 (pakowanie), 18 (projekt aplikacji) — `TODO`.
7. Domknięcia: markery „FastAPI” w 12/model-i-raport, 13/warstwa-danych, 14/api → `15-fastapi/index.md`; markery „projekt aplikacji”, „pobieranie stron”, „CLI”, tkinter zostają.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty |
|---|---|---|
| `index.md` | Wprowadzenie / „15. FastAPI” | cel; biblioteki i wersje; plik wymagań; ---; ## W tym rozdziale (5) |
| `pierwsza-aplikacja.md` | Pierwsza aplikacja | Aplikacja i trasy (`aplikacja.py`); Pierwsze żądania (`pierwsze.py`); Uruchomienie serwera (terminal `python -m uvicorn`); Dokumentacja interfejsu (`dokumentacja.py`, TODO zrzut `/docs`); Klient testowy |
| `modele.md` | Modele danych — Pydantic | Model i walidacja (`model.py`); Treść żądania i model odpowiedzi (`zamowienia.py`); Modele zagnieżdżone i schematy (`koszyk.py`) |
| `sklep.md` | Serwer sklepu | Trasy w routerach i własne błędy (`sklep_fastapi.py`); Żądania do sklepu (`zamowienia-sklep.py`); Klient z rozdziału 14 (`klient14.py`); Porównanie z `http.server` |
| `baza.md` | API nad warstwą danych | Silnik przy starcie i sesja na żądanie (`sklep_baza.py`); Zamówienia w bazie (`uzycie-baza.py`); Model za API (`model_api.py`) |
| `testy-i-uruchomienie.md` | Testy i uruchomienie | Testy z klientem testowym (`tests/conftest.py`, `tests/test_api.py`, `pyproject.toml`, pytest); Uruchomienie u odbiorcy (terminal, opcje, konfiguracja, dziennik); Lista kontrolna; Dalej (TODO 16, 17, 18) |

Szacunek: 850–1000 linii; bez wykresów.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 14)

```yaml
      - 15. FastAPI:
          - Wprowadzenie: zastosowania/15-fastapi/index.md
          - Pierwsza aplikacja: zastosowania/15-fastapi/pierwsza-aplikacja.md
          - Modele danych — Pydantic: zastosowania/15-fastapi/modele.md
          - Serwer sklepu: zastosowania/15-fastapi/sklep.md
          - API nad warstwą danych: zastosowania/15-fastapi/baza.md
          - Testy i uruchomienie: zastosowania/15-fastapi/testy-i-uruchomienie.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `testy-i-uruchomienie.md` | tkinter; pakowanie; projekt aplikacji | rozdziały 16, 17, 18 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/12-projekt-ml/model-i-raport.md` (marker FastAPI) | `15-fastapi/index.md` |
| `zastosowania/13-bazy-danych/warstwa-danych.md` (marker FastAPI) | `15-fastapi/baza.md` |
| `zastosowania/14-http-api/api.md` (marker FastAPI) | `15-fastapi/index.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/`; „Python Notatki” 16 (co-dalej) wymienia FastAPI jako pomysł na projekt — bez markera.

## Listy kontrolne

- Przed commitem: staging modułów z bloków (rozdział 15 + `modele.py`, `baza.py`, `operacje.py`, `dane_przykladowe.py` z rozdziału 13 i `sklep_api.py` z rozdziału 14); harness z `--data=staging` i interpreterem `venv-ch15`; `refresh_outputs.py`; `verify_page.py` dwa przebiegi; pytest ręcznie; oba buildy `--strict`; kotwice; cudzysłowy; kolokwializmy; recenzje z weryfikacją uwag.
- Po commicie: domknięcia w rozdziałach 12, 13, 14, status w `PLAN_ZASTOSOWANIA.md`, `ZRZUTY.md`, integracja do `dev`, pamięć, raport.
