# Projekt rozdziału 11 części „Python Zastosowania” — PyTorch — tensory i sieć neuronowa

Piąty rozdział ścieżki Uczenie maszynowe. Branch: `content/zastosowania-11` (z `dev` po `52fb09b`). Realizacja autonomiczna na polecenie autora z 16 IX 2026.

## Decyzje redakcyjne (16 IX 2026)

1. **Zakres:** instalacja PyTorch i tensory (tworzenie, typy — `float32` domyślnie, wymiana z NumPy i pandas, działania i rozgłaszanie jak w rozdziale 2, urządzenie CPU/GPU); automatyczne różniczkowanie (`requires_grad`, `backward()`, `grad`, kumulacja gradientu, `no_grad()`, `detach()`), spadek gradientu w jednym wymiarze i regresja liniowa ręczną pętlą (zgodność z metodą najmniejszych kwadratów z rozdziału 2), `nn.MSELoss` i optymalizatory `SGD`/`Adam`; sieć neuronowa — `nn.Linear`, `nn.ReLU`, `nn.Sequential`, klasa dziedzicząca po `nn.Module`, funkcja straty `BCEWithLogitsLoss`, pętla treningowa, `TensorDataset`/`DataLoader`, moduł `trening.py` (`trenuj()`, `przewiduj()`, wczesne zatrzymanie), granica decyzyjna na półksiężycach z rozdziału 10; klasyfikacja obrazów — cyfry digits jako tensory, sieć w pełni połączona z `CrossEntropyLoss` i `softmax`, sieć splotowa (`Conv2d`, `MaxPool2d`, `Flatten`), błędy, zapis `state_dict` i wczytanie; trening w praktyce — regresja mieszkań siecią z przygotowaniem danych z rozdziału 9, przeuczenie i wczesne zatrzymanie, porównanie z modelem liniowym, hiperparametry i regularyzacja, GPU, kiedy PyTorch, lista kontrolna. Poza zakresem: torchvision i zbiory do pobrania (MNIST), sieci rekurencyjne i transformery, uczenie transferowe, autoenkodery, `torch.compile`.
2. **Dane:** `make_moons` i `load_digits` (rozdział 10), `mieszkania.csv` z rozdziału 9 — kopia w `docs/zastosowania/11-pytorch/pliki/` obok modułu `trening.py`; harness `--data=docs/zastosowania/11-pytorch/pliki`. Skrypty jednej strony działają w jednym katalogu (`cnn.py` zapisuje `cyfry.pt`, `zapis.py` go wczytuje).
3. **Środowisko:** `venv-ch11` — torch 2.14.0 (koło z PyPI dla Windows to wersja CPU, `torch.__version__` = `2.14.0+cpu`, ok. 550 MB; w Linuksie koło z PyPI zawiera CUDA — wersję CPU instaluje się z `--index-url https://download.pytorch.org/whl/cpu`), scikit-learn 1.9.1, pandas 3.0.5, NumPy 2.5.3, Matplotlib 3.11.2; Python 3.14.7. Plik wymagań: dopisany `torch==2.14.0`.
4. **Fakty sprawdzone 16 IX 2026:** `torch.tensor([1.0])` → `float32`, `torch.tensor([1])` → `int64`; `from_numpy` dzieli pamięć, `torch.tensor(tablica)` kopiuje; `manual_seed(42)` odtwarza `rand`; `x.grad` kumuluje się (8 → 16), `zero_()` zeruje; `numpy()` na tensorze z gradientem → `RuntimeError`; spadek gradientu na (x−2)²+1 z x=10: lr 0,5 → 2,0 dokładnie w 20 krokach, 0,1 i 0,9 → 2,09, 1,1 → rozbieżność (309); regresja powierzchnia→cena po standaryzacji: lr 0,1 → w = 0,8018 = korelacja (jak `lstsq`), lr 0,01 za wolno (strata 0,37 po 100 krokach), 1,0 oscyluje, 2,1 → NaN; SGD lr 0,1 to samo, Adam lr 0,1 → 0,8036; `nn.Linear(2, 1)` ma 3 parametry, MLP 2→16→16→1 — 337; półksiężyce: model liniowy dokładność 0,86/0,83 (sklearn 0,85), MLP 1,0/1,0; trening deterministyczny na CPU po `manual_seed` (dwa przebiegi identyczne); `DataLoader(shuffle=True)` losuje z generatora globalnego w chwili iteracji; digits (podział 75/25, warstwa 64→64→10, Adam lr 0,003, 30 epok, porcje 32): MLP 4810 parametrów, test ≈ 0,97; CNN 8/16 filtrów 1898 parametrów, test ≈ 0,98; regresja logistyczna sklearn 0,962; `state_dict` CNN ≈ 10 kB; `torch.load` domyślnie `weights_only=True`; mieszkania (240/60/100): MLP 12→32→32→1 z wczesnym zatrzymaniem MAE test 56–62 tys. zależnie od hiperparametrów, bez zatrzymania strata walidacyjna rośnie od epoki ≈ 21; model liniowy w PyTorch MAE test 47,6 tys. (sklearn 48,1 tys.) — sieć na 240 wierszach przegrywa z modelem liniowym z dobrymi cechami.
5. **Terminy:** „tensor”, „automatyczne różniczkowanie” (ang. *automatic differentiation*, autograd), „gradient”, „spadek gradientu” (ang. *gradient descent*), „współczynnik uczenia” (ang. *learning rate*), „funkcja straty” (ang. *loss function*), „optymalizator”, „epoka” (ang. *epoch*), „porcja” (ang. *batch*), „sieć neuronowa” (ang. *neural network*), „warstwa w pełni połączona” (ang. *fully connected*, *linear layer*), „funkcja aktywacji” (ang. *activation function*), „ReLU”, „logit”, „softmax”, „entropia krzyżowa” (ang. *cross-entropy*), „sieć splotowa” (ang. *convolutional neural network*, CNN), „filtr / jądro” (ang. *kernel*), „łączenie” (ang. *pooling*), „wczesne zatrzymanie” (ang. *early stopping*), „porzucanie” (ang. *dropout*), „wagi” (ang. *weights*), „słownik stanu” (`state_dict`).
6. Odsyłacze wstecz: rozdział 2 (rozgłaszanie, najmniejsze kwadraty), 7 (podział, przeuczenie, powtarzalność, zapis modelu), 8 (regresja logistyczna, funkcja logistyczna), 9 (przygotowanie danych, model liniowy na logarytmach), 10 (półksiężyce, digits); „Python Notatki” 10–11 (klasy, dziedziczenie). Zapowiedzi: 12 (projekt) — `TODO`.
7. Domknięcia: marker „rozdziału o PyTorch” (10/obserwacje-nietypowe) → `11-pytorch/index.md`; marker „rozdziału 11” (07/przeuczenie) → `11-pytorch/index.md`.

