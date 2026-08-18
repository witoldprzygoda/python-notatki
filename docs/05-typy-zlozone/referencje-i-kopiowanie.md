# Referencje i kopiowanie

Poszczególne komórki kontenerów w Pythonie są **referencjami** do obiektów w pamięci — dokładnie w tym samym sensie, w jakim referencjami są nazwy zmiennych (model opisany w rozdziale [3. Nazwy i typy](../03-nazwy-typy/obiekty-i-pamiec.md)). Ta strona pokazuje dwie praktyczne konsekwencje tego faktu: pułapki przy budowaniu tablic wielowymiarowych oraz różnicę między kopią płytką a głęboką.

## Tablice wielowymiarowe

Za pomocą listy można stworzyć również tablicę wielowymiarową. Trzeba tu jednak pamiętać, że nie polega to na „definicji” tablicy o określonej wielkości (jak w innych językach programowania), ale na zainicjalizowaniu każdej komórki. Bardzo się tu przyda skrócony zapis — złożenie listowe (ang. *list comprehension*):

```{ .python .no-copy }
X = 4
Y = 2
tab2d = [[0 for y in range(Y)] for x in range(X)]
# [[0, 0], [0, 0], [0, 0], [0, 0]]
```

Logika: dla każdej iteracji podstawowego poziomu (x), budującej podstawowy poziom listy tab2d, wykonane jest utworzenie zagnieżdżonej listy `[0 for y in range(Y)]` wypełnionej zerami. Zapis można skrócić, tworząc każdą zagnieżdżoną listę za pomocą jednoelementowej listy [0] przemnożonej Y razy:

```{ .python .no-copy }
tab2d = [[0]*Y for _ in range(X)]   # zmiennej _ nie potrzebujemy
```

!!! warning "Pułapka klonowania"
    Czy możliwy jest jeszcze większy skrót, np. `X*[Y*[0]]`? Niestety — w takim
    przypadku mnożenie powiela jedynie **referencję**: wszystkie X komórek zewnętrznej
    listy wskazuje na TĘ SAMĄ wewnętrzną listę `Y*[0]`. Choć na pierwszy rzut oka
    powstała taka sama struktura, zmiana zawartości jednej komórki jest widoczna
    we wszystkich wierszach:

    ```{ .python .no-copy }
    >>> X = 4
    >>> Y = 2
    >>> tab2d = X*[Y*[0]]
    >>> tab2d
    [[0, 0], [0, 0], [0, 0], [0, 0]]
    >>> tab2d[0][0] = 7      # zmiana jednej komórki...
    >>> tab2d
    [[7, 0], [7, 0], [7, 0], [7, 0]]
    ```

Nawet w przypadku „poprawnie” skonstruowanej dwuwymiarowej tablicy warto sobie uświadomić, że poszczególne komórki takiej struktury są **referencjami** do określonych miejsc w pamięci. Jeśli zbudujemy tablicę wypełnioną samymi zerami, wszystkie komórki pokazują na ten sam adres — to opisana w rozdziale [3. Nazwy i typy](../03-nazwy-typy/obiekty-i-pamiec.md) optymalizacja małych wartości całkowitych z zakresu [-5, 256]. Jakakolwiek zmiana zawartości komórki pociąga za sobą zmianę dowiązania adresowego:

```{ .python .no-copy }
>>> tab2d = [[0]*Y for _ in range(X)]
>>> [[id(komorka) for komorka in wiersz] for wiersz in tab2d]
[[140707302204504, 140707302204504], [140707302204504, 140707302204504], [140707302204504, 140707302204504], [140707302204504, 140707302204504]]
>>> id(0)
140707302204504
>>> tab2d[0][0] = 7
>>> tab2d
[[7, 0], [0, 0], [0, 0], [0, 0]]
>>> id(tab2d[0][0])
140707302204728
>>> id(7)
140707302204728
```

Konkretne wartości zwracane przez `id()` zależą od komputera i sesji interpretera — istotne jest jedynie to, które z nich są sobie równe.

