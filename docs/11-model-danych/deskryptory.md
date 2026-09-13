# Deskryptory

Ten podrozdział uzupełnia rozdział o mechanizm, który stoi za właściwościami, metodami klasy i wiązaniem zwykłych metod z instancją — w rozdziale 10 nazwaliśmy go deskryptorem, tu go definiujemy. Wiedza ta nie jest potrzebna do pisania zwykłych klas; przydaje się, gdy ten sam sposób dostępu do atrybutu — walidacja, obliczenie, blokada zapisu — ma wracać w wielu klasach, oraz do zrozumienia, jak Python wyszukuje atrybuty. Podrozdział można pominąć przy pierwszej lekturze.

## Protokół deskryptorów

**Deskryptor** (ang. *descriptor*) to obiekt umieszczony jako atrybut klasy, którego własny typ definiuje przynajmniej jedną z metod `__get__(self, obiekt, wlasciciel=None)`, `__set__(self, obiekt, wartosc)` i `__delete__(self, obiekt)`. Gdy program odczytuje, przypisuje lub usuwa taki atrybut przez instancję, Python zamiast sięgać do słownika instancji wywołuje odpowiednią metodę deskryptora, przekazując jej instancję (z zastrzeżeniem dla deskryptorów bez `__set__`, omówionym w sekcji o kolejności wyszukiwania). Czwarta metoda, `__set_name__(self, wlasciciel, nazwa)`, jest wywoływana raz, przy tworzeniu klasy, i informuje deskryptor, pod jaką nazwą został w niej umieszczony:

```python title="sledzacy.py"
class Sledzacy:
    """Deskryptor wypisujący każde wywołanie metod protokołu."""

    def __set_name__(self, wlasciciel, nazwa):
        print(f"__set_name__: klasa {wlasciciel.__name__}, nazwa {nazwa!r}")
        self.nazwa = nazwa

    def __get__(self, obiekt, wlasciciel=None):
        print(f"__get__: obiekt klasy {type(obiekt).__name__}")
        return obiekt.__dict__.get(self.nazwa)

    def __set__(self, obiekt, wartosc):
        print(f"__set__: wartość {wartosc!r}")
        obiekt.__dict__[self.nazwa] = wartosc

    def __delete__(self, obiekt):
        print("__delete__")
        del obiekt.__dict__[self.nazwa]


print("przed definicją klasy")


class Konto:
    saldo = Sledzacy()


print("po definicji klasy")
k = Konto()
k.saldo = 100
print("odczyt:", k.saldo)
del k.saldo
print("odczyt po usunięciu:", k.saldo)
```

```{ .text .no-copy }
przed definicją klasy
__set_name__: klasa Konto, nazwa 'saldo'
po definicji klasy
__set__: wartość 100
__get__: obiekt klasy Konto
odczyt: 100
__delete__
__get__: obiekt klasy Konto
odczyt po usunięciu: None
```

Deskryptor jest jeden — utworzony raz, w ciele klasy `Konto` — i obsługuje wszystkie instancje; dlatego wartości przechowuje nie w sobie, lecz w słowniku `__dict__` każdej instancji, pod nazwą poznaną z `__set_name__`. Zwykłe przypisanie `k.saldo = 100` nie tworzy wpisu `saldo` w słowniku instancji wprost, jak w rozdziale 10, lecz trafia do `__set__`; to deskryptor decyduje, co się stanie z wartością. Dostęp przez klasę, `Konto.saldo`, również trafia do `__get__`, z parametrem `obiekt` równym `None` — obsługujemy go w następnym przykładzie.

## Walidator wielokrotnego użytku — `Nieujemna`

Właściwość z rozdziału 10 sprawdzała, czy promień okręgu jest nieujemny. Gdyby klasa miała trzy takie atrybuty, trzeba by napisać trzy pary metod odczytu i zapisu o identycznej treści. Deskryptor zamyka tę logikę w jednej klasie, którą można umieścić w dowolnej liczbie klas i atrybutów:

