# Projekt rozdziału 5 części „Python Zastosowania” — pandas — analiza

Piąty rozdział ścieżki Dane; drugi o pandas (rozdział 4: tabele). Branch: `content/zastosowania-05` (z `dev` po `2c5d3a9`). Realizacja autonomiczna na polecenie autora z 14 IX 2026.

## Decyzje redakcyjne (14 IX 2026)

1. **Zakres:** grupowanie (`groupby`, `agg` z nazwami, `MultiIndex`, `transform`, `filter`, `apply`), tabele przestawne i kształt (`pivot_table`, `crosstab`, `melt`/`pivot`, `stack`/`unstack`, tabela do raportu), łączenie (`merge` — rodzaje złączeń, klucze, sufiksy, `validate`, pułapki; `concat` z wielu plików; `join`), szeregi czasowe (`DatetimeIndex`, `date_range`, `resample`, `rolling`/`expanding`/`ewm`, `shift`/`diff`/`pct_change`, luki, `Grouper`, strefy), wydajność i potok (pomiary na 2 mln wierszy, kategorie, agregacje wbudowane, pamięć i Parquet, `pipe()`, moduł z testem). Poza zakresem: seaborn, statystyka wnioskowania, SQL (rozdział 13). Rozdział 6 (projekt raportu) — zapowiedź `TODO`.
2. **Dane:** `zamowienia-2025.csv` — 240 zamówień I–VI 2025 generowanych skryptem `generuj.py` (ziarno 42, rozkład beta dat — więcej zamówień w kolejnych miesiącach; 6 klientów, 4 kategorie, rabaty); skrypt w pierwszym podrozdziale, plik także w `dane/`. `klienci.csv` (7 klientów, miasto, segment; jeden bez zamówień) jako blok. Harness: `--data=docs/zastosowania/05-pandas-analiza/dane`; maska czasów `[\d.]+ (s|ms)` na stronie o wydajności.
3. **Środowisko:** pandas 3.0.5, NumPy 2.5.3, Matplotlib 3.11.2, pyarrow 25.0.1, tabulate 0.10.0 (`to_markdown()`), pytest 9.1.1 (test modułu — wydruk z rzeczywistego uruchomienia jako `.text .no-copy`).
4. **Fakty sprawdzone 14 IX 2026:** `groupby` na kolumnie `category` domyślnie `observed=True`; `agg` ze słownikiem list → kolumny `MultiIndex` (spłaszczanie `"_".join`); `merge(validate="many_to_one")` → `MergeError`; klucze `int64` i `str` → `ValueError`; `concat` z `keys=` → `MultiIndex`; `resample("W")` kończy tygodnie w niedzielę (`W-SUN`), `"ME"`/`"MS"` koniec/początek miesiąca; `rolling("7D")` okno czasowe; `Series.first()` usunięte; `tz_localize("Europe/Warsaw")` obsługuje zmianę czasu (30 III 2025); 2 mln wierszy: `groupby` po `str` 0,06 s, po `category` 0,03 s, pamięć 32 MB → 2 MB; `agg("mean")` 0,04 s, `agg(lambda)` 0,13 s; `map(lambda)` 0,29 s vs wektorowo 5 ms; Parquet zapis 0,3 s / CSV 2,6 s, odczyt 0,1 / 0,8 s, rozmiar 20 / 67 MB; `downcast="integer"` → `int16`.
5. **Terminy:** „grupowanie”, „agregacja”, „podział–zastosowanie–złączenie” (ang. *split-apply-combine*), „indeks wielopoziomowy” (ang. *MultiIndex*), „tabela przestawna” (ang. *pivot table*), „postać długa i szeroka” (ang. *long/wide*), „złączenie” (ang. *join*) lewe/prawe/wewnętrzne/zewnętrzne, „klucz”, „zmiana częstotliwości” (ang. *resampling*), „okno kroczące” (ang. *rolling window*), „okno rozszerzające” (ang. *expanding*), „wygładzanie wykładnicze” (ang. *exponentially weighted*), „potok” (ang. *pipeline*).
6. Odsyłacze wstecz: „Python Notatki” 5 (słowniki, `Counter`), 7 (moduły), 13 (pomiary), 16 (pytest); „Python Zastosowania” 1 (projekt, z notatnika do modułu), 2 (średnia ruchoma, `unique` z licznościami, `memmap`), 3 (szeregi czasowe w Matplotlib, `fill_between`), 4 (wszystkie strony).
7. Domknięcia: 3 markery „analizie w pandas” (02/statystyka:96 → `grupowanie.md`; 04/wczytywanie → `grupowanie.md`; 04/przeksztalcenia → `index.md`).

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty |
|---|---|---|
| `index.md` | Wprowadzenie / „5. pandas — analiza” | cel; dane; wersje; ---; ## W tym rozdziale (5) |
| `grupowanie.md` | Grupowanie | Dane rozdziału (`generuj.py`, `klienci.csv`); Podział, zastosowanie, złączenie (`grupowanie.py`); Agregacje — `agg()` (`agregacje.py`); Grupowanie po kilku kolumnach — `MultiIndex` (`wiele-kluczy.py`); `transform()` i `filter()` (`transform.py`); `apply()` na grupach (`apply-grupy.py`) |
| `przestawianie.md` | Tabele przestawne i kształt danych | `pivot_table()` (`pivot.py`); `crosstab()` (`crosstab.py`); Postać długa i szeroka — `melt()` i `pivot()` (`melt.py`); `stack()` i `unstack()` (`stack.py`); Tabela do raportu (`tabela-raport.py`) |
| `laczenie.md` | Łączenie tabel | `merge()` — klucz i rodzaje złączeń (`merge.py`); Klucze, sufiksy i walidacja (`merge-klucze.py`); Pułapki kluczy (`merge-pulapki.py`); `concat()` (`concat.py`); `join()` i wyrównanie serii (`join.py`); Analiza po złączeniu (`po-zlaczeniu.py`) |
| `szeregi-czasowe.md` | Szeregi czasowe | Indeks czasowy (`indeks-czasowy.py`); Zmiana częstotliwości — `resample()` (`resample.py`); Okna — `rolling()`, `expanding()`, `ewm()` (`okna.py`; `okna.png`); Przesunięcia i zmiany (`zmiany.py`); Luki, kalendarz i strefy czasowe (`luki-strefy.py`) |
| `wydajnosc-i-potok.md` | Wydajność i potok analizy | Pomiar na dużej tabeli (`duza-tabela.py`); Agregacje wbudowane zamiast własnych (`agregacje-koszt.py`); Pamięć i format pośredni (`pamiec.py`); Potok — łańcuch metod i `pipe()` (`potok.py`); Z notatnika do modułu i testu (`analiza.py`, `test_analiza.py`, wydruk pytest); Dalej: projekt raportu (TODO 6) |

