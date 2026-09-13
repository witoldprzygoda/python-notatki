# 14. NumPy i Matplotlib

Dotychczas wystarczały nam listy, słowniki i moduł `math`. Obliczenia na dużych zbiorach liczb i ich wizualizacja wymagają jednak bibliotek spoza języka: **NumPy** dostarcza typ tablicy `ndarray` i operacje wykonywane na całych tablicach naraz, a **Matplotlib** rysuje wykresy. Na tych dwóch bibliotekach opiera się cały ekosystem naukowy Pythona — SciPy, pandas, scikit-learn — dlatego poznajemy je jako pierwsze biblioteki zewnętrzne używane w pełnych, uruchamianych przykładach. Dotąd instalowaliśmy wyłącznie narzędzia pracy, jak pytest w rozdziale 7.

Rozdział ma charakter pomostowy: pokazuje podstawy — tablice, operacje wektorowe, podstawowe wykresy — i domyka pomiar wektoryzacji z rozdziału 13. Pełne omówienie obu bibliotek, a także pandas i SciPy, przewidujemy w części II książki, poświęconej bibliotekom.

Oba pakiety instalujemy w środowisku wirtualnym kursu z rozdziału [1. Instalacja i środowisko pracy](../01-instalacja/pip.md):

```powershell title="Terminal"
python -m pip install numpy matplotlib
```

W chwili pisania aktualne wersje to NumPy 2.5.3 i Matplotlib 3.11.2; przykłady w rozdziale wymagają NumPy 2.x. Konwencja importu — `import numpy as np` oraz, dla wykresów, `import matplotlib.pyplot as plt` — jest powszechna i nie zmieniamy jej, bo tak wyglądają wszystkie przykłady w dokumentacji i w cudzym kodzie; poniższy skrypt importuje sam pakiet `matplotlib`, aby odczytać wersję:

```python title="wersje.py"
import numpy as np
import matplotlib

print(np.__version__, matplotlib.__version__)
```

```{ .text .no-copy }
2.5.3 3.11.2
```

Wykresy w tym rozdziale nie są zrzutami ekranu — każdy powstał z kodu, który go poprzedza, uruchomionego bez zmian.

---

## W tym rozdziale

1. [Tablice ndarray](ndarray.md) — od listy do tablicy, tworzenie, typy elementów, indeksowanie i maski, widok a kopia, zapis i odczyt
2. [Operacje na tablicach](operacje.md) — funkcje uniwersalne, rozgłaszanie, agregacje z osią, kształt, liczby losowe, pomiar wektoryzacji, algebra liniowa
3. [Matplotlib — pierwszy wykres i styl obiektowy](matplotlib-podstawy.md) — hierarchia obiektów, `subplots()`, style linii, tekst i adnotacje
4. [Matplotlib — rodzaje wykresów, układ i zapis](matplotlib-wykresy.md) — `scatter()`, `bar()`, `hist()`, wiele paneli, `savefig()`, typowe pułapki
5. [Przykłady i rozszerzenia](przyklady-i-rozszerzenia.md) — podrozdział uzupełniający: wielomian bez `eval()`, histogram z wykresem pudełkowym, mapa ciepła, animacja, SciPy, odsyłacz do Numby
