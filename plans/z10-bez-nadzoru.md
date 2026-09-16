# Projekt rozdziału 10 części „Python Zastosowania” — Uczenie bez nadzoru

Czwarty rozdział ścieżki Uczenie maszynowe. Branch: `content/zastosowania-10` (z `dev` po `42af40f`). Realizacja autonomiczna na polecenie autora z 16 IX 2026.

## Decyzje redakcyjne (16 IX 2026)

1. **Zakres:** grupowanie — algorytm k-średnich krok po kroku w NumPy (rozgłaszanie z rozdziału 2), `KMeans` (skalowanie, `n_init`, `inertia_`, `predict`), dobór liczby grup (łokieć, sylwetka), profile grup jako segmenty, kształt grup — `DBSCAN` i `eps`; redukcja wymiaru — `PCA` (wariancja wyjaśniona, wykres osypiska, rzut na dwie składowe, ładunki, związek z `np.linalg.eigh` z rozdziału 2, konieczność skalowania), PCA w potoku jako lekarstwo na cechy skorelowane z rozdziału 8 (składowe nieskorelowane, ważność permutacyjna składowych), wizualizacja t-SNE (tylko do oglądania, bez `transform`); obserwacje nietypowe — błędy wstrzyknięte do danych, reguła statystyczna (mediana i MAD, zakres), `IsolationForest` (`score_samples`, `contamination`, braki dozwolone), `LocalOutlierFactor` (współczynnik, `novelty=True`), porównanie metod; kiedy uczenie bez nadzoru; lista kontrolna. Poza zakresem: grupowanie hierarchiczne z dendrogramem (wzmianka o `AgglomerativeClustering`), UMAP (pakiet zewnętrzny), modele mieszanin gaussowskich, autoenkodery (rozdział 11 sieci).
2. **Dane:** `load_wine` (178 × 13, trzy odmiany — etykiety ukrywamy przed modelem i używamy tylko do oceny), `make_moons` (kształt grup), `load_breast_cancer` (30 cech skorelowanych z rozdziału 8), `load_digits` (1797 × 64, t-SNE), `mieszkania.csv` z rozdziału 9 (link do `../09-regresja/dane/mieszkania.csv`; skrypt `bledy.py` dopisuje trzy błędne wiersze i zapisuje `mieszkania-bledy.csv`). Harness: `--data=docs/zastosowania/09-regresja/dane`.
3. **Środowisko:** scikit-learn 1.9.1 (jak rozdziały 7–9); bez zmian w pliku wymagań.
4. **Fakty sprawdzone 16 IX 2026:** k-średnich ręcznie na 2 cechach zbiega w 6 krokach, inercja 102,65 wobec 101,96 dla `n_init=10` (inne minimum lokalne, ARI 0,93 między nimi); pełne 13 cech po skalowaniu: ARI 0,90 z odmianami, tabela krzyżowa prawie przekątniowa; bez skalowania ARI 0,37 (dominuje `proline`, odchylenie 315); inercja maleje bez wyraźnego łokcia (2314, 1659, 1278, 1175, …), sylwetka największa dla k = 3 (0,285); profile grup: grupa niskich flawonoidów i wysokiej intensywności barwy, grupa wysokiej proliny; `make_moons` (300, szum 0,08): k-średnich ARI 0,26, `DBSCAN(eps=0.2)` ARI 1,0, `eps=0.1` → 19 grup i 60 szumu; PCA wine: 36,2% + 19,2% + 11,1%, 10 składowych do 95%; ładunki PC1: flawonoidy 0,42, fenole 0,39, OD280 0,38 wobec fenole nieflawonoidowe −0,30; PC2: intensywność barwy 0,53, alkohol 0,48; `eigh` kowariancji daje te same wartości (4,732, 2,511, 1,454) co `explained_variance_`; bez skalowania PC1 = 99,8% (`proline`); breast cancer: AUC CV regresji logistycznej po PCA — 1 składowa 0,963, 2 → 0,987, 5 → 0,993, 30 → 0,991; 5 składowych = 84,9% wariancji, korelacje między składowymi 0; ważność permutacyjna PC1 0,46 ± 0,04, PC2 0,03, reszta ≈ 0; digits: PCA 2D 28,5% wariancji, kNN na 2D — PCA 0,60, t-SNE 0,98; `TSNE` bez `transform`, `perplexity=30`; anomalie: `IsolationForest` przyjmuje `NaN`, `contamination="auto"` flaguje 95 z 403; wstrzyknięte błędy — cena ×10 (z-score ceny za metr 34,9; LOF 2D 15,1, ranga 1), 5 pokoi na 28 m² (LOF na powierzchnia/pokoje/cena ranga 2, z-score niewidoczny), rok 2091 (zakres; LOF nie przyjmuje `NaN`); las izolacji stawia najwyżej duże 5-pokojowe mieszkania — rzadkie, nie błędne.
5. **Terminy:** „uczenie bez nadzoru” (ang. *unsupervised learning*), „grupowanie” (ang. *clustering*), „algorytm k-średnich” (ang. *k-means*), „środek grupy” (ang. *centroid*), „inercja” (ang. *inertia*), „sylwetka” (ang. *silhouette*), „skorygowany indeks Randa” (ang. *adjusted Rand index*, ARI), „grupowanie gęstościowe” (DBSCAN), „redukcja wymiaru” (ang. *dimensionality reduction*), „analiza głównych składowych” (ang. *principal component analysis*, PCA), „wariancja wyjaśniona” (ang. *explained variance*), „ładunki” (ang. *loadings*), „wykres osypiska” (ang. *scree plot*), „t-SNE”, „obserwacja nietypowa / anomalia” (ang. *outlier*, *anomaly*), „las izolacji” (ang. *isolation forest*), „lokalny współczynnik odstawania” (ang. *local outlier factor*, LOF), „wykrywanie nowości” (ang. *novelty detection*).
6. Odsyłacze wstecz: rozdział 2 (rozgłaszanie i macierz odległości, `eigh` kowariancji), 3 (wykresy), 5 (grupowanie w pandas), 6 (wartości odstające w projekcie), 7 (skalowanie, potok, walidacja), 8 (breast cancer, cechy skorelowane, ważność permutacyjna, wine), 9 (mieszkania, `FunctionTransformer`, imputacja). Zapowiedzi: 11 (sieci neuronowe, autoenkodery) — `TODO`.
7. Domknięcia: markery „uczeniu bez nadzoru” (02/algebra ×2, 08/wybor, 09/modele-nieliniowe) → `10-bez-nadzoru/`; marker „linki 10–11” (07/przeuczenie) częściowo (10).

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty (wykresy) |
|---|---|---|
| `index.md` | Wprowadzenie / „10. Uczenie bez nadzoru” | cel; dane; wersje; ---; ## W tym rozdziale (3) |
| `grupowanie.md` | Grupowanie | Algorytm k-średnich krok po kroku (`krok.py`; `krok.png`); `KMeans` na wszystkich cechach (`kmeans.py`); Liczba grup (`liczba-grup.py`; `liczba-grup.png`); Profile grup (`profile.py`; `profile.png`); Kształt grup — DBSCAN (`ksztalt.py`; `ksztalt.png`) |
| `redukcja-wymiaru.md` | Redukcja wymiaru | Analiza głównych składowych (`pca.py`; `pca.png`); Składowe i skalowanie (`skladowe.py`); PCA w potoku — cechy skorelowane (`pca-potok.py`); Wizualizacja — t-SNE (`tsne.py`; `tsne.png`) |
| `obserwacje-nietypowe.md` | Obserwacje nietypowe | Błędy do wykrycia (`bledy.py`); Reguła statystyczna (`regula.py`); Las izolacji (`izolacja.py`; `izolacja.png`); Lokalny współczynnik odstawania (`lof.py`; `lof.png`); Kiedy uczenie bez nadzoru; Lista kontrolna uczenia bez nadzoru; Dalej: sieci neuronowe (TODO 11) |

