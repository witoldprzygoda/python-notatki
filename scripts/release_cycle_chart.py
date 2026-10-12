"""Wykres okresów wsparcia wersji Pythona z przewodnika dla deweloperów CPythona.

Pobiera stronę https://devguide.python.org/versions/ (albo czyta jej zapisaną kopię
podaną opcją --html), wycina pierwszy element <svg class="release-cycle-chart">
bez zmian i zapisuje go jako samodzielny plik SVG z deklaracją XML. Tak powstaje
rysunek docs/01-instalacja/img/python-cykl-wydan.svg (instalacja.md).

Pionowa linia na wykresie oznacza dzień, w którym przewodnik wygenerował stronę
(nagłówek Last-Modified), a nie dzień pobrania; skrypt wypisuje ten nagłówek.
Po odświeżeniu rysunku trzeba sprawdzić tekst alternatywny i opis faz w instalacja.md.

Istniejącego pliku wynikowego skrypt nie nadpisuje bez opcji --nadpisz.

Użycie: python scripts/release_cycle_chart.py <wynik.svg> [--html=strona.html] [--nadpisz]
"""

import re
import sys
import urllib.request
from pathlib import Path

ADRES = "https://devguide.python.org/versions/"
# serwer odrzuca domyślny nagłówek User-Agent biblioteki urllib (HTTP 403)
NAGLOWKI = {"User-Agent": "python-notatki/release_cycle_chart"}
WYKRES = re.compile(
    r'<svg\s+xmlns="http://www.w3.org/2000/svg"\s+class="release-cycle-chart".*?</svg>', re.S
)


def main(argumenty: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    opcje = [a for a in argumenty if a.startswith("--")]
    pozycyjne = [a for a in argumenty if not a.startswith("--")]
    if len(pozycyjne) != 1:
        print(__doc__)
        return 2
    wynik = Path(pozycyjne[0])
    nadpisz = "--nadpisz" in opcje
    html = next((a.split("=", 1)[1] for a in opcje if a.startswith("--html=")), None)
    if wynik.exists() and not nadpisz:
        print(f"{wynik} już istnieje; użyj --nadpisz, aby go zastąpić")
        return 1
    if html:
        tekst = Path(html).read_text(encoding="utf-8")
    else:
        zadanie = urllib.request.Request(ADRES, headers=NAGLOWKI)
        with urllib.request.urlopen(zadanie, timeout=30) as odpowiedz:
            print("Last-Modified:", odpowiedz.headers.get("Last-Modified"))
            tekst = odpowiedz.read().decode("utf-8")
    dopasowanie = WYKRES.search(tekst)
    if not dopasowanie:
        print("brak wykresu release-cycle-chart na stronie")
        return 1
    wynik.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n' + dopasowanie.group(0) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("zapisano", wynik)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
