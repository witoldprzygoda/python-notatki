# Projekt rozdziału 22 części „Python Zastosowania” — Pliki Office i obrazy

Czwarty rozdział ścieżki Automatyzacja. Branch: `content/zastosowania-22` (z `dev` po rozdziale 21). Realizacja autonomiczna w ramach zbiorczego polecenia autora z 23 IX 2026.

## Decyzje redakcyjne (23 IX 2026)

1. **Zakres:** arkusze Excel biblioteką openpyxl (skoroszyt i arkusz, `append()`, komórki po adresie, formuły wpisywane jako tekst i liczone dopiero przez Excel — `data_only=True` daje `None` w pliku nigdy nieprzeliczonym, formaty liczb i dat, czcionka i wypełnienie nagłówka, szerokości kolumn, zablokowany wiersz nagłówka, autofiltr, odczyt `iter_rows(values_only=True)`, drugi arkusz z podsumowaniem, wykres słupkowy `BarChart`; pandas `to_excel()` z rozdziału 4 jako droga dla całych tabel), dokumenty Word biblioteką python-docx (`Document`, nagłówki, akapity i biegi z pogrubieniem, lista punktowana, tabela ze stylem „Table Grid”, obraz z szerokością w centymetrach, podział strony, właściwości dokumentu, odczyt akapitów i tabel, szablon z polami `{{…}}` i pułapka podziału tekstu na biegi), obrazy biblioteką Pillow (`Image.open`, `size`/`mode`/`format`, `resize`, `thumbnail`, `crop`, `rotate`, `convert("L")`, zapis JPEG z `quality`, `ImageDraw` — figury i tekst z `ImageFont.load_default(size=…)`, znak wodny przez `alpha_composite`, przetwarzanie wsadowe katalogu, wykres słupkowy rysowany `ImageDraw`), narzędzie `raport` (CSV → `.xlsx` z tabelą, formułami i wykresem oraz `.docx` z tabelą podsumowania i obrazem wykresu; `argparse` z rozdziału 20, testy pytest otwierające pliki z powrotem), inne formaty prozą (PowerPoint — python-pptx, PDF — pypdf/reportlab, konwersja LibreOffice `--headless --convert-to`), lista kontrolna. Cztery strony + index. Poza zakresem: `.xls`/`.doc` (stare formaty binarne), makra, style numerowane Worda, EXIF, filtry i przekształcenia geometryczne poza obrotem, matplotlib (rozdział 14 „Python Notatki”) — wykres w dokumencie rysujemy Pillow, żeby nie dodawać zależności.
2. **Biblioteki:** openpyxl 3.1.5 (jak w rozdziale 4), python-docx 1.2.0, Pillow 12.3.0 (jak w rozdziale 16), pytest 9.1.1. Plik wymagań z tymi wersjami. Środowisko `venv-ch22`.
3. **Dane:** `sprzedaz.csv` jako blok (12 wierszy: data, produkt, kategoria, ilość, cena); obrazy generowane skryptem (`ImageDraw`), więc bez pobierania. Obrazy wynikowe (`oryginal.png`, `znak-wodny.png`, `wykres.png`) kopiowane ze stagingu do `docs/zastosowania/22-office-obrazy/img/` i wstawione na strony — to jedyne wyniki, których tekst nie odda. Zrzuty arkusza i dokumentu otwartych w Excelu i Wordzie: `TODO` w `ZRZUTY.md` (decyzja autora, czy potrzebne). Harness: moduły `slupki.py` i `raport.py` oraz `test_raport.py` w `--skip`; rozmiary plików w bajtach nie są wypisywane (zależą od wersji bibliotek), wypisujemy wymiary i porównania.
4. **Fakty sprawdzone 23 IX 2026 (Python 3.14.7):** openpyxl zapisuje formułę jako tekst `=B2*C2` i nie liczy jej; `load_workbook(data_only=True)` zwraca `None` dla formuły w pliku zapisanym przez openpyxl; liczba `149.0` po odczycie wraca jako `int` `149`; `number_format`, `Font(bold=True)`, `PatternFill("solid", fgColor=…)`, `column_dimensions[...].width`, `freeze_panes`, `BarChart` + `Reference` + `set_categories`, `iter_rows(values_only=True)`, `ws.dimensions`; python-docx: `add_heading(level=1)` → styl „Heading 1”, `add_paragraph(style="List Bullet")`, `add_table(rows, cols)` ze stylem „Table Grid”, `add_picture(width=Cm(8))`, `add_page_break()`, `core_properties.author`, odczyt `paragraphs`, `tables`, `inline_shapes`; Pillow: `ImageFont.load_default(size=24)` (od 10.1 wektorowa czcionka wbudowana), `textbbox`, `thumbnail` zmienia obraz w miejscu i zachowuje proporcje, `rotate(90, expand=True)` zamienia wymiary, `convert("L")`, `save(..., quality=85)` dla JPEG wymaga RGB.
5. **Terminy:** „skoroszyt” (ang. *workbook*) i „arkusz” (ang. *worksheet*), „komórka”, „formuła”, „bieg” (ang. *run*) w Wordzie, „miniatura” (ang. *thumbnail*), „znak wodny” (ang. *watermark*), „tryb obrazu” (ang. *mode*), „przetwarzanie wsadowe” (ang. *batch processing*).
6. Odsyłacze wstecz: „Python Notatki” 9 (CSV, `pathlib`), 14 (matplotlib — wzmianka), 16 (pytest); „Python Zastosowania” 4 (pandas `to_excel`/`read_excel`), 16 (Pillow w `PhotoImage`), 20 (narzędzie, `argparse`, testy `main(argv)`), 21 (rekordy z CSV). Zapowiedź: 23 (projekt) — `TODO`.
7. Domknięcia: marker „plikach Office i obrazach” w 21/narzedzie (Dalej) → `22-office-obrazy/index.md`.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i pliki |
|---|---|---|
| `index.md` | Wprowadzenie / „22. Pliki Office i obrazy” | cel; biblioteki; plik wymagań; dane (`sprzedaz.csv`); ---; ## W tym rozdziale (4) |
| `excel.md` | Arkusze Excel | Zapis arkusza (`arkusz.py`); Odczyt arkusza (`odczyt.py`); Podsumowanie i wykres (`wykres.py`); Arkusz a pandas |
| `word.md` | Dokumenty Word | Budowa dokumentu (`dokument.py`); Odczyt i szablon (`szablon.py`); Format i konwersja |
| `obrazy.md` | Obrazy | Otwieranie i przekształcenia (`przeksztalcenia.py`, obraz `oryginal.png`); Rysowanie i znak wodny (`rysowanie.py`, obraz `znak-wodny.png`); Wykres słupkowy (`slupki.py`, `wykres-slupkowy.py`, obraz `wykres.png`); Przetwarzanie wsadowe (`miniatury.py`) |
| `raport.md` | Raport z danych | Narzędzie raport (`raport.py`, `uzycie-raport.py`); Testy (`test_raport.py`, pytest); Inne formaty; Lista kontrolna; Dalej (TODO 23) |