```python title="nieujemna.py"
class Nieujemna:
    """Deskryptor atrybutu przyjmującego wyłącznie liczby nieujemne."""

    def __set_name__(self, wlasciciel, nazwa):
        self.nazwa_pola = "_" + nazwa

    def __get__(self, obiekt, wlasciciel=None):
        if obiekt is None:
            return self
        return getattr(obiekt, self.nazwa_pola)

    def __set__(self, obiekt, wartosc):
        if wartosc < 0:
            raise ValueError(f"{self.nazwa_pola[1:]} nie może być ujemna: {wartosc}")
        setattr(obiekt, self.nazwa_pola, wartosc)


class Produkt:
    """Produkt o nieujemnej cenie i ilości."""

    cena = Nieujemna()
    ilosc = Nieujemna()

    def __init__(self, nazwa, cena, ilosc):
        self.nazwa = nazwa
        self.cena = cena
        self.ilosc = ilosc

    def __repr__(self):
        return f"Produkt({self.nazwa!r}, {self.cena}, {self.ilosc})"

    def wartosc(self):
        """Zwraca łączną wartość produktu."""
        return self.cena * self.ilosc


p = Produkt("rower", 1200, 2)
print(p, p.wartosc(), vars(p))
p.ilosc = 3
print(p.wartosc())
for wyrazenie in ["p.cena = -5", "Produkt('kask', 80, -1)"]:
    try:
        exec(wyrazenie)
    except ValueError as e:
        print("ValueError:", e)
print(type(Produkt.cena).__name__)
```

```{ .text .no-copy }
Produkt('rower', 1200, 2) 2400 {'nazwa': 'rower', '_cena': 1200, '_ilosc': 2}
3600
ValueError: cena nie może być ujemna: -5
ValueError: ilosc nie może być ujemna: -1
Nieujemna
```

Walidacja działa w `__init__`, przy późniejszym przypisaniu i dla każdego atrybutu z osobna, a klasa `Produkt` nie zawiera ani jednego wiersza sprawdzającego. Metoda `__get__` obsługuje dwa przypadki: przez instancję (`p.cena`) zwraca wartość z pola zapasowego, a przez klasę (`Produkt.cena`) otrzymuje `obiekt` równy `None` i zwraca sam deskryptor — stąd `Nieujemna` w ostatnim wierszu; tak samo zachowuje się `property`, która przez klasę zwraca obiekt `property`. Pole zapasowe `_cena` w `__dict__` instancji jest widoczne, jak `_promien` przy właściwościach; deskryptor jest umową, nie blokadą.

## Deskryptor tylko do odczytu — `TylkoDoOdczytu`

Metoda `__set__`, która zawsze zgłasza `AttributeError`, zamienia atrybut w stałą ustalaną raz, przy definicji klasy. Zgłoszenie `AttributeError` jest tu konwencją — ten sam wyjątek daje właściwość bez metody zapisu:

```python title="tylko-do-odczytu.py"
class TylkoDoOdczytu:
    """Deskryptor stałej, której nie można nadpisać przez instancję."""

    def __init__(self, wartosc):
        self.wartosc = wartosc

    def __set_name__(self, wlasciciel, nazwa):
        self.nazwa = nazwa

    def __get__(self, obiekt, wlasciciel=None):
        return self.wartosc

    def __set__(self, obiekt, wartosc):
        raise AttributeError(f"atrybut {self.nazwa!r} jest tylko do odczytu")


class Konfiguracja:
    wersja = TylkoDoOdczytu("3.14")


konfiguracja = Konfiguracja()
print(konfiguracja.wersja, Konfiguracja.wersja)
try:
    konfiguracja.wersja = "3.15"
except AttributeError as e:
    print("AttributeError:", e)
print(konfiguracja.wersja, vars(konfiguracja))
```

```{ .text .no-copy }
3.14 3.14
AttributeError: atrybut 'wersja' jest tylko do odczytu
3.14 {}
```

## Deskryptory danych i niedanych — kolejność wyszukiwania atrybutu

W rozdziale 10 podaliśmy uproszczoną regułę: słownik instancji, potem słownik klasy. Pełna reguła uwzględnia deskryptory i dzieli je na dwa rodzaje. **Deskryptor danych** (ang. *data descriptor*) definiuje `__set__` lub `__delete__` (zwykle obok `__get__`); **deskryptor niedanych** (ang. *non-data descriptor*) ma tylko `__get__`. Odczyt `obiekt.atrybut` przebiega w kolejności:

1. deskryptor danych o tej nazwie w klasie obiektu lub jej klasach bazowych (według `__mro__`) — wywoływane jest jego `__get__`;
2. wpis w słowniku `__dict__` instancji;
3. deskryptor niedanych albo zwykły atrybut w klasie lub klasach bazowych;
4. metoda `__getattr__`, jeśli klasa ją definiuje;
5. wyjątek `AttributeError`.

