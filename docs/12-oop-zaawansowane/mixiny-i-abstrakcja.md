# Mixiny, kompozycja i klasy abstrakcyjne

Dziedziczenie wielokrotne z poprzedniego podrozdziału rzadko służy do łączenia dwóch pełnoprawnych klas. Jego codziennym zastosowaniem są **mixiny** — małe klasy dodające jedno zachowanie — a obok nich stoi kompozycja, znana z rozdziału 10. Z drugiej strony hierarchia bywa potrzebna nie po to, aby dzielić kod, lecz aby wymusić na klasach pochodnych określony interfejs; do tego służą **klasy abstrakcyjne** z modułu `abc`. W tym podrozdziale porównujemy te trzy narzędzia, budujemy hierarchię z klasą abstrakcyjną, poznajemy `typing.Protocol` jako sformalizowane typowanie kacze i zbieramy zasady wyboru mechanizmu.

## Mixiny

**Mixin** (ang. *mixin*) to klasa zaprojektowana nie jako samodzielny typ, lecz jako dodatek: dostarcza jedną spójną porcję zachowania — metody — i zakłada, że klasa, do której zostanie domieszana, ma odpowiednie atrybuty. Mixin nie definiuje `__init__` i nie tworzy własnego stanu:

```python title="mixiny.py"
import json


class ReprMixin:
    """Dodaje __repr__ zbudowane z atrybutów instancji."""

    def __repr__(self):
        atrybuty = ", ".join(f"{nazwa}={wartosc!r}" for nazwa, wartosc in vars(self).items())
        return f"{type(self).__name__}({atrybuty})"


class JsonMixin:
    """Dodaje zapis do JSON i odczyt z JSON przez atrybuty instancji."""

    def do_json(self):
        return json.dumps(vars(self), ensure_ascii=False)

    @classmethod
    def z_json(cls, tekst):
        return cls(**json.loads(tekst))


class Student(JsonMixin, ReprMixin):
    def __init__(self, imie, wiek):
        self.imie = imie
        self.wiek = wiek


s = Student("Jan", 22)
print(s)
tekst = s.do_json()
print(tekst)
print(Student.z_json(tekst))
print([k.__name__ for k in Student.__mro__])
```

```{ .text .no-copy }
Student(imie='Jan', wiek=22)
{"imie": "Jan", "wiek": 22}
Student(imie='Jan', wiek=22)
['Student', 'JsonMixin', 'ReprMixin', 'object']
```

W klasie `Student` nie zapisano ani `__repr__`, ani obsługi JSON z rozdziału 9 — obie zdolności domieszała z dwóch niezależnych klas, które można w ten sam sposób dodać do dowolnej innej klasy z atrybutami w `vars()`. Metoda klasy `z_json()` korzysta z `cls`, więc tworzy obiekt tej klasy, do której mixin domieszano — dokładnie tak, jak konstruktory alternatywne z rozdziału 10. Konwencje: przyrostek `Mixin` w nazwie, brak `__init__`, jedno zachowanie na klasę, a w nawiasie klasy pochodnej mixiny przed właściwą klasą bazową, aby ich metody miały pierwszeństwo w MRO.

## Dziedziczenie, mixin czy kompozycja

Trzy sposoby ponownego użycia kodu odpowiadają trzem relacjom między klasami:

| Cecha | Dziedziczenie | Mixin | Kompozycja |
|---|---|---|---|
| relacja | „jest” (ang. *is-a*): `Pies` jest `Zwierze` | „zachowuje się jak” (ang. *acts-as*): `Student` zapisuje się do JSON | „ma” (ang. *has-a*): `Samochod` ma `Silnik` |
| `__init__` | klasa pochodna wywołuje `super().__init__()` | mixin go nie definiuje | obiekt składowy tworzony w `__init__` |
| kształt kodu | hierarchia, często głęboka | płaska lista dodatków | delegowanie do atrybutu |
| kiedy | prawdziwa relacja typów, wspólny interfejs | dodanie zachowania bez hierarchii | wszystko pozostałe |

Zasada z rozdziału 10 pozostaje w mocy: kompozycję wybieramy domyślnie, mixiny dodają zachowania bez budowania hierarchii, a dziedziczymy tylko wtedy, gdy klasa pochodna może wszędzie zastąpić bazową. Wiele mixinów naraz czyni klasę trudną do zrozumienia — „jedna klasa, jedno zachowanie” dotyczy także domieszek.

## Klasy abstrakcyjne — `abc.ABC` i `@abstractmethod`

