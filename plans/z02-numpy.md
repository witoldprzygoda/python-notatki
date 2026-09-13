# Projekt rozdziału 2 części „Python Zastosowania” — NumPy w praktyce

Drugi rozdział ścieżki Dane według `PLAN_ZASTOSOWANIA.md`. Branch: `content/zastosowania-02` (z `dev` po `95748bf`). Realizacja autonomiczna na polecenie autora z 13 IX 2026.

## Decyzje redakcyjne (13 IX 2026)

1. **Zakres:** NumPy poza rozdziałem 14 „Python Notatki” — tablice wielowymiarowe i indeksowanie zaawansowane, statystyka opisowa i porządkowanie danych, algebra liniowa z dopasowaniem, losowość i symulacje, wydajność i pamięć. Bez powtarzania rozdziału 14 (tworzenie, dtype, maski, widok a kopia, ufunc, rozgłaszanie 2D, agregacje z osią, `default_rng`, benchmark) — tylko odsyłacze.
2. **Środowisko odniesienia:** Python 3.14.7, NumPy 2.5.3, Matplotlib 3.11.2 (sprawdzone 13 IX 2026); weryfikacja w `venv-ch8` z `MPLBACKEND=Agg`; skrypty (nie notatniki) — jak w rozdziale 14; wykresy z listingów przez `make_figures.py --img=`.
3. **Dane:** generowane w skryptach z `default_rng(42)` (stacje × dni × zmienne, chmury punktów) albo krótkie tablice wpisane wprost; bez plików zewnętrznych.
4. **Modernizacje NumPy 2.x:** `numpy.polynomial.Polynomial.fit()` zamiast `np.polyfit()`; `np.linalg.lstsq(rcond=None)`; `np.unique(return_inverse=True)`; `Generator.spawn()` (od 1.25) dla niezależnych strumieni; `np.lib.format.open_memmap()` i `np.load(mmap_mode="r")`; `np.vectorize` pokazany jako wygoda, nie przyspieszenie.
5. **Wykresy** (5): `dopasowanie.png`, `obrot.png`, `rozklady.png`, `monte-carlo.png`, `bladzenie.png` — komendy Matplotlib w zakresie rozdziału 14; pełne omówienie wykresów w rozdziale 3 (zapowiedź).
6. **SciPy** jako wzmianki (`scipy.stats`, `scipy.linalg`, `scipy.optimize`) — bez instalacji; scikit-learn i PCA jako zapowiedź ścieżki uczenia maszynowego.
7. Odsyłacze wstecz: „Python Notatki” 3 (float, operatory bitowe), 5 (listy), 6 (funkcje), 9 (pliki), 13 (timeit, Numba), 14 (wszystkie sekcje), 15 (procesy — strumienie losowe); „Python Zastosowania” 1 (notatnik, projekt). Zapowiedzi: rozdział 3 (Matplotlib w praktyce), 4 (pandas), 10 (uczenie bez nadzoru — PCA) — `TODO` po temacie.
8. Terminy: „oś” (ang. *axis*), „kwantyl”, „percentyl”, „histogram”, „metoda najmniejszych kwadratów” (ang. *least squares*), „wektor własny” (ang. *eigenvector*), „symulacja Monte Carlo”, „błądzenie losowe” (ang. *random walk*), „próbkowanie ponowne” (ang. *bootstrap*), „mapowanie pliku w pamięci” (ang. *memory mapping*).

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty |
|---|---|---|
| `index.md` | Wprowadzenie / „2. NumPy w praktyce” | co dokłada do rozdziału 14; wymagania; wersje; ---; ## W tym rozdziale (5) |
| `tablice-wielowymiarowe.md` | Tablice wielowymiarowe | Osie i kształt (`osie.py`: stacje × dni × zmienne, `...`); Nowe osie i rozgłaszanie w trzech wymiarach (`nowe-osie.py`: `None`, `keepdims`, normalizacja); Agregacje wzdłuż wielu osi (`agregacje-3d.py`: `axis=(0, 1)`, `argmax` + `unravel_index`); Łączenie, dzielenie i przestawianie (`ksztalty.py`: `stack`, `concatenate`, `split`, `moveaxis`, `transpose`); Indeksowanie tablicami indeksów (`indeksy.py`: pary indeksów a `np.ix_`, `np.nonzero`, `np.take_along_axis`) |
| `statystyka-i-porzadkowanie.md` | Statystyka i porządkowanie danych | Kwantyle i rozkład (`kwantyle.py`: `median`, `percentile`, `histogram`, `bincount`, `digitize`); Sortowanie tabel (`sortowanie.py`: `argsort` po kolumnie, malejąco, `lexsort`, `argpartition`, `searchsorted`); Wartości unikatowe i zbiory (`unikatowe.py`: `unique` z `return_counts`/`return_inverse`, `isin`, `intersect1d`, `setdiff1d`); Warunki i przekształcenia (`warunki.py`: `where`, `select`, `clip`, `diff`, `cumsum`); Brakujące wartości (`brakujace.py`: `nan`, `isnan`, `nanmean`, `nan_to_num`, `interp`); SciPy — wzmianka |
| `algebra-liniowa.md` | Algebra liniowa i dopasowanie | Układy równań (`uklad.py`: `solve`, `allclose`, `LinAlgError`); Dopasowanie prostej — najmniejsze kwadraty (`prosta.py`: `lstsq`, `Polynomial.fit`, R², wykres `dopasowanie.png`); Wektory własne i kierunek główny (`wlasne.py`: `eigh` kowariancji; zapowiedź PCA); Przekształcenia geometryczne (`obrot.py`: obrót i skalowanie, `obrot.png`); Normy i odległości (`odleglosci.py`: `norm`, odległości parami rozgłaszaniem, najbliższy sąsiad) |
| `losowosc-i-symulacje.md` | Losowość i symulacje | Generator i rozkłady (`rozklady.py`: `integers`, `uniform`, `normal`, `binomial`, `poisson`, `choice(p=)`, `permutation`; `rozklady.png`); Ziarno i niezależne strumienie (`ziarno.py`: `spawn()`); Symulacja Monte Carlo (`monte-carlo.py`: π; `monte-carlo.png`); Błądzenie losowe (`bladzenie.py`: 1000 tras × 200 kroków, `cumsum(axis=1)`; `bladzenie.png`); Próbkowanie ponowne (`bootstrap.py`: przedział ufności średniej) |
| `wydajnosc-i-pamiec.md` | Wydajność i pamięć | Typ elementów a pamięć (`pamiec.py`: `nbytes`, `float32`, `finfo`, `uint8`); Operacje w miejscu i argument `out=` (`w-miejscu.py`); Pętle, `np.vectorize` i prawdziwa wektoryzacja (`wektoryzacja2.py`: pomiar); Duże dane — porcje i `memmap` (`memmap.py`); Typowe pułapki (lista z przykładami `pulapki.py`); Kiedy sięgnąć dalej (Numba, pandas, SciPy) |

