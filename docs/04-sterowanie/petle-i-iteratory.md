# Pętle i iteratory

## Pętla for

Chyba najpopularniejsza struktura językowa, w wersji po pełnym zakresie jakiegoś obiektu złożonego (kontenera — rozdział [5. Typy złożone](../05-typy-zlozone/index.md)) — tutaj na przykładzie łańcucha znakowego:

```python title="petla-for.py"
a = "abcdefgh"
for i in a:
    print(i, end=" ")
# a b c d e f g h
```

Obiekt o nazwie `i` (przyzwyczajenie — możemy użyć dowolnej nazwy) staje się na moment jednej iteracji referencją do poszczególnych obiektów (tu jednoliterowych łańcuchów znakowych); każdy z nich ma swoje (chwilowe) miejsce w pamięci.

<div data-activity-slot="flow-for-basics"></div>

Pętla for w Pythonie posiada również wersję **for… else**, gdzie blok else wykonany zostanie, gdy pętla całkowicie zakończy swoje działanie (nie zostanie przerwana np. przez break). `else` powinien być w takim samym wcięciu co `for` — na co trzeba uważać zwłaszcza, gdy dana pętla for jest zagnieżdżona wewnątrz innej pętli.

```python title="for-else.py"
for i in "abc":
    print(i, end=" ")
else:
    print("poprawny koniec")
# a b c poprawny koniec
```

Zazwyczaj jesteśmy przyzwyczajeni do pętli, która używa jakiejś zmiennej indeksującej. Nie jest to konieczne, ale jeśli potrzebujemy dodatkowo indeksu, najlepiej użyć wbudowanej funkcji `enumerate()`. Zwraca ona **iterator par** (indeks, element) — oba składniki można pobrać w pętli (jest to przykład rozpakowywania przekazanych danych):

```python title="enumerate-pary.py"
a = "abcdefgh"
for i, j in enumerate(a):
    print(i, j, end="; ")
# 0 a; 1 b; 2 c; 3 d; 4 e; 5 f; 6 g; 7 h;
```

Funkcja `enumerate()` posiada również nazwany argument `start`, za pomocą którego możemy zdefiniować początkową wartość (różną od domyślnego 0), czyli `enumerate(a, start=1)`.

A co, jeśli w kodzie pętli nie wpiszemy dwóch obiektów i, j — tylko jeden?

```python title="enumerate-krotki.py"
a = "abcdefgh"
for i in enumerate(a):
    print(i, end="; ")
```

Kod jest nadal całkowicie poprawny, ale obiektowi `i` będą przypisane krotki (class 'tuple'), czyli pary wartości: `(0, 'a'); (1, 'b'); …`, które można również „rozpakować” poprzez przypisanie do dwóch nazwanych obiektów, czyli np. `x, y = i`. Typ tuple omówimy w rozdziale [5. Typy złożone](../05-typy-zlozone/krotka.md). Bliźniaczą funkcją jest `zip()`, łącząca elementy kilku sekwencji w pary — opisujemy ją w rozdziale [5. Typy złożone](../05-typy-zlozone/krotka.md).

Iterator zwracany przez `enumerate()` jest **jednorazowy**: każdy odczyt konsumuje kolejny element, a po pełnym przejściu iterator jest wyczerpany (obiekt źródłowy pozostaje przy tym nietknięty):

```{ .python .no-copy }
>>> e = enumerate("abc")
>>> list(e)              # pierwsze przejście konsumuje iterator
[(0, 'a'), (1, 'b'), (2, 'c')]
>>> list(e)              # drugie przejście — iterator już pusty
[]
```

Znaczek podkreślenia `_` użyty w pętli for to nie jest żaden tajemny trik, tylko zwykła nazwa zmiennej. Jest taki obyczaj, że znaczkiem `_` nazywamy obiekty, których zawartości de facto nie potrzebujemy.

## Leniwa sekwencja range

