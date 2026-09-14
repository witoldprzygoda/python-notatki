# Projekt rozdziału 9 części „Python Zastosowania” — Regresja i przygotowanie danych

Trzeci rozdział ścieżki Uczenie maszynowe. Branch: `content/zastosowania-09` (z `dev` po `30314d2`). Realizacja autonomiczna na polecenie autora z 14 IX 2026.

## Decyzje redakcyjne (14 IX 2026)

1. **Zakres:** regresja liniowa i miary błędu (MAE, RMSE, R², MAPE, `DummyRegressor`, reszty); przygotowanie danych — typy kolumn, `OneHotEncoder` (z `drop="first"` dla modelu liniowego, `handle_unknown`), `OrdinalEncoder` z jawną kolejnością, `SimpleImputer` (`add_indicator`), `ColumnTransformer` z `set_output(transform="pandas")` i `get_feature_names_out()`, potok, wyciek celu (cecha wyliczona z etykiety); regularyzacja i inżynieria cech — `PolynomialFeatures`, `Ridge` (krzywa walidacji `alpha`), `Lasso` jako selekcja, transformacja celu `TransformedTargetRegressor` z logarytmem; modele nieliniowe — `DecisionTreeRegressor` (krzywa głębokości), `RandomForestRegressor`, `HistGradientBoostingRegressor` (natywne kategorie i braki), porównanie CV, ważność permutacyjna, model końcowy, lista kontrolna regresji. Poza zakresem: przedziały predykcji (kwantylowe HGB pokrywały 51% zamiast 80% — pominięte), SVR, GAM, szeregi czasowe jako regresja. Zapowiedź rozdziału 10 (`TODO`).
2. **Dane:** `mieszkania.csv` — 400 ofert mieszkań w Krakowie generowanych skryptem `generuj_mieszkania.py` (ziarno 42): `dzielnica` (5 kategorii), `powierzchnia`, `pokoje`, `pietro`, `rok_budowy` (8% braków), `stan` (porządkowa: do remontu / dobry / po remoncie, 4% braków), `winda` (bool), `odleglosc_km`, `cena` (prawoskośna, mediana 605 tys.). Plik w `docs/zastosowania/09-regresja/dane/`; harness `--data=`.
3. **Środowisko:** scikit-learn 1.9.1 (jak rozdziały 7–8).
4. **Fakty sprawdzone 14 IX 2026:** podział 300/100; bazowy MAE 219 tys.; liniowa na 4 cechach liczbowych MAE 88 tys., R² 0,83, MAPE 14,5%; pełny potok liniowy MAE ≈ 68 tys., R² 0,89 (CV); log celu dla modelu liniowego nie poprawia MAE (68 tys.) i obniża R² (0,85); Ridge/Lasso na 13 cechach bez zysku; wielomian 2. stopnia → ~100 cech; Lasso zeruje cechy przy rosnącym `alpha`; wyciek `cena_za_m2` → R² 0,95; drzewo: głębokość 4 najlepsza (MAE 94 tys.), pełne przeuczone (trening 0); las MAE 72 tys.; HGB 66 tys., z logarytmem celu 61 tys. (R² 0,90) — najlepszy; HGB natywnie z `category` 65 tys.; ważność permutacyjna: powierzchnia dominuje; `OneHotEncoder(drop="first", handle_unknown="ignore")` dozwolone; `root_mean_squared_error` w `metrics`.
   **Po recenzji (14 IX 2026):** zawyżanie cen dużych mieszkań w modelu na log(cena) wynika z liniowej powierzchni; model liniowy na logarytmach ceny i powierzchni (`FunctionTransformer(np.log)`) ma CV MAE 53 tys., R² 0,93 i jest modelem końcowym (test MAE 48 tys., MAPE 7,5%); lasso wybierane walidacją krzyżową, nie testem.
