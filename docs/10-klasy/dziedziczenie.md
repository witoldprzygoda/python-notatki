# Dziedziczenie

Hierarchię wyjątków z rozdziału 8 czytaliśmy od góry: `KeyError` jest odmianą `LookupError`, a ta — odmianą `Exception`. Mechanizm, który buduje takie drzewa, to **dziedziczenie** (ang. *inheritance*): nowa klasa przejmuje atrybuty i metody klasy istniejącej, a następnie je uzupełnia lub zmienia. W tym podrozdziale definiujemy klasy pochodne, nadpisujemy metody i rozszerzamy je funkcją `super()`, sprawdzamy typy funkcjami `isinstance()` i `issubclass()`, tworzymy własne klasy wyjątków — pierwsze praktyczne zastosowanie dziedziczenia, zapowiedziane w rozdziale 8 — a na koniec zestawiamy dziedziczenie z kompozycją i zbieramy zasady projektowania klas.

## Klasa bazowa i klasa pochodna

Klasę, po której dziedziczymy, nazywamy **klasą bazową** (ang. *base class*; także nadklasą, ang. *superclass*), a klasę dziedziczącą — **klasą pochodną** (ang. *derived class*; także podklasą, ang. *subclass*). Klasę bazową podajemy w nawiasach po nazwie klasy pochodnej:

```python title="zwierzeta.py"
class Zwierze:
    def __init__(self, imie, gatunek):
        self.imie = imie
        self.gatunek = gatunek

    def przedstaw(self):
        return f"{self.imie} ({self.gatunek})"

    def odglos(self):
        return "..."


class Pies(Zwierze):
    def odglos(self):
        return "Hau!"


class Kot(Zwierze):
    def odglos(self):
        return "Miau!"


p = Pies("Burek", "pies")
k = Kot("Filemon", "kot")
z = Zwierze("Nemo", "ryba")
print(p.przedstaw(), "|", k.przedstaw())
print(p.odglos(), k.odglos(), z.odglos())
print(Pies.__bases__)
print(Pies.__mro__)
```

```{ .text .no-copy }
Burek (pies) | Filemon (kot)
Hau! Miau! ...
(<class '__main__.Zwierze'>,)
(<class '__main__.Pies'>, <class '__main__.Zwierze'>, <class 'object'>)
```

