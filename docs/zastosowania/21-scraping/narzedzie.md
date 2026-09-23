# Narzędzie i zasady

Moduły z poprzedniej strony składają się w narzędzie wiersza poleceń według reguł z rozdziału 20: argumenty, dziennik na `stderr`, kody wyjścia, testy przez `main(argv)`.

## Narzędzie zbieracz

```python title="zbieracz.py"
"""zbieracz — pobiera listę produktów ze stron sklepu i zapisuje ją do pliku CSV."""

import argparse
import csv
import logging
import sys
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from pobieranie import Pobieracz, strony
from rekordy import lista_produktow, rekord_produktu

dziennik = logging.getLogger("zbieracz")
POLA = ["sku", "nazwa", "cena", "ocena", "moc_w", "pojemnosc_l"]


def zbuduj_parser():
    parser = argparse.ArgumentParser(prog="zbieracz", description="Zbiera produkty ze stron sklepu do pliku CSV.")
    parser.add_argument("adres", help="adres pierwszej strony listy")
    parser.add_argument("-o", "--wyjscie", type=Path, default=Path("produkty.csv"), help="plik CSV (domyślnie %(default)s)")
    parser.add_argument("--opoznienie", type=float, default=1.0, metavar="SEK", help="odstęp między żądaniami (domyślnie %(default)s s)")
    parser.add_argument("--limit", type=int, metavar="N", help="pobierz najwyżej N produktów")
    parser.add_argument("--pamiec", type=Path, help="katalog pamięci podręcznej")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="więcej komunikatów")
    return parser


def main(argv=None):
    argumenty = zbuduj_parser().parse_args(argv)
    poziom = [logging.WARNING, logging.INFO, logging.DEBUG][min(argumenty.verbose, 2)]
    logging.basicConfig(level=poziom, format="%(levelname)s: %(message)s", stream=sys.stderr, force=True)
    for biblioteka in ("httpx", "httpcore"):
        logging.getLogger(biblioteka).setLevel(logging.WARNING)
    try:
        pobieracz = Pobieracz(argumenty.adres, opoznienie=argumenty.opoznienie, pamiec=argumenty.pamiec)
    except httpx.TransportError as blad:
        dziennik.error("%s", blad)
        return 1
    rekordy = []
    try:
        pozycje = []
        for url, zupa in strony(pobieracz, argumenty.adres):
            pozycje.extend(lista_produktow(zupa, url))
        for pozycja in pozycje[: argumenty.limit]:
            zupa = BeautifulSoup(pobieracz.pobierz(pozycja["url"]), "html.parser")
            rekordy.append({**rekord_produktu(zupa), "ocena": pozycja["ocena"]})
        with open(argumenty.wyjscie, "w", newline="", encoding="utf-8") as plik:
            pisarz = csv.DictWriter(plik, fieldnames=POLA)
            pisarz.writeheader()
            pisarz.writerows(rekordy)
    except httpx.HTTPStatusError as blad:
        dziennik.error("serwer odpowiedział %d dla %s", blad.response.status_code, blad.request.url.path)
        return 1
    except (httpx.TransportError, OSError) as blad:
        dziennik.error("%s", blad)
        return 1
    finally:
        pobieracz.zamknij()
    print(f"Zapisano rekordów: {len(rekordy)} -> {argumenty.wyjscie}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

```python title="uzycie-zbieracz.py"
import os
import subprocess
import sys
from pathlib import Path

from sklep_serwer import uruchom

serwer, adres = uruchom("sklep")
srodowisko = {**os.environ, "PYTHONUTF8": "1"}


