# Warsztat scikit-learn

Siłą scikit-learn jest jednolitość: każdy model, od najbliższych sąsiadów po lasy losowe, ma te same metody, każde przekształcenie danych ten sam interfejs, a potok łączy jedno z drugim w obiekt, który trenuje się, ocenia i zapisuje jak pojedynczy model. Ten podrozdział pokazuje ten wspólny szkielet — w rozdziałach 8–10 zmienią się tylko modele, a szkielet pozostanie ten sam.

## Estymator — jeden interfejs

```python title="estymator.py"
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

iris = load_iris(as_frame=True)
X_trening, X_test, y_trening, y_test = train_test_split(iris.data, iris.target, test_size=0.25, random_state=42, stratify=iris.target)
modele = {"sąsiedzi": KNeighborsClassifier(n_neighbors=5), "drzewo": DecisionTreeClassifier(max_depth=3, random_state=42), "regresja logistyczna": LogisticRegression(max_iter=1000)}
for nazwa, model in modele.items():
    model.fit(X_trening, y_trening)
    print(f"{nazwa:<22}{model.score(X_test, y_test):.3f}")
model = modele["sąsiedzi"]
print(model.get_params())
print(round(model.set_params(n_neighbors=7).fit(X_trening, y_trening).score(X_test, y_test), 3))
print([atrybut for atrybut in dir(model) if atrybut.endswith("_") and not atrybut.startswith("_")])
```

```{ .text .no-copy }
sąsiedzi              0.974
drzewo                0.895
regresja logistyczna  0.947
{'algorithm': 'auto', 'leaf_size': 30, 'metric': 'minkowski', 'metric_params': None, 'n_jobs': None, 'n_neighbors': 5, 'p': 2, 'weights': 'uniform'}
0.947
['classes_', 'effective_metric_', 'effective_metric_params_', 'feature_names_in_', 'n_features_in_', 'n_samples_fit_', 'outputs_2d_']
```

Każdy model w scikit-learn jest **estymatorem** (ang. *estimator*): obiektem z metodami `fit(X, y)`, `predict(X)` i `score(X, y)`, więc trzy różne algorytmy trenujemy i oceniamy tą samą pętlą, bez zmiany kodu. Hiperparametry podajemy w konstruktorze i odczytujemy przez `get_params()` — słownik, z którym pracują narzędzia doboru z dalszych sekcji tego podrozdziału — a `set_params()` zmienia je na istniejącym obiekcie. Atrybuty z podkreśleniem z poprzedniego podrozdziału w innych modelach obejmują współczynniki `coef_` czy strukturę drzewa `tree_`. Modele z tego listingu omawiają rozdziały 8 i 9; tu są tylko dowodem wspólnego interfejsu.

## Transformatory i potok

```python title="potok.py"
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

iris = load_iris(as_frame=True)
X_trening, X_test, y_trening, y_test = train_test_split(iris.data, iris.target, test_size=0.25, random_state=42, stratify=iris.target)
skaler = StandardScaler().fit(X_trening)
print(skaler.mean_.round(2), skaler.scale_.round(2))
print(skaler.transform(X_test.head(2)).round(2))

potok = Pipeline([("skalowanie", StandardScaler()), ("model", KNeighborsClassifier(n_neighbors=5))])
potok.set_output(transform="pandas")
potok.fit(X_trening, y_trening)
print(round(potok.score(X_test, y_test), 3), round(KNeighborsClassifier(n_neighbors=5).fit(X_trening, y_trening).score(X_test, y_test), 3))
print(potok.named_steps["skalowanie"].mean_.round(2))
print(potok[:-1].transform(X_test.head(2)).round(2))
print(potok.get_params()["model__n_neighbors"])
```

```{ .text .no-copy }
[5.88 3.07 3.76 1.19] [0.85 0.44 1.78 0.77]
[[-1.74  0.3  -1.39 -1.3 ]
 [ 0.5   0.53  0.53  0.53]]
0.921 0.974
[5.88 3.07 3.76 1.19]
    sepal length (cm)  sepal width (cm)  petal length (cm)  petal width (cm)
42              -1.74              0.30              -1.39             -1.30
56               0.50              0.53               0.53              0.53
5
```

