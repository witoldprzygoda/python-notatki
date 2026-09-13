# Klasy danych — dataclass, NamedTuple i Enum

Wiele klas istnieje po to, aby przechowywać kilka pól: punkt ma `x` i `y`, wersja programu — trzy liczby, student — imię, nazwisko i wiek. Dla takich klas `__init__`, `__repr__` i `__eq__` wyglądają zawsze tak samo i są tylko powtarzalną pracą. Python generuje je automatycznie dekoratorem `@dataclass`; obok niego stoją `typing.NamedTuple` dla niemodyfikowalnych rekordów i `Enum` dla zbiorów nazwanych stałych. Na końcu wracamy do instrukcji `match` z rozdziału 4, która z klasami danych i wyliczeniami pokazuje pełnię możliwości.

## Dekorator `@dataclass`

Klasa punktu napisana ręcznie według zasad z rozdziałów 10 i 11 wymaga trzech metod specjalnych:

```python title="punkt-recznie.py"
class Punkt:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Punkt(x={self.x!r}, y={self.y!r})"

    def __eq__(self, inny):
        if not isinstance(inny, Punkt):
            return NotImplemented
        return (self.x, self.y) == (inny.x, inny.y)


p = Punkt(1.0, 2.0)
print(p, p == Punkt(1.0, 2.0), p == Punkt(2.0, 1.0))
```

```{ .text .no-copy }
Punkt(x=1.0, y=2.0) True False
```

**Klasa danych** (ang. *data class*) uzyskuje to samo z deklaracji pól. Dekorator `@dataclass` z modułu `dataclasses` czyta adnotacje typów w ciele klasy — składnię `nazwa: typ` z rozdziału 3 — i na ich podstawie generuje metody:

```python title="punkt-dataclass.py"
from dataclasses import dataclass


@dataclass
class Punkt:
    x: float
    y: float


p = Punkt(1.0, 2.0)
print(p, p == Punkt(1.0, 2.0), p == Punkt(2.0, 1.0))
print(Punkt.__match_args__, vars(p))
print(Punkt(1, 2) == Punkt(1.0, 2.0), p == (1.0, 2.0))
```

```{ .text .no-copy }
Punkt(x=1.0, y=2.0) True False
('x', 'y') {'x': 1.0, 'y': 2.0}
True False
```

Dekorator dopisał `__init__` z parametrami w kolejności pól, `__repr__` w postaci wyrażenia tworzącego obiekt i `__eq__` porównujące pola jak krotki — ale tylko z obiektem **tej samej klasy**; dla innych typów zwraca `NotImplemented`, stąd `False` dla krotki. Adnotacje nie są sprawdzane: `Punkt(1, 2)` przyjmie liczby całkowite, jak każda funkcja z adnotacjami — Python ich nie wymusza (rozdział 3). Dekorator tworzy też krotkę `__match_args__` z nazwami pól, potrzebną instrukcji `match` z ostatniej sekcji. Sama klasa pozostaje zwykłą klasą: można dopisywać metody, właściwości i dziedziczyć.

## Funkcja `field()` i metoda `__post_init__`

Wartości domyślne pól zapisujemy jak wartości domyślne parametrów. Pole z modyfikowalną wartością domyślną — listą, słownikiem — wymaga jednak funkcji `field()` z argumentem `default_factory`, bo jedna lista podana wprost byłaby wspólna dla wszystkich obiektów, jak w pułapce z rozdziału 6:

```python title="mutable-default.py"
from dataclasses import dataclass

try:
    @dataclass
    class Koszyk:
        pozycje: list = []
except ValueError as e:
    print("ValueError:", e)
```

```{ .text .no-copy }
ValueError: mutable default <class 'list'> for field pozycje is not allowed: use default_factory
```

