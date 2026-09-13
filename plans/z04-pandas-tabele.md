# Projekt rozdziału 4 części „Python Zastosowania” — pandas — tabele

Czwarty rozdział ścieżki Dane według `PLAN_ZASTOSOWANIA.md`; pierwszy z dwóch o pandas (rozdział 5: analiza — grupowanie, łączenie, przestawianie, szeregi czasowe). Punkt wyjścia: projekt rozdziału 17 w `PLAN_ROZWOJU.md`. Branch: `content/zastosowania-04` (z `dev` po `cd57920`). Realizacja autonomiczna na polecenie autora z 14 IX 2026.

## Decyzje redakcyjne (14 IX 2026)

1. **Zakres (tabele):** `Series` i `DataFrame`, indeks; wczytywanie i zapis (CSV z polskimi separatorami, Excel, JSON, Parquet, porcje); selekcja (`[]`, `loc`, `iloc`, maski, `query()`, sortowanie) i przypisywanie w modelu kopiowania przy zapisie; typy, daty, braki, duplikaty, kategorie; przekształcenia kolumn (`.str`, `map`/`replace`/`apply`, `cut`/`qcut`) i wykres z tabeli. Poza zakresem (rozdział 5): `groupby`, `merge`/`concat`, `pivot_table`, `resample`/`rolling`, `MultiIndex` — zapowiedzi `TODO`. Jednowierszowy `groupby` na stronie 2 jako zapowiedź (domyka obietnicę rozdziału 1 „ta sama analiza w kilku wierszach”).
2. **Środowisko:** Python 3.14.7, pandas 3.0.5 (Copy-on-Write zawsze włączone, domyślny typ `str`, `datetime64[us]` z `read_csv`), NumPy 2.5.3, Matplotlib 3.11.2, openpyxl 3.1.5, pyarrow 25.0.1; weryfikacja w `venv-ch8` z `MPLBACKEND=Agg`; wynik `map-apply.py` z maską czasów.
3. **Dane:** wspólny plik `zamowienia.csv` (10 wierszy; separator `;`, przecinek dziesiętny, brak w `miasto`, `ilosc`, `rabat`; napis `brak`; zduplikowany wiersz) osadzony jako blok `text title=`; `pomiary.csv` z rozdziału 1 (24 wiersze) na stronach 2 i 5. Pliki Excel/JSON/Parquet powstają w skryptach.
4. **Fakty pandas 3 sprawdzone 14 IX 2026:** `dtypes` pokazuje `str`; `info()` wypisuje `str`; przypisanie łańcuchowe `df["a"][0] = x` daje `ChainedAssignmentError` (ostrzeżenie) i nie zmienia danych; `Series` wzięta z `DataFrame` po modyfikacji nie zmienia ramki; przefiltrowana ramka jest niezależna (brak `SettingWithCopyWarning`); `option mode.copy_on_write` przestarzała; `fillna(method=)` usunięte — `ffill()`; `describe()` obejmuje kolumnę dat; `read_json` nie rozpoznaje kolumny `data` jako daty; `Int64` z `<NA>`; `bool(pd.NA)` → `TypeError`; 1 mln napisów 17 MB → `category` 1 MB; szerokość wydruku 80 znaków — ramki do 8 kolumn.
5. **Terminy:** „ramka danych” (ang. *DataFrame*) — dalej `DataFrame`; „seria” (`Series`); „indeks”, „etykieta”; „maska logiczna”; „kopiowanie przy zapisie” (ang. *copy-on-write*); „akcesor” (ang. *accessor*) `.str`, `.dt`, `.cat`; „porcja” (ang. *chunk*); „typ kategorialny”; „wartość brakująca”.
6. Odsyłacze wstecz: „Python Notatki” 3 (typy), 5 (słowniki, `Counter`), 7 (`csv`… nie — 9), 8 (ostrzeżenia, menedżer kontekstu), 9 (`csv`, `json`, kodowania, `pathlib`), 13 (pomiary czasu), 14 (NumPy, `loadtxt`, wykresy); „Python Zastosowania” 1 (projekt, `genfromtxt`, `pomiary.csv`), 2 (maski, `nan`, `unique`, `histogram`, `memmap`), 3 (`ax=`, style, `bar_label`).
7. Domknięcia: 8 markerów „rozdziału o pandas” (09/csv-i-json, 14/ndarray, 01/pierwsza-analiza ×2, 02/statystyka ×2, 02/wydajnosc, 03/zapis); marker o grupowaniu (02/statystyka:96) zostaje dla rozdziału 5 z przemianowanym tematem „analizie w pandas”.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty |
|---|---|---|
| `index.md` | Wprowadzenie / „4. pandas — tabele” | co to pandas i dlaczego po NumPy; wymagania (`requirements.txt` z pandas, openpyxl, pyarrow); wersje; ---; ## W tym rozdziale (5) |
| `series-i-dataframe.md` | Series i DataFrame | Series — dane z etykietami (`series.py`); DataFrame — tabela kolumn (`dataframe.py`); Indeks — etykiety wierszy (`indeks.py`); pandas a NumPy (`pandas-numpy.py`); Wyświetlanie (`wyswietlanie.py`) |
| `wczytywanie-i-zapis.md` | Wczytywanie i zapis | Plik CSV — `read_csv()` (`zamowienia.csv`, `wczytanie.py`); Pierwsze oględziny (`ogledziny.py`); Analiza z rozdziału 1 w pandas (`pomiary.csv`, `pomiary-pandas.py`); Zapis — `to_csv()` (`zapis.py`); Excel, JSON i Parquet (`formaty.py`); Duże pliki — porcje i wybór kolumn (`porcje.py`) |
| `selekcja.md` | Selekcja i filtrowanie | Kolumny i wiersze — `[]`, `loc` i `iloc` (`loc-iloc.py`); Maski logiczne (`maski.py`); Zapytania — `query()` (`query.py`); Sortowanie i wartości skrajne (`sortowanie.py`); Przypisywanie i kopiowanie przy zapisie (`cow.py`) |
| `typy-i-braki.md` | Typy, braki i czyszczenie | Typy kolumn (`typy.py`); Daty — `to_datetime()` i `.dt` (`daty.py`); Wartości brakujące (`braki.py`); Duplikaty i niespójne napisy (`duplikaty.py`); Typ kategorialny (`kategorie.py`) |
| `przeksztalcenia.md` | Przekształcenia i wykres z tabeli | Nowe kolumny (`nowe-kolumny.py`); Napisy — akcesor `.str` (`napisy.py`); `map()`, `replace()` i `apply()` (`map-apply.py`, maska czasów); Przedziały — `cut()` i `qcut()` (`przedzialy.py`); Wykres z tabeli — `plot()` (`wykres.py`; `wykres.png`); Dalej: analiza (TODO rozdział 5) |

