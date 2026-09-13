# Projekt rozdziału 3 części „Python Zastosowania” — Matplotlib w praktyce

Trzeci rozdział ścieżki Dane według `PLAN_ZASTOSOWANIA.md`. Branch: `content/zastosowania-03` (z `dev` po `47913ab`). Realizacja autonomiczna na polecenie autora z 13 IX 2026.

## Decyzje redakcyjne (13 IX 2026)

1. **Zakres:** Matplotlib poza rozdziałem 14 „Python Notatki” (tam: hierarchia obiektów, `subplots()`, style linii, adnotacje, `scatter`/`bar`/`hist`, siatka paneli, `savefig`, pułapki, `imshow`, `boxplot`, animacja). Tu: anatomia wykresu i sterowanie podziałkami, skalami i stylem; typy wykresów dla danych z niepewnością, kategoriami i rozkładami; daty i szeregi czasowe; układy wielu paneli (`subplot_mosaic`, wstawki, wspólne kolory); wykres do raportu i publikacji (formaty, styl domowy, czytelność, `PdfPages`, skrypt generujący). Bez powtarzania rozdziału 14 — odsyłacze.
2. **Środowisko:** Python 3.14.7, Matplotlib 3.11.2, NumPy 2.5.3; weryfikacja w `venv-ch8` z `MPLBACKEND=Agg`; skrypty jak w rozdziale 2; wykresy z listingów przez `make_figures.py --img=`. Skrypty bez wydruku mają w harnessie status „brak bloku wyniku” — dopuszczalny; gdzie to pouczające, skrypt wypisuje typy obiektów, wartości podziałek lub rozmiary plików.
3. **Dane:** generowane z `default_rng(42)`; daty jako `np.datetime64` z `np.arange`; bez plików zewnętrznych.
4. **Interfejsy sprawdzone 13 IX 2026 (3.11.2):** `ax.spines[["top", "right"]].set_visible()`, `MultipleLocator`, `PercentFormatter`, `FuncFormatter`, `twinx()`, `secondary_yaxis()`, `set_yscale("log")`, `bar_label()`, `fill_between()`, `errorbar()`, `stairs()`, `violinplot()`, `hexbin()`, `subplot_mosaic()` z `sharex`, `inset_axes()`, `fig.legend(loc="outside …")`, `plt.colormaps[...]`, `matplotlib.dates` (`AutoDateLocator`, `ConciseDateFormatter`, `DateFormatter`, `MonthLocator`), `axvspan()`, `autofmt_xdate()`, `rc_context()`, pliki `.mplstyle`, `PdfPages`, `savefig(metadata=)`, style `seaborn-v0_8-colorblind` i `tableau-colorblind10`.
5. **Terminy:** „podziałka” (ang. *tick*), „lokalizator” (ang. *locator*), „formater” (ang. *formatter*), „oś bliźniacza” (ang. *twin axis*), „oś wtórna” (ang. *secondary axis*), „małe wielokrotności” (ang. *small multiples*), „mozaika paneli”, „wstawka” (ang. *inset*), „wykres skrzypcowy” (ang. *violin plot*), „przedział niepewności”, „styl domowy” (ang. *house style*), „arkusz stylu” (ang. *style sheet*).
6. Odsyłacze wstecz: „Python Notatki” 8 (menedżer kontekstu — `rc_context`), 9 (`datetime`, `pathlib`), 14 (wszystkie sekcje Matplotlib), 16 (skrypt jako narzędzie); „Python Zastosowania” 1 (notatnik, projekt, powtarzalność), 2 (średnia ruchoma, kwantyle, `histogram`). Zapowiedzi: rozdział 4 (pandas — wykresy z tabel) — `TODO` po temacie; seaborn — wzmianka.
7. Domknięcie: marker „rozdziału o Matplotlib w praktyce” w `02-numpy/losowosc-i-symulacje.md`.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty (wykresy) |
|---|---|---|
| `index.md` | Wprowadzenie / „3. Matplotlib w praktyce” | co dokłada do rozdziału 14; wymagania; wersje; ---; ## W tym rozdziale (5) |
| `anatomia-wykresu.md` | Anatomia wykresu i style | Obiekty rysunku (`anatomia.py`: `Line2D`, `ax.lines`, `spines`, lokalizator); Podziałki — lokalizatory i formatery (`podzialki.py`; `podzialki.png`); Skale — logarytmiczna, oś bliźniacza i wtórna (`skale.py`; `skale.png`); Ramka, siatka i marginesy (`ramka.py`; `ramka.png`); Style i `rcParams` (`style.py`; `style.png`) |
| `wykresy-danych.md` | Wykresy dla danych | Przedziały niepewności — `fill_between()` i `errorbar()` (`niepewnosc.py`; `niepewnosc.png`); Słupki grupowane, skumulowane i z etykietami (`slupki.py`; `slupki.png`); Rozkłady — histogram, `stairs()`, pudełka i skrzypce (`rozklady2.py`; `rozklady2.png`); Zależności — kategorie, nakładanie punktów i `hexbin()` (`zaleznosci.py`; `zaleznosci.png`) |
| `szeregi-czasowe.md` | Daty i szeregi czasowe | Daty w NumPy i na osi (`daty.py`; `daty.png`); Lokalizatory i formatery dat (`daty-format.py`; `daty-format.png`); Wygładzanie, okresy i zdarzenia (`okresy.py`; `okresy.png`); Porównanie szeregów (`porownanie.py`; `porownanie.png`); `datetime` a `np.datetime64` (`konwersje-dat.py`) |
| `wiele-paneli-i-uklad.md` | Wiele paneli i układ | Małe wielokrotności (`male-wielokrotnosci.py`; `male-wielokrotnosci.png`); Mozaika paneli — `subplot_mosaic()` (`mozaika.py`; `mozaika.png`); Wstawka i wspólna legenda (`wstawka.py`; `wstawka.png`); Kolory spójne między panelami (`kolory.py`; `kolory.png`); Układ automatyczny a ręczny (`uklad.py`; `uklad.png`) |
| `zapis-i-raport.md` | Wykres do raportu i publikacji | Format, rozdzielczość i rozmiar (`zapis2.py`); Styl domowy w jednym pliku (`raport.mplstyle`, `styl-domowy.py`; `styl-domowy.png`); Czytelność — daltonizm i druk czarno-biały (`czytelnosc.py`; `czytelnosc.png`); Wiele wykresów w jednym PDF — `PdfPages` (`pdfpages.py`); Skrypt generujący wykresy raportu (`raport.py`); Pułapki prezentacji (lista); Dalej: pandas i seaborn |

