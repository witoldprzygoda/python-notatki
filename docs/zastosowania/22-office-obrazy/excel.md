# Arkusze Excel

Plik `.xlsx` to **skoroszyt** (ang. *workbook*) z jednym lub wieloma **arkuszami** (ang. *worksheet*), a arkusz to siatka komórek adresowanych literą kolumny i numerem wiersza. openpyxl odwzorowuje ten model wprost: skoroszyt, arkusz, komórka z wartością i formatem.

## Zapis arkusza

```python title="arkusz.py"
import csv
from datetime import date

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

with open("sprzedaz.csv", encoding="utf-8", newline="") as plik:
    wiersze = list(csv.DictReader(plik))

skoroszyt = Workbook()
arkusz = skoroszyt.active
arkusz.title = "Sprzedaż"
arkusz.append(["Data", "Produkt", "Kategoria", "Ilość", "Cena", "Wartość"])
for numer, wiersz in enumerate(wiersze, 2):
    arkusz.append([date.fromisoformat(wiersz["data"]), wiersz["produkt"], wiersz["kategoria"], int(wiersz["ilosc"]), float(wiersz["cena"]), f"=D{numer}*E{numer}"])
ostatni = len(wiersze) + 1
arkusz.append(["Razem", None, None, f"=SUM(D2:D{ostatni})", None, f"=SUM(F2:F{ostatni})"])

for komorka in arkusz[1]:
    komorka.font = Font(bold=True)
    komorka.fill = PatternFill("solid", fgColor="DDEBF7")
    komorka.alignment = Alignment(horizontal="center")
for wiersz in arkusz.iter_rows(min_row=2, max_row=ostatni + 1):
    wiersz[0].number_format = "YYYY-MM-DD"
    wiersz[4].number_format = wiersz[5].number_format = "#,##0.00 zł"
for kolumna, szerokosc in zip("ABCDEF", (12, 28, 12, 8, 14, 14)):
    arkusz.column_dimensions[kolumna].width = szerokosc
arkusz.freeze_panes = "A2"
arkusz.auto_filter.ref = f"A1:F{ostatni}"
skoroszyt.save("sprzedaz.xlsx")
print(arkusz.dimensions, arkusz["F2"].value, arkusz["A2"].value, type(arkusz["E2"].value).__name__)
```

```{ .text .no-copy }
A1:F14 =D2*E2 2026-09-01 float
```

`Workbook()` tworzy skoroszyt z jednym arkuszem (`active`); `append()` dodaje wiersz z listy wartości, a komórkę można też ustawić po adresie, jak w słowniku (`arkusz["F2"]`). Wartości zachowują typy Pythona: data staje się datą Excela, liczby liczbami, a tekst zaczynający się od `=` — formułą, którą openpyxl zapisuje bez wyniku i **nie liczy**: policzy ją Excel przy otwarciu pliku. Kolumna „Wartość” i wiersz „Razem” są więc formułami, nie liczbami z Pythona — gdy użytkownik zmieni ilość, arkusz przeliczy się sam. Formatowanie to obiekty przypisane do komórek: czcionka, wypełnienie, wyrównanie, **format liczbowy** w zapisie Excela (`#,##0.00 zł` — separator tysięcy, dwa miejsca, jednostka), szerokości kolumn w znakach; `freeze_panes` blokuje wiersz nagłówka przy przewijaniu, a `auto_filter` dodaje filtry w nagłówku. Wymiary arkusza (`dimensions`) obejmują wszystkie zapisane komórki.

<!-- TODO: screenshot — arkusz sprzedaz.xlsx otwarty w Excelu: nagłówek z wypełnieniem i filtrami, formaty walutowe, wiersz Razem -->

## Odczyt arkusza

```python title="odczyt.py"
from openpyxl import load_workbook

skoroszyt = load_workbook("sprzedaz.xlsx")
print(skoroszyt.sheetnames)
arkusz = skoroszyt["Sprzedaż"]
print(arkusz.max_row, arkusz.max_column, arkusz["F2"].value, arkusz["A2"].value, arkusz["E2"].value)
for wiersz in arkusz.iter_rows(min_row=2, max_row=4, values_only=True):
    print(wiersz)
naglowki = [komorka.value for komorka in arkusz[1]]
rekordy = [dict(zip(naglowki, wiersz)) for wiersz in arkusz.iter_rows(min_row=2, max_row=arkusz.max_row - 1, values_only=True)]
print(len(rekordy), rekordy[0]["Produkt"], sum(r["Ilość"] * r["Cena"] for r in rekordy))
print(load_workbook("sprzedaz.xlsx", data_only=True)["Sprzedaż"]["F2"].value)
```

```{ .text .no-copy }
['Sprzedaż']
14 6 =D2*E2 2026-09-01 00:00:00 149
(datetime.datetime(2026, 9, 1, 0, 0), 'Czajnik elektryczny', 'AGD', 3, 149, '=D2*E2')
(datetime.datetime(2026, 9, 1, 0, 0), 'Toster dwukomorowy', 'AGD', 2, 199, '=D3*E3')
(datetime.datetime(2026, 9, 2, 0, 0), 'Waga kuchenna', 'Akcesoria', 5, 69.99, '=D4*E4')
12 Czajnik elektryczny 5131.42
None
```

