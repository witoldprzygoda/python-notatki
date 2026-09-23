# Raport z danych

Trzy biblioteki łączą się w jednym narzędziu: z pliku CSV powstają arkusz z formułami i wykresem oraz dokument z podsumowaniem i obrazem. Narzędzie stosuje reguły z rozdziału 20 — argumenty, kody wyjścia, `main(argv)` — i testy, które otwierają wytworzone pliki z powrotem.

## Narzędzie raport

```python title="raport.py"
"""raport — z pliku CSV sprzedaży tworzy arkusz Excel i dokument Word z podsumowaniem."""

import argparse
import csv
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

from docx import Document
from docx.shared import Cm
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Font

from slupki import wykres_slupkowy


def wczytaj(sciezka):
    with open(sciezka, encoding="utf-8", newline="") as plik:
        wiersze = list(csv.DictReader(plik))
    if not wiersze or {"data", "produkt", "kategoria", "ilosc", "cena"} - set(wiersze[0]):
        raise ValueError(f"{sciezka}: oczekiwane kolumny data, produkt, kategoria, ilosc, cena")
    return wiersze


def podsumuj(wiersze, klucz):
    suma = defaultdict(float)
    for wiersz in wiersze:
        suma[wiersz[klucz]] += int(wiersz["ilosc"]) * float(wiersz["cena"])
    return sorted(suma.items(), key=lambda para: -para[1])


def zapisz_arkusz(wiersze, sciezka):
    skoroszyt = Workbook()
    arkusz = skoroszyt.active
    arkusz.title = "Sprzedaż"
    arkusz.append(["Data", "Produkt", "Kategoria", "Ilość", "Cena", "Wartość"])
    for numer, wiersz in enumerate(wiersze, 2):
        arkusz.append([date.fromisoformat(wiersz["data"]), wiersz["produkt"], wiersz["kategoria"], int(wiersz["ilosc"]), float(wiersz["cena"]), f"=D{numer}*E{numer}"])
    arkusz.append(["Razem", None, None, None, None, f"=SUM(F2:F{len(wiersze) + 1})"])
    for komorka in arkusz[1]:
        komorka.font = Font(bold=True)
    for wiersz in arkusz.iter_rows(min_row=2):
        wiersz[0].number_format = "YYYY-MM-DD"
        wiersz[4].number_format = wiersz[5].number_format = "#,##0.00 zł"
    arkusz.column_dimensions["B"].width = 28
    arkusz.freeze_panes = "A2"
    podsumowanie = skoroszyt.create_sheet("Podsumowanie")
    podsumowanie.append(["Produkt", "Wartość"])
    for produkt, wartosc in podsumuj(wiersze, "produkt"):
        podsumowanie.append([produkt, round(wartosc, 2)])
    wykres = BarChart()
    wykres.title = "Sprzedaż według produktu"
    wykres.add_data(Reference(podsumowanie, min_col=2, min_row=1, max_row=podsumowanie.max_row), titles_from_data=True)
    wykres.set_categories(Reference(podsumowanie, min_col=1, min_row=2, max_row=podsumowanie.max_row))
    wykres.x_axis.delete = wykres.y_axis.delete = False
    podsumowanie.add_chart(wykres, "D2")
    skoroszyt.save(sciezka)


def zapisz_dokument(wiersze, sciezka, obraz_wykresu):
    dokument = Document()
    dokument.add_heading("Raport sprzedaży", level=1)
    kategorie = podsumuj(wiersze, "kategoria")
    razem = f"{sum(wartosc for _, wartosc in kategorie):,.2f}".replace(",", " ").replace(".", ",")
    dokument.add_paragraph(f"Okres {wiersze[0]['data']} – {wiersze[-1]['data']}, {len(wiersze)} transakcji, łącznie {razem} zł.")
    tabela = dokument.add_table(rows=1, cols=2)
    tabela.style = "Table Grid"
    tabela.rows[0].cells[0].text, tabela.rows[0].cells[1].text = "Kategoria", "Wartość"
    for kategoria, wartosc in kategorie:
        komorki = tabela.add_row().cells
        komorki[0].text, komorki[1].text = kategoria, f"{wartosc:,.2f}".replace(",", " ").replace(".", ",")
    dokument.add_heading("Produkty", level=2)
    dokument.add_picture(str(obraz_wykresu), width=Cm(15))
    dokument.save(sciezka)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="raport", description="Tworzy arkusz Excel i dokument Word z pliku CSV sprzedaży.")
    parser.add_argument("csv", type=Path, help="plik CSV z kolumnami data, produkt, kategoria, ilosc, cena")
    parser.add_argument("-o", "--katalog", type=Path, default=Path("."), help="katalog wynikowy (domyślnie bieżący)")
    parser.add_argument("--format", choices=["xlsx", "docx", "oba"], default="oba", help="co wytworzyć (domyślnie %(default)s)")
    argumenty = parser.parse_args(argv)
    nazwa = argumenty.csv.stem
    wytworzone = []
    try:
        wiersze = wczytaj(argumenty.csv)
        argumenty.katalog.mkdir(parents=True, exist_ok=True)
        if argumenty.format in ("xlsx", "oba"):
            zapisz_arkusz(wiersze, argumenty.katalog / f"{nazwa}.xlsx")
            wytworzone.append(f"{nazwa}.xlsx")
        if argumenty.format in ("docx", "oba"):
            wykres = argumenty.katalog / f"{nazwa}-wykres.png"
            wykres_slupkowy(podsumuj(wiersze, "produkt")[:6], wykres, "Sprzedaż według produktu (zł)")
            zapisz_dokument(wiersze, argumenty.katalog / f"{nazwa}.docx", wykres)
            wytworzone += [f"{nazwa}-wykres.png", f"{nazwa}.docx"]
    except (OSError, ValueError) as blad:
        print(f"raport: {blad}", file=sys.stderr)
        return 1
    print("Zapisano:", ", ".join(wytworzone), "w", argumenty.katalog)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

```python title="uzycie-raport.py"
import os
import subprocess
import sys
from pathlib import Path