Szacunek: 650–750 linii; 7 wykresów.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 9)

```yaml
      - 10. Uczenie bez nadzoru:
          - Wprowadzenie: zastosowania/10-bez-nadzoru/index.md
          - Grupowanie: zastosowania/10-bez-nadzoru/grupowanie.md
          - Redukcja wymiaru: zastosowania/10-bez-nadzoru/redukcja-wymiaru.md
          - Obserwacje nietypowe: zastosowania/10-bez-nadzoru/obserwacje-nietypowe.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `obserwacje-nietypowe.md` | sieci neuronowe w PyTorch | rozdział 11 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/02-numpy/algebra-liniowa.md` (PCA) | `10-bez-nadzoru/redukcja-wymiaru.md` |
| `zastosowania/02-numpy/algebra-liniowa.md` (macierz odległości) | `10-bez-nadzoru/grupowanie.md` |
| `zastosowania/07-ml-pojecia/przeuczenie-i-ocena.md` | `10-bez-nadzoru/index.md` (marker zostaje dla 11) |
| `zastosowania/08-klasyfikacja/wybor-i-interpretacja.md` | `10-bez-nadzoru/redukcja-wymiaru.md#pca-w-potoku-cechy-skorelowane` |
| `zastosowania/09-regresja/modele-nieliniowe.md` | `10-bez-nadzoru/index.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/`.

## Listy kontrolne

- Przed commitem: harness z `--data=docs/zastosowania/09-regresja/dane`; `refresh_outputs.py`; `make_figures.py --img= --data=`; oba buildy `--strict`; kotwice; cudzysłowy; kolokwializmy; recenzje z weryfikacją uwag.
- Po commicie: domknięcia, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
