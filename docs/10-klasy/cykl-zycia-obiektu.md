# Cykl życia obiektu

Ten podrozdział uzupełnia rozdział o mechanizmy, których w codziennym kodzie nie używa się wprost, ale które tłumaczą, co dzieje się z obiektem od wywołania klasy do zwolnienia pamięci: metodę `__new__` tworzącą obiekt przed `__init__`, wzorzec Singleton, licznik referencji znany z rozdziału 3, metodę `__del__`, słabe referencje, cykle referencji z modułem `gc` oraz współdziałanie `__slots__` z dziedziczeniem. Dalsze rozdziały odwołują się do niego tylko przy `__new__` i Singletonie; pozostałe sekcje można pominąć przy pierwszej lekturze.

## Metody `__new__` i `__init__`

W podrozdziale o definicji klasy wywołanie klasy opisaliśmy jako dwa kroki: utworzenie obiektu i jego inicjalizację. Za pierwszy krok odpowiada metoda specjalna `__new__`, którą każda klasa dziedziczy po `object`. Otrzymuje ona klasę jako pierwszy argument (nazywany `cls`, bo obiektu jeszcze nie ma) oraz argumenty wywołania, a zwraca nowy obiekt; dopiero na tym obiekcie Python wywołuje `__init__` z tymi samymi argumentami:

```python title="new-init.py"
class Foo:
    def __new__(cls, *args, **kwargs):
        print("__new__:", cls.__name__, args, kwargs)
        obiekt = super().__new__(cls)
        return obiekt

    def __init__(self, a, b):
        print("__init__:", a, b)
        self.a = a
        self.b = b


f = Foo(1, b=2)
print(vars(f))
```

```{ .text .no-copy }
__new__: Foo (1,) {'b': 2}
__init__: 1 2
{'a': 1, 'b': 2}
```

Metoda `__new__` jest metodą statyczną (Python opakowuje ją w `staticmethod` bez dekoratora), więc nic nie jest do niej wiązane automatycznie: przy wywołaniu klasy interpreter przekazuje jej klasę jako pierwszy argument, a w `super().__new__(cls)` musimy zrobić to sami — inaczej niż w `super().__init__()`, gdzie `self` jest wiązany jak w każdej metodzie instancji. Nowy obiekt tworzy ostatecznie `__new__` klasy `object` — w klasach dziedziczących wprost po `object` jedyne miejsce, w którym naprawdę powstaje obiekt w pamięci; klasy pochodne od typów wbudowanych, jak `int` czy `tuple`, korzystają z `__new__` tych typów. Własne `__new__` definiujemy rzadko: gdy trzeba wpłynąć na samo tworzenie obiektu, na przykład zwrócić obiekt istniejący zamiast nowego (Singleton poniżej) albo w klasach pochodnych od typów niemodyfikowalnych, których wartości nie da się już zmienić w `__init__`. Wszystko inne należy do `__init__`.

### Pułapka: `__new__` bez `return`

Wynikiem wywołania klasy jest to, co zwróci `__new__`. Jeśli `__new__` nie zwróci obiektu klasy — na przykład dlatego, że zapomnieliśmy o `return` — Python pomija `__init__`, a wywołanie klasy zwraca `None`:

```python title="new-bez-return.py"
class Bez:
    def __new__(cls):
        print("__new__ bez return")
        super().__new__(cls)

    def __init__(self):
        print("__init__")


wynik = Bez()
print("wynik:", wynik)
```

```{ .text .no-copy }
__new__ bez return
wynik: None
```

## Wzorzec Singleton

**Singleton** to wzorzec projektowy (ang. *design pattern*), w którym klasa ma tylko jedną instancję, wspólną dla całego programu — na przykład obiekt konfiguracji albo połączenie z bazą danych. W Pythonie realizuje go `__new__`, które przy pierwszym wywołaniu tworzy obiekt i zapamiętuje go w atrybucie klasy, a przy kolejnych zwraca ten sam obiekt:

```python title="singleton.py"
class Konfiguracja:
    _instancja = None

    def __new__(cls, *args, **kwargs):
        if cls._instancja is None:
            cls._instancja = super().__new__(cls)
        return cls._instancja

    def __init__(self, tryb):
        self.tryb = tryb


k1 = Konfiguracja("testowy")
k2 = Konfiguracja("produkcyjny")
print(k1 is k2, k1.tryb)
```

```{ .text .no-copy }
True produkcyjny
```

Oba wywołania zwróciły ten sam obiekt, co potwierdza `is`. Wydruk `k1.tryb` ujawnia jednak pułapkę: `__init__` wykonuje się przy **każdym** wywołaniu klasy, także gdy `__new__` zwróciło obiekt istniejący, więc drugie wywołanie nadpisało atrybut ustawiony przez pierwsze. Singleton z `__init__` musi to uwzględnić — na przykład inicjalizować atrybuty tylko raz, sprawdzając, czy już istnieją, albo nie przyjmować argumentów. Prostszą realizację wzorca, przez dekorator klasy, oraz inne wzorce omawiamy w rozdziale o zaawansowanych mechanizmach obiektowych. <!-- TODO: link po powstaniu rozdziału o zaawansowanych mechanizmach obiektowych --> W praktyce Singleton stosujemy rzadko: moduł, który jest importowany raz i przechowuje stan w swoich zmiennych, daje ten sam efekt bez klasy.

