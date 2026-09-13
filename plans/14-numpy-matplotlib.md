# Projekt rozdziału 14 — NumPy i Matplotlib

Skondensowany projekt stron rozdziału 14 według `PLAN_ROZWOJU.md` (sekcja 4, „14. NumPy i Matplotlib”) i `DEVELOPMENT_WORKFLOW.md`. Branch: `content/14-numpy-matplotlib` (z `dev` po integracji rozdziału 13, commit `4c0678f`). Rozdział pomostowy: zakres wyznaczony przez laboratoria 9–10 i wykład 9; pełne omówienie bibliotek trafi do części II (`plans/CZESC-II.md`).

## Decyzje redakcyjne (13 IX 2026)

1. **Środowisko:** pakiety instalowane w venv kursu poleceniem `python -m pip install numpy matplotlib`; wersje odniesienia NumPy 2.5.3, Matplotlib 3.11.2, SciPy 1.18.1 (koła dla 3.14; sprawdzone 13 IX 2026). Weryfikacja stron interpreterem tymczasowego venv w scratchpadzie (`venv-ch8`, Python 3.14.7) z `MPLBACKEND=Agg`.
2. **Wykresy jako obrazy generowane skryptem:** każdy przykład Matplotlib kończy się `fig.savefig("nazwa.png", dpi=120)`; obrazy w `docs/14-numpy-matplotlib/img/` powstają skryptem `make_figures_ch14.py` (scratchpad), który uruchamia bloki `python title=` stron i kopiuje pliki PNG. Strony osadzają je zapisem `![opis](img/nazwa.png){ width="640" }`. Bez zrzutów ekranu, bez wpisów w `ZRZUTY.md`.
3. **`plt.show()`** tylko w pierwszym przykładzie (bez bloku wyniku — ostrzeżenie Agg w harnessie jest oczekiwane) i w prozie; pozostałe przykłady zapisują plik i wypisują potwierdzenie.
4. **Styl obiektowy** (`fig, ax = plt.subplots()`) jako jedyny styl w kodzie; interfejs stanowy `pyplot` pokazany raz jako `.python .no-copy` dla rozpoznawania cudzego kodu.
5. **Tylko `default_rng()`** z ziarnem 42 (wyniki powtarzalne, bloki weryfikowalne); bez `np.random.seed/rand/randn`.
6. **Modernizacje względem W09:** `boxplot(orientation="vertical")` zamiast `vert=` (przestarzałe od 3.11); `layout="constrained"` zamiast `tight_layout()`; `make_interp_spline` zamiast `interp1d`; `eval()` zastąpione współczynnikami i `np.polyval()`; `np.sin(np.pi)` ≈ 1,22e-16 (nie 0) z `np.isclose()`; przyspieszenie NumPy podawane z własnego pomiaru (ok. 16× dla 10⁶ elementów, nie „75×”).
7. **Pliki danych** osadzone jako bloki `text title="pomiary.csv"` (harness zapisuje je do katalogu tymczasowego); bez katalogu `data/`.
8. **Odsyłacze wstecz:** rozdz. 3 (typ float), 4 (`arange`/`linspace`), 5 (wycinki list, tablice wielowymiarowe, kopie), 7 (`math.isclose`, eksperyment Decimal), 9 (CSV, `pathlib`), 11 (`__getitem__` z krotką, `__matmul__`), 13 (wektoryzacja, Numba).
9. Etykieta strony 5 bez dopisku „(dla dociekliwych)” — oznaczenie w pierwszym akapicie i w `index.md`.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty |
|---|---|---|
| `index.md` | Wprowadzenie / „14. NumPy i Matplotlib” | ekosystem naukowy; instalacja; konwencje importu; rozdział pomostowy → część II; ---; ## W tym rozdziale (5); nota lab9–10 |
| `ndarray.md` | Tablice ndarray | Od listy do tablicy (`lista-a-tablica.py`); Tworzenie tablic (`tworzenie.py`: array/zeros/ones/full/eye/arange/linspace); Atrybuty i typy elementów (`atrybuty.py`: ndim/shape/size/dtype/itemsize/nbytes, int64 w NumPy 2 na Windows, `astype`, ciche przepełnienie int8; `float32-float64.py` — eksperyment lab3 z Decimal, float32, float64 i `np.isclose`); Indeksowanie i wycinki (`indeksowanie.py`: 1D/2D, fancy, maski `& | ~`, błąd `and`); Widok a kopia (`widok-a-kopia.py`: `base`, `.copy()`, tabela); Zapis i odczyt (`zapis-odczyt.py`: `save/load`, `savez`, `loadtxt` z `pomiary.csv`, `savetxt`) |
| `operacje.md` | Operacje na tablicach | Operacje elementowe i funkcje uniwersalne (`ufunc.py`: arytmetyka, porównania, `np.where`, `np.sin(np.pi)`); Rozgłaszanie (`broadcasting.py`: skalar, kolumna + wiersz, reguły, `ValueError`); Agregacje i oś `axis` (`agregacje.py` + schemat `.text`); Przekształcanie kształtu (`ksztalt.py`: reshape −1, ravel/flatten, T, stack); Liczby losowe — `default_rng()` (`losowe.py`); Wektoryzacja — pomiar (`wektoryzacja.py`: pętla, `sum()` z generatorem, NumPy dla 10⁶; domyka rozdz. 13); Przydatne funkcje (tabela: sort/argsort, unique, clip, nan*, round, allclose); Algebra liniowa (dla dociekliwych) (`algebra.py`: `@` a `*`, det, inv, solve; `__matmul__` z rozdz. 11; `meshgrid` zdaniem) |
| `matplotlib-podstawy.md` | Matplotlib — pierwszy wykres i styl obiektowy | Hierarchia obiektów (schemat Figure → Axes → Axis); Pierwszy wykres (`pierwszy-wykres.py` z `plt.show()`, obraz `pierwszy-wykres.png`); Interfejs `pyplot` a styl obiektowy (`.python .no-copy`); Linie, znaczniki i style (`style-linii.py`: color/linestyle/marker, skrót `"r--o"`, legend, grid, xlim, `plt.style.context`, `style.available`); Tekst i adnotacje (`adnotacje.py`: `text`, `annotate` ze strzałką, zapis matematyczny `r"$\sin(x)$"`) |
| `matplotlib-wykresy.md` | Matplotlib — rodzaje wykresów, układ i zapis | Wykres punktowy — `scatter()` (`punktowy.py`: `c=`, `s=`, `cmap`, `colorbar`); Słupkowy i histogram — `bar()` i `hist()` (`slupki-histogram.py`: bins, density, edgecolor); Wiele paneli — `subplots()` (`panele.py`: 2×2, `layout="constrained"`, `sharex`, `suptitle`; `gridspec` zdaniem); Zapis do pliku — `savefig()` (formaty, dpi, `bbox_inches="tight"`, `transparent`, `plt.close()` w pętli); Typowe pułapki (show blokuje, nachodzenie, `set_aspect("equal")`, wiele okien) |
| `przyklady-i-rozszerzenia.md` | Przykłady i rozszerzenia | Wielomian bez `eval()` (`wielomian.py` z `input()` — współczynniki i przedział, `np.polyval`; harness `--stdin`); Histogram i wykres pudełkowy (`analiza.py`: `axvline` średnia/mediana, `boxplot(orientation=)`); Mapa ciepła — `imshow()` (`mapa-ciepla.py`: `corrcoef`, `colorbar`; obraz jako tablica zdaniem); Animacja — `FuncAnimation` (`.python .no-copy`, zapis GIF przez Pillow); SciPy — krótki przegląd (`.python .no-copy`: `curve_fit`, `ttest_ind`, `make_interp_spline`; zapowiedź części II); Numba — odsyłacz do rozdz. 13 |