Szacunek: 650–800 linii; 3 obrazy generowane; 2 zrzuty do decyzji autora.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 21)

```yaml
      - 22. Pliki Office i obrazy:
          - Wprowadzenie: zastosowania/22-office-obrazy/index.md
          - Arkusze Excel: zastosowania/22-office-obrazy/excel.md
          - Dokumenty Word: zastosowania/22-office-obrazy/word.md
          - Obrazy: zastosowania/22-office-obrazy/obrazy.md
          - Raport z danych: zastosowania/22-office-obrazy/raport.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `raport.md` | projekt narzędzia automatyzującego | rozdział 23 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/21-scraping/narzedzie.md` (marker „Dalej”) | `22-office-obrazy/index.md` |

## CONTENT HANDOFF

Brak wykładu źródłowego; rozdział rozszerza `to_excel()` z rozdziału 4 i `PhotoImage` z rozdziału 16 o bezpośrednie użycie bibliotek openpyxl, python-docx i Pillow.

## Listy kontrolne

- Przed commitem: staging z bloków; `refresh_outputs.py`; `verify_page.py` dwa przebiegi z `--skip`; pytest w stagingu; obrazy skopiowane do `img/`; oba buildy `--strict`; cudzysłowy; kolokwializmy; recenzje z weryfikacją uwag; wpisy w `ZRZUTY.md`.
- Po commicie: domknięcie w 21/narzedzie, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć.
