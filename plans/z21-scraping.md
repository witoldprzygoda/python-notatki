# Projekt rozdziału 21 części „Python Zastosowania” — Pobieranie i parsowanie stron

Trzeci rozdział ścieżki Automatyzacja. Branch: `content/zastosowania-21` (z `dev` po rozdziale 20). Realizacja autonomiczna w ramach zbiorczego polecenia autora z 23 IX 2026.

## Decyzje redakcyjne (23 IX 2026)

1. **Zakres:** budowa dokumentu HTML (elementy, atrybuty, drzewo) i parser BeautifulSoup z selektorami CSS (`select`, `select_one`, `get_text`, atrybuty, `:not`/`:has`, tabela → słownik, JSON-LD ze `<script>`), poruszanie się po drzewie (`parent`, `children`, `next_sibling`, `find`/`find_all`), wybór parsera (`html.parser` z biblioteki standardowej, `lxml`), granice wyrażeń regularnych wobec HTML (kolejność atrybutów, `>` w atrybucie, komentarze); pobieranie stron klientem httpx z rozdziału 14 (`Client` z `base_url`, nagłówek `User-Agent` z kontaktem, `timeout`, `raise_for_status`, `HTTPStatusError` a `TransportError`, kodowanie: nagłówek, `<meta charset>` przez `odpowiedz.content`); uprzejmość wobec serwera — `robots.txt` przez `urllib.robotparser`, odstęp między żądaniami, pamięć podręczna na dysku; moduł `pobieranie.py` (klasa `Pobieracz`: identyfikacja, robots, odstęp z `time.monotonic()`, pamięć podręczna, generator `strony()` z `urljoin`), moduł `rekordy.py` (lista produktów, rekord produktu, czyszczenie liczb wzorcem z rozdziału 19), zbiór do CSV/JSON z podsumowaniem; strony dynamiczne (JavaScript, wewnętrzne API, Playwright — bez kodu); narzędzie `zbieracz` z `argparse` z rozdziału 20 (adres, `-o`, `--opoznienie`, `--limit`, `--pamiec`, `-v`, kody 0/1/2) uruchamiane jako proces; testy pytest z fixture serwera; zasady prawne i etyczne (regulamin, `robots.txt`, dane osobowe, obciążenie, API zamiast HTML); lista kontrolna. Cztery strony + index. Poza zakresem: Scrapy, Selenium/Playwright (wzmianka), logowanie i formularze, asynchroniczne pobieranie, XPath, `pandas.read_html`.
2. **Biblioteki:** httpx 0.28.1 (jak w rozdziale 14), beautifulsoup4 4.15.0 (soupsieve 2.9.2), lxml 6.1.3, pytest 9.1.1. Plik wymagań z tymi wersjami. Środowisko `venv-ch21`.
3. **Dane:** strona testowa sklepu budowana skryptem `zbuduj_sklep.py` (10 produktów: dwie strony listy, strony produktów z tabelą i JSON-LD, `koszyk/`, `robots.txt` z `Disallow: /koszyk/`; jeden produkt bez ceny, jeden bez oceny, cena z separatorem tysięcy) i serwowana lokalnie modułem `sklep_serwer.py` (`ThreadingHTTPServer` na porcie losowym, cicha obsługa) — wyniki nie zawierają portu (dziennik podaje ścieżki). Harness: `zbuduj_sklep.py` uruchamiany w stagingu po ekstrakcji (katalog `sklep/` jako dane), moduły `sklep_serwer.py`, `pobieranie.py`, `rekordy.py`, `zbieracz.py`, `test_zbieracz.py` w `--skip`; narzędzie w skrypcie kontrolnym uruchamiane jako proces z połączonymi strumieniami (jak w rozdziale 20).
4. **Fakty sprawdzone 23 IX 2026 (Python 3.14.7):** `BeautifulSoup(html, "html.parser")` i `"lxml"` dają te same wyniki dla strony testowej; `select_one` zwraca `None` przy braku; `get_text(" ", strip=True)` łączy fragmenty; `tag["class"]` to lista; `BeautifulSoup("plik.html", ...)` ostrzega `MarkupResemblesLocatorWarning`; `RobotFileParser.parse()` ustawia `last_checked`, `can_fetch("zbieracz", url)` dopasowuje po pierwszym członie nazwy agenta, `crawl_delay()` zwraca `None` bez dyrektywy; httpx: `Response.encoding` z nagłówka, domyślnie `utf-8`; `raise_for_status()` → `HTTPStatusError` z `.response` i `.request`; `ConnectError`/`ConnectTimeout` są podklasami `TransportError`, wszystko pod `HTTPError`; `http.server` odpowiada `HTTP/1.0` bez `charset`; `ThreadingHTTPServer(("127.0.0.1", 0), …)` daje losowy port w `server_port`.
5. **Terminy:** „pobieranie stron” (ang. *web scraping*), „parser HTML”, „drzewo dokumentu”, „selektor CSS”, „element” i „atrybut”, „zupa” tylko jako nazwa zmiennej `zupa` (obiekt `BeautifulSoup`), „pamięć podręczna” (ang. *cache*), „odstęp między żądaniami”, „strona dynamiczna”, „dane osobowe”.
6. Odsyłacze wstecz: „Python Notatki” 9 (pliki, CSV/JSON), 16 (pytest, fixture); „Python Zastosowania” 14 (HTTP, httpx, `http.server`, `urllib.parse`), 19 (wzorce, `re.compile`), 20 (`argparse`, kody wyjścia, dziennik na `stderr`, testy `main(argv)`). Zapowiedzi: 22 (pliki Office i obrazy), 23 (projekt narzędzia) — `TODO`.
7. Domknięcia: markery „pobieraniu i parsowaniu stron” w 14/api i 19/pulapki → `21-scraping/index.md`; w 20/narzedzie (Dalej) marker → link.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i pliki |
|---|---|---|
| `index.md` | Wprowadzenie / „21. Pobieranie i parsowanie stron” | cel; biblioteki; plik wymagań; ---; ## W tym rozdziale (4) |
| `html-i-parser.md` | HTML i parser | Struktura strony (fragment HTML); Strona testowa (`zbuduj_sklep.py`); Wybieranie elementów (`parser.py`); Poruszanie się po drzewie (`drzewo.py`); Wyrażenia regularne a parser (`porownanie.py`) |
| `pobieranie.md` | Pobieranie stron | Serwer testowy (`sklep_serwer.py`); Klient httpx (`klient.py`); Uprzejmość wobec serwera (`uprzejmosc.py`) |
| `dane-ze-stron.md` | Dane ze stron | Moduł pobierania (`pobieranie.py`); Rekordy z HTML (`rekordy.py`); Przejście po stronach i zapis (`zbierz.py`); Strony dynamiczne |
| `narzedzie.md` | Narzędzie i zasady | Narzędzie zbieracz (`zbieracz.py`, `uzycie-zbieracz.py`); Testy z serwerem testowym (`test_zbieracz.py`, pytest); Zasady prawne i etyczne; Lista kontrolna; Dalej (TODO 22, 23) |

