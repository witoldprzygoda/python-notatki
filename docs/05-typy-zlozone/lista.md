# Lista

Lista jest przykładem kontenera o **modyfikowalnej** zawartości. Listę w zapisie rozpoznajemy po prostokątnych nawiasach, elementy oddzielone przecinkami, co naturalnie upodabnia ten kontener do tablicy. Lista może mieć elementy różnych typów, łącznie z typami złożonymi — czyli np. zagnieżdżoną kolejną listą.

## Tworzenie listy

Podstawowe operacje na obiektach listy są podobne do tych dla typu str. Listy można powielać przez mnożenie, dodawać:

```{ .python .no-copy }
>>> lista = [1, 2, 3]
>>> lista * 3
[1, 2, 3, 1, 2, 3, 1, 2, 3]
>>> lista + ["cztery", "pięć"]
[1, 2, 3, 'cztery', 'pięć']
>>> lista + lista
[1, 2, 3, 1, 2, 3]
```

Na liście można wykonywać selekcję (slicing, opisany przy typie str w rozdziale [3. Nazwy i typy](../03-nazwy-typy/typy-proste.md)), ale nową rzeczą jest fakt, że wybrany przez taką selekcję fragment listy może być **zmodyfikowany lub usunięty**:

```{ .python .no-copy }
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
letters[2:5] = ['C', 'D', 'E']   # podmiana
letters[2:5] = []                # usunięcie ich
letters[:] = []                  # cała lista
len(letters)                     # 0 — len() liczy elementy najwyższego poziomu
```

Funkcja `len()` zwraca liczbę elementów podstawowego poziomu listy — lista zagnieżdżona liczy się jako jeden element (`len([[1, 2], [3]])` daje 2, nie 3).

Listę tworzymy zazwyczaj przez wymienienie elementów w prostokątnym nawiasie, ale równie często korzysta się z konstruktora — ten przyjmuje **co najwyżej jeden argument** (wywołany bez argumentów tworzy pustą listę); można taką operację postrzegać jako operator konwersji na typ list. W środku mogą być obiekty w „różnych nawiasach”, ale również iteratory. A jeśli argumentem będzie łańcuch znakowy, zostanie stworzona lista z poszczególnych znaków. Ilustracja:

```{ .python .no-copy }
lista = ["aa", "cc", "bb"]
# lista = list("aa", "cc", "bb")   # błąd
lista = list(["aa", "cc", "bb"])   # [] list
lista = list(("aa", "cc", "bb"))   # () tuple
lista = list({"aa", "cc", "bb"})   # {} set
```

Lista może zawierać elementy różnych typów, nawet obiekty iteratora. Jak pamiętamy z rozdziału [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md), odczytanie iteratora oznacza jego wyczerpanie — jest to obiekt jednorazowy.

Można oczywiście zagnieżdżać obiekty. Ciekawym przypadkiem jest zagnieżdżenie listy w samej sobie… co prowadzi do „niekończącej się” rekurencji w głąb (widać to podczas „slicingu” tak powstałego obiektu). Można by napisać funkcję, w której wykonujemy pętlę po kolejnych elementach listy, sprawdzając ich typ, oraz — gdy się okaże, że typ elementu to lista (warunek `if isinstance(i, list):`) — rekurencyjnie wywołać funkcję z tym elementem. W ten sposób szybko przekonalibyśmy się, że wykonanie zakończy się błędem typu:

```{ .text .no-copy }
RecursionError: maximum recursion depth exceeded
```

