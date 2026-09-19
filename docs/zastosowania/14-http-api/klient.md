# Klient HTTP — httpx

Biblioteka **httpx** zamienia kilka wierszy `urllib.request` w jedno wywołanie: parametry zapytania, nagłówki i JSON podajemy jako argumenty, a odpowiedź ma gotowe metody dekodowania. Ten podrozdział pokazuje codzienne użycie klienta na serwerze sklepu z poprzedniego podrozdziału, a na koniec odpytuje prawdziwe API o kursy walut.

## Żądanie GET

```python title="zapytania.py"
import httpx

from sklep_serwer import uruchom

serwer = uruchom()
odpowiedz = httpx.get("http://127.0.0.1:8765/produkty", params={"kategoria": "książki"})
print(odpowiedz, odpowiedz.status_code, odpowiedz.reason_phrase, odpowiedz.http_version)
print(odpowiedz.url)
print(odpowiedz.headers["content-type"], odpowiedz.encoding)
print(odpowiedz.json())
print(odpowiedz.text[:40])
print(odpowiedz.request.method, dict(odpowiedz.request.headers))
print(httpx.get("http://127.0.0.1:8765/produkty/9").json(), httpx.get("http://127.0.0.1:8765/produkty/9").is_error)
serwer.shutdown()
```

```{ .text .no-copy }
<Response [200 OK]> 200 OK HTTP/1.1
http://127.0.0.1:8765/produkty?kategoria=ksi%C4%85%C5%BCki
application/json; charset=utf-8 utf-8
[{'id': 1, 'nazwa': 'Python. Wprowadzenie', 'kategoria': 'książki', 'cena': 59.0, 'stan': 12}, {'id': 2, 'nazwa': 'Algorytmy', 'kategoria': 'książki', 'cena': 89.0, 'stan': 5}]
[{"id": 1, "nazwa": "Python. Wprowadzeni
GET {'host': '127.0.0.1:8765', 'accept': '*/*', 'accept-encoding': 'gzip, deflate', 'connection': 'keep-alive', 'user-agent': 'python-httpx/0.28.1'}
{'blad': 'nie ma produktu 9'} True
```

`httpx.get()` przyjmuje adres i słownik `params`, który koduje w zapytanie za nas — polskie litery zamienia na kodowanie procentowe, jak `urlencode()` z podrozdziału o protokole. Odpowiedź niesie kod, opis i wersję protokołu, nagłówki w obiekcie o kluczach niewrażliwych na wielkość liter, treść jako `text` (zdekodowany według `charset`) i `json()`, a w `request` — wysłane żądanie, w tym nagłówki, które httpx dodał sam: `User-Agent`, `Accept`, `Accept-Encoding` z kompresją. Kod `4xx` nie jest wyjątkiem — odpowiedź wraca normalnie z `is_error` równym `True` — więc o zgłaszaniu błędów decyduje klient.

## Klient i połączenia

```python title="klient.py"
import httpx

from sklep_serwer import uruchom

serwer = uruchom()
with httpx.Client(base_url="http://127.0.0.1:8765", headers={"Authorization": "Bearer tajny-klucz"}, timeout=5.0) as klient:
    print([produkt["nazwa"] for produkt in klient.get("/produkty").json()])
    odpowiedz = klient.post("/zamowienia", json={"produkt_id": 1, "ilosc": 2})
    print(odpowiedz.status_code, odpowiedz.headers["location"], odpowiedz.json())
    print(dict(odpowiedz.request.headers)["content-type"], odpowiedz.request.content)
    for tresc in ({"produkt_id": 9, "ilosc": 1}, {"produkt_id": 2, "ilosc": 50}, {"produkt_id": 1}):
        try:
            klient.post("/zamowienia", json=tresc).raise_for_status()
        except httpx.HTTPStatusError as blad:
            print(blad.response.status_code, blad.response.json()["blad"])
    print(klient.get("/produkty/1").json()["stan"])
serwer.shutdown()
```

```{ .text .no-copy }
['Python. Wprowadzenie', 'Algorytmy', 'Słuchawki']
201 /zamowienia/1 {'id': 1, 'produkt_id': 1, 'ilosc': 2, 'wartosc': 118.0}
application/json b'{"produkt_id":1,"ilosc":2}'
404 nie ma produktu 9
409 dostępne sztuk: 5
422 wymagane pola: produkt_id (liczba), ilosc (liczba >= 1)
10
```

Funkcje modułu (`httpx.get()`, `httpx.post()`) otwierają i zamykają połączenie przy każdym wywołaniu; **klient** `httpx.Client` utrzymuje połączenia między żądaniami do tego samego serwera i przechowuje wspólne ustawienia: adres bazowy, nagłówki (tu klucz do zamówień), limit czasu (ang. *timeout*). Używamy go w bloku `with`, jak pliku. Argument `json=` serializuje treść i ustawia `Content-Type`, `raise_for_status()` zamienia każdy kod spoza `2xx` w `HTTPStatusError`, którego atrybut `response` daje dostęp do odpowiedzi z komunikatem serwera — wzorzec dla kodu, który błąd może jedynie zgłosić wyżej. Biblioteka `requests` ma niemal ten sam interfejs (`requests.get()`, `Session` w roli `Client`, `raise_for_status()`), więc kod przenosi się między nimi z niewielkimi zmianami.

## Błędy sieci i limit czasu

