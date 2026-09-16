# 11. PyTorch — tensory i sieć neuronowa

Wszystkie modele ścieżki były dotąd gotowymi klasami scikit-learn z metodami `fit()` i `predict()`. **Sieć neuronowa** (ang. *neural network*) to model złożony z warstw: każda liczy ważone sumy swoich wejść — jak regresja liniowa z rozdziału 9 — i przepuszcza je przez prostą funkcję nieliniową, a złożenie kilku takich warstw odwzorowuje zależności, których model liniowy nie odda. **Wagi** (ang. *weights*) wszystkich warstw znajduje spadek gradientu. **PyTorch** dostarcza trzech rzeczy, których do tego potrzeba: tensorów — tablic jak w NumPy, ale liczonych także na karcie graficznej — automatycznego różniczkowania, które wyznacza gradient dowolnej funkcji zapisanej na tensorach, oraz gotowych warstw i optymalizatorów. Rozdział buduje sieć z tych elementów: od tensora, przez gradient i pętlę treningową, po klasyfikację obrazów cyfr i regresję cen mieszkań — z porównaniem do modeli z poprzednich rozdziałów, które nie zawsze wypada na korzyść sieci.

Dane rozdziału to zbiory z poprzednich rozdziałów: półksiężyce `make_moons` i cyfry digits z rozdziału 10 oraz `mieszkania.csv` z rozdziału 9. Do pobrania są kopia tego pliku — [mieszkania.csv](pliki/mieszkania.csv) — i moduł [trening.py](pliki/trening.py) z pętlą treningową, który powstaje w podrozdziale o sieci neuronowej i służy kolejnym stronom; skrypty uruchamiamy w katalogu z tymi dwoma plikami.

Bibliotekę PyTorch w wersji 2.14.0 dopisujemy do pliku wymagań jako pakiet `torch`. Koło z PyPI dla Windows to wersja na procesor (`torch.__version__` pokazuje `2.14.0+cpu`) zajmująca około 550 MB; w Linuksie koło z PyPI to wersja z obsługą kart NVIDIA, która wraz z osobnymi pakietami bibliotek CUDA zajmuje kilkakrotnie więcej, a wersję na sam procesor instaluje się z indeksu `https://download.pytorch.org/whl/cpu`. Do obliczeń w tym rozdziale procesor wystarcza — najdłuższy trening trwa kilka sekund.

```text title="requirements.txt"
numpy==2.5.3
matplotlib==3.11.2
ipykernel==7.3.0
jupyterlab==4.6.3
pandas==3.0.5
openpyxl==3.1.5
pyarrow==25.0.1
tabulate==0.10.0
pytest==9.1.1
scikit-learn==1.9.1
torch==2.14.0
```

```powershell title="Terminal"
python -m pip install -r requirements.txt
```

Rozdział buduje na rozdziale 2 (rozgłaszanie, najmniejsze kwadraty), 7 (podział danych, przeuczenie, powtarzalność, zapis modelu), 8 (regresja logistyczna), 9 (przygotowanie danych) i 10 (dane); z części „Python Notatki” korzysta z rozdziałów 10 (klasy i dziedziczenie) i 11 (wywołanie obiektu). Pozostałe wersje jak w rozdziale 7: scikit-learn 1.9.1, pandas 3.0.5, NumPy 2.5.3, Matplotlib 3.11.2.

---

## W tym rozdziale

1. [Tensory](tensory.md) — sprawdzenie instalacji, tworzenie tensorów, wymiana z NumPy i pandas, działania i rozgłaszanie, urządzenie
2. [Automatyczne różniczkowanie](autograd.md) — gradient, spadek gradientu, regresja liniowa pętlą, funkcja straty i optymalizator
3. [Sieć neuronowa](siec.md) — warstwy i `nn.Sequential`, pętla treningowa, porcje danych, moduł `trening.py`, granica decyzyjna
4. [Klasyfikacja obrazów](cyfry.md) — obrazy jako tensory, sieć w pełni połączona, sieć splotowa, zapis i wczytanie modelu
5. [Trening w praktyce](praktyka.md) — regresja cen mieszkań, hiperparametry i regularyzacja, GPU i większe dane, kiedy PyTorch, lista kontrolna
