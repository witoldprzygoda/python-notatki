# Moduły narzędzia

Trzy nowe moduły — historia, analiza, raport — i dwa łączące wszystko w polecenie. Bloki z tytułem `monitor/…` to pliki pakietu; dwa skrypty przebiegu na końcu strony leżą w katalogu projektu.

## Historia pomiarów

```python title="monitor/__init__.py"
"""monitor-cen — monitor cen sklepu: pomiary, historia i raporty."""
```

```python title="monitor/historia.py"
"""Historia pomiarów cen w bazie SQLite."""

import sqlite3

SCHEMAT = """
CREATE TABLE IF NOT EXISTS pomiary (
    id INTEGER PRIMARY KEY,
    czas TEXT NOT NULL,
    sku TEXT NOT NULL,
    nazwa TEXT NOT NULL,
    cena REAL
);
CREATE INDEX IF NOT EXISTS pomiary_sku ON pomiary (sku, czas);
"""


def otworz(sciezka):
    polaczenie = sqlite3.connect(sciezka)
    polaczenie.executescript(SCHEMAT)
    return polaczenie


def zapisz_pomiar(polaczenie, czas, rekordy):
    with polaczenie:
        polaczenie.executemany(
            "INSERT INTO pomiary (czas, sku, nazwa, cena) VALUES (?, ?, ?, ?)",
            [(czas, rekord["sku"], rekord["nazwa"], rekord["cena"]) for rekord in rekordy],
        )
    return len(rekordy)


def pomiary(polaczenie):
    """Chwile pomiarów od najstarszej."""
    return [wiersz[0] for wiersz in polaczenie.execute("SELECT DISTINCT czas FROM pomiary ORDER BY czas")]


def pomiar(polaczenie, czas):
    """Słownik sku -> (nazwa, cena) dla jednej chwili."""
    zapytanie = "SELECT sku, nazwa, cena FROM pomiary WHERE czas = ? ORDER BY sku"
    return {sku: (nazwa, cena) for sku, nazwa, cena in polaczenie.execute(zapytanie, (czas,))}


def historia_produktu(polaczenie, sku):
    return polaczenie.execute("SELECT czas, cena FROM pomiary WHERE sku = ? ORDER BY czas", (sku,)).fetchall()
```

Jedna tabela wystarcza: wiersz to cena jednego produktu w jednej chwili, a indeks po SKU i czasie przyspiesza historię produktu. `otworz()` tworzy schemat, jeśli go nie ma, więc pierwsze uruchomienie nie wymaga żadnego kroku przygotowawczego; `zapisz_pomiar()` wstawia wszystkie rekordy w jednej transakcji (`with polaczenie` z rozdziału 13), a pomiar w bazie jest albo cały, albo żaden. Chwila pomiaru jest tekstem w zapisie rok-miesiąc-dzień godzina:minuta — jak w ISO 8601, tylko ze spacją zamiast litery „T” — który sortuje się chronologicznie. Cena `None` staje się `NULL`.

## Analiza zmian

```python title="monitor/analiza.py"
"""Porównanie dwóch pomiarów i sprawdzenie identyfikatorów produktów."""

import re

SKU = re.compile(r"[A-Z]{2,4}-\d{3}")


def poprawne_sku(rekordy):
    """Dzieli rekordy na te z poprawnym SKU i listę odrzuconych identyfikatorów."""
    dobre = [rekord for rekord in rekordy if SKU.fullmatch(rekord["sku"])]
    return dobre, [rekord["sku"] for rekord in rekordy if not SKU.fullmatch(rekord["sku"])]


def porownaj(poprzedni, biezacy):
    """poprzedni, biezacy: słowniki sku -> (nazwa, cena); zwraca zmiany, nowe i brakujące."""
    zmiany = []
    for sku in sorted(poprzedni.keys() & biezacy.keys()):
        nazwa, stara = poprzedni[sku]
        _, nowa = biezacy[sku]
        if stara == nowa:
            continue
        procent = round((nowa - stara) / stara * 100, 1) if stara and nowa is not None else None
        zmiany.append({"sku": sku, "nazwa": nazwa, "stara": stara, "nowa": nowa, "procent": procent})
    return {
        "zmiany": zmiany,
        "nowe": sorted(biezacy.keys() - poprzedni.keys()),
        "brakujace": sorted(poprzedni.keys() - biezacy.keys()),
    }
```