Dekorator odrzuca taką definicję. Funkcja `field()` przyjmuje ponadto argumenty `init`, `repr` i `compare`, które wyłączają pole z generowanych metod, a metoda `__post_init__` — wywoływana przez wygenerowany `__init__` na końcu — służy do walidacji i wyliczania pól pochodnych:

```python title="student-field.py"
from dataclasses import dataclass, field


@dataclass
class Student:
    imie: str
    nazwisko: str
    wiek: int = 20
    oceny: list[float] = field(default_factory=list)
    identyfikator: str = field(init=False, repr=False)

    def __post_init__(self):
        if self.wiek < 0:
            raise ValueError(f"wiek nie może być ujemny: {self.wiek}")
        self.identyfikator = f"{self.nazwisko[:3].upper()}{self.wiek}"

    def srednia(self):
        """Zwraca średnią ocen albo 0.0 dla pustej listy."""
        return sum(self.oceny) / len(self.oceny) if self.oceny else 0.0


s1 = Student("Jan", "Nowak")
s2 = Student("Anna", "Kowalska", 22, [4.5, 5.0])
print(s1, s1.identyfikator)
print(s2, s2.srednia())
print(s1.oceny is s2.oceny)
try:
    Student("Piotr", "Lis", wiek=-5)
except ValueError as e:
    print("ValueError:", e)
```

```{ .text .no-copy }
Student(imie='Jan', nazwisko='Nowak', wiek=20, oceny=[]) NOW20
Student(imie='Anna', nazwisko='Kowalska', wiek=22, oceny=[4.5, 5.0]) 4.75
False
ValueError: wiek nie może być ujemny: -5
```

Pole `identyfikator` nie jest parametrem `__init__` ani częścią `__repr__`, a jego wartość ustala `__post_init__`; każdy obiekt dostaje własną listę ocen z `default_factory=list`. Pola bez wartości domyślnej muszą poprzedzać pola z wartościami — jak parametry funkcji; reguła dotyczy tylko pól trafiających do `__init__`, dlatego `identyfikator` z `init=False` może stać na końcu bez wartości domyślnej.

## Opcje `frozen`, `order`, `slots` i `kw_only`

Dekorator przyjmuje argumenty zmieniające zestaw generowanych metod. Klasa z `order=True` dostaje metody porównań porządkujących, które porównują pola jak krotki, w kolejności deklaracji; klasa z `frozen=True` odrzuca przypisania do pól i staje się haszowalna:

```python title="wersja-opcje.py"
from dataclasses import FrozenInstanceError, dataclass


@dataclass(order=True)
class Wersja:
    major: int
    minor: int
    patch: int = 0


wersje = [Wersja(3, 10), Wersja(3, 9, 1), Wersja(2, 7)]
print(sorted(wersje))
print(Wersja(3, 9) < Wersja(3, 10), max(wersje))


@dataclass(frozen=True)
class Punkt:
    x: float
    y: float


p = Punkt(1.0, 2.0)
print({p: "początek"}[Punkt(1.0, 2.0)], hash(p) == hash(Punkt(1.0, 2.0)))
try:
    p.x = 5.0
except FrozenInstanceError as e:
    print("FrozenInstanceError:", e)


@dataclass(slots=True, kw_only=True)
class Konfiguracja:
    nazwa: str
    poziom: int = 1


k = Konfiguracja(nazwa="test")
print(k, Konfiguracja.__slots__, hasattr(k, "__dict__"))
try:
    Konfiguracja("test")
except TypeError as e:
    print("TypeError:", e)
```

```{ .text .no-copy }
[Wersja(major=2, minor=7, patch=0), Wersja(major=3, minor=9, patch=1), Wersja(major=3, minor=10, patch=0)]
True Wersja(major=3, minor=10, patch=0)
początek True
FrozenInstanceError: cannot assign to field 'x'
Konfiguracja(nazwa='test', poziom=1) ('nazwa', 'poziom') False
TypeError: Konfiguracja.__init__() takes 1 positional argument but 2 were given
```

