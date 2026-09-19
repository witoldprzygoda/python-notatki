# Serwer w bibliotece standardowej

Serwer echo z poprzedniego podrozdziału odpowiadał tak samo na każdą ścieżkę. Serwer sklepu musi rozpoznać, o co proszono — listę produktów, jeden produkt, złożenie zamówienia — sprawdzić dane i odpowiedzieć właściwym kodem. Piszemy go w `http.server`, bo każdy element widać wtedy wprost: trasę, walidację, kod stanu, nagłówek; to, co framework z rozdziału 15 zrobi w kilku wierszach, tu zajmuje kilkadziesiąt i przez to uczy.

## Trasy i odpowiedzi JSON

```python title="sklep_serwer.py"
"""Serwer sklepu: produkty i zamówienia jako interfejs JSON na porcie 8765."""

import json
import sys
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

PRODUKTY = {
    1: {"id": 1, "nazwa": "Python. Wprowadzenie", "kategoria": "książki", "cena": 59.0, "stan": 12},
    2: {"id": 2, "nazwa": "Algorytmy", "kategoria": "książki", "cena": 89.0, "stan": 5},
    3: {"id": 3, "nazwa": "Słuchawki", "kategoria": "elektronika", "cena": 249.0, "stan": 8},
}
ZAMOWIENIA = []
KLUCZ = "tajny-klucz"
LICZNIK = {"niestabilny": 0}


class Sklep(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def wyslij_json(self, status, dane, naglowki=()):
        tresc = json.dumps(dane, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(tresc)))
        for nazwa, wartosc in naglowki:
            self.send_header(nazwa, wartosc)
        self.end_headers()
        self.wfile.write(tresc)

    def do_GET(self):
        adres = urlsplit(self.path)
        czesci = adres.path.strip("/").split("/")
        if czesci == ["produkty"]:
            kategoria = parse_qs(adres.query).get("kategoria", [None])[0]
            self.wyslij_json(HTTPStatus.OK, [p for p in PRODUKTY.values() if kategoria in (None, p["kategoria"])])
        elif len(czesci) == 2 and czesci[0] == "produkty" and czesci[1].isdigit():
            produkt = PRODUKTY.get(int(czesci[1]))
            if produkt is None:
                self.wyslij_json(HTTPStatus.NOT_FOUND, {"blad": f"nie ma produktu {czesci[1]}"})
            else:
                self.wyslij_json(HTTPStatus.OK, produkt)
        elif czesci == ["raport.csv"]:
            wiersze = "id;nazwa;cena\n" + "".join(f"{p['id']};{p['nazwa']};{p['cena']}\n" for p in PRODUKTY.values())
            tresc = (wiersze * 200).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Length", str(len(tresc)))
            self.end_headers()
            self.wfile.write(tresc)
        elif czesci == ["wolny"]:
            time.sleep(2)
            self.wyslij_json(HTTPStatus.OK, {"gotowe": True})
        elif czesci == ["niestabilny"]:
            LICZNIK["niestabilny"] += 1
            if LICZNIK["niestabilny"] < 3:
                self.wyslij_json(HTTPStatus.SERVICE_UNAVAILABLE, {"blad": "chwilowo niedostępne"}, [("Retry-After", "1")])
            else:
                self.wyslij_json(HTTPStatus.OK, {"proba": LICZNIK["niestabilny"]})
        else:
            self.wyslij_json(HTTPStatus.NOT_FOUND, {"blad": "nieznany adres"})

    def do_POST(self):
        tresc = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if self.path != "/zamowienia":
            return self.wyslij_json(HTTPStatus.NOT_FOUND, {"blad": "nieznany adres"})
        if self.headers.get("Authorization") != f"Bearer {KLUCZ}":
            return self.wyslij_json(HTTPStatus.UNAUTHORIZED, {"blad": "brak lub zły klucz"})
        try:
            dane = json.loads(tresc)
        except json.JSONDecodeError:
            return self.wyslij_json(HTTPStatus.BAD_REQUEST, {"blad": "treść nie jest poprawnym JSON"})
        if not isinstance(dane, dict) or type(dane.get("produkt_id")) is not int or type(dane.get("ilosc")) is not int or dane["ilosc"] < 1:
            return self.wyslij_json(HTTPStatus.UNPROCESSABLE_CONTENT, {"blad": "wymagane pola: produkt_id (liczba), ilosc (liczba >= 1)"})
        produkt = PRODUKTY.get(dane["produkt_id"])
        if produkt is None:
            return self.wyslij_json(HTTPStatus.NOT_FOUND, {"blad": f"nie ma produktu {dane['produkt_id']}"})
        if produkt["stan"] < dane["ilosc"]:
            return self.wyslij_json(HTTPStatus.CONFLICT, {"blad": f"dostępne sztuk: {produkt['stan']}"})
        produkt["stan"] -= dane["ilosc"]
        zamowienie = {"id": len(ZAMOWIENIA) + 1, "produkt_id": produkt["id"], "ilosc": dane["ilosc"], "wartosc": produkt["cena"] * dane["ilosc"]}
        ZAMOWIENIA.append(zamowienie)
        self.wyslij_json(HTTPStatus.CREATED, zamowienie, [("Location", f"/zamowienia/{zamowienie['id']}")])

    def log_message(self, *args):
        pass


class SerwerSklepu(ThreadingHTTPServer):
    def handle_error(self, zadanie, adres_klienta):
        if not isinstance(sys.exception(), ConnectionError):
            super().handle_error(zadanie, adres_klienta)


def uruchom(port=8765):
    serwer = SerwerSklepu(("127.0.0.1", port), Sklep)
    threading.Thread(target=serwer.serve_forever, daemon=True).start()
    return serwer


if __name__ == "__main__":
    print("Serwer sklepu: http://127.0.0.1:8765/produkty — zatrzymanie: Ctrl+C")
    SerwerSklepu(("127.0.0.1", 8765), Sklep).serve_forever()
```