Porównanie działa na zbiorach kluczy z rozdziału 5 „Python Notatki”: część wspólna daje produkty do porównania cen, różnice — produkty nowe i brakujące. Zmiana procentowa ma sens tylko wtedy, gdy obie ceny są liczbami, a stara jest różna od zera; w pozostałych przypadkach jest `None`, a zmiana i tak trafia do listy, bo pojawienie się albo zniknięcie ceny jest informacją. Wzorzec z rozdziału 19 sprawdza SKU przed zapisem — błędny identyfikator zniekształciłby porównania w każdym późniejszym raporcie.

## Raport

```python title="monitor/raport.py"
"""Raport z dwóch ostatnich pomiarów: arkusz Excel i dokument Word."""

from docx import Document
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font

from monitor import analiza, historia


def dane_raportu(polaczenie):
    chwile = historia.pomiary(polaczenie)
    if len(chwile) < 2:
        raise ValueError("raport wymaga co najmniej dwóch pomiarów")
    poprzedni, biezacy = historia.pomiar(polaczenie, chwile[-2]), historia.pomiar(polaczenie, chwile[-1])
    return chwile[-2], chwile[-1], poprzedni, biezacy, analiza.porownaj(poprzedni, biezacy)


def cena_tekstem(cena):
    return f"{cena:,.2f} zł".replace(",", " ").replace(".", ",") if cena is not None else "brak"


def zapisz_arkusz(polaczenie, sciezka):
    przed, po, poprzedni, biezacy, wynik = dane_raportu(polaczenie)
    skoroszyt = Workbook()
    ceny = skoroszyt.active
    ceny.title = "Ceny"
    ceny.append(["SKU", "Produkt", f"Cena {przed}", f"Cena {po}"])
    for sku, (nazwa, cena) in sorted(biezacy.items()):
        ceny.append([sku, nazwa, poprzedni.get(sku, (None, None))[1], cena])
    zmiany = skoroszyt.create_sheet("Zmiany")
    zmiany.append(["SKU", "Produkt", "Poprzednia", "Bieżąca", "Zmiana %"])
    for zmiana in wynik["zmiany"]:
        zmiany.append([zmiana["sku"], zmiana["nazwa"], zmiana["stara"], zmiana["nowa"], zmiana["procent"]])
    for sku in wynik["nowe"]:
        zmiany.append([sku, biezacy[sku][0], None, biezacy[sku][1], "nowy"])
    for sku in wynik["brakujace"]:
        zmiany.append([sku, poprzedni[sku][0], poprzedni[sku][1], None, "brak"])
    for arkusz in (ceny, zmiany):
        for komorka in arkusz[1]:
            komorka.font = Font(bold=True)
        arkusz.column_dimensions["B"].width = 28
        arkusz.freeze_panes = "A2"
    wykres = BarChart()
    wykres.title = f"Ceny bieżące ({po})"
    wykres.add_data(Reference(ceny, min_col=4, min_row=1, max_row=ceny.max_row), titles_from_data=True)
    wykres.set_categories(Reference(ceny, min_col=2, min_row=2, max_row=ceny.max_row))
    wykres.x_axis.delete = wykres.y_axis.delete = False
    wykres.width, wykres.height = 24, 10
    ceny.add_chart(wykres, "F2")
    skoroszyt.save(sciezka)
    return wynik


def zapisz_dokument(polaczenie, sciezka):
    przed, po, poprzedni, biezacy, wynik = dane_raportu(polaczenie)
    dokument = Document()
    dokument.add_heading("Monitor cen — raport", level=1)
    dokument.add_paragraph(
        f"Porównanie pomiarów {przed} i {po}: {len(biezacy)} produktów, zmian cen: {len(wynik['zmiany'])}, "
        f"nowych: {len(wynik['nowe'])}, brakujących: {len(wynik['brakujace'])}."
    )
    if wynik["zmiany"]:
        tabela = dokument.add_table(rows=1, cols=4)
        tabela.style = "Table Grid"
        for komorka, tekst in zip(tabela.rows[0].cells, ("Produkt", "Poprzednia", "Bieżąca", "Zmiana")):
            komorka.text = tekst
        for zmiana in wynik["zmiany"]:
            komorki = tabela.add_row().cells
            komorki[0].text = zmiana["nazwa"]
            komorki[1].text = cena_tekstem(zmiana["stara"])
            komorki[2].text = cena_tekstem(zmiana["nowa"])
            komorki[3].text = f"{zmiana['procent']:+.1f} %".replace(".", ",") if zmiana["procent"] is not None else "—"
    for etykieta, klucz, zrodlo in (("Nowe produkty", "nowe", biezacy), ("Brakujące produkty", "brakujace", poprzedni)):
        if wynik[klucz]:
            dokument.add_paragraph(f"{etykieta}: " + ", ".join(zrodlo[sku][0] for sku in wynik[klucz]))
    dokument.save(sciezka)
    return wynik
```