```python title="bledy-sieci.py"
import httpx

from sklep_serwer import uruchom

serwer = uruchom()
try:
    httpx.get("http://127.0.0.1:8765/wolny", timeout=0.5)
except httpx.TimeoutException as blad:
    print("limit czasu:", type(blad).__name__)
try:
    httpx.get("http://127.0.0.1:8799/", timeout=2.0)
except httpx.TransportError as blad:
    print("błąd transportu:", type(blad).__name__, isinstance(blad, httpx.RequestError))
print(httpx.get("http://127.0.0.1:8765/wolny", timeout=httpx.Timeout(5.0, connect=1.0)).json())
serwer.shutdown()
```

```{ .text .no-copy }
limit czasu: ReadTimeout
błąd transportu: ConnectTimeout True
{'gotowe': True}
```

Sieć zawodzi inaczej niż serwer: brak odpowiedzi w czasie, odmowa połączenia, zerwanie w trakcie. httpx zgłasza je jako `TransportError` (podklasa `RequestError`) — z odmianami `TimeoutException` (`ConnectTimeout`, `ReadTimeout`) i `ConnectError` — osobno od `HTTPStatusError`, który oznacza, że serwer odpowiedział, tylko kodem błędu. **Limit czasu** domyślnie wynosi 5 sekund, a `timeout=None` wyłącza go całkiem — wtedy program czeka w nieskończoność na serwer, który przestał odpowiadać; dobieramy go do usługi, a `httpx.Timeout` pozwala ustalić osobno czas na nawiązanie połączenia i na odczyt. Na tej maszynie próba połączenia z zamkniętym portem kończy się przekroczeniem czasu; na innych systemach to natychmiastowa odmowa (`ConnectError`) — dlatego przechwytujemy klasę bazową.

## Duże odpowiedzi

```python title="pobieranie.py"
from pathlib import Path

import httpx

from sklep_serwer import uruchom

serwer = uruchom()
with httpx.Client(base_url="http://127.0.0.1:8765") as klient, klient.stream("GET", "/raport.csv") as odpowiedz:
    print(odpowiedz.status_code, odpowiedz.headers["content-type"], odpowiedz.headers["content-length"])
    porcje = 0
    with open("raport.csv", "wb") as plik:
        for porcja in odpowiedz.iter_bytes(chunk_size=8192):
            plik.write(porcja)
            porcje += 1
print(porcje, Path("raport.csv").stat().st_size)
print(Path("raport.csv").read_text(encoding="utf-8").splitlines()[:2])
serwer.shutdown()
```

```{ .text .no-copy }
200 text/csv; charset=utf-8 15600
2 15600
['id;nazwa;cena', '1;Python. Wprowadzenie;59.0']
```

Zwykłe `get()` wczytuje całą treść do pamięci, zanim odda odpowiedź. Przy plikach do pobrania — raportach, obrazach, archiwach — `stream()` w bloku `with` oddaje odpowiedź po nagłówkach, a `iter_bytes()` wydaje treść porcjami, które zapisujemy do pliku w trybie binarnym z rozdziału 9 „Python Notatki”. Pamięć programu nie zależy wtedy od rozmiaru pliku; ten sam wzorzec (`iter_lines()`) obsługuje odpowiedzi wysyłane wiersz po wierszu.

## Prawdziwe API — kursy NBP

```python title="kursy.py"
import httpx

ADRES = "https://api.nbp.pl/api/exchangerates"
with httpx.Client(base_url=ADRES, params={"format": "json"}, timeout=10.0) as nbp:
    kurs = nbp.get("/rates/a/eur/").json()
    print(kurs)
    print(kurs["currency"], kurs["rates"][0]["mid"], kurs["rates"][0]["effectiveDate"])
    ostatnie = nbp.get("/rates/a/usd/last/3/").json()["rates"]
    print([(dzien["effectiveDate"], dzien["mid"]) for dzien in ostatnie])
    tabela = nbp.get("/tables/a/").json()[0]
    print(tabela["effectiveDate"], len(tabela["rates"]), {kurs["code"]: kurs["mid"] for kurs in tabela["rates"] if kurs["code"] in ("EUR", "USD", "CHF", "GBP")})
    odpowiedz = nbp.get("/rates/a/xyz/")
    print(odpowiedz.status_code, odpowiedz.headers["content-type"], repr(odpowiedz.text))
```

```{ .text .no-copy }
{'table': 'A', 'currency': 'euro', 'code': 'EUR', 'rates': [{'no': '182/A/NBP/2026', 'effectiveDate': '2026-09-18', 'mid': 4.3633}]}
euro 4.3633 2026-09-18
[('2026-09-16', 3.7639), ('2026-09-17', 3.803), ('2026-09-18', 3.7998)]
2026-09-18 32 {'USD': 3.7998, 'EUR': 4.3633, 'CHF': 4.6085, 'GBP': 5.0804}
404 text/plain; charset=utf-8 '404 NotFound - Not Found - Brak danych'
```

Interfejs API Narodowego Banku Polskiego nie wymaga klucza i odpowiada JSON-em, gdy parametr `format` ma wartość `json` — parametr wspólny dla wszystkich żądań podajemy klientowi raz. Adresy mają budowę typową dla interfejsów sieciowych: zasób (`rates`), tabela, kod waluty, opcjonalnie zakres (`last/3`). Wynik pochodzi z 19 IX 2026 i przy uruchomieniu będzie inny — to jedyny skrypt rozdziału, którego wydruk zależy od dnia. Ostatnie żądanie pokazuje, że prawdziwe API nie zawsze trzyma się reguł: nieznany kod waluty daje `404`, ale z treścią tekstową zamiast JSON, więc `json()` zgłosiłby wyjątek — kod klienta sprawdza najpierw kod stanu i `Content-Type`, potem dekoduje. Dokumentację interfejsu czytamy jak dokumentację biblioteki w rozdziale 1: adresy, parametry, kody błędów, limity liczby żądań.