Metoda `do_GET()` rozkłada ścieżkę na segmenty i dopasowuje je do **tras** (ang. *routes*): `/produkty` z opcjonalnym filtrem w zapytaniu, `/produkty/3` z numerem produktu, `/raport.csv` z treścią tekstową, dwie trasy pomocnicze dla następnych podrozdziałów (`/wolny` odpowiada po dwóch sekundach, `/niestabilny` dwa razy odmawia kodem `503` z nagłówkiem `Retry-After`, potem odpowiada) i wszystko inne jako `404`. Każda odpowiedź poza raportem CSV, także błąd, jest dokumentem JSON — klient zawsze może ją odczytać tym samym kodem, a błąd ma pole `blad` z komunikatem dla człowieka. `do_POST()` najpierw czyta całą treść — w HTTP/1.1 połączenie pozostaje otwarte, a nieodczytane bajty zostałyby wzięte za początek następnego żądania — potem sprawdza po kolei: adres, klucz w nagłówku `Authorization` (`401`), czy treść jest JSON-em (`400`), czy ma właściwe pola (`422`), czy produkt istnieje (`404`) i czy jest na stanie (`409`) — dopiero potem zmienia dane i odpowiada `201` z nagłówkiem `Location` wskazującym utworzone zamówienie. Kolejność jest zasadą: najpierw tanie sprawdzenia formy, potem stan. Klasa serwera pomija w `handle_error()` zerwane połączenia — klient, który przestał czekać na odpowiedź, nie jest błędem serwera i nie zasługuje na wydruk śladu wywołań. Dane w słownikach modułu znikają z procesem; w rozdziale 15 ich miejsce zajmie warstwa danych z rozdziału 13.

## Pierwsze żądania

```python title="pierwsze.py"
import json
from urllib.request import Request, urlopen

from sklep_serwer import uruchom

serwer = uruchom()
with urlopen("http://127.0.0.1:8765/produkty?kategoria=elektronika") as odpowiedz:
    print(odpowiedz.status, odpowiedz.headers["Content-Type"])
    print(json.loads(odpowiedz.read()))
with urlopen("http://127.0.0.1:8765/produkty/2") as odpowiedz:
    print(json.loads(odpowiedz.read())["nazwa"])
dane = json.dumps({"produkt_id": 2, "ilosc": 1}).encode("utf-8")
naglowki = {"Content-Type": "application/json", "Authorization": "Bearer tajny-klucz"}
with urlopen(Request("http://127.0.0.1:8765/zamowienia", data=dane, headers=naglowki, method="POST")) as odpowiedz:
    print(odpowiedz.status, odpowiedz.headers["Location"], json.loads(odpowiedz.read()))
with urlopen("http://127.0.0.1:8765/produkty/2") as odpowiedz:
    print(json.loads(odpowiedz.read())["stan"])
serwer.shutdown()
```

