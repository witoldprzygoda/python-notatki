# Plan rozwoju — „Python Zastosowania”

Stan na 13 IX 2026. Część „Python Zastosowania” jest kontynuacją „Python Notatki” (część „Python Notatki”, rozdziały 1–16, ukończona) i obejmuje biblioteki Pythona w zastosowaniach. Decyzje autora: tytuł „Python Zastosowania” (13 IX 2026), ten sam serwis i repozytorium, w lewym panelu osobna grupa „Python Zastosowania” pod grupą „Python Notatki” (funkcja `navigation.sections`), zakres według propozycji z 13 IX 2026 z osobną ścieżką uczenia maszynowego.

## 0. Zasady

1. **Ścieżki.** Część składa się ze **ścieżek** — niezależnych, skończonych samouczków (4–6 rozdziałów), z których każda kończy się projektem spinającym jej biblioteki. Ścieżki są numerowane ciągiem rozdziałów części (1, 2, 3, …), a przynależność do ścieżki podaje strona główna i wprowadzenie tomu.
2. **Skończoność.** Jedna biblioteka na rozdział i jedno narzędzie na zadanie (FastAPI albo Flask, nie oba). Rozszerzanie wyłącznie przez dopisanie rozdziału na końcu ścieżki lub nowej ścieżki; istniejące rozdziały nie rosną.
3. **Wymagania wstępne.** Każda ścieżka zakłada część „Python Notatki”; ścieżka uczenia maszynowego zakłada też ścieżkę danych. Wprowadzenie każdego rozdziału wymienia rozdziały części „Python Notatki”, na których buduje.
4. **Konwencje części „Python Notatki” obowiązują** (`CLAUDE.md`, `DEVELOPMENT_WORKFLOW.md`): rejestr, bloki kodu, harness, trzy recenzje, zapowiedzi w przód z `<!-- TODO: link po powstaniu rozdziału o … -->`, bez odwołań do materiałów z zajęć.
5. **Biblioteki i wersje.** Każdy rozdział podaje wersje „w chwili pisania” i plik wymagań z przypiętymi wersjami; weryfikacja w osobnym środowisku wirtualnym z tymi pakietami (Python 3.14). Wykresy generowane z listingów; dane przykładowe osadzone w tekście jako bloki plików lub jawnie oznaczone jako dane przykładowe.
6. **Notatniki.** Komórki notatnika zapisujemy jako bloki ```python title="nazwa.ipynb — komórka N"``` z wynikiem w bloku `{ .text .no-copy }`; weryfikuje je `scripts/verify_cells.py` (komórki w kolejności w jądrze Jupyter przez `nbclient`; opcje `--refresh`, `--img`, `--cwd`, `--mask`). `scripts/verify_page.py` pomija bloki z `.ipynb` w tytule.
7. **Układ katalogów:** `docs/zastosowania/<NN>-<slug>/`, obrazy w `img/` rozdziału; strona `docs/zastosowania/index.md` jest wprowadzeniem części.

## 1. Ścieżki i rozdziały