Obie funkcje zaczynają od tych samych danych: dwóch ostatnich pomiarów i wyniku porównania. Arkusz „Ceny” zestawia obie ceny każdego produktu z bieżącego pomiaru, arkusz „Zmiany” — tylko różnice, z oznaczeniem produktów nowych i brakujących; wykres pokazuje ceny bieżące. Dokument ma jeden akapit z liczbami i tabelę zmian z procentem ze znakiem (`:+.1f`); dla produktów bez ceny w komórce jest słowo, nie pusta wartość. Formatowanie ogranicza się do tego, co odbiorca zauważy: pogrubiony nagłówek, szersza kolumna nazwy, zablokowany wiersz.

## Wiersz poleceń

```python title="monitor/cli.py"
"""monitor-cen — pobiera ceny ze sklepu, zapisuje historię pomiarów i tworzy raporty."""

import argparse
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from monitor import analiza, historia, raport
from monitor.pobieranie import Pobieracz, strony
from monitor.rekordy import lista_produktow, rekord_produktu

dziennik = logging.getLogger("monitor")


def pobierz(argumenty):
    try:
        pobieracz = Pobieracz(argumenty.adres, opoznienie=argumenty.opoznienie)
    except httpx.TransportError as blad:
        dziennik.error("%s", blad)
        return 1
    try:
        pozycje = []
        for url, zupa in strony(pobieracz, argumenty.adres):
            pozycje.extend(lista_produktow(zupa, url))
        rekordy = [rekord_produktu(BeautifulSoup(pobieracz.pobierz(pozycja["url"]), "html.parser")) for pozycja in pozycje]
    except (httpx.HTTPError, PermissionError) as blad:
        dziennik.error("%s", blad)
        return 1
    finally:
        pobieracz.zamknij()
    rekordy, odrzucone = analiza.poprawne_sku(rekordy)
    for sku in odrzucone:
        dziennik.warning("pominięto rekord o niepoprawnym SKU: %s", sku)
    polaczenie = historia.otworz(argumenty.baza)
    ile = historia.zapisz_pomiar(polaczenie, argumenty.czas, rekordy)
    polaczenie.close()
    print(f"Zapisano pomiar {argumenty.czas}: {ile} produktów")
    return 0


def raportuj(argumenty):
    argumenty.katalog.mkdir(parents=True, exist_ok=True)
    polaczenie = historia.otworz(argumenty.baza)
    try:
        wynik = raport.zapisz_arkusz(polaczenie, argumenty.katalog / "monitor-cen.xlsx")
        raport.zapisz_dokument(polaczenie, argumenty.katalog / "monitor-cen.docx")
    except ValueError as blad:
        dziennik.error("%s", blad)
        return 1
    finally:
        polaczenie.close()
    print(f"Raport: zmian cen {len(wynik['zmiany'])}, nowych {len(wynik['nowe'])}, brakujących {len(wynik['brakujace'])} -> {argumenty.katalog}")
    return 0


def pokaz_historie(argumenty):
    polaczenie = historia.otworz(argumenty.baza)
    wiersze = historia.historia_produktu(polaczenie, argumenty.sku)
    polaczenie.close()
    if not wiersze:
        dziennik.error("brak pomiarów dla %s", argumenty.sku)
        return 1
    for czas, cena in wiersze:
        print(czas, raport.cena_tekstem(cena))
    return 0


def zbuduj_parser():
    parser = argparse.ArgumentParser(prog="monitor-cen", description="Monitor cen sklepu: pomiary, historia i raporty.")
    parser.add_argument("--baza", type=Path, default=Path("monitor.sqlite"), help="plik bazy (domyślnie %(default)s)")
    parser.add_argument("--dziennik", type=Path, metavar="PLIK", help="zapisuj komunikaty do pliku zamiast na stderr")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="więcej komunikatów")
    podpolecenia = parser.add_subparsers(dest="polecenie", required=True)
    pomiar = podpolecenia.add_parser("pobierz", help="pobierz ceny i zapisz pomiar")
    pomiar.add_argument("adres", help="adres pierwszej strony listy produktów")
    pomiar.add_argument("--opoznienie", type=float, default=1.0, metavar="SEK", help="odstęp między żądaniami (domyślnie %(default)s s)")
    pomiar.add_argument("--czas", default=datetime.now().strftime("%Y-%m-%d %H:%M"), help="chwila pomiaru (domyślnie teraz)")
    pomiar.set_defaults(funkcja=pobierz)
    zestawienie = podpolecenia.add_parser("raport", help="arkusz i dokument z dwóch ostatnich pomiarów")
    zestawienie.add_argument("-o", "--katalog", type=Path, default=Path("."), help="katalog wynikowy (domyślnie bieżący)")
    zestawienie.set_defaults(funkcja=raportuj)
    produkt = podpolecenia.add_parser("historia", help="ceny produktu z kolejnych pomiarów")
    produkt.add_argument("sku")
    produkt.set_defaults(funkcja=pokaz_historie)
    return parser


def main(argv=None):
    argumenty = zbuduj_parser().parse_args(argv)
    poziom = [logging.WARNING, logging.INFO, logging.DEBUG][min(argumenty.verbose, 2)]
    if argumenty.dziennik:
        logging.basicConfig(level=poziom, format="%(asctime)s %(levelname)s: %(message)s", filename=argumenty.dziennik, encoding="utf-8", force=True)
    else:
        logging.basicConfig(level=poziom, format="%(levelname)s: %(message)s", stream=sys.stderr, force=True)
    for biblioteka in ("httpx", "httpcore"):
        logging.getLogger(biblioteka).setLevel(logging.WARNING)
    try:
        return argumenty.funkcja(argumenty)
    except (OSError, sqlite3.Error) as blad:
        dziennik.error("%s", blad)
        return 1
```

