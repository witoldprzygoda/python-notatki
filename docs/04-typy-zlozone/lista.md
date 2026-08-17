# Lista

Lista jest przykładem kontenera o **modyfikowalnej** zawartości. Listę w zapisie rozpoznajemy po prostokątnych nawiasach, elementy oddzielone przecinkami, co naturalnie upodabnia ten kontener do tablicy. Lista może mieć elementy różnych typów, łącznie z typami złożonymi — czyli np. zagnieżdżoną kolejną listą.

## Tworzenie listy

Podstawowe operacje na obiektach listy są podobne do tych dla typu str. Listy można powielać przez mnożenie, dodawać.

<!-- TODO: przykład z PDF (zrzut): mnożenie i dodawanie list -->

Na liście można wykonywać selekcję („slicing”), ale nową rzeczą jest fakt, że wybrany przez taką selekcję fragment listy może być **zmodyfikowany lub usunięty**:

```python
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
letters[2:5] = ['C', 'D', 'E']   # podmiana
letters[2:5] = []                # usunięcie ich
letters[:] = []                  # cała lista
len(letters)                     # długość, ale uwaga: na poziomie głównym
```

Listę tworzymy zazwyczaj przez wymienienie elementów w prostokątnym nawiasie, ale równie często korzysta się z konstruktora — ten wymaga **dokładnie jednego argumentu**; można taką operację postrzegać jako operator konwersji na typ list. W środku mogą być obiekty w „różnych nawiasach”, ale również generatory czy iteratory. A jeśli argumentem będzie łańcuch znakowy, zostanie stworzona lista z poszczególnych znaków. Ilustracja:

```python
lista = ["aa", "cc", "bb"]
# lista = list("aa", "cc", "bb")   # błąd
lista = list(["aa", "cc", "bb"])   # [] list
lista = list(("aa", "cc", "bb"))   # () tuple
lista = list({"aa", "cc", "bb"})   # {} set
```

Lista może zawierać elementy różnych typów, nawet obiekty generatora czy iteratora. Jak pamiętamy, odczytanie iteratora oznacza skasowanie jego zawartości.

Można oczywiście zagnieżdżać obiekty. Ciekawym przypadkiem jest zagnieżdżenie listy w samej sobie… co prowadzi do „niekończącej się” rekurencji w głąb (widać to podczas „slicingu” tak powstałego obiektu). Można by napisać funkcję, w której wykonujemy pętlę po kolejnych elementach listy, sprawdzając ich typ, oraz — gdy się okaże, że typ elementu to lista (warunek `if isinstance(i, list):`) — rekurencyjnie wywołać funkcję z tym elementem. W ten sposób szybko przekonalibyśmy się, że wykonanie zakończy się błędem typu:

```{ .text .no-copy }
RecursionError: maximum recursion depth exceeded while calling a Python object
```

