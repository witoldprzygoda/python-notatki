# Projekt rozdziału 6 części „Python Zastosowania” — Projekt: raport z danych

Szósty, ostatni rozdział ścieżki Dane — projekt spinający rozdziały 1–5. Branch: `content/zastosowania-06` (z `dev` po `b568fc8`). Realizacja autonomiczna na polecenie autora z 14 IX 2026.

## Decyzje redakcyjne (14 IX 2026)

1. **Zakres:** kompletny projekt `raport-sprzedazy` w układzie z rozdziału 1: pytania raportu, plik surowy z wadami (duplikaty, dwa formaty dat, nazwiska w różnej pisowni, `brak` w rabacie, brak ilości, ceny odstające), eksploracja i spisane decyzje; moduły `skrypty/przygotowanie.py` i `skrypty/analiza.py` z testami pytest; `skrypty/rysunki.py` i `skrypty/generuj_raport.py` wytwarzające tabele CSV, rysunki PNG i dokument `wyniki/raport.md`; README i lista kontrolna. Trzy strony + index. Zapowiedź ścieżki uczenia maszynowego (`TODO` rozdział 7).
2. **Dane:** `dane/surowe/zamowienia_surowe.csv` — 245 wierszy z generatora `generuj_surowe.py` (ziarno 42; baza jak w rozdziale 5 plus 12 dat `dd.mm.yyyy`, 10 nazwisk ze spacjami i wielkością liter, 4 `brak`, 4 puste ilości, 3 kategorie z wielką literą i spacją, 2 ceny ×10, 5 duplikatów, przetasowanie); `dane/surowe/klienci.csv` jak w rozdziale 5. Pliki w `docs/zastosowania/06-projekt-dane/dane/surowe/`; harness kopiuje katalog rekurencyjnie (`--data=` rozszerzone 14 IX 2026 o podkatalogi; `make_figures.py` zbiera obrazy z podkatalogów).
3. **Pułapka dat:** `pd.to_datetime(format="mixed", dayfirst=True)` odwraca dzień i miesiąc w datach ISO (wynik sięga grudnia) — parsujemy dwa formaty jawnie i łączymy `fillna()`.
4. **Środowisko:** pandas 3.0.5, NumPy 2.5.3, Matplotlib 3.11.2, pyarrow 25.0.1, tabulate 0.10.0, pytest 9.1.1; skrypty uruchamiane z katalogu projektu (`python skrypty/...`); testy z `tests/conftest.py` dodającym `skrypty/` do `sys.path`; wydruk pytest z rzeczywistego uruchomienia.
5. **Terminy:** „potok”, „dane surowe/przetworzone”, „wartość odstająca” (ang. *outlier*), „lista kontrolna”, „dziennik decyzji”.
6. Odsyłacze wstecz: „Python Notatki” 7 (moduły), 9 (`pathlib`, CSV), 16 (pytest, `conftest.py`); „Python Zastosowania” 1 (układ projektu, README), 2 (mediana), 3 (styl domowy, skrypt generujący, `PdfPages` — wzmianka), 4 (czyszczenie), 5 (grupowanie, `resample`, `rolling`, `merge`, `pipe`, `to_markdown`).
7. Domknięcie: marker „rozdziału o projekcie raportu z danych” w `05-pandas-analiza/wydajnosc-i-potok.md`.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty |
|---|---|---|
| `index.md` | Wprowadzenie / „6. Projekt: raport z danych” | cel; wymagania; dane do pobrania; ---; ## W tym rozdziale (3) |
| `zadanie-i-dane.md` | Zadanie, dane i decyzje | Pytania raportu; Układ projektu; Dane surowe (`generuj_surowe.py`, `dane/surowe/klienci.csv`); Eksploracja (`skrypty/eksploracja.py`); Decyzje czyszczenia (tabela, `README.md` fragment) |
| `potok.md` | Potok — czyszczenie, analiza i testy | Moduł przygotowania (`skrypty/przygotowanie.py`); Moduł analizy (`skrypty/analiza.py`); Podgląd wyników (`skrypty/podglad.py`); Testy (`tests/conftest.py`, `tests/test_przygotowanie.py`, `tests/test_analiza.py`, pytest) |
| `raport.md` | Raport — rysunki, tabele i dokument | Rysunki (`skrypty/rysunki.py`); Skrypt generujący (`skrypty/generuj_raport.py`; `trend.png`, `kategorie.png`, `klienci.png`); Dokument raportu (wydruk `wyniki/raport.md`); README i lista kontrolna; Dalej: uczenie maszynowe (TODO 7) |

Szacunek: 650–800 linii; 3 wykresy.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 5)

```yaml
      - 6. Projekt: raport z danych:
          - Wprowadzenie: zastosowania/06-projekt-dane/index.md
          - Zadanie, dane i decyzje: zastosowania/06-projekt-dane/zadanie-i-dane.md
          - Potok — czyszczenie, analiza i testy: zastosowania/06-projekt-dane/potok.md
          - Raport — rysunki, tabele i dokument: zastosowania/06-projekt-dane/raport.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `raport.md` | ścieżka uczenia maszynowego | rozdział 7 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/05-pandas-analiza/wydajnosc-i-potok.md` | `06-projekt-dane/index.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/`. Ścieżka Dane (1–6) ukończona; następna ścieżka: Uczenie maszynowe (7–12).

## Listy kontrolne

- Przed commitem: pliki `dane/surowe/` z generatora i bloku; harness z `--data=` (podkatalogi); `refresh_outputs.py`; `make_figures.py --img= --data=`; pytest ręcznie dla bloku wyniku; oba buildy `--strict`; kotwice; cudzysłowy; kolokwializmy; trzy recenzje.
- Po commicie: domknięcie w rozdziale 5, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