Szacunek: 950–1100 linii; 1 wykres.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 3)

```yaml
      - 4. pandas — tabele:
          - Wprowadzenie: zastosowania/04-pandas-tabele/index.md
          - Series i DataFrame: zastosowania/04-pandas-tabele/series-i-dataframe.md
          - Wczytywanie i zapis: zastosowania/04-pandas-tabele/wczytywanie-i-zapis.md
          - Selekcja i filtrowanie: zastosowania/04-pandas-tabele/selekcja.md
          - Typy, braki i czyszczenie: zastosowania/04-pandas-tabele/typy-i-braki.md
          - Przekształcenia i wykres z tabeli: zastosowania/04-pandas-tabele/przeksztalcenia.md
```

Strona główna i `docs/zastosowania/index.md`: „4. [pandas — tabele](…/04-pandas-tabele/index.md) — Series i DataFrame, wczytywanie i zapis, selekcja, typy i braki, przekształcenia”.

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `wczytywanie-i-zapis.md` | grupowanie (`groupby`) | rozdział 5 |
| `przeksztalcenia.md` | grupowanie, łączenie tabel, przestawianie, szeregi czasowe | rozdział 5 |
| `napisy.py` — wzorce | wyrażenia regularne | rozdział 19 (wzmianka bez TODO) |

## Domknięcia

| Plik | Cel |
|---|---|
| `09-wejscie-wyjscie/csv-i-json.md:117` | `04-pandas-tabele/index.md` |
| `14-numpy-matplotlib/ndarray.md:276` | `04-pandas-tabele/index.md` |
| `zastosowania/01-jupyter/pierwsza-analiza.md:67` | `04-pandas-tabele/typy-i-braki.md` |
| `zastosowania/01-jupyter/pierwsza-analiza.md:170` | `04-pandas-tabele/wczytywanie-i-zapis.md` |
| `zastosowania/02-numpy/statystyka-i-porzadkowanie.md:96` | zostaje (rozdział 5) — marker „analizie w pandas” |
| `zastosowania/02-numpy/statystyka-i-porzadkowanie.md:151` | `04-pandas-tabele/typy-i-braki.md` |
| `zastosowania/02-numpy/wydajnosc-i-pamiec.md:139` | `04-pandas-tabele/wczytywanie-i-zapis.md` |
| `zastosowania/03-matplotlib/zapis-i-raport.md:230` | `04-pandas-tabele/przeksztalcenia.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/`; rozdział 17 z `PLAN_ROZWOJU.md` rozdzielony na rozdziały 4 i 5 tej części.

## Listy kontrolne

- Przed commitem: harness (`--mask="[\d.,]+ (s|ms)"` dla `przeksztalcenia.md`), `refresh_outputs.py`, `make_figures.py --img=`, oba buildy `--strict`, kotwice i obrazy, cudzysłowy, kolokwializmy, trzy recenzje.
- Po commicie: domknięcia (8 markerów), status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
