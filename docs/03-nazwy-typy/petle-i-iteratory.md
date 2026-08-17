# Pętle i iteratory

## Pętla for

Chyba najpopularniejsza struktura językowa, w wersji po pełnym zakresie jakiegoś obiektu złożonego (kontenera, tablicy) — tutaj na przykładzie łańcucha znakowego:

```python
a = "abcdefgh"
for i in a:
    print(i, end=" ")
# a b c d e f g h
```

Obiekt o nazwie `i` (przyzwyczajenie — możemy użyć dowolnej nazwy) staje się na moment jednej iteracji referencją do poszczególnych obiektów (tu jednoliterowych łańcuchów znakowych); każdy z nich ma swoje (chwilowe) miejsce w pamięci.

Pętla for w Pythonie posiada również wersję **for… else**, gdzie blok else wykonany zostanie, gdy pętla całkowicie zakończy swoje działanie (nie zostanie przerwana np. przez break). `else` powinien być w takim samym wcięciu co `for` — na co trzeba uważać zwłaszcza, gdy dana pętla for jest zagnieżdżona wewnątrz innej pętli.

```python
for i in "abc":
    print(i, end=" ")
else:
    print("poprawny koniec")
# a b c poprawny koniec
```

Zazwyczaj jesteśmy przyzwyczajeni do pętli, która używa jakiejś zmiennej indeksującej. Nie jest to konieczne, ale jeśli potrzebujemy dodatkowo indeksu, najlepiej użyć wbudowanej funkcji `enumerate()`. Zwraca ona sekwencję par argumentów — oba można pobrać w pętli (jest to przykład rozpakowywania przekazanych danych):

```python
a = "abcdefgh"
for i, j in enumerate(a):
    print(i, j, end="; ")
# 0 a; 1 b; 2 c; 3 d; 4 e; 5 f; 6 g; 7 h;
```

Funkcja `enumerate()` posiada również nazwany argument `start`, za pomocą którego możemy zdefiniować początkową wartość (różną od domyślnego 0), czyli `enumerate(a, start=1)`.

A co, jeśli w kodzie pętli nie wpiszemy dwóch obiektów i, j — tylko jeden?

```python
a = "abcdefgh"
for i in enumerate(a):
    print(i, end="; ")
```

Kod jest nadal całkowicie poprawny, ale obiektowi `i` będą przypisane krotki (class 'tuple'), czyli pary wartości: `(0, 'a'); (1, 'b'); …`, które można również „rozpakować” poprzez przypisanie do dwóch nazwanych obiektów, czyli np. `x, y = i`. Typ tuple omówimy później.

Funkcja `enumerate()` zwraca **typ iterowalny**, czyli taki, po którym może przejść iterator, wydobywając kolejne elementy. Przejście iteratora jest **jednorazowe** — raz odczytany element jest usuwany z obiektu zwróconego przez enumerate().

<!-- TODO: przykłady z PDF (zrzuty): dwukrotna pętla po iteratorze; rozpakowanie
     do listy tylko raz; sum(1 for _ in x) -->

Znaczek podkreślenia `_` użyty w pętli for to nie jest żaden tajemny trik, tylko zwykła nazwa zmiennej. Jest taki obyczaj, że znaczkiem `_` nazywamy obiekty, których zawartości de facto nie potrzebujemy.

## Generator range

Funkcja `range()` to typ generatora zwracającego sekwencję liczb całkowitych. (W zewnętrznym module NumPy dostępna jest również wersja dla wartości zmiennoprzecinkowych.) Składnia range() zawiera do trzech parametrów. Z jednym parametrem oznacza, ile elementów (zaczynając od 0, z krokiem 1) wygenerować: `range(5)` wyprodukuje 0, 1, 2, 3, 4 — ale jeśli ich nie „rozpakujemy”, zobaczymy tylko obiekt range. Dlaczego nie widzimy sekwencji liczb? Ponieważ generatory są w Pythonie mechanizmem **leniwej ewaluacji** funkcji, która w przeciwnym razie musiałaby zwracać obciążającą pamięć lub kosztowną w obliczaniu listę.

Z dwoma parametrami podajemy zakres od–do (wyłączając górną wartość, z krokiem 1). Z trzema — możemy dodatkowo podać krok. Krok może być ujemny (od większej wartości do mniejszej).