Szacunek: 950–1100 linii; ok. 15 wykresów.

## Blok nawigacji (`mkdocs.yml`, w grupie „Python Zastosowania” po rozdziale 2)

```yaml
      - 3. Matplotlib w praktyce:
          - Wprowadzenie: zastosowania/03-matplotlib/index.md
          - Anatomia wykresu i style: zastosowania/03-matplotlib/anatomia-wykresu.md
          - Wykresy dla danych: zastosowania/03-matplotlib/wykresy-danych.md
          - Daty i szeregi czasowe: zastosowania/03-matplotlib/szeregi-czasowe.md
          - Wiele paneli i układ: zastosowania/03-matplotlib/wiele-paneli-i-uklad.md
          - Wykres do raportu i publikacji: zastosowania/03-matplotlib/zapis-i-raport.md
```

Strona główna i `docs/zastosowania/index.md`: „3. [Matplotlib w praktyce](…/03-matplotlib/index.md) — anatomia wykresu, wykresy dla danych, szeregi czasowe, wiele paneli, wykres do raportu”.

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `zapis-i-raport.md` | wykresy bezpośrednio z tabel pandas | rozdział 4 (pandas) |

## Domknięcia

| Plik | Zapowiedź | Cel |
|---|---|---|
| `zastosowania/02-numpy/losowosc-i-symulacje.md` | „rozdziału o Matplotlib w praktyce” — TODO | `03-matplotlib/wykresy-danych.md` (rozkłady i przedziały) |

## CONTENT HANDOFF

Rozdział nie ma odpowiednika w `sources/` (wykład 9 obejmuje podstawy z rozdziału 14); `tight_layout()` ze slajdów zastąpione `layout="constrained"`, `vert=` przez `orientation=`.

## Listy kontrolne

- Przed commitem: harness, `refresh_outputs.py`, `make_figures.py --img=`, oba buildy `--strict`, audyt kotwic i obrazów, cudzysłowy, kolokwializmy, trzy recenzje (w tym oględziny obrazów).
- Po commicie: domknięcie w rozdziale 2, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
