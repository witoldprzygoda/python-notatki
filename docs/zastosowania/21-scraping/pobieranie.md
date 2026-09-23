# Pobieranie stron

Parser otrzymywał dotąd pliki z dysku. Prawdziwe strony pobiera klient HTTP — httpx z rozdziału 14 — a serwer, który je podaje, należy do kogoś innego: program musi się przedstawić, nie przeciążać go i szanować jego zasady.

## Serwer testowy

```python title="sklep_serwer.py"
"""Lokalny serwer HTTP dla strony testowej — zamiast prawdziwego sklepu."""

import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class CichaObsluga(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass  # bez wpisów o każdym żądaniu w terminalu


def uruchom(katalog="sklep"):
    serwer = ThreadingHTTPServer(("127.0.0.1", 0), partial(CichaObsluga, directory=str(katalog)))
    threading.Thread(target=serwer.serve_forever, daemon=True).start()
    return serwer, f"http://127.0.0.1:{serwer.server_port}/"
```

Moduł `http.server` z rozdziału 14 ma gotową klasę `SimpleHTTPRequestHandler` (tam pisaliśmy własną obsługę po `BaseHTTPRequestHandler`), która podaje pliki z katalogu jak zwykły serwer WWW. Port `0` oznacza dowolny wolny port — system przydziela go, a serwer zapisuje w `server_port`, więc skrypty nie kolidują z innymi programami; serwer działa w wątku w tle (rozdział 15 „Python Notatki”), a skrypt kończy go wywołaniem `shutdown()`. Adresy w wynikach różnią się portem między uruchomieniami, dlatego skrypty rozdziału wypisują ścieżki, nie pełne adresy.

## Klient httpx

```python title="klient.py"
import httpx
from bs4 import BeautifulSoup

from sklep_serwer import uruchom

serwer, adres = uruchom("sklep")
naglowki = {"User-Agent": "zbieracz/1.0 (+mailto:kontakt@example.com)"}
with httpx.Client(base_url=adres, headers=naglowki, timeout=10.0) as klient:
    odpowiedz = klient.get("index.html")
    print(odpowiedz.status_code, odpowiedz.headers["content-type"], odpowiedz.encoding, len(odpowiedz.text))
    print(odpowiedz.request.headers["user-agent"], odpowiedz.url.path)
    print(BeautifulSoup(odpowiedz.content, "html.parser").original_encoding)
    odpowiedz = klient.get("nie-ma.html")
    print(odpowiedz.status_code, odpowiedz.is_success)
    try:
        odpowiedz.raise_for_status()
    except httpx.HTTPStatusError as blad:
        print("HTTPStatusError:", blad.response.status_code, blad.request.url.path)
serwer.shutdown()
serwer.server_close()
try:
    httpx.get(adres + "index.html", timeout=2.0)
except httpx.TransportError as blad:
    print("TransportError — serwer nie odpowiada:", isinstance(blad, httpx.HTTPError))
```

```{ .text .no-copy }
200 text/html utf-8 1209
zbieracz/1.0 (+mailto:kontakt@example.com) /index.html
utf-8
404 False
HTTPStatusError: 404 /nie-ma.html
TransportError — serwer nie odpowiada: True
```

Klient z `base_url` skraca adresy do ścieżek, a nagłówki ustawione raz są wysyłane z każdym żądaniem. Nagłówek `User-Agent` identyfikuje program: nazwa, wersja i sposób kontaktu pozwalają administratorowi serwera napisać do autora zamiast blokować adres; udawanie przeglądarki jest złą praktyką. `timeout` chroni przed zawieszeniem na serwerze, który nie odpowiada. Kodowanie tekstu httpx bierze z nagłówka `Content-Type`, a bez niego zakłada UTF-8; gdy strona deklaruje kodowanie tylko w `<meta charset>`, bezpieczniej przekazać parserowi bajty `odpowiedz.content` — BeautifulSoup odczyta deklarację sam. Błędy dzielą się na dwie rodziny: `HTTPStatusError` po `raise_for_status()` oznacza odpowiedź serwera z kodem błędu (tu 404), a `TransportError` — brak odpowiedzi: po zatrzymaniu serwera i zamknięciu jego gniazda (`server_close()`) połączenie kończy się odmową (`ConnectError`) albo — gdy system zwleka z odmową dłużej niż `timeout`, jak Windows — przekroczeniem czasu (`ConnectTimeout`); obie rodziny dziedziczą po `httpx.HTTPError`, gdy chcemy przechwycić obie naraz.

## Uprzejmość wobec serwera

```python title="uprzejmosc.py"
import hashlib
import time
from pathlib import Path
from urllib.robotparser import RobotFileParser

import httpx

from sklep_serwer import uruchom

serwer, adres = uruchom("sklep")
klient = httpx.Client(base_url=adres, headers={"User-Agent": "zbieracz/1.0"}, timeout=10.0)

roboty = RobotFileParser()
roboty.parse(klient.get("robots.txt").text.splitlines())
for sciezka in ("index.html", "produkt-1.html", "koszyk/"):
    print(sciezka, roboty.can_fetch("zbieracz", adres + sciezka))
print("odstęp z robots.txt:", roboty.crawl_delay("zbieracz"))

pamiec = Path("pamiec")
pamiec.mkdir(exist_ok=True)


def pobierz(sciezka, opoznienie=1.0):
    plik = pamiec / (hashlib.sha256((adres + sciezka).encode()).hexdigest()[:16] + ".html")
    if plik.exists():
        print("z pamięci podręcznej:", sciezka)
        return plik.read_text(encoding="utf-8")
    time.sleep(opoznienie)
    odpowiedz = klient.get(sciezka)
    odpowiedz.raise_for_status()
    plik.write_text(odpowiedz.text, encoding="utf-8")
    print("pobrano:", sciezka)
    return odpowiedz.text


for _ in range(2):
    for strona in ("index.html", "strona-2.html"):
        pobierz(strona, opoznienie=0.2)
print(len(list(pamiec.iterdir())), "pliki w pamięci podręcznej")
klient.close()
serwer.shutdown()
```

```{ .text .no-copy }
index.html True
produkt-1.html True
koszyk/ False
odstęp z robots.txt: None
pobrano: index.html
pobrano: strona-2.html
z pamięci podręcznej: index.html
z pamięci podręcznej: strona-2.html
2 pliki w pamięci podręcznej
```

Trzy zasady uprzejmego programu. Plik `robots.txt` w katalogu głównym serwera mówi robotom, dokąd nie wchodzić; `RobotFileParser` z biblioteki standardowej czyta go i odpowiada na pytanie `can_fetch()` dla nazwy programu, a `crawl_delay()` zwraca żądany odstęp, jeśli plik go podaje (tu nie). Odstęp między żądaniami — `time.sleep()` — sprawia, że program nie obciąża serwera bardziej niż człowiek z przeglądarką; sekunda to rozsądna wartość domyślna. **Pamięć podręczna** (ang. *cache*) na dysku zapisuje raz pobrane strony pod nazwą ze skrótu adresu, więc podczas pisania i poprawiania parsera nie pobieramy ich od nowa — drugie przejście pętli nie wysłało żadnego żądania. Klucz skrótu zawiera adres z losowym portem serwera testowego, więc ponowne uruchomienie skryptu pobiera strony od nowa; wobec prawdziwego serwera adres jest stały i pamięć podręczna działa także między uruchomieniami. W programie do wielokrotnego użytku pamięć podręczna powinna mieć termin ważności, bo strony się zmieniają.