| Nr | Rozdział | Ścieżka | Katalog | Podstron | Status |
|---|---|---|---|---|---|
| 1 | Jupyter i warsztat danych | Dane | `zastosowania/01-jupyter/` | 4 | ukończony — 13 IX 2026 (`plans/z01-jupyter.md`; wprowadzenie części + index + 4 strony, 585 linii; trzy recenzje naniesione; zrzuty w `ZRZUTY.md` 14–15) |
| 2 | NumPy w praktyce | Dane | `zastosowania/02-numpy/` | 5 | ukończony — 13 IX 2026 (`plans/z02-numpy.md`; index + 5 stron, 860 linii; 25 skryptów, 5 wykresów; trzy recenzje naniesione; zapowiedź z rozdziału 1 domknięta) |
| 3 | Matplotlib w praktyce | Dane | `zastosowania/03-matplotlib/` | 5 | ukończony — 14 IX 2026 (`plans/z03-matplotlib.md`; index + 5 stron, ok. 950 linii; 24 skrypty, 20 wykresów; trzy recenzje naniesione; zapowiedź z rozdziału 2 domknięta) |
| 4 | pandas — tabele | Dane | `zastosowania/04-pandas-tabele/` | 5 | ukończony — 14 IX 2026 (`plans/z04-pandas-tabele.md`; index + 5 stron, ok. 970 linii; 26 skryptów, 1 wykres, pliki `dane/`; trzy recenzje naniesione; 7 zapowiedzi domkniętych, 1 przemianowana dla rozdziału 5) |
| 5 | pandas — analiza | Dane | `zastosowania/05-pandas-analiza/` | 5 | ukończony — 14 IX 2026 (`plans/z05-pandas-analiza.md`; index + 5 stron, ok. 1060 linii; 27 skryptów, 1 wykres, pliki `dane/` z generatora; trzy recenzje naniesione; 3 zapowiedzi domknięte) |
| 6 | Projekt: raport z danych | Dane | `zastosowania/06-projekt-dane/` | 3 | ukończony — 14 IX 2026 (`plans/z06-projekt-dane.md`; index + 3 strony, ok. 650 linii; projekt `raport-sprzedazy` z 13 plików, 5 testów, 3 rysunki; trzy recenzje naniesione; zapowiedź z rozdziału 5 domknięta). **Ścieżka Dane ukończona.** |
| 7 | Uczenie maszynowe — pojęcia i warsztat | Uczenie maszynowe | `zastosowania/07-ml-pojecia/` | 4 | ukończony — 14 IX 2026 (`plans/z07-ml-pojecia.md`; index + 4 strony, ok. 660 linii; 18 skryptów, 5 wykresów; trzy recenzje naniesione; zapowiedzi z rozdziału 6 i rozdziału 14 „Python Notatki” domknięte) |
| 8 | Klasyfikacja | Uczenie maszynowe | `zastosowania/08-klasyfikacja/` | 4 | ukończony — 14 IX 2026 (`plans/z08-klasyfikacja.md`; index + 4 strony, ok. 930 linii; 22 skrypty, 11 wykresów; trzy recenzje naniesione; 2 zapowiedzi z rozdziału 7 domknięte) |
| 9 | Regresja i przygotowanie danych | Uczenie maszynowe | `zastosowania/09-regresja/` | 4 | ukończony — 14 IX 2026 (`plans/z09-regresja.md`; index + 4 strony, ok. 900 linii; 20 skryptów, 7 wykresów, dane `dane/mieszkania.csv` z generatora; cztery recenzje z weryfikacją uwag naniesione, model końcowy liniowy na logarytmach ceny i powierzchni; 4 zapowiedzi z rozdziałów 7–8 domknięte) |
| 10 | Uczenie bez nadzoru | Uczenie maszynowe | `zastosowania/10-bez-nadzoru/` | 3 | ukończony — 16 IX 2026 (`plans/z10-bez-nadzoru.md`; index + 3 strony, ok. 570 linii; 13 skryptów, 8 wykresów; dane z rozdziału 9 i zbiory wbudowane; cztery recenzje z weryfikacją uwag naniesione; 5 zapowiedzi z rozdziałów 2, 7, 8 i 9 domkniętych) |
| 11 | PyTorch — tensory i sieć neuronowa | Uczenie maszynowe | `zastosowania/11-pytorch/` | 5 | ukończony — 16 IX 2026 (`plans/z11-pytorch.md`; index + 5 stron, ok. 940 linii; 19 skryptów, 7 wykresów; `pliki/` z modułem `trening.py` i kopią `mieszkania.csv`; torch 2.14.0 w pliku wymagań; cztery recenzje z weryfikacją uwag naniesione; 2 zapowiedzi z rozdziałów 7 i 10 domknięte) |
| 12 | Projekt: od danych do modelu | Uczenie maszynowe | `zastosowania/12-projekt-ml/` | 3 | ukończony — 19 IX 2026 (`plans/z12-projekt-ml.md`; index + 3 strony, ok. 780 linii; projekt `rezygnacja-klientow` z 16 plików, 7 testów, 2 rysunki; dane `dane/surowe/klienci.csv` i `dane/nowi_klienci.csv` z generatora; recenzje stron 1 i 3 naniesione, strona 2 i kontrola faktów przejrzane samodzielnie — dwie recenzje przerwał limit API; zapowiedź z rozdziału 11 domknięta). **Ścieżka Uczenie maszynowe ukończona.** |
| 13 | Bazy danych — `sqlite3` i SQLAlchemy | Aplikacje | `zastosowania/13-bazy-danych/` | 5 | ukończony — 19 IX 2026 (`plans/z13-bazy-danych.md`; index + 5 stron, ok. 1130 linii; 21 skryptów i 6 modułów/testów, bez wykresów; dane wpisane w skrypty; SQLAlchemy 2.0.54 w pliku wymagań; cztery recenzje z własną weryfikacją uwag naniesione; zapowiedź z rozdziału 12 domknięta) |
| 14 | HTTP i API | Aplikacje | `zastosowania/14-http-api/` | 4 | w realizacji — `plans/z14-http-api.md` |
| 15 | FastAPI | Aplikacje | `zastosowania/15-fastapi/` | 5 | zaplanowany |
| 16 | Interfejs graficzny tkinter | Aplikacje | `zastosowania/16-tkinter/` | 7 | zaplanowany (projekt w `PLAN_ROZWOJU.md`, sekcja 18) |
| 17 | Pakowanie i dystrybucja | Aplikacje | `zastosowania/17-pakowanie/` | 4 | zaplanowany |
| 18 | Projekt: aplikacja z bazą, API i oknem | Aplikacje | `zastosowania/18-projekt-aplikacja/` | 3 | zaplanowany |
| 19 | Wyrażenia regularne | Automatyzacja | `zastosowania/19-re/` | 4 | zaplanowany |
| 20 | Narzędzia wiersza poleceń | Automatyzacja | `zastosowania/20-cli/` | 4 | zaplanowany |
| 21 | Pobieranie i parsowanie stron | Automatyzacja | `zastosowania/21-scraping/` | 4 | zaplanowany |
| 22 | Pliki Office i obrazy | Automatyzacja | `zastosowania/22-office-obrazy/` | 4 | zaplanowany |
| 23 | Projekt: narzędzie automatyzujące | Automatyzacja | `zastosowania/23-projekt-automatyzacja/` | 3 | zaplanowany |