Funkcja `range()` zwraca **leniwą, niemodyfikowalną sekwencję** liczb całkowitych. Składnia range() zawiera do trzech parametrów. Z jednym parametrem oznacza, ile elementów (zaczynając od 0, z krokiem 1) wygenerować: `range(5)` reprezentuje liczby 0, 1, 2, 3, 4 — ale jeśli ich nie „rozpakujemy”, zobaczymy tylko obiekt range. Dlaczego nie widzimy sekwencji liczb? Ponieważ range stosuje **leniwą ewaluację**: nie przechowuje elementów, lecz oblicza je na żądanie — w przeciwnym razie musiałby powstać obiekt obciążający pamięć lub kosztowny w obliczaniu.

Z dwoma parametrami podajemy zakres od–do (wyłączając górną wartość, z krokiem 1). Z trzema — możemy dodatkowo podać krok. Krok może być ujemny (od większej wartości do mniejszej).

Mimo leniwej natury range jest pełnoprawną sekwencją — zna swoją długość, można odwoływać się do elementów przez indeks, stosować selekcje zakresowe (wynikiem jest `int` albo kolejny obiekt range — tak też można odwrócić kolejność) i przechodzić po nim **wielokrotnie**:

```{ .python .no-copy }
>>> r = range(5)
>>> len(r)
5
>>> r[2]
2
>>> r[1:3]
range(1, 3)
>>> r[::-1]
range(4, -1, -1)
>>> list(r)          # „materializacja” do listy
[0, 1, 2, 3, 4]
>>> list(r)          # range można przejść ponownie
[0, 1, 2, 3, 4]
```

Konstruktor `list()` — kontener list omawiamy w rozdziale [5. Typy złożone](../05-typy-zlozone/lista.md) — jest kanonicznym sposobem „zmaterializowania” leniwej sekwencji do postaci przechowującej wszystkie elementy. (W zewnętrznym module NumPy dostępna jest funkcja `numpy.arange()` przyjmująca krok zmiennoprzecinkowy; dla kroków ułamkowych dokumentacja NumPy zaleca jednak `numpy.linspace()`.)

## Iteratory

Kolejność sekwencji można odwrócić również za pomocą wbudowanej funkcji `reversed()` — zwraca ona **iterator**; jego konkretna klasa zależy od argumentu (`range_iterator` dla range, `reversed` dla str, `list_reverseiterator` dla list).

!!! note "Sekwencja range a iterator"
    Czym różni się leniwa sekwencja (jak range) od iteratora? Obie strategie obliczają
    elementy na żądanie. Sekwencja jest jednak dostępna bez ograniczeń — można
    przechodzić po niej wielokrotnie, sprawdzić długość, odwołać się przez indeks.
    Przejście przez **iterator** jest **jednorazowe**: iterator można przekazać do
    funkcji `next()`, która zwraca (konsumuje) kolejne elementy, aż na koniec zgłosi
    wyjątek `StopIteration`. Sekwencji range nie da się przekazać bezpośrednio do
    next() — najpierw trzeba z niej uzyskać iterator funkcją `iter()`.
    Terminem **generator** określa się w Pythonie szczególny rodzaj iteratora,
    tworzony wyrażeniami generatorowymi i funkcjami ze słowem kluczowym `yield` —
    wracamy do niego przy złożeniach (rozdział
    [5. Typy złożone](../05-typy-zlozone/zlozenia.md)) oraz przy funkcjach.

```{ .python .no-copy }
>>> r = range(5)
>>> it = iter(r)     # jawnie utworzony iterator sekwencji
>>> next(it)
0
>>> next(it)         # kolejne wywołania konsumują elementy
1
>>> list(it)         # reszta elementów — iterator się wyczerpał
[2, 3, 4]
>>> list(it)
[]
```

Czy można reversed() wykorzystać do odwrócenia i porównania łańcucha znakowego (czy jest palindromem)? Można, ale ponieważ reversed() tworzy iterator (leniwa ewaluacja), nie można go ot tak porównać. Natomiast można sprytnie wykonać iterację i połączenie elementów za pomocą funkcji `join()`. Działa ona na obiekcie typu str, który będzie **separatorem** poszczególnych elementów, po których iterujemy (metody typu str — rozdział [3. Nazwy i typy](../03-nazwy-typy/typy-proste.md); join przyjmuje dowolny obiekt iterowalny, więc wróci przy listach i krotkach w rozdziale 5):

