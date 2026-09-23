# Założenia i architektura

Projekt zaczynamy od wymagań i podziału na moduły; kod piszemy później i jest krótszy, gdy każdy moduł ma jedno zadanie.

## Wymagania

1. **Pomiar**: `monitor-cen pobierz ADRES` pobiera listę produktów ze wszystkich stron sklepu, uprzejmie wobec serwera (`robots.txt`, odstęp, identyfikacja), i zapisuje pomiar — chwilę, SKU (ang. *stock keeping unit* — identyfikator produktu w sklepie), nazwę i cenę każdego produktu — w bazie SQLite; produkt bez ceny zapisuje z ceną pustą, rekord o niepoprawnym SKU pomija z ostrzeżeniem.
2. **Historia**: `monitor-cen historia SKU` wypisuje ceny produktu z kolejnych pomiarów.
3. **Raport**: `monitor-cen raport` porównuje dwa ostatnie pomiary i zapisuje arkusz Excel (ceny obu pomiarów, arkusz zmian, wykres cen bieżących) oraz dokument Word (podsumowanie i tabela zmian); przy jednym pomiarze zgłasza błąd.
4. **Uruchamianie**: bez terminala — z harmonogramu zadań; komunikaty do dziennika w pliku; kody wyjścia `0`, `1` (błąd serwera, zakaz, brak danych), `2` (błąd użycia).
5. **Testy**: moduły testowane bez sieci, narzędzie — na serwerze testowym z rozdziału 21.

## Przepływ danych

```{ .text .no-copy }
strony sklepu (HTML)
      │  pobieranie.Pobieracz, strony()        rozdział 21
      ▼
drzewa BeautifulSoup
      │  rekordy.lista_produktow(), rekord_produktu()
      ▼
rekordy {sku, nazwa, cena}
      │  analiza.poprawne_sku()                 rozdział 19
      ▼
historia.zapisz_pomiar()  ──►  monitor.sqlite   rozdział 13
      │  historia.pomiar() × 2
      ▼
analiza.porownaj()  ──►  zmiany, nowe, brakujące
      │  raport.zapisz_arkusz(), zapisz_dokument()   rozdział 22
      ▼
monitor-cen.xlsx, monitor-cen.docx
```

Każda strzałka to wywołanie funkcji z jednego modułu, a dane między modułami są zwykłymi słownikami i listami — dzięki temu każdy moduł da się przetestować osobno, a wymiana sklepu na inny dotyczy tylko modułu rekordów i selektora odsyłacza „dalej” w `strony()`.

## Układ pakietu

```{ .text .no-copy }
monitor-cen/
├── pyproject.toml
├── requirements.txt          środowisko programisty
├── monitor/
│   ├── __init__.py
│   ├── __main__.py           python -m monitor
│   ├── cli.py                podpolecenia pobierz, raport, historia
│   ├── pobieranie.py         z rozdziału 21: Pobieracz, strony()
│   ├── rekordy.py            z rozdziału 21: lista_produktow(), rekord_produktu()
│   ├── historia.py           baza SQLite z pomiarami
│   ├── analiza.py            porównanie pomiarów, sprawdzenie SKU
│   └── raport.py             arkusz Excel i dokument Word
├── tests/
│   └── test_monitor.py
├── zbuduj_sklep.py           z rozdziału 21: strona testowa
├── sklep_serwer.py           z rozdziału 21: lokalny serwer
└── symuluj_zmiane.py         zmiana cen między pomiarami
```

Narzędzie jest pakietem `monitor` z punktem wejścia w `cli.py`, jak w rozdziale 17; skrypty poza pakietem służą tylko przebiegowi i testom — w prawdziwym wdrożeniu sklep jest w sieci, a ich miejsce zajmuje adres.

## Pliki z rozdziału 21

Cztery pliki kopiujemy bez zmian: `pobieranie.py` i `rekordy.py` do katalogu `monitor/`, `zbuduj_sklep.py` i `sklep_serwer.py` do katalogu projektu. Moduł pobierania importuje tylko biblioteki, więc działa w pakiecie pod nową ścieżką `monitor.pobieranie`; moduł rekordów zna układ strony testowej, a generator `strony()` w module pobierania — jej odsyłacz do następnej strony (`a.dalej`); dla innego sklepu piszemy odpowiednik modułu rekordów z tymi samymi dwiema funkcjami i dostosowujemy ten selektor. Skrypt `zbuduj_sklep.py` uruchamiamy raz, żeby powstał katalog `sklep/`.

## Konfiguracja pakietu

```toml title="pyproject.toml"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "monitor-cen"
version = "0.1.0"
description = "Monitor cen sklepu: pomiary, historia i raporty"
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.28,<1",
    "beautifulsoup4>=4.15,<5",
    "openpyxl>=3.1,<4",
    "python-docx>=1.2,<2",
]

[project.scripts]
monitor-cen = "monitor.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["monitor"]

[tool.pytest.ini_options]
pythonpath = ["."]
```

Zależności to tylko biblioteki, których używa pakiet, zapisane jako zakresy według rozdziału 17 — dokładne wersje i pytest zostają w pliku wymagań środowiska programisty. Nazwa pakietu (`monitor`) różni się od nazwy projektu (`monitor-cen`), więc Hatchling nie odnajdzie go sam i dostaje jego nazwę wprost; `[project.scripts]` tworzy polecenie `monitor-cen`, a `__main__.py` dodatkowo `python -m monitor`.