## Podział na strony

| Plik | Etykieta nav / H1 | Sekcje H2 i skrypty (wykresy) |
|---|---|---|
| `index.md` | Wprowadzenie / „11. PyTorch — tensory i sieć neuronowa” | cel; dane i pliki; instalacja i wersje (`requirements.txt`, terminal); ---; ## W tym rozdziale (5) |
| `tensory.md` | Tensory | Sprawdzenie instalacji (`sprawdzenie.py`); Tworzenie tensorów (`tensory.py`); Tensory a NumPy i pandas (`numpy-most.py`); Działania i rozgłaszanie (`dzialania.py`); Urządzenie (`urzadzenie.py`) |
| `autograd.md` | Automatyczne różniczkowanie | Gradient (`gradient.py`); Spadek gradientu (`spadek.py`; `spadek.png`); Regresja liniowa pętlą (`regresja-gradient.py`; `strata.png`); Funkcja straty i optymalizator (`optymalizator.py`) |
| `siec.md` | Sieć neuronowa | Warstwy i `nn.Sequential` (`warstwy.py`); Pętla treningowa (`petla.py`); Porcje danych — `DataLoader` (`porcje.py`); Moduł `trening.py` (plik); Granica decyzyjna (`granica.py`; `granica.png`) |
| `cyfry.md` | Klasyfikacja obrazów | Obrazy jako tensory (`dane-cyfry.py`; `cyfry.png`); Sieć w pełni połączona (`mlp-cyfry.py`; `mlp-cyfry.png`); Sieć splotowa (`cnn.py`; `bledy-cyfry.png`); Zapis i wczytanie modelu (`zapis.py`) |
| `praktyka.md` | Trening w praktyce | Regresja — mieszkania (`mieszkania-siec.py`; `wczesne-zatrzymanie.png`); Hiperparametry i regularyzacja (`regularyzacja.py`); GPU i większe dane; Kiedy PyTorch; Lista kontrolna treningu sieci; Dalej: projekt (TODO 12) |

Szacunek: 950–1100 linii; 7 wykresów.

## Blok nawigacji (`mkdocs.yml`, po rozdziale 10)

```yaml
      - 11. PyTorch — tensory i sieć neuronowa:
          - Wprowadzenie: zastosowania/11-pytorch/index.md
          - Tensory: zastosowania/11-pytorch/tensory.md
          - Automatyczne różniczkowanie: zastosowania/11-pytorch/autograd.md
          - Sieć neuronowa: zastosowania/11-pytorch/siec.md
          - Klasyfikacja obrazów: zastosowania/11-pytorch/cyfry.md
          - Trening w praktyce: zastosowania/11-pytorch/praktyka.md
```

## Zapowiedzi w przód

| Strona | Temat | Cel |
|---|---|---|
| `praktyka.md` | projekt: od danych do modelu | rozdział 12 |

## Domknięcia

| Plik | Cel |
|---|---|
| `zastosowania/10-bez-nadzoru/obserwacje-nietypowe.md` | `11-pytorch/index.md` |
| `zastosowania/07-ml-pojecia/przeuczenie-i-ocena.md` | `11-pytorch/index.md` |

## CONTENT HANDOFF

Brak odpowiednika w `sources/`.

## Listy kontrolne

- Przed commitem: harness z `--data=docs/zastosowania/11-pytorch/pliki` i interpreterem `venv-ch11`; `refresh_outputs.py`; `make_figures.py --img= --data=`; dwa przebiegi weryfikacji (determinizm); oba buildy `--strict`; kotwice; cudzysłowy; kolokwializmy; recenzje z weryfikacją uwag.
- Po commicie: domknięcia, status w `PLAN_ZASTOSOWANIA.md`, integracja do `dev`, pamięć, raport.