Zwykłe dziedziczenie niczego nie wymusza: klasa bazowa może obiecywać metodę `pole()`, ale nic nie stoi na przeszkodzie, aby klasa pochodna jej nie napisała, a błąd ujawni się dopiero przy wywołaniu. **Klasa abstrakcyjna** (ang. *abstract base class*, ABC) to klasa, której instancji nie da się utworzyć, dopóki ma choć jedną niezaimplementowaną **metodę abstrakcyjną**, i która wymaga od klas pochodnych implementacji tych metod. Definiujemy ją, dziedzicząc po `abc.ABC` i oznaczając metody dekoratorem `@abstractmethod`:

```python title="figury.py"
import math
from abc import ABC, abstractmethod


class Figura(ABC):
    """Figura płaska o polu i obwodzie."""

    @abstractmethod
    def pole(self):
        """Zwraca pole figury."""

    @abstractmethod
    def obwod(self):
        """Zwraca obwód figury."""

    def opis(self):
        """Zwraca opis figury z polem i obwodem."""
        return f"{type(self).__name__}: pole {self.pole():.2f}, obwód {self.obwod():.2f}"


class Kolo(Figura):
    def __init__(self, promien):
        self.promien = promien

    def pole(self):
        return math.pi * self.promien**2

    def obwod(self):
        return 2 * math.pi * self.promien


class Prostokat(Figura):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def pole(self):
        return self.a * self.b


print(Kolo(1).opis())
print(sorted(Figura.__abstractmethods__))
for klasa, argumenty in [(Figura, ()), (Prostokat, (3, 4))]:
    try:
        klasa(*argumenty)
    except TypeError as e:
        print("TypeError:", e)
```

```{ .text .no-copy }
Kolo: pole 3.14, obwód 6.28
['obwod', 'pole']
TypeError: Can't instantiate abstract class Figura without an implementation for abstract methods 'obwod', 'pole'
TypeError: Can't instantiate abstract class Prostokat without an implementation for abstract method 'obwod'
```

Klasa `Kolo` implementuje obie metody abstrakcyjne i odziedziczyła zwykłą metodę `opis()`, która korzysta z nich przez `self` — klasa abstrakcyjna może zawierać dowolnie dużo gotowego kodu opartego na metodach, których jeszcze nie ma. W klasie `Prostokat` pominięto `obwod()`, więc pozostaje ona abstrakcyjna: błąd pojawia się przy próbie utworzenia obiektu, z komunikatem wymieniającym brakujące metody, a nie dopiero przy wywołaniu `obwod()` gdzieś w programie. Zbiór `__abstractmethods__` zawiera nazwy metod, których jeszcze nie zaimplementowano. Ciało metody abstrakcyjnej może być samym docstringiem — wystarcza on za treść, jak w klasach wyjątków z rozdziału 10.

Funkcja `isinstance()` rozpoznaje klasy pochodne od klasy abstrakcyjnej jak każde inne, a metoda `Figura.register(Obca)` pozwala ponadto zarejestrować klasę niedziedziczącą jako „wirtualną” podklasę — tak działają klasy z `collections.abc` z rozdziału 11, które rozpoznają listy i słowniki, choć te po nich nie dziedziczą.

### Abstrakcyjna właściwość

Dekorator `@abstractmethod` łączy się z `@property`, `@classmethod` i `@staticmethod`; `@abstractmethod` stoi wtedy najbliżej definicji, jako wewnętrzny:

```python title="wlasciwosc-abstrakcyjna.py"
from abc import ABC, abstractmethod


class Pojazd(ABC):
    @property
    @abstractmethod
    def predkosc_max(self):
        """Zwraca prędkość maksymalną w km/h."""


class Samochod(Pojazd):
    @property
    def predkosc_max(self):
        return 200


print(Samochod().predkosc_max)
try:
    Pojazd()
except TypeError as e:
    print("TypeError:", e)
```

```{ .text .no-copy }
200
TypeError: Can't instantiate abstract class Pojazd without an implementation for abstract method 'predkosc_max'
```

### Implementacja w metodzie abstrakcyjnej i `super()`

Metoda abstrakcyjna może mieć treść. Klasa pochodna nadal musi ją nadpisać, ale może wywołać wersję bazową przez `super()` i wzbogacić ją o własne działania — to typowy sposób udostępniania wspólnej części zachowania:

```python title="super-w-abstrakcyjnej.py"
from abc import ABC, abstractmethod


class Raport(ABC):
    @abstractmethod
    def generuj(self):
        print("nagłówek raportu")


class RaportSprzedazy(Raport):
    def generuj(self):
        super().generuj()
        print("tabela sprzedaży")


RaportSprzedazy().generuj()
```