**Transformator** (ang. *transformer*) to estymator, który zamiast przewidywać przekształca cechy: `fit()` uczy się parametrów przekształcenia — `StandardScaler` średniej i odchylenia każdej cechy — a `transform()` je stosuje. Skalowanie do średniej 0 i odchylenia 1 ma znaczenie dla modeli opartych na odległości, jak KNN, gdy cechy mają różne jednostki; dla iris, gdzie wszystkie są w centymetrach, w tym podziale wynik nawet nieco spada — skalowanie nie zawsze pomaga. **Potok** (ang. *pipeline*) łączy transformatory i model w jeden estymator: `fit()` potoku trenuje skaler na zbiorze treningowym i przekazuje przekształcone cechy modelowi, `predict()` powtarza przekształcenie na nowych danych — z parametrami z treningu, nigdy z danych testowych. `set_output(transform="pandas")` każe transformatorom zwracać ramki z nazwami kolumn zamiast tablic, a nazwa kroku z dwoma podkreśleniami (`model__n_neighbors`) adresuje hiperparametr wewnątrz potoku.

## Walidacja krzyżowa

```python title="walidacja.py"
from sklearn.datasets import load_iris
from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_validate
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

iris = load_iris(as_frame=True)
X, y = iris.data, iris.target
potok = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5))
podzialy = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
wyniki = cross_val_score(potok, X, y, cv=podzialy)
print(wyniki.round(3), f"{wyniki.mean():.3f} ± {wyniki.std():.3f}")
for k in (1, 5, 15, 45):
    wyniki = cross_val_score(make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k)), X, y, cv=podzialy)
    print(k, f"{wyniki.mean():.3f} ± {wyniki.std():.3f}")
szczegoly = cross_validate(potok, X, y, cv=podzialy, return_train_score=True)
print(list(szczegoly), szczegoly["train_score"].mean().round(3), szczegoly["test_score"].mean().round(3))
```

```{ .text .no-copy }
[1.    0.967 0.933 1.    0.967] 0.973 ± 0.025
1 0.933 ± 0.060
5 0.973 ± 0.025
15 0.953 ± 0.045
45 0.867 ± 0.087
['fit_time', 'score_time', 'test_score', 'train_score'] 0.963 0.973
```

Jeden podział na trening i test daje jedną liczbę, która zależy od losowania — inny `random_state`, inny wynik. **Walidacja krzyżowa** (ang. *cross-validation*) dzieli dane na kilka części (tu pięć, `n_splits=5`), trenuje tyle razy, ile jest części, za każdym razem z inną częścią jako walidacyjną, i zwraca tyle samo wyników; ich średnia jest stabilniejszą oceną, a odchylenie mówi, jak bardzo wynik zależy od podziału. `StratifiedKFold` zachowuje proporcje klas w każdej części, `shuffle=True` z ziarnem miesza dane przed podziałem; `cross_val_score()` przyjmuje estymator — tu cały potok, więc skalowanie za każdym razem uczy się tylko na części treningowej — a `cross_validate()` zwraca też wynik na treningu i czasy. Porównanie kilku wartości `k` w pętli to najprostszy dobór hiperparametru — tu na całym zbiorze, bo walidacja krzyżowa zastępuje pojedynczy podział; gdy wybrany model ma być jeszcze oceniony, zbiór testowy odkładamy wcześniej, jak w następnej sekcji, która przeprowadza dobór systematycznie.

## Dobór hiperparametrów — `GridSearchCV`

```python title="siatka.py"
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

iris = load_iris(as_frame=True)
X_trening, X_test, y_trening, y_test = train_test_split(iris.data, iris.target, test_size=0.25, random_state=42, stratify=iris.target)
potok = Pipeline([("skalowanie", StandardScaler()), ("model", KNeighborsClassifier())])
siatka = GridSearchCV(potok, param_grid={"model__n_neighbors": [1, 3, 5, 7, 9, 11, 15, 21], "model__weights": ["uniform", "distance"]}, cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42))
siatka.fit(X_trening, y_trening)
print(siatka.best_params_, round(siatka.best_score_, 3))
wyniki = pd.DataFrame(siatka.cv_results_)
print(wyniki[["param_model__n_neighbors", "param_model__weights", "mean_test_score", "std_test_score", "rank_test_score"]].sort_values("rank_test_score").head(5).round(3).to_string(index=False))
print(type(siatka.best_estimator_).__name__, round(siatka.score(X_test, y_test), 3))
```

