# Dane ze stron

Pobieranie z uprzejmością i rozbiór strony na rekord to dwa moduły, z których korzysta każdy skrypt zbierający dane: pierwszy odpowiada za sieć, drugi za układ strony. Rozdzielenie ich pozwala testować parser na plikach z dysku, a pobieranie na serwerze testowym.

## Moduł pobierania

```python title="pobieranie.py"
"""Pobieranie stron z uprzejmością: identyfikacja, robots.txt, odstęp między żądaniami, pamięć podręczna."""

import hashlib
import logging
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

dziennik = logging.getLogger("zbieracz")


class Pobieracz:
    def __init__(self, adres, nazwa="zbieracz/1.0 (+mailto:kontakt@example.com)", opoznienie=1.0, pamiec=None):
        self.nazwa = nazwa
        self.klient = httpx.Client(headers={"User-Agent": nazwa}, timeout=10.0, follow_redirects=True)
        self.pamiec = Path(pamiec) if pamiec else None
        self.roboty = RobotFileParser()
        odpowiedz = self.klient.get(urljoin(adres, "/robots.txt"))
        self.roboty.parse(odpowiedz.text.splitlines() if odpowiedz.is_success else [])
        self.opoznienie = max(opoznienie, self.roboty.crawl_delay(nazwa) or 0)
        self.ostatnie = 0.0

    def pobierz(self, url):
        sciezka = httpx.URL(url).path
        if not self.roboty.can_fetch(self.nazwa, url):
            raise PermissionError(f"robots.txt zabrania pobierania: {sciezka}")
        plik = self.pamiec / (hashlib.sha256(url.encode()).hexdigest()[:16] + ".html") if self.pamiec else None
        if plik and plik.exists():
            dziennik.debug("z pamięci podręcznej: %s", sciezka)
            return plik.read_bytes()
        odstep = self.opoznienie - (time.monotonic() - self.ostatnie)
        if odstep > 0:
            time.sleep(odstep)
        odpowiedz = self.klient.get(url)
        self.ostatnie = time.monotonic()
        odpowiedz.raise_for_status()
        dziennik.info("pobrano: %s (%d bajtów)", sciezka, len(odpowiedz.content))
        if plik:
            self.pamiec.mkdir(exist_ok=True)
            plik.write_bytes(odpowiedz.content)
        return odpowiedz.content

    def zamknij(self):
        self.klient.close()


def strony(pobieracz, url):
    """Przechodzi po stronach listy, dopóki jest odsyłacz „dalej”."""
    while url:
        zupa = BeautifulSoup(pobieracz.pobierz(url), "html.parser")
        yield url, zupa
        dalej = zupa.select_one("a.dalej")
        url = urljoin(url, dalej["href"]) if dalej else None
```

Klasa `Pobieracz` zbiera zasady z poprzedniej strony w jednym obiekcie: przy tworzeniu pobiera `robots.txt` (brak pliku oznacza brak ograniczeń) i podnosi odstęp do wartości z `Crawl-delay`, jeśli serwer jej żąda; `pobierz()` odmawia adresów zabronionych wyjątkiem `PermissionError`, sięga do pamięci podręcznej, a przed każdym żądaniem odczekuje resztę odstępu liczonego zegarem `time.monotonic()` — niezależnym od zmian czasu systemowego. Metoda zwraca bajty odpowiedzi, nie tekst — parser sam rozpozna kodowanie, jak na poprzedniej stronie — i te same bajty trafiają do pamięci podręcznej. Komunikaty trafiają do dziennika z rozdziału 20, ze ścieżką zamiast pełnego adresu; `follow_redirects=True` pozwala podążyć za przekierowaniem serwera, na przykład z adresu katalogu bez końcowego ukośnika na adres z ukośnikiem; `robots.txt` sprawdzamy jednak tylko dla adresu żądanego, nie docelowego. Generator `strony()` przechodzi po kolejnych stronach listy, dopóki znajduje odsyłacz „dalej”, a `urljoin()` z rozdziału 14 zamienia adres względny z atrybutu `href` w pełny.

## Rekordy z HTML

```python title="rekordy.py"
"""Rekordy z HTML sklepu: lista produktów i dane pojedynczego produktu."""

import json
import re
from urllib.parse import urljoin

LICZBA = re.compile(r"\d[\d ]*(?:,\d+)?")


def liczba(tekst):
    """„1 299,00 zł” → 1299.0, „2200 W” → 2200.0, brak liczby → None."""
    dopasowanie = LICZBA.search((tekst or "").replace("\xa0", " "))
    return float(dopasowanie.group().replace(" ", "").replace(",", ".")) if dopasowanie else None


def lista_produktow(zupa, url_strony):
    pozycje = []
    for element in zupa.select("li.produkt"):
        ocena = element.select_one("span.ocena")
        pozycje.append({"nazwa": element.a.get_text(strip=True), "url": urljoin(url_strony, element.a["href"]), "ocena": liczba(ocena.get_text()) if ocena else None})
    return pozycje


def rekord_produktu(zupa):
    strukturalne = json.loads(zupa.select_one('script[type="application/ld+json"]').string)
    dane = {wiersz.th.get_text(strip=True): wiersz.td.get_text(strip=True) for wiersz in zupa.select("table.dane tr")}
    return {
        "sku": strukturalne["sku"],
        "nazwa": zupa.select_one("h1.nazwa").get_text(strip=True),
        "cena": liczba(zupa.select_one("p.cena").get_text()),
        "moc_w": liczba(dane.get("Moc")),
        "pojemnosc_l": liczba(dane.get("Pojemność")),
    }
```