Skoro dwuwymiarowa lista to po prostu listy zagnieżdżone w listach, można zawsze zacząć od pustej listy w liście `[[]]`, by potem za pomocą `extend()` czy `append()` rozszerzać i dokładać. Można też zacząć od jednego wymiaru i pozostałe dokładać później.

!!! info "NumPy"
    Poważniejsze używanie macierzy na pewno skieruje nas ku modułowi **NumPy**,
    dedykowanemu do pracy z macierzami (typ ndarray) — poznamy w dalszej części kursu.

## Kopiowanie: płytkie i głębokie

Obiekty modyfikowalne, takie jak lista, mają stały początkowy adres w pamięci (różny od adresu pierwszego elementu) — zatem modyfikacja ich zawartości bądź powiększenie nie zmienia tego adresu:

```{ .python .no-copy }
>>> L = [1, 2, 3]
>>> id(L)
2333498581312
>>> L.append(4)
>>> L
[1, 2, 3, 4]
>>> id(L)                # ten sam adres
2333498581312
```

(Konkretna wartość adresu będzie w każdej sesji inna — istotne, że nie uległa zmianie.)

Kopiowanie listy może być operacją wykonywania kopii **płytkiej** lub **głębokiej**. Przypisanie innej nazwy do istniejącej nazwy listy nie jest żadnym kopiowaniem, tylko dowiązaniem kolejnej nazwy do tego samego adresu — wszelkie operacje za pomocą jednej nazwy wpływają na tę samą zawartość w pamięci:

```{ .python .no-copy }
>>> L = [1, 2, [10, 20]]
>>> M = L                # to nie kopia, tylko druga nazwa
>>> M is L
True
>>> M.append(99)
>>> L
[1, 2, [10, 20], 99]
```

Typ list posiada funkcję `copy()`, która na podstawowym poziomie elementów wykonuje rzeczywiście kopię. Jednak jeśli elementem jest zagnieżdżona lista, to kopia nie jest wykonana — skopiowany zostaje adres, a zatem jest to **płytka kopia**:

```{ .python .no-copy }
>>> L = [1, 2, [10, 20]]
>>> P = L.copy()
>>> P is L
False
>>> P[0] = 111
>>> L
[1, 2, [10, 20]]
>>> P
[111, 2, [10, 20]]
>>> P[2][0] = 999        # zagnieżdżona lista jest wspólna!
>>> P
[111, 2, [999, 20]]
>>> L
[1, 2, [999, 20]]
```

Płytką kopię tworzą równoważnie: `L.copy()`, `list(L)`, pełny wycinek `L[:]` oraz `copy.copy(L)` — we wszystkich czterech przypadkach zagnieżdżone obiekty pozostają wspólne.

Jeśli chcemy wykonać głęboką kopię, łącznie z zagnieżdżonymi obiektami, można wykorzystać moduł `copy`. Posiada on funkcję `copy()` o działaniu takim samym jak copy() typu list, ale posiada również funkcję `deepcopy()`:

```{ .python .no-copy }
>>> import copy
>>> L = [1, 2, [10, 20]]
>>> P = copy.copy(L)     # działa jak L.copy() — kopia płytka
>>> P[2][0] = 999
>>> L
[1, 2, [999, 20]]
>>> L = [1, 2, [10, 20]]
>>> G = copy.deepcopy(L) # kopia głęboka
>>> G[2][0] = 999
>>> G
[1, 2, [999, 20]]
>>> L
[1, 2, [10, 20]]
```

Emulację kopiowania — na podstawowym poziomie — można wykonać również przechodząc po elementach listy i budując, wartość po wartości, nową listę:

```{ .python .no-copy }
>>> L = [1, 2, 3]
>>> nowaL = []
>>> for wartosc in L:
...     nowaL.append(wartosc)
...
>>> nowaL
[1, 2, 3]
>>> nowaL is L
False
```