`load_workbook()` czyta plik; `iter_rows(values_only=True)` daje krotki wartości bez obiektów komórek, a złożenie z nagłówkami — listę słowników jak z `csv.DictReader` w rozdziale 9 „Python Notatki”. Trzy własności odczytu wymagają uwagi: liczba zapisana jako `149.0` wraca jako `149`, bo plik przechowuje ją bez części ułamkowej; data wraca jako `datetime` z zerową godziną, bo Excel nie odróżnia daty od chwili; komórka z formułą zwraca tekst formuły. Opcja `data_only=True` zwraca wartości policzone — ale plik zapisany przez openpyxl, którego Excel nigdy nie zapisał, nie ma ich wcale i daje `None`. Wartość liczymy więc sami w Pythonie (suma iloczynów) albo czytamy plik po zapisaniu go przez Excel.

## Podsumowanie i wykres

```python title="wykres.py"
from collections import defaultdict

from openpyxl import load_workbook
from openpyxl.chart import BarChart, Reference

skoroszyt = load_workbook("sprzedaz.xlsx")
sprzedaz = skoroszyt["Sprzedaż"]
suma = defaultdict(float)
for _, produkt, kategoria, ilosc, cena, _ in sprzedaz.iter_rows(min_row=2, max_row=sprzedaz.max_row - 1, values_only=True):
    suma[produkt] += ilosc * cena

podsumowanie = skoroszyt.create_sheet("Podsumowanie")
podsumowanie.append(["Produkt", "Wartość"])
for produkt, wartosc in sorted(suma.items(), key=lambda para: -para[1]):
    podsumowanie.append([produkt, round(wartosc, 2)])
podsumowanie.column_dimensions["A"].width = 28
wykres = BarChart()
wykres.title = "Sprzedaż według produktu"
wykres.y_axis.title = "zł"
wykres.add_data(Reference(podsumowanie, min_col=2, min_row=1, max_row=podsumowanie.max_row), titles_from_data=True)
wykres.set_categories(Reference(podsumowanie, min_col=1, min_row=2, max_row=podsumowanie.max_row))
wykres.x_axis.delete = wykres.y_axis.delete = False
wykres.height, wykres.width = 9, 18
podsumowanie.add_chart(wykres, "D2")
skoroszyt.save("sprzedaz-podsumowanie.xlsx")
print(skoroszyt.sheetnames, podsumowanie.max_row, [w for w in podsumowanie.iter_rows(min_row=2, max_row=3, values_only=True)])
```

```{ .text .no-copy }
['Sprzedaż', 'Podsumowanie'] 12 [('Robot planetarny', 1299.0), ('Waga kuchenna', 559.92)]
```

Podsumowanie po produkcie liczymy w Pythonie (`defaultdict` z rozdziału 7 „Python Notatki”) i zapisujemy w drugim arkuszu jako liczby: grupowanie po nazwie jest prostsze w Pythonie niż w formułach, a wartości są dostępne także dla programu, który czyta plik bez Excela. `BarChart` dostaje dane przez `Reference` — zakres komórek arkusza z nagłówkiem jako tytułem serii — i osobno kategorie z pierwszej kolumny; osie włączamy jawnie (`delete = False`), bo bez tego znacznika nowsze wersje Excela rysują wykres bez podpisów kategorii i skali; `add_chart()` umieszcza wykres w komórce, a wymiary są w centymetrach. Wykres jest częścią pliku: Excel rysuje go przy otwarciu i aktualizuje po zmianie danych. Formatowanie warunkowe i walidację danych openpyxl też potrafi zapisać — dokumentacja biblioteki opisuje je w tym samym stylu obiektów przypisanych do arkusza; tabel przestawnych nie tworzy, jedynie zachowuje istniejące przy odczycie i ponownym zapisie pliku.

## Arkusz a pandas

Gdy zadaniem jest zapisać całą tabelę, prostsza jest metoda `to_excel()` z rozdziału 4: pandas zapisuje nagłówki, typy i daty jednym wywołaniem, korzystając w tle z openpyxl (albo z pakietu xlsxwriter, jeśli jest zainstalowany), a `read_excel()` czyta arkusz do `DataFrame`. openpyxl bezpośrednio sięgamy, gdy liczy się to, co pandas pomija: formuły, formaty liczb, szerokości kolumn, zablokowane nagłówki, wykresy, kilka arkuszy o różnym układzie. Oba podejścia łączą się w jednym pliku: pandas zapisuje dane, a openpyxl otwiera zapisany skoroszyt i dodaje formatowanie. Formaty starsze niż `.xlsx` — binarne `.xls` — openpyxl nie obsługuje; w praktyce wystarczy zapisać plik ponownie w Excelu.