from docx import Document
from openpyxl import load_workbook

import raport

print("kod:", raport.main(["sprzedaz.csv", "-o", "wyniki"]))
print(sorted(p.name for p in Path("wyniki").iterdir()))
skoroszyt = load_workbook("wyniki/sprzedaz.xlsx")
print(skoroszyt.sheetnames, skoroszyt["Sprzedaż"]["F14"].value, skoroszyt["Podsumowanie"]["A2"].value)
dokument = Document("wyniki/sprzedaz.docx")
print(dokument.paragraphs[1].text)
print([komorka.text for komorka in dokument.tables[0].rows[1].cells], len(dokument.inline_shapes))
print("kod:", raport.main(["sprzedaz.csv", "--format", "docx", "-o", "wyniki/tylko-word"]))
Path("zly.csv").write_text("a,b\n1,2\n", encoding="utf-8")
for argumenty in (["brak.csv"], ["zly.csv"]):
    proces = subprocess.run([sys.executable, "raport.py", *argumenty], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", env={**os.environ, "PYTHONUTF8": "1"})
    print(proces.stdout.strip(), f"[kod {proces.returncode}]")
```

```{ .text .no-copy }
Zapisano: sprzedaz.xlsx, sprzedaz-wykres.png, sprzedaz.docx w wyniki
kod: 0
['sprzedaz-wykres.png', 'sprzedaz.docx', 'sprzedaz.xlsx']
['Sprzedaż', 'Podsumowanie'] =SUM(F2:F13) Robot planetarny
Okres 2026-09-01 – 2026-09-06, 12 transakcji, łącznie 5 131,42 zł.
['AGD', '3 679,90'] 1
Zapisano: sprzedaz-wykres.png, sprzedaz.docx w wyniki\tylko-word
kod: 0
raport: [Errno 2] No such file or directory: 'brak.csv' [kod 1]
raport: zly.csv: oczekiwane kolumny data, produkt, kategoria, ilosc, cena [kod 1]
```

Narzędzie dzieli pracę na funkcje o jednym zadaniu: wczytanie i sprawdzenie kolumn, podsumowanie po dowolnym kluczu, zapis arkusza, zapis dokumentu. `main()` tylko składa je według argumentów i tłumaczy błędy — brak pliku, złe kolumny, niepoprawną liczbę w wierszu, plik wynikowy otwarty w Excelu — na komunikat na `stderr` i kod `1`. Nazwy plików wynikowych pochodzą od nazwy pliku wejściowego, a katalog wynikowy powstaje w razie potrzeby. Skrypt kontrolny wywołuje `main()` z listą argumentów i otwiera wytworzone pliki obiema bibliotekami: formuła sumy w wierszu 14, pierwszy produkt podsumowania, akapit i tabela dokumentu oraz jeden obraz w dokumencie; przypadki błędne uruchamia jako proces z połączonymi strumieniami, jak w rozdziale 20.

## Testy

```python title="test_raport.py"
from pathlib import Path

import pytest
from docx import Document
from openpyxl import load_workbook

import raport

CSV = "data,produkt,kategoria,ilosc,cena\n2026-09-01,Czajnik,AGD,2,100.00\n2026-09-02,Termos,Akcesoria,3,50.00\n2026-09-03,Czajnik,AGD,1,100.00\n"


@pytest.fixture
def plik_csv(tmp_path):
    sciezka = tmp_path / "dane.csv"
    sciezka.write_text(CSV, encoding="utf-8")
    return sciezka


def test_podsumowanie_po_produkcie():
    wiersze = raport.wczytaj(Path(__file__).with_name("sprzedaz.csv"))
    produkty = dict(raport.podsumuj(wiersze, "produkt"))
    assert produkty["Waga kuchenna"] == pytest.approx(8 * 69.99)
    assert raport.podsumuj(wiersze, "produkt")[0][0] == "Robot planetarny"


def test_narzedzie_tworzy_oba_pliki(plik_csv, tmp_path, capsys):
    assert raport.main([str(plik_csv), "-o", str(tmp_path / "wyniki")]) == 0
    assert "dane.xlsx, dane-wykres.png, dane.docx" in capsys.readouterr().out
    arkusz = load_workbook(tmp_path / "wyniki" / "dane.xlsx")["Sprzedaż"]
    assert arkusz["F2"].value == "=D2*E2" and arkusz["A5"].value == "Razem"
    podsumowanie = load_workbook(tmp_path / "wyniki" / "dane.xlsx")["Podsumowanie"]
    assert [w for w in podsumowanie.iter_rows(min_row=2, values_only=True)] == [("Czajnik", 300.0), ("Termos", 150.0)]
    dokument = Document(tmp_path / "wyniki" / "dane.docx")
    assert "3 transakcji, łącznie 450,00 zł" in dokument.paragraphs[1].text
    assert [k.text for k in dokument.tables[0].rows[1].cells] == ["AGD", "300,00"]
    assert len(dokument.inline_shapes) == 1


def test_zle_kolumny_to_kod_1(tmp_path, capsys):
    zly = tmp_path / "zly.csv"
    zly.write_text("a,b\n1,2\n", encoding="utf-8")
    assert raport.main([str(zly)]) == 1
    assert "oczekiwane kolumny" in capsys.readouterr().err
```

```powershell title="Terminal"
python -m pytest -q
```

```{ .text .no-copy }
...                                                                      [100%]
3 passed in 0.49s
```

Testy używają małego CSV wpisanego w kod, więc oczekiwane liczby da się sprawdzić w pamięci; test podsumowania czyta plik rozdziału ścieżką od `__file__`, żeby nie zależeć od katalogu bieżącego. Pliki wynikowe testujemy tak, jak zrobi to odbiorca — otwierając je: formuła i wiersz „Razem” w arkuszu, podsumowanie w drugim arkuszu, akapit, tabela i obraz w dokumencie. `pytest.approx()` porównuje liczby zmiennoprzecinkowe z tolerancją.

## Inne formaty

Prezentacje `.pptx` obsługuje biblioteka python-pptx tym samym modelem co python-docx: slajd, układ, pola tekstowe, obrazy. Z formatem PDF wiążą się dwa zadania: tekst i strony istniejących plików czyta pypdf, a dokumenty od zera tworzy reportlab; obie biblioteki są poza zakresem tej książki. Formaty OpenDocument (`.ods`, `.odt`) LibreOffice konwertuje z formatów Office i na nie poleceniem `soffice --headless --convert-to` ze strony o dokumentach Word. Dla samych danych tabelarycznych najprostszym formatem wymiany pozostaje CSV z rozdziału 9 „Python Notatki” — arkusz i dokument są dla odbiorcy, nie dla programu.

## Lista kontrolna

- **openpyxl**: formuły jako tekst `=…`, liczone przez Excel; `data_only=True` tylko dla plików zapisanych przez Excel; formaty liczb i dat w zapisie Excela; `freeze_panes`, szerokości kolumn, wykres z `Reference`.
- **pandas `to_excel()`** dla całych tabel, openpyxl dla formatowania; oba na jednym pliku.
- **python-docx**: style „Heading N”, „List Bullet”, „Table Grid”; formatowanie na biegach; wymiary w `Cm`/`Pt`; szablon z polami `{{…}}` podstawianymi w biegach.
- **Pillow**: `thumbnail()` w miejscu z proporcjami, `resize()` nowy obraz; JPEG bez przezroczystości; polskie litery tylko z czcionką `truetype()`; znak wodny na warstwie `RGBA`; `with Image.open()` w pętlach.
- **Narzędzie**: funkcje o jednym zadaniu, `main(argv)` z kodami wyjścia, testy otwierające pliki wynikowe.
- **Konwersja i PDF**: LibreOffice `--headless --convert-to`.

## Dalej: projekt narzędzia

Ścieżka Automatyzacja kończy się projektem: narzędziem, które pobiera dane ze stron jak w rozdziale 21, przetwarza je wzorcami z rozdziału 19, a wynik oddaje jako arkusz i dokument z tego rozdziału — uruchamianym z wiersza poleceń według reguł z rozdziału 20: [rozdział 23](../23-projekt-automatyzacja/index.md).