Klasy `Pies` i `Kot` nie definiują `__init__` ani `przedstaw()`, a mimo to `Pies("Burek", "pies")` przyjmuje dwa argumenty, a `p.przedstaw()` działa — obie metody zostały odziedziczone po `Zwierze`. Wyszukiwanie atrybutów z sekcji [Atrybut klasy a atrybut instancji](atrybuty-i-metody.md#atrybut-klasy-a-atrybut-instancji) zyskuje kolejny krok: Python sprawdza słownik instancji, potem słownik jej klasy, a gdy nazwy tam nie ma — słownik klasy bazowej, i tak dalej aż do `object`. Kolejność tego przeszukiwania jest zapisana w atrybucie `__mro__` (od ang. *method resolution order*, kolejność rozstrzygania metod), a bezpośrednie klasy bazowe w krotce `__bases__`. Każda klasa, także zdefiniowana bez nawiasów, dziedziczy po `object` — dlatego `help()` w poprzednich podrozdziałach pokazywało `builtins.object`, a domyślna reprezentacja obiektu pochodzi właśnie stamtąd. Przy dziedziczeniu pojedynczym, jedynym w tym rozdziale, `__mro__` sprowadza się do łańcucha od klasy do `object`; dziedziczenie po kilku klasach naraz i algorytm ustalający wtedy kolejność omawiamy w rozdziale o zaawansowanych mechanizmach obiektowych. <!-- TODO: link po powstaniu rozdziału o zaawansowanych mechanizmach obiektowych -->

## Nadpisywanie metod i polimorfizm

Metoda `odglos()` jest zdefiniowana trzykrotnie. Definicja w klasie pochodnej **nadpisuje** (ang. *override*) definicję odziedziczoną: dla psa wyszukiwanie zatrzymuje się w `Pies`, dla ryby dociera do `Zwierze`. Kod, który wywołuje `odglos()`, nie musi wiedzieć, z jaką klasą ma do czynienia — każdy obiekt odpowiada po swojemu:

```python title="polimorfizm.py"
class Zwierze:
    def __init__(self, imie, gatunek):
        self.imie = imie
        self.gatunek = gatunek

    def odglos(self):
        return "..."


class Pies(Zwierze):
    def odglos(self):
        return "Hau!"


class Kot(Zwierze):
    def odglos(self):
        return "Miau!"


for zwierze in [Pies("Burek", "pies"), Kot("Filemon", "kot"), Zwierze("Nemo", "ryba")]:
    print(f"{zwierze.imie}: {zwierze.odglos()}")
```

```{ .text .no-copy }
Burek: Hau!
Filemon: Miau!
Nemo: ...
```

Tę własność — jedno wywołanie, różne zachowania zależne od klasy obiektu — nazywamy **polimorfizmem** (ang. *polymorphism*). Pętla korzysta ze wspólnego interfejsu: każda klasa w hierarchii ma metodę `odglos()`, więc lista może zawierać obiekty różnych klas, a kod pętli pozostaje jeden. Z polimorfizmem spotkaliśmy się już bez tej nazwy — `len()` działa na łańcuchach, listach i słownikach, a `print()` wypisuje każdy obiekt za pomocą jego `__str__`.

## Funkcja `super()`

Nadpisana metoda często ma nie zastąpić metody bazowej, lecz ją **rozszerzyć**: zrobić to, co klasa bazowa, i coś więcej. Najczęstszym przypadkiem jest `__init__` klasy pochodnej, która musi zainicjalizować atrybuty klasy bazowej, a potem własne. Funkcja `super()` zwraca obiekt pośredniczący, przez który wywołujemy metody następnej klasy w kolejności `__mro__` — przy dziedziczeniu pojedynczym jest to klasa bazowa — na rzecz bieżącego obiektu:

```python title="pracownik.py"
class Czlowiek:
    """Osoba o imieniu, nazwisku i wieku."""

    def __init__(self, imie, nazwisko, wiek=20):
        self.imie = imie
        self.nazwisko = nazwisko
        self.wiek = wiek

    def __repr__(self):
        return f"Czlowiek({self.imie!r}, {self.nazwisko!r}, {self.wiek})"

    def __str__(self):
        return f"{self.imie} {self.nazwisko} (lat {self.wiek})"


class Pracownik(Czlowiek):
    """Osoba zatrudniona w firmie."""

    def __init__(self, imie, nazwisko, firma, wiek=20):
        super().__init__(imie, nazwisko, wiek)
        self.firma = firma

    def __repr__(self):
        return f"Pracownik({self.imie!r}, {self.nazwisko!r}, {self.firma!r}, {self.wiek})"

    def __str__(self):
        return f"{super().__str__()}, {self.firma}"


p = Pracownik("Jan", "Kowalski", "ACME", 34)
print(p)
print(repr(p))
print(vars(p))
print(super(Pracownik, p).__str__())
```

```{ .text .no-copy }
Jan Kowalski (lat 34), ACME
Pracownik('Jan', 'Kowalski', 'ACME', 34)
{'imie': 'Jan', 'nazwisko': 'Kowalski', 'wiek': 34, 'firma': 'ACME'}
Jan Kowalski (lat 34)
```

W `Pracownik.__init__` wywołanie `super().__init__(imie, nazwisko, wiek)` uruchamia `Czlowiek.__init__` na tworzonym obiekcie — stąd w `vars(p)` komplet atrybutów — a dopiero potem klasa pochodna dodaje `firma`. Metoda `__str__` rozszerza wynik bazowy o nazwę firmy, a `__repr__` klasy pochodnej jest zapisany od nowa, bo wyrażenie tworzące pracownika ma inne argumenty niż wyrażenie tworzące człowieka. Zapis `super()` bez argumentów jest skrótem pełnej postaci `super(Pracownik, p)`, którą pokazuje ostatni wiersz: pierwszy argument wskazuje, od której klasy w `__mro__` zacząć szukanie dalej, a drugi — obiekt. Pełna postać jest nadal poprawna i bywa potrzebna poza metodami; w metodach piszemy `super()`. Wywołanie metody bazowej wprost, `Czlowiek.__init__(self, ...)`, również działa, ale wiąże kod z konkretną nazwą klasy — `super()` pozostaje poprawne po zmianie klasy bazowej i przy dziedziczeniu wielokrotnym.

Metody klasy z sekcji [Metody klasy — `@classmethod`](atrybuty-i-metody.md#metody-klasy-classmethod) również są dziedziczone i właśnie dla nich `cls` ma znaczenie: konstruktor alternatywny wywołany przez klasę pochodną tworzy obiekt klasy pochodnej, bo `cls` jest wtedy klasą pochodną:

```python title="dziedziczony-konstruktor.py"
class Student:
    def __init__(self, imie, nazwisko):
        self.imie = imie
        self.nazwisko = nazwisko

    @classmethod
    def z_napisu(cls, napis):
        imie, nazwisko = napis.split()
        return cls(imie, nazwisko)


class StudentZaoczny(Student):
    tryb = "zaoczny"


s = StudentZaoczny.z_napisu("Anna Nowak")
print(type(s).__name__, s.nazwisko, s.tryb)
```

```{ .text .no-copy }
StudentZaoczny Nowak zaoczny
```

### Pułapka: pominięte `super().__init__()`

Jeśli klasa pochodna definiuje własne `__init__`, Python nie wywoła `__init__` klasy bazowej automatycznie — nadpisanie działa dla `__init__` tak samo jak dla każdej innej metody. Bez wywołania `super().__init__()` atrybuty klasy bazowej nie powstają:

```python title="bez-super.py"
class Czlowiek:
    def __init__(self, imie, nazwisko):
        self.imie = imie
        self.nazwisko = nazwisko

    def __str__(self):
        return f"{self.imie} {self.nazwisko}"


class Pracownik(Czlowiek):
    def __init__(self, imie, nazwisko, firma):
        self.firma = firma


p = Pracownik("Jan", "Kowalski", "ACME")
print(p.firma)
print(p)
```

```{ .text .no-copy }
ACME
Traceback (most recent call last):
  File "bez-super.py", line 17, in <module>
    print(p)
    ~~~~~^^^
  File "bez-super.py", line 7, in __str__
    return f"{self.imie} {self.nazwisko}"
              ^^^^^^^^^
AttributeError: 'Pracownik' object has no attribute 'imie'
```

Obiekt powstał, ma atrybut `firma`, ale odziedziczona metoda `__str__` sięga po `imie`, którego nikt nie ustawił. Błąd ujawnia się dopiero przy użyciu, często daleko od miejsca definicji — dlatego regułą jest: `__init__` klasy pochodnej wywołuje `super().__init__()` z argumentami, których oczekuje klasa bazowa, zwykle w pierwszym wierszu.

### Pułapka: atrybut klasy wspólny z klasą pochodną

[Pułapka modyfikowalnego atrybutu klasy](atrybuty-i-metody.md#puapka-modyfikowalny-atrybut-klasy) obejmuje także klasy pochodne — dziedziczą one atrybut klasy, a nie jego kopię:

```python title="wspolna-lista.py"
class A:
    elementy = []

    def dodaj(self, wartosc):
        self.elementy.append(wartosc)


class B(A):
    pass


a = A()
b = B()
a.dodaj(1)
b.dodaj(2)
print(a.elementy, b.elementy, A.elementy, B.elementy)
print(a.elementy is b.elementy)
```

```{ .text .no-copy }
[1, 2] [1, 2] [1, 2] [1, 2]
True
```

Cztery nazwy, jedna lista: `B.elementy` to ten sam obiekt co `A.elementy`, a obie instancje modyfikują go przez `self.elementy`. Rozwiązanie jest to samo co poprzednio — lista tworzona w `__init__`, wtedy każdy obiekt, niezależnie od klasy, ma własną.

## Funkcje `isinstance()` i `issubclass()`

Funkcja `type()` zwraca dokładną klasę obiektu, więc porównanie `type(p) == Zwierze` dla psa daje `False`, choć pies jest zwierzęciem. Sprawdzanie typu z uwzględnieniem dziedziczenia zapewniają dwie funkcje wbudowane. Funkcja `isinstance(obiekt, klasa)`, znana z rozdziału [3. Nazwy i typy](../03-nazwy-typy/konwersje-i-adnotacje.md#sprawdzanie-typu), odpowiada, czy obiekt jest instancją klasy lub którejś z jej klas pochodnych; nowa jest `issubclass(klasa, klasa_bazowa)`, która odpowiada, czy klasa dziedziczy po klasie bazowej, bezpośrednio lub pośrednio. Obie przyjmują też krotkę klas i odpowiadają `True`, gdy pasuje którakolwiek:

```python title="typy.py"
from collections import Counter


class Zwierze:
    pass


class Pies(Zwierze):
    pass


class Kot(Zwierze):
    pass


p = Pies()
print(type(p) == Zwierze, isinstance(p, Zwierze), isinstance(p, Kot), isinstance(p, (Kot, Pies)))
print(issubclass(Pies, Zwierze), issubclass(Pies, Kot), issubclass(Pies, object), issubclass(Pies, Pies))
print(issubclass(bool, int), isinstance(True, int), type(True) is int)
print(issubclass(Counter, dict), isinstance(Counter("banan"), dict))
print(issubclass(KeyError, LookupError), issubclass(FileNotFoundError, OSError))
```

```{ .text .no-copy }
False True False True
True False True True
True True False
True True
True True
```

Wyniki porządkują kilka faktów z wcześniejszych rozdziałów. Typ `bool` jest klasą pochodną `int` — dlatego `True + 1` daje `2`, a `isinstance(True, int)` jest prawdą. `Counter` z rozdziału [7. Moduły, pakiety i biblioteka standardowa](../07-moduly/biblioteka-standardowa.md#licznik-counter) jest klasą pochodną słownika, więc ma wszystkie jego metody i przechodzi test `isinstance(..., dict)`. Hierarchia wyjątków z rozdziału [8. Wyjątki i zarządzanie zasobami](../08-wyjatki/zglaszanie-wyjatkow.md#hierarchia-wyjatkow) jest zwykłym dziedziczeniem, a klauzula `except LookupError` obsługuje `KeyError` dlatego, że Python dopasowuje wyjątek do klauzuli według dziedziczenia: klasa w `except` pasuje do wyjątków tej klasy i wszystkich jej klas pochodnych. W kodzie sprawdzającym typ piszemy więc `isinstance(x, Zwierze)`, nie `type(x) == Zwierze`: pierwszy zapis akceptuje także obiekty klas pochodnych, których autor klasy bazowej nie musiał przewidzieć. Sprawdzanie typów jest zresztą potrzebne rzadziej, niż można by sądzić — kod polimorficzny, jak pętla z sekcji o nadpisywaniu, nie pyta obiektu o klasę, tylko wywołuje jego metodę.

## Własne klasy wyjątków

W rozdziale 8 zapowiedzieliśmy własne typy wyjątków; teraz mamy wszystko, czego do tego trzeba. Własny wyjątek to klasa pochodna od `Exception` albo od jednego z jego wyspecjalizowanych potomków — najlepiej tego, który najbliżej opisuje rodzaj błędu:

```python title="wyjatki-wlasne.py"
class BladWieku(ValueError):
    """Błąd związany z wiekiem osoby."""


class BladZakresu(BladWieku):
    """Wiek poza dopuszczalnym zakresem."""

    def __init__(self, wiek):
        self.wiek = wiek
        super().__init__(f"wiek poza zakresem 0–150: {wiek}")


def sprawdz_wiek(wiek):
    """Zwraca wiek, jeśli mieści się w zakresie 0–150."""
    if not 0 <= wiek <= 150:
        raise BladZakresu(wiek)
    return wiek


for wiek in [30, -5]:
    try:
        print("poprawny wiek:", sprawdz_wiek(wiek))
    except BladWieku as e:
        print(f"{type(e).__name__}: {e} (atrybut wiek = {e.wiek})")

try:
    sprawdz_wiek(200)
except ValueError as e:
    print("ValueError:", e)

print(BladZakresu.__mro__)
```

```{ .text .no-copy }
poprawny wiek: 30
BladZakresu: wiek poza zakresem 0–150: -5 (atrybut wiek = -5)
ValueError: wiek poza zakresem 0–150: 200
(<class '__main__.BladZakresu'>, <class '__main__.BladWieku'>, <class 'ValueError'>, <class 'Exception'>, <class 'BaseException'>, <class 'object'>)
```

Ciało klasy `BladWieku` składa się wyłącznie z docstringu — nic więcej nie jest potrzebne, bo wszystko, co potrafi wyjątek (komunikat, `args`, łańcuchy `from`, `add_note()`), dziedziczy po `ValueError`. Klasa `BladZakresu` dodaje atrybut `wiek`, aby obsługa mogła odczytać wartość, która wywołała błąd, i przekazuje komunikat do `super().__init__()` — dzięki temu `str(e)` oraz ślad wywołań wyglądają jak dla wyjątków wbudowanych. Dziedziczenie porządkuje obsługę na trzech poziomach: `except BladZakresu` obsługuje tylko ten błąd, `except BladWieku` — wszystkie błędy wieku, także te, które zdefiniujemy później, a `except ValueError` — również nasze wyjątki, bo kod, który nie zna naszych klas, wciąż widzi w nich `ValueError`. Klasa bazowa dla wyjątków całego programu (na przykład `BladAplikacji(Exception)`) pozwala obsłużyć jedną klauzulą wszystkie błędy własne, nie przechwytując wbudowanych. Przyjęte konwencje: wyjątki dziedziczą po `Exception`, nie po `BaseException` (rozdział 8), mają docstring i nazwy kończące się na `Error` — w naszych polskich nazwach ich odpowiednikiem jest przedrostek `Blad` — a ich definicje pozostają proste: kilka atrybutów, bez logiki.

## Kompozycja a dziedziczenie

Dziedziczenie wyraża relację „jest” (ang. *is-a*): pies jest zwierzęciem, pracownik jest człowiekiem, `BladZakresu` jest `ValueError`. Wiele relacji między obiektami to jednak „ma” (ang. *has-a*): samochód ma silnik, konto ma właściciela, grupa ma listę studentów. Takie relacje wyraża **kompozycja** (ang. *composition*) — obiekt jednej klasy jest atrybutem obiektu innej klasy:

```python title="kompozycja.py"
class Silnik:
    def __init__(self, moc):
        self.moc = moc

    def uruchom(self):
        return f"silnik {self.moc} KM pracuje"


class Samochod:
    def __init__(self, marka, moc):
        self.marka = marka
        self.silnik = Silnik(moc)

    def jedz(self):
        return f"{self.marka}: {self.silnik.uruchom()}"


auto = Samochod("Fiat", 90)
print(auto.jedz())
print(isinstance(auto, Silnik), isinstance(auto.silnik, Silnik))
```

```{ .text .no-copy }
Fiat: silnik 90 KM pracuje
False True
```

Samochód nie jest silnikiem, więc `class Samochod(Silnik)` byłoby błędem projektowym: samochód „odziedziczyłby” metody silnika i udawał, że jest jego odmianą. Zamiast tego `Samochod` przechowuje obiekt `Silnik` w atrybucie i deleguje do niego pracę. Kompozycja jest luźniejsza od dziedziczenia — silnik można wymienić na inny obiekt o tej samej metodzie `uruchom()`, a zmiana klasy `Silnik` nie wpływa na interfejs `Samochod`. Ogólna wskazówka brzmi: dziedziczymy, gdy klasa pochodna naprawdę jest odmianą bazowej i może ją wszędzie zastąpić; w pozostałych przypadkach składamy obiekty. Sposoby łączenia obu podejść i typowe wzorce projektowe omawiamy w rozdziale o zaawansowanych mechanizmach obiektowych. <!-- TODO: link po powstaniu rozdziału o zaawansowanych mechanizmach obiektowych -->

!!! tip "Zasady projektowania klas"
    - Wszystkie atrybuty instancji tworzymy w `__init__`; nie dodajemy ich później z zewnątrz.
    - Każda klasa ma docstring i metodę `__repr__`; `__str__` dodajemy, gdy obiekt ma być czytelny dla użytkownika.
    - Klasa pochodna z własnym `__init__` wywołuje `super().__init__()`.
    - Typ sprawdzamy funkcją `isinstance()`, nie porównaniem `type()` — a najlepiej wcale, wywołując metodę wspólnego interfejsu.
    - Walidację danych umieszczamy w `__init__` i w metodach zapisu właściwości, zgłaszając `ValueError` lub własny wyjątek.
    - Atrybuty klasy służą stałym i danym celowo wspólnym; obiekty modyfikowalne trafiają do instancji.
    - Relację „ma” wyrażamy kompozycją, relację „jest” — dziedziczeniem.
    - Domyślnie `==` porównuje instancje tak jak `is`, według tożsamości, a każdy obiekt może być kluczem słownika. Porównywanie według wartości wymaga metody `__eq__`, a wtedy zachowanie haszowalności — także `__hash__`; obie poznamy w rozdziale o modelu danych. <!-- TODO: link po powstaniu rozdziału o modelu danych -->