Szacunek: 1000–1150 linii; 1 wykres.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 4)

```yaml
      - 5. pandas — analiza:
          - Wprowadzenie: zastosowania/05-pandas-analiza/index.md
          - Grupowanie: zastosowania/05-pandas-analiza/grupowanie.md
          - Tabele przestawne i kształt danych: zastosowania/05-pandas-analiza/przestawianie.md
          - Łączenie tabel: zastosowania/05-pandas-analiza/laczenie.md
          - Szeregi czasowe: zastosowania/05-pandas-analiza/szeregi-czasowe.md
          - Wydajność i potok analizy: zastosowania/05-pandas-analiza/wydajnosc-i-potok.md
```

Strona główna i `docs/zastosowania/index.md`: „5. [pandas — analiza](…/05-pandas-analiza/index.md) — grupowanie, tabele przestawne, łączenie tabel, szeregi czasowe, wydajność i potok”.

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `wydajnosc-i-potok.md` | projekt: raport z danych | rozdział 6 |
| `laczenie.md` | złączenia w SQL | rozdział 13 (wzmianka bez TODO) |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/02-numpy/statystyka-i-porzadkowanie.md:96` | `05-pandas-analiza/grupowanie.md` |
| `zastosowania/04-pandas-tabele/wczytywanie-i-zapis.md` | `05-pandas-analiza/grupowanie.md` |
| `zastosowania/04-pandas-tabele/przeksztalcenia.md` | `05-pandas-analiza/index.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/`; druga połowa rozdziału 17 z `PLAN_ROZWOJU.md` (grupowanie i łączenie) rozszerzona o szeregi czasowe i wydajność.

## Listy kontrolne

- Przed commitem: `dane/zamowienia-2025.csv` z generatora, `dane/klienci.csv` z bloku; harness z `--data=` i maską czasów; `refresh_outputs.py`; `make_figures.py --img= --data=`; oba buildy `--strict`; kotwice; cudzysłowy; kolokwializmy; trzy recenzje.
- Po commicie: domknięcia (3 markery), status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