Reguły haszowania wynikają z rozdziału 11: klasa z `__eq__` bez `__hash__` jest niehaszowalna, więc zwykła klasa danych — która ma wygenerowane `__eq__` — ma `__hash__` ustawione na `None`. Dopiero `frozen=True` czyni pola niemodyfikowalnymi i pozwala bezpiecznie wygenerować `__hash__` z krotki pól. Opcja `slots=True` (od Pythona 3.10) generuje `__slots__` z rozdziału 10 zamiast `__dict__`, a `kw_only=True` czyni wszystkie pola parametrami tylko nazwanymi. Pozostałe opcje to `init`, `repr`, `eq` (wyłączanie generowania), `unsafe_hash` (wymuszenie `__hash__` mimo modyfikowalności — stąd nazwa), `match_args` (wyłączanie `__match_args__`) i `weakref_slot` (obsługa słabych referencji przy `slots=True`).

## Klasy danych a dziedziczenie

Klasa danych może dziedziczyć po innej klasie danych; pola klasy bazowej stoją w `__init__` przed polami klasy pochodnej. Klasa pochodna bez własnego `@dataclass` dziedziczy wygenerowane metody bez zmian:

```python title="dziedziczenie-dataclass.py"
from dataclasses import dataclass


@dataclass
class A:
    x: int = 10


class B(A):
    pass


@dataclass
class C(A):
    y: int = 20


print(A(), B(5), C(1, 2))
print(A() == A(10), B(5) == A(5), type(B(5)).__name__)
try:
    @dataclass
    class Zle(A):
        z: int
except TypeError as e:
    print("TypeError:", e)
```

```{ .text .no-copy }
A(x=10) B(x=5) C(x=1, y=2)
True False B
TypeError: non-default argument 'z' follows default argument 'x'
```

Klasa `B` korzysta z `__init__` i `__repr__` wygenerowanych dla `A` — `__repr__` wypisuje jednak `B(...)`, bo używa nazwy klasy obiektu. Porównanie `B(5) == A(5)` daje `False`: wygenerowane `__eq__` wymaga tej samej klasy. Klasa `C` z własnym `@dataclass` otrzymuje nowy `__init__(x, y)`. Ostatni przypadek pokazuje ograniczenie: pole `z` bez wartości domyślnej stanęłoby w `__init__` za polem `x` z wartością domyślną, co jest niedozwolone tak samo jak w definicji funkcji — rozwiązaniem jest wartość domyślna dla `z` albo `kw_only=True`.

## Funkcje `asdict()`, `replace()` i zapis do JSON

