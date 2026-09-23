# Dokumenty Word

Dokument `.docx` składa się z akapitów, a akapit z **biegów** (ang. *run*) — fragmentów tekstu o jednym formatowaniu. Tabele są elementami między akapitami; obraz i podział strony python-docx wstawia jako zawartość biegu w osobnym akapicie. python-docx buduje dokument z takich elementów i czyta je z istniejącego pliku.

## Budowa dokumentu

```python title="dokument.py"
import csv
from collections import defaultdict

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

with open("sprzedaz.csv", encoding="utf-8", newline="") as plik:
    wiersze = list(csv.DictReader(plik))
suma = defaultdict(float)
for wiersz in wiersze:
    suma[wiersz["kategoria"]] += int(wiersz["ilosc"]) * float(wiersz["cena"])

dokument = Document()
dokument.core_properties.author = "raport"
dokument.core_properties.title = "Raport sprzedaży"
dokument.add_heading("Raport sprzedaży", level=1)
akapit = dokument.add_paragraph("Zestawienie za okres ")
akapit.add_run(f"{wiersze[0]['data']} – {wiersze[-1]['data']}").bold = True
akapit.add_run(f" obejmuje {len(wiersze)} transakcji na łączną kwotę ")
akapit.add_run(f"{sum(suma.values()):,.2f} zł".replace(",", " ").replace(".", ",")).italic = True
akapit.add_run(".")
dokument.add_heading("Kategorie", level=2)
for kategoria, wartosc in sorted(suma.items()):
    dokument.add_paragraph(f"{kategoria}: {wartosc:,.2f} zł".replace(",", " ").replace(".", ","), style="List Bullet")

tabela = dokument.add_table(rows=1, cols=3)
tabela.style = "Table Grid"
for komorka, tekst in zip(tabela.rows[0].cells, ("Data", "Produkt", "Wartość")):
    komorka.text = tekst
    komorka.paragraphs[0].runs[0].bold = True
for wiersz in wiersze[:5]:
    komorki = tabela.add_row().cells
    komorki[0].text = wiersz["data"]
    komorki[1].text = wiersz["produkt"]
    komorki[2].text = f"{int(wiersz['ilosc']) * float(wiersz['cena']):.2f}".replace(".", ",")
    komorki[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
uwaga = dokument.add_paragraph()
uwaga.add_run("Pięć pierwszych transakcji; pełne dane w arkuszu.").font.size = Pt(9)
dokument.add_page_break()
dokument.add_heading("Załącznik", level=2)
dokument.add_paragraph("Wykres sprzedaży według produktu znajduje się na następnej stronie.")
dokument.save("raport.docx")
print(len(dokument.paragraphs), len(dokument.tables), len(tabela.rows), dokument.core_properties.title)
```

```{ .text .no-copy }
9 1 6 Raport sprzedaży
```

`Document()` otwiera pusty dokument z domyślnym szablonem biblioteki (wzorowanym na szablonie Worda), w którym istnieją gotowe style: `add_heading(level=1)` używa stylu „Heading 1”, `add_paragraph(style="List Bullet")` — listy punktowanej. Akapit zwrócony przez `add_paragraph()` przyjmuje kolejne biegi przez `add_run()`; bieg ma własne pogrubienie, kursywę i czcionkę (`font.size` w punktach). Liczby formatujemy po polsku — spacja jako separator tysięcy, przecinek dziesiętny — bo dokument czyta człowiek, nie program. Tabela powstaje z liczbą kolumn i wierszem nagłówka, a kolejne wiersze dodaje `add_row()`; komórka ma własne akapity, więc wyrównanie i pogrubienie ustawiamy na jej akapicie i biegu. Styl „Table Grid” daje obramowanie. Wymiary podajemy w jednostkach `Pt` lub `Cm` (szerokość obrazu na stronie o raporcie), nie w surowych liczbach. Właściwości dokumentu (autor, tytuł) Word pokazuje w informacjach o pliku.

<!-- TODO: screenshot — raport.docx otwarty w Wordzie: nagłówek, akapit z pogrubionym zakresem dat, lista punktowana i tabela z obramowaniem -->

## Odczyt i szablon

```python title="szablon.py"
from docx import Document

dokument = Document("raport.docx")
print([akapit.style.name for akapit in dokument.paragraphs][:4])
print([akapit.text for akapit in dokument.paragraphs if akapit.style.name.startswith("Heading")])
tabela = dokument.tables[0]
print([komorka.text for komorka in tabela.rows[1].cells], len(tabela.rows))

szablon = Document()
szablon.add_heading("Umowa nr {{numer}}", level=1)
szablon.add_paragraph("Zawarta dnia {{data}} pomiędzy {{sprzedawca}} a {{kupujacy}}.")
akapit = szablon.add_paragraph("Przedmiot: ")
akapit.add_run("{{przedmiot}}").bold = True
szablon.save("szablon-umowy.docx")

pola = {"numer": "17/2026", "data": "23 września 2026", "sprzedawca": "Sklep AGD", "kupujacy": "Jan Kowalski", "przedmiot": "Czajnik elektryczny"}
umowa = Document("szablon-umowy.docx")
for akapit in umowa.paragraphs:
    for bieg in akapit.runs:
        for nazwa, wartosc in pola.items():
            bieg.text = bieg.text.replace("{{" + nazwa + "}}", wartosc)
umowa.save("umowa-17-2026.docx")
print([akapit.text for akapit in Document("umowa-17-2026.docx").paragraphs])
print(Document("umowa-17-2026.docx").paragraphs[2].runs[1].bold)
```

```{ .text .no-copy }
['Heading 1', 'Normal', 'Heading 2', 'List Bullet']
['Raport sprzedaży', 'Kategorie', 'Załącznik']
['2026-09-01', 'Czajnik elektryczny', '447,00'] 6
['Umowa nr 17/2026', 'Zawarta dnia 23 września 2026 pomiędzy Sklep AGD a Jan Kowalski.', 'Przedmiot: Czajnik elektryczny']
True
```

Odczyt daje listę akapitów z tekstem i nazwą stylu — nagłówki rozpoznajemy po stylu — oraz tabele z wierszami i komórkami. Najczęstsze zastosowanie odczytu to **szablon**: dokument z polami `{{nazwa}}` przygotowany w Wordzie, w którym program podstawia wartości. Podstawiamy w biegach, nie w akapitach, żeby zachować formatowanie (pogrubiony przedmiot umowy pozostaje pogrubiony). Pułapka: Word dzieli tekst na biegi według własnej historii edycji, więc pole wpisane ręcznie może być rozbite na kilka biegów (`{{`, `numer`, `}}`) i podstawienie go nie znajdzie; szablon warto wkleić do Worda jako czysty tekst albo przed podstawieniem wypisać teksty biegów każdego akapitu.

## Format i konwersja

python-docx czyta i pisze wyłącznie `.docx`; starszy binarny `.doc` trzeba zapisać ponownie w Wordzie. Biblioteka nie renderuje dokumentu — nie zna podziału na strony ani wyglądu — i nie zapisze PDF. Do konwersji służy zainstalowany edytor: LibreOffice uruchamiany z wiersza poleceń przez `subprocess` z rozdziału 20:

```powershell title="Terminal"
soffice --headless --convert-to pdf raport.docx
```

To samo polecenie konwertuje `.xlsx` i `.pptx`; jeśli zamiast `pdf` podać `xlsx` (z `--outdir`, żeby nie nadpisać źródła), LibreOffice zapisuje arkusz z openpyxl ponownie i zwykle uzupełnia wartości formuł, których plik nie miał — wynik sprawdzamy odczytem z `data_only=True`.