def narzedzie(*argumenty):
    proces = subprocess.run([sys.executable, "zbieracz.py", *argumenty, "--opoznienie", "0"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", env=srodowisko)
    print(proces.stdout + f"[kod {proces.returncode}]")


narzedzie(adres + "index.html", "-v", "--pamiec", "pamiec")
print(Path("produkty.csv").read_text(encoding="utf-8").splitlines()[:2])
narzedzie(adres + "index.html", "--limit", "3", "-o", "trzy.csv", "-vv", "--pamiec", "pamiec")
print(len(Path("trzy.csv").read_text(encoding="utf-8").splitlines()) - 1, "rekordy")
narzedzie(adres + "koszyk/")
narzedzie(adres + "brak.html")
serwer.shutdown()
```

```{ .text .no-copy }
INFO: pobrano: /index.html (1219 bajtów)
INFO: pobrano: /strona-2.html (908 bajtów)
INFO: pobrano: /produkt-1.html (651 bajtów)
INFO: pobrano: /produkt-2.html (639 bajtów)
INFO: pobrano: /produkt-3.html (648 bajtów)
INFO: pobrano: /produkt-4.html (647 bajtów)
INFO: pobrano: /produkt-5.html (620 bajtów)
INFO: pobrano: /produkt-6.html (626 bajtów)
INFO: pobrano: /produkt-7.html (640 bajtów)
INFO: pobrano: /produkt-8.html (679 bajtów)
INFO: pobrano: /produkt-9.html (580 bajtów)
INFO: pobrano: /produkt-10.html (650 bajtów)
Zapisano rekordów: 10 -> produkty.csv
[kod 0]
['sku,nazwa,cena,ocena,moc_w,pojemnosc_l', 'AGD-001,Czajnik elektryczny,149.0,4.5,2200.0,1.7']
DEBUG: z pamięci podręcznej: /index.html
DEBUG: z pamięci podręcznej: /strona-2.html
DEBUG: z pamięci podręcznej: /produkt-1.html
DEBUG: z pamięci podręcznej: /produkt-2.html
DEBUG: z pamięci podręcznej: /produkt-3.html
Zapisano rekordów: 3 -> trzy.csv
[kod 0]
3 rekordy
ERROR: robots.txt zabrania pobierania: /koszyk/
[kod 1]
ERROR: serwer odpowiedział 404 dla /brak.html
[kod 1]
```

Narzędzie ma tylko jedno zadanie: złożyć moduły i zamienić wynik na kody wyjścia — `0` po zapisie, `1` przy błędzie serwera, zakazie z `robots.txt` albo błędzie zapisu pliku, `2` przy błędnych argumentach z `argparse`. Biblioteki httpx i httpcore również piszą do dziennika — httpx każde żądanie z pełnym adresem na poziomie `INFO`, httpcore szczegóły połączenia na poziomie `DEBUG` — więc ich dzienniki ustawiamy na poziom ostrzeżeń, by `-v` pokazywał komunikaty narzędzia, nie bibliotek. Skrypt kontrolny uruchamia je jako proces z połączonymi strumieniami, jak w rozdziale 20: przy `-v` dziennik pokazuje każde pobranie ze ścieżką i rozmiarem, przy `-vv` także trafienia w pamięć podręczną (drugie uruchomienie pobrało tylko `robots.txt`), a podsumowanie ze `stdout` pojawia się na końcu. Zakaz z `robots.txt` i odpowiedź 404 dają komunikat błędu i kod `1` — bez śladu wywołań.

## Testy z serwerem testowym

```python title="test_zbieracz.py"
import csv
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

import zbieracz
from rekordy import liczba, lista_produktow, rekord_produktu
from sklep_serwer import uruchom

SKLEP = Path(__file__).parent / "sklep"


@pytest.fixture(scope="module")
def adres():
    serwer, adres = uruchom(SKLEP)
    yield adres
    serwer.shutdown()


def test_liczba_z_tekstu():
    assert liczba("1 299,00 zł") == 1299.0
    assert liczba("2200 W") == 2200.0
    assert liczba("cena na zapytanie") is None
    assert liczba(None) is None


def test_lista_i_rekord_z_plikow():
    zupa = BeautifulSoup((SKLEP / "index.html").read_text(encoding="utf-8"), "html.parser")
    pozycje = lista_produktow(zupa, "http://sklep.test/index.html")
    assert len(pozycje) == 6 and pozycje[0]["url"] == "http://sklep.test/produkt-1.html"
    assert pozycje[3]["ocena"] is None
    zupa = BeautifulSoup((SKLEP / "produkt-9.html").read_text(encoding="utf-8"), "html.parser")
    rekord = rekord_produktu(zupa)
    assert rekord["sku"] == "AGD-009" and rekord["cena"] is None and rekord["moc_w"] == 800.0


def test_narzedzie_zapisuje_csv(adres, tmp_path, capsys):
    wyjscie = tmp_path / "produkty.csv"
    assert zbieracz.main([adres + "index.html", "-o", str(wyjscie), "--opoznienie", "0"]) == 0
    with open(wyjscie, encoding="utf-8", newline="") as plik:
        wiersze = list(csv.DictReader(plik))
    assert len(wiersze) == 10 and wiersze[6]["cena"] == "1299.0" and wiersze[8]["cena"] == ""
    assert "Zapisano rekordów: 10" in capsys.readouterr().out


def test_robots_zabrania_koszyka(adres, capsys):
    assert zbieracz.main([adres + "koszyk/", "--opoznienie", "0"]) == 1
    assert "robots.txt" in capsys.readouterr().err
```

```powershell title="Terminal"
python -m pytest -q
```

```{ .text .no-copy }
....                                                                     [100%]
4 passed in 0.93s
```

Fixture o zasięgu modułu uruchamia serwer raz dla wszystkich testów i zamyka go po ostatnim (rozdział 16 „Python Notatki”). Funkcje rozbioru testujemy na plikach z dysku, bez sieci, ze ścieżką liczoną od `__file__`, więc testy działają z dowolnego katalogu; narzędzie — przez `main(argv)` z plikiem w `tmp_path` i strumieniami z `capsys`, jak w rozdziale 20. Wobec prawdziwego serwisu funkcje rozbioru testujemy na zapisanych kopiach jego stron, bez sieci; gdy serwis zmieni układ, narzędzie zacznie zwracać puste albo błędne rekordy — wtedy zapisujemy nową kopię, poprawiamy parser i test.

## Zasady prawne i etyczne

Pobieranie stron obciąża cudzy serwer i korzysta z cudzych treści, więc przed napisaniem narzędzia sprawdzamy kilka kwestii.

- **Regulamin serwisu** może zabraniać automatycznego pobierania; jego naruszenie bywa podstawą blokady konta lub roszczeń. Gdy serwis ma API albo eksport danych, korzystamy z nich.
- **`robots.txt`** nie jest przepisem prawa, ale wyraża wolę właściciela, a w prawie UE zastrzeżenie odczytywalne maszynowo może wyłączać dozwoloną eksplorację tekstów i danych; program, który go ignoruje, traci argument, że działa w dobrej wierze.
- **Dane osobowe** — nazwiska, adresy, wizerunki — podlegają RODO niezależnie od tego, że są publicznie widoczne; ich zbieranie wymaga podstawy prawnej i celu, a nie samej możliwości technicznej.
- **Treści chronione prawem autorskim** — teksty, opisy, zdjęcia — wolno analizować na własne potrzeby, ale nie wolno ich rozpowszechniać ani publikować dalej; pojedyncze fakty (ceny, terminy) nie podlegają prawu autorskiemu, lecz systematyczne pobranie istotnej części cudzego katalogu może naruszać odrębne prawo producenta bazy danych.
- **Obciążenie serwera**: odstęp między żądaniami, pamięć podręczna, pobieranie tylko potrzebnych stron i poza godzinami szczytu; wiele równoległych połączeń z jednego programu przypomina atak.
- **Identyfikacja**: prawdziwy `User-Agent` z kontaktem; udawanie przeglądarki i obchodzenie blokad zamienia pobieranie w nadużycie.

W razie wątpliwości — zwłaszcza przy danych osobowych i użyciu komercyjnym — decyzję podejmuje prawnik, nie programista.

## Lista kontrolna

- **Najpierw API lub eksport**; pobieranie stron, gdy ich nie ma.
- **Selektory z narzędzi deweloperskich**; `select_one()` sprawdzane na `None`.
- **Parser podany jawnie**; `html.parser` bez instalacji, `lxml` dla szybkości.
- **Wyrażenia regularne tylko do tekstu** wydobytego przez parser.
- **Klient z `User-Agent`, `timeout`, `raise_for_status()`**; bajty `content` do parsera; `HTTPStatusError` i `TransportError` osobno.
- **`robots.txt`, odstęp, pamięć podręczna** w jednym obiekcie pobierania.
- **Rekord o stałych kluczach**, `None` dla braków, liczby oczyszczone przy rozbiorze.
- **Narzędzie z kodami wyjścia**, testy na plikach i na serwerze testowym.

## Dalej: pliki Office i obrazy

Zebrane rekordy trafiają zwykle do arkusza kalkulacyjnego albo raportu: następny rozdział czyta i pisze pliki pakietu Office oraz przetwarza obrazy <!-- TODO: link po powstaniu rozdziału o plikach Office i obrazach -->, a projekt ścieżki łączy pobieranie, przetwarzanie i raport w jedno narzędzie <!-- TODO: link po powstaniu rozdziału o projekcie narzędzia automatyzującego -->.