Szacunek: 650–800 linii; bez wykresów i zrzutów.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 20)

```yaml
      - 21. Pobieranie i parsowanie stron:
          - Wprowadzenie: zastosowania/21-scraping/index.md
          - HTML i parser: zastosowania/21-scraping/html-i-parser.md
          - Pobieranie stron: zastosowania/21-scraping/pobieranie.md
          - Dane ze stron: zastosowania/21-scraping/dane-ze-stron.md
          - Narzędzie i zasady: zastosowania/21-scraping/narzedzie.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `narzedzie.md` | pliki Office i obrazy; projekt narzędzia automatyzującego | rozdziały 22, 23 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/14-http-api/api.md` (marker) | `21-scraping/index.md` |
| `zastosowania/19-re/pulapki.md` (marker) | `21-scraping/index.md` |
| `zastosowania/20-cli/narzedzie.md` (marker „Dalej”) | `21-scraping/index.md` |

## CONTENT HANDOFF

Brak wykładu źródłowego; rozdział łączy klienta httpx z rozdziału 14, wzorce z rozdziału 19 i narzędzie wiersza poleceń z rozdziału 20 z nową biblioteką BeautifulSoup.

## Listy kontrolne

- Przed commitem: staging z bloków + `zbuduj_sklep.py`; `refresh_outputs.py`; `verify_page.py` dwa przebiegi z `--skip` modułów i testów; pytest w stagingu; oba buildy `--strict`; cudzysłowy; kolokwializmy; recenzje z weryfikacją uwag.
- Po commicie: domknięcia w 14/api, 19/pulapki, 20/narzedzie, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć.