```{ .python .no-copy }
>>> "---".join("abc")        # separator między elementami
'a---b---c'
>>> odwrocony = reversed("KayaK")
>>> "".join(odwrocony)       # pusty separator → łańcuch z iteratora
'KayaK'
>>> "".join(odwrocony)       # iterator już skonsumowany!
''
```

Stosując pusty łańcuch jako separator, wytworzyliśmy łańcuch znakowy z obiektu iteratora — i sprawdzenie palindromu (np. słowa KayaK) się powiodło. Pamiętajmy jednak, że przebiegnięcie po iteratorze jest jednorazowe — drugie złączenie daje pusty łańcuch, więc powtórne porównanie zwróci False. Palindrom można też sprawdzić bez iteratorów, wycinkiem z ujemnym krokiem (slicing — rozdział [3. Nazwy i typy](../03-nazwy-typy/typy-proste.md)):

```{ .python .no-copy }
>>> s = "KayaK"
>>> s == s[::-1]
True
```

## Pętla while

Dopóki warunek logiczny jest spełniony, blok należący do while (czyli odpowiednio wcięty) jest wykonywany. Poniższy przykład wykorzystuje wycinki łańcucha (opisane w rozdziale [3. Nazwy i typy](../03-nazwy-typy/typy-proste.md)) oraz fakt, że pusty łańcuch jest logicznie fałszywy:

```python title="while-gwiazdki.py"
gwiazdki = "*"*10
while gwiazdki:   # odwrócona połówka trójkąta
    print(gwiazdki)
    gwiazdki = gwiazdki[1:]   # obcinamy pierwszą gwiazdkę
```

Pętla while posiada również możliwość dodania bloku `else:` po całkowitym jej wykonaniu — czyli jeśli nie zostanie przerwana za pomocą break:

```python title="while-else.py"
a = 1
while a < 3:
    print("a =", a, end=" ")
    a += 1
else:
    print("wykonano!")
# a = 1 a = 2 wykonano!
```

## Break, continue, pass

Są to słowa kluczowe języka Python, których znaczenie zapewne dobrze znamy. Kilka przykładów ilustrujących działanie:

```python title="liczby-pierwsze.py"
for n in range(2, 12):
    for x in range(2, n):
        if n % x == 0:
            print(n, "rowna sie", x, "*", n//x)
            break
    else:
        # to jest wyswietlone gdy petla for sie zakonczy
        print(n, "jest liczba pierwsza")
```

W wyniku działania otrzymamy:

```{ .text .no-copy }
2 jest liczba pierwsza
3 jest liczba pierwsza
4 rowna sie 2 * 2
5 jest liczba pierwsza
6 rowna sie 2 * 3
7 jest liczba pierwsza
8 rowna sie 2 * 4
9 rowna sie 3 * 3
10 rowna sie 2 * 5
11 jest liczba pierwsza
```

Zwróćmy uwagę na wcięcia w powyższym programie. Wykorzystuje on składnię for… else — `else` należy do drugiej, zagnieżdżonej pętli, która, jeśli znajdzie dzielnik jakiejś liczby, przerywa pętlę for (za pomocą break), a jeśli nie znajdzie i się zakończy, przechodzi do else i wypisuje, że dana liczba jest liczbą pierwszą.

```python title="parzyste-nieparzyste.py"
for num in range(2, 10):
    if num % 2 == 0:
        print("Liczba parzysta", num)
        continue   # opuszczenie reszty iteracji za continue
    print("Liczba nieparzysta", num)
```

Powyższy program sprawdza, czy liczba ma resztę z dzielenia przez 2 — jeśli nie ma, to jest parzysta i dalsza część kodu nie jest wykonywana po wydaniu komendy continue (przeskoczenie do końca bloku danej iteracji i przejście do kolejnej).

```{ .python .no-copy }
while True:
    pass   # pusta instrukcja
```

Powyższa pętla jest nieskończona, aż do zatrzymania programu za pomocą ++ctrl+c++. Komendę `pass` używa się często w kodzie, który później zostanie napisany, a początkowo wymaga instrukcji pustej.
