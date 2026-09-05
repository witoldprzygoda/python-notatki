# Funkcje jako obiekty

Na stronie [Definiowanie funkcji](definiowanie-funkcji.md#funkcja-jako-obiekt) ustaliliśmy, że nazwa funkcji jest referencją do obiektu klasy `function`, a na stronie [Zasięg nazw i domknięcia](zasieg-nazw-i-domkniecia.md#domkniecia) zwracaliśmy funkcje jako wynik innych funkcji. Ta strona rozwija konsekwencje tego faktu: przekazujemy funkcje jako argumenty, przechowujemy je w kolekcjach, rozpoznajemy obiekty wywoływalne, tworzymy funkcje anonimowe wyrażeniem lambda, piszemy własne funkcje klucza dla `sorted()`, `min()` i `max()` oraz poznajemy zapowiedziane w rozdziale 5 funkcje `map()` i `filter()`.

## Funkcje pierwszej klasy

W Pythonie funkcja jest **obiektem pierwszej klasy** (ang. *first-class object*): można ją przypisać nazwie, przekazać jako argument, zwrócić jako wynik i przechować w kolekcji — tak samo jak liczbę czy listę. Przypisanie `pole = pole_prostokata` na stronie [Definiowanie funkcji](definiowanie-funkcji.md#funkcja-jako-obiekt) i zwracanie funkcji `pomnoz` z fabryki `mnoznik()` w sekcji [Domknięcia](zasieg-nazw-i-domkniecia.md#domkniecia) były pierwszymi przejawami tej własności. Przekazywanie funkcji jako argumentu ilustruje funkcja `zastosuj()`, która wywołuje otrzymaną funkcję na każdym elemencie listy:

```python title="zastosuj.py"
def zastosuj(funkcja, dane):
    """Zwraca listę wyników funkcji dla kolejnych elementów sekwencji dane."""
    return [funkcja(element) for element in dane]


def kwadrat(x):
    """Zwraca kwadrat liczby x."""
    return x * x


print(zastosuj(kwadrat, [1, 2, 3]))
print(zastosuj(abs, [-1, -2, 3]))
print(zastosuj(str.upper, ["ala", "ola"]))
print(zastosuj(len, ["a", "bb", "ccc"]))
```

```{ .text .no-copy }
[1, 4, 9]
[1, 2, 3]
['ALA', 'OLA']
[1, 2, 3]
```

W wywołaniu `zastosuj(kwadrat, [1, 2, 3])` argumentem jest obiekt funkcji `kwadrat` — nazwa bez nawiasów. Zapis `zastosuj(kwadrat(2), [1, 2, 3])` przekazałby wynik wywołania, liczbę `4`, a nie funkcję. Wewnątrz `zastosuj()` parametr `funkcja` jest lokalną nazwą tego samego obiektu, więc `funkcja(element)` wywołuje przekazaną funkcję. Argumentem może być dowolna funkcja jednoargumentowa: własna, wbudowana (`abs`, `len`) albo metoda podana przez nazwę typu (`str.upper`) — dokładnie tak jak w argumencie `key` funkcji `sorted()` z rozdziału [5. Typy złożone](../05-typy-zlozone/lista.md#sortowanie).

Funkcję, która przyjmuje funkcję jako argument albo zwraca funkcję, nazywamy **funkcją wyższego rzędu** (ang. *higher-order function*). Funkcja `zastosuj()` przyjmuje funkcję, `mnoznik()` ją zwraca, a dekoratory z końca rozdziału łączą obie te cechy. <!-- TODO: link po powstaniu strony dekoratory.md -->

Funkcję przekazaną po to, by funkcja wyższego rzędu wywołała ją w odpowiednim momencie swojego wykonania, nazywamy **wywołaniem zwrotnym** (ang. *callback*). W poniższym przykładzie sposób obsługi wartości ujemnej nie jest ustalony w `sumuj()` — określa go kod wywołujący, przekazując własną funkcję `ostrzez` albo wbudowaną `print`:

```python title="wywolanie-zwrotne.py"
def sumuj(dane, zglos):
    """Zwraca sumę sekwencji dane; elementy ujemne przekazuje funkcji zglos."""
    suma = 0
    for element in dane:
        if element < 0:
            zglos(element)
        suma += element
    return suma


def ostrzez(wartosc):
    print("Uwaga: wartość ujemna", wartosc)


print(sumuj([3, -1, 4, -5], ostrzez))
print(sumuj([3, -1, 4, -5], print))
```

```{ .text .no-copy }
Uwaga: wartość ujemna -1
Uwaga: wartość ujemna -5
1
-1
-5
1
```

Ten sam mechanizm spotkamy przy programowaniu interfejsów graficznych, gdzie funkcja powiązana z przyciskiem jest wywoływana po jego naciśnięciu. <!-- TODO: link po powstaniu rozdziału o tkinter -->

Funkcje można też przechowywać w kolekcjach. Lista funkcji pozwala wykonać w pętli serię przekształceń:

```python title="lista-funkcji.py"
def kwadrat(x):
    """Zwraca kwadrat liczby x."""
    return x * x


def szescian(x):
    """Zwraca sześcian liczby x."""
    return x ** 3


for funkcja in [abs, kwadrat, szescian]:
    print(funkcja.__name__, funkcja(-3))
```

```{ .text .no-copy }
abs 3
kwadrat 9
szescian -27
```

Słownik z funkcjami jako wartościami pozwala wybrać operację po kluczu; taki słownik nazywa się **tablicą rozdzielczą** (ang. *dispatch table*) i zastępuje długi łańcuch `if`–`elif`:

```python title="tablica-rozdzielcza.py"
def dodaj(a, b):
    return a + b


def odejmij(a, b):
    return a - b


def pomnoz(a, b):
    return a * b


dzialania = {"+": dodaj, "-": odejmij, "*": pomnoz}

for znak in "+", "-", "*", "/":
    dzialanie = dzialania.get(znak)
    if dzialanie is None:
        print(znak, "nieznane działanie")
    else:
        print(znak, dzialanie.__name__, dzialanie(6, 3))
```

```{ .text .no-copy }
+ dodaj 9
- odejmij 3
* pomnoz 18
/ nieznane działanie
```

Metoda `get()` słownika, poznana w rozdziale [5. Typy złożone](../05-typy-zlozone/slownik.md#metody-sownika), zwraca obiekt funkcji albo `None`, a `dzialanie(6, 3)` wywołuje wybraną funkcję. Dodanie nowego działania sprowadza się do dopisania pary do słownika, bez zmian w pętli.

## Obiekty wywoływalne

Wspólną cechą funkcji zdefiniowanych instrukcją `def`, funkcji wbudowanych i metod jest to, że można je **wywołać**, dopisując nawiasy z argumentami. Każdy taki obiekt nazywamy **obiektem wywoływalnym** (ang. *callable*). Wbudowana funkcja `callable()` sprawdza tę własność:

```{ .python .no-copy }
>>> def kwadrat(x):
...     return x * x
...
>>> callable(kwadrat), callable(len), callable("abc".upper)
(True, True, True)
>>> callable(42), callable("abc"), callable([1, 2])
(False, False, False)
```

Później poznamy także inne rodzaje obiektów wywoływalnych, nie tylko funkcje. <!-- TODO: link po powstaniu rozdziału o klasach --> Wynik `True` nie gwarantuje, że wywołanie się powiedzie — liczba i rodzaj argumentów muszą jeszcze odpowiadać parametrom. Wynik `False` gwarantuje natomiast, że wywołanie zakończy się błędem:

```python title="niewywolywalny.py"
liczba = 42
print(liczba())
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "niewywolywalny.py", line 2, in <module>
    print(liczba())
          ~~~~~~^^
TypeError: 'int' object is not callable
```

Ten sam komunikat, z inną nazwą klasy, spotkaliśmy przy przesłonięciu nazwy wbudowanej `list` w sekcji [Przestrzenie nazw i zasięgi](zasieg-nazw-i-domkniecia.md#przestrzenie-nazw-i-zasiegi). Zwykle oznacza on, że nazwa, którą uważaliśmy za funkcję, wskazuje na inny obiekt — wynik wcześniejszego wywołania albo przesłoniętą nazwę wbudowaną.

Obiektu wywoływalnego wymaga dwuargumentowa forma funkcji `iter()`, zapowiedziana w rozdziale [5. Typy złożone](../05-typy-zlozone/lista.md#elementy-listy). Wywołanie `iter(obiekt_wywoływalny, wartownik)` tworzy iterator, który przy każdym pobraniu elementu wywołuje przekazany obiekt bez argumentów i zwraca wynik — dopóki wynik nie będzie równy wartownikowi. Wtedy iterator kończy się: zgłasza wyjątek `StopIteration`, który pętla `for` obsługuje automatycznie, tak jak przy iteratorach z rozdziału [4. Sterowanie przepływem](../04-sterowanie/petle-i-iteratory.md#iteratory). Obiekt wywoływany bez argumentów zwraca za każdym razem nową wartość tylko wtedy, gdy czerpie ją ze źródła zewnętrznego albo przechowuje stan między wywołaniami. W rozdziale 5 stan przechowywała lista, a obiektem wywoływalnym była jej metoda `kopia.pop`; funkcja bez takiego obiektu musi przechować stan sama — to zadanie dla domknięcia z deklaracją `nonlocal`. Poniżej funkcja `utworz_licznik()` z sekcji [Deklaracje global i nonlocal](zasieg-nazw-i-domkniecia.md#deklaracje-global-i-nonlocal), uzupełniona o docstring:

```python title="wartownik-licznik.py"
def utworz_licznik():
    """Zwraca funkcję zwracającą przy każdym wywołaniu kolejną liczbę od 1."""
    licznik = 0

    def nastepny():
        nonlocal licznik
        licznik += 1
        return licznik

    return nastepny


licz = utworz_licznik()
for numer in iter(licz, 4):
    print(numer)
print(licz())
```

```{ .text .no-copy }
1
2
3
5
```

Iterator wywołał `licz()` czterokrotnie: trzy wyniki przekazał pętli, a czwarty, równy wartownikowi `4`, zakończył iterację i został porzucony — dlatego następne wywołanie `licz()` zwraca `5`. Iterator ten jest jednorazowy, jak wszystkie iteratory poznane dotąd; jego klasa `callable_iterator` jest szczegółem implementacyjnym CPythona. Praktycznym zastosowaniem tej formy jest wczytywanie wierszy od użytkownika aż do słowa kończącego — wbudowana funkcja `input()` z rozdziału [2. Konsola](../02-konsola/konsola-w-praktyce.md#funkcja-input-wczytywanie-danych), wywoływana bez argumentów, zwraca kolejny wpisany wiersz:

```python title="do-slowa-koniec.py"
for wiersz in iter(input, "koniec"):
    print("Dodano:", wiersz)
print("Koniec listy")
```

```{ .text .no-copy }
mleko
Dodano: mleko
chleb
Dodano: chleb
koniec
Koniec listy
```

Wiersze bez przedrostka „Dodano:” są tekstem wpisanym przez użytkownika. Wersja z pętlą `while` wymagałaby dwóch wywołań `input()` — przed pętlą i na jej końcu — instrukcji `break` albo operatora `:=` z rozdziału [4. Sterowanie przepływem](../04-sterowanie/wyrazenia-warunkowe.md#operator-przypisania-w-wyrazeniu) w warunku pętli: `while (wiersz := input()) != "koniec":`.

## Wyrażenie lambda

**Wyrażenie lambda** (ang. *lambda expression*) tworzy obiekt funkcji bez instrukcji `def` i bez nazwy. Zapis `lambda parametry: wyrażenie` jest wyrażeniem, którego wartością jest obiekt klasy `function`; jego wywołanie oblicza wyrażenie po dwukropku i zwraca wynik — tak jak funkcja z pojedynczą instrukcją `return`:

```{ .python .no-copy }
>>> lambda x: x + 1
<function <lambda> at 0x...>
>>> (lambda x: x + 1)(3)
4
>>> nastepna = lambda x: x + 1
>>> nastepna(3)
4
>>> type(nastepna), nastepna.__name__
(<class 'function'>, '<lambda>')
```

Wyrażenie `lambda x: x + 1` samo w sobie tylko tworzy obiekt; nawiasy wokół niego i argument `(3)` wywołują ten obiekt natychmiast. Funkcje utworzone wyrażeniem lambda nazywa się **anonimowymi** (ang. *anonymous function*): atrybut `__name__` ma u nich wartość `'<lambda>'` niezależnie od nazwy, której obiekt ewentualnie przypiszemy — przypisanie `nastepna = …` posłużyło wyżej jedynie do obejrzenia atrybutów. Dokumentacja języka opisuje wyrażenie `lambda x: x + 1` jako równoważne definicji:

```{ .python .no-copy }
def <lambda>(x):
    return x + 1
```

Lista parametrów podlega tej samej gramatyce, którą opisuje strona [Argumenty i parametry](argumenty-i-parametry.md): wartości domyślne, `*args`, `**kwargs`, parametry tylko pozycyjne i tylko nazwane; może być też pusta:

```{ .python .no-copy }
>>> (lambda x, y=10: x + y)(1)
11
>>> (lambda *args: sum(args))(1, 2, 3)
6
>>> (lambda x, *, y: x + y)(1, y=2)
3
>>> (lambda: 42)()
42
```

Ograniczenie dotyczy ciała: po dwukropku stoi dokładnie jedno wyrażenie. Nie ma w nim miejsca na instrukcje — przypisanie znakiem `=`, `return`, `if` w formie instrukcji, pętle — ani na docstring i adnotacje; zapis `lambda x: return x` jest błędem `SyntaxError: invalid syntax`. Dozwolony jest natomiast operator trójskładnikowy z rozdziału [4. Sterowanie przepływem](../04-sterowanie/wyrazenia-warunkowe.md#operator-trojskadnikowy), np. `lambda x: "parzysta" if x % 2 == 0 else "nieparzysta"`. Funkcję wymagającą więcej niż jednego wyrażenia definiujemy instrukcją `def`.

PEP 8 zaleca, by nie przypisywać wyrażenia lambda nazwie, lecz użyć instrukcji `def`; pylint zgłasza takie przypisanie jako *unnecessary-lambda-assignment* z tym samym zaleceniem. Powód widać w śladzie wywołań: funkcja anonimowa jest w nim opisana jako `<lambda>`, a funkcja z `def` — własną nazwą:

```python title="lambda-traceback.py"
dziel = lambda a, b: a / b
print(dziel(2, 0))
```

```{ .text .no-copy }
Traceback (most recent call last):
  File "lambda-traceback.py", line 2, in <module>
    print(dziel(2, 0))
          ~~~~~^^^^^^
  File "lambda-traceback.py", line 1, in <lambda>
    dziel = lambda a, b: a / b
                         ~~^~~
ZeroDivisionError: division by zero
```

Po zamianie pierwszego wiersza na definicję `def dziel(a, b): return a / b` drugi wpis śladu brzmiałby `in dziel`. Jedyną przewagą wyrażenia lambda nad instrukcją `def` jest możliwość osadzenia go wewnątrz większego wyrażenia — i tam jest jego właściwe miejsce: jako argument funkcji wyższego rzędu (funkcja klucza, wywołanie zwrotne) albo wartość w tablicy rozdzielczej, np. `{"*": lambda a, b: a * b}`, gdy krótka funkcja jest potrzebna tylko raz.

Wyrażenie lambda umieszczone w ciele funkcji tworzy domknięcie na tych samych zasadach co zagnieżdżona instrukcja `def` — fabrykę `mnoznik()` z sekcji [Domknięcia](zasieg-nazw-i-domkniecia.md#domkniecia) można zapisać jako `return lambda wartosc: wartosc * przez`. Jak każda funkcja, funkcja anonimowa odczytuje zmienne wolne dopiero przy wywołaniu, dotyczy jej więc [późne wiązanie nazw](zasieg-nazw-i-domkniecia.md#pozne-wiazanie-nazw) — niezależnie od tego, czy zmienna wolna jest nazwą globalną, jak w poniższej pętli, czy zmienną domknięcia:

```python title="lambda-w-petli.py"
funkcje = []
for i in range(3):
    funkcje.append(lambda: i)
print([f() for f in funkcje])

funkcje = []
for i in range(3):
    funkcje.append(lambda i=i: i)
print([f() for f in funkcje])
```

```{ .text .no-copy }
[2, 2, 2]
[0, 1, 2]
```

Trzy funkcje anonimowe odczytują zmienną wolną `i` dopiero przy wywołaniu, po zakończeniu pętli; wartość domyślna `i=i`, obliczana w chwili tworzenia funkcji, utrwala bieżącą wartość. Dokumentacja Pythona omawia ten przypadek w sekcji FAQ i zaznacza, że zachowanie nie jest szczególną cechą wyrażeń lambda, lecz dotyczy również zwykłych funkcji — co pokazaliśmy na poprzedniej stronie.

## Funkcja klucza w sorted, min i max

W rozdziale [5. Typy złożone](../05-typy-zlozone/lista.md#sortowanie) argument `key` funkcji `sorted()` i metody `sort()` przyjmował gotowe obiekty wywoływalne: funkcję `len` i metodę `str.lower`. Taki obiekt nazywa się **funkcją klucza** (ang. *key function*): sortowanie wywołuje ją dokładnie raz dla każdego elementu i porównuje zwrócone wartości zamiast samych elementów, przy czym w wyniku pozostają elementy oryginalne. Teraz możemy podać funkcję własną — nazwaną albo anonimową:

```python title="klucz.py"
def ostatnia_litera(slowo):
    """Zwraca ostatni znak słowa."""
    return slowo[-1]


slowa = ["Python", "jest", "super", "!"]
print(sorted(slowa, key=ostatnia_litera))
print(sorted(slowa, key=lambda slowo: slowo[-1]))
print(sorted(slowa, key=lambda slowo: (len(slowo), slowo)))
print(min(slowa, key=len), max(slowa, key=len))
```

```{ .text .no-copy }
['!', 'Python', 'super', 'jest']
['!', 'Python', 'super', 'jest']
['!', 'jest', 'super', 'Python']
! Python
```

Dwa pierwsze wywołania są równoważne; wersja z wyrażeniem lambda jest zwięzła, bo funkcja klucza jest potrzebna tylko w tym jednym miejscu. W trzecim wywołaniu funkcja klucza zwraca krotkę. Krotki — podobnie jak listy i łańcuchy — są porównywane leksykograficznie (ang. *lexicographic order*), jak wyrazy w porządku alfabetycznym: decyduje pierwszy element, a przy równych pierwszych elementach drugi. Słowa są więc uporządkowane według długości, a słowa równej długości alfabetycznie. Funkcje `min()` i `max()` przyjmują argument `key` na tych samych zasadach: `max(slowa, key=len)` zwraca najdłuższe słowo, a nie jego długość.

Funkcja klucza rozstrzyga też, jak uporządkować słownik — po kluczach, po wartościach albo po parach:

```python title="klucz-slownik.py"
oceny = {"Ala": 5, "Bartek": 2, "Celina": 4}
print(max(oceny, key=oceny.get))
print(sorted(oceny, key=oceny.get))
print(sorted(oceny.items(), key=lambda para: para[1], reverse=True))
print(dict(sorted(oceny.items(), key=lambda para: para[1])))
```

```{ .text .no-copy }
Ala
['Bartek', 'Celina', 'Ala']
[('Ala', 5), ('Celina', 4), ('Bartek', 2)]
{'Bartek': 2, 'Celina': 4, 'Ala': 5}
```

Iteracja po słowniku daje kolejne klucze, więc `max(oceny, key=oceny.get)` porównuje wartości `oceny.get("Ala")`, `oceny.get("Bartek")`, `oceny.get("Celina")` i zwraca klucz z największą wartością — metoda `oceny.get`, podana bez nawiasów, jest obiektem wywoływalnym tak jak funkcja. Widok `items()` daje pary, których drugi element wskazujemy funkcją anonimową; wywołanie `dict()` na posortowanej liście par buduje nowy słownik uporządkowany według wartości, ponieważ słownik zachowuje kolejność wstawiania.

Kierunek sortowania ustala argument `reverse`, a przy kluczu liczbowym także znak minus w funkcji klucza; połączenie obu technik pozwala sortować malejąco po jednym składniku i rosnąco po drugim:

```python title="klucz-krotki.py"
studenci = [("Celina", 4.5), ("Bartek", 3.0), ("Ala", 4.5)]
print(max(studenci, key=lambda student: student[1]))
print(sorted(studenci, key=lambda student: student[1], reverse=True))
print(sorted(studenci, key=lambda student: (-student[1], student[0])))
```

```{ .text .no-copy }
('Celina', 4.5)
[('Celina', 4.5), ('Ala', 4.5), ('Bartek', 3.0)]
[('Ala', 4.5), ('Celina', 4.5), ('Bartek', 3.0)]
```

Przy równych ocenach `max()` zwraca pierwszy napotkany element, a sortowanie z `reverse=True` zachowuje pierwotną kolejność elementów o równym kluczu — jest stabilne, jak opisano w rozdziale 5. Klucz złożony z oceny ze znakiem minus i imienia porządkuje oceny malejąco, a studentów o tej samej ocenie według imienia rosnąco.

## Funkcje map() i filter()

Zapowiedziane przy [wyrażeniu generatorowym](../05-typy-zlozone/zlozenia.md#wyrazenie-generatorowe) funkcje `map()` i `filter()` są wbudowanymi funkcjami wyższego rzędu. Wywołanie `map(funkcja, iterowalny)` zwraca iterator, który przy pobieraniu kolejnych elementów stosuje funkcję do kolejnych elementów obiektu iterowalnego:

```{ .python .no-copy }
>>> m = map(str.upper, ["ala", "ola"])
>>> m
<map object at 0x...>
>>> type(m)
<class 'map'>
>>> next(m)
'ALA'
>>> list(m)
['OLA']
>>> list(m)
[]
```

Obiekt klasy `map` jest iteratorem takim jak wyniki `enumerate()` i `zip()`: obsługuje `next()`, nie obsługuje `len()` (wywołanie `len(m)` zgłasza `TypeError: object of type 'map' has no len()`) i jest jednorazowy — po wyczerpaniu drugie wywołanie `list(m)` zwraca pustą listę. Nie jest generatorem; termin ten rezerwujemy dla wyrażenia generatorowego oraz funkcji generatorowej, którą poznamy w dalszej części rozdziału. <!-- TODO: link po powstaniu strony funkcje-generatorowe.md --> Gdy wynik jest potrzebny w całości, przekazujemy iterator funkcji `list()` albo innej funkcji przyjmującej obiekt iterowalny:

```python title="map-typowe.py"
print(list(map(int, "3 14 15".split())))
print(" ".join(map(str, [3, 14, 15])))
print(sum(map(len, ["ab", "cde", "f"])))
print(list(map(round, [3.14159, 3.14159, 3.14159], range(1, 4))))
```

```{ .text .no-copy }
[3, 14, 15]
3 14 15
6
[3.1, 3.14, 3.142]
```

Dwa pierwsze wiersze to częste idiomy konwersji: łańcuchy z `input()` na liczby i liczby na łańcuchy przed `join()`. Ostatni pokazuje, że `map()` przyjmuje więcej obiektów iterowalnych, jeśli funkcja ma tyle samo parametrów — `round()` otrzymuje kolejno pary `(3.14159, 1)`, `(3.14159, 2)`, `(3.14159, 3)`. Jak `zip()` z rozdziału [5. Typy złożone](../05-typy-zlozone/krotka.md#funkcja-zip), iterator kończy się wraz z najkrótszym obiektem; wbudowana funkcja `pow(a, b)` oblicza `a ** b`:

```python title="map-strict.py"
print(list(map(pow, [2, 3, 4], [3, 2])))
print(list(map(pow, [2, 3, 4], [3, 2], strict=True)))
```

```{ .text .no-copy }
[8, 9]
Traceback (most recent call last):
  File "map-strict.py", line 2, in <module>
    print(list(map(pow, [2, 3, 4], [3, 2], strict=True)))
          ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: map() argument 2 is shorter than argument 1
```

!!! note "Parametr strict od Pythona 3.14"
    Argument `strict=True`, znany z `zip()` od Pythona 3.10, funkcja `map()` przyjmuje
    od wersji 3.14. Przy różnych długościach obiektów iterowalnych iterator zgłasza
    wyjątek `ValueError`, zamiast bez ostrzeżenia skracać wynik do długości
    najkrótszego z nich. Wyjątek pojawia się dopiero przy pobieraniu elementów — tu
    wewnątrz `list()` — a nie w chwili wywołania `map()`, bo do tego momentu iterator
    niczego nie oblicza. W starszych wersjach Pythona wywołanie z tym argumentem
    kończy się błędem `TypeError: map() takes no keyword arguments`, ponieważ
    `map()` nie przyjmowała wówczas żadnych argumentów nazwanych.

Wywołanie `filter(funkcja, iterowalny)` zwraca iterator klasy `filter` przekazujący dalej tylko te elementy, dla których funkcja zwróciła wartość prawdziwą. Funkcja `filter()` przyjmuje dokładnie jeden obiekt iterowalny; w miejsce funkcji można podać `None` — wtedy iterator przekazuje dalej elementy, których wartość logiczna jest prawdziwa, co usuwa z kolekcji wartości fałszywe według katalogu z rozdziału [3. Nazwy i typy](../03-nazwy-typy/typy-proste.md#typ-bool):

```python title="filter.py"
liczby = [3, -1, 0, 7, -5]
print(list(filter(lambda x: x > 0, liczby)))
print(list(filter(str.isdigit, ["12", "ab", "7"])))
print(list(filter(None, [0, 1, "", "ala", None, [], [1]])))
```

```{ .text .no-copy }
[3, 7]
['12', '7']
[1, 'ala', [1]]
```

W drugim wywołaniu rolę funkcji filtrującej pełni metoda `str.isdigit()`, sprawdzająca, czy łańcuch składa się wyłącznie z cyfr. To samo zadanie — kwadraty liczb parzystych — można zapisać przez `map()` i `filter()` z dwiema funkcjami anonimowymi albo złożeniem listowym:

```python title="map-filter-zlozenie.py"
dane = [1, 2, 3, 4, 5, 6]
print(list(map(lambda x: x * x, filter(lambda x: x % 2 == 0, dane))))
print([x * x for x in dane if x % 2 == 0])
print(list(map(str.upper, ["ala", "ola"])))
print([slowo.upper() for slowo in ["ala", "ola"]])
```

```{ .text .no-copy }
[4, 16, 36]
[4, 16, 36]
['ALA', 'OLA']
['ALA', 'OLA']
```

Dokumentacja Pythona opisuje `filter(funkcja, iterowalny)` jako równoważne wyrażeniu generatorowemu `(x for x in iterowalny if funkcja(x))`. Gdy funkcję trzeba by dopiero utworzyć wyrażeniem lambda, złożenie jest zwykle czytelniejsze; `map()` i `filter()` są wygodne, gdy potrzebna funkcja już istnieje, jak w `map(int, …)` czy `filter(str.isdigit, …)`. Obie funkcje pochodzą ze stylu **programowania funkcyjnego** (ang. *functional programming*), w którym dąży się do składania obliczeń z funkcji zwracających wynik zależny wyłącznie od argumentów i niewywołujących skutków ubocznych (ang. *side effect*), czyli niezmieniających obiektów spoza własnej przestrzeni lokalnej i niewykonujących operacji wejścia-wyjścia — takie funkcje nazywa się **czystymi** (ang. *pure function*); `kwadrat()` jest funkcją czystą, a `ostrzez()`, która wypisuje tekst, nie jest. Kolejne narzędzia tego stylu — funkcje `reduce()` i `partial()` z modułu `functools`, moduły `operator` i `itertools` — poznamy wraz z biblioteką standardową w następnym rozdziale. <!-- TODO: link po powstaniu rozdziału o modułach -->