```python title="monitor/__main__.py"
import sys

from monitor.cli import main

sys.exit(main())
```

Podpolecenia z rozdziału 17: każde ma własne argumenty i funkcję ustawioną przez `set_defaults()` — zamiast łańcucha `if` po nazwie podpolecenia z tamtego rozdziału — a `main()` po wspólnej konfiguracji dziennika wywołuje tę funkcję. Opcje wspólne — baza, plik dziennika, szczegółowość — stoją przed nazwą podpolecenia. `--czas` przyjmuje chwilę pomiaru zamiast bieżącej: przydaje się w testach i przebiegu, gdzie wynik ma być powtarzalny, oraz przy uzupełnianiu historii z zapisanych stron. `--dziennik` przełącza komunikaty na plik z datą w każdym wierszu — tak działa narzędzie z harmonogramu, gdzie `stderr` nie ma odbiorcy. Kody wyjścia i obsługa błędów są takie jak w rozdziale 21: brak połączenia, błąd serwera, zakaz z `robots.txt` oraz błąd pliku lub bazy dają komunikat i `1`, błąd użycia — `2` z `argparse`.

## Przebieg

```python title="symuluj_zmiane.py"
"""Symuluje zmianę w sklepie testowym: podmienia dwie ceny i usuwa jeden produkt z listy."""

import re
from pathlib import Path

ZMIANY = {"329,90": "299,90", "1 299,00": "1 349,00"}
sklep = Path("sklep")
for sciezka in sorted(sklep.glob("*.html")):
    tekst = sciezka.read_text(encoding="utf-8")
    nowy = tekst
    for stara, nowa in ZMIANY.items():
        nowy = re.sub(re.escape(stara) + r"(?= zł)", nowa, nowy)
        nowy = nowy.replace(f'"price": "{stara.replace(" ", "").replace(",", ".")}"', f'"price": "{nowa.replace(" ", "").replace(",", ".")}"')
    nowy = re.sub(r'<li class="produkt" data-id="10">.*?</li>\n', "", nowy, flags=re.S)
    if nowy != tekst:
        sciezka.write_text(nowy, encoding="utf-8")
        print("zmieniono:", sciezka.name)
```

