# Projekt rozdziału 18 części „Python Zastosowania” — Projekt: aplikacja z bazą, API i oknem

Ostatni rozdział ścieżki Aplikacje. Branch: `content/zastosowania-18` (z `dev` po `58f769c`). Realizacja autonomiczna na polecenie autora z 23 IX 2026.

## Decyzje redakcyjne (23 IX 2026)

1. **Zakres:** jeden pakiet `sklep` (układ `src`, `pyproject.toml` z Hatchling jak w rozdziale 17) łączący ścieżkę: warstwa danych z rozdziału 13 (`modele.py`, `baza.py`, `operacje.py`, `dane_przykladowe.py` — bez zmian poza importami względnymi), usługa FastAPI z rozdziału 15 (`api.py`: silnik w cyklu życia z wypełnieniem danych przykładowych, sesja na żądanie, trasy `/produkty`, `/produkty/{id}`, `/klienci`, `/klienci/{id}/podsumowanie`, `/zamowienia`, `/zamowienia/{id}`, `/zamowienia/{id}/anulowanie`; funkcja `uruchom()` z uvicorn jako punkt wejścia `sklep-serwer`), klient API w stylu rozdziału 14 (`klient.py`: `KlientSklepu` na httpx z `BladApi`, adres z `SKLEP_ADRES`), okno klienta w CustomTkinter z rozdziału 16 (`okno.py`: tabela produktów w `ttk.Treeview`, wybór klienta, koszyk, złożenie zamówienia, podsumowanie; żądania HTTP w wątku z kolejką i `after()`; przełącznik `--zamknij-po`; punkt wejścia `sklep`), testy (API przez `TestClient` z bazą w pliku tymczasowym, logika koszyka bez okna), uruchomienie (`sklep-serwer`, `sklep`, zmienne `SKLEP_BAZA`, `SKLEP_ADRES`, `SKLEP_PORT`), dostawa (koło; `.exe` okna z PyInstaller z `--collect-all customtkinter`), README i lista kontrolna ścieżki. Trzy strony + index. Poza zakresem: uwierzytelnianie użytkowników, HTTPS, wdrożenie serwera na maszynie zdalnej (wzmianka), Alembic, aktualizacja danych na żywo (odświeżanie przyciskiem), CustomTkinter poza oknem klienta.
2. **Biblioteki i wersje (sonda 23 IX 2026):** te z rozdziałów 13–17 — SQLAlchemy 2.0.54, FastAPI 0.141.1, uvicorn 0.53.0, httpx 0.28.1, httpx2 2.13.0 (klient testowy), CustomTkinter 6.0.0, Pillow (zrzuty), pytest 9.1.1, build 1.6.1, Hatchling 1.32.4, PyInstaller 6.22.3; Python 3.14.7, Tk 9.0.4. `dependencies` pakietu jako zakresy: `fastapi>=0.141,<1`, `uvicorn>=0.53,<1`, `sqlalchemy>=2,<3`, `httpx>=0.27,<1`, `customtkinter>=6,<7`; grupa `test`: `pytest>=9`, `httpx2>=2`.
3. **Dane:** dane przykładowe sklepu z rozdziału 13 wypełniane przy starcie serwera, gdy baza jest pusta; baza `sklep.db` w katalogu roboczym (`SKLEP_BAZA`). Harness: staging pakietu z bloków (`extract_project.py`; `LICENSE` bez kropki dopisywany osobno), instalacja edytowalna do `venv-ch18`, skrypty kontrolne przez `TestClient` i uvicorn w wątku; okno pod harnessem `scripts/tk_harness/sitecustomize.py` (zrzut `img/okno.png`); `pytest` w stagingu; PyInstaller przez skrypt (`--collect-all customtkinter`, ok. 20 s).
4. **Fakty do sprawdzenia sondą:** PyInstaller z CustomTkinter (zasoby motywów — `--collect-all customtkinter`), uvicorn w wątku + okno w tym samym procesie skryptu kontrolnego, `TestClient` z bazą w `tmp_path` przez nadpisanie zależności (jak w rozdziale 15), zmienna `SKLEP_BAZA` czytana przy imporcie `baza.py` (jak w rozdziale 13 — w skryptach ustawiana przed importem), kolejność wypełniania danych w `lifespan`.
5. **Terminy:** „architektura warstwowa” (ang. *layered architecture*), „klient–serwer”, „umowa interfejsu” (ang. *API contract*), bez nowych terminów bibliotek — rozdział scala poznane.
6. Odsyłacze wstecz: „Python Zastosowania” 13 (warstwa danych), 14 (klient API, `BladApi`, ponawianie), 15 (API, sesja na żądanie, `TestClient`, `dependency_overrides`), 16 (CustomTkinter, wątek + kolejka + `after`, `--zamknij-po`), 17 (pakiet, punkty wejścia, PyInstaller, zmienne środowiskowe); „Python Notatki” 7 (`__main__`), 15 (wątki), 16 (pytest). Zapowiedź: ścieżka Automatyzacja (rozdział 19) — `TODO`.
7. Domknięcia: markery „projekcie aplikacji” w 13/warstwa-danych, 14/api, 15/testy-i-uruchomienie, 16/projekt-kontakty, 17/aplikacja-dla-uzytkownika → `18-projekt-aplikacja/index.md`; strona `docs/zastosowania/index.md`: ścieżka Aplikacje ukończona.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i pliki |
|---|---|---|
| `index.md` | Wprowadzenie / „18. Projekt: aplikacja z bazą, API i oknem” | cel i architektura; biblioteki; plik wymagań; ---; ## W tym rozdziale (3) |
| `serwer.md` | Serwer: baza i API | Układ pakietu (drzewo, `pyproject.toml`); Warstwa danych z rozdziału 13 (`modele.py`, `baza.py`, `operacje.py`, `dane_przykladowe.py`); Usługa API (`api.py`); Pierwsze żądania (`uzycie-api.py`) |
| `okno.md` | Klient: moduł API i okno | Klient API (`klient.py`, `uzycie-klienta.py`); Okno (`okno.py`); Okno w działaniu (`uzycie-okna.py`, zrzut) |
| `dostawa.md` | Testy, uruchomienie i dostawa | Testy (`tests/conftest.py`, `tests/test_api.py`, `tests/test_koszyk.py`, pytest); Uruchomienie (`sklep-serwer`, `sklep`, zmienne); Dostawa (koło, `zbuduj-okno.py` z PyInstaller, README); Lista kontrolna ścieżki; Dalej (TODO 19) |

