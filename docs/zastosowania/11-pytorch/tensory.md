# Tensory

**Tensor** to tablica wielowymiarowa PyTorch — odpowiednik `ndarray` z rozdziału 2, z tym samym pojęciem kształtu, osi, typu elementów i rozgłaszania. Różnią go dwie rzeczy, dla których PyTorch istnieje: tensor pamięta, jak został policzony, co pozwala wyznaczyć gradient (następny podrozdział), i może leżeć w pamięci karty graficznej. Ten podrozdział przenosi nawyki z NumPy na tensory i wskazuje różnice.

## Sprawdzenie instalacji

```python title="sprawdzenie.py"
import torch

print(torch.__version__)
print(torch.cuda.is_available(), torch.get_default_dtype())
```

```{ .text .no-copy }
2.14.0+cpu
False torch.float32
```

Przyrostek `+cpu` oznacza wersję na procesor; `torch.cuda.is_available()` mówi, czy ta instalacja PyTorch może liczyć na karcie NVIDIA — w wersji `+cpu` zwraca `False` także na komputerze z taką kartą. Domyślny typ liczb zmiennoprzecinkowych to `float32`, nie `float64` jak w NumPy: sieciom neuronowym pojedyncza precyzja wystarcza, a zajmuje o połowę mniej pamięci i liczy się szybciej.

## Tworzenie tensorów

```python title="tensory.py"
import torch

t = torch.tensor([[1.0, 2.0], [3.0, 4.0]])
print(t)
print(t.dtype, t.shape, t.ndim, t.device)
print(torch.tensor([1, 2, 3]).dtype, torch.tensor([True, False]).dtype)
print(torch.zeros(2, 3).shape, torch.arange(5), torch.linspace(0, 1, 5))
torch.manual_seed(42)
losowe = torch.rand(2, 3)
print(losowe)
torch.manual_seed(42)
print(torch.equal(losowe, torch.rand(2, 3)))
print(t[0], t[:, 1], t[t > 2])
print(t.sum().item(), t.mean(dim=0), t.tolist())
```

```{ .text .no-copy }
tensor([[1., 2.],
        [3., 4.]])
torch.float32 torch.Size([2, 2]) 2 cpu
torch.int64 torch.bool
torch.Size([2, 3]) tensor([0, 1, 2, 3, 4]) tensor([0.0000, 0.2500, 0.5000, 0.7500, 1.0000])
tensor([[0.8823, 0.9150, 0.3829],
        [0.9593, 0.3904, 0.6009]])
True
tensor([1., 2.]) tensor([2., 4.]) tensor([3., 4.])
10.0 tensor([2., 3.]) [[1.0, 2.0], [3.0, 4.0]]
```

`torch.tensor()` tworzy tensor z listy, a `zeros()`, `arange()`, `linspace()` i `rand()` działają jak ich odpowiedniki z NumPy; liczby całkowite dostają typ `int64`, zmiennoprzecinkowe `float32`. Losowość korzysta domyślnie z jednego globalnego generatora ustawianego przez `torch.manual_seed()` — nie z obiektu generatora jak `default_rng()` z rozdziału 2 — i ziarno odtwarza ten sam wynik. Indeksowanie, wycinki i maski logiczne działają jak w NumPy; różnicą jest nazwa argumentu osi (`dim` zamiast `axis`). Tak jak w NumPy, `.item()` wyciąga z tensora jednoelementowego liczbę Pythona, a `.tolist()` — listę.

## Tensory a NumPy i pandas

```python title="numpy-most.py"
import numpy as np
import pandas as pd
import torch

tablica = np.arange(6, dtype=np.float64).reshape(2, 3)
wspolny = torch.from_numpy(tablica)
kopia = torch.tensor(tablica)
tablica[0, 0] = 100
print(wspolny.dtype, wspolny[0, 0].item(), kopia[0, 0].item())
wspolny[0, 1] = -1
print(tablica[0, 1])
jednoprecyzyjny = torch.tensor(tablica, dtype=torch.float32)
print(jednoprecyzyjny.dtype, jednoprecyzyjny.numpy().dtype)
ramka = pd.DataFrame({"a": [1.0, 2.0], "b": [3.0, 4.0]})
print(torch.tensor(ramka.to_numpy(), dtype=torch.float32))
```