Różnicę widać, gdy w słowniku instancji umieścimy wpis o tej samej nazwie co deskryptor:

```python title="kolejnosc-wyszukiwania.py"
class Danych:
    def __get__(self, obiekt, wlasciciel=None):
        return "z deskryptora danych"

    def __set__(self, obiekt, wartosc):
        obiekt.__dict__["a"] = wartosc


class Niedanych:
    def __get__(self, obiekt, wlasciciel=None):
        return "z deskryptora niedanych"


class Przyklad:
    a = Danych()
    b = Niedanych()


p = Przyklad()
print(p.a, "|", p.b)
p.a = "wartość"
p.__dict__["b"] = "z instancji"
print(vars(p))
print(p.a, "|", p.b)
```

```{ .text .no-copy }
z deskryptora danych | z deskryptora niedanych
{'a': 'wartość', 'b': 'z instancji'}
z deskryptora danych | z instancji
```

Wpis `a` w słowniku instancji istnieje, ale odczyt `p.a` nadal trafia do deskryptora danych — ma on pierwszeństwo przed słownikiem. Wpis `b` przesłonił deskryptor niedanych, bo ten stoi w kolejności dopiero za słownikiem instancji. Krok czwarty, metoda `__getattr__`, jest ostatnim etapem wyszukiwania: Python wywołuje ją tylko wtedy, gdy zwykłe wyszukiwanie zawiodło, co pozwala obsłużyć atrybuty nieistniejące:

```python title="getattr-demo.py"
class Ustawienia:
    """Ustawienia ze słownika, dostępne jako atrybuty."""

    def __init__(self, **wartosci):
        self._wartosci = dict(wartosci)

    def __getattr__(self, nazwa):
        try:
            return self._wartosci[nazwa]
        except KeyError:
            raise AttributeError(f"brak ustawienia {nazwa!r}") from None


u = Ustawienia(motyw="ciemny", rozmiar=12)
print(u.motyw, u.rozmiar, u._wartosci)
try:
    print(u.jezyk)
except AttributeError as e:
    print("AttributeError:", e)
```

```{ .text .no-copy }
ciemny 12 {'motyw': 'ciemny', 'rozmiar': 12}
AttributeError: brak ustawienia 'jezyk'
```

