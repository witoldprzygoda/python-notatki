# Dziedziczenie wielokrotne i MRO

W rozdziale 10 każda klasa pochodna miała jedną klasę bazową, a kolejność rozstrzygania metod — atrybut `__mro__` — była zwykłym łańcuchem od klasy do `object`. Python pozwala jednak dziedziczyć po kilku klasach naraz. Wtedy kolejność przeszukiwania klas przestaje być oczywista, a funkcja `super()` ujawnia swoje prawdziwe znaczenie. W tym podrozdziale poznajemy składnię dziedziczenia wielokrotnego, problem diamentu, algorytm C3 wyznaczający kolejność rozstrzygania metod — z pełnym przykładem rozpisanym krok po kroku — oraz przypadki, w których spójnej kolejności nie da się zbudować. Dla dociekliwych śledzimy wywołania `__new__` i `__init__` w rozbudowanej hierarchii.

## Wiele klas bazowych

**Dziedziczenie wielokrotne** (ang. *multiple inheritance*) zapisujemy, wymieniając w nawiasie kilka klas bazowych. Klasa pochodna przejmuje metody wszystkich, a przy nazwach obecnych w kilku klasach decyduje kolejność w nawiasie:

```python title="wiele-baz.py"
class Nadajnik:
    def nadaj(self):
        return "nadaję"

    def opis(self):
        return "nadajnik"


class Odbiornik:
    def odbierz(self):
        return "odbieram"

    def opis(self):
        return "odbiornik"


class Radiotelefon(Nadajnik, Odbiornik):
    pass


class Krotkofalowka(Odbiornik, Nadajnik):
    pass


r = Radiotelefon()
print(r.nadaj(), r.odbierz(), r.opis())
print(Krotkofalowka().opis())
print(isinstance(r, Nadajnik), isinstance(r, Odbiornik))
print([klasa.__name__ for klasa in Radiotelefon.__mro__])
```

```{ .text .no-copy }
nadaję odbieram nadajnik
odbiornik
True True
['Radiotelefon', 'Nadajnik', 'Odbiornik', 'object']
```

Metoda `opis()` istnieje w obu klasach bazowych; `Radiotelefon` wybiera wersję z `Nadajnik`, bo ta klasa stoi w nawiasie pierwsza, a `Krotkofalowka` — z `Odbiornik`. Obiekt jest instancją obu klas bazowych. Atrybut `__mro__` z rozdziału 10 pokazuje kolejność, w jakiej Python przeszukuje klasy: najpierw klasa obiektu, potem klasy bazowe w kolejności z nawiasu, na końcu `object`. W tym podrozdziale wypisujemy `__mro__` jako listę nazw — pełna reprezentacja `<class '__main__.Radiotelefon'>` zaciemniałaby przykłady.

## Problem diamentu i kolejność rozstrzygania metod

Trudności pojawiają się, gdy klasy bazowe mają wspólnego przodka. Hierarchia przybiera wtedy kształt rombu — stąd nazwa **problem diamentu** (ang. *diamond problem*): kaczka jest zwierzęciem latającym i zwierzęciem pływającym, a obie te klasy pochodzą od `Zwierze`. Czy `__init__` wspólnego przodka wykona się raz, czy dwa razy, i w jakiej kolejności?

```python title="diament.py"
class Zwierze:
    def __init__(self):
        print("Zwierze.__init__")
        super().__init__()


class Latajace(Zwierze):
    def __init__(self):
        print("Latajace.__init__")
        super().__init__()


class Plywajace(Zwierze):
    def __init__(self):
        print("Plywajace.__init__")
        super().__init__()


class Kaczka(Latajace, Plywajace):
    def __init__(self):
        print("Kaczka.__init__")
        super().__init__()


print([klasa.__name__ for klasa in Kaczka.__mro__])
print(Kaczka.mro() == list(Kaczka.__mro__))
kaczka = Kaczka()
```

```{ .text .no-copy }
['Kaczka', 'Latajace', 'Plywajace', 'Zwierze', 'object']
True
Kaczka.__init__
Latajace.__init__
Plywajace.__init__
Zwierze.__init__
```