```{ .text .no-copy }
nagłówek raportu
tabela sprzedaży
```

## Fabryka pojazdów

Klasa abstrakcyjna łączy się z mechanizmami rozdziału 10 w typowy wzór: wspólne atrybuty i walidację umieszczamy w klasie bazowej, interfejs wymuszamy metodami abstrakcyjnymi, a tworzenie obiektów właściwej klasy pochodnej powierzamy metodzie klasy:

```python title="fabryka-pojazdow.py"
from abc import ABC, abstractmethod


class Pojazd(ABC):
    """Pojazd o modelu, roku produkcji i bieżącej prędkości."""

    def __init__(self, model, rok):
        if not self.poprawny_rok(rok):
            raise ValueError(f"niepoprawny rok produkcji: {rok}")
        self.model = model
        self.rok = rok
        self._predkosc = 0

    def __repr__(self):
        return f"{type(self).__name__}({self.model!r}, {self.rok})"

    @property
    def predkosc(self):
        return self._predkosc

    @predkosc.setter
    def predkosc(self, wartosc):
        if not 0 <= wartosc <= self.predkosc_max:
            raise ValueError(f"prędkość poza zakresem 0–{self.predkosc_max}: {wartosc}")
        self._predkosc = wartosc

    @property
    @abstractmethod
    def predkosc_max(self):
        """Zwraca prędkość maksymalną pojazdu."""

    @abstractmethod
    def opis(self):
        """Zwraca opis pojazdu."""

    @staticmethod
    def poprawny_rok(rok):
        """Sprawdza, czy rok produkcji jest wiarygodny."""
        return 1886 <= rok <= 2100

    @classmethod
    def utworz(cls, typ, model, rok):
        """Zwraca pojazd wskazanego typu."""
        typy = {"samochod": Samochod, "autobus": Autobus}
        if typ not in typy:
            raise ValueError(f"nieznany typ pojazdu: {typ!r}")
        return typy[typ](model, rok)


class Samochod(Pojazd):
    predkosc_max = 180

    def opis(self):
        return f"samochód {self.model} z roku {self.rok}"


class Autobus(Pojazd):
    predkosc_max = 100

    def __init__(self, model, rok, miejsca=50):
        super().__init__(model, rok)
        self.miejsca = miejsca

    def opis(self):
        return f"autobus {self.model} na {self.miejsca} miejsc"


flota = [Pojazd.utworz("samochod", "Fiat", 2019), Pojazd.utworz("autobus", "Solaris", 2022)]
for pojazd in flota:
    pojazd.predkosc = 90
    print(pojazd, "|", pojazd.opis(), "|", pojazd.predkosc)
try:
    flota[1].predkosc = 120
except ValueError as e:
    print("ValueError:", e)
try:
    Pojazd.utworz("rower", "Kross", 2020)
except ValueError as e:
    print("ValueError:", e)
```

```{ .text .no-copy }
Samochod('Fiat', 2019) | samochód Fiat z roku 2019 | 90
Autobus('Solaris', 2022) | autobus Solaris na 50 miejsc | 90
ValueError: prędkość poza zakresem 0–100: 120
ValueError: nieznany typ pojazdu: 'rower'
```

Klasy pochodne zaspokoiły abstrakcyjną właściwość `predkosc_max` zwykłym atrybutem klasy — to dozwolone, bo mechanizm klas abstrakcyjnych sprawdza tylko, czy wartość dostępna pod tą nazwą jest nadal oznaczona jako abstrakcyjna (atrybut `__isabstractmethod__`), a zwykła liczba takiego oznaczenia nie ma. Metoda klasy `utworz()` wybiera klasę pochodną według nazwy; słownik typów wewnątrz klasy bazowej odwołuje się do klas zdefiniowanych niżej, co działa, bo ciało metody wykonuje się dopiero przy wywołaniu. Rozbudowaną postać tego wzorca, z rejestracją klas bez ręcznego słownika, pokazujemy w podrozdziałach o wzorcach projektowych i metaprogramowaniu.

## Typowanie kacze i `typing.Protocol` (dla dociekliwych)

Klasa abstrakcyjna wymusza interfejs przez dziedziczenie. Python równie często obywa się bez tego: funkcja wywołuje `zrodlo.czytaj()` i przyjmie każdy obiekt, który ma taką metodę — to typowanie kacze z rozdziału 11. Formalizuje je klasa `typing.Protocol`: opisuje wymagane metody, a klasy nie muszą po niej dziedziczyć, aby były z nią zgodne — liczy się struktura, stąd nazwa **podtypowanie strukturalne** (ang. *structural subtyping*):