Szacunek: 850–950 linii.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 13)

```yaml
  - 14. NumPy i Matplotlib:
      - Wprowadzenie: 14-numpy-matplotlib/index.md
      - Tablice ndarray: 14-numpy-matplotlib/ndarray.md
      - Operacje na tablicach: 14-numpy-matplotlib/operacje.md
      - Matplotlib — pierwszy wykres i styl obiektowy: 14-numpy-matplotlib/matplotlib-podstawy.md
      - Matplotlib — rodzaje wykresów, układ i zapis: 14-numpy-matplotlib/matplotlib-wykresy.md
      - Przykłady i rozszerzenia: 14-numpy-matplotlib/przyklady-i-rozszerzenia.md
```

`docs/index.md`: „14. [NumPy i Matplotlib](14-numpy-matplotlib/index.md) — tablice ndarray, operacje wektorowe, wykresy w stylu obiektowym”.

## Zapowiedzi w przód (rejestrowane w `PLAN_ROZWOJU.md` / `plans/CZESC-II.md`)

| Strona | Temat | Cel |
|---|---|---|
| `ndarray.md` (Zapis i odczyt) | pandas — tabele danych z nazwanymi kolumnami | część II (sekcja 17 planu) |
| `przyklady-i-rozszerzenia.md` | SciPy i scikit-learn w pełnym zakresie | część II (ścieżka danych) |