Szacunek: 950–1100 linii.

## Blok nawigacji (`mkdocs.yml`, w grupie „Python Zastosowania” po rozdziale 1)

```yaml
      - 2. NumPy w praktyce:
          - Wprowadzenie: zastosowania/02-numpy/index.md
          - Tablice wielowymiarowe: zastosowania/02-numpy/tablice-wielowymiarowe.md
          - Statystyka i porządkowanie danych: zastosowania/02-numpy/statystyka-i-porzadkowanie.md
          - Algebra liniowa i dopasowanie: zastosowania/02-numpy/algebra-liniowa.md
          - Losowość i symulacje: zastosowania/02-numpy/losowosc-i-symulacje.md
          - Wydajność i pamięć: zastosowania/02-numpy/wydajnosc-i-pamiec.md
```

Strona główna i `docs/zastosowania/index.md`: „2. [NumPy w praktyce](…/02-numpy/index.md) — tablice wielowymiarowe, statystyka i porządkowanie, algebra liniowa, losowość i symulacje, wydajność i pamięć”.

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `algebra-liniowa.md`, `losowosc-i-symulacje.md` | wykresy — pełne omówienie | rozdział 3 (Matplotlib w praktyce) |
| `statystyka-i-porzadkowanie.md`, `wydajnosc-i-pamiec.md` | tabele z kolumnami różnych typów | rozdział 4 (pandas) — istniejący marker |
| `algebra-liniowa.md` | analiza głównych składowych | rozdział 10 (uczenie bez nadzoru) |

## Domknięcia

| Plik | Zapowiedź | Cel |
|---|---|---|
| `zastosowania/01-jupyter/pierwsza-analiza.md` | „rozdziału o NumPy w praktyce” — TODO | `02-numpy/index.md` |

## CONTENT HANDOFF

Rozdział nie ma odpowiednika w `sources/` (wykład 9 pokrywa zakres rozdziału 14); `np.polyfit`, `np.random.rand` i `interp1d` ze slajdów pozostają zastąpione nowszymi interfejsami.

## Listy kontrolne

- Przed commitem: harness (`--mask=\d+\.\d+ (s|ms)`), `refresh_outputs.py`, `make_figures.py --img=`, oba buildy `--strict`, audyt kotwic i obrazów, cudzysłowy, kolokwializmy, trzy recenzje.
- Po commicie: domknięcie w rozdziale 1, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