```{ .text .no-copy }
{'model__n_neighbors': 21, 'model__weights': 'distance'} 0.982
 param_model__n_neighbors param_model__weights  mean_test_score  std_test_score  rank_test_score
                       21             distance            0.982           0.022                1
                        3             distance            0.973           0.022                2
                        3              uniform            0.973           0.022                2
                        7              uniform            0.965           0.051                4
                        7             distance            0.965           0.051                4
Pipeline 0.947
```

`GridSearchCV` łączy siatkę wartości hiperparametrów z walidacją krzyżową: dla każdej kombinacji liczy średni wynik, wybiera najlepszą i trenuje na niej model na całym zbiorze treningowym — `best_estimator_`, którego używa `predict()` i `score()` obiektu siatki. Dobór odbywa się **wyłącznie na zbiorze treningowym** (walidacja krzyżowa dzieli go wewnętrznie); zbiór testowy służy dopiero do końcowej oceny wybranego modelu, a jego wynik bywa niższy od najlepszego wyniku walidacji, bo ten ostatni jest wybrany spośród wielu prób. Drugi hiperparametr, `weights="distance"`, waży głosy sąsiadów odwrotnie proporcjonalnie do odległości zamiast liczyć je równo (`"uniform"`). Tabela `cv_results_` pokazuje wszystkie kombinacje z odchyleniem — różnice mniejsze od odchylenia nie są rozstrzygające, więc z kilku równie dobrych wartości wybieramy prostszą: `score()` siatki użył wyboru automatycznego, a kierując się tą zasadą, wybralibyśmy `k = 3` z równymi wagami — ten wariant zapisujemy w następnej sekcji.

## Zapis i wczytanie modelu

```python title="zapis-modelu.py"
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.datasets import load_iris
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

iris = load_iris(as_frame=True)
potok = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=3)).fit(iris.data, iris.target)
joblib.dump({"model": potok, "wersja_sklearn": sklearn.__version__, "klasy": iris.target_names.tolist()}, "model-iris.joblib")
print(Path("model-iris.joblib").stat().st_size // 1000, "kB")

wczytany = joblib.load("model-iris.joblib")
print(wczytany["wersja_sklearn"], wczytany["klasy"])
nowe = pd.DataFrame([[5.0, 3.4, 1.5, 0.2]], columns=iris.data.columns)
print(wczytany["model"].predict(nowe), wczytany["model"][-1].n_neighbors)
```

```{ .text .no-copy }
15 kB
1.9.1 ['setosa', 'versicolor', 'virginica']
[0] 3
```

Wytrenowany potok zapisujemy przez `joblib.dump()` — biblioteka joblib, zależność scikit-learn, serializuje obiekty Pythona z dużymi tablicami sprawniej niż `pickle` z rozdziału 9 „Python Notatki” i ma te same ograniczenia: plik wczytujemy tylko z zaufanego źródła i tą samą wersją biblioteki, bo model z innej wersji może się nie wczytać albo liczyć inaczej. Dlatego obok modelu zapisujemy wersję scikit-learn i nazwy klas; słownik jest wygodniejszy niż sam estymator. Wczytany potok przewiduje bez ponownego treningu — tak model trafia do skryptu lub aplikacji, która go używa.

## Powtarzalność

Trzy źródła losowości w tym podrozdziale — podział na zbiory, mieszanie w walidacji krzyżowej i losowość niektórych modeli (drzewa, lasy, sieci) — mają jeden środek: argument `random_state=` z liczbą całkowitą. Bez niego każdy przebieg daje inne liczby, a różnice między modelami stają się nieodróżnialne od różnic wynikających z losowania; z nim wyniki w tej książce odtwarzają się co do cyfry. Ziarno ustala powtarzalność, nie jakość: model, który wypada dobrze tylko dla jednego ziarna, jest słaby — dlatego wnioski opieramy na walidacji krzyżowej, nie na jednym podziale.
