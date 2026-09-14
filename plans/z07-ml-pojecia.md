# Projekt rozdziału 7 części „Python Zastosowania” — Uczenie maszynowe — pojęcia i warsztat

Pierwszy rozdział ścieżki Uczenie maszynowe (7–12). Branch: `content/zastosowania-07` (z `dev` po `16bf12d`). Realizacja autonomiczna na polecenie autora z 14 IX 2026.

## Decyzje redakcyjne (14 IX 2026)

1. **Zakres:** pojęcia (uczenie z nadzorem i bez, klasyfikacja i regresja, cechy i etykiety, model–trening–predykcja, generalizacja, miary) z ręcznym klasyfikatorem centroidów w NumPy; pierwszy model od początku do końca na zbiorze iris (`train_test_split`, `KNeighborsClassifier`, `score`, `DummyClassifier`, `predict` na nowych obserwacjach, granica decyzyjna); warsztat scikit-learn (estymator, hiperparametry a atrybuty z `_`, transformatory i `Pipeline`, `set_output`, walidacja krzyżowa, `GridSearchCV`, zapis modelu joblib, powtarzalność); przeuczenie i uczciwa ocena (niedouczenie/przeuczenie na drzewie regresji, krzywa walidacji, krzywa uczenia, wyciek danych na losowych cechach, mapa wyboru modelu). Poza zakresem (rozdziały 8–10): miary klasyfikacji poza dokładnością, regresja i przygotowanie cech (kodowanie, imputacja, `ColumnTransformer`), grupowanie i PCA. Zapowiedzi `TODO`.
2. **Dane:** zbiory wbudowane scikit-learn — iris (150×4, trzy gatunki), wine (krzywa uczenia), diabetes (regresja, wzmianka), dane syntetyczne z `default_rng(42)`. Bez plików; harness bez `--data`.
3. **Środowisko:** scikit-learn 1.9.1 (joblib 1.6.0, SciPy 1.18.1, threadpoolctl 3.6.0), pandas 3.0.5, NumPy 2.5.3, Matplotlib 3.11.2.
4. **Fakty sprawdzone 14 IX 2026:** `load_iris(as_frame=True)` daje `DataFrame` z nazwami cech i `Series` `target`; `predict` na tablicy NumPy po treningu na ramce ostrzega `UserWarning`, a ramka z kolumnami w innej kolejności zgłasza `ValueError`; `train_test_split(stratify=y, random_state=42)` → 112/38; KNN k=5 na iris 0,974, `DummyClassifier` 0,316; klasyfikator centroidów 0,927; potok ze skalowaniem 0,921 (skalowanie nie zawsze pomaga); CV 5× → średnia 0,973 ± 0,025; `GridSearchCV` z siatką k × wagi wybiera k=21 z wagami odległościowymi (0,982 CV, 0,947 test) — proza zaleca prostsze k=3; `learning_curve` wymaga `shuffle=True` przy posortowanych etykietach (inaczej `LogisticRegression` dostaje jedną klasę); wyciek: selekcja cech na całym zbiorze losowym daje 0,73 wobec uczciwych 0,53 (w sondzie 0,82/0,54 przy innym stanie generatora); `DecisionBoundaryDisplay.from_estimator` działa (dla wielu klas `multiclass_colors=`, nie `cmap=`; `response_method="predict"` dla ostrych obszarów); `float.round` nie istnieje — `round(score, 3)`.
5. **Terminy:** „uczenie maszynowe” (ang. *machine learning*), „uczenie z nadzorem / bez nadzoru” (ang. *supervised / unsupervised*), „cecha” (ang. *feature*), „etykieta” / „zmienna docelowa” (ang. *label*, *target*), „próbka” (ang. *sample*), „zbiór treningowy / testowy”, „trening” — „dopasowanie” (ang. *fit*), „predykcja”, „dokładność” (ang. *accuracy*), „uogólnianie” (ang. *generalization*), „przeuczenie / niedouczenie” (ang. *overfitting / underfitting*), „hiperparametr”, „estymator”, „transformator”, „potok”, „walidacja krzyżowa” (ang. *cross-validation*), „wyciek danych” (ang. *data leakage*), „model bazowy” (ang. *baseline*), „krzywa walidacji / uczenia”, „granica decyzyjna”.
6. Odsyłacze wstecz: „Python Notatki” 8 (instrukcja `with`), 9 (`pickle`), 14 (NumPy, wykresy); „Python Zastosowania” 1 (projekt), 2 (`argmin`, `norm`, `default_rng`, mediana), 3 (wykresy, style), 4 (ramki), 5 (`groupby`), 6 (potok, testy). Zapowiedzi: rozdział 8 (miary klasyfikacji, macierz pomyłek, modele), 9 (regresja, `ColumnTransformer`, kodowanie), 10 (grupowanie, PCA), 11 (PyTorch) — `TODO` po temacie.
7. Domknięcia: marker „pojęciach uczenia maszynowego” (06/raport) → `07-ml-pojecia/index.md`; marker „rozdziału o SciPy” (14/przyklady) → scikit-learn w rozdziale 7, SciPy — wzmianka w rozdziale 2 (`wydajnosc-i-pamiec.md`).

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty (wykresy) |
|---|---|---|
| `index.md` | Wprowadzenie / „7. Uczenie maszynowe — pojęcia i warsztat” | czym jest ścieżka; wymagania (`requirements.txt` + scikit-learn); ---; ## W tym rozdziale (4) |
| `pojecia.md` | Pojęcia uczenia maszynowego | Reguły a dane; Zadania — klasyfikacja, regresja, grupowanie; Cechy, etykiety, próbki (`cechy.py`; `cechy.png`); Model, trening, predykcja — klasyfikator centroidów (`centroidy.py`); Uogólnianie i zbiór testowy; Słownik pojęć (tabela) |
| `pierwszy-model.md` | Pierwszy model od początku do końca | Dane (`dane.py`); Podział (`podzial.py`); Trening i predykcja (`knn.py`); Ocena i model bazowy (`ocena.py`); Nowe obserwacje (`nowe.py`); Granica decyzyjna (`granica.py`; `granica.png`) |
| `warsztat.md` | Warsztat scikit-learn | Estymator — jeden interfejs (`estymator.py`); Transformatory i potok (`potok.py`); Walidacja krzyżowa (`walidacja.py`); Dobór hiperparametrów — `GridSearchCV` (`siatka.py`); Zapis i wczytanie modelu (`zapis-modelu.py`); Powtarzalność |
| `przeuczenie-i-ocena.md` | Przeuczenie i uczciwa ocena | Niedouczenie i przeuczenie (`dopasowanie.py`; `dopasowanie.png`); Krzywa walidacji (`krzywa-walidacji.py`; `krzywa-walidacji.png`); Krzywa uczenia (`krzywa-uczenia.py`; `krzywa-uczenia.png`); Wyciek danych (`wyciek.py`); Wybór modelu — mapa ścieżki (tabela); Dalej: klasyfikacja (TODO 8) |