Kolejność realizacji: ścieżka Dane (1–6, ukończona) → Uczenie maszynowe (7–12, ukończona) → Aplikacje (13–18) → Automatyzacja (19–23). Projekty rozdziałów powstają w `plans/zNN-<slug>.md` bezpośrednio przed realizacją; rozdział 17 (pandas) i 18 (tkinter) z `PLAN_ROZWOJU.md` są punktem wyjścia dla rozdziałów 4–5 i 16.

## 2. Zapowiedzi z części „Python Notatki” do domknięcia

| Plik części „Python Notatki” | Zapowiedź | Rozdział części „Python Zastosowania” |
|---|---|---|
| `09-wejscie-wyjscie/csv-i-json.md:117`, `14-numpy-matplotlib/ndarray.md:276` | pandas — tabele z nazwanymi kolumnami | 4 — domknięte 14 IX 2026 |
| `14-numpy-matplotlib/przyklady-i-rozszerzenia.md:170` | SciPy i scikit-learn | 7 (scikit-learn); SciPy — wzmianka w 2 — domknięte 14 IX 2026 |
| `06-funkcje/funkcje-jako-obiekty.md:67`, `12-oop-zaawansowane/wzorce-projektowe.md:234`, `15-wspolbieznosc/synchronizacja.md:235` | tkinter | 16 |

## 3. Pytania otwarte

1. Zakładki w górnym pasku (`navigation.tabs`) jako alternatywa dla grup w lewym panelu — do decyzji autora po obejrzeniu układu.
2. Osobna zakładka „Ściągawki” (tabele odniesienia) po ukończeniu ścieżek.
3. Zadania do stron przez istniejącą infrastrukturę aktywności — które rozdziały części „Python Zastosowania” mają je dostać.
