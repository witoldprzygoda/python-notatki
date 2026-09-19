# Protokół HTTP

HTTP jest protokołem tekstowym: klient wysyła **żądanie** (ang. *request*), serwer odsyła **odpowiedź** (ang. *response*), a oba komunikaty są czytelne dla człowieka. Ten podrozdział pokazuje je na lokalnym serwerze z biblioteki standardowej — najpierw przez klienta `http.client`, potem bajt po bajcie przez gniazdo (ang. *socket*) — i porządkuje elementy, z których składa się każda wymiana: adres, metodę, kod stanu, nagłówki i treść.

## Żądanie i odpowiedź

```python title="echo_serwer.py"
"""Najprostszy serwer HTTP: odpowiada tekstem z odebraną ścieżką, a żądanie POST odbija jako JSON."""

import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

OSTATNIE = {}


class Echo(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def wyslij(self, status, tresc, typ):
        self.send_response_only(status)
        self.send_header("Content-Type", typ)
        self.send_header("Content-Length", str(len(tresc)))
        self.end_headers()
        self.wfile.write(tresc)

    def do_GET(self):
        OSTATNIE["linia"] = self.requestline
        OSTATNIE["naglowki"] = dict(self.headers)
        self.wyslij(HTTPStatus.OK, f"Witaj! Ścieżka: {self.path}".encode("utf-8"), "text/plain; charset=utf-8")

    def do_POST(self):
        dlugosc = int(self.headers.get("Content-Length", 0))
        dane = json.loads(self.rfile.read(dlugosc))
        odpowiedz = {"otrzymano": dane, "typ": self.headers["Content-Type"]}
        self.wyslij(HTTPStatus.CREATED, json.dumps(odpowiedz, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def log_message(self, *args):
        pass


def uruchom(port=8765):
    serwer = ThreadingHTTPServer(("127.0.0.1", port), Echo)
    threading.Thread(target=serwer.serve_forever, daemon=True).start()
    return serwer
```

```python title="zadanie.py"
import http.client
from urllib.parse import quote

from echo_serwer import OSTATNIE, uruchom

serwer = uruchom()
polaczenie = http.client.HTTPConnection("127.0.0.1", 8765)
polaczenie.request("GET", "/sklep?kategoria=" + quote("książki"))
odpowiedz = polaczenie.getresponse()
print(odpowiedz.status, odpowiedz.reason, odpowiedz.version)
print(odpowiedz.getheaders())
print(odpowiedz.read().decode("utf-8"))
print(OSTATNIE)
polaczenie.close()
serwer.shutdown()
```

```{ .text .no-copy }
200 OK 11
[('Content-Type', 'text/plain; charset=utf-8'), ('Content-Length', '52')]
Witaj! Ścieżka: /sklep?kategoria=ksi%C4%85%C5%BCki
{'linia': 'GET /sklep?kategoria=ksi%C4%85%C5%BCki HTTP/1.1', 'naglowki': {'Host': '127.0.0.1:8765', 'Accept-Encoding': 'identity'}}
```

Obsługę żądań pisze klasa dziedzicząca po `BaseHTTPRequestHandler`: dla każdego połączenia biblioteka tworzy jej obiekt, a dla każdego żądania wywołuje metodę o nazwie metody HTTP — `do_GET()`, `do_POST()` — z rozłożonym już żądaniem w atrybutach `path`, `headers` i `rfile`. Odpowiedź budujemy w trzech krokach: linia stanu (`send_response_only()`; pełne `send_response()` dopisuje jeszcze nagłówki `Server` i `Date`), nagłówki (`send_header()`, `end_headers()`) i treść zapisana do `wfile` jako bajty. `ThreadingHTTPServer` obsługuje każde połączenie w osobnym wątku z rozdziału 15 „Python Notatki”, a uruchomiony w wątku w tle nie blokuje skryptu, który chce go odpytać. Po stronie klienta `http.client` wysyła żądanie i zwraca obiekt odpowiedzi z kodem stanu, opisem, wersją protokołu (`11` to HTTP/1.1), nagłówkami i treścią do odczytania. W adresie mogą występować tylko znaki ASCII — polskie litery zapisujemy **kodowaniem procentowym** (ang. *percent-encoding*) przez `quote()`, co widać w ścieżce, którą serwer odebrał.