Każda klasa wywołuje `super().__init__()` dokładnie raz, a mimo to `Zwierze.__init__` wykonało się tylko raz — na końcu, po obu klasach pośrednich. Odpowiada za to **kolejność rozstrzygania metod** (ang. *method resolution order*, MRO): uporządkowana lista klas, w której każda klasa występuje raz, a klasy pochodne stoją przed swoimi klasami bazowymi. Lista ta jest dostępna jako krotka `__mro__` i przez metodę `mro()` wywoływaną na klasie. Python przeszukuje ją przy każdym dostępie do atrybutu, a `super()` — o czym niżej — przekazuje wywołanie do **następnej** klasy na tej liście, nie do „klasy bazowej”. Dzięki temu w diamencie wspólny przodek stoi za obiema klasami pośrednimi i jest inicjalizowany jeden raz.

## Algorytm C3

Kolejność rozstrzygania metod wyznacza **algorytm C3** — procedura **linearyzacji** (ang. *linearization*) hierarchii, czyli ułożenia jej klas w jednej liście. Dla zwykłych programów wystarczy pamiętać dwie własności wyniku: klasa pochodna zawsze poprzedza swoje klasy bazowe, a klasy bazowe zachowują kolejność z nawiasu. Warto jednak raz prześledzić sam algorytm, bo tylko on tłumaczy przypadki nieoczywiste i komunikat błędu z dalszej sekcji.

Linearyzację klasy `K` oznaczamy `L[K]`; dla klasy bez własnych baz `L[K] = K object`. Dla klasy `K(B1, …, Bn)` obowiązuje wzór:

```{ .text .no-copy }
L[K] = K + merge(L[B1], …, L[Bn], [B1, …, Bn])
```

Operacja `merge` scala listy według reguły czoła i ogona: bierze pierwszy element (**czoło**) pierwszej listy i sprawdza, czy nie występuje w **ogonie** (wszystkich elementach poza pierwszym) którejkolwiek z pozostałych list. Jeśli nie występuje, dopisuje go do wyniku i usuwa ze wszystkich list; jeśli występuje, próbuje czoła następnej listy. Powtarza to, aż listy się wyczerpią — albo aż żadne czoło nie będzie dopuszczalne, co oznacza brak spójnej kolejności. Przykład z siedmioma klasami pokazuje algorytm w całości (klasę `object` pomijamy w zapisie, bo zawsze stoi na końcu):

```python title="c3-siedem-klas.py"
class O:
    pass


class F(O):
    pass


class E(O):
    pass


class D(O):
    pass


class C(D, F):
    pass


class B(D, E):
    pass


class A(B, C):
    pass


for klasa in (C, B, A):
    print(klasa.__name__, [k.__name__ for k in klasa.__mro__])
```

```{ .text .no-copy }
C ['C', 'D', 'F', 'O', 'object']
B ['B', 'D', 'E', 'O', 'object']
A ['A', 'B', 'C', 'D', 'E', 'F', 'O', 'object']
```

Linearyzacje klas bazowych są trywialne: `L[O] = O`, `L[F] = F O`, `L[E] = E O`, `L[D] = D O`. Dla klasy `C` scalamy `L[D]`, `L[F]` i listę baz `D F`:

```{ .text .no-copy }
L[C] = C + merge(D O, F O, D F)
     = C D + merge(O, F O, F)      # czoło D nie występuje w żadnym ogonie
     = C D F + merge(O, O)         # O jest w ogonie listy F O, więc bierzemy F
     = C D F O
L[B] = B + merge(D O, E O, D E)
     = B D E O                     # tak samo jak dla C
L[A] = A + merge(B D E O, C D F O, B C)
     = A B + merge(D E O, C D F O, C)     # B nie występuje w ogonach
     = A B C + merge(D E O, D F O)        # D jest w ogonie C D F O, więc bierzemy C
     = A B C D + merge(E O, F O)          # teraz D jest dopuszczalne
     = A B C D E + merge(O, F O)          # E nie występuje w ogonach
     = A B C D E F + merge(O, O)          # O jest w ogonie F O, więc bierzemy F
     = A B C D E F O
```

Wynik `A B C D E F O` jest uporządkowany zgodnie z poziomami hierarchii: klasy niższe, bardziej wyspecjalizowane, mają pierwszeństwo. Nie zawsze tak jest. Wystarczy w klasie `B` zamienić kolejność baz na `class B(E, D)`, a linearyzacja `A` przyjmie postać `A B E C D F O` — klasa `E`, położona wyżej w hierarchii, wyprzedzi klasę `C`, położoną niżej. Nie rozstrzyga o tym poziom hierarchii, lecz sama procedura scalania: po wybraniu `B` czołem pierwszej listy jest `E`, dopuszczalne, więc trafia do wyniku przed `C`:

```python title="c3-wariant.py"
class O:
    pass


class F(O):
    pass


class E(O):
    pass


class D(O):
    pass


class C(D, F):
    pass


class B(E, D):
    pass


class A(B, C):
    pass


print([k.__name__ for k in B.__mro__])
print([k.__name__ for k in A.__mro__])
```

```{ .text .no-copy }
['B', 'E', 'D', 'O', 'object']
['A', 'B', 'E', 'C', 'D', 'F', 'O', 'object']
```

Rozpisanie tego wariantu pozostawiamy jako ćwiczenie; początek: `L[B] = B E D O`, `L[A] = A + merge(B E D O, C D F O, B C) = A B + merge(E D O, C D F O, C) = A B E + merge(D O, C D F O, C) = …`

## Funkcja `super()` a MRO

Funkcja `super()` z rozdziału 10 nie oznacza „klasy bazowej”, lecz „klasę stojącą — w kolejności rozstrzygania metod **obiektu**, na którym wywołano metodę — bezpośrednio za klasą, w której metodę zapisano”. Przy dziedziczeniu pojedynczym obie interpretacje dają to samo; przy wielokrotnym — nie:

```python title="super-mro.py"
class Baza:
    def __init__(self):
        print("Baza.__init__")
        super().__init__()


class A(Baza):
    def __init__(self):
        print("A.__init__")
        super().__init__()


class C(Baza):
    def __init__(self):
        print("C.__init__")
        super().__init__()


class D(A, C):
    def __init__(self):
        print("D.__init__")
        super().__init__()


print([k.__name__ for k in D.__mro__])
D()
print("---")
A()
```

```{ .text .no-copy }
['D', 'A', 'C', 'Baza', 'object']
D.__init__
A.__init__
C.__init__
Baza.__init__
---
A.__init__
Baza.__init__
```

Klasa `A` dziedziczy wyłącznie po `Baza`, a mimo to `super().__init__()` w `A.__init__` uruchomiło `C.__init__` — bo obiekt jest instancją `D`, a w `__mro__` klasy `D` po `A` stoi `C`. Ta sama metoda `A.__init__` wywołana dla obiektu klasy `A` przechodzi wprost do `Baza`. Zachowanie `super()` zależy więc od klasy obiektu, nie od klasy, w której metodę zapisano; dlatego w rozdziale 10 zalecaliśmy `super()` zamiast jawnego `Baza.__init__(self)` — tylko `super()` włącza klasę w ten łańcuch.

### Kooperatywne `__init__` z `**kwargs`

Łańcuch wywołań `super().__init__()` przez wszystkie klasy nazywamy **kooperatywnym dziedziczeniem** (ang. *cooperative inheritance*): każda klasa wykonuje swoją część pracy i przekazuje sterowanie dalej. Gdy klasy przyjmują różne argumenty, stosuje się konwencję: każda odbiera własne parametry jako nazwane, a pozostałe przekazuje dalej w `**kwargs`:

```python title="kaczka-kwargs.py"
class Zwierze:
    def __init__(self, imie, **kwargs):
        super().__init__(**kwargs)
        self.imie = imie


class Latajace:
    def __init__(self, zasieg, **kwargs):
        super().__init__(**kwargs)
        self.zasieg = zasieg


class Plywajace:
    def __init__(self, glebokosc, **kwargs):
        super().__init__(**kwargs)
        self.glebokosc = glebokosc


class Kaczka(Latajace, Plywajace, Zwierze):
    pass


kaczka = Kaczka(imie="Donald", zasieg=500, glebokosc=2)
print([k.__name__ for k in Kaczka.__mro__])
print(vars(kaczka))
```

```{ .text .no-copy }
['Kaczka', 'Latajace', 'Plywajace', 'Zwierze', 'object']
{'imie': 'Donald', 'glebokosc': 2, 'zasieg': 500}
```