Funkcje przyjmują gotowe drzewo, więc nie zależą od sieci. Tekst ze strony trzeba oczyścić: wzorzec z rozdziału 19 wydobywa liczbę z „1 299,00 zł” i „2200 W”, usuwa separator tysięcy — zwykłą lub twardą spację (`\xa0`), częstą na stronach — i zamienia przecinek na kropkę, a gdy liczby nie ma („cena na zapytanie”, brak wiersza w tabeli), zwraca `None` zamiast zgłaszać błąd — brak danych jest w tym zadaniu normą, nie wyjątkiem. Klucze rekordu są ustalone raz i takie same dla każdego produktu, co pozwala zapisać rekordy do CSV; nazwy z jednostką (`moc_w`, `pojemnosc_l`) dokumentują, co znaczy liczba.

## Przejście po stronach i zapis

```python title="zbierz.py"
import csv
import json
from pathlib import Path

from bs4 import BeautifulSoup

from pobieranie import Pobieracz, strony
from rekordy import lista_produktow, rekord_produktu
from sklep_serwer import uruchom

serwer, adres = uruchom("sklep")
pobieracz = Pobieracz(adres, opoznienie=0.0, pamiec="pamiec")
pozycje = []
for numer, (url, zupa) in enumerate(strony(pobieracz, adres + "index.html"), 1):
    znalezione = lista_produktow(zupa, url)
    print(f"strona {numer}: {len(znalezione)} produktów")
    pozycje.extend(znalezione)
rekordy = []
for pozycja in pozycje:
    zupa = BeautifulSoup(pobieracz.pobierz(pozycja["url"]), "html.parser")
    rekordy.append({**rekord_produktu(zupa), "ocena": pozycja["ocena"]})
pobieracz.zamknij()
serwer.shutdown()

print(len(rekordy), rekordy[0])
print(rekordy[8])
POLA = ["sku", "nazwa", "cena", "ocena", "moc_w", "pojemnosc_l"]
with open("produkty.csv", "w", newline="", encoding="utf-8") as plik:
    pisarz = csv.DictWriter(plik, fieldnames=POLA)
    pisarz.writeheader()
    pisarz.writerows(rekordy)
Path("produkty.json").write_text(json.dumps(rekordy, ensure_ascii=False, indent=1), encoding="utf-8")
print(Path("produkty.csv").read_text(encoding="utf-8").splitlines()[:3])
z_cena = [rekord for rekord in rekordy if rekord["cena"] is not None]
print(f"z ceną: {len(z_cena)}, średnia: {sum(r['cena'] for r in z_cena) / len(z_cena):.2f} zł, najdroższy: {max(z_cena, key=lambda r: r['cena'])['nazwa']}")
```

```{ .text .no-copy }
strona 1: 6 produktów
strona 2: 4 produktów
10 {'sku': 'AGD-001', 'nazwa': 'Czajnik elektryczny', 'cena': 149.0, 'moc_w': 2200.0, 'pojemnosc_l': 1.7, 'ocena': 4.5}
{'sku': 'AGD-009', 'nazwa': 'Sokowirówka', 'cena': None, 'moc_w': 800.0, 'pojemnosc_l': None, 'ocena': 3.9}
['sku,nazwa,cena,ocena,moc_w,pojemnosc_l', 'AGD-001,Czajnik elektryczny,149.0,4.5,2200.0,1.7', 'AGD-002,Toster dwukomorowy,199.0,4.2,850.0,']
z ceną: 9, średnia: 351.49 zł, najdroższy: Robot planetarny
```

Skrypt najpierw przechodzi po stronach listy i zbiera odsyłacze, potem pobiera stronę każdego produktu i składa rekord — z oceną z listy, bo strona produktu jej nie ma. Rekordy zapisuje `csv.DictWriter` z rozdziału 9 „Python Notatki” z ustaloną listą pól oraz JSON dla programów, które oczekują danych zagnieżdżonych; `None` w CSV staje się pustym polem. Podsumowanie liczy tylko rekordy z ceną. Odstęp zerowy i pamięć podręczna są dopuszczalne wobec serwera testowego; wobec cudzego serwera odstęp należy zachować.

## Strony dynamiczne

Część stron nie ma danych w HTML, który przysyła serwer: przeglądarka wykonuje skrypt JavaScript, a ten dopiero pobiera dane i buduje listę. Parser widzi wtedy pusty szkielet. Najpierw warto sprawdzić w narzędziach deweloperskich przeglądarki (zakładka „Sieć”), skąd skrypt bierze dane — często jest to wewnętrzne API zwracające JSON, które można odpytać klientem httpx jak w rozdziale 14, prościej i taniej niż HTML. Gdy takiego API nie ma, potrzebna jest przeglądarka sterowana z programu (biblioteka Playwright) — wolniejsza i bardziej zasobochłonna, poza zakresem tej książki. Zanim jednak sięgniemy po pobieranie stron, sprawdzamy, czy serwis nie udostępnia oficjalnego API albo pliku do pobrania: to źródło stabilniejsze, szybsze i zgodne z wolą właściciela.
