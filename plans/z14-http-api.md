# Projekt rozdziału 14 części „Python Zastosowania” — HTTP i API

Drugi rozdział ścieżki Aplikacje. Branch: `content/zastosowania-14` (z `dev` po `0922b34`). Realizacja autonomiczna na polecenie autora z 19 IX 2026.

## Decyzje redakcyjne (19 IX 2026)

1. **Zakres:** protokół HTTP (żądanie i odpowiedź, linia żądania, nagłówki, treść, kody stanu, metody; obserwacja na lokalnym serwerze `http.server` przez `http.client` i surowe gniazdo; adresy URL z `urllib.parse`; `HTTPStatus` i `HTTPMethod`; JSON jako treść z `urllib.request`); serwer w bibliotece standardowej (`ThreadingHTTPServer` + `BaseHTTPRequestHandler` z trasami `/produkty`, `/produkty/{id}`, `/zamowienia` (POST z kluczem `Authorization: Bearer`), `/raport.csv`, `/wolny`, `/niestabilny`; odpowiedzi JSON z kodami 200/201/400/401/404/409/422/503, `Location`, `Retry-After`; uruchomienie w wątku; klient `urllib.request` z `HTTPError`); klient httpx (`get`/`post` z `params`, `json`, `headers`; `Response`; `Client` z `base_url`, nagłówkami i limitem czasu; `raise_for_status` i `HTTPStatusError`; błędy transportu i `ReadTimeout`; `stream()` z `iter_bytes()`; prawdziwe API — kursy walut NBP); interfejs API w praktyce (zasady REST na przykładzie serwera, moduł klienta API z własnymi wyjątkami i ponawianiem po 503 z `Retry-After`, klucz z zmiennej środowiskowej, testy z `httpx.MockTransport`, lista kontrolna). Cztery strony + index. Poza zakresem: HTTPS od strony serwera, ciasteczka i sesje logowania, HTTP/2, `asyncio`/`AsyncClient`, uwierzytelnianie OAuth, WebSocket.
2. **Biblioteki:** biblioteka standardowa (`http.server`, `http.client`, `urllib`, `socket`, `json`) i **httpx 0.28.1** jako klient (wzmianka o `requests` — ten sam interfejs); FastAPI dopiero w rozdziale 15. Wersja Pythona 3.14.7.
3. **Dane:** sklep w pamięci serwera (`PRODUKTY` z trzema produktami, `ZAMOWIENIA`), klucz API `tajny-klucz`; moduły stron: `echo_serwer.py` (strona 1), `sklep_serwer.py` (strona 2, używany przez strony 3–4), `sklep_api.py` (strona 4). Port stały 8765; każdy skrypt uruchamia serwer w wątku i zatrzymuje go (`shutdown()`). Prawdziwe API: `api.nbp.pl` (bez klucza) — skrypt `kursy.py` z wynikiem z 19 IX 2026; harness: `refresh_outputs.py --skip=kursy.py`, `verify_page.py --mask` na daty i kursy. Brak plików do pobrania.
4. **Fakty sprawdzone 19 IX 2026:** `BaseHTTPRequestHandler.protocol_version` domyślnie `HTTP/1.0` — ustawiamy `HTTP/1.1` (wymaga `Content-Length`; `http.client` używa wtedy jednego połączenia dla kolejnych żądań); `send_response_only()` nie dodaje nagłówków `Server` i `Date` (deterministyczny wydruk surowej odpowiedzi), `send_response()` dodaje; `log_message()` nadpisane, by nie pisać do stderr; `http.client` wymaga ścieżki ASCII — polskie znaki kodujemy `quote()`; domyślne nagłówki `http.client`: `Host`, `Accept-Encoding: identity`; httpx: `User-Agent: python-httpx/0.28.1`, `Accept-Encoding: gzip, deflate`; na tej maszynie połączenie z zamkniętym portem lokalnym kończy się `ConnectTimeout` (nie `ConnectError`) — w tekście ogólnie `TransportError`; `HTTPStatus.UNPROCESSABLE_CONTENT` (422) istnieje w 3.14; `httpx.Response.json()`, `raise_for_status()` z komunikatem `Client error '404 Not Found' for url '…'`; `stream()` + `iter_bytes(chunk_size=8192)` na 15 600 B daje 2 porcje; `MockTransport(handler)` z `httpx.Response(status, json=...)`; NBP: `/api/exchangerates/rates/a/eur/?format=json` → `{'table': 'A', 'currency': 'euro', 'code': 'EUR', 'rates': [{'no': '182/A/NBP/2026', 'effectiveDate': '2026-09-18', 'mid': 4.3633}]}`, nieznany kod waluty → 404 z tekstem `404 NotFound - Not Found - Brak danych`, odpowiedzi gzip.
5. **Terminy:** „protokół HTTP”, „żądanie” (ang. *request*), „odpowiedź” (ang. *response*), „metoda” (ang. *method*), „kod stanu” (ang. *status code*), „nagłówek” (ang. *header*), „treść” (ang. *body*), „adres URL”, „kodowanie procentowe” (ang. *percent-encoding*), „punkt końcowy” (ang. *endpoint*), „interfejs API” (ang. *application programming interface*), „REST” (ang. *representational state transfer*), „zasób” (ang. *resource*), „klucz API / token”, „limit czasu” (ang. *timeout*), „strumieniowanie” (ang. *streaming*), „ponawianie” (ang. *retry*), „idempotentność” (ang. *idempotence*), „atrapa transportu”.
6. Odsyłacze wstecz: „Python Notatki” 8 (wyjątki, `with`), 9 (JSON, `json`), 10 (klasy, własne wyjątki), 15 (wątki, `urllib.request` w studiach wydajności), 16 (pytest, atrapy); „Python Zastosowania” 13 (warstwa danych — API w rozdziale 15 ją udostępni). Zapowiedzi: 15 (FastAPI), 18 (projekt) — `TODO`; 21 (pobieranie stron) — `TODO`.
7. Domknięcia: marker „rozdziału o HTTP i API” (13/warstwa-danych) → `14-http-api/index.md`; marker „FastAPI” w 12/model-i-raport i 13/warstwa-danych zostaje.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty |
|---|---|---|
| `index.md` | Wprowadzenie / „14. HTTP i API” | cel; biblioteki i wersje; plik wymagań; ---; ## W tym rozdziale (4) |
| `protokol.md` | Protokół HTTP | Żądanie i odpowiedź (`echo_serwer.py`, `zadanie.py`); Protokół w surowej postaci (`gniazdo.py`); Adresy URL (`adresy.py`); Metody i kody stanu (`kody.py`); Nagłówki i treść (`tresc.py`) |
| `serwer.md` | Serwer w bibliotece standardowej | Trasy i odpowiedzi JSON (`sklep_serwer.py`); Pierwsze żądania (`pierwsze.py`); Błędy jako odpowiedzi (`bledy.py`); Uruchomienie z terminala |
| `klient.md` | Klient HTTP — httpx | Żądanie GET (`zapytania.py`); Klient i połączenia (`klient.py`); Błędy sieci i limit czasu (`bledy-sieci.py`); Duże odpowiedzi (`pobieranie.py`); Prawdziwe API — kursy NBP (`kursy.py`) |
| `api.md` | Interfejs API w praktyce | Zasady REST; Moduł klienta API (`sklep_api.py`, `uzycie.py`); Testy z atrapą transportu (`tests/conftest.py`, `tests/test_sklep_api.py`, pytest); Klucze, limity i konfiguracja; Lista kontrolna; Dalej: FastAPI (TODO 15, 18) |