5. **Terminy:** „regresja liniowa”, „średni błąd bezwzględny” (ang. *mean absolute error*, MAE), „pierwiastek błędu średniokwadratowego” (ang. *root mean squared error*, RMSE), „współczynnik determinacji” (R²), „reszta” (ang. *residual*), „kodowanie zero-jedynkowe” (ang. *one-hot encoding*), „kodowanie porządkowe” (ang. *ordinal encoding*), „imputacja” (ang. *imputation*), „transformator kolumn”, „inżynieria cech” (ang. *feature engineering*), „cechy wielomianowe”, „regularyzacja grzbietowa / lasso” (ang. *ridge*, *lasso*), „transformacja celu”, „wyciek celu” (ang. *target leakage*).
6. Odsyłacze wstecz: rozdziały 2 (najmniejsze kwadraty, R²), 4 (typy, braki, `category`), 6 (czyszczenie), 7 (potok, walidacja, wyciek), 8 (regularyzacja `C`, drzewa i lasy, ważność permutacyjna). Zapowiedzi: 10 (PCA dla cech skorelowanych), 12 (projekt).
7. Domknięcia: markery „regresji i przygotowaniu danych” (07/pojecia, 07/przeuczenie, 08/regresja-logistyczna, 08/wybor) → `09-regresja/`; marker „linki 9–11” (07/przeuczenie) częściowo (9).

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty (wykresy) |
|---|---|---|
| `index.md` | Wprowadzenie / „9. Regresja i przygotowanie danych” | cel; dane; wersje; ---; ## W tym rozdziale (4) |
| `regresja-liniowa.md` | Regresja liniowa i miary błędu | Dane — ceny mieszkań (`generuj_mieszkania.py`, `ogledziny.py`; `rozklad.png`); Miary błędu (`miary.py`); Regresja liniowa na cechach liczbowych (`liniowa.py`); Reszty (`reszty.py`; `reszty.png`) |
| `przygotowanie-danych.md` | Przygotowanie danych | Typy kolumn (`typy.py`); Kodowanie kategorii (`kodowanie.py`); Braki — imputacja (`imputacja.py`); `ColumnTransformer` i potok (`transformator.py`); Współczynniki po kodowaniu (`wspolczynniki.py`; `wspolczynniki.png`); Wyciek celu (`wyciek-celu.py`) |
| `regularyzacja-i-cechy.md` | Regularyzacja i inżynieria cech | Cechy wielomianowe (`wielomian.py`); Regresja grzbietowa — `alpha` (`ridge.py`; `alfa.png`); Lasso jako selekcja cech (`lasso.py`); Transformacja celu (`log-celu.py`; `log-celu.png`) |
| `modele-nieliniowe.md` | Modele nieliniowe i wybór | Drzewo regresji (`drzewo.py`; `drzewo.png`); Las i wzmacnianie gradientowe (`zespoly.py`); Porównanie modeli (`porownanie.py`); Ważność permutacyjna (`waznosc.py`; `waznosc.png`); Model końcowy (`model-koncowy.py`); Lista kontrolna regresji; Dalej: uczenie bez nadzoru (TODO 10) |

Szacunek: 850–1000 linii; 7 wykresów.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 8)

```yaml
      - 9. Regresja i przygotowanie danych:
          - Wprowadzenie: zastosowania/09-regresja/index.md
          - Regresja liniowa i miary błędu: zastosowania/09-regresja/regresja-liniowa.md
          - Przygotowanie danych: zastosowania/09-regresja/przygotowanie-danych.md
          - Regularyzacja i inżynieria cech: zastosowania/09-regresja/regularyzacja-i-cechy.md
          - Modele nieliniowe i wybór: zastosowania/09-regresja/modele-nieliniowe.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `modele-nieliniowe.md` | uczenie bez nadzoru (PCA, grupowanie) | rozdział 10 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/07-ml-pojecia/pojecia.md` | `09-regresja/przygotowanie-danych.md` |
| `zastosowania/07-ml-pojecia/przeuczenie-i-ocena.md` (×2) | `09-regresja/przygotowanie-danych.md#wyciek-celu`, `09-regresja/index.md` |
| `zastosowania/08-klasyfikacja/regresja-logistyczna.md` | `09-regresja/regularyzacja-i-cechy.md` |
| `zastosowania/08-klasyfikacja/wybor-i-interpretacja.md` | `09-regresja/index.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/`.

## Listy kontrolne

- Przed commitem: plik danych z generatora do `dane/`; harness z `--data=`; `refresh_outputs.py`; `make_figures.py --img= --data=`; oba buildy `--strict`; kotwice; cudzysłowy; kolokwializmy; trzy recenzje.
- Po commicie: domknięcia, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