```python title="uzycie-monitor.py"
import os
import subprocess
import sys
from pathlib import Path

from docx import Document
from openpyxl import load_workbook

from sklep_serwer import uruchom

srodowisko = {**os.environ, "PYTHONUTF8": "1"}
subprocess.run([sys.executable, "zbuduj_sklep.py"], check=True, capture_output=True)
Path("monitor.sqlite").unlink(missing_ok=True)
serwer, adres = uruchom("sklep")


def monitor(*argumenty, baza="monitor.sqlite"):
    proces = subprocess.run([sys.executable, "-m", "monitor", "--baza", baza, *argumenty], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", env=srodowisko)
    print(proces.stdout.rstrip() + f" [kod {proces.returncode}]")


monitor("pobierz", adres + "index.html", "--opoznienie", "0", "--czas", "2026-09-22 08:00")
monitor("raport", "-o", "raporty")
print(subprocess.run([sys.executable, "symuluj_zmiane.py"], capture_output=True, text=True, encoding="utf-8", env=srodowisko).stdout.rstrip())
monitor("--dziennik", "monitor.log", "-v", "pobierz", adres + "index.html", "--opoznienie", "0", "--czas", "2026-09-23 08:00")
print(Path("monitor.log").read_text(encoding="utf-8").splitlines()[-1].split(": ", 1)[1])
monitor("historia", "AGD-003")
monitor("historia", "AGD-999")
monitor("raport", "-o", "raporty")
serwer.shutdown()
skoroszyt = load_workbook("raporty/monitor-cen.xlsx")
print(skoroszyt.sheetnames, list(skoroszyt["Zmiany"].iter_rows(min_row=1, values_only=True)))
print([akapit.text for akapit in Document("raporty/monitor-cen.docx").paragraphs][:3])
```

```{ .text .no-copy }
Zapisano pomiar 2026-09-22 08:00: 10 produktów [kod 0]
ERROR: raport wymaga co najmniej dwóch pomiarów [kod 1]
zmieniono: index.html
zmieniono: produkt-3.html
zmieniono: produkt-7.html
zmieniono: strona-2.html
Zapisano pomiar 2026-09-23 08:00: 9 produktów [kod 0]
pobrano: /produkt-9.html (580 bajtów)
2026-09-22 08:00 329,90 zł
2026-09-23 08:00 299,90 zł [kod 0]
ERROR: brak pomiarów dla AGD-999 [kod 1]
Raport: zmian cen 2, nowych 0, brakujących 1 -> raporty [kod 0]
['Ceny', 'Zmiany'] [('SKU', 'Produkt', 'Poprzednia', 'Bieżąca', 'Zmiana %'), ('AGD-003', 'Ekspres przelewowy', 329.9, 299.9, -9.1), ('AGD-007', 'Robot planetarny', 1299, 1349, 3.8), ('AGD-010', 'Grill elektryczny', 289, None, 'brak')]
['Monitor cen — raport', 'Porównanie pomiarów 2026-09-22 08:00 i 2026-09-23 08:00: 9 produktów, zmian cen: 2, nowych: 0, brakujących: 1.', 'Brakujące produkty: Grill elektryczny']
```

Skrypt kontrolny odtwarza sklep, usuwa poprzednią bazę i uruchamia narzędzie jako proces `python -m monitor` z połączonymi strumieniami, jak w rozdziale 20. Pierwszy pomiar zapisuje dziesięć produktów; raport po jednym pomiarze kończy się błędem i kodem `1`. Symulacja obniża cenę ekspresu, podnosi cenę robota i usuwa grill z listy — wzorzec z rozdziału 19 podmienia ceny w tekście, `replace()` — w danych JSON-LD. Drugi pomiar pisze dziennik do pliku; skrypt wypisuje treść ostatniego wpisu bez daty i poziomu, które stoją na początku każdego wiersza. Historia produktu pokazuje obie ceny, nieznany SKU daje kod `1`, a raport po dwóch pomiarach wypisuje liczbę zmian i zapisuje oba pliki: arkusz „Zmiany” ma dwie zmiany cen i jeden brakujący produkt, dokument — akapit z liczbami i listę brakujących.