```{ .text .no-copy }
torch.float64 100.0 0.0
-1.0
torch.float32 float32
tensor([[1., 3.],
        [2., 4.]])
```

`torch.from_numpy()` nie kopiuje danych: tensor i tablica dzielą pamięć, więc zmiana jednego widać w drugim — i tensor dziedziczy typ `float64`. `torch.tensor()` kopiuje, a argument `dtype=` od razu zmienia typ; tak przenosimy dane do modeli, które oczekują `float32` i zgłaszają błąd przy mieszaniu typów. W drugą stronę działa `.numpy()`, a ramkę pandas przenosimy przez `to_numpy()` z rozdziału 4; narzędzia przygotowania danych scikit-learn z rozdziału 9 domyślnie zwracają tablice.

## Działania i rozgłaszanie

```python title="dzialania.py"
import torch

torch.manual_seed(42)
pomiary = torch.rand(4, 3) * 10
print(pomiary.round(decimals=1))
print(pomiary.mean(dim=0).round(decimals=2), pomiary.max(dim=1).values.round(decimals=1))
znormalizowane = (pomiary - pomiary.mean(dim=0)) / pomiary.std(dim=0)
print(znormalizowane.std(dim=0))
wagi = torch.tensor([1.0, 0.5, 0.0])
print((pomiary * wagi).sum(dim=1).round(decimals=2), (pomiary @ wagi).round(decimals=2))
print(pomiary.reshape(2, 6).shape, pomiary.T.shape, pomiary.flatten().shape)
pomiary.add_(1)
print(pomiary[0].round(decimals=1))
print(torch.exp(torch.tensor([0.0, 1.0])), torch.tensor([1, 2]) / 2)
```

```{ .text .no-copy }
tensor([[8.8000, 9.2000, 3.8000],
        [9.6000, 3.9000, 6.0000],
        [2.6000, 7.9000, 9.4000],
        [1.3000, 9.3000, 5.9000]])
tensor([5.5800, 7.5800, 6.3000]) tensor([9.2000, 9.6000, 9.4000, 9.3000])
tensor([1., 1., 1.])
tensor([13.4000, 11.5500,  6.5300,  6.0000]) tensor([13.4000, 11.5500,  6.5300,  6.0000])
torch.Size([2, 6]) torch.Size([3, 4]) torch.Size([12])
tensor([ 9.8000, 10.2000,  4.8000])
tensor([1.0000, 2.7183]) tensor([0.5000, 1.0000])
```

Działania elementowe, rozgłaszanie (wektor wag o kształcie `(3,)` mnoży każdy z czterech wierszy), agregacje wzdłuż osi, iloczyn macierzowy `@` i zmiana kształtu — wszystko jak w rozdziale 2. Dwie różnice: `max(dim=)` zwraca parę wartości i indeksów, a `std()` dzieli przez `n − 1` jak pandas, nie przez `n` jak NumPy. Metody z podkreśleniem na końcu (`add_()`) działają w miejscu, jak `out=` z rozdziału 2 — oszczędzają pamięć, ale do tensorów, z których liczymy gradient, wolno je stosować tylko w bloku `no_grad()` z następnego podrozdziału. Dzielenie tensorów całkowitych daje `float32`.

## Urządzenie

```python title="urzadzenie.py"
import torch

urzadzenie = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(urzadzenie)
x = torch.rand(3, device=urzadzenie)
print(x.device, x.to("cpu").device)
print(torch.get_num_threads() > 1)
```

```{ .text .no-copy }
cpu
cpu cpu
True
```

Tensor leży na **urządzeniu** (ang. *device*): procesorze albo karcie graficznej (`cuda`; na komputerach Apple `mps`). Wszystkie tensory jednej operacji muszą leżeć na tym samym urządzeniu, dlatego kod piszemy z jedną zmienną `urzadzenie` i przenosimy na nie model oraz porcje danych metodą `.to()`. Na procesorze PyTorch używa wszystkich rdzeni, co w tym rozdziale wystarcza; karta graficzna opłaca się przy dużych sieciach i dużych porcjach danych, a kod pozostaje ten sam.
