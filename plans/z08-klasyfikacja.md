# Projekt rozdziału 8 części „Python Zastosowania” — Klasyfikacja

Drugi rozdział ścieżki Uczenie maszynowe. Branch: `content/zastosowania-08` (z `dev` po `f0782e7`). Realizacja autonomiczna na polecenie autora z 14 IX 2026.

## Decyzje redakcyjne (14 IX 2026)

1. **Zakres:** miary klasyfikacji (macierz pomyłek, precyzja, czułość, F1, `classification_report`, próg decyzyjny, krzywa ROC i AUC, klasy nierównoliczne — dokładność zrównoważona i `class_weight`, wiele klas — uśrednianie makro/ważone); regresja logistyczna (funkcja logistyczna i `decision_function`, współczynniki i iloraz szans, regularyzacja `C`, wiele klas, kiedy model liniowy wystarcza); drzewa decyzyjne i lasy losowe (`export_text`, `plot_tree`, głębokość i `min_samples_leaf`, ważność cech, `RandomForestClassifier` z `oob_score`, liczba drzew, wzmianka o wzmacnianiu gradientowym `HistGradientBoostingClassifier`); wybór modelu i interpretacja (porównanie wielu miar w `cross_validate`, ważność permutacyjna, analiza błędów, próg pod koszt błędu, model końcowy z joblib, lista kontrolna). Poza zakresem: SVM, naiwny Bayes, kalibracja, uczenie wieloetykietowe. Zapowiedź rozdziału 9 (`TODO`).
2. **Dane:** `load_breast_cancer` (569 × 30, dwie klasy; klasę pozytywną definiujemy jako nowotwór złośliwy: `y = (target == 0)` → 212 pozytywnych, 357 negatywnych), `load_wine` (trzy klasy) dla miar wieloklasowych; podzbiór nierównoliczny (30 złośliwych + 357 łagodnych) z `default_rng(42)`. Bez plików.
3. **Środowisko:** jak rozdział 7 (scikit-learn 1.9.1).
4. **Fakty sprawdzone 14 IX 2026:** podział 426/143 (53 pozytywne w teście); regresja logistyczna ze skalowaniem — macierz `[[89, 1], [1, 52]]` w układzie (negatywna, pozytywna), dokładność 0,986, AUC 0,998; `DummyClassifier` 0,629; próg 0,1 daje czułość 1,0 przy precyzji 0,83, próg 0,7 — precyzję 1,0 przy czułości 0,94; krzywa walidacji `C`: najlepiej 0,1–1; wielkość współczynników rośnie z `C`; wine — regresja logistyczna 100% na teście, `coef_` (3, 13); drzewo `max_depth=3`: trening 0,977, test 0,944, 7 liści; pełne drzewo: głębokość 7, 18 liści, trening 1,0, test 0,923; CV po głębokości: 1 → 0,888, 3 → 0,924, 5 → 0,928, pełne 0,91; las 300 drzew: test 0,958, OOB 0,962, CV 0,953; HGB CV 0,967; porównanie CV (dokładność/czułość/F1/AUC): logistyczna 0,974/0,992/0,979/0,995 najlepsza; ważność permutacyjna mała, bo cechy skorelowane; podzbiór nierównoliczny: dokładność 0,995 wobec bazowej 0,922, zrównoważona 0,967 wobec 0,5; `class_weight="balanced"` zwiększa czułość klasy rzadkiej; `penalty` regresji logistycznej przestarzałe — nie drukować.
5. **Terminy:** „macierz pomyłek” (ang. *confusion matrix*), „prawdziwie/fałszywie dodatni/ujemny”, „precyzja” (ang. *precision*), „czułość” (ang. *recall*, *sensitivity*), „swoistość” (ang. *specificity*), „F1”, „próg decyzyjny” (ang. *decision threshold*), „krzywa ROC”, „pole pod krzywą” (ang. *AUC*), „klasy nierównoliczne” (ang. *imbalanced classes*), „dokładność zrównoważona” (ang. *balanced accuracy*), „funkcja logistyczna” (ang. *sigmoid*), „iloraz szans” (ang. *odds ratio*), „regularyzacja” (ang. *regularization*), „drzewo decyzyjne”, „liść”, „las losowy” (ang. *random forest*), „próbki poza workiem” (ang. *out-of-bag*, OOB), „ważność cech” (ang. *feature importance*), „ważność permutacyjna” (ang. *permutation importance*), „wzmacnianie gradientowe” (ang. *gradient boosting*).
6. Odsyłacze wstecz: rozdział 7 (wszystkie strony), 3 (wykresy, style), 2 (`default_rng`, mediana), 5 (`to_markdown`); „Python Notatki” 5 (słowniki), 14. Zapowiedzi: 9 (regresja, `ColumnTransformer`, kodowanie), 10 (PCA dla cech skorelowanych — wzmianka), 11 (sieci) — `TODO`.
7. Domknięcia: 2 markery „rozdziału o klasyfikacji” (07/pierwszy-model, 07/przeuczenie) → `08-klasyfikacja/miary.md` i `index.md`.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty (wykresy) |
|---|---|---|
| `index.md` | Wprowadzenie / „8. Klasyfikacja” | cel; dane; wersje; ---; ## W tym rozdziale (4) |
| `miary.md` | Miary klasyfikacji | Dane — diagnoza nowotworu (`dane.py`); Macierz pomyłek (`macierz.py`; `macierz.png`); Precyzja, czułość i F1 (`miary.py`); Próg decyzyjny (`prog.py`; `prog.png`); Krzywa ROC i AUC (`roc.py`; `roc.png`); Klasy nierównoliczne (`nierownowaga.py`); Wiele klas (`wieloklasowo.py`; `wieloklasowo.png`) |
| `regresja-logistyczna.md` | Regresja logistyczna | Model liniowy dla klasyfikacji (`sigmoida.py`; `sigmoida.png`); Współczynniki i iloraz szans (`wspolczynniki.py`; `wspolczynniki.png`); Regularyzacja — parametr `C` (`regularyzacja.py`; `regularyzacja.png`); Wiele klas (`wiele-klas.py`); Kiedy model liniowy wystarcza (`granica-liniowa.py`; `granica-liniowa.png`) |
| `drzewa-i-lasy.md` | Drzewa decyzyjne i lasy losowe | Drzewo decyzyjne (`drzewo.py`; `drzewo.png`); Głębokość i przeuczenie (`glebokosc.py`); Ważność cech (`waznosc.py`); Las losowy (`las.py`; `las.png`); Wzmacnianie gradientowe (`boosting.py`) |
| `wybor-i-interpretacja.md` | Wybór modelu i interpretacja | Porównanie modeli (`porownanie.py`); Ważność permutacyjna (`permutacja.py`; `permutacja.png`); Analiza błędów (`bledy.py`); Próg pod koszt błędu (`koszt.py`); Model końcowy (`model-koncowy.py`); Lista kontrolna klasyfikacji; Dalej: regresja (TODO 9) |