## Protokół w surowej postaci

```python title="gniazdo.py"
import socket

from echo_serwer import uruchom

serwer = uruchom()
with socket.create_connection(("127.0.0.1", 8765)) as gniazdo:
    gniazdo.sendall(b"GET /witaj HTTP/1.1\r\nHost: 127.0.0.1:8765\r\nConnection: close\r\n\r\n")
    dane = b""
    while porcja := gniazdo.recv(4096):
        dane += porcja
print(repr(dane[:33]))
print(dane.decode("utf-8").replace("\r\n", "\n"))
serwer.shutdown()
```

```{ .text .no-copy }
b'HTTP/1.1 200 OK\r\nContent-Type: te'
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8
Content-Length: 24

Witaj! Ścieżka: /witaj
```

Bez żadnej biblioteki HTTP: otwieramy gniazdo TCP, wysyłamy tekst i czytamy, co wraca. Żądanie to linia z **metodą**, ścieżką i wersją protokołu, potem **nagłówki** (ang. *headers*) w postaci `Nazwa: wartość`, pusta linia i — w żądaniach przesyłających dane, jak POST — **treść** (ang. *body*); każdą linię kończy para `\r\n`. Odpowiedź ma tę samą budowę: linia stanu z wersją, **kodem stanu** (ang. *status code*) i opisem, nagłówki, pusta linia, treść. `Content-Length` mówi, ile bajtów treści czytać, `Content-Type` — jak je rozumieć (tu tekst w UTF-8), a `Connection: close` prosi serwer o zamknięcie połączenia po odpowiedzi (w HTTP/1.1, włączonym atrybutem `protocol_version`, połączenie domyślnie pozostaje otwarte), dzięki czemu pętla `recv()` kończy się pustym obiektem `bytes`. Wszystko dalej — klienci, serwery, frameworki — jest wygodniejszą obsługą tych kilku linii.

## Adresy URL

```python title="adresy.py"
from urllib.parse import parse_qs, quote, urlencode, urljoin, urlsplit

adres = urlsplit("https://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json&start=2025-01-01#top")
print(adres.scheme, adres.netloc, adres.path, adres.query, adres.fragment, sep=" | ")
print(adres.hostname, adres.port)
print(parse_qs(adres.query))
print(urlencode({"q": "python 3.14", "lang": "pl"}))
print(quote("zażółć gęślą/jaźń"))
print(urljoin("https://sklep.pl/api/produkty/", "../klienci"))
```

```{ .text .no-copy }
https | api.nbp.pl | /api/exchangerates/rates/a/eur/ | format=json&start=2025-01-01 | top
api.nbp.pl None
{'format': ['json'], 'start': ['2025-01-01']}
q=python+3.14&lang=pl
za%C5%BC%C3%B3%C5%82%C4%87%20g%C4%99%C5%9Bl%C4%85/ja%C5%BA%C5%84
https://sklep.pl/api/klienci
```

**Adres URL** (ang. *Uniform Resource Locator*) składa się ze schematu (`http` albo `https` — HTTP szyfrowany), nazwy serwera z opcjonalnym portem, ścieżki, zapytania po znaku `?` i fragmentu po `#`, który zostaje w przeglądarce i nie idzie do serwera. `urlsplit()` rozkłada adres na części, `parse_qs()` zamienia zapytanie w słownik list (parametr może wystąpić wielokrotnie), a `urlencode()` buduje zapytanie ze słownika, kodując spacje, znaki specjalne i znaki spoza ASCII. Kodowanie procentowe zapisuje bajty UTF-8 znaku jako `%XX`; `quote()` domyślnie zostawia ukośnik, bo rozdziela on segmenty ścieżki. `urljoin()` łączy adres bazowy ze względnym według reguł znanych z odsyłaczy w HTML. Ręczne sklejanie adresów f-stringiem prowadzi do błędów tego samego rodzaju, co sklejanie SQL w rozdziale 13 — biblioteki klienckie robią to za nas.

## Metody i kody stanu