Szacunek: 800–950 linii; 5 wykresów.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 6)

```yaml
      - 7. Uczenie maszynowe — pojęcia i warsztat:
          - Wprowadzenie: zastosowania/07-ml-pojecia/index.md
          - Pojęcia uczenia maszynowego: zastosowania/07-ml-pojecia/pojecia.md
          - Pierwszy model od początku do końca: zastosowania/07-ml-pojecia/pierwszy-model.md
          - Warsztat scikit-learn: zastosowania/07-ml-pojecia/warsztat.md
          - Przeuczenie i uczciwa ocena: zastosowania/07-ml-pojecia/przeuczenie-i-ocena.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `pierwszy-model.md`, `przeuczenie-i-ocena.md` | miary klasyfikacji i modele | rozdział 8 |
| `pojecia.md`, `przeuczenie-i-ocena.md` | regresja i przygotowanie cech | rozdział 9 |
| `pojecia.md` | grupowanie i PCA | rozdział 10 |
| `przeuczenie-i-ocena.md` | sieci neuronowe (PyTorch) | rozdział 11 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/06-projekt-dane/raport.md` | `07-ml-pojecia/index.md` |
| `14-numpy-matplotlib/przyklady-i-rozszerzenia.md` | `07-ml-pojecia/index.md` (scikit-learn); SciPy → `02-numpy/wydajnosc-i-pamiec.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/` (wykład 12 wspomina DS/ML jednym slajdem).

## Listy kontrolne

- Przed commitem: harness, `refresh_outputs.py`, `make_figures.py --img=`, oba buildy `--strict`, kotwice, cudzysłowy, kolokwializmy, trzy recenzje.
- Po commicie: domknięcia, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
