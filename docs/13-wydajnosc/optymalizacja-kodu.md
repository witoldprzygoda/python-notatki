# Optymalizacja kodu

Narzędzia z poprzedniego podrozdziału wskazują wąskie gardło; ten podrozdział mówi, co z nim zrobić. Zaczynamy od zasad, które chronią przed optymalizowaniem niewłaściwych miejsc, potem przechodzimy do wyboru struktury danych — największego źródła przyspieszeń w zwykłym kodzie — i idiomów, które CPython wykonuje szybko. Domykamy zapowiedź z rozdziału 10, mierząc pamięć zajmowaną przez obiekty z `__slots__`, a dla dociekliwych zaglądamy do kodu bajtowego modułem `dis`.

## Zasady optymalizacji

1. Najpierw kod poprawny i czytelny, potem szybki.
2. Pomiar **przed** zmianą — `timeit`, `cProfile` — wskazuje wąskie gardło; bez pomiaru optymalizujemy na podstawie przypuszczeń.
3. Poprawiamy jedno miejsce — to, które profiler wskazał — nie cały program.
4. Pomiar **po** zmianie rozstrzyga, czy zmiana pomogła; jeśli nie, cofamy ją.
5. Algorytm i struktura danych przed **mikrooptymalizacją** — drobnymi zmianami zapisu bez zmiany algorytmu: zamiana `O(n²)` na `O(n log n)` daje przy tysiącu elementów stukrotne przyspieszenie, a przy większych danych jeszcze większe; przestawianie instrukcji — kilkuprocentowe.
6. Funkcje wbudowane i biblioteka standardowa (`sorted()`, `sum()`, `collections`) są zwykle szybsze od własnych pętli, bo wykonują się w C.
7. Generatory zamiast list, gdy dane są duże, a przetwarzanie jednoprzebiegowe.
8. Biblioteki numeryczne zamiast pętli w czystym Pythonie, gdy dane są tablicami liczb — ostatni podrozdział.
9. Bez przedwczesnej optymalizacji: kod, który nie jest wąskim gardłem, ma być czytelny, nie szybki.

## Złożoność obliczeniowa i wybór struktury danych

**Złożoność obliczeniowa** (ang. *computational complexity*) opisuje, jak czas operacji rośnie wraz z rozmiarem danych `n`. Zapis `O(1)` oznacza czas stały, niezależny od `n`; `O(n)` — proporcjonalny do `n`; `O(n log n)` — nieco szybciej niż liniowo (tak rośnie czas `sorted()`); `O(n²)` — kwadratowo, co dla stu tysięcy elementów daje dziesięć miliardów kroków. Ta sama operacja ma różną złożoność w różnych strukturach danych, a operator `in` jest najczęstszym przykładem:

```python title="zbior-a-lista.py"
import timeit

n = 100_000
lista = list(range(n))
zbior = set(lista)
slownik = {liczba: True for liczba in lista}

for nazwa, kolekcja in [("lista", lista), ("zbior", zbior), ("slownik", slownik)]:
    czas = timeit.timeit("n - 1 in kolekcja", globals={"n": n, "kolekcja": kolekcja}, number=1000)
    print(f"{nazwa:8} {czas / 1000 * 1e6:10.3f} µs na sprawdzenie")
```

```{ .text .no-copy }
lista       489.557 µs na sprawdzenie
zbior         0.043 µs na sprawdzenie
slownik       0.043 µs na sprawdzenie
```