## Licznik referencji i `sys.getrefcount()`

W rozdziale [3. Nazwy i typy](../03-nazwy-typy/obiekty-i-pamiec.md#usuwanie-obiektow-del) ustaliliśmy, że obiekt znika z pamięci, gdy jego **licznik referencji** (ang. *reference count*) spadnie do zera, a `del` usuwa nazwę, nie obiekt. Funkcja `sys.getrefcount()` pokazuje wartość licznika:

```python title="refcount.py"
import sys

lista = [1, 2, 3]
print(sys.getrefcount(lista))
inna = lista
print(sys.getrefcount(lista))
del inna
print(sys.getrefcount(lista))
print(sys.getrefcount(1), sys.getrefcount(None))
```

```{ .text .no-copy }
2
3
2
3221225472 3221225472
```

Świeżo utworzona lista z jedną nazwą ma licznik równy 2, nie 1: na czas wywołania `getrefcount()` jej argument jest dodatkową referencją. Druga nazwa `inna` zwiększa licznik, `del inna` go zmniejsza. Ostatni wiersz ilustruje inne zjawisko: małe liczby całkowite, `None`, `True` i `False` oraz kilka innych często używanych obiektów są od Pythona 3.12 **obiektami nieśmiertelnymi** (ang. *immortal objects*, PEP 683) — ich licznik ma stałą, bardzo dużą wartość, nie jest aktualizowany i nigdy nie spada do zera. Dokładna wartość zależy od wersji interpretera; powyższa pochodzi z Pythona 3.14. Kompilacja free-threaded interpretera (wariant `3.14t` z rozdziału [1. Instalacja i środowisko pracy](../01-instalacja/instalacja.md#instalacja-interpreterow)) realizuje licznik referencji jeszcze inaczej — wracamy do niej w rozdziale o współbieżności. <!-- TODO: link po powstaniu rozdziału o współbieżności -->

## Metoda `__del__`

Metoda specjalna `__del__`, nazywana **finalizatorem** (ang. *finalizer*), jest wywoływana tuż przed zwolnieniem obiektu — gdy jego licznik referencji spadnie do zera. Klasa `Bug` z podrozdziału o atrybutach zyskuje licznik malejący:

```python title="bug.py"
class Bug:
    licznik = 0

    def __init__(self):
        Bug.licznik += 1
        self.id = Bug.licznik

    def __repr__(self):
        return f"Bug({self.id})"

    def __del__(self):
        Bug.licznik -= 1
        print(f"koniec {self!r}, pozostało: {Bug.licznik}")


bugs = [Bug(), Bug(), Bug()]
print(bugs, Bug.licznik)
del bugs[0]
print(bugs, Bug.licznik)
b = bugs[0]
del bugs[0]
print("obiekt 2 ma jeszcze nazwę b, licznik:", Bug.licznik)
del b
bugs.clear()
print("koniec programu, licznik:", Bug.licznik)
```

```{ .text .no-copy }
[Bug(1), Bug(2), Bug(3)] 3
koniec Bug(1), pozostało: 2
[Bug(2), Bug(3)] 2
obiekt 2 ma jeszcze nazwę b, licznik: 2
koniec Bug(2), pozostało: 1
koniec Bug(3), pozostało: 0
koniec programu, licznik: 0
```

Usunięcie elementu z listy zwolniło pierwszy obiekt natychmiast — nikt inny go nie wskazywał. Drugi obiekt przetrwał usunięcie z listy, bo wciąż wskazywała go nazwa `b`, i został zwolniony dopiero po `del b`. W CPythonie zwolnienie następuje dokładnie w chwili, gdy znika ostatnia referencja, dlatego kolejność komunikatów jest przewidywalna. Nie jest to jednak gwarancja języka: dokumentacja zastrzega, że `__del__` może nie zostać wywołane dla obiektów istniejących jeszcze przy zamykaniu interpretera, a przy cyklach referencji (sekcja poniżej) wywołanie jest odroczone. Dlatego `__del__` nie nadaje się do zwalniania zasobów — plików, połączeń, blokad — do tego służy instrukcja `with` z rozdziału [8. Wyjątki i zarządzanie zasobami](../08-wyjatki/with-i-contextlib.md), która zwalnia zasób w określonym miejscu programu. W przykładzie ostatnie obiekty usuwamy jawnie przed końcem programu, aby komunikaty pojawiły się w przewidywalnej kolejności.

## Słabe referencje — `weakref.ref()`

Każda zwykła referencja — nazwa, element listy, atrybut — utrzymuje obiekt w pamięci. Czasem chcemy obserwować obiekt, nie utrzymując go w pamięci: pamięć podręczna nie powinna blokować zwolnienia obiektów, których nikt już nie używa. Służy do tego **słaba referencja** (ang. *weak reference*) z modułu `weakref`:

```python title="slaba-referencja.py"
import weakref


class Czlowiek:
    def __init__(self, imie):
        self.imie = imie


c = Czlowiek("Jan")
w = weakref.ref(c)
print(w() is c, w().imie)
print(w)
del c
print(w())
print(w)
```

```{ .text .no-copy }
True Jan
<weakref at 0x0000021F4A0F76A0; to 'Czlowiek' at 0x0000021F4A0A5160>
None
<weakref at 0x0000021F4A0F76A0; dead>
```

Obiekt `w` nie jest obiektem `c`, lecz uchwytem: wywołanie `w()` zwraca obserwowany obiekt, dopóki ten istnieje, a potem `None`. Słaba referencja nie zwiększa licznika referencji, więc `del c` zwalnia obiekt mimo istnienia `w`. Nie każdy obiekt obsługuje słabe referencje: instancje własnych klas, funkcje i zbiory — tak, ale `list`, `dict`, `int`, `str` i `tuple` — nie (`weakref.ref([])` zgłasza `TypeError`); klasy z `__slots__` również nie, chyba że dodadzą do krotki nazwę `"__weakref__"`. Moduł oferuje ponadto słowniki ze słabymi wartościami lub kluczami (`WeakValueDictionary`, `WeakKeyDictionary`), z których wpisy znikają wraz ze zwolnieniem obiektów — typowa podstawa pamięci podręcznej.

## Cykle referencji i moduł `gc`

Licznik referencji zawodzi, gdy obiekty wskazują na siebie nawzajem: każdy z nich ma licznik co najmniej 1, choć z zewnątrz nie wskazuje ich już nic. Takimi **cyklami referencji** (ang. *reference cycles*) zajmuje się drugi mechanizm CPythona — **odśmiecacz** (ang. *garbage collector*) z modułu `gc`, uruchamiany automatycznie, gdy przybywa nowych obiektów, a na żądanie funkcją `gc.collect()`:

```python title="cykl.py"
import gc


class Wezel:
    def __init__(self, nazwa):
        self.nazwa = nazwa
        self.sasiad = None

    def __del__(self):
        print("zwalniam", self.nazwa)


a = Wezel("a")
b = Wezel("b")
a.sasiad = b
b.sasiad = a
del a, b
print("po del a, b")
zebrane = gc.collect()
print("gc.collect() zwróciło:", zebrane)
```

```{ .text .no-copy }
po del a, b
zwalniam a
zwalniam b
gc.collect() zwróciło: 2
```

Po `del a, b` żaden komunikat się nie pojawił — oba obiekty wciąż wskazują na siebie przez atrybut `sasiad`, więc ich liczniki nie spadły do zera. Dopiero `gc.collect()` odnalazł cykl nieosiągalny z programu, wywołał oba finalizatory i zwrócił liczbę znalezionych obiektów nieosiągalnych (wartość zależy od wersji interpretera; powyższa pochodzi z Pythona 3.14). W zwykłym programie nie wywołujemy `gc.collect()` — odśmiecacz działa sam — ale warto wiedzieć, że obiekt w cyklu nie jest zwalniany natychmiast po `del`, a jego `__del__` uruchomi się w nieokreślonym momencie. To druga przyczyna, dla której zasoby zwalniamy instrukcją `with`, a nie w finalizatorze.

## Atrybut `__slots__` a dziedziczenie

Atrybut `__slots__` z podrozdziału o atrybutach działa na poziomie klasy, w której go zdefiniowano, a dziedziczenie wprowadza dwie reguły. Klasa pochodna, która nie definiuje własnego `__slots__`, odzyskuje słownik `__dict__` — jej instancje znów przyjmują dowolne atrybuty. Klasa pochodna, która chce zachować ograniczenie, definiuje `__slots__` wyłącznie z **nowymi** nazwami; nazwy z klasy bazowej są dziedziczone:

```python title="slots-dziedziczenie.py"
class Baza:
    __slots__ = ("x", "y")


class Potomna(Baza):
    pass


class PotomnaZeSlotami(Baza):
    __slots__ = ("z",)


p = Potomna()
p.x = 1
p.w = 2
print(vars(p), hasattr(p, "__dict__"))

q = PotomnaZeSlotami()
q.x = 1
q.z = 3
print(hasattr(q, "__dict__"), Baza.__slots__, PotomnaZeSlotami.__slots__)
try:
    q.w = 4
except AttributeError as e:
    print("AttributeError:", e)
```

```{ .text .no-copy }
{'w': 2} True
False ('x', 'y') ('z',)
AttributeError: 'PotomnaZeSlotami' object has no attribute 'w' and no __dict__ for setting new attributes
```

Słownik `vars(p)` zawiera tylko `w` — atrybut `x` jest przechowywany w miejscu zarezerwowanym przez `__slots__` klasy bazowej, a `w` trafił do odzyskanego `__dict__`. Instancja `q` przyjmuje `x`, `y` i `z`, a każdą inną nazwę odrzuca. Wynika z tego praktyczna zasada: `__slots__` ma sens tylko wtedy, gdy definiuje go każda klasa w hierarchii; wystarczy jedna klasa bez niego, aby ograniczenie i oszczędność pamięci zniknęły dla jej instancji.