```python title="protokol-czytelne.py"
from typing import Protocol, runtime_checkable


@runtime_checkable
class Czytelne(Protocol):
    def czytaj(self) -> str: ...


class Plik:
    def czytaj(self):
        return "dane z pliku"


class Api:
    def czytaj(self):
        return "dane z api"


class Liczba:
    def __init__(self, wartosc):
        self.wartosc = wartosc


def przetworz(zrodlo: Czytelne) -> str:
    return zrodlo.czytaj().upper()


for zrodlo in [Plik(), Api()]:
    print(przetworz(zrodlo))
print(isinstance(Plik(), Czytelne), isinstance(Liczba(5), Czytelne))
```

```{ .text .no-copy }
DANE Z PLIKU
DANE Z API
True False
```

Klasy `Plik` i `Api` nie wiedzą o istnieniu `Czytelne`, a mimo to `isinstance()` je akceptuje — dekorator `@runtime_checkable` włącza sprawdzanie w czasie działania, które bada wyłącznie obecność wymaganych metod, nie ich sygnatury ani typy wyników. Bez dekoratora `isinstance()` zgłasza `TypeError`; instancji samego protokołu nie da się utworzyć. Ciało `...` — literał wielokropka — to przyjęty w protokołach zapis pustego ciała: liczy się wyłącznie nazwa i sygnatura metody. Głównym odbiorcą adnotacji `zrodlo: Czytelne` są jednak narzędzia analizy statycznej, które wskażą wywołanie `przetworz(Liczba(5))` jako błąd jeszcze przed uruchomieniem programu — wracamy do nich w rozdziale o narzędziach analizy typów. <!-- TODO: link po powstaniu rozdziału o narzędziach analizy typów --> Wybór między `ABC` a `Protocol` jest prosty: klasa abstrakcyjna, gdy chcemy wymusić implementację i dzielić kod w hierarchii; protokół, gdy chcemy jedynie opisać, czego funkcja oczekuje, nie narzucając dziedziczenia.

## Zasady projektowania

Mechanizmy tego i poprzedniego podrozdziału łatwo nadużyć. Kilka reguł porządkuje wybory; pierwsze trzy pochodzą z zestawu zasad znanych pod skrótem **SOLID**, ostatnia — z zasady **DRY** (ang. *don't repeat yourself*):

- **Pojedyncza odpowiedzialność** (ang. *single responsibility*): klasa robi jedną rzecz; gdy opis klasy wymaga spójnika „i”, lepiej ją podzielić — na dwie klasy albo klasę i mixin.
- **Otwarte na rozszerzanie, zamknięte na modyfikację** (ang. *open/closed*): nowe zachowanie dodajemy nową klasą pochodną, strategią albo wpisem w rejestrze, nie edycją istniejącego kodu — fabryka z rejestrem z podrozdziału o wzorcach projektowych pozwoli dodać `Rower` bez zmiany `Pojazd`; wersja ze słownikiem wewnątrz `utworz()` tego warunku jeszcze nie spełnia.
- **Zastępowalność** (ang. *Liskov substitution*): obiekt klasy pochodnej musi działać wszędzie tam, gdzie oczekiwano klasy bazowej — inaczej relacja „jest” jest fałszywa i właściwa jest kompozycja.
- **Bez powtórzeń**: powtarzający się kod w kilku klasach to sygnał, że brakuje mixinu, klasy bazowej albo funkcji pomocniczej.

Tabela zbiera odpowiedzi na typowe pytania projektowe:

| Potrzeba | Mechanizm |
|---|---|
| prosty kontener danych | klasa danych (`@dataclass`) lub `NamedTuple` — następny podrozdział |
| dane niemodyfikowalne i lekkie | `NamedTuple` lub `@dataclass(frozen=True)` |
| wymuszenie interfejsu w klasach pochodnych | `ABC` z `@abstractmethod` |
| dodanie zachowania bez hierarchii | mixin |
| walidacja atrybutów | `@property` (rozdział 10) lub deskryptor (rozdział 11) |
| opis oczekiwanego interfejsu bez dziedziczenia | `typing.Protocol` |
| stałe i zbiory nazwanych wartości | `Enum` — następny podrozdział |
| rejestrowanie klas pochodnych | `__init_subclass__` — podrozdział o metaprogramowaniu |
| kontrola tworzenia klas | metaklasa — ostateczność |
