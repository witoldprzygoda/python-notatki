# Projekt rozdziału 12 części „Python Zastosowania” — Projekt: od danych do modelu

Szósty, ostatni rozdział ścieżki Uczenie maszynowe — projekt spinający rozdziały 7–11. Branch: `content/zastosowania-12` (z `dev` po `14895f7`). Realizacja autonomiczna na polecenie autora z 19 IX 2026.

## Decyzje redakcyjne (19 IX 2026)

1. **Zakres:** kompletny projekt `rezygnacja-klientow` — przewidywanie rezygnacji klientów operatora internetowego z pliku surowego o typowych wadach (duplikaty, etykieta celu w czterech pisowniach, plan z wielką literą i spacją, wiek brakujący i niemożliwy, kolumna `powod_rezygnacji` będąca wyciekiem celu); koszty błędów uzgodnione z odbiorcą (utrata klienta 500 zł, oferta zatrzymująca 80 zł); moduły `skrypty/przygotowanie.py` (czyszczenie z dziennikiem, podział, `ColumnTransformer`), `skrypty/modele.py` (kandydaci z rozdziałów 8 i 11, porównanie w walidacji krzyżowej, tabela kosztów i próg), `skrypty/rysunki.py`, `skrypty/porownanie.py`, `skrypty/trenuj.py` (wybór, próg, jednorazowa ocena testowa, ważność permutacyjna, trening na całości, pakiet joblib z metadanymi, raport Markdown z rysunkami), `skrypty/przewiduj.py` (ocena nowych klientów z pliku CSV, kontrola wejścia względem zakresów i kategorii z treningu); testy pytest; README i lista kontrolna. Sieć z rozdziału 11 reprezentuje `MLPClassifier` scikit-learn (wspólna walidacja krzyżowa); PyTorch niepotrzebny. Trzy strony + index. Poza zakresem: kalibracja prawdopodobieństw, monitorowanie dryfu, API (zapowiedź ścieżki Aplikacje).
2. **Dane:** `dane/surowe/klienci.csv` — 2010 wierszy z generatora `generuj_surowe.py` (ziarno 42; 2000 klientów, rezygnacja 27,9%, zależności z interakcjami: umowa miesięczna × zgłoszenia, staż ≤ 6 miesięcy, przelew × opóźnienia; wady: 80 etykiet `1/0`, 30 wielkimi literami, 40 planów z wielką literą i spacją, 90 braków wieku, 5 wieków 0 i 5 wieków 140, 10 duplikatów); `dane/nowi_klienci.csv` — 6 klientów do oceny (jeden z nieznanym planem, jeden z wiekiem 150, jeden bez wieku). Pliki w `docs/zastosowania/12-projekt-ml/dane/`; harness `--data=` ze stagingiem całego projektu (moduły `skrypty/` wyciągnięte z bloków książki skryptem `extract_project.py` w scratchpadzie).
3. **Środowisko:** `venv-ch8` — scikit-learn 1.9.1, pandas 3.0.5, NumPy 2.5.3, Matplotlib 3.11.2, joblib 1.6.0, tabulate 0.10.0, pytest 9.1.1; skrypty uruchamiane z katalogu projektu; `tests/conftest.py` dodaje `skrypty/` do `sys.path`.
4. **Fakty sprawdzone 19 IX 2026 (sonda):** po czyszczeniu 2000 wierszy, 100 braków wieku; podział 1500/500 (419/139 rezygnacji); walidacja krzyżowa AUC: regresja logistyczna 0,867 ± 0,037, las 0,848, wzmacnianie 0,834, MLP 0,832, bazowy 0,5; z kolumną `powod_rezygnacji` AUC 1,0; koszt (500/80) na 1500 klientach: nikt 209 500, wszyscy 120 000, model przy progu 0,15 — 85 060 (0,20 — 86 120); test regresji logistycznej AUC 0,868; ważność permutacyjna: umowa 0,21, zgłoszenia 0,04, staż 0,03; `MLPClassifier(early_stopping=True)` bez ostrzeżeń.
5. **Terminy:** „rezygnacja klientów” (ang. *churn*), „koszt błędu”, „oferta zatrzymująca”, „pakiet modelu”, „kontrola wejścia”, „dziennik decyzji” (z rozdziału 6).
6. Odsyłacze wstecz: „Python Notatki” 7 (moduły, `sys.argv`), 9 (`pathlib`, CSV), 16 (pytest); „Python Zastosowania” 1 (układ projektu), 4 (czyszczenie), 6 (dziennik decyzji, README, lista kontrolna, raport Markdown), 7 (podział, walidacja, zapis modelu), 8 (AUC, próg według kosztu, model końcowy, ważność permutacyjna), 9 (`ColumnTransformer`, imputacja, wyciek celu), 10 (obserwacje nietypowe — kontrola wejścia), 11 (sieć, `MLPClassifier`). Zapowiedzi: 13 (ścieżka Aplikacje), 15 (FastAPI — model za API), 20 (argparse) — `TODO`.
7. Domknięcia: marker „rozdziału o projekcie uczenia maszynowego” (11/praktyka) → `12-projekt-ml/index.md`.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty (wykresy) |
|---|---|---|
| `index.md` | Wprowadzenie / „12. Projekt: od danych do modelu” | cel; zadanie i koszty; dane do pobrania; wersje; ---; ## W tym rozdziale (3) |
| `zadanie-i-dane.md` | Zadanie, dane i decyzje | Zadanie i koszt błędu; Układ projektu; Dane surowe (`generuj_surowe.py`); Eksploracja (`skrypty/eksploracja.py`); Decyzje (tabela, `README.md`, `.gitignore`) |
| `potok-i-modele.md` | Potok, modele i wybór | Moduł przygotowania (`skrypty/przygotowanie.py`); Moduł modeli (`skrypty/modele.py`); Rysunki (`skrypty/rysunki.py`); Porównanie i próg (`skrypty/porownanie.py`; `koszt-prog.png`); Testy (`tests/conftest.py`, `tests/test_przygotowanie.py`, `tests/test_modele.py`, pytest) |
| `model-i-raport.md` | Model końcowy, raport i użycie | Skrypt treningowy (`skrypty/trenuj.py`; `waznosc.png`); Dokument raportu (`pokaz_raport.py`); Ocena nowych klientów (`dane/nowi_klienci.csv`, `skrypty/przewiduj.py`, `tests/test_przewiduj.py`, pytest); Lista kontrolna projektu; Dalej: ścieżka Aplikacje (TODO 13, 15) |

Szacunek: 750–900 linii; 2 wykresy.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 11)

```yaml
      - "12. Projekt: od danych do modelu":
          - Wprowadzenie: zastosowania/12-projekt-ml/index.md
          - Zadanie, dane i decyzje: zastosowania/12-projekt-ml/zadanie-i-dane.md
          - Potok, modele i wybór: zastosowania/12-projekt-ml/potok-i-modele.md
          - Model końcowy, raport i użycie: zastosowania/12-projekt-ml/model-i-raport.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `model-i-raport.md` | ścieżka Aplikacje (bazy danych), model za API (FastAPI), argparse | rozdziały 13, 15, 20 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/11-pytorch/praktyka.md` | `12-projekt-ml/index.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/`. Ścieżka Uczenie maszynowe (7–12) ukończona; następna ścieżka: Aplikacje (13–18).

## Listy kontrolne

- Przed commitem: staging projektu z bloków; harness z `--data=staging`; `refresh_outputs.py`; `make_figures.py --img= --data=`; pytest ręcznie dla bloków wyniku; pliki `dane/` w repo z generatora; oba buildy `--strict`; kotwice; cudzysłowy; kolokwializmy; recenzje z weryfikacją uwag.
- Po commicie: domknięcie w rozdziale 11, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