```python title="kody.py"
from http import HTTPMethod, HTTPStatus

print([metoda.value for metoda in HTTPMethod])
print(HTTPMethod.GET.description)
print(HTTPStatus.NOT_FOUND, HTTPStatus.NOT_FOUND.value, HTTPStatus.NOT_FOUND.phrase, HTTPStatus.NOT_FOUND.description)
print(HTTPStatus(201).phrase, HTTPStatus(422).phrase, HTTPStatus(503).phrase)
print(HTTPStatus.OK.is_success, HTTPStatus.NOT_FOUND.is_client_error, HTTPStatus.SERVICE_UNAVAILABLE.is_server_error)
print([status.value for status in HTTPStatus if status.is_redirection][:5])
```

```{ .text .no-copy }
['CONNECT', 'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'TRACE']
Retrieve the target.
404 404 Not Found Nothing matches the given URI
Created Unprocessable Content Service Unavailable
True True True
[300, 301, 302, 303, 304]
```

**Metoda** (ang. *method*) mówi, co klient chce zrobić z zasobem pod adresem: `GET` odczytuje i niczego nie zmienia, `POST` tworzy albo wyzwala działanie, `PUT` zastępuje, `PATCH` zmienia część, `DELETE` usuwa; `HEAD` to `GET` bez treści, `OPTIONS` pyta o dostępne metody. `GET`, `PUT` i `DELETE` są **idempotentne** (ang. *idempotent*): powtórzenie żądania nie zmienia wyniku, więc można je bezpiecznie ponawiać — `POST` nie. Kod stanu ma trzy cyfry, z których pierwsza określa klasę odpowiedzi: `2xx` sukces (`200 OK`, `201 Created`, `204 No Content`), `3xx` przekierowanie, `4xx` błąd klienta (`400` złe żądanie, `401` brak uwierzytelnienia, `403` brak uprawnień, `404` brak zasobu, `409` konflikt ze stanem, `422` poprawny format, ale nieprawidłowe dane, `429` za dużo żądań), `5xx` błąd serwera (`500`, `503` chwilowo niedostępny). Moduł `http` ma oba zestawy jako wyliczenia z rozdziału 12 „Python Notatki”, z opisami i pomocniczymi własnościami.

## Nagłówki i treść

```python title="tresc.py"
import json
from urllib.request import Request, urlopen

from echo_serwer import uruchom

serwer = uruchom()
dane = json.dumps({"produkt_id": 1, "ilosc": 2}).encode("utf-8")
zadanie = Request("http://127.0.0.1:8765/zamowienia", data=dane, headers={"Content-Type": "application/json"}, method="POST")
with urlopen(zadanie) as odpowiedz:
    print(odpowiedz.status, odpowiedz.headers["Content-Type"])
    print(json.loads(odpowiedz.read()))
with urlopen("http://127.0.0.1:8765/") as odpowiedz:
    print(odpowiedz.status, odpowiedz.read().decode("utf-8"))
serwer.shutdown()
```

```{ .text .no-copy }
201 application/json; charset=utf-8
{'otrzymano': {'produkt_id': 1, 'ilosc': 2}, 'typ': 'application/json'}
200 Witaj! Ścieżka: /
```

Treść żądania i odpowiedzi to bajty; nagłówek `Content-Type` mówi, jak je czytać: `application/json` dla danych między programami, `text/html` dla stron, `application/x-www-form-urlencoded` dla formularzy, `text/csv` dla danych tabelarycznych. JSON z rozdziału 9 „Python Notatki” jest najczęstszym formatem interfejsów API — `json.dumps()` przed wysłaniem, `json.loads()` po odebraniu — a `urllib.request` z biblioteki standardowej wystarcza do prostego żądania, choć wymaga ręcznego kodowania treści, budowania obiektu `Request` i dekodowania odpowiedzi. Inne ważne nagłówki: `Authorization` (klucz lub token), `Location` (adres utworzonego zasobu albo cel przekierowania) i `Retry-After` (kiedy spróbować ponownie) — te trzy sprawdza lub wysyła serwer z następnego podrozdziału — oraz `Accept` (jaki format klient przyjmie) i `User-Agent` (kto pyta), które klient httpx dodaje sam.