`Latajace.__init__` odbiera `zasieg`, a `imie` i `glebokosc` przekazuje dalej; `Plywajace` odbiera `glebokosc`; `Zwierze` odbiera `imie` i wywołuje `object.__init__()` już bez argumentów — gdyby jakiś argument pozostał, `object.__init__()` zgłosiłby `TypeError`, co samo w sobie jest przydatną kontrolą literówek w nazwach parametrów. Klasy `Latajace` i `Plywajace` nie dziedziczą po `Zwierze`, a mimo to wywołują `super().__init__()`: kooperatywne klasy nie zakładają, które klasy stoją za nimi w MRO, i zawsze przekazują sterowanie dalej. Kolejność atrybutów w `vars()` odzwierciedla kolejność przypisań — najgłębsza klasa wykonuje swoje przypisanie pierwsza, bo każda klasa najpierw woła `super()`, a dopiero potem ustawia własny atrybut.

## Niespójne MRO

Algorytm C3 może nie znaleźć kolejności spełniającej wszystkie ograniczenia. Klasyczny przypadek to klasa pochodna, która wymienia klasę bazową przed klasą po niej dziedziczącą:

```python title="niespojne-mro.py"
class Baza:
    pass


class B(Baza):
    pass


class C(B):
    pass


try:
    class D(B, C):
        pass
except TypeError as e:
    print("TypeError:", e)


class D(C, B):
    pass


print([k.__name__ for k in D.__mro__])


class X:
    pass


class Y:
    pass


class A(X, Y):
    pass


class B2(Y, X):
    pass


try:
    class C2(A, B2):
        pass
except TypeError as e:
    print("TypeError:", e)
```

```{ .text .no-copy }
TypeError: Cannot create a consistent method resolution order (MRO) for bases B, C
['D', 'C', 'B', 'Baza', 'object']
TypeError: Cannot create a consistent method resolution order (MRO) for bases X, Y
```

Rozpiszmy pierwszy przypadek: `L[B] = B Baza`, `L[C] = C B Baza`, więc `L[D] = D + merge(B Baza, C B Baza, B C)`. Czoło `B` pierwszej listy występuje w ogonie listy `C B Baza`; czoło `C` drugiej listy występuje w ogonie listy baz `B C`. Żadne czoło nie jest dopuszczalne — algorytm zatrzymuje się, a Python zgłasza `TypeError` już przy definicji klasy. Wystarczy odwrócić kolejność w nawiasie: `D(C, B)` daje `D C B Baza`. Drugi przypadek jest mniej oczywisty: `A` wymaga, aby `X` stało przed `Y`, `B2` — aby `Y` stało przed `X`, i żadna kolejność baz w `C2` tego nie pogodzi. Zasada praktyczna: w nawiasie klasy bardziej szczegółowe wymieniamy przed ogólniejszymi, a niespójne MRO traktujemy jako sygnał, że hierarchia wymaga przeprojektowania, nie obejścia.

## Śledzenie `__new__` i `__init__` w hierarchii (dla dociekliwych)

Rozdział 10 pokazał, że wywołanie klasy to `__new__`, a potem `__init__`. W hierarchii z dziedziczeniem wielokrotnym obie metody przechodzą przez MRO — o ile każda klasa przekazuje sterowanie przez `super()`. Poniższe klasy wypisują każde wejście do metody i wyjście z niej; różnią się dwoma szczegółami: sposobem wywołania `__new__` (zaznaczonym w komentarzu) oraz tym, czy `__init__` przekazuje `x` dalej — `Baza` wywołuje `super().__init__()` bez argumentu, `A` przekazuje `x`:

```python title="sledzenie-new-init.py"
class Baza:
    def __new__(cls, *args):
        print("-> Baza __new__", *args)
        nowy = object.__new__(cls)  # wprost object, nie super()
        print("<- Baza __new__")
        return nowy

    def __init__(self, x):
        print("-> Baza __init__", x)
        super().__init__()
        print("-- Baza __init__")
        self.x = x
        print("<- Baza __init__")

    def id(self):
        print("-Baza-")


class A:
    def __new__(cls, *args):
        print("-> A __new__", *args)
        nowy = super().__new__(cls)
        print("<- A __new__")
        return nowy

    def __init__(self, x):
        print("-> A __init__", x)
        super().__init__(x)
        print("-- A __init__")
        self.x = x
        print("<- A __init__")

    def id(self):
        print("-A-")


class B(Baza):
    pass


class C(B):
    pass


class D(A, C, B, Baza):
    pass


print([k.__name__ for k in D.__mro__])
d = D(789)
d.id()
A.id(d)
Baza.id(d)
print(d.x)
```

