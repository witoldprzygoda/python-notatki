# Referencje i kopiowanie

Poszczególne komórki kontenerów w Pythonie są **referencjami** do obiektów w pamięci. Ta strona pokazuje dwie praktyczne konsekwencje tego faktu: pułapki przy budowaniu tablic wielowymiarowych oraz różnicę między kopią płytką a głęboką.

## Tablice wielowymiarowe

Za pomocą listy można stworzyć również tablicę wielowymiarową. Trzeba tu jednak pamiętać, że nie polega to na „definicji” tablicy o określonej wielkości (jak w innych językach programowania), ale na zainicjalizowaniu każdej komórki. Bardzo się tu przyda skrócony zapis (list comprehension):

```python
X = 4
Y = 2
tab2d = [[0 for y in range(Y)] for x in range(X)]
# [[0, 0], [0, 0], [0, 0], [0, 0]]
```

Logika: dla każdej iteracji podstawowego poziomu (x), budującej podstawowy poziom listy tab2d, wykonane jest utworzenie zagnieżdżonej listy `[0 for y in range(Y)]` wypełnionej zerami. Zapis można skrócić, tworząc każdą zagnieżdżoną listę za pomocą jednoelementowej listy [0] przemnożonej Y razy:

```python
tab2d = [[0]*Y for _ in range(X)]   # zmiennej _ nie potrzebujemy
```

!!! warning "Pułapka klonowania"
    Czy możliwy jest jeszcze większy skrót, np. `X*[Y*[0]]`? Niestety — w takim
    przypadku wewnętrzna lista `Y*[0]` zostanie **sklonowana** (a nie skopiowana).
    Choć na pierwszy rzut oka powstała taka sama struktura, zmiana zawartości jednej
    komórki pociąga za sobą zmianę we wszystkich pozostałych podwymiarach.

<!-- TODO: przykłady z PDF (zrzuty): klonowanie X*[Y*[0]]; adresy komórek tablicy zer;
     przypisanie 7 i adresy -->

Nawet w przypadku „poprawnie” skonstruowanej dwuwymiarowej tablicy warto sobie uświadomić, że poszczególne komórki takiej struktury są **referencjami** do określonych miejsc w pamięci. Jeśli zbudujemy tablicę wypełnioną samymi zerami, wszystkie komórki pokazują na ten sam adres (Python wykonuje optymalizację dla pewnego zakresu wartości całkowitych). Jakakolwiek zmiana zawartości komórki pociąga za sobą zmianę dowiązania adresowego.

Skoro dwuwymiarowa lista to po prostu listy zagnieżdżone w listach, można zawsze zacząć od pustej listy w liście `[[]]`, by potem za pomocą `extend()` czy `append()` rozszerzać i dokładać. Można też zacząć od jednego wymiaru i pozostałe dokładać później.

!!! info "NumPy"
    Poważniejsze używanie macierzy na pewno skieruje nas ku modułowi **NumPy**,
    dedykowanemu do pracy z macierzami (typ ndarray) — poznamy w dalszej części kursu.

## Kopiowanie: płytkie i głębokie

Obiekty modyfikowalne, takie jak lista, mają stały początkowy adres w pamięci (różny od adresu pierwszego elementu) — zatem modyfikacja ich zawartości bądź powiększenie nie zmienia tego adresu.

Kopiowanie listy może być operacją wykonywania kopii **płytkiej** lub **głębokiej**. Przypisanie innej nazwy do istniejącej nazwy listy nie jest żadnym kopiowaniem, tylko dowiązaniem kolejnej nazwy do tego samego adresu — wszelkie operacje za pomocą jednej nazwy wpływają na tę samą zawartość w pamięci.

Typ list posiada funkcję `copy()`, która na podstawowym poziomie elementów wykonuje rzeczywiście kopię. Jednak jeśli elementem jest zagnieżdżona lista, to kopia nie jest wykonana — skopiowany zostaje adres, a zatem jest to **płytka kopia**.

Jeśli chcemy wykonać głęboką kopię, łącznie z zagnieżdżonymi obiektami, można wykorzystać moduł `copy`. Posiada on funkcję `copy()` o działaniu takim samym jak copy() typu list, ale posiada również funkcję `deepcopy()`.

<!-- TODO: przykłady z PDF (zrzuty): copy() płytkie, copy.copy(), copy.deepcopy(),
     emulacja kopiowania pętlą -->