```{ .text .no-copy }
200 application/json; charset=utf-8
[{'id': 3, 'nazwa': 'Słuchawki', 'kategoria': 'elektronika', 'cena': 249.0, 'stan': 8}]
Algorytmy
201 /zamowienia/1 {'id': 1, 'produkt_id': 2, 'ilosc': 1, 'wartosc': 89.0}
4
```

Klient z biblioteki standardowej wystarcza, by sprawdzić, że serwer działa: filtr w zapytaniu zwraca jeden produkt, zamówienie dostaje numer i adres w `Location`, a stan magazynu maleje. Widać też, ile pracy `urllib.request` zostawia programiście — kodowanie treści, nagłówki, `json.loads()` na bajtach — i dlaczego następny podrozdział sięga po httpx.

## Błędy jako odpowiedzi

```python title="bledy.py"
import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from sklep_serwer import uruchom

serwer = uruchom()
proby = [
    ("GET", "/produkty/9", None, {}),
    ("POST", "/zamowienia", b'{"produkt_id": 1, "ilosc": 1}', {}),
    ("POST", "/zamowienia", b"nie json", {"Authorization": "Bearer tajny-klucz"}),
    ("POST", "/zamowienia", b'{"produkt_id": "1"}', {"Authorization": "Bearer tajny-klucz"}),
    ("POST", "/zamowienia", b'{"produkt_id": 3, "ilosc": 50}', {"Authorization": "Bearer tajny-klucz"}),
]
for metoda, sciezka, dane, naglowki in proby:
    try:
        with urlopen(Request("http://127.0.0.1:8765" + sciezka, data=dane, headers=naglowki, method=metoda)):
            print(metoda, sciezka, "— sukces")
    except HTTPError as blad:
        print(metoda, sciezka, "—", blad.code, blad.reason, json.loads(blad.read())["blad"])
serwer.shutdown()
```

```{ .text .no-copy }
GET /produkty/9 — 404 Not Found nie ma produktu 9
POST /zamowienia — 401 Unauthorized brak lub zły klucz
POST /zamowienia — 400 Bad Request treść nie jest poprawnym JSON
POST /zamowienia — 422 Unprocessable Content wymagane pola: produkt_id (liczba), ilosc (liczba >= 1)
POST /zamowienia — 409 Conflict dostępne sztuk: 8
```

Każdy błąd ma kod, który mówi, kto zawinił i co zrobić: `401` — dodać klucz, `400` — naprawić format, `422` — naprawić dane, `404` — zasobu nie ma, `409` — żądanie poprawne, ale stan magazynu na nie nie pozwala. `urllib.request` zgłasza dla kodów `4xx` i `5xx` wyjątek `HTTPError`, z którego wciąż da się odczytać treść odpowiedzi — a w niej komunikat, który mówi więcej niż sam kod. Serwer nie zgłasza wyjątków na zewnątrz: każda przewidziana niepoprawna sytuacja kończy się odpowiedzią, a proces działa dalej.

## Uruchomienie z terminala

```powershell title="Terminal"
python sklep_serwer.py
```

```{ .text .no-copy }
Serwer sklepu: http://127.0.0.1:8765/produkty — zatrzymanie: Ctrl+C
```

Blok strażnika `__main__` z rozdziału 7 „Python Notatki” uruchamia serwer na pierwszym planie: adres `http://127.0.0.1:8765/produkty` otwiera się w przeglądarce, która pokaże JSON, a ++ctrl+c++ zatrzymuje proces. Adres `127.0.0.1` oznacza tylko tę maszynę; serwer widoczny dla innych komputerów nasłuchiwałby na `0.0.0.0` — czego z serwerem z biblioteki standardowej nie robimy, bo nie jest przygotowany na ruch z zewnątrz (brak HTTPS, limitów i ochrony przed błędnymi żądaniami). Do rozwoju i testów wystarcza; do wdrożenia służy serwer aplikacyjny, o którym w rozdziale 15.