```{ .text .no-copy }
['D', 'A', 'C', 'B', 'Baza', 'object']
-> A __new__ 789
-> Baza __new__
<- Baza __new__
<- A __new__
-> A __init__ 789
-> Baza __init__ 789
-- Baza __init__
<- Baza __init__
-- A __init__
<- A __init__
-A-
-A-
-Baza-
789
```

Klasa `D` nie definiuje ani `__new__`, ani `__init__`, więc wywołanie `D(789)` trafia do pierwszej klasy w MRO, która je ma — do `A`. Metoda `A.__new__` przekazuje sterowanie przez `super().__new__(cls)` do następnej klasy z własnym `__new__`; klasy `C` i `B` go nie definiują, więc jest nią `Baza`. Argument `789` nie dotarł do `Baza.__new__`, bo `A` przekazała samo `cls` — i słusznie — gdy klasa definiuje własne `__new__`, `object.__new__()` odrzuca dodatkowe argumenty (toleruje je jedynie wtedy, gdy klasa nadpisała wyłącznie `__init__`). `Baza.__new__` wywołuje `object.__new__(cls)` wprost; gdyby za nią stała jeszcze jakaś klasa z własnym `__new__`, ten zapis pominąłby ją — dlatego w rozdziale 10 pisaliśmy `super().__new__(cls)`. Obiekt powstaje jeden, w `object.__new__`, a wszystkie pozostałe wywołania `__new__` tylko przekazują sterowanie.

Łańcuch `__init__` przebiega tak samo: `A.__init__` przekazuje `x` do `super().__init__(x)`, a następną klasą z `__init__` jest `Baza`, która przyjmuje `x` — sygnatury są zgodne. Wywołanie `d.id()` zatrzymuje się na pierwszej definicji w MRO, czyli w `A`; metodę z dalszej klasy można wywołać jawnie, przez klasę, z obiektem jako pierwszym argumentem: `Baza.id(d)`. Ten sam obiekt ma jeden atrybut `x` — dwa przypisania `self.x = x` w `Baza` i w `A` dotyczą tej samej instancji.

Kolejność w MRO tłumaczy też, dlaczego klasa `A` nie działa samodzielnie:

```python title="a-samodzielnie.py"
class A:
    def __init__(self, x):
        print("-> A __init__", x)
        super().__init__(x)
        self.x = x


a = A(1)
```

```{ .text .no-copy }
-> A __init__ 1
Traceback (most recent call last):
  File "a-samodzielnie.py", line 8, in <module>
    a = A(1)
  File "a-samodzielnie.py", line 4, in __init__
    super().__init__(x)
    ~~~~~~~~~~~~~~~~^^^
TypeError: object.__init__() takes exactly one argument (the instance to initialize)
```

Dla obiektu klasy `A` następną klasą po `A` jest `object`, którego `__init__` nie przyjmuje argumentów — `super().__init__(x)` kończy się `TypeError`. W hierarchii `D` ta sama metoda działała, bo za `A` stała `Baza` z `__init__(self, x)`. Metoda `A.__init__` jest więc napisana z myślą o współpracy w hierarchii, a nie o samodzielnym użyciu; kooperatywne klasy z `**kwargs` z poprzedniej sekcji unikają tej pułapki, bo do `object.__init__()` docierają zawsze bez argumentów. Wywołanie `object.__init__(self, x)` wprost, zamiast przez `super()`, niczego nie zmienia — również zgłasza `TypeError`, gdy klasa definiuje własne `__init__`.

Zamiana kolejności baz na `class D(C, A)` przenosi problem w inne miejsce: MRO to `D C B Baza A object`, więc `Baza.__init__` wywołuje `super().__init__()` bez argumentów, a następną klasą jest teraz `A`, której `__init__` argumentu wymaga — `TypeError: A.__init__() missing 1 required positional argument: 'x'`. Każda klasa w hierarchii kooperatywnej musi zatem przekazywać dalej to, czego oczekują klasy stojące za nią — a ponieważ nie wiadomo, które to będą, najbezpieczniejszą konwencją pozostaje `**kwargs`.