Generator jest obiektem przechowującym stan, mogącym wielokrotnie wchodzić do i opuszczać ten sam dynamiczny zakres. Da się wydobyć z generatora wszystkie elementy — np. utworzyć obiekt złożony; dla listy wyglądałoby to tak: `i = list(range(5))`.

Do elementów z generatora można odnieść się przez indeks, można też użyć selekcji zakresowych. Wynikiem będzie albo `int`, albo kolejny obiekt range. Można też w ten sposób odwrócić kolejność.

<!-- TODO: przykłady z PDF (zrzuty): range z indeksami/slicing, odwrócenie -->

## Iteratory a generatory

Kolejność można odwrócić również za pomocą wbudowanej funkcji `reversed()` — zwraca ona obiekt typu iterowalnego (class 'range_iterator').

!!! note "Iterator vs generator"
    Czym się różni obiekt iterowalny od obiektu generatora? Obydwa stosują strategię
    leniwej ewaluacji. Jednak obiekt generatora jest dostępny bez ograniczeń — możemy
    przez niego przechodzić wielokrotnie, sprawdzić wielkość, odwołać się przez indeks.
    Przejście przez iterator może być wykonane **tylko raz**. Iterator może być
    przekazany do funkcji `next()`, która zwraca (konsumuje) kolejne obiekty, aż na
    koniec zgłosi wyjątek. Obiektu generatora nie da się przekazać do next().

<!-- TODO: przykłady z PDF (zrzuty): dwa przejścia po range vs jedno po reversed();
     next() na iteratorze -->

Czy można reversed() wykorzystać do odwrócenia i porównania łańcucha znakowego (czy jest palindromem)? Można, ale ponieważ reversed() tworzy iterator (leniwa ewaluacja), nie można go ot tak porównać. Natomiast można sprytnie wykonać iterację i połączenie elementów za pomocą funkcji `join()`. Działa ona na obiekcie typu str, który będzie **separatorem** poszczególnych elementów, po których iterujemy. Stosując pusty łańcuch jako separator, wytworzymy łańcuch znakowy z obiektu iteratora — i wtedy sprawdzenie palindromu (np. słowa KayaK) się powiedzie. Pamiętajmy jednak, że przebiegnięcie po iteratorze jest jednorazowe — drugie porównanie da False.

<!-- TODO: przykłady z PDF (zrzuty): join z separatorem "---", palindrom KayaK,
     drugie porównanie False, palindrom przez slicing -->

## Pętla while

Dopóki warunek logiczny jest spełniony, blok należący do while (czyli odpowiednio wcięty) jest wykonywany.

```python
gwiazdki = "*"*10
while gwiazdki:   # odwrócona połówka trójkąta
    print(gwiazdki)
    gwiazdki = gwiazdki[1:]   # obcinamy pierwszą gwiazdkę
```

Pętla while posiada również możliwość dodania bloku `else:` po całkowitym jej wykonaniu — czyli jeśli nie zostanie przerwana za pomocą break:

```python
a = 1
while a < 3:
    print("a = ", a, end=" ")
    a += 1
else:
    print("wykonano!")
# a = 1 a = 2 wykonano!
```

## Break, continue, pass

Są to słowa kluczowe języka Python, których znaczenie zapewne dobrze znamy. Kilka przykładów ilustrujących działanie:

```python
for n in range(2, 12):
    for x in range(2, n):
        if n % x == 0:
            print(n, " rowna sie ", x, '*', n//x)
            break
    else:
        # to jest wyswietlone gdy petla for sie zakonczy
        print(n, " jest liczba pierwsza")
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

```python
for num in range(2, 10):
    if num % 2 == 0:
        print("Liczba parzysta", num)
        continue   # opuszczenie reszty iteracji za continue
    print("Liczba nieparzysta", num)
```

Powyższy program sprawdza, czy liczba ma resztę z dzielenia przez 2 — jeśli nie ma, to jest parzysta i dalsza część kodu nie jest wykonywana po wydaniu komendy continue (przeskoczenie do końca bloku danej iteracji i przejście do kolejnej).

```python
while True:
    pass   # pusta instrukcja
```

Powyższa pętla jest nieskończona, aż do zatrzymania programu za pomocą ++ctrl+c++. Komendę `pass` używa się często w kodzie, który później zostanie napisany, a początkowo wymaga instrukcji pustej.