## Domknięcia zapowiedzi z wcześniejszych rozdziałów

| Plik | Wiersz | Zapowiedź | Cel |
|---|---|---|---|
| `04-sterowanie/petle-i-iteratory.md` | 83 | nawias o `numpy.arange()` i `numpy.linspace()` | `ndarray.md#tworzenie-tablic` |
| `05-typy-zlozone/referencje-i-kopiowanie.md` | 61–63 | admonition „NumPy … poznamy w dalszej części kursu” | `ndarray.md` (H1) |
| `11-model-danych/kolekcje-i-wywolania.md` | 163 | `tablica[0, :]` — TODO | `ndarray.md#indeksowanie-i-wycinki` |
| `11-model-danych/operatory.md` | 504 | `@` w NumPy — TODO | `operacje.md#algebra-liniowa-dla-dociekliwych` |
| `13-wydajnosc/przyspieszanie-pythona.md` | 28 | kod i pomiar wektoryzacji — TODO | `operacje.md#wektoryzacja-pomiar` |

## CONTENT HANDOFF (rozbieżności ze źródłami)

(a) W09 sl. 5 i 15: `np.random.rand/randn/seed` — w książce wyłącznie `default_rng()`; (b) W09 sl. 9: `np.sin([0, π/2, π])` podane jako `[0. 1. 0.]` — w rzeczywistości `1.22e-16` dla π, stąd `np.isclose()`; (c) W09 sl. 11–12: „75× szybciej”, „~250× Numba” — w książce własne pomiary (ok. 16× dla NumPy); (d) W09 sl. 20, 24, 25: `tight_layout()` → `layout="constrained"`; sl. 31: `boxplot(vert=True)` przestarzałe od Matplotlib 3.11 → `orientation="vertical"`; sl. 34: `interp1d` (tryb utrzymaniowy) → `make_interp_spline`; (e) W09 sl. 30: `eval()` na wejściu użytkownika zastąpione współczynnikami wielomianu; (f) W09 sl. 6: zniekształcona ekstrakcja atrybutów (`a.size # (2, 3)`) — wartości z uruchomienia; (g) W09 sl. 14: `ravel()` jest widokiem tylko dla tablic ciągłych w pamięci — w książce z zastrzeżeniem; (h) lab3: sumowanie `0.1 0.2 0.3` — w float32 wynik równy dokładnie `0.6` (mniejsza precyzja maskuje błąd), w float64 `0.6000000000000001`; pokazane jako eksperyment.

## Listy kontrolne

- Przed commitem stron: harness interpreterem venv (`MPLBACKEND=Agg`), `refresh_outputs.py` z blokami danych, `make_figures_ch14.py`, oba buildy, audyt kotwic, cudzysłowy, kolokwializmy, trzy recenzje.
- Po commicie: domknięcia z tabeli, status w `PLAN_ROZWOJU.md`, integracja do `dev`, wpis w pamięci.