Moduł `dataclasses` dostarcza funkcje działające na każdej klasie danych: `fields()` zwraca opis pól, `asdict()` — słownik z wartościami (rekurencyjnie, także dla zagnieżdżonych klas danych), `astuple()` — krotkę, a `replace()` tworzy kopię z podmienionymi polami, co jest właściwą drogą „zmiany” obiektu zamrożonego (od Pythona 3.13 to samo robi ogólna funkcja `copy.replace()`). Słownik z `asdict()` domyka zapowiedź z rozdziału [9. Wejście, wyjście i pliki](../09-wejscie-wyjscie/csv-i-json.md#format-json-i-modu-json): tak zapisujemy własne typy do JSON i odczytujemy je z powrotem:

```python title="asdict-json.py"
import json
from dataclasses import asdict, dataclass, field, fields, replace


@dataclass(frozen=True)
class Adres:
    miasto: str
    kod: str


@dataclass
class Osoba:
    imie: str
    adres: Adres
    tagi: list[str] = field(default_factory=list)


osoba = Osoba("Jan", Adres("Nowy Sącz", "33-300"), ["student"])
print([pole.name for pole in fields(Osoba)])
print(asdict(osoba))
tekst = json.dumps(asdict(osoba), ensure_ascii=False)
print(tekst)
dane = json.loads(tekst)
odczytana = Osoba(dane["imie"], Adres(**dane["adres"]), dane["tagi"])
print(odczytana == osoba)
print(replace(osoba.adres, kod="33-301"), osoba.adres)
```

```{ .text .no-copy }
['imie', 'adres', 'tagi']
{'imie': 'Jan', 'adres': {'miasto': 'Nowy Sącz', 'kod': '33-300'}, 'tagi': ['student']}
{"imie": "Jan", "adres": {"miasto": "Nowy Sącz", "kod": "33-300"}, "tagi": ["student"]}
True
Adres(miasto='Nowy Sącz', kod='33-301') Adres(miasto='Nowy Sącz', kod='33-300')
```

Odczyt wymaga odtworzenia zagnieżdżonych obiektów ręcznie — `json.loads()` zwraca słowniki, a nie klasy danych; `Adres(**dane["adres"])` rozpakowuje słownik na argumenty nazwane. Dla płaskich klas wystarczy `Klasa(**dane)`.

## `typing.NamedTuple`

Krotka z nazwanymi polami z rozdziału [7. Moduły, pakiety i biblioteka standardowa](../07-moduly/biblioteka-standardowa.md#krotka-z-nazwanymi-polami-namedtuple) ma współczesny zapis klasowy w module `typing`, z adnotacjami i wartościami domyślnymi jak w klasie danych — ale wynikiem jest nadal krotka:

```python title="punkt-namedtuple.py"
from typing import NamedTuple


class Punkt(NamedTuple):
    x: float
    y: float
    kolor: str = "czarny"

    def odleglosc_od_srodka(self):
        """Zwraca odległość punktu od początku układu."""
        return (self.x**2 + self.y**2) ** 0.5


p = Punkt(3.0, 4.0)
print(p, p.x, p[0], p.odleglosc_od_srodka())
x, y, kolor = p
print(x, y, kolor, isinstance(p, tuple), p == (3.0, 4.0, "czarny"))
print(p._asdict(), p._replace(kolor="zielony"))
try:
    p.x = 5.0
except AttributeError as e:
    print("AttributeError:", e)
```

```{ .text .no-copy }
Punkt(x=3.0, y=4.0, kolor='czarny') 3.0 3.0 5.0
3.0 4.0 czarny True True
{'x': 3.0, 'y': 4.0, 'kolor': 'czarny'} Punkt(x=3.0, y=4.0, kolor='zielony')
AttributeError: can't set attribute
```

Obiekt `Punkt` jest krotką: obsługuje indeksy, rozpakowanie i porównania z krotkami, jest niemodyfikowalny i haszowalny, a metody `_asdict()` i `_replace()` odpowiadają funkcjom `asdict()` i `replace()`. Wybór między trzema mechanizmami:

| Cecha | `@dataclass` | `NamedTuple` | zwykła klasa |
|---|---|---|---|
| modyfikowalność | domyślnie tak; `frozen=True` | nie — to krotka | tak |
| `__init__`, `__repr__`, `__eq__` | generowane | generowane | ręcznie |
| `__hash__` | przy `frozen=True` | tak | domyślnie według tożsamości |
| indeksowanie i rozpakowanie | nie | tak — jak krotka | nie |
| dziedziczenie i metody | pełne | metody tak, dziedziczenie ograniczone | pełne |
| zastosowanie | obiekty z danymi i zachowaniem | lekkie, niemodyfikowalne rekordy | złożona logika, własny stan |

## Wyliczenia — `Enum`, `auto`, `IntEnum` i `StrEnum`

**Wyliczenie** (ang. *enumeration*) to zbiór nazwanych stałych — dni tygodnia, statusy zamówienia, kolory — zapisany jako klasa pochodna od `enum.Enum`. Każda wartość przypisana do nazwy w ciele klasy — poza metodami i nazwami specjalnymi — staje się **elementem** wyliczenia: obiektem z nazwą i wartością, istniejącym w jednym egzemplarzu:

```python title="kolory-enum.py"
from enum import Enum, IntEnum, StrEnum, auto


class Kolor(Enum):
    CZERWONY = 1
    ZIELONY = 2
    NIEBIESKI = 3


class Status(Enum):
    AKTYWNY = auto()
    ZAWIESZONY = auto()
    USUNIETY = auto()


print(Kolor.CZERWONY, repr(Kolor.CZERWONY), Kolor.CZERWONY.name, Kolor.CZERWONY.value)
print(Kolor(2), Kolor["NIEBIESKI"], Kolor(2) is Kolor.ZIELONY)
print([status.value for status in Status], len(Status))
print(Kolor.CZERWONY == 1, Kolor.CZERWONY == Kolor.CZERWONY, Kolor.CZERWONY in Kolor)
try:
    print(Kolor.CZERWONY < Kolor.ZIELONY)
except TypeError as e:
    print("TypeError:", e)


class Priorytet(IntEnum):
    NISKI = 1
    SREDNI = 2
    WYSOKI = 3


class Tryb(StrEnum):
    JASNY = auto()
    CIEMNY = auto()


print(Priorytet.WYSOKI > Priorytet.NISKI, Priorytet.WYSOKI + 1, sorted([Priorytet.WYSOKI, Priorytet.NISKI]))
print(Tryb.JASNY, Tryb.JASNY == "jasny", f"tryb={Tryb.CIEMNY}", Tryb("ciemny"))
```

```{ .text .no-copy }
Kolor.CZERWONY <Kolor.CZERWONY: 1> CZERWONY 1
Kolor.ZIELONY Kolor.NIEBIESKI True
[1, 2, 3] 3
False True True
TypeError: '<' not supported between instances of 'Kolor' and 'Kolor'
True 4 [<Priorytet.NISKI: 1>, <Priorytet.WYSOKI: 3>]
jasny True tryb=ciemny ciemny
```

Element wyliczenia ma atrybuty `name` i `value`; do elementu docieramy przez atrybut klasy (`Kolor.ZIELONY`), przez wartość (`Kolor(2)`) albo przez nazwę w nawiasach kwadratowych (`Kolor["NIEBIESKI"]`), a każda z tych dróg zwraca ten sam obiekt — dlatego elementy porównujemy przez `is` albo `==` i używamy jako kluczy słownika. Funkcja `auto()` nadaje kolejne liczby całkowite od 1, więc nie trzeba nadawać wartości ręcznie, gdy liczy się tylko nazwa. Zwykłe wyliczenie nie jest liczbą: `Kolor.CZERWONY == 1` daje `False`, a porównania porządkujące zgłaszają `TypeError`. Gdy elementy mają być liczbami — do sortowania, arytmetyki, zgodności ze starszym kodem używającym stałych całkowitych — dziedziczymy po `IntEnum`; gdy mają być łańcuchami, na przykład wartościami w pliku konfiguracyjnym lub JSON, po `StrEnum` (od Pythona 3.11), w którym `auto()` nadaje nazwę elementu małymi literami, a `str()` i f-string dają samą wartość — dlatego `Tryb("ciemny")` wypisało się jako `ciemny`, nie `Tryb.CIEMNY`. Powtórzona nazwa w wyliczeniu to `TypeError`; powtórzona wartość tworzy alias tego samego elementu.

## Dopasowanie `match`/`case` z klasami danych i wyliczeniami

W rozdziale [4. Sterowanie przepływem](../04-sterowanie/wyrazenia-warunkowe.md#pola-wyboru-match) instrukcja `match` porównywała wartość z literałami. Jej właściwą siłą są **wzorce klasowe** (ang. *class patterns*), które sprawdzają typ obiektu i jednocześnie wiążą jego atrybuty z nazwami, oraz wzorce sekwencji i odwzorowań. Klasy danych i wyliczenia pasują do tego mechanizmu bez dodatkowej pracy:

```python title="match-klasy.py"
from dataclasses import dataclass
from enum import Enum


class Kolor(Enum):
    CZERWONY = 1
    ZIELONY = 2


@dataclass
class Punkt:
    x: float
    y: float


@dataclass
class Okrag:
    srodek: Punkt
    promien: float


def opisz(obiekt):
    match obiekt:
        case Punkt(x=0, y=0):
            return "początek układu"
        case Punkt(x, y) if x == y:
            return f"punkt na przekątnej, x = y = {x}"
        case Punkt(x, y):
            return f"punkt ({x}, {y})"
        case Okrag(srodek=Punkt(x=0, y=0), promien=r):
            return f"okrąg o środku w początku układu i promieniu {r}"
        case Okrag(promien=r) if r <= 0:
            return "okrąg o niedodatnim promieniu"
        case Okrag():
            return "inny okrąg"
        case Kolor.CZERWONY | Kolor.ZIELONY as kolor:
            return f"kolor {kolor.name.lower()}"
        case [Punkt() as pierwszy, *reszta]:
            return f"lista punktów zaczynająca się od {pierwszy}, dalszych: {len(reszta)}"
        case {"typ": typ, **pozostale}:
            return f"słownik typu {typ!r} z kluczami {sorted(pozostale)}"
        case str() | int() | float() as wartosc:
            return f"wartość prosta {wartosc!r}"
        case _:
            return "nieznany obiekt"


przypadki = [
    Punkt(0, 0),
    Punkt(2, 2),
    Punkt(1, 3),
    Okrag(Punkt(0, 0), 5),
    Okrag(Punkt(1, 1), -1),
    Okrag(Punkt(1, 1), 2),
    Kolor.ZIELONY,
    [Punkt(1, 2), Punkt(3, 4), Punkt(5, 6)],
    {"typ": "trójkąt", "boki": 3, "kolor": "niebieski"},
    "tekst",
    None,
]
for przypadek in przypadki:
    print(opisz(przypadek))
```

```{ .text .no-copy }
początek układu
punkt na przekątnej, x = y = 2
punkt (1, 3)
okrąg o środku w początku układu i promieniu 5
okrąg o niedodatnim promieniu
inny okrąg
kolor zielony
lista punktów zaczynająca się od Punkt(x=1, y=2), dalszych: 2
słownik typu 'trójkąt' z kluczami ['boki', 'kolor']
wartość prosta 'tekst'
nieznany obiekt
```

Wzorzec `Punkt(x=0, y=0)` pasuje do obiektu klasy `Punkt` (sprawdzanego przez `isinstance()`, więc także klas pochodnych), którego atrybuty mają podane wartości; wzorzec `Punkt(x, y)` z argumentami pozycyjnymi korzysta z `__match_args__` — wygenerowanego przez `@dataclass` — aby przypisać pierwszy argument do `x`, drugi do `y`, i wiąże te wartości z nazwami. Wzorce można zagnieżdżać (`Okrag(srodek=Punkt(x=0, y=0), ...)`), uzupełniać **strażnikiem** (ang. *guard*) `if` sprawdzanym po dopasowaniu oraz łączyć alternatywą `|` i wiązaniem `as`. Element wyliczenia `Kolor.CZERWONY` jest we wzorcu wartością do porównania, bo zawiera kropkę — goła nazwa byłaby nazwą do związania, co stanowi najczęstszą pomyłkę w `match`. Wzorzec sekwencji `[Punkt() as pierwszy, *reszta]` i wzorzec odwzorowania `{"typ": typ, **pozostale}` rozkładają listę i słownik jak rozpakowanie z rozdziału 5; wzorzec odwzorowania pasuje także wtedy, gdy słownik ma dodatkowe klucze. Obowiązuje pierwszy pasujący `case`, dlatego przypadki szczególne stoją przed ogólnymi, a `case _` na końcu przechwytuje resztę.