Odczyt `u._wartosci` nie wywołuje `__getattr__`, bo atrybut istnieje w słowniku instancji; `u.motyw` — tak, bo zwykłe wyszukiwanie go nie znajduje. Metoda `__getattr__` powinna zgłaszać `AttributeError` dla nazw, których nie zna, aby `hasattr()` i `getattr()` z wartością domyślną działały poprawnie. Istnieje też metoda `__getattribute__`, wywoływana przy każdym jawnym odczycie atrybutu (`obiekt.nazwa`, `getattr()`), choć nie przy niejawnym wyszukiwaniu metod specjalnych przez operatory i funkcje wbudowane — to ona wykonuje kroki od pierwszego do trzeciego, a `__getattr__` otrzymuje sterowanie dopiero wtedy, gdy `__getattribute__` zgłosi `AttributeError`; nadpisuje się ją bardzo rzadko i ostrożnie, bo błąd w niej uniemożliwia dostęp do wszystkich atrybutów. Wracamy do niej w podrozdziale [Metaprogramowanie](../12-oop-zaawansowane/metaprogramowanie.md#wasna-metaklasa) rozdziału 12.

## Klasa `property` jako deskryptor

Właściwość z rozdziału 10 jest deskryptorem danych: obiekt `property` ma `__get__` wywołujące metodę odczytu i `__set__` wywołujące metodę zapisu. Uproszczona własna wersja pokazuje cały mechanizm, łącznie ze składnią dekoratora:

```python title="wlasciwosc.py"
class Wlasciwosc:
    """Uproszczony odpowiednik klasy property."""

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __set_name__(self, wlasciciel, nazwa):
        self.nazwa = nazwa

    def __get__(self, obiekt, wlasciciel=None):
        if obiekt is None:
            return self
        return self.fget(obiekt)

    def __set__(self, obiekt, wartosc):
        if self.fset is None:
            raise AttributeError(f"właściwość {self.nazwa!r} nie ma metody zapisu")
        self.fset(obiekt, wartosc)

    def setter(self, fset):
        """Zwraca nową właściwość z dodaną metodą zapisu."""
        return Wlasciwosc(self.fget, fset)


class Okrag:
    def __init__(self, promien):
        self.promien = promien

    @Wlasciwosc
    def promien(self):
        return self._promien

    @promien.setter
    def promien(self, wartosc):
        if wartosc < 0:
            raise ValueError(f"promień nie może być ujemny: {wartosc}")
        self._promien = wartosc

    @Wlasciwosc
    def pole(self):
        return 3.14159 * self._promien**2


o = Okrag(2)
print(o.promien, round(o.pole, 2), vars(o))
o.promien = 3
print(o.promien, type(Okrag.promien).__name__)
try:
    o.pole = 1
except AttributeError as e:
    print("AttributeError:", e)
```

```{ .text .no-copy }
2 12.57 {'_promien': 2}
3 Wlasciwosc
AttributeError: właściwość 'pole' nie ma metody zapisu
```

Zapis `@Wlasciwosc` nad metodą `promien` oznacza `promien = Wlasciwosc(promien)` — funkcja odczytu trafia do `fget`, a atrybut klasy `promien` staje się deskryptorem. Dekorator `@promien.setter` wywołuje metodę `setter()` istniejącego deskryptora, która zwraca nowy deskryptor z obiema funkcjami; składnia dekoratora przypisuje go ponownie pod nazwą `promien`. Wbudowana klasa `property` robi dokładnie to, dodając `deleter()`, docstring i kilka zabezpieczeń.

## Funkcje jako deskryptory — metody związane

Ostatnie zagadnienie podrozdziału wyjaśnia, dlaczego `obiekt.metoda()` przekazuje `self`. Funkcja zdefiniowana instrukcją `def` ma metodę `__get__`, jest więc deskryptorem niedanych. Odczyt `obiekt.metoda` przechodzi przez krok trzeci kolejności wyszukiwania: Python znajduje funkcję w słowniku klasy i wywołuje jej `__get__(obiekt, klasa)`, a ta zwraca **metodę związaną** (ang. *bound method*) — obiekt pamiętający funkcję i instancję, który przy wywołaniu wstawia instancję jako pierwszy argument:

```python title="metody-zwiazane.py"
class Czlowiek:
    def __init__(self, imie):
        self.imie = imie

    def przedstaw(self):
        return f"Jestem {self.imie}."

    @classmethod
    def anonim(cls):
        return cls("Anonim")

    @staticmethod
    def powitanie():
        return "Dzień dobry"


c = Czlowiek("Jan")
funkcja = Czlowiek.__dict__["przedstaw"]
print(type(funkcja).__name__, hasattr(funkcja, "__get__"), hasattr(funkcja, "__set__"))
metoda = c.przedstaw
print(type(metoda).__name__, metoda(), metoda.__self__ is c, metoda.__func__ is funkcja)
print(funkcja.__get__(c, Czlowiek)())
print(type(Czlowiek.__dict__["anonim"]).__name__, type(Czlowiek.__dict__["powitanie"]).__name__)
print(hasattr(property, "__set__"), hasattr(classmethod, "__set__"), hasattr(staticmethod, "__set__"))
```

```{ .text .no-copy }
function True False
method Jestem Jan. True True
Jestem Jan.
classmethod staticmethod
True False False
```

W słowniku klasy `przedstaw` jest zwykłą funkcją; dopiero dostęp przez instancję tworzy metodę związaną z atrybutami `__self__` (instancja) i `__func__` (funkcja). Ręczne wywołanie `funkcja.__get__(c, Czlowiek)()` daje ten sam wynik, co pokazuje, że `types.MethodType` z rozdziału 10 wykonywał tę samą pracę. Dekoratory `@classmethod` i `@staticmethod` opakowują funkcję w obiekty, których `__get__` zwraca odpowiednio metodę związaną z klasą i gołą funkcję — to dlatego metoda klasy dostaje `cls`, a statyczna nic. Wszystkie trzy są deskryptorami niedanych, więc wpis w słowniku instancji może je przesłonić; `property` jest deskryptorem danych i ma pierwszeństwo — dokładnie tak, jak zapowiedzieliśmy w rozdziale 10 przy kolejności wyszukiwania atrybutów.