Szacunek: 900–1050 linii (dużo kodu); 1 zrzut generowany harnessem.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 17)

```yaml
      - "18. Projekt: aplikacja z bazą, API i oknem":
          - Wprowadzenie: zastosowania/18-projekt-aplikacja/index.md
          - "Serwer: baza i API": zastosowania/18-projekt-aplikacja/serwer.md
          - "Klient: moduł API i okno": zastosowania/18-projekt-aplikacja/okno.md
          - Testy, uruchomienie i dostawa: zastosowania/18-projekt-aplikacja/dostawa.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `dostawa.md` | ścieżka Automatyzacja (wyrażenia regularne) | rozdział 19 |

## Domknięcia

| Plik | Cel |
|---|---|
| 13/warstwa-danych, 14/api, 15/testy-i-uruchomienie, 16/projekt-kontakty, 17/aplikacja-dla-uzytkownika (marker projekt aplikacji) | `18-projekt-aplikacja/index.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/`; projekt scala rozdziały 13–17 tej części.

## Listy kontrolne

- Przed commitem: staging z bloków + LICENSE; `pip install -e stage18[test]`; `refresh_outputs.py` (z `PYTHONPATH=scripts/tk_harness` i `ZRZUTY_KATALOG` dla strony okna); `verify_page.py` dwa przebiegi (`--skip` modułów pakietu i testów); pytest w stagingu; oba buildy `--strict`; cudzysłowy; kolokwializmy; recenzje z weryfikacją uwag.
- Po commicie: domknięcia w rozdziałach 13–17, status w `PLAN_ZASTOSOWANIA.md` i „Ścieżka Aplikacje ukończona”, strony indeksowe, integracja do `dev`, pamięć, raport.