Szacunek: 850–1000 linii; 9 wykresów.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 7)

```yaml
      - 8. Klasyfikacja:
          - Wprowadzenie: zastosowania/08-klasyfikacja/index.md
          - Miary klasyfikacji: zastosowania/08-klasyfikacja/miary.md
          - Regresja logistyczna: zastosowania/08-klasyfikacja/regresja-logistyczna.md
          - Drzewa decyzyjne i lasy losowe: zastosowania/08-klasyfikacja/drzewa-i-lasy.md
          - Wybór modelu i interpretacja: zastosowania/08-klasyfikacja/wybor-i-interpretacja.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `wybor-i-interpretacja.md` | regresja i przygotowanie danych | rozdział 9 |
| `wybor-i-interpretacja.md` | PCA dla cech skorelowanych | rozdział 10 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/07-ml-pojecia/pierwszy-model.md` | `08-klasyfikacja/miary.md` |
| `zastosowania/07-ml-pojecia/przeuczenie-i-ocena.md` | `08-klasyfikacja/index.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/`.

## Listy kontrolne

- Przed commitem: harness, `refresh_outputs.py`, `make_figures.py --img=`, oba buildy `--strict`, kotwice, cudzysłowy, kolokwializmy, trzy recenzje.
- Po commicie: domknięcia, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