Szacunek: 800–950 linii; bez wykresów.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 13)

```yaml
      - 14. HTTP i API:
          - Wprowadzenie: zastosowania/14-http-api/index.md
          - Protokół HTTP: zastosowania/14-http-api/protokol.md
          - Serwer w bibliotece standardowej: zastosowania/14-http-api/serwer.md
          - Klient HTTP — httpx: zastosowania/14-http-api/klient.md
          - Interfejs API w praktyce: zastosowania/14-http-api/api.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `api.md` | FastAPI; projekt aplikacji; pobieranie stron | rozdziały 15, 18, 21 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/13-bazy-danych/warstwa-danych.md` | `14-http-api/index.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/`; „Python Notatki” 16 (co-dalej) wymienia `urllib` i FastAPI jako pomysły na projekty — bez markera.

## Listy kontrolne

- Przed commitem: staging modułów z bloków; harness z `--data=staging` i interpreterem `venv-ch14`; `refresh_outputs.py --skip=kursy.py`; wynik `kursy.py` z ręcznego uruchomienia; `verify_page.py --mask`; dwa przebiegi weryfikacji; pytest ręcznie; oba buildy `--strict`; kotwice; cudzysłowy; kolokwializmy; recenzje z weryfikacją uwag.
- Po commicie: domknięcie w rozdziale 13, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