po wykonaniu blisko 1000 rekurencyjnie zagnieżdżonych wywołań. Rekurencję — wraz z jej ograniczeniami i limitem zagnieżdżeń, który można odczytać i zmienić w module `sys` — omawiamy w rozdziale [6. Funkcje](../06-funkcje/rekurencja.md#limit-rekurencji).

## Elementy listy

Typowa iteracja po elementach listy to pętla for. Można również sprawdzić, czy interesujący element znajduje się na liście, za pomocą operatora `in`:

```python title="operator-in.py"
lista = ["jeden", "dwa", "trzy"]
if "dwa" in lista:
    print("Tak, 'dwa' jest elementem listy.")
```

Innym sposobem otrzymania elementów listy (i nie tylko) jest **rozpakowanie**. Możliwa jest też operacja odwrotna — zbudowanie listy:

```{ .python .no-copy }
>>> lista = ["jeden", "dwa", "trzy"]
>>> a, b, c = lista            # rozpakowanie do trzech nazw
>>> a
'jeden'
>>> c
'trzy'
>>> pierwszy, *reszta = lista  # gwiazdka zbiera pozostałe elementy
>>> pierwszy
'jeden'
>>> reszta
['dwa', 'trzy']
>>> nowa = [pierwszy, *reszta, "cztery"]   # operacja odwrotna: budowanie listy
>>> nowa
['jeden', 'dwa', 'trzy', 'cztery']
```

Mechanizm pakowania i rozpakowywania omawiamy systematycznie przy [krotce](krotka.md).

Obiekt listy nie jest iteratorem, ale można taki utworzyć za pomocą funkcji `iter()`, której argumentem jest obiekt iterowalny (np. lista) — mechanizm poznany w rozdziale [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md). Kolejne elementy pobieramy funkcją `next()`. Po wyczerpaniu elementów next() zgłasza wyjątek `StopIteration`; aby tego uniknąć, można podać w next() drugi argument — wartość domyślną zwracaną zamiast wyjątku:

```{ .python .no-copy }
>>> lista = ["jeden", "dwa", "trzy"]
>>> it = iter(lista)
>>> next(it)
'jeden'
>>> next(it)
'dwa'
>>> next(it)
'trzy'
>>> next(it)
Traceback (most recent call last):
  File "<python-input-5>", line 1, in <module>
    next(it)
    ~~~~^^^^
StopIteration
>>> next(it, "koniec")
'koniec'
```

Wartość domyślną można wykorzystać jako wartownika (ang. *sentinel*) kończącego pętlę:

```{ .python .no-copy }
>>> it = iter(lista)
>>> element = next(it, "koniec")
>>> while element != "koniec":
...     print(element)
...     element = next(it, "koniec")
...
jeden
dwa
trzy
```

Gdyby nie sprawdzenie w warunku pętli, next() zwracałoby w nieskończoność wartość domyślną „koniec”. Drugi argument samej funkcji `iter()` ma natomiast inne znaczenie: w formie dwuargumentowej `iter(obiekt_wywoływalny, wartownik)` pierwszym argumentem musi być obiekt wywoływalny — jest on wywoływany bez argumentów tak długo, aż zwróci wartość wartownika. Do tej formy wracamy w rozdziale [6. Funkcje](../06-funkcje/funkcje-jako-obiekty.md#obiekty-wywoywalne); tutaj tylko krótka ilustracja:

```{ .python .no-copy }
>>> iter(lista, "trzy")
Traceback (most recent call last):
  File "<python-input-10>", line 1, in <module>
    iter(lista, "trzy")
    ~~~~^^^^^^^^^^^^^^^
TypeError: iter(v, w): v must be callable
>>> kopia = lista.copy()
>>> it = iter(kopia.pop, "jeden")   # wywołuj kopia.pop(), aż zwróci "jeden"
>>> next(it)
'trzy'
>>> next(it)
'dwa'
>>> next(it)
Traceback (most recent call last):
  File "<python-input-15>", line 1, in <module>
    next(it)
    ~~~~^^^^
StopIteration
>>> kopia
[]
```

W badaniu elementów listy (i nie tylko listy) pomocne mogą być dwie funkcje: `all()`, `any()`. Pierwsza zwraca True, gdy **wszystkie** elementy listy mają ewaluowaną wartość logiczną True. Druga — `any()` — zwraca True, gdy **choć jeden** element jest prawdziwy. Dla pustej listy `all()` zwraca True (nie ma elementu, który łamałby warunek), a `any()` — False.

Na każdej kolekcji iterowalnej (także krotkach i zbiorach, a dla słownika — po kluczach) działają ponadto funkcje wbudowane `len()`, `sum()`, `min()` i `max()`:

```{ .python .no-copy }
>>> nums = [3, 1, 4, 1, 5]
>>> len(nums), sum(nums), min(nums), max(nums)
(5, 14, 1, 5)
```

Funkcja `sum()` wymaga elementów liczbowych, a `min()`/`max()` — elementów wzajemnie porównywalnych. Wspomnijmy też, że poznana przy iteratorach metoda `join()` łączy elementy listy (łańcuchy znakowe) w jeden napis: `' '.join(['raz', 'dwa'])` daje `'raz dwa'`.

## Funkcje składowe listy

Poniżej zwięzły przegląd funkcji należących do typu list — warto się z nimi zapoznać.

**append(element)** — wstawia element na końcu listy. Jeśli lista jest pusta, to jest to jej pierwszy element:

```{ .python .no-copy }
>>> L = []
>>> L.append(1)
>>> L.append("dwa")
>>> L
[1, 'dwa']
```

!!! warning "Modyfikowalność w pętli"
    Modyfikowalność obiektu listy może doprowadzić do zaskakujących efektów.
    Jeśli w pętli for wykonywanej na obiektach listy będziemy wewnątrz pętli
    dodawać kolejne elementy, to pętla się nie zakończy (przerwanie: ++ctrl+c++):

    ```{ .python .no-copy }
    >>> L = [1, 2]
    >>> for x in L:
    ...     L.append(x)   # pętla nigdy się nie zakończy
    ```

    Równie zdradliwe jest **usuwanie** podczas iteracji: po remove() elementy
    przesuwają się w lewo, a licznik pętli idzie dalej — element następujący
    bezpośrednio po usuniętym zostaje pominięty:

    ```{ .python .no-copy }
    >>> nums = [1, 2, 2, 3]
    >>> for x in nums:
    ...     if x % 2 == 0:
    ...         nums.remove(x)
    ...
    >>> nums    # spodziewaliśmy się [1, 3] — druga dwójka „umknęła” iteracji
    [1, 2, 3]
    ```

    Bezpieczne wzorce: iteracja po kopii (`for x in nums[:]`) albo budowa nowej
    listy złożeniem (`[x for x in nums if x % 2 != 0]`) — oba dają `[1, 3]`.

**extend(&lt;obiekt&gt;)** — dodaje na koniec listy elementy innej wielkości iterowalnej: listy, krotki, łańcucha znakowego czy leniwej sekwencji range (jej elementy zostają wyliczone i dołączone do listy):

```{ .python .no-copy }
>>> L = [1, 2]
>>> L.extend([3, 4])
>>> L
[1, 2, 3, 4]
>>> L.extend("ab")
>>> L
[1, 2, 3, 4, 'a', 'b']
>>> L.extend(range(3))
>>> L
[1, 2, 3, 4, 'a', 'b', 0, 1, 2]
```

**insert(pozycja, element)** — wstawia na wskazanej pozycji element (można wstawiać na początku i na końcu):

```{ .python .no-copy }
>>> L = ["b", "c"]
>>> L.insert(0, "a")        # na początku
>>> L
['a', 'b', 'c']
>>> L.insert(len(L), "d")   # na końcu
>>> L
['a', 'b', 'c', 'd']
```

**remove(element)** — przeszukuje listę pod kątem wystąpienia elementu i usuwa pierwszy napotkany. Jeśli elementu nie ma na liście, zgłoszony zostaje wyjątek `ValueError`. Aby temu zapobiec, należy przed usunięciem sprawdzić (operatorem `in`), czy dany element jest na liście:

```{ .python .no-copy }
>>> L = [1, 2, 3, 2]
>>> L.remove(2)
>>> L
[1, 3, 2]
>>> L.remove(7)
Traceback (most recent call last):
  File "<python-input-3>", line 1, in <module>
    L.remove(7)
    ~~~~~~~~^^^
ValueError: list.remove(x): x not in list
>>> if 7 in L:
...     L.remove(7)
...
>>> L
[1, 3, 2]
```

**pop()** — opcjonalnie z argumentem indeks — usuwa wskazany element z listy (bez argumentu: ostatni) i **zwraca** go. Indeks może być również ujemny. Jeśli indeks jest poza zakresem, zgłoszony zostaje wyjątek `IndexError`:

```{ .python .no-copy }
>>> L = ["a", "b", "c", "d"]
>>> L.pop()
'd'
>>> L.pop(0)
'a'
>>> L.pop(-1)
'c'
>>> L
['b']
>>> L.pop(5)
Traceback (most recent call last):
  File "<python-input-5>", line 1, in <module>
    L.pop(5)
    ~~~~~^^^
IndexError: pop index out of range
```

**del** — usuwa wskazany indeksem element lub zakres elementów, albo i całą zawartość (operator poznany w rozdziale [3. Nazwy i typy](../03-nazwy-typy/obiekty-i-pamiec.md)). Składnię można zapisać z nawiasami lub jako operator del przed wybranym zakresem elementów:

```{ .python .no-copy }
>>> L = [0, 1, 2, 3, 4, 5, 6, 7]
>>> del(L[0])      # zapis z nawiasami — to nadal operator, nie funkcja
>>> L
[1, 2, 3, 4, 5, 6, 7]
>>> del L[1:3]
>>> L
[1, 4, 5, 6, 7]
>>> del L[::2]     # co drugi element
>>> L
[4, 6]
>>> del L[:]
>>> L
[]
>>> del L[0]
Traceback (most recent call last):
  File "<python-input-9>", line 1, in <module>
    del L[0]
        ~^^^
IndexError: list assignment index out of range
```

**clear()** — usuwa wszystkie elementy z listy; funkcja jest bezargumentowa i niczego nie zwraca. Nawet w przypadku funkcji nic niezwracającej można wykonać przypisanie — obiektem zwracanym jest wtedy None:

```{ .python .no-copy }
>>> L = [1, 2, 3]
>>> wynik = L.clear()
>>> L
[]
>>> print(wynik)
None
```

**count(element)** — zwraca liczbę obiektów o wartości element znajdujących się na liście (na jej podstawowym poziomie):

```{ .python .no-copy }
>>> L = [1, 2, 1, 3, 1]
>>> L.count(1)
3
>>> L.count(5)
0
```

**index(element)** — zwraca pozycję indeksową pierwszego napotkanego wystąpienia elementu; jeśli elementu nie ma, zgłaszany jest `ValueError`. Aby odczytać wszystkie wystąpienia, zamiast index() często pisze się złożenie z warunkiem (funkcję `enumerate()` poznaliśmy w rozdziale [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md)):

```{ .python .no-copy }
>>> L = ["a", "b", "c", "b"]
>>> L.index("b")
1
>>> L.index("x")
Traceback (most recent call last):
  File "<python-input-2>", line 1, in <module>
    L.index("x")
    ~~~~~~~^^^^^
ValueError: list.index(x): x not in list
>>> [i for i, x in enumerate(L) if x == "b"]
[1, 3]
```

**reverse()** — odwraca kolejność elementów na liście, w miejscu (por. funkcja `reversed()` z rozdziału 4, która zwraca iterator, nie modyfikując listy):

```{ .python .no-copy }
>>> L = [1, 2, 3, 4]
>>> L.reverse()
>>> L
[4, 3, 2, 1]
```

**copy()** — wykonuje kopię listy na podstawowym poziomie elementów (kopia płytka — szczegóły na stronie [Referencje i kopiowanie](referencje-i-kopiowanie.md)):

```{ .python .no-copy }
>>> L = [1, 2, 3]
>>> P = L.copy()
>>> P
[1, 2, 3]
>>> P is L
False
```

## Sortowanie

**sort()** — sortuje listę **w miejscu** (ang. *in-place*), rosnąco (domyślnie) lub malejąco (`reverse=True`), według kryterium porównania `<`; obiekty różnych typów, które nie mogą być porównane, nie mogą też być posortowane:

```{ .python .no-copy }
>>> L = [3, 1, 2]
>>> L.sort()
>>> L
[1, 2, 3]
>>> L.sort(reverse=True)
>>> L
[3, 2, 1]
>>> L = [3, "dwa", 1]
>>> L.sort()
Traceback (most recent call last):
  File "<python-input-6>", line 1, in <module>
    L.sort()
    ~~~~~~^^
TypeError: '<' not supported between instances of 'str' and 'int'
```

!!! warning "sort() niczego nie zwraca"
    Metoda sort() modyfikuje listę i zwraca None — częstym błędem jest zapis
    `lista = lista.sort()`, który kasuje listę (podstawia None pod jej nazwę):

    ```{ .python .no-copy }
    >>> lista = [3, 1, 2]
    >>> lista = lista.sort()    # częsty błąd!
    >>> print(lista)
    None
    ```

Sposób określania porównywanych wartości definiuje argument `key`, przyjmujący funkcję wyliczającą na każdym elemencie wartość porównywaną podczas sortowania — np. sortowanie według długości elementów albo bez uwzględniania wielkości liter (tu dodatkowo z odwróconą kolejnością):

```{ .python .no-copy }
>>> zwierzeta = ["pies", "kot", "krokodyl", "ryba"]
>>> zwierzeta.sort(key=len)
>>> zwierzeta
['kot', 'pies', 'ryba', 'krokodyl']
>>> owoce = ["banan", "Ananas", "cytryna"]
>>> owoce.sort(key=str.lower, reverse=True)
>>> owoce
['cytryna', 'banan', 'Ananas']
```

Sortowanie jest **stabilne**: elementy o tej samej wartości klucza zachowują wzajemną kolejność. Widać to na mieszance typów int i str (bezpośrednio nieporównywalnych) sortowanej z `key=str` — `"1"` oraz `1` pozostają względem siebie w pierwotnym porządku:

```{ .python .no-copy }
>>> L = [2, "1", 1, "10", "2"]
>>> L.sort(key=str)
>>> L
['1', 1, '10', 2, '2']
```

Argument `key` przyjmuje funkcję — na razie korzystamy z funkcji wbudowanych; własne kryteria, w tym zwięzłe anonimowe wyrażenia `lambda`, poznamy w rozdziale [6. Funkcje](../06-funkcje/funkcje-jako-obiekty.md#funkcja-klucza-w-sorted-min-i-max).

Bardziej uniwersalna jest wbudowana funkcja **sorted()**, działająca na wszelkich kolekcjach iterowalnych — zwraca **nową**, posortowaną listę, a oryginalny kontener pozostaje niezmieniony. Argumenty `key` i `reverse` podajemy z nazwą:

```{ .python .no-copy }
>>> sorted(["bbb", "a", "cc"], key=len)
['a', 'cc', 'bbb']
>>> sorted("Python jest super".split(), key=str.lower)
['jest', 'Python', 'super']
```

Więcej technik sortowania opisuje dokumentacja: [Sorting HOWTO](https://docs.python.org/3/howto/sorting.html).

## Złożenia listowe (list comprehension)

Skrócony zapis, tzw. złożenie listowe (ang. *list comprehension*), pozwala w jednej linii utworzyć listę, wykonać iterację i sprawdzić warunek. Ogólna postać składni:

```{ .text .no-copy }
[wyrażenie for zmienna in iterowalne if warunek]
```

Przykładowo, pętlę budującą listę potęg dwójki można zastąpić jedną linią; w składni można też dodać warunek, a nawet podwójną pętlę (kombinacja każdego elementu z każdym):

```{ .python .no-copy }
>>> pow2 = []
>>> for x in range(10):
...     pow2.append(2 ** x)
...
>>> pow2
[1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
>>> pow2 = [2 ** x for x in range(10)]
>>> pow2
[1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
>>> [2 ** x for x in range(10) if x > 5]
[64, 128, 256, 512]
>>> [x + y for x in ["Jestem ", "Mam na imię "] for y in ["Adam", "Ewa"]]
['Jestem Adam', 'Jestem Ewa', 'Mam na imię Adam', 'Mam na imię Ewa']
```

Jeszcze inny przykład — przeliczanie temperatury w stopniach Celsjusza na stopnie Fahrenheita:

```{ .python .no-copy }
>>> Celsius = [-17.7778, -10, 0, 12.5, 36.6, 38.0, 42.0]
>>> Fahrenheit = [9/5*x + 32 for x in Celsius]
>>> Fahrenheit
[-3.999999999848569e-05, 14.0, 32.0, 54.5, 97.88000000000001, 100.4, 107.60000000000001]
```

Naturalnie wolelibyśmy wynik zapisany z precyzją np. do dwóch miejsc po przecinku. Jeśli chcemy od razu wynik z określoną precyzją, można skorzystać z funkcji zaokrąglenia `round(wartość, precyzja)`:

```{ .python .no-copy }
Fahrenheit = [round(9/5*x + 32, 2) for x in Celsius]
# wynik: [-0.0, 14.0, 32.0, 54.5, 97.88, 100.4, 107.6]
```

Jeśli jednak chodzi o formatowanie wyświetlania, a nie ingerowanie w sam rezultat, można skorzystać z f-stringów poznanych w rozdziale [3. Nazwy i typy](../03-nazwy-typy/typy-proste.md):

```{ .python .no-copy }
newF = [f"{x:.1f}" for x in Fahrenheit]
# wynik: ['-0.0', '14.0', '32.0', '54.5', '97.9', '100.4', '107.6']
```

Jak widać, efektem jest lista obiektów typu str, a nie float (w starszym kodzie ten sam efekt daje zapis `'%.1f' % x` — formatowanie w stylu printf). Można jednak wykonać wtórną konwersję:

```{ .python .no-copy }
newF = [float(f"{x:.1f}") for x in Fahrenheit]
# wynik: [-0.0, 14.0, 32.0, 54.5, 97.9, 100.4, 107.6]
```

Złożenia mają odpowiedniki dla słowników i zbiorów oraz czwartą formę — wyrażenie generatorowe; zestawia je podrozdział [Złożenia](zlozenia.md).

## Kolejka i stos

W informatyce są wyróżnione pewne proste struktury danych, takie jak kolejka i stos. Ich implementację można poglądowo wykonać w oparciu o listę:

```{ .python .no-copy }
# emulacja kolejki (queue)
tab = [1, 2, 3]
tab.append(4)   # queue.push(4)
tab.pop(0)      # queue.pop()
tab[0]          # queue.peek()

# emulacja stosu (stack)
tab = [1, 2, 3]
tab.append(4)   # stack.push(4)
tab.pop()       # stack.pop()
tab[-1]         # stack.peek()
```

!!! note "collections.deque"
    Emulacja kolejki na liście ma charakter poglądowy: operacja `pop(0)` wymaga
    przesunięcia wszystkich pozostałych elementów, jest więc kosztowna dla dłuższych
    list. Dokumentacja Pythona rekomenduje do tego celu typ `collections.deque`,
    zaprojektowany pod szybkie operacje na obu końcach — poznamy go w dalszej
    części kursu. Stos na liście pozostaje w pełni poprawny.