po wykonaniu blisko 1000 rekurencyjnie zagnieżdżonych wywołań. Temat obsługi rekurencyjnych wywołań i ograniczeń może uda się omówić później (vide: [Tail Recursion Elimination](http://neopythonic.blogspot.com/2009/04/tail-recursion-elimination.html)). W module sys można sprawdzić, na ile zagnieżdżeń ustawiony jest Python.

## Elementy listy

Typowa iteracja po elementach listy to pętla for. Można również sprawdzić, czy interesujący element znajduje się na liście, za pomocą operatora `in`:

```python
lista = ["jeden", "dwa", "trzy"]
if "dwa" in lista:
    print("Tak, 'dwa' jest elementem listy.")
```

Innym sposobem otrzymania elementów listy (i nie tylko) jest **rozpakowanie**. Możliwa jest też operacja odwrotna — zbudowanie listy.

<!-- TODO: przykłady z PDF (zrzuty): rozpakowanie listy; budowanie listy -->

Obiekt listy nie jest iteratorem, ale można taki utworzyć za pomocą funkcji `iter()` — jej pierwszym parametrem jest obiekt sekwencyjny (np. lista), drugim (opcjonalnie) wartość kończąca iterację. Następnie można pobrać kolejne elementy za pomocą `next()`. Aby pobieranie nie skończyło się zgłoszeniem wyjątku, można zdefiniować również w next() element kończący iterację.

<!-- TODO: przykłady z PDF (zrzuty): iter/next z wartownikiem; pętla bez sprawdzenia -->

W badaniu elementów listy (i nie tylko listy) pomocne mogą być dwie funkcje: `all()`, `any()`. Pierwsza zwraca True, gdy **wszystkie** elementy listy mają ewaluowaną wartość logiczną True. Druga — `any()` — zwraca True, gdy **choć jeden** element jest prawdziwy.

## Funkcje składowe listy

Poniżej zwięzły przegląd funkcji należących do typu list — warto się z nimi zapoznać.

**append(element)** — wstawia element na końcu listy. Jeśli lista jest pusta, to jest to jej pierwszy element.

!!! warning "Modyfikowalność w pętli"
    Modyfikowalność obiektu listy może doprowadzić do zaskakujących efektów.
    Na przykład, jeśli w pętli for wykonywanej na obiektach listy będziemy wewnątrz
    pętli dodawać kolejne elementy, to pętla się nie zakończy (przerwanie: ++ctrl+c++).

**extend(&lt;obiekt&gt;)** — dodaje na koniec listy elementy innej wielkości iteracyjnej: listy, krotki, łańcucha znakowego czy generatora range (który jest ewaluowany, produkując zdefiniowaną sekwencję).

**insert(pozycja, element)** — wstawia na wskazanej pozycji element (można wstawiać na początku i na końcu).

**remove(element)** — przeszukuje listę pod kątem wystąpienia elementu i usuwa pierwszy napotkany. Jeśli elementu nie ma na liście, zgłoszony zostaje wyjątek `ValueError`. Aby temu zapobiec, należy przed usunięciem sprawdzić (operatorem `in`), czy dany element jest na liście.

**pop()** — opcjonalnie z argumentem indeks — usuwa wskazany element z listy (bez argumentu: ostatni) i **zwraca** go. Indeks może być również ujemny. Jeśli indeks jest poza zakresem, zgłoszony zostaje wyjątek `IndexError`.

**del** — usuwa wskazany indeksem element lub zakres elementów, albo i całą zawartość. Składnię można użyć jako wywołanie funkcji lub jako operator del przed wybranym zakresem elementów.

<!-- TODO: uzupełnić z PDF (zrzuty przy każdej metodzie) oraz pozostałe metody:
     index(), count(), sort(), reverse(), clear(), copy() -->

## Złożenia listowe (list comprehension)

<!-- TODO: uzupełnić z PDF wstęp do składni [wyrażenie for x in iterowalne if warunek]
     oraz przykład Celsius → Fahrenheit (zrzuty) -->

Jeśli chcemy od razu wynik z określoną precyzją, można skorzystać z funkcji zaokrąglenia `round(wartość, precyzja)`:

```python
Fahrenheit = [round(9/5*x+32, 2) for x in Celsius]
# wynik: [-0.0, 14.0, 32.0, 54.5, 97.88, 100.4, 107.6]
```

Jeśli jednak chodzi o formatowanie wyświetlania, a nie ingerowanie w sam rezultat, można skorzystać z kilku wariantów formatowania typu str. Jedna z możliwości:

```python
newF = [ '%.1f' % x for x in Fahrenheit ]
# wynik: ['-0.0', '14.0', '32.0', '54.5', '97.9', '100.4', '107.6']
```

Jak widać, efektem jest lista obiektów typu str, a nie float. Można jednak wykonać wtórną konwersję:

```python
newF = [ float('%.1f' % x) for x in Fahrenheit ]
# wynik: [-0.0, 14.0, 32.0, 54.5, 97.9, 100.4, 107.6]
```

## Kolejka i stos

W informatyce są wyróżnione pewne proste struktury danych, takie jak kolejka i stos. Ich implementację można bezproblemowo wykonać w oparciu o listę:

```python
# emulacja kolejki (queue)
tab = [1,2,3]
tab.append(x)   # queue.push(x)
tab.pop(0)      # queue.pop()
tab[0]          # queue.peek()

# emulacja stosu (stack)
tab = [1,2,3]
tab.append(x)   # stack.push(x)
tab.pop()       # stack.pop()
tab[-1]         # stack.peek()
```