Lista sprawdza elementy po kolei — `O(n)`, a szukany element jest ostatni — podczas gdy zbiór i słownik z rozdziału 5 obliczają skrót elementu i sięgają od razu we właściwe miejsce — `O(1)`. Ponad dziesięć tysięcy razy szybciej to nie mikrooptymalizacja, lecz inna klasa rozwiązania; wystarczy raz zbudować zbiór z listy. Drugi klasyczny przypadek to kolejka: usuwanie z początku listy przesuwa wszystkie pozostałe elementy, a `deque` z rozdziału [7. Moduły, pakiety i biblioteka standardowa](../07-moduly/biblioteka-standardowa.md#kolejka-dwustronna-deque) robi to w czasie stałym, co zapowiadaliśmy w sekcji [Kolejka i stos](../05-typy-zlozone/lista.md#kolejka-i-stos) rozdziału 5:

```python title="deque-a-lista.py"
import timeit

ustaw_liste = "lista = list(range(100_000))"
ustaw_deque = "from collections import deque; kolejka = deque(range(100_000))"
czas_listy = timeit.timeit("lista.pop(0)", setup=ustaw_liste, number=50_000)
czas_deque = timeit.timeit("kolejka.popleft()", setup=ustaw_deque, number=50_000)
print(f"lista.pop(0) × 50 000:      {czas_listy:.4f} s")
print(f"deque.popleft() × 50 000:   {czas_deque:.4f} s")
print(f"stosunek: {czas_listy / czas_deque:.1f}")
```

```{ .text .no-copy }
lista.pop(0) × 50 000:      0.4103 s
deque.popleft() × 50 000:   0.0009 s
stosunek: 467.1
```

Reguła wyboru: `in` na dużej kolekcji — zbiór lub słownik; kolejka — `deque`; szukanie po kluczu — słownik zamiast listy krotek; dostęp przez indeks i dopisywanie na końcu — lista. Wiki Pythona (strona *Time Complexity* na wiki.python.org) zawiera tabelę złożoności operacji dla wszystkich typów wbudowanych.

## Idiomy szybkiego kodu

Kilka konstrukcji CPython wykonuje wyraźnie szybciej od ich „ręcznych” odpowiedników, bo pętla przebiega wewnątrz kodu C zamiast w interpreterze:

```python title="idiomy.py"
import sys
import timeit

slowa = ["python"] * 10_000
czas_plus = timeit.timeit("s = ''\nfor w in slowa:\n    s += w + ' '", globals=globals(), number=100)
czas_join = timeit.timeit("' '.join(slowa)", globals=globals(), number=100)
print(f"konkatenacja +=: {czas_plus:.4f} s, join: {czas_join:.4f} s")

czas_petli = timeit.timeit("wynik = []\nfor x in range(10_000):\n    wynik.append(x * x)", number=200)
czas_zlozenia = timeit.timeit("[x * x for x in range(10_000)]", number=200)
print(f"pętla z append: {czas_petli:.4f} s, złożenie listowe: {czas_zlozenia:.4f} s")

czas_petli = timeit.timeit("suma = 0\nfor x in range(10_000):\n    suma += x", number=200)
czas_sum = timeit.timeit("sum(range(10_000))", number=200)
print(f"pętla sumująca: {czas_petli:.4f} s, sum(): {czas_sum:.4f} s")

print(f"lista kwadratów: {sys.getsizeof([x * x for x in range(1_000_000)]) / 1e6:.1f} MB, generator: {sys.getsizeof(x * x for x in range(1_000_000))} B")
```

```{ .text .no-copy }
konkatenacja +=: 0.0719 s, join: 0.0029 s
pętla z append: 0.0580 s, złożenie listowe: 0.0473 s
pętla sumująca: 0.0364 s, sum(): 0.0119 s
lista kwadratów: 8.4 MB, generator: 208 B
```

Cztery idiomy warte zapamiętania:

- **`str.join()` zamiast `+=` w pętli.** Łańcuchy są niemodyfikowalne (rozdział 3), więc `+=` w ogólności tworzy nowy łańcuch — CPython potrafi w prostych przypadkach rozszerzyć go w miejscu, ale to szczegół implementacji; `join()` oblicza długość wyniku raz, kopiuje każdy fragment raz i wykonuje całą pętlę w C.
- **Złożenia listowe zamiast pętli z `append()`.** Zysk jest umiarkowany — kilkanaście procent — bo obie wersje wykonują wyrażenie `x * x` w interpreterze; ważniejsza jest czytelność. Złożenia zagnieżdżone i z wieloma warunkami lepiej jednak zapisać pętlą — składnię z rozdziału 5 stosujemy, dopóki mieści się w jednym czytelnym wierszu.
- **Funkcje wbudowane zamiast pętli.** `sum()`, `min()`, `max()`, `sorted()`, `any()`, `all()` iterują w C — trzykrotne przyspieszenie względem pętli sumującej, mniejsze niż przy `join()`, bo pętla w Pythonie wykonuje tu tylko jedno dodawanie na obrót; `map()` i `filter()` z rozdziału 6 również, o ile przekazana funkcja jest wbudowana.
- **Generatory zamiast list przy jednym przejściu.** Lista miliona kwadratów zajmuje osiem megabajtów samych referencji, generator — dwieście bajtów; `sum(x * x for x in ...)` nie tworzy listy w ogóle.

Do listy idiomów należy jeszcze **memoizacja** z rozdziału [6. Funkcje](../06-funkcje/dekoratory.md#memoizacja) i `functools.cache` z rozdziału 7: gdy funkcja jest wywoływana wielokrotnie z tymi samymi argumentami i nie ma efektów ubocznych, pamięć podręczna zamienia obliczenie w odczyt ze słownika — jak w porównaniu wersji Fibonacciego z poprzedniego podrozdziału. Warunkiem są haszowalne argumenty i wynik zależny wyłącznie od nich.

Nieco kosztu dodają też mechanizmy obiektowe z poprzednich rozdziałów, o czym warto wiedzieć, choć rzadko ma to znaczenie: właściwości i deskryptory z rozdziałów 10 i 11 zamieniają dostęp do atrybutu w wywołanie funkcji, metody porównań dopisane przez `functools.total_ordering` są wolniejsze od napisanych wprost, a `isinstance()` z protokołem oznaczonym `@runtime_checkable` z rozdziału 12 sprawdza obecność każdej wymaganej metody. Żaden z tych kosztów nie uzasadnia rezygnacji z czytelnego mechanizmu, dopóki profiler nie wskaże go jako wąskiego gardła.

## Pamięć — `__slots__` z pomiarem

Rozdział [10. Klasy i obiekty](../10-klasy/atrybuty-i-metody.md#atrybut-__slots__) zapowiedział pomiar oszczędności, jaką daje `__slots__`. Najprostsza metoda — `sys.getsizeof()` instancji — zawodzi:

```python title="slots-pamiec.py"
import sys
import timeit
import tracemalloc


class Punkt:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class PunktSlots:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y


p, s = Punkt(1, 2), PunktSlots(1, 2)
print(f"getsizeof: {sys.getsizeof(p)} B a {sys.getsizeof(s)} B; słownik instancji: {sys.getsizeof(p.__dict__)} B")

for klasa in (Punkt, PunktSlots):
    tracemalloc.start()
    obiekty = [klasa(i, i) for i in range(100_000)]
    biezace, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{klasa.__name__:11} 100 000 obiektów: {biezace / 1e6:5.1f} MB, ok. {round(biezace / 100_000):3} B na obiekt")
    del obiekty

for obiekt in (p, s):
    czas = timeit.timeit("obiekt.x", globals={"obiekt": obiekt}, number=1_000_000)
    print(f"odczyt atrybutu {type(obiekt).__name__:11} × 1 000 000: {czas:.3f} s")
```

```{ .text .no-copy }
getsizeof: 48 B a 48 B; słownik instancji: 296 B
Punkt       100 000 obiektów:  12.8 MB, ok. 128 B na obiekt
PunktSlots  100 000 obiektów:   8.8 MB, ok.  88 B na obiekt
odczyt atrybutu Punkt       × 1 000 000: 0.020 s
odczyt atrybutu PunktSlots  × 1 000 000: 0.010 s
```

Obie instancje mają według `getsizeof()` po 48 bajtów, bo od Pythona 3.11 słownik atrybutów instancji jest tworzony leniwie i przechowywany osobno — `getsizeof()` go nie wlicza, a odczyt `p.__dict__` w naszym przykładzie dopiero go materializuje (stąd 296 bajtów). Prawdziwy koszt pokazuje `tracemalloc` na stu tysiącach obiektów: około 128 bajtów na zwykły obiekt i 88 na obiekt z `__slots__` — w obu liczbach mieści się jeszcze ok. 40 B na obiekt `int` przekazany do `__init__` i miejsce w liście, więc same instancje zajmują ok. 88 i 48 B: `__slots__` oszczędza tu blisko połowę, a przy większej liczbie atrybutów więcej. Dostęp do atrybutu jest szybszy o połowę. Obie różnice mają znaczenie dopiero przy milionach obiektów; w klasach danych z rozdziału [12. Programowanie obiektowe — mechanizmy zaawansowane](../12-oop-zaawansowane/klasy-danych.md#opcje-frozen-order-slots-i-kw_only) ten sam efekt daje opcja `slots=True`.

## Kod bajtowy — moduł `dis` (dla dociekliwych)

Interpreter CPython nie wykonuje kodu źródłowego wprost: kompilator zamienia go w **kod bajtowy** (ang. *bytecode*) — ciąg prostych instrukcji zapisywanych w plikach `.pyc` w katalogu `__pycache__` z rozdziału 7 — a pętla interpretera wykonuje je jedna po drugiej. Moduł `dis` wypisuje kod bajtowy funkcji i pozwala sprawdzić, czy dwa zapisy są dla interpretera tym samym:

```python title="dis-demo.py"
import dis

iloraz = lambda a, b: a // b


def iloraz_def(a, b):
    return a // b


print(iloraz.__code__.co_code == iloraz_def.__code__.co_code)
dis.dis(iloraz_def)
```

```{ .text .no-copy }
True
  6           RESUME                   0

  7           LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (a, b)
              BINARY_OP                2 (//)
              RETURN_VALUE
```

Atrybut `co_code` obiektu kodu to surowe bajty instrukcji; dla wyrażenia `lambda` i funkcji `def` są identyczne — wybór między nimi to kwestia czytelności i czytelnego śladu wywołań, jak ustaliliśmy w rozdziale 6. Wydruk `dis.dis()` pokazuje instrukcje z numerami wierszy źródłowych: `RESUME` to instrukcja pusta — znacznik początku funkcji dla mechanizmów śledzenia i optymalizacji, `LOAD_FAST_BORROW_LOAD_FAST_BORROW` odkłada oba parametry na stos w jednej instrukcji, `BINARY_OP 2 (//)` wykonuje dzielenie całkowite, a `RETURN_VALUE` zwraca wynik. Nazwy i zestaw instrukcji zmieniają się między wersjami Pythona — w starszych wersjach ten sam kod dawał `LOAD_FAST` dwukrotnie i `BINARY_FLOOR_DIVIDE`, w 3.11 wprowadzono specjalizację instrukcji według typów argumentów i łączenie częstych par instrukcji (od 3.13 widoczne w wydruku jako `LOAD_FAST_LOAD_FAST`), a w 3.14 — warianty `LOAD_FAST_BORROW`, które nie zwiększają licznika referencji — dlatego kodu bajtowego nie porównujemy między wersjami ani nie traktujemy jako części języka. Moduł `dis` przydaje się w jednym celu: gdy dwie wersje kodu różnią się czasem, a nie wiadomo dlaczego, porównanie instrukcji zwykle pokazuje, która z nich wykonuje więcej pracy.
